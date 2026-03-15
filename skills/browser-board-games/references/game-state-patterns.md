# Game State Patterns

## State Machine for Game Phases

Every board game follows a lifecycle of phases. Model these explicitly with a state machine.

### Phase Definitions

```typescript
// packages/shared/src/types.ts

export type GamePhase =
  | "waiting"       // Room created, waiting for players
  | "ready_check"   // All slots filled, confirming readiness
  | "setup"         // Game-specific setup (draft, deal cards, place pieces)
  | "playing"       // Main game loop
  | "paused"        // Player disconnected, waiting for reconnect
  | "finished";     // Game over

export type TurnPhase =
  | "action"        // Player's main action
  | "reaction"      // Other players can respond
  | "resolution"    // Resolve effects
  | "cleanup";      // End-of-turn bookkeeping

export interface PhaseTransition {
  from: GamePhase;
  to: GamePhase;
  condition: (state: GameState) => boolean;
  onTransition?: (state: GameState) => void;
}
```

### Phase Machine Implementation

```typescript
class PhaseMachine {
  private transitions: PhaseTransition[] = [];

  constructor(private state: GameState) {}

  addTransition(transition: PhaseTransition) {
    this.transitions.push(transition);
    return this;
  }

  tryTransition(): boolean {
    const available = this.transitions.filter(
      t => t.from === this.state.phase && t.condition(this.state)
    );

    if (available.length === 0) return false;

    const transition = available[0];
    transition.onTransition?.(this.state);
    this.state.phase = transition.to;
    return true;
  }
}

// Usage: define transitions for your game
const phases = new PhaseMachine(gameState)
  .addTransition({
    from: "waiting",
    to: "ready_check",
    condition: (s) => s.players.size >= s.minPlayers,
    onTransition: (s) => broadcastNotification("All players joined! Ready up."),
  })
  .addTransition({
    from: "ready_check",
    to: "setup",
    condition: (s) => allPlayersReady(s),
    onTransition: (s) => initializeGame(s),
  })
  .addTransition({
    from: "setup",
    to: "playing",
    condition: (s) => setupComplete(s),
    onTransition: (s) => startFirstTurn(s),
  })
  .addTransition({
    from: "playing",
    to: "finished",
    condition: (s) => checkWinCondition(s) !== null,
    onTransition: (s) => { s.winner = checkWinCondition(s)!; },
  });
```

---

## Command Pattern for Moves

Model every game action as a command object. This gives you: undo/redo, move replay, server validation, and game history for free.

### Move Interface

```typescript
// packages/shared/src/types.ts

export interface GameMove {
  type: string;                    // "place_piece", "play_card", "roll_dice", etc.
  playerId: string;
  timestamp: number;
  data: Record<string, unknown>;   // Move-specific payload
}

export interface MoveResult {
  valid: boolean;
  reason?: string;                 // Why it was rejected
  moveId?: string;                 // Unique ID for this move
  events?: GameEvent[];            // Side effects (captures, draws, etc.)
  gameOver?: boolean;
  winner?: string;
}

export interface GameEvent {
  type: string;                    // "piece_captured", "card_drawn", "score_changed"
  data: Record<string, unknown>;
}
```

### Game Engine Interface

```typescript
// packages/shared/src/engine.ts

export interface GameEngine {
  /** Get current game state (read-only view) */
  getState(): Readonly<GameState>;

  /** Get all valid moves for a player */
  getValidMoves(playerId: string): GameMove[];

  /** Check if a specific move is valid without applying it */
  isValidMove(move: GameMove): boolean;

  /** Apply a move and return the result */
  applyMove(move: GameMove): MoveResult;

  /** Undo the last move (if allowed by game rules) */
  undoLastMove(): boolean;

  /** Get move history */
  getMoveHistory(): GameMove[];
}
```

### Engine Implementation Pattern

