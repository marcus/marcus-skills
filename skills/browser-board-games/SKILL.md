---
name: browser-board-games
description: "Architecture and implementation guide for browser-based multiplayer board games with real-time interactions, smooth 2D animations, lobby management, and WebSocket networking. Use when building any turn-based or real-time board/card/tabletop game for the browser."
---

# Browser Board Games

Build multiplayer browser-based board games with real-time networking, smooth animations, and production-ready lobby systems. This skill provides the full technical architecture — you provide the game design and rules.

## Philosophy

- **Server-authoritative**: The server owns game state. Clients are rendering terminals.
- **Build the game layer, borrow the plumbing**: Use Colyseus for networking (rooms, state sync, reconnection). Build rendering, animation, game logic, and UI yourself.
- **TypeScript everywhere**: Shared types and validation between client and server via monorepo.
- **HTML/CSS-first rendering**: Use the DOM for board layout and game elements. Reach for Canvas only when DOM can't keep up.
- **Framework-agnostic game core**: Game logic is pure TypeScript. UI layer can use any framework or none.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    CLIENT                            │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐ │
│  │ UI Layer │  │ Renderer │  │ Animation Engine  │ │
│  │ (HTML/   │  │ (DOM +   │  │ (Web Animations   │ │
│  │  CSS)    │  │  Canvas) │  │  API + rAF)       │ │
│  └────┬─────┘  └────┬─────┘  └────────┬──────────┘ │
│       │              │                 │             │
│  ┌────┴──────────────┴─────────────────┴──────────┐ │
│  │            Client Game Controller               │ │
│  │   (input handling, optimistic updates,          │ │
│  │    animation triggers, sound)                   │ │
│  └─────────────────────┬───────────────────────────┘ │
│                        │                             │
│  ┌─────────────────────┴───────────────────────────┐ │
│  │         Colyseus Client SDK                      │ │
│  │   (WebSocket, state sync, reconnection)          │ │
│  └─────────────────────┬───────────────────────────┘ │
└────────────────────────┼─────────────────────────────┘
                         │ WebSocket
┌────────────────────────┼─────────────────────────────┐
│                    SERVER                            │
│  ┌─────────────────────┴───────────────────────────┐ │
│  │         Colyseus Server                          │ │
│  │   (rooms, lobby, matchmaking, reconnection)      │ │
│  └─────────────────────┬───────────────────────────┘ │
│                        │                             │
│  ┌─────────────────────┴───────────────────────────┐ │
│  │            Game Room (per match)                 │ │
│  │  ┌─────────────┐  ┌──────────────────────────┐  │ │
│  │  │ Game State  │  │ Game Logic Engine         │  │ │
│  │  │ (Colyseus   │  │ (rules, validation,       │  │ │
│  │  │  Schema)    │  │  turn management,         │  │ │
│  │  └─────────────┘  │  win conditions)          │  │ │
│  │                    └──────────────────────────┘  │ │
│  └──────────────────────────────────────────────────┘ │
│                                                      │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Persistence Layer (optional)                    │ │
│  │  SQLite/Redis for game history, user accounts    │ │
│  └──────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Runtime** | Node.js + TypeScript | Shared types client/server, ecosystem |
| **Networking** | Colyseus 0.15+ | Industry standard game room server, handles rooms/state sync/reconnection |
| **Client build** | Vite | Fast HMR, native TS support |
| **Server run** | tsx | TypeScript execution without compile step |
| **Board rendering** | HTML/CSS (CSS Grid + transforms) | Scalable, accessible, GPU-accelerated transforms |
| **Animation** | Web Animations API + requestAnimationFrame | Native, no dependencies, hardware accelerated |
| **Complex visuals** | Canvas 2D (only when needed) | Particle effects, complex paths, many moving sprites |
| **Audio** | Web Audio API | No library needed for board game sound effects |
| **Monorepo** | npm/pnpm workspaces | Shared packages without publish overhead |
| **Testing** | Vitest | Fast, native TS, compatible with Vite |
| **Persistence** | SQLite (better-sqlite3) | Zero-config, single file, good for game history |

### What We Don't Use (and Why)

| Skipped | Why |
|---------|-----|
| PixiJS / Phaser / Konva | Overkill for board games — DOM handles it. Reach for Canvas 2D directly when needed. |
| Socket.IO | Colyseus handles WebSocket transport with game-specific features on top. |
| GSAP / anime.js | Web Animations API covers board game needs natively. |
| React / Vue / Svelte | Game core is framework-agnostic. Use one for UI chrome if you want, but game rendering is vanilla. |
| Redux / Zustand | Colyseus schema IS your state. No second store needed. |
| Howler.js | Web Audio API is sufficient for board game audio. |

