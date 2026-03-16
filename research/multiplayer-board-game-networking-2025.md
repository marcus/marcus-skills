# Browser-Based Multiplayer Board Game Networking: Architecture & Libraries (2025-2026)

Comprehensive research on real-time multiplayer networking for browser-based board games.

---

## 1. WebSocket Libraries Comparison

### Native WebSocket API (Browser)
- **What**: Built-in browser API, no dependencies
- **Pros**: Zero bundle size, no abstraction overhead, standard protocol
- **Cons**: No automatic reconnection, no rooms/channels, no fallback transports, no message acknowledgments, no heartbeat — you build everything yourself
- **Verdict for board games**: Only viable as a building block. You will inevitably rebuild Socket.IO features poorly.

### ws (Node.js Server)
- **Version**: Actively maintained (22.7k GitHub stars)
- **What**: Minimal, fast, standards-compliant WebSocket server for Node.js
- **Performance**: ~100k messages/sec with 16 clients on Node 18
- **Pros**: Lightweight, no opinions, fast, well-tested
- **Cons**: Server-only (pairs with native browser WebSocket), no rooms/reconnection/broadcasting built in
- **Verdict**: Good as a transport layer if you want full control. Colyseus uses it internally.

### uWebSockets.js
- **What**: C++ WebSocket server exposed to Node.js as a native V8 addon
- **Performance**: ~700k messages/sec — **7x faster than ws** (Bun benchmarks). Ranked fastest in TechEmpower benchmarks.
- **Pros**: Extreme performance, forms the core of Bun's WebSocket implementation
- **Cons**: C++ dependency, less approachable API, limited community examples for game patterns
- **Colyseus integration**: Available as `@colyseus/uwebsockets-transport` drop-in replacement
- **Verdict**: Use when you need raw throughput. Unnecessary for most board games (low message volume).

### Bun Built-in WebSockets
- **Performance**: 7x throughput vs Node.js + ws (built on uWebSockets internally)
- **Features**: Native pub/sub topics, per-message compression, contextual data on connections
- **Pros**: Extremely fast, native pub/sub simplifies room-like patterns, clean API
- **Cons**: Runtime lock-in to Bun, younger ecosystem
- **Colyseus integration**: Available as `@colyseus/bun-websockets` transport
- **Verdict**: Compelling if already using Bun. The native pub/sub is elegant for game rooms.

### Socket.IO v4
- **Version**: v4.x (10.4 KB minified+gzipped)
- **What**: Event-based bidirectional communication with automatic reconnection, rooms, namespaces
- **Reconnection**: Built-in exponential backoff, heartbeat monitoring
- **Rooms**: Server-side concept, `socket.join("room")`, `io.to("room").emit()`
- **Scaling**: Redis adapter for multi-server deployments
- **Overhead**: Minimal — `42["hello","world"]` for a typical message frame
- **Pros**: Battle-tested, excellent DX, rooms/namespaces built-in, automatic transport fallback (long-polling to WebSocket), huge ecosystem
- **Cons**: Not a raw WebSocket (incompatible with plain WS clients), slight overhead vs raw WS, no built-in state sync or game-specific features
- **Verdict**: Solid middle ground if building custom game logic. But for board games, Colyseus or boardgame.io are better because they add state sync and game concepts on top.

### Colyseus v0.17
- **Version**: `@colyseus/sdk` v0.17.35 (March 2026), 6.8k stars, 57 contributors
- **What**: Full multiplayer game framework — not just a WebSocket library
- **Transport**: Pluggable — ws (default), uWebSockets.js, WebTransport, Bun WebSockets, TCP
- **State Sync**: Automatic delta/patch synchronization via Schema system
- **Rooms**: First-class concept with full lifecycle, matchmaking, auto-dispose
- **Reconnection**: Built-in `allowReconnection()` with configurable timeout
- **Hidden Information**: StateView with `@view()` decorator for per-client state filtering
- **Scaling**: Redis-based horizontal scaling with seat reservation pattern
- **Verdict**: **Best general-purpose choice for board game multiplayer.** See deep dive below.