```typescript
export class BoardGameEngine implements GameEngine {
  private state: GameState;
  private moveHistory: GameMove[] = [];
  private undoStack: GameState[] = [];     // Snapshots for undo

  constructor(initialState: GameState) {
    this.state = structuredClone(initialState);
  }

  getValidMoves(playerId: string): GameMove[] {
    if (this.state.currentTurn !== playerId) return [];
    // Delegate to game-specific move generation
    return this.generateMoves(playerId);
  }

  isValidMove(move: GameMove): boolean {
    if (this.state.phase !== "playing") return false;
    if (this.state.currentTurn !== move.playerId) return false;
    // Delegate to game-specific validation
    return this.validateMove(move);
  }

  applyMove(move: GameMove): MoveResult {
    if (!this.isValidMove(move)) {
      return { valid: false, reason: "Invalid move" };
    }

    // Save state for undo
    this.undoStack.push(structuredClone(this.state));

    // Apply the move (game-specific)
    const events = this.executeMove(move);

    // Record in history
    this.moveHistory.push(move);

    // Check win condition
    const winner = this.checkWinCondition();
    if (winner) {
      this.state.phase = "finished";
      this.state.winner = winner;
      return {
        valid: true,
        moveId: String(this.moveHistory.length),
        events,
        gameOver: true,
        winner,
      };
    }

    // Advance turn
    this.advanceTurn();

    return {
      valid: true,
      moveId: String(this.moveHistory.length),
      events,
    };
  }

  undoLastMove(): boolean {
    if (this.undoStack.length === 0) return false;
    this.state = this.undoStack.pop()!;
    this.moveHistory.pop();
    return true;
  }

  // --- Override these for your specific game ---

  protected generateMoves(playerId: string): GameMove[] {
    throw new Error("Implement in subclass");
  }

  protected validateMove(move: GameMove): boolean {
    throw new Error("Implement in subclass");
  }

  protected executeMove(move: GameMove): GameEvent[] {
    throw new Error("Implement in subclass");
  }

  protected checkWinCondition(): string | null {
    throw new Error("Implement in subclass");
  }

  protected advanceTurn(): void {
    const playerIds = Array.from(this.state.players.keys());
    const currentIndex = playerIds.indexOf(this.state.currentTurn);
    this.state.currentTurn = playerIds[(currentIndex + 1) % playerIds.length];
    this.state.turnNumber++;
  }
}
```

---

## Hidden Information

Games with hidden information (card hands, fog of war) require careful architecture. The key rule: **the server never sends hidden data to unauthorized clients**.

### Architecture Patterns

**Pattern 1: Colyseus Schema Filters (Recommended)**

Use `@filter` decorators to control what each client sees. Colyseus evaluates filters server-side before sending state patches.

```typescript
class Card extends Schema {
  @type("string") id: string = "";
  @type("string") owner: string = "";
  @type("boolean") faceUp: boolean = false;

  @filter(function(this: Card, client: Client) {
    // Only owner sees the value of face-down cards
    return this.faceUp || this.owner === client.sessionId;
  })
  @type("string") suit: string = "";

  @filter(function(this: Card, client: Client) {
    return this.faceUp || this.owner === client.sessionId;
  })
  @type("string") rank: string = "";
}
```

**Pattern 2: Separate State Views**

For complex hidden information, compute per-player state views:

```typescript
function getPlayerView(fullState: GameState, playerId: string): PlayerGameView {
  return {
    ...fullState,
    // Replace other players' hands with card counts
    players: fullState.players.map(p => ({
      ...p,
      hand: p.id === playerId
        ? p.hand  // Full hand for this player
        : p.hand.map(card => ({ id: card.id, hidden: true })),  // Hidden
    })),
    // Hide face-down deck cards
    deck: { count: fullState.deck.length },
    // Show discard pile (public)
    discardPile: fullState.discardPile,
  };
}
```

**Pattern 3: Message-Based Reveals**

Send private information via direct messages instead of shared state:

```typescript
// Server: deal cards privately
function dealCards(room: GameRoom) {
  for (const [sessionId, player] of room.state.players) {
    const hand = drawCards(room.state.deck, 5);
    player.handSize = hand.length; // Public: how many cards they have

    // Private: send actual cards only to this player
    room.clients.find(c => c.sessionId === sessionId)?.send("dealt_cards", {
      cards: hand.map(c => ({ id: c.id, suit: c.suit, rank: c.rank })),
    });
  }
}
```

---

## Random Number Generation

Multiplayer games need deterministic, verifiable randomness.

### Seeded RNG

