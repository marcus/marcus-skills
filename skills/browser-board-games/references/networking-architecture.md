# Networking Architecture

## Colyseus Setup

### Server Bootstrap

```typescript
// packages/server/src/index.ts
import { Server } from "colyseus";
import { createServer } from "http";
import { GameRoom } from "./rooms/GameRoom";

const port = Number(process.env.PORT) || 2567;
const server = new Server({
  server: createServer(),
  // Optional: configure transport
  // transport: new WebSocketTransport({ pingInterval: 3000, pingMaxRetries: 3 })
});

// Register room handlers
server.define("game", GameRoom)
  .filterBy(["gameType"])         // Allow filtering by game variant
  .sortBy({ clients: -1 });      // Fill rooms with most players first

// Built-in lobby room (auto-lists available rooms)
server.define("lobby", LobbyRoom);

server.listen(port);
console.log(`Game server listening on ws://localhost:${port}`);
```

### Client Connection

```typescript
// packages/client/src/connection.ts
import { Client, Room } from "colyseus.js";

const ENDPOINT = import.meta.env.VITE_SERVER_URL || "ws://localhost:2567";
const client = new Client(ENDPOINT);

export async function createRoom(gameType: string, options: RoomOptions): Promise<Room> {
  return client.create("game", { gameType, ...options });
}

export async function joinRoom(roomId: string): Promise<Room> {
  return client.joinById(roomId);
}

export async function quickMatch(gameType: string): Promise<Room> {
  return client.joinOrCreate("game", { gameType });
}

export async function joinWithCode(code: string): Promise<Room> {
  const rooms = await client.getAvailableRooms("game");
  const room = rooms.find(r => r.metadata?.code === code);
  if (!room) throw new Error("Room not found");
  return client.joinById(room.roomId);
}
```

---

## State Schema Design

Colyseus uses `@colyseus/schema` for automatic state synchronization. Only schema-decorated properties are synced.

### Schema Design Principles

1. **Keep schemas flat** — Deeply nested schemas generate more patches
2. **Use MapSchema for dynamic collections** — Players, pieces, cards
3. **Use ArraySchema for ordered lists** — Move history, card decks
4. **Separate synced state from server-only state** — Don't put secrets in the schema
5. **Use `@filter` for hidden information** — Each player sees different state

### Example: Chess-like Game Schema

```typescript
// packages/shared/src/schema.ts
import { Schema, type, MapSchema, ArraySchema, filter } from "@colyseus/schema";

export class Position extends Schema {
  @type("uint8") row: number = 0;
  @type("uint8") col: number = 0;
}

export class Piece extends Schema {
  @type("string") id: string = "";
  @type("string") type: string = "";    // "pawn", "rook", etc.
  @type("string") owner: string = "";   // player sessionId
  @type(Position) position = new Position();
  @type("boolean") captured: boolean = false;
}

export class Player extends Schema {
  @type("string") sessionId: string = "";
  @type("string") displayName: string = "";
  @type("uint8") color: number = 0;     // 0 = white, 1 = black
  @type("boolean") connected: boolean = true;
  @type("boolean") ready: boolean = false;
  @type("uint32") timeRemainingMs: number = 0;
}

export class MoveRecord extends Schema {
  @type("string") pieceId: string = "";
  @type(Position) from = new Position();
  @type(Position) to = new Position();
  @type("string") playerId: string = "";
  @type("uint32") timestamp: number = 0;
}

export class GameState extends Schema {
  @type("string") phase: string = "waiting";  // waiting | ready_check | playing | finished
  @type({ map: Player }) players = new MapSchema<Player>();
  @type({ map: Piece }) pieces = new MapSchema<Piece>();
  @type([MoveRecord]) moveHistory = new ArraySchema<MoveRecord>();
  @type("string") currentTurn: string = "";   // sessionId of active player
  @type("uint16") turnNumber: number = 0;
  @type("string") winner: string = "";         // sessionId or "" if ongoing
  @type("string") roomCode: string = "";
}
```

### Hidden Information with Filters

For games where players have private information (card hands, hidden tiles):

```typescript
export class Card extends Schema {
  @type("string") id: string = "";