---

## Quick Start: Project Structure

```
board-game/
├── package.json              # Workspace root
├── tsconfig.base.json        # Shared TS config
├── packages/
│   ├── shared/               # Shared between client and server
│   │   ├── package.json
│   │   ├── src/
│   │   │   ├── types.ts      # Game types, move definitions, enums
│   │   │   ├── constants.ts  # Game constants (board size, max players, etc.)
│   │   │   ├── validation.ts # Move validation (runs on BOTH client and server)
│   │   │   └── schema.ts     # Colyseus schema definitions
│   │   └── tsconfig.json
│   ├── server/
│   │   ├── package.json
│   │   ├── src/
│   │   │   ├── index.ts      # Server entry, Colyseus setup
│   │   │   ├── rooms/
│   │   │   │   ├── GameRoom.ts    # Main game room
│   │   │   │   └── LobbyRoom.ts   # Custom lobby (optional, Colyseus has built-in)
│   │   │   ├── game/
│   │   │   │   ├── engine.ts      # Game logic engine (YOUR GAME HERE)
│   │   │   │   ├── turns.ts       # Turn/phase management
│   │   │   │   └── ai.ts          # Bot player logic (optional)
│   │   │   └── persistence/
│   │   │       └── store.ts       # Game save/load
│   │   └── tsconfig.json
│   └── client/
│       ├── package.json
│       ├── index.html
│       ├── src/
│       │   ├── main.ts           # Entry point
│       │   ├── connection.ts     # Colyseus client setup
│       │   ├── lobby/
│       │   │   ├── lobby-ui.ts   # Lobby screen
│       │   │   └── matchmaker.ts # Join/create room logic
│       │   ├── game/
│       │   │   ├── board.ts      # Board rendering (DOM)
│       │   │   ├── pieces.ts     # Game piece rendering
│       │   │   ├── input.ts      # Mouse/touch input handling
│       │   │   └── controller.ts # Client game controller
│       │   ├── animation/
│       │   │   ├── engine.ts     # Animation scheduler
│       │   │   ├── easing.ts     # Easing functions
│       │   │   └── effects.ts    # Visual effects (particles, highlights)
│       │   ├── audio/
│       │   │   └── sounds.ts     # Sound effect manager
│       │   ├── ui/
│       │   │   ├── hud.ts        # Heads-up display (scores, turn indicator)
│       │   │   ├── chat.ts       # In-game chat
│       │   │   └── settings.ts   # Player settings
│       │   └── assets/
│       │       ├── sprites/      # Game piece images/SVGs
│       │       └── sounds/       # Audio files (.webm, .mp3)
│       ├── vite.config.ts
│       └── tsconfig.json
├── .env                      # COLYSEUS_PORT, etc.
└── vitest.config.ts          # Test config
```

See [references/project-structure.md](references/project-structure.md) for full setup instructions including package.json configurations, tsconfig setup, and build scripts.

---

## Core Systems

### 1. Networking with Colyseus

Colyseus is the one significant dependency. It provides:

- **Rooms**: Isolated game instances with lifecycle hooks
- **Schema-based state**: Automatic delta synchronization to all clients
- **Lobby**: Built-in lobby with room listing and filtering
- **Reconnection**: Token-based reconnection with configurable timeouts
- **Matchmaking**: Built-in or custom matchmaking logic

See [references/networking-architecture.md](references/networking-architecture.md) for:
- Colyseus server setup and room configuration
- State schema design patterns
- Message protocol design
- Reconnection implementation
- Scaling strategies

**Key pattern — Server-authoritative moves:**

```typescript
// Client sends a move request (NOT a state change)
room.send("move", { pieceId: "rook-1", to: { row: 4, col: 7 } });

// Server validates and applies (or rejects)
onMessage("move", (client, data) => {
  const player = this.state.players.get(client.sessionId);
  if (!isValidMove(this.state, player, data)) {
    client.send("error", { message: "Invalid move" });
    return;
  }
  applyMove(this.state, player, data);
  // Colyseus auto-syncs state changes to all clients
});
```

### 2. Lobby and Matchmaking

The lobby system handles everything before gameplay starts:

- **Room browser**: List available games with filters (game type, player count, skill level)
- **Quick match**: Auto-join or create a room matching criteria
- **Private rooms**: Share a room code with friends
- **Spectator mode**: Join as observer
- **Ready check**: All players confirm before game starts

See [references/lobby-and-matchmaking.md](references/lobby-and-matchmaking.md) for complete lobby implementation patterns, room codes, and matchmaking algorithms.