```typescript
// Simple mulberry32 PRNG — deterministic given a seed
function createRNG(seed: number): () => number {
  let state = seed;
  return () => {
    state |= 0;
    state = (state + 0x6d2b79f5) | 0;
    let t = Math.imul(state ^ (state >>> 15), 1 | state);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Usage in game engine
class GameEngine {
  private rng: () => number;

  constructor(seed: number) {
    this.rng = createRNG(seed);
  }

  rollDice(sides: number): number {
    return Math.floor(this.rng() * sides) + 1;
  }

  shuffleDeck<T>(deck: T[]): T[] {
    const shuffled = [...deck];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(this.rng() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }

  drawRandom<T>(array: T[]): T {
    return array[Math.floor(this.rng() * array.length)];
  }
}
```

### Server-Side Roll Pattern

For games where randomness must be hidden until revealed (rolling dice for an attack):

```typescript
// Server generates the random value
onMessage("roll_dice", (client, data) => {
  const result = this.engine.rollDice(6);
  // Store result in state — it gets synced to all clients
  this.state.lastDiceRoll = result;
  this.state.lastRoller = client.sessionId;
  // Client animations trigger from state change listener
});
```

---

## Turn and Timer Management

### Turn Structure

```typescript
interface TurnManager {
  currentPlayer: string;
  turnNumber: number;
  turnPhase: TurnPhase;
  turnTimeLimit: number;       // ms, 0 = unlimited
  turnStartedAt: number;       // timestamp

  startTurn(playerId: string): void;
  endTurn(): void;
  checkTimeout(): boolean;
}

class BasicTurnManager implements TurnManager {
  currentPlayer: string = "";
  turnNumber: number = 0;
  turnPhase: TurnPhase = "action";
  turnTimeLimit: number;
  turnStartedAt: number = 0;

  private playerOrder: string[];
  private currentIndex: number = 0;

  constructor(players: string[], timeLimit: number = 0) {
    this.playerOrder = players;
    this.turnTimeLimit = timeLimit;
  }

  startTurn(playerId: string) {
    this.currentPlayer = playerId;
    this.turnPhase = "action";
    this.turnStartedAt = Date.now();
    this.turnNumber++;
  }

  endTurn() {
    this.currentIndex = (this.currentIndex + 1) % this.playerOrder.length;
    this.startTurn(this.playerOrder[this.currentIndex]);
  }

  checkTimeout(): boolean {
    if (this.turnTimeLimit <= 0) return false;
    return Date.now() - this.turnStartedAt >= this.turnTimeLimit;
  }

  getRemainingTime(): number {
    if (this.turnTimeLimit <= 0) return Infinity;
    return Math.max(0, this.turnTimeLimit - (Date.now() - this.turnStartedAt));
  }
}
```

### Chess Clock

```typescript
class ChessClock {
  private times: Map<string, number>;     // Remaining time per player in ms
  private activePlayer: string | null = null;
  private lastTick: number = 0;
  private increment: number;               // Time added after each move (Fischer)

  constructor(players: string[], initialTime: number, increment: number = 0) {
    this.times = new Map(players.map(p => [p, initialTime]));
    this.increment = increment;
  }

  start(playerId: string) {
    this.activePlayer = playerId;
    this.lastTick = Date.now();
  }

  switchTo(playerId: string) {
    if (this.activePlayer) {
      this.tick(); // Update outgoing player's time
      // Add increment to player who just moved
      const remaining = this.times.get(this.activePlayer)!;
      this.times.set(this.activePlayer, remaining + this.increment);
    }
    this.activePlayer = playerId;
    this.lastTick = Date.now();
  }

  tick(): void {
    if (!this.activePlayer) return;
    const now = Date.now();
    const elapsed = now - this.lastTick;
    const remaining = this.times.get(this.activePlayer)! - elapsed;
    this.times.set(this.activePlayer, Math.max(0, remaining));
    this.lastTick = now;
  }

  getTime(playerId: string): number {
    if (playerId === this.activePlayer) {
      // Account for time since last tick
      const elapsed = Date.now() - this.lastTick;
      return Math.max(0, this.times.get(playerId)! - elapsed);
    }
    return this.times.get(playerId) || 0;
  }

  isExpired(playerId: string): boolean {
    return this.getTime(playerId) <= 0;
  }

  pause() {
    this.tick();
    this.activePlayer = null;
  }
}
```

### Server Timer Tick