  // Only the owner can see the card's value
  @filter(function (this: Card, client: any, value: any, root: GameState) {
    return this.owner === client.sessionId || this.faceUp;
  })
  @type("string") value: string = "";

  @type("string") owner: string = "";
  @type("boolean") faceUp: boolean = false;
}
```

**Important**: Filters run on the server. The client never receives data that fails the filter check. This is the correct way to handle hidden information — never trust the client to hide data it has received.

---

## Message Protocol

Define a clear message protocol between client and server. Use string message types with typed payloads.

### Message Types

```typescript
// packages/shared/src/types.ts

// Client → Server messages
export interface ClientMessages {
  "move": { pieceId: string; to: { row: number; col: number } };
  "ready": {};
  "unready": {};
  "chat": { text: string };
  "rematch": {};
  "forfeit": {};
  "request_undo": {};
  "respond_undo": { accept: boolean };
}

// Server → Client messages
export interface ServerMessages {
  "error": { code: string; message: string };
  "move_rejected": { reason: string };
  "move_accepted": { moveId: string };
  "game_over": { winner: string; reason: string };
  "turn_timer": { remainingMs: number };
  "undo_requested": { by: string };
  "notification": { type: string; message: string };
}
```

### Server Message Handling

```typescript
// packages/server/src/rooms/GameRoom.ts
import { Room, Client } from "colyseus";
import { GameState, Player } from "@shared/schema";
import type { ClientMessages } from "@shared/types";

export class GameRoom extends Room<GameState> {
  maxClients = 4;
  autoDispose = true;

  onCreate(options: any) {
    this.setState(new GameState());
    this.state.roomCode = this.generateRoomCode();

    // Set metadata for lobby listing
    this.setMetadata({
      gameType: options.gameType,
      code: this.state.roomCode,
      maxPlayers: options.maxPlayers || 2,
    });

    this.registerMessageHandlers();
    this.setSimulationInterval(() => this.update(), 1000); // 1Hz tick for timers
  }

  private registerMessageHandlers() {
    this.onMessage<ClientMessages["move"]>("move", (client, data) => {
      this.handleMove(client, data);
    });

    this.onMessage<ClientMessages["ready"]>("ready", (client) => {
      const player = this.state.players.get(client.sessionId);
      if (player) player.ready = true;
      this.checkAllReady();
    });

    this.onMessage<ClientMessages["chat"]>("chat", (client, data) => {
      // Broadcast chat to all clients
      this.broadcast("chat", {
        from: client.sessionId,
        text: data.text.slice(0, 500), // Sanitize length
        timestamp: Date.now(),
      });
    });
  }

  private handleMove(client: Client, data: ClientMessages["move"]) {
    if (this.state.phase !== "playing") return;
    if (this.state.currentTurn !== client.sessionId) {
      client.send("move_rejected", { reason: "Not your turn" });
      return;
    }

    const result = this.gameEngine.applyMove({
      type: "move",
      playerId: client.sessionId,
      timestamp: Date.now(),
      data,
    });

    if (!result.valid) {
      client.send("move_rejected", { reason: result.reason });
      return;
    }

    // State changes are auto-synced by Colyseus
    client.send("move_accepted", { moveId: result.moveId });

    if (result.gameOver) {
      this.state.phase = "finished";
      this.state.winner = result.winner;
      this.broadcast("game_over", {
        winner: result.winner,
        reason: result.reason,
      });
    }
  }

  onJoin(client: Client, options: any) {
    const player = new Player();
    player.sessionId = client.sessionId;
    player.displayName = options.displayName || `Player ${this.state.players.size + 1}`;
    player.color = this.state.players.size;
    this.state.players.set(client.sessionId, player);
  }

  async onLeave(client: Client, consented: boolean) {
    const player = this.state.players.get(client.sessionId);
    if (!player) return;
    player.connected = false;

    if (consented) {
      // Player intentionally left — remove them
      this.state.players.delete(client.sessionId);
      return;
    }

    // Disconnected — allow reconnection for 60 seconds
    try {
      await this.allowReconnection(client, 60);
      player.connected = true;
    } catch {
      // Timed out — remove player
      this.state.players.delete(client.sessionId);
    }
  }