**Key pattern — Room lifecycle:**

```
CREATE → WAITING_FOR_PLAYERS → READY_CHECK → PLAYING → FINISHED
                ↑                                         │
                └────── REMATCH ←─────────────────────────┘
```

### 3. Rendering (DOM-First)

Board games are ideal for DOM rendering. CSS Grid defines the board. HTML elements are game pieces. CSS transforms handle movement. Canvas is reserved for effects that DOM can't handle efficiently.

See [references/rendering-and-animation.md](references/rendering-and-animation.md) for:
- Board layout patterns (grid, hex, freeform)
- Piece rendering with SVG and HTML
- Responsive scaling strategies
- Camera/viewport for large boards
- Touch and mouse input handling
- Drag-and-drop implementation

**Key pattern — CSS Grid board:**

```typescript
function createBoard(rows: number, cols: number): HTMLElement {
  const board = document.createElement('div');
  board.style.cssText = `
    display: grid;
    grid-template-columns: repeat(${cols}, 1fr);
    grid-template-rows: repeat(${rows}, 1fr);
    aspect-ratio: ${cols} / ${rows};
    max-width: min(90vw, 90vh * ${cols / rows});
  `;
  return board;
}
```

### 4. Animation System

Smooth animations are critical for game feel. Use the Web Animations API for piece movement and CSS transitions for UI state changes. Reserve `requestAnimationFrame` loops for continuous effects.

See [references/rendering-and-animation.md](references/rendering-and-animation.md) for:
- Animation queue system (sequential and parallel animations)
- Easing functions for natural movement
- Card flip, dice roll, piece slide patterns
- Particle effects with Canvas
- Animation-state sync (wait for animations before next turn)

**Key pattern — Animated piece movement:**

```typescript
function animateMove(piece: HTMLElement, from: Point, to: Point): Promise<void> {
  const dx = (to.col - from.col) * cellSize;
  const dy = (to.row - from.row) * cellSize;

  const animation = piece.animate([
    { transform: 'translate(0, 0)' },
    { transform: `translate(${dx}px, ${dy}px)` }
  ], {
    duration: 300,
    easing: 'cubic-bezier(0.22, 1, 0.36, 1)', // ease-out-quint
    fill: 'forwards'
  });

  return animation.finished.then(() => {
    // Commit final position to layout
    piece.style.gridColumn = String(to.col + 1);
    piece.style.gridRow = String(to.row + 1);
    animation.cancel();
  });
}
```

### 5. Game State and Logic

Game logic lives in a pure TypeScript engine with no DOM or network dependencies. This engine runs on the server for authority and optionally on the client for prediction.

See [references/game-state-patterns.md](references/game-state-patterns.md) for:
- State machine patterns for game phases
- Command pattern for moves (enables undo, replay, server validation)
- Hidden information architecture (server-side filtering)
- Random number generation (seeded RNG for reproducibility)
- Turn and timer management
- Win condition evaluation
- AI/bot player interface
- Game persistence and crash recovery

**Key pattern — Move as command:**

```typescript
interface GameMove {
  type: string;
  playerId: string;
  timestamp: number;
  data: Record<string, unknown>;
}

interface GameEngine {
  getState(): GameState;
  getValidMoves(playerId: string): GameMove[];
  applyMove(move: GameMove): MoveResult;
  undoLastMove(): boolean;
}
```

### 6. Audio

Board games need minimal but satisfying audio: piece placement, card sounds, turn notifications, victory fanfare. The Web Audio API handles this without any library.

```typescript
class SoundManager {
  private ctx: AudioContext;
  private buffers = new Map<string, AudioBuffer>();

  async load(name: string, url: string) {
    const response = await fetch(url);
    const data = await response.arrayBuffer();
    this.buffers.set(name, await this.ctx.decodeAudioData(data));
  }

  play(name: string, volume = 1.0) {
    const buffer = this.buffers.get(name);
    if (!buffer) return;
    const source = this.ctx.createBufferSource();
    const gain = this.ctx.createGain();
    gain.gain.value = volume;
    source.buffer = buffer;
    source.connect(gain).connect(this.ctx.destination);
    source.start();
  }
}
```

---

## Implementation Sequence

When building a new board game, follow this order:

### Phase 1: Foundation (get two players connected)
1. Set up the monorepo with shared/server/client packages
2. Create Colyseus server with a basic game room
3. Define game state schema (Colyseus Schema)
4. Build minimal lobby: create room, join room, player list
5. Verify: two browser tabs can connect and see each other

