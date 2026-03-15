# Lobby and Matchmaking

## Lobby Architecture

The lobby is a separate Colyseus room (or uses the built-in `LobbyRoom`) that manages the pre-game experience: browsing rooms, creating rooms, joining, and ready-checking.

```
┌─────────────────────────────────────────────────┐
│                  LOBBY FLOW                      │
│                                                  │
│  Main Menu                                       │
│    ├── Quick Play ──→ Auto-join or create room   │
│    ├── Browse Games ──→ Room list with filters   │
│    ├── Create Game ──→ Configure + get room code │
│    ├── Join by Code ──→ Enter 4-char code        │
│    └── Resume Game ──→ Rejoin in-progress game   │
│                                                  │
│  In Room (pre-game)                              │
│    ├── Player list with ready status             │
│    ├── Game settings (host can modify)           │
│    ├── Chat                                      │
│    ├── Add Bot button                            │
│    ├── Ready / Unready toggle                    │
│    └── Start Game (when all ready)               │
└─────────────────────────────────────────────────┘
```

---

## Room Browser

### Server: Listing Available Rooms

Colyseus provides a built-in lobby mechanism, or you can query rooms directly.

```typescript
// Using Colyseus built-in LobbyRoom
import { LobbyRoom } from "colyseus";

// In server setup
server.define("lobby", LobbyRoom);

// Game rooms auto-register with the lobby when you set metadata
server.define("game", GameRoom)
  .enableRealtimeListing(); // Rooms appear in lobby automatically
```

### Client: Room List UI

```typescript
// packages/client/src/lobby/lobby-ui.ts
import { Client, RoomAvailable } from "colyseus.js";

interface RoomListEntry {
  roomId: string;
  gameType: string;
  playerCount: number;
  maxPlayers: number;
  hostName: string;
  roomCode: string;
  status: "waiting" | "playing";
  createdAt: number;
}

class LobbyUI {
  private client: Client;
  private lobby: Room | null = null;
  private rooms: RoomListEntry[] = [];

  constructor(client: Client) {
    this.client = client;
  }

  async connect() {
    // Join the lobby room for real-time room updates
    this.lobby = await this.client.joinOrCreate("lobby");

    // Listen for room list changes
    this.lobby.onMessage("rooms", (rooms: RoomAvailable[]) => {
      this.rooms = rooms.map(r => ({
        roomId: r.roomId,
        gameType: r.metadata?.gameType || "unknown",
        playerCount: r.clients,
        maxPlayers: r.maxClients,
        hostName: r.metadata?.hostName || "Unknown",
        roomCode: r.metadata?.code || "",
        status: r.metadata?.status || "waiting",
        createdAt: r.metadata?.createdAt || 0,
      }));
      this.renderRoomList();
    });

    this.lobby.onMessage("+", ([roomId, room]: [string, RoomAvailable]) => {
      // Room added or updated
      this.updateRoom(roomId, room);
      this.renderRoomList();
    });

    this.lobby.onMessage("-", (roomId: string) => {
      // Room removed
      this.rooms = this.rooms.filter(r => r.roomId !== roomId);
      this.renderRoomList();
    });
  }

  private renderRoomList() {
    const container = document.getElementById("room-list")!;
    container.innerHTML = "";

    const waitingRooms = this.rooms
      .filter(r => r.status === "waiting")
      .sort((a, b) => b.createdAt - a.createdAt);

    if (waitingRooms.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <p>No games available</p>
          <button id="create-game-btn" class="primary-btn">Create a Game</button>
        </div>
      `;
      return;
    }

    for (const room of waitingRooms) {
      const card = document.createElement("div");
      card.className = "room-card";
      card.innerHTML = `
        <div class="room-info">
          <span class="room-type">${room.gameType}</span>
          <span class="room-host">Hosted by ${room.hostName}</span>
        </div>
        <div class="room-players">
          ${room.playerCount}/${room.maxPlayers} players
        </div>
        <button class="join-btn" data-room-id="${room.roomId}">Join</button>
      `;
      container.appendChild(card);
    }
  }

  async joinRoom(roomId: string): Promise<Room> {
    // Leave lobby before joining game
    this.lobby?.leave();
    return this.client.joinById(roomId);
  }

  disconnect() {
    this.lobby?.leave();
  }
}
```

---

## Room Creation

### Create Room Flow

```typescript
interface CreateRoomOptions {
  gameType: string;
  maxPlayers: number;
  isPrivate: boolean;
  turnTimeLimit: number;    // 0 = unlimited
  displayName: string;
  allowSpectators: boolean;
}