### PartyKit / PartyServer
- **Version**: Now under Cloudflare ownership (`cloudflare/partykit`), 5.5k stars
- **What**: Edge-first real-time platform built on Cloudflare Durable Objects
- **Client**: `partysocket` — dependency-free reconnecting WebSocket with React hook
- **Reconnection**: Automatic with exponential backoff (1-5s min, 10s max, 1.3 growth factor)
- **Rooms**: Each "party" is an isolated room with persistent storage
- **State**: In-memory + durable key-value storage per party
- **Verdict**: Excellent for collaborative apps. Less ideal for board games — no state sync schema, no game lifecycle, no matchmaking. See deep dive below.

### boardgame.io v0.50.2
- **Version**: v0.50.2 (November 2022 — **last release over 3 years ago**)
- **What**: Turn-based game engine with multiplayer built in
- **Transport**: Socket.IO under the hood
- **State Sync**: Full state sync with optimistic updates
- **Verdict**: Purpose-built for board games but **appears unmaintained**. Still a great architectural reference. See deep dive below.

### Recommendation Ranking for Board Games

| Rank | Library | Best For |
|------|---------|----------|
| 1 | **Colyseus** | General multiplayer board games, real-time + turn-based |
| 2 | **boardgame.io** | Pure turn-based games (if maintenance risk acceptable) |
| 3 | **Socket.IO + custom** | When you need full control over game architecture |
| 4 | **PartyKit** | Simple real-time games deployed to edge |
| 5 | **Bun native WS** | Performance-critical, simple message patterns |
| 6 | **ws/native** | Only if building a custom framework |

---

## 2. Server Authoritative vs Client Authoritative for Board Games

### Key Insight: Board Games Should Always Be Server Authoritative

Unlike FPS/action games where latency compensation creates complexity, board games are an **ideal fit** for pure server authority because:

1. **Low frequency of moves**: Players make discrete moves, not continuous input streams. A 50-200ms round trip is imperceptible when clicking to place a piece or play a card.
2. **Rule enforcement is critical**: Board games have complex, deterministic rules. The server MUST validate every move.
3. **Hidden information**: Card games, fog-of-war, and secret objectives require the server to be the single source of truth.
4. **No prediction needed**: Unlike FPS games, there's no need for client-side prediction, dead reckoning, or lag compensation.
5. **Cheat prevention**: With full server authority, cheating is eliminated for logic (clients can still automate, but can't fabricate state).

### Recommended Pattern for Board Games

```
Client sends:  { type: "playCard", cardId: 5, targetSlot: "B3" }
                           |
                           v
Server validates:  Is it this player's turn?
                   Does the player have card 5?
                   Is B3 a legal target?
                   Apply game rules
                           |
                           v
Server broadcasts: Updated state (delta) to all clients
                   Each client gets their filtered view (hidden info)
```

### Optimistic Updates (Optional, Use Sparingly)

boardgame.io's approach is instructive: clients run game logic locally in parallel with the server for responsiveness, but the server's state always wins. For board games, this is only useful for:
- Drag-and-drop animations (show the piece moving immediately)
- UI responsiveness (disable the played card immediately)
- NOT for game logic (never trust the client's computed next state)

---

## 3. State Synchronization Approaches

### Full State Sync
- **How**: Send the entire game state to all clients after every change
- **Pros**: Simple, no desync bugs, easy debugging
- **Cons**: Bandwidth scales with state size, wasteful for small changes
- **Good for**: Small board games (chess, tic-tac-toe), prototyping
- **Used by**: boardgame.io (with optimistic updates)

### Delta/Patch Sync (Recommended for Board Games)
- **How**: Track changes at the property level, send only modified fields
- **Pros**: Minimal bandwidth, scales well, handles complex state
- **Cons**: More complex implementation, need change tracking
- **Good for**: Medium to large board games, real-time elements
- **Used by**: **Colyseus** (its primary differentiator)

Colyseus implementation details:
- Each `Schema` instance maintains a `ChangeTree` tracking mutations
- Only the **latest** mutation per property is queued per patch interval
- Default `patchRate` is 50ms (20 patches/sec), configurable
- Each Schema instance gets a unique `refId` for client-side mapping
- Initial connection sends full state; subsequent updates are deltas only
- Bandwidth is proportional to change volume, not total state size

### Event Sourcing / Command Pattern
- **How**: Store and transmit a sequence of events/commands rather than state snapshots
- **Pros**: Full history, undo/redo, replay, debugging, small wire format
- **Cons**: State reconstruction cost, more complex architecture, potential divergence
- **Good for**: Turn-based games with undo, games needing replay
- **Used by**: boardgame.io (internally, enabling undo/redo and time-travel debugging), Board Game Arena (notification queue)

### CRDT (Conflict-free Replicated Data Types)
- **How**: Data structures that merge automatically without conflicts
- **Pros**: Works peer-to-peer, handles offline/partition gracefully, no central server needed
- **Cons**: Not designed for rule enforcement, hard to validate game rules, eventual consistency may produce invalid intermediate states
- **Good for**: Collaborative editing (whiteboards, documents), NOT board games
- **Library**: Yjs (most popular JS CRDT) — 50+ integrations, used by Linear and Figma
- **Verdict for board games**: **Not recommended.** Board games require authoritative rule validation that CRDTs cannot enforce. CRDTs solve a problem (conflict-free merging) that server-authoritative games don't have.

### Recommended Hybrid: Delta Sync + Event Messages

For board games, the best approach combines:
1. **Delta/patch sync for game state** (Colyseus Schema) — automatic, efficient, handles complex nested state
2. **Event messages for ephemeral actions** — chat, animations, sound triggers, notifications that shouldn't persist in state

```typescript
// State (synced automatically via delta patches)
class GameState extends Schema {
    @type({ map: Player }) players = new MapSchema<Player>();
    @type([ Card ]) board = new ArraySchema<Card>();
    @type("string") currentPhase: string;
    @type("number") turnNumber: number;
}

// Events (sent as one-off messages, not in state)
room.broadcast("animation", { type: "cardFlip", cardId: 5 });
room.broadcast("chat", { player: "Alice", text: "Good move!" });
```

---

## 4. Room/Lobby Management Patterns

### Colyseus Approach (Most Complete)

**Room Lifecycle**:
```typescript
// Server defines room types
defineServer({
  rooms: {
    "chess": ChessRoom,
    "poker": PokerRoom,
  }
});

// Client joins (auto-matchmaking)
const room = await client.joinOrCreate("chess", { ranked: true });

// Or join specific room (invite link)
const room = await client.joinById(roomId);
```

**Room Properties**:
- `maxClients`: Auto-locks room when full, auto-unlocks on disconnect
- `metadata`: Queryable matchmaking data (difficulty, map, etc.)
- `private`: Hide from matchmaking
- `locked/unlocked`: Manual removal from matchmaking pool
- `autoDispose`: Clean up when last player leaves (default: true)

**Matchmaking** (v0.17):
```typescript
// Update matchmaking criteria dynamically
await this.setMatchmaking({
    metadata: { difficulty: "hard", mapName: "castle" },
    private: false,
    maxClients: 4
});
```

**Spectators**: Any client joining without a `playerID` becomes a spectator in boardgame.io. In Colyseus, you implement this by checking a role in `onJoin()` and not creating a player entity.

### boardgame.io Lobby Pattern

REST API-based lobby:
- `POST /games/{name}/create` — Create a match with specified player count
- `POST /games/{name}/{id}/join` — Join with display name, get credentials
- `GET /games/{name}` — List available matches
- `POST /games/{name}/{id}/playAgain` — Rematch flow

Credentials are returned on join and required for all future move authentication.

### Board Game Arena Pattern

Server-side matchmaking with a table/lobby system:
- Players create or join "tables" from a central lobby
- The platform handles player-count requirements
- Games start when the table is full
- Real-time and turn-based modes supported on the same table system
- State machine transitions handle game flow automatically

### Recommended Lobby Architecture for Board Games

```
┌─────────────┐     REST API      ┌──────────────┐
│   Lobby UI   │◄────────────────►│  HTTP Server  │
│  (React)     │                  │  (list rooms, │
│              │                  │   create,     │
└──────┬───────┘                  │   join)       │
       │                          └──────┬────────┘
       │  WebSocket                      │
       │                          ┌──────▼────────┐
       └─────────────────────────►│  Game Room    │
                                  │  (Colyseus)   │
                                  │  - State sync │
                                  │  - Game logic │
                                  │  - Turns      │
                                  └───────────────┘
```

Key patterns:
1. **Lobby is HTTP/REST**, game rooms are WebSocket — separation of concerns
2. **Room codes** for private games (friends sharing a 4-letter code)
3. **Seat reservation** with timeout (Colyseus default: 15 seconds)
4. **Metadata-based filtering** for public matchmaking
5. **"Play Again" flow**: Create new room, migrate players from old room

---

## 5. Reconnection Handling

### Colyseus Reconnection (Best-in-Class)

**Server-side**:
```typescript
async onDrop(client: Client, code: number) {
    // Mark player as disconnected in state
    this.state.players.get(client.sessionId).connected = false;

    // Hold their seat for 60 seconds
    await this.allowReconnection(client, 60);
}

onReconnect(client: Client) {
    // Restore connected status
    this.state.players.get(client.sessionId).connected = true;
}

onLeave(client: Client, code: number) {
    // Only called after reconnection window expires, or voluntary leave
    this.state.players.delete(client.sessionId);
}
```

**Client-side** (v0.17 — automatic):
```typescript
// SDK auto-reconnects by default with these settings:
room.reconnection.maxRetries = 15;        // attempts
room.reconnection.minDelay = 100;         // ms
room.reconnection.maxDelay = 5000;        // ms
room.reconnection.minUptime = 5000;       // ms before reconnect allowed

// Messages sent during disconnection are queued (max 10 by default)
// Events: room.onDrop, room.onReconnect
```

Key design: In v0.17, `onDrop` (unexpected disconnect) is separated from `onLeave` (intentional departure). The `allowReconnection()` returns a Deferred that can be `.reject()`-ed to force-kick a player.

### PartySocket Reconnection

```typescript
const ws = new PartySocket({
    host: "...",
    room: "game-123",
    // Reconnection config:
    minReconnectionDelay: 1000,   // randomized 1-5s
    maxReconnectionDelay: 10000,
    reconnectionDelayGrowFactor: 1.3,
    maxRetries: Infinity,
    connectionTimeout: 4000,
});
// Messages buffered automatically during reconnection
```

PartySocket works as a standalone library with ANY WebSocket server, not just PartyKit.

### Board Game-Specific Reconnection Patterns

1. **Preserve player seat**: Don't remove the player from the game on disconnect. Mark them as "away" and give a generous timeout (30-120 seconds for board games — these aren't fast-paced).

2. **Full state on reconnect**: Send the complete game state on reconnection rather than trying to replay missed deltas. Colyseus handles this automatically — the handshake sends full state.

3. **Turn timer pausing**: If the disconnected player's turn is active, pause or extend the turn timer. Resume when they reconnect.

4. **AI takeover**: For competitive games, optionally let an AI play for a disconnected player after a timeout.

5. **Visual indicator**: Show other players a "Player X is reconnecting..." status so they know to wait.

6. **Graceful degradation**: If a player fails to reconnect within the timeout, let remaining players vote to: continue without them (AI takes over), abandon the game, or save and resume later.

---

## 6. Colyseus Deep Dive

### Architecture

```
┌──────────────────────────────────────────────────┐
│                  Colyseus Server                  │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │              Match Maker                     │ │
│  │   joinOrCreate / create / join / joinById    │ │
│  └──────────────────┬──────────────────────────┘ │
│                     │                             │
│  ┌──────────────────▼──────────────────────────┐ │
│  │    Room Instance (one per game session)      │ │
│  │                                              │ │
│  │  ┌────────────┐  ┌─────────────────────┐    │ │
│  │  │   State    │  │   Message Handlers  │    │ │
│  │  │  (Schema)  │  │   (validated w/     │    │ │
│  │  │            │  │    Zod schemas)     │    │ │
│  │  └──────┬─────┘  └─────────────────────┘    │ │
│  │         │                                    │ │
│  │  ┌──────▼─────────────────────────────────┐ │ │
│  │  │  ChangeTree (tracks property mutations) │ │ │
│  │  └──────┬─────────────────────────────────┘ │ │
│  │         │ @ patchRate (default 50ms)         │ │
│  │  ┌──────▼──────┐  ┌────────────────────┐   │ │
│  │  │ Delta Encode │  │  StateView Filter  │   │ │
│  │  │ (per-client) │  │  (hidden info)     │   │ │
│  │  └──────┬──────┘  └────────┬───────────┘   │ │
│  │         └──────────┬───────┘                │ │
│  │                    │ WebSocket               │ │
│  │         ┌──────────▼───────────┐            │ │
│  │         │   Transport Layer    │            │ │
│  │         │  ws | uWS | Bun     │            │ │
│  │         └──────────────────────┘            │ │
│  └──────────────────────────────────────────────┘ │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │  Presence (Redis) — for multi-process       │ │
│  │  Pub/Sub, matchmaking across processes      │ │
│  └─────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

### Schema System (The Core Innovation)

Colyseus's Schema is its most important feature for board games. It provides:

**Automatic delta sync** — Define your state with decorators, Colyseus handles encoding and transmission:
```typescript
class Card extends Schema {
    @type("string") suit: string;
    @type("number") value: number;
    @view() @type("boolean") faceUp: boolean = false;
}

class Player extends Schema {
    @type("string") name: string;
    @type("number") score: number = 0;
    @type([ Card ]) hand = new ArraySchema<Card>();
    @view() @type("number") secretObjective: number;
}

class GameState extends Schema {
    @type({ map: Player }) players = new MapSchema<Player>();
    @type([ Card ]) board = new ArraySchema<Card>();
    @type("string") phase: string = "waiting";
    @type("number") currentPlayerIndex: number = 0;
    @type("number") turnTimeRemaining: number = 0;
}
```

**Supported types**: string, number, boolean, int8/16/32/64, uint8/16/32/64, float32/64, bigInt64, bigUint64, plus complex types: ArraySchema, MapSchema, SetSchema, CollectionSchema, nested Schema classes.

**Limitations**:
- Max 64 synchronizable properties per Schema class (work around with nesting)
- MapSchema keys must be strings
- SetSchema and CollectionSchema are JavaScript SDK only
- Don't use Schema for messages (use `room.send()` / `room.broadcast()`)
- StateView not optimized for large datasets

### Hidden Information (StateView)

Critical for card games and games with private player data:
```typescript
class Player extends Schema {
    @type("string") name: string;           // visible to all
    @view() @type([ Card ]) hand = new ArraySchema<Card>();  // only visible via view
}

// In room:
onJoin(client, options) {
    const player = new Player();
    client.view = new StateView();
    client.view.add(player);  // This client sees their own hand
    // Other clients DON'T see this player's hand
}
```

Tagged views for multiple visibility levels:
```typescript
@view(1) @type("number") secretRole: number;  // Only visible with tag 1
client.view.add(player, 1);  // Grant tag-1 visibility
```

### Message Handling with Validation

```typescript
// Server-side with Zod validation
messages = {
    "playCard": validate(z.object({
        cardIndex: z.number().min(0).max(12),
        targetSlot: z.string()
    }), (client, payload) => {
        const player = this.state.players.get(client.sessionId);
        // Validate game rules...
        // Mutate state...
    }),

    "chat": (client, message) => {
        this.broadcast("chat", {
            player: client.sessionId,
            text: message
        });
    },

    "*": (client, type, payload) => {
        console.warn(`Unknown message type: ${type}`);
    }
}
```

### Performance Characteristics

- **1,000-2,000 CCU** per small cloud server (1 vCPU, 1 GB RAM) for simple games
- **2-5 KB memory per connection** (scales with state size)
- Default 50ms patch rate (20 patches/sec) — configurable, can be lowered for turn-based
- Horizontal scaling via Redis presence + driver

### When to Use Colyseus for Board Games

**Ideal for**:
- Card games (hidden hands via StateView)
- Strategy games (complex nested state, turn management)
- Real-time board games (timer-based, simultaneous actions)
- Games with spectators (viewers get filtered state)
- Games needing reconnection (built-in, robust)

**Less ideal for**:
- Purely peer-to-peer games (Colyseus is server-authoritative by design)
- Games with >64 properties per entity (Schema limit — mitigate with nesting)
- Serverless deployments (Colyseus needs a persistent process)

---

## 7. PartyKit / PartyServer Deep Dive

### Architecture

PartyKit is built on **Cloudflare Durable Objects**, providing globally distributed, stateful, on-demand servers. Each "party" is a lightweight server instance that:
- Maintains in-memory state across requests
- Has access to durable key-value storage (max 128 KiB per value)
- Supports both WebSocket and HTTP access to the same state
- Can hibernate between messages to reduce costs
- Runs close to users on Cloudflare's edge network

### PartyServer API

```typescript
import type * as Party from "partykit/server";

export default class GameRoom implements Party.Server {
    gameState: GameState;

    constructor(readonly room: Party.Room) {
        this.gameState = new GameState();
    }

    async onStart() {
        // Load persisted state
        const saved = await this.room.storage.get("state");
        if (saved) this.gameState = saved;
    }

    onConnect(conn: Party.Connection, ctx: Party.ConnectionContext) {
        // Send current state to new player
        conn.send(JSON.stringify({ type: "fullState", state: this.gameState }));
        this.room.broadcast(JSON.stringify({
            type: "playerJoined", id: conn.id
        }), [conn.id]);
    }

    async onMessage(message: string, sender: Party.Connection) {
        const action = JSON.parse(message);
        // Validate and apply...
        this.gameState = applyAction(this.gameState, action);
        // Persist
        await this.room.storage.put("state", this.gameState);
        // Broadcast
        this.room.broadcast(JSON.stringify({
            type: "stateUpdate",
            state: this.gameState
        }));
    }

    onClose(conn: Party.Connection) { /* cleanup */ }
}
```

### PartySocket Client (Works Anywhere)

```typescript
import PartySocket from "partysocket";

const ws = new PartySocket({
    host: "my-game.user.partykit.dev",
    room: "game-abc123",
});

// React hook
import usePartySocket from "partysocket/react";
const ws = usePartySocket({
    host: "...",
    room: "game-abc123",
    onMessage(e) {
        const update = JSON.parse(e.data);
        setGameState(update.state);
    }
});
```

### PartyKit vs Colyseus for Board Games

| Feature | Colyseus | PartyKit |
|---------|----------|----------|
| State sync | Automatic delta/patch (Schema) | Manual (send JSON yourself) |
| Hidden info | StateView with @view() | Manual filtering |
| Reconnection | Built-in allowReconnection() | PartySocket auto-reconnect (transport only) |
| Matchmaking | Built-in with metadata filtering | None (build yourself) |
| Room lifecycle | Full lifecycle hooks | onStart/onConnect/onMessage/onClose |
| Message validation | Zod integration | Manual |
| Deployment | Self-hosted or Colyseus Cloud | Cloudflare edge (managed) |
| Scaling | Redis + multiple processes | Automatic (Durable Objects) |
| Cost model | Server cost (always running) | Pay-per-use (hibernation) |
| Latency | Single server region | Edge (close to users globally) |
| CRDT support | No | y-partykit (Yjs integration) |

**Verdict**: PartyKit is simpler and cheaper for basic real-time features, but lacks game-specific primitives. You'd need to build state sync, matchmaking, hidden information filtering, and game lifecycle yourself. For a serious board game, Colyseus saves months of work. PartyKit shines for collaborative features (shared cursors, presence indicators) alongside a game, not as the game server itself.

**Exception**: If you want **serverless/edge deployment** and are willing to build game primitives on top, PartyKit's Durable Objects model is compelling for its automatic scaling and global distribution.

---

## 8. How Production Board Game Platforms Handle Networking

### Board Game Arena (BGA)

**Tech Stack**: PHP 8.4, MySQL 5.7, Dojo Toolkit 1.15

**Architecture**:
- **Server-side state machine** in PHP managing game flow
- States are typed: Active Player (single turn), Multiple Active Player (simultaneous), Game (automatic transitions), Private Parallel (async individual states)
- **Stateless request model**: New PHP class instance per request, state lives in MySQL
- **Database transactions**: All state changes are atomic — exceptions trigger full rollback
- **Notification queue**: All client updates flow through notifications, queued and sent at end of successful actions
- Public notifications (`notify->all()`) and private notifications (`notify->player()`) for hidden information
- **AJAX for actions**: Players trigger moves via HTTP requests, NOT WebSocket messages
- State synchronized through the notification system after server processes each action

**Key Insight**: BGA uses a **traditional web architecture** (PHP + MySQL + AJAX) rather than WebSockets for game logic. Real-time feeling comes from the notification queue pushing updates after each action completes. This works because board games are discrete-action-based, not continuous.

**Lessons**:
1. You don't strictly NEED WebSockets for turn-based board games — AJAX + server push works
2. Database transactions provide excellent atomicity guarantees for game state
3. The notification pattern (queue changes, send at end of successful action) prevents partial state updates
4. State machine is the right abstraction for board game flow

### boardgame.io (Open Source Reference)

**Architecture**:
- **Game defined as pure functions**: Moves are `({ G, ctx }) => { mutate G }` — side-effect free
- **Dual state model**: `G` (developer game state, must be JSON-serializable) + `ctx` (framework metadata: turn, currentPlayer, phase)
- **Phases → Turns → Stages**: Three-level hierarchy for game flow
  - Phases: Game-wide periods (e.g., "setup", "play", "scoring")
  - Turns: Player-specific, containing multiple moves
  - Stages: Sub-turn divisions allowing different move sets per player simultaneously
- **Server-authoritative with optimistic updates**: Clients run logic locally, server corrects
- **Secret state via playerView**: Server-side filtering function strips hidden data per player
- **Event sourcing**: Moves stored as events enabling undo/redo and time-travel debugging
- **Lobby**: REST API for match CRUD + React lobby component

**Transport**: Socket.IO under the hood, abstracted away.

**Lessons**:
1. Pure function moves are brilliant — easy to test, reason about, and replay
2. The Phase/Turn/Stage hierarchy elegantly models complex board game flow
3. `playerView` filtering is simple and effective for hidden information
4. Event sourcing enables powerful features (undo, replay, debugging) almost for free
5. **Caveat**: Last release was November 2022 (v0.50.2). Project appears dormant.

### TOSIOS (Open Source Colyseus Example)

A multiplayer browser shooter demonstrating Colyseus patterns:
- Monorepo with shared constants/methods between client and server
- Authoritative server validates all input
- Colyseus Schema for state, rooms for sessions
- Tiled Editor maps with collision layers
- Delta compression handles networking efficiently

---

## Recommended Architecture for a New Board Game (2025-2026)

### Stack

```
Client:  React/TypeScript + @colyseus/sdk v0.17
Server:  Node.js/TypeScript + Colyseus v0.17
Transport: ws (default) or Bun WebSockets for performance
Validation: Zod (integrated with Colyseus message handlers)
Deployment: Self-hosted (Docker + Nginx) or Colyseus Cloud
```

### Project Structure

```
packages/
├── shared/           # Shared between client and server
│   ├── schemas/      # Colyseus Schema definitions
│   │   ├── GameState.ts
│   │   ├── Player.ts
│   │   └── Card.ts
│   ├── constants.ts  # Game rules, limits
│   └── types.ts      # Message types, enums
├── server/
│   ├── rooms/
│   │   ├── GameRoom.ts       # Room with lifecycle hooks
│   │   └── LobbyRoom.ts     # Optional lobby room
│   ├── game/
│   │   ├── GameEngine.ts     # Core game logic (pure functions)
│   │   ├── TurnManager.ts    # Turn/phase management
│   │   └── Validator.ts      # Move validation
│   └── index.ts              # Server entry with defineServer()
└── client/
    ├── hooks/
    │   ├── useColyseus.ts    # Connection management
    │   └── useGameState.ts   # State subscription
    ├── components/
    │   ├── Lobby.tsx
    │   ├── GameBoard.tsx
    │   └── PlayerHand.tsx
    └── App.tsx
```

### Key Architectural Patterns

**1. Separate game logic from networking:**
```typescript
// game/GameEngine.ts — pure functions, easily testable
export function playCard(state: GameState, playerId: string, cardIndex: number): Result {
    const player = state.players.get(playerId);
    if (!player) return { ok: false, error: "Player not found" };
    if (state.currentPlayerId !== playerId) return { ok: false, error: "Not your turn" };
    if (cardIndex < 0 || cardIndex >= player.hand.length) return { ok: false, error: "Invalid card" };
    // Apply the move...
    return { ok: true };
}

// rooms/GameRoom.ts — networking wrapper
messages = {
    "playCard": validate(z.object({ cardIndex: z.number() }), (client, payload) => {
        const result = playCard(this.state, client.sessionId, payload.cardIndex);
        if (!result.ok) {
            client.send("error", result.error);
        }
        // State mutations in playCard() are automatically synced
    })
}
```

**2. Use StateView for hidden information:**
```typescript
onJoin(client, options) {
    const player = new Player();
    player.name = options.name;
    this.state.players.set(client.sessionId, player);

    // Each client sees only their own hand
    client.view = new StateView();
    client.view.add(player);  // Grants visibility to @view() fields
}
```

**3. Robust reconnection:**
```typescript
async onDrop(client, code) {
    const player = this.state.players.get(client.sessionId);
    if (player) {
        player.connected = false;
        // Pause turn timer if it's their turn
        if (this.state.currentPlayerId === client.sessionId) {
            this.pauseTurnTimer();
        }
    }
    try {
        await this.allowReconnection(client, 120); // 2 minutes for board games
    } catch {
        // Player didn't reconnect — handle cleanup in onLeave
    }
}

onReconnect(client) {
    const player = this.state.players.get(client.sessionId);
    if (player) {
        player.connected = true;
        if (this.state.currentPlayerId === client.sessionId) {
            this.resumeTurnTimer();
        }
    }
}
```

**4. Turn management via state machine pattern (inspired by BGA/boardgame.io):**
```typescript
type Phase = "lobby" | "setup" | "playing" | "scoring" | "finished";

// In your room, manage phase transitions:
private advanceTurn() {
    const playerIds = Array.from(this.state.players.keys());
    const currentIdx = playerIds.indexOf(this.state.currentPlayerId);
    const nextIdx = (currentIdx + 1) % playerIds.length;
    this.state.currentPlayerId = playerIds[nextIdx];
    this.state.turnNumber++;

    // Check for phase transitions
    if (this.checkGameEnd()) {
        this.state.phase = "scoring";
        this.calculateScores();
    }

    this.resetTurnTimer();
}
```

---

## Version Summary (as of March 2026)

| Library | Latest Version | Last Activity | License |
|---------|---------------|---------------|---------|
| Colyseus | @colyseus/sdk 0.17.35 | Mar 2026 (active) | MIT |
| Socket.IO | 4.x | Active | MIT |
| boardgame.io | 0.50.2 | Nov 2022 (dormant) | MIT |
| PartyKit | Under cloudflare/partykit | Active | MIT |
| ws | Actively maintained | Active | MIT |
| uWebSockets.js | Active | Active | Apache 2.0 |
| Yjs | Active | Active | MIT |
| partysocket | 0.0.33+ | Active | MIT |

---

## TL;DR Recommendation

**Use Colyseus v0.17** for multiplayer board games. It provides the most complete, actively-maintained solution with:
- Automatic delta state synchronization (Schema system)
- Per-client state filtering for hidden information (StateView)
- Built-in reconnection with configurable timeouts
- Room lifecycle and matchmaking
- Pluggable transports (ws, uWebSockets, Bun)
- Horizontal scaling via Redis
- Message validation with Zod
- TypeScript-first with full type safety

Study **boardgame.io's architecture** for game design patterns (phases/turns/stages, pure function moves, playerView filtering, event sourcing for undo) even though the library itself is unmaintained. These patterns can be implemented on top of Colyseus.

Use **PartySocket** (from PartyKit) as your client-side WebSocket wrapper even with Colyseus — it's dependency-free, has excellent reconnection, and provides a React hook. Or use Colyseus's built-in client SDK which now has comparable reconnection in v0.17.

Avoid CRDTs (Yjs) for game state — they solve the wrong problem for authoritative games. Consider them only for collaborative side-features (shared note-taking, collaborative strategy planning).