### Phase 2: Game Logic (make it playable)
6. Define move types and validation in `shared/`
7. Implement game engine with turn management
8. Wire moves through Colyseus messages
9. Build basic board rendering (DOM, no animation yet)
10. Verify: two players can play a complete game

### Phase 3: Polish (make it feel good)
11. Add animation system for piece movement
12. Add sound effects
13. Implement ready check and game-over flow
14. Add rematch functionality
15. Add spectator mode

### Phase 4: Production (make it reliable)
16. Implement reconnection handling
17. Add game persistence (save/load)
18. Add input validation and anti-cheat
19. Responsive design and mobile touch support
20. Deploy to production

---

## Key Architectural Decisions

### Why Colyseus (not raw WebSockets)?

Building room management, state synchronization, and reconnection from scratch is 2000+ lines of networking code that is hard to get right. Colyseus is MIT-licensed, well-maintained, and purpose-built for this. It's the one dependency that earns its place.

If you truly want zero dependencies, see [references/networking-architecture.md](references/networking-architecture.md) for a raw `ws` alternative architecture, but expect to invest significant effort in reconnection, state delta sync, and room lifecycle management.

### Why DOM rendering (not Canvas/WebGL)?

Board games have relatively few moving elements (tens, not thousands). DOM elements are:
- **Accessible** (screen readers, keyboard nav)
- **Responsive** (CSS handles layout)
- **Styleable** (CSS animations, transitions, themes)
- **Interactive** (native click/touch/drag events)
- **GPU-accelerated** (transforms and opacity are composited)

Use Canvas 2D only for: particle effects, complex procedural graphics, or boards with 500+ simultaneously animated elements.

### Why Web Animations API (not GSAP/anime.js)?

The Web Animations API is now supported in all modern browsers and provides:
- Hardware-accelerated animation on compositor thread
- Promise-based completion
- Cancellation and timeline control
- No bundle size cost

For the 5% of animations that need more (spring physics, complex timelines), implement a small custom interpolation system with `requestAnimationFrame`. See [references/rendering-and-animation.md](references/rendering-and-animation.md).

### Why framework-agnostic?

The game rendering layer should be pure DOM manipulation. This makes it:
- Portable across frameworks (or no framework)
- Easier to optimize (no virtual DOM overhead for game elements)
- Simpler to reason about (direct DOM = direct control)

Use a framework for the UI chrome (lobby, settings, chat) if you want, but keep the game board vanilla.

---

## Common Board Game Patterns

| Pattern | When to Use | Reference |
|---------|------------|-----------|
| Grid board (chess, checkers) | Square tile boards | [rendering-and-animation.md](references/rendering-and-animation.md) |
| Hex board (Catan, hex strategy) | Hexagonal tile boards | [rendering-and-animation.md](references/rendering-and-animation.md) |
| Card hand (poker, Uno) | Fan layout with hover/select | [rendering-and-animation.md](references/rendering-and-animation.md) |
| Dice rolling | Physics-like dice animation | [rendering-and-animation.md](references/rendering-and-animation.md) |
| Hidden information | Cards/tiles only owner can see | [game-state-patterns.md](references/game-state-patterns.md) |
| Timed turns | Chess clock, turn timer | [game-state-patterns.md](references/game-state-patterns.md) |
| Undo/redo | Take-back moves | [game-state-patterns.md](references/game-state-patterns.md) |
| Spectator mode | Watch without playing | [lobby-and-matchmaking.md](references/lobby-and-matchmaking.md) |
| Private rooms | Play with friends via code | [lobby-and-matchmaking.md](references/lobby-and-matchmaking.md) |
| Rematch | Play again with same players | [lobby-and-matchmaking.md](references/lobby-and-matchmaking.md) |
| Bot players | AI opponents | [game-state-patterns.md](references/game-state-patterns.md) |

---

## Reference Documents

| Document | Covers |
|----------|--------|
| [networking-architecture.md](references/networking-architecture.md) | Colyseus setup, state schemas, message protocols, reconnection, scaling, raw WebSocket alternative |
| [rendering-and-animation.md](references/rendering-and-animation.md) | DOM board rendering, CSS Grid/hex layouts, animation system, drag-and-drop, responsive design, Canvas effects |
| [game-state-patterns.md](references/game-state-patterns.md) | State machines, command pattern, hidden info, RNG, turns, timers, AI bots, persistence |
| [lobby-and-matchmaking.md](references/lobby-and-matchmaking.md) | Room browser, quick match, private rooms, spectators, ready check, chat, room codes |
| [project-structure.md](references/project-structure.md) | Monorepo setup, package configs, build scripts, dev workflow, testing, deployment, security |