  private generateRoomCode(): string {
    // 4-char alphanumeric code (no ambiguous chars)
    const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
    return Array.from({ length: 4 }, () =>
      chars[Math.floor(Math.random() * chars.length)]
    ).join("");
  }
}
```

---

## Reconnection Handling

Colyseus provides built-in reconnection support. Here's how to implement it properly:

### Server Side

```typescript
// In GameRoom
async onLeave(client: Client, consented: boolean) {
  const player = this.state.players.get(client.sessionId);
  if (!player) return;

  player.connected = false;

  // If the player intentionally left (closed tab with confirmation), don't wait
  if (consented) {
    this.handlePlayerLeft(client.sessionId);
    return;
  }

  // Allow reconnection — pause their timer if applicable
  this.pausePlayerTimer(client.sessionId);

  try {
    // Wait up to 60 seconds for reconnection
    const reconnectedClient = await this.allowReconnection(client, 60);
    player.connected = true;
    this.resumePlayerTimer(client.sessionId);
    reconnectedClient.send("notification", {
      type: "reconnected",
      message: "Welcome back!"
    });
  } catch {
    // Player didn't reconnect in time
    this.handlePlayerLeft(client.sessionId);
  }
}

private handlePlayerLeft(sessionId: string) {
  if (this.state.phase === "playing") {
    // Forfeit the game or replace with bot
    this.state.phase = "finished";
    this.broadcast("notification", {
      type: "player_left",
      message: `${this.state.players.get(sessionId)?.displayName} left the game`,
    });
  }
  this.state.players.delete(sessionId);
}
```

### Client Side

```typescript
// packages/client/src/connection.ts

let reconnectionToken: any = null;

export function setupReconnection(room: Room) {
  // Save reconnection token
  reconnectionToken = room.reconnectionToken;

  room.onLeave((code) => {
    if (code === 1000) {
      // Normal close — don't reconnect
      return;
    }
    attemptReconnect();
  });
}

async function attemptReconnect() {
  if (!reconnectionToken) return;

  const maxAttempts = 10;
  const baseDelay = 500;

  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      showReconnecting(attempt + 1, maxAttempts);
      const room = await client.reconnect(reconnectionToken);
      hideReconnecting();
      setupRoom(room); // Re-bind all listeners
      return;
    } catch {
      // Exponential backoff with jitter
      const delay = baseDelay * Math.pow(2, attempt) + Math.random() * 500;
      await sleep(delay);
    }
  }

  showDisconnected(); // Give up — show "connection lost" UI
}
```

---

## State Synchronization Patterns

### Listening to State Changes (Client)

Colyseus provides fine-grained callbacks for state changes:

```typescript
// packages/client/src/game/controller.ts