```typescript
// In GameRoom
onCreate(options: any) {
  // ...
  this.clock = new ChessClock(playerIds, 5 * 60 * 1000, 5000); // 5min + 5s increment

  // Tick timer every second and broadcast remaining times
  this.setSimulationInterval(() => {
    if (this.state.phase !== "playing") return;

    this.clock.tick();

    // Update schema state for all players
    for (const [sessionId, player] of this.state.players) {
      player.timeRemainingMs = this.clock.getTime(sessionId);
    }

    // Check for timeout
    if (this.clock.isExpired(this.state.currentTurn)) {
      this.handleTimeout(this.state.currentTurn);
    }
  }, 1000);
}
```

---

## AI / Bot Players

Design the game engine so AI players use the exact same interface as human players. This makes bots trivially pluggable.

### Bot Interface

```typescript
interface BotPlayer {
  /** Given the game state, choose a move */
  chooseMove(state: Readonly<GameState>, playerId: string): GameMove;
}

// Simple random bot
class RandomBot implements BotPlayer {
  chooseMove(state: Readonly<GameState>, playerId: string): GameMove {
    const validMoves = engine.getValidMoves(playerId);
    return validMoves[Math.floor(Math.random() * validMoves.length)];
  }
}

// Smarter bot with heuristic evaluation
class HeuristicBot implements BotPlayer {
  chooseMove(state: Readonly<GameState>, playerId: string): GameMove {
    const validMoves = engine.getValidMoves(playerId);

    // Score each move
    const scored = validMoves.map(move => {
      const simState = structuredClone(state);
      const simEngine = new GameEngine(simState);
      simEngine.applyMove(move);
      return {
        move,
        score: this.evaluate(simEngine.getState(), playerId),
      };
    });

    // Pick the highest-scoring move
    scored.sort((a, b) => b.score - a.score);
    return scored[0].move;
  }

  private evaluate(state: GameState, playerId: string): number {
    // Game-specific evaluation function
    // Return higher scores for better positions
    throw new Error("Implement per game");
  }
}
```

### Server-Side Bot Integration

```typescript
// In GameRoom
private bots = new Map<string, BotPlayer>();

addBot(difficulty: "easy" | "medium" | "hard") {
  const botId = `bot-${this.bots.size + 1}`;
  const bot = difficulty === "easy" ? new RandomBot() : new HeuristicBot();
  this.bots.set(botId, bot);

  // Add bot as a player
  const player = new Player();
  player.sessionId = botId;
  player.displayName = `Bot ${this.bots.size}`;
  player.isBot = true;
  this.state.players.set(botId, player);
}

// In the game tick or after each move
private checkBotTurn() {
  const bot = this.bots.get(this.state.currentTurn);
  if (!bot) return; // Human player's turn

  // Add slight delay for natural feel
  this.clock.setTimeout(() => {
    const move = bot.chooseMove(this.engine.getState(), this.state.currentTurn);
    this.engine.applyMove(move);
    // State changes auto-sync via Colyseus
  }, 500 + Math.random() * 1500); // 0.5-2s thinking time
}
```

---

## Game Persistence

### Save Game State

```typescript
import Database from "better-sqlite3";

const db = new Database("games.db");

// Create tables
db.exec(`
  CREATE TABLE IF NOT EXISTS games (
    id TEXT PRIMARY KEY,
    game_type TEXT NOT NULL,
    state TEXT NOT NULL,        -- JSON serialized game state
    move_history TEXT NOT NULL,  -- JSON serialized moves
    phase TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    players TEXT NOT NULL        -- JSON array of player info
  );
`);

function saveGame(roomId: string, state: GameState, moves: GameMove[]) {
  const stmt = db.prepare(`
    INSERT OR REPLACE INTO games (id, game_type, state, move_history, phase, created_at, updated_at, players)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);

  stmt.run(
    roomId,
    state.gameType,
    JSON.stringify(state),
    JSON.stringify(moves),
    state.phase,
    state.createdAt || Date.now(),
    Date.now(),
    JSON.stringify(Array.from(state.players.values()).map(p => ({
      id: p.sessionId,
      name: p.displayName,
    }))),
  );
}

function loadGame(roomId: string): { state: GameState; moves: GameMove[] } | null {
  const row = db.prepare("SELECT state, move_history FROM games WHERE id = ?").get(roomId);
  if (!row) return null;
  return {
    state: JSON.parse(row.state),
    moves: JSON.parse(row.move_history),
  };
}
```

### Auto-Save Pattern

```typescript
// In GameRoom
private saveInterval: ReturnType<typeof setInterval> | null = null;