async function createRoom(client: Client, options: CreateRoomOptions): Promise<Room> {
  const room = await client.create("game", {
    gameType: options.gameType,
    maxPlayers: options.maxPlayers,
    isPrivate: options.isPrivate,
    turnTimeLimit: options.turnTimeLimit,
    displayName: options.displayName,
    allowSpectators: options.allowSpectators,
  });

  return room;
}
```

### Server: Room Creation Handler

```typescript
// In GameRoom
onCreate(options: any) {
  this.setState(new GameState());
  this.maxClients = options.maxPlayers || 2;
  this.state.roomCode = this.generateRoomCode();
  this.state.gameType = options.gameType;

  // Set metadata for lobby listing
  this.setMetadata({
    gameType: options.gameType,
    code: this.state.roomCode,
    hostName: "waiting...",  // Updated when first player joins
    maxPlayers: this.maxClients,
    status: "waiting",
    isPrivate: options.isPrivate || false,
    allowSpectators: options.allowSpectators !== false,
    createdAt: Date.now(),
  });

  // Private rooms don't appear in the lobby
  if (options.isPrivate) {
    this.setPrivate(true);
  }

  this.registerMessageHandlers();
}
```

---

## Room Codes

4-character alphanumeric codes for sharing with friends. Avoid ambiguous characters (0/O, 1/I/L).

```typescript
// Server-side code generation
function generateRoomCode(): string {
  const chars = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"; // No O, 0, I, 1, L
  let code: string;
  do {
    code = Array.from({ length: 4 }, () =>
      chars[Math.floor(Math.random() * chars.length)]
    ).join("");
  } while (isCodeInUse(code)); // Ensure uniqueness
  return code;
}

// Track active codes
const activeCodes = new Set<string>();

function isCodeInUse(code: string): boolean {
  return activeCodes.has(code);
}
```

### Client: Join by Code

```typescript
async function joinByCode(client: Client, code: string): Promise<Room> {
  // Normalize input
  const normalizedCode = code.toUpperCase().trim();

  if (!/^[A-Z0-9]{4}$/.test(normalizedCode)) {
    throw new Error("Invalid room code format");
  }

  // Find room with this code
  const rooms = await client.getAvailableRooms("game");
  const room = rooms.find(r => r.metadata?.code === normalizedCode);

  if (!room) {
    throw new Error("Room not found. Check the code and try again.");
  }

  if (room.clients >= room.maxClients) {
    throw new Error("Room is full.");
  }

  return client.joinById(room.roomId);
}
```

---

## Quick Match / Matchmaking

### Simple Quick Match

Join the first available room, or create one if none exists:

```typescript
async function quickMatch(client: Client, gameType: string, displayName: string): Promise<Room> {
  try {
    // joinOrCreate: join an available room, or create a new one
    return await client.joinOrCreate("game", {
      gameType,
      displayName,
    });
  } catch (error) {
    throw new Error("Failed to find a game. Please try again.");
  }
}
```

### Skill-Based Matchmaking

For games with rankings:

```typescript
// Server: custom matchmaking in filterBy
server.define("game", GameRoom)
  .filterBy(["gameType", "skillBracket"]);