function bindStateListeners(room: Room<GameState>) {
  const state = room.state;

  // Listen to specific field changes
  state.listen("currentTurn", (value, previousValue) => {
    highlightActivePlayer(value);
    if (value === room.sessionId) {
      showYourTurnIndicator();
      playSound("your_turn");
    }
  });

  state.listen("phase", (phase) => {
    handlePhaseChange(phase);
  });

  // Listen to map changes (players joining/leaving)
  state.players.onAdd((player, sessionId) => {
    renderPlayerCard(sessionId, player);

    // Listen to changes on individual player
    player.listen("connected", (connected) => {
      setPlayerConnectionStatus(sessionId, connected);
    });
  });

  state.players.onRemove((player, sessionId) => {
    removePlayerCard(sessionId);
  });

  // Listen to piece changes (the core game rendering)
  state.pieces.onAdd((piece, pieceId) => {
    renderPiece(piece);

    piece.position.listen("row", () => animatePieceMove(piece));
    piece.position.listen("col", () => animatePieceMove(piece));
  });

  state.pieces.onChange((piece, pieceId) => {
    if (piece.captured) {
      animateCapture(piece);
    }
  });

  // Listen to move history (for move log / replay)
  state.moveHistory.onAdd((move, index) => {
    addToMoveLog(move);
  });
}
```

### Optimistic Updates (Optional)

For snappy feel, apply moves locally before server confirmation:

```typescript
function sendMove(pieceId: string, to: Position) {
  // 1. Validate locally (same logic as server)
  if (!isValidMove(localState, myPlayerId, { pieceId, to })) {
    showInvalidMoveFlash();
    return;
  }

  // 2. Apply optimistic update
  const rollback = captureState();
  applyMoveLocally(pieceId, to);
  startMoveAnimation(pieceId, to);

  // 3. Send to server
  room.send("move", { pieceId, to });

  // 4. If server rejects, rollback
  const handler = room.onMessage("move_rejected", () => {
    handler(); // Remove listener
    rollback();
    showMoveRejected();
  });

  // Auto-cleanup on success (state sync will confirm)
  setTimeout(() => handler(), 5000);
}
```

---

## Scaling Considerations

### Single Server (handles most board games)

A single Colyseus server can handle thousands of concurrent rooms. Board games have low message rates (moves per second, not frames per second), so a single server goes very far.

**Capacity estimate**: A modest server (2 CPU, 4GB RAM) can handle:
- ~5,000 concurrent WebSocket connections
- ~2,000 active game rooms
- Turn-based games with <10 messages/second/room

### Multi-Server (when you need it)

When you outgrow one server, Colyseus supports horizontal scaling:

1. **Sticky sessions with a load balancer**: Route reconnecting clients to the same server
2. **Redis presence**: Share room availability across servers via `@colyseus/redis-presence`
3. **Redis driver**: Share room state across servers via `@colyseus/redis-driver`

```typescript
import { Server } from "colyseus";
import { RedisPresence } from "@colyseus/redis-presence";
import { RedisDriver } from "@colyseus/redis-driver";

const server = new Server({
  presence: new RedisPresence({ host: "redis-host" }),
  driver: new RedisDriver({ host: "redis-host" }),
});
```

### Deployment Recommendations

| Provider | Why | Notes |
|----------|-----|-------|
| **Fly.io** | Best for WebSocket servers | Global edge, sticky sessions built-in, affordable |
| **Railway** | Easiest deploy | Good for getting started, auto-scaling |
| **Self-hosted VPS** | Maximum control | Hetzner or DigitalOcean, good price/performance |

Key deployment requirements:
- WebSocket support (most providers support this)
- Sticky sessions or single-server
- Persistent process (not serverless/lambda)

---

## Alternative: Raw WebSocket Architecture

If you prefer zero dependencies for networking, here's the pattern using the `ws` package:

```typescript
import { WebSocketServer, WebSocket } from "ws";

interface GameRoom {
  id: string;
  code: string;
  players: Map<string, { ws: WebSocket; data: PlayerData }>;
  state: GameState;
  spectators: Set<WebSocket>;
}

const rooms = new Map<string, GameRoom>();

const wss = new WebSocketServer({ port: 2567 });

wss.on("connection", (ws) => {
  ws.on("message", (raw) => {
    const msg = JSON.parse(raw.toString());
    switch (msg.type) {
      case "create_room": handleCreateRoom(ws, msg); break;
      case "join_room": handleJoinRoom(ws, msg); break;
      case "move": handleMove(ws, msg); break;
      // ... etc
    }
  });
});

function broadcast(room: GameRoom, message: object, exclude?: WebSocket) {
  const data = JSON.stringify(message);
  for (const [, player] of room.players) {
    if (player.ws !== exclude && player.ws.readyState === WebSocket.OPEN) {
      player.ws.send(data);
    }
  }
  for (const spectator of room.spectators) {
    if (spectator.readyState === WebSocket.OPEN) {
      spectator.send(data);
    }
  }
}
```

**What you'll need to build yourself with raw WebSockets**:
- Room creation, joining, and lifecycle management (~200 lines)
- State synchronization and delta patching (~300 lines)
- Reconnection with session tokens (~200 lines)
- Heartbeat/ping-pong (~50 lines)
- Message serialization and type safety (~100 lines)

This is feasible but time-consuming. Colyseus wraps all of this and adds schema-based efficient serialization. For most projects, Colyseus is the right choice.