onCreate(options: any) {
  // ...

  // Auto-save every 30 seconds during active games
  this.saveInterval = setInterval(() => {
    if (this.state.phase === "playing") {
      saveGame(this.roomId, this.state, this.engine.getMoveHistory());
    }
  }, 30_000);
}

// Also save on every move for critical state
private handleMove(client: Client, data: any) {
  // ... validate and apply ...
  saveGame(this.roomId, this.state, this.engine.getMoveHistory());
}

onDispose() {
  if (this.saveInterval) clearInterval(this.saveInterval);
  // Final save
  saveGame(this.roomId, this.state, this.engine.getMoveHistory());
}
```

### Crash Recovery

```typescript
// On server startup, restore in-progress games
async function restoreGames(server: Server) {
  const activeGames = db.prepare(
    "SELECT * FROM games WHERE phase = 'playing'"
  ).all();

  for (const game of activeGames) {
    const state = JSON.parse(game.state);
    const moves = JSON.parse(game.move_history);

    // Create room with restored state
    const room = await server.createRoom("game", {
      restored: true,
      roomId: game.id,
      initialState: state,
      moveHistory: moves,
    });

    console.log(`Restored game ${game.id} with ${state.players.size} players`);
  }
}
```

---

## Undo / Redo

### Simple Snapshot Undo

For games with small state (chess, checkers):

```typescript
class UndoManager {
  private snapshots: string[] = [];  // JSON serialized states
  private maxHistory = 50;

  saveCheckpoint(state: GameState) {
    this.snapshots.push(JSON.stringify(state));
    if (this.snapshots.length > this.maxHistory) {
      this.snapshots.shift();
    }
  }

  undo(): GameState | null {
    if (this.snapshots.length <= 1) return null; // Keep initial state
    this.snapshots.pop(); // Remove current
    return JSON.parse(this.snapshots[this.snapshots.length - 1]);
  }

  canUndo(): boolean {
    return this.snapshots.length > 1;
  }
}
```

### Multiplayer Undo Protocol

Undo in multiplayer requires opponent consent:

```typescript
// Server
onMessage("request_undo", (client) => {
  if (this.state.moveHistory.length === 0) return;

  const lastMove = this.state.moveHistory[this.state.moveHistory.length - 1];
  if (lastMove.playerId !== client.sessionId) {
    client.send("error", { message: "Can only undo your own moves" });
    return;
  }

  // Ask opponent for permission
  this.broadcast("undo_requested", {
    by: client.sessionId,
    move: lastMove,
  }, { except: client });

  this.pendingUndo = { requestedBy: client.sessionId, move: lastMove };
});

onMessage("respond_undo", (client, { accept }) => {
  if (!this.pendingUndo) return;

  if (accept) {
    this.engine.undoLastMove();
    this.broadcast("notification", { type: "undo", message: "Move undone" });
  } else {
    this.clients.find(c => c.sessionId === this.pendingUndo!.requestedBy)
      ?.send("notification", { type: "undo_denied", message: "Undo request denied" });
  }

  this.pendingUndo = null;
});
```

---

## Game Replay

Since all moves are recorded, replaying a game is straightforward:

```typescript
class GameReplay {
  private engine: GameEngine;
  private moves: GameMove[];
  private currentMove = -1;

  constructor(initialState: GameState, moves: GameMove[]) {
    this.engine = new GameEngine(structuredClone(initialState));
    this.moves = moves;
  }

  /** Step forward one move */
  next(): { move: GameMove; state: GameState } | null {
    if (this.currentMove >= this.moves.length - 1) return null;
    this.currentMove++;
    const move = this.moves[this.currentMove];
    this.engine.applyMove(move);
    return { move, state: this.engine.getState() };
  }

  /** Jump to a specific move */
  goTo(moveIndex: number): GameState {
    // Replay from start to target move
    this.engine = new GameEngine(structuredClone(this.initialState));
    this.currentMove = -1;
    for (let i = 0; i <= moveIndex && i < this.moves.length; i++) {
      this.engine.applyMove(this.moves[i]);
      this.currentMove = i;
    }
    return this.engine.getState();
  }

  /** Auto-play with animation delay */
  async autoPlay(onMove: (move: GameMove, state: GameState) => Promise<void>) {
    while (this.currentMove < this.moves.length - 1) {
      const result = this.next()!;
      await onMove(result.move, result.state);
    }
  }
}
```