// Client: include skill bracket
async function rankedMatch(client: Client, gameType: string, playerRating: number): Promise<Room> {
  // Bracket into skill tiers
  const bracket = Math.floor(playerRating / 200) * 200; // 0-199, 200-399, etc.

  return client.joinOrCreate("game", {
    gameType,
    skillBracket: bracket,
  });
}
```

### Expanding Search (if no match found)

```typescript
async function expandingMatch(
  client: Client,
  gameType: string,
  rating: number,
  maxWaitMs: number = 30000
): Promise<Room> {
  const startTime = Date.now();
  let bracketWidth = 200;

  while (Date.now() - startTime < maxWaitMs) {
    const minRating = Math.max(0, rating - bracketWidth);
    const maxRating = rating + bracketWidth;

    const rooms = await client.getAvailableRooms("game");
    const match = rooms.find(r =>
      r.metadata?.gameType === gameType &&
      r.metadata?.avgRating >= minRating &&
      r.metadata?.avgRating <= maxRating &&
      r.clients < r.maxClients
    );

    if (match) {
      return client.joinById(match.roomId);
    }

    // Widen search
    bracketWidth += 100;
    await new Promise(r => setTimeout(r, 2000));
  }

  // Create a new room after timeout
  return client.create("game", { gameType, avgRating: rating });
}
```

---

## Ready Check System

All players must confirm readiness before the game starts. This prevents AFK players from ruining the experience.

```typescript
// Server-side ready check
class ReadyCheckManager {
  private readyTimeout: ReturnType<typeof setTimeout> | null = null;

  constructor(private room: GameRoom) {}

  startReadyCheck() {
    this.room.state.phase = "ready_check";

    // All players must ready up within 30 seconds
    this.readyTimeout = setTimeout(() => {
      this.handleReadyTimeout();
    }, 30_000);

    this.room.broadcast("notification", {
      type: "ready_check",
      message: "Game is about to start! Press Ready.",
      timeoutMs: 30_000,
    });
  }

  playerReady(sessionId: string) {
    const player = this.room.state.players.get(sessionId);
    if (!player) return;
    player.ready = true;

    if (this.allReady()) {
      this.clearTimeout();
      this.room.startGame();
    }
  }

  playerUnready(sessionId: string) {
    const player = this.room.state.players.get(sessionId);
    if (!player) return;
    player.ready = false;
  }

  private allReady(): boolean {
    for (const [, player] of this.room.state.players) {
      if (!player.ready && !player.isBot) return false;
    }
    return true;
  }

  private handleReadyTimeout() {
    // Kick unready players and go back to waiting
    for (const [sessionId, player] of this.room.state.players) {
      if (!player.ready && !player.isBot) {
        const client = this.room.clients.find(c => c.sessionId === sessionId);
        client?.send("notification", {
          type: "kicked",
          message: "Removed for not readying up in time.",
        });
        client?.leave(1000); // Intentional disconnect code
      }
    }

    this.room.state.phase = "waiting";
  }

  private clearTimeout() {
    if (this.readyTimeout) {
      clearTimeout(this.readyTimeout);
      this.readyTimeout = null;
    }
  }
}
```

### Client: Ready Check UI

```typescript
function showReadyCheck(room: Room, timeoutMs: number) {
  const overlay = document.createElement("div");
  overlay.className = "ready-check-overlay";
  overlay.innerHTML = `
    <div class="ready-check-modal">
      <h2>Game Starting!</h2>
      <p>All players must ready up</p>
      <div class="player-ready-list" id="ready-list"></div>
      <div class="ready-timer" id="ready-timer"></div>
      <button id="ready-btn" class="ready-btn">Ready</button>
    </div>
  `;

  document.body.appendChild(overlay);

  // Ready button
  const btn = document.getElementById("ready-btn")!;
  let isReady = false;
  btn.addEventListener("click", () => {
    isReady = !isReady;
    room.send(isReady ? "ready" : "unready");
    btn.textContent = isReady ? "Waiting..." : "Ready";
    btn.classList.toggle("ready-active", isReady);
  });

  // Countdown timer
  const timerEl = document.getElementById("ready-timer")!;
  const endTime = Date.now() + timeoutMs;
  const timerInterval = setInterval(() => {
    const remaining = Math.max(0, Math.ceil((endTime - Date.now()) / 1000));
    timerEl.textContent = `${remaining}s`;
    if (remaining <= 0) clearInterval(timerInterval);
  }, 100);

  // Update player ready states from schema
  room.state.players.forEach((player, sessionId) => {
    player.listen("ready", (ready) => {
      updateReadyList(sessionId, player.displayName, ready);
    });
  });

  // Clean up when game starts
  room.state.listen("phase", (phase) => {
    if (phase === "playing" || phase === "setup") {
      clearInterval(timerInterval);
      overlay.remove();
    }
  });
}
```

---

## Spectator Mode

Spectators see the game state but cannot make moves.

### Server: Spectator Handling

```typescript
// In GameRoom
onJoin(client: Client, options: any) {
  if (options.spectate) {
    // Don't add as player, just let them receive state
    client.send("notification", {
      type: "spectating",
      message: "You are watching this game.",
    });

    // Optionally track spectator count
    this.state.spectatorCount = this.clients.length - this.state.players.size;
    return;
  }

  if (this.state.players.size >= this.maxClients) {
    // Room full — offer spectator mode
    if (this.metadata.allowSpectators) {
      client.send("notification", {
        type: "room_full",
        message: "Room is full. You are now spectating.",
      });
      this.state.spectatorCount++;
      return;
    }
    throw new Error("Room is full");
  }

  // Add as player (normal join)
  const player = new Player();
  player.sessionId = client.sessionId;
  player.displayName = options.displayName || `Player ${this.state.players.size + 1}`;
  player.color = this.assignColor();
  this.state.players.set(client.sessionId, player);
}

// Prevent spectators from sending game messages
private registerMessageHandlers() {
  this.onMessage("move", (client, data) => {
    if (!this.state.players.has(client.sessionId)) {
      client.send("error", { message: "Spectators cannot make moves" });
      return;
    }
    this.handleMove(client, data);
  });
}
```

### Client: Spectator UI

```typescript
function initSpectatorMode(room: Room) {
  // Disable all interactive elements
  document.querySelectorAll(".piece").forEach(el => {
    (el as HTMLElement).style.pointerEvents = "none";
    (el as HTMLElement).style.cursor = "default";
  });

  // Show spectator banner
  const banner = document.createElement("div");
  banner.className = "spectator-banner";
  banner.textContent = "Spectating";
  document.body.appendChild(banner);

  // Spectators can still chat (if allowed)
  // Hide move-related UI (undo button, forfeit, etc.)
  document.getElementById("game-controls")?.classList.add("hidden");
}
```

---

## Chat System

In-game chat alongside gameplay.

### Server: Chat with Rate Limiting

```typescript
class ChatManager {
  private messageCounts = new Map<string, { count: number; resetAt: number }>();
  private readonly MAX_MESSAGES_PER_MINUTE = 30;

  handleMessage(room: Room, client: Client, text: string) {
    // Sanitize
    const sanitized = text.trim().slice(0, 500);
    if (!sanitized) return;

    // Rate limit
    if (this.isRateLimited(client.sessionId)) {
      client.send("error", { message: "Slow down! Too many messages." });
      return;
    }

    // Broadcast to all clients in the room
    room.broadcast("chat", {
      from: client.sessionId,
      displayName: room.state.players.get(client.sessionId)?.displayName || "Spectator",
      text: sanitized,
      timestamp: Date.now(),
    });
  }

  private isRateLimited(sessionId: string): boolean {
    const now = Date.now();
    const entry = this.messageCounts.get(sessionId);

    if (!entry || now >= entry.resetAt) {
      this.messageCounts.set(sessionId, { count: 1, resetAt: now + 60_000 });
      return false;
    }

    entry.count++;
    return entry.count > this.MAX_MESSAGES_PER_MINUTE;
  }
}
```

### Quick Chat (Predefined Messages)

For mobile-friendly communication without a keyboard:

```typescript
const QUICK_CHAT_OPTIONS = [
  { id: "gg", text: "Good game!" },
  { id: "gl", text: "Good luck!" },
  { id: "nice", text: "Nice move!" },
  { id: "thinking", text: "Thinking..." },
  { id: "oops", text: "Oops!" },
  { id: "rematch", text: "Rematch?" },
];

function renderQuickChat(room: Room, container: HTMLElement) {
  const bar = document.createElement("div");
  bar.className = "quick-chat-bar";

  for (const option of QUICK_CHAT_OPTIONS) {
    const btn = document.createElement("button");
    btn.className = "quick-chat-btn";
    btn.textContent = option.text;
    btn.addEventListener("click", () => {
      room.send("chat", { text: option.text, isQuickChat: true });
    });
    bar.appendChild(btn);
  }

  container.appendChild(bar);
}
```

---

## Rematch Flow

After a game ends, players can request a rematch without going back to the lobby.

```typescript
// Server
class RematchManager {
  private rematchVotes = new Set<string>();

  requestRematch(sessionId: string, room: GameRoom) {
    this.rematchVotes.add(sessionId);

    room.broadcast("notification", {
      type: "rematch_request",
      by: sessionId,
      votes: this.rematchVotes.size,
      needed: room.state.players.size,
    });

    if (this.rematchVotes.size === room.state.players.size) {
      this.startRematch(room);
    }
  }

  private startRematch(room: GameRoom) {
    // Reset game state
    room.state.phase = "waiting";
    room.state.winner = "";
    room.state.turnNumber = 0;
    room.state.moveHistory.clear();
    room.state.pieces.clear();

    // Reset player readiness
    for (const [, player] of room.state.players) {
      player.ready = false;
    }

    // Swap colors/positions for fairness
    this.swapPlayerColors(room);

    this.rematchVotes.clear();

    // Go straight to ready check
    room.readyCheck.startReadyCheck();
  }

  private swapPlayerColors(room: GameRoom) {
    const players = Array.from(room.state.players.values());
    if (players.length === 2) {
      const tmp = players[0].color;
      players[0].color = players[1].color;
      players[1].color = tmp;
    }
  }
}
```

---

## Authentication (Lightweight)

For casual browser games, full auth is usually overkill. Use anonymous sessions with optional upgrade.

### Anonymous Session Tokens

```typescript
// Client: generate or retrieve session token
function getSessionToken(): string {
  let token = localStorage.getItem("game_session_token");
  if (!token) {
    token = crypto.randomUUID();
    localStorage.setItem("game_session_token", token);
  }
  return token;
}

function getDisplayName(): string {
  return localStorage.getItem("display_name") || generateRandomName();
}

// Include in room join options
const room = await client.joinOrCreate("game", {
  sessionToken: getSessionToken(),
  displayName: getDisplayName(),
});
```

### Random Name Generator

```typescript
const ADJECTIVES = [
  "Swift", "Bold", "Clever", "Lucky", "Mighty",
  "Noble", "Quick", "Sharp", "Steady", "Brave",
];

const ANIMALS = [
  "Fox", "Bear", "Hawk", "Wolf", "Deer",
  "Eagle", "Lion", "Otter", "Panda", "Tiger",
];

function generateRandomName(): string {
  const adj = ADJECTIVES[Math.floor(Math.random() * ADJECTIVES.length)];
  const animal = ANIMALS[Math.floor(Math.random() * ANIMALS.length)];
  const num = Math.floor(Math.random() * 100);
  return `${adj}${animal}${num}`;
}
```
