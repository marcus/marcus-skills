# Project Structure and Setup

## Monorepo Setup

Use npm workspaces (or pnpm workspaces) with three packages sharing TypeScript types.

### Root package.json

```json
{
  "name": "board-game",
  "private": true,
  "workspaces": [
    "packages/*"
  ],
  "scripts": {
    "dev": "concurrently \"npm run dev:server\" \"npm run dev:client\"",
    "dev:server": "npm run dev -w packages/server",
    "dev:client": "npm run dev -w packages/client",
    "build": "npm run build -w packages/shared && npm run build -w packages/server && npm run build -w packages/client",
    "test": "vitest",
    "test:run": "vitest run",
    "lint": "tsc --noEmit"
  },
  "devDependencies": {
    "concurrently": "^9.0.0",
    "typescript": "^5.5.0",
    "vitest": "^2.0.0"
  }
}
```

### Shared Package

```json
// packages/shared/package.json
{
  "name": "@game/shared",
  "version": "1.0.0",
  "private": true,
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "dependencies": {
    "@colyseus/schema": "^2.0.0"
  }
}
```

```typescript
// packages/shared/src/index.ts
export * from "./types";
export * from "./schema";
export * from "./constants";
export * from "./validation";
```

### Server Package

```json
// packages/server/package.json
{
  "name": "@game/server",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "start": "tsx src/index.ts",
    "build": "tsc"
  },
  "dependencies": {
    "@game/shared": "*",
    "colyseus": "^0.15.0",
    "better-sqlite3": "^11.0.0"
  },
  "devDependencies": {
    "tsx": "^4.0.0",
    "@types/better-sqlite3": "^7.0.0"
  }
}
```

### Client Package

```json
// packages/client/package.json
{
  "name": "@game/client",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@game/shared": "*",
    "colyseus.js": "^0.15.0"
  },
  "devDependencies": {
    "vite": "^6.0.0"
  }
}
```

---

## TypeScript Configuration

### Base Config (shared)

```json
// tsconfig.base.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "experimentalDecorators": true,
    "emitDecoratorMetadata": false
  }
}
```

Note: `experimentalDecorators: true` is required for Colyseus `@type` decorators.

### Server Config

```json
// packages/server/tsconfig.json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"],
  "references": [
    { "path": "../shared" }
  ]
}
```

### Client Config

```json
// packages/client/tsconfig.json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"],
  "references": [
    { "path": "../shared" }
  ]
}
```

---

## Vite Configuration

```typescript
// packages/client/vite.config.ts
import { defineConfig } from "vite";
import { resolve } from "path";

export default defineConfig({
  resolve: {
    alias: {
      "@game/shared": resolve(__dirname, "../shared/src"),
    },
  },
  server: {
    port: 3000,
    proxy: {
      // Proxy WebSocket connections to Colyseus server during dev
      "/ws": {
        target: "ws://localhost:2567",
        ws: true,
      },
    },
  },
  build: {
    target: "ES2022",
    outDir: "dist",
  },
});
```

---

## Development Workflow

### Local Multiplayer Testing

The most important dev workflow: testing with multiple browser tabs.

```bash
# Terminal 1: Start everything
npm run dev
# Server runs on :2567, client on :3000
```

Open `http://localhost:3000` in two (or more) browser tabs. Each tab is a separate player.

### Hot Reloading

- **Client**: Vite HMR updates the UI instantly
- **Server**: `tsx watch` restarts the server on file changes
- **Shared**: Changes in shared trigger both client HMR and server restart

### Debug Tools

Add a debug panel for development:

```typescript
// packages/client/src/debug.ts
function createDebugPanel(room: Room) {
  if (!import.meta.env.DEV) return;

  const panel = document.createElement("div");
  panel.id = "debug-panel";
  panel.style.cssText = `
    position: fixed; top: 0; right: 0;
    width: 300px; max-height: 100vh;
    overflow-y: auto; background: rgba(0,0,0,0.9);
    color: #0f0; font-family: monospace;
    font-size: 11px; padding: 8px;
    z-index: 9999; pointer-events: none;
  `;
  document.body.appendChild(panel);

  // Update every frame
  function update() {
    panel.innerHTML = `
      <div><b>Room:</b> ${room.id}</div>
      <div><b>Session:</b> ${room.sessionId}</div>
      <div><b>Phase:</b> ${room.state.phase}</div>
      <div><b>Turn:</b> ${room.state.currentTurn}</div>
      <div><b>Players:</b> ${room.state.players.size}</div>
      <div><b>Move #:</b> ${room.state.turnNumber}</div>
      <hr>
      <div><b>State:</b></div>
      <pre>${JSON.stringify(room.state.toJSON(), null, 1)}</pre>
    `;
    requestAnimationFrame(update);
  }
  update();
}
```

---

## Testing Strategy

### Unit Tests: Game Logic

The game engine is pure TypeScript with no dependencies. Test it thoroughly.

```typescript
// packages/shared/src/__tests__/engine.test.ts
import { describe, it, expect } from "vitest";
import { GameEngine } from "../engine";
import { createInitialState } from "../setup";

describe("GameEngine", () => {
  it("should reject moves when it's not the player's turn", () => {
    const engine = new GameEngine(createInitialState(["player1", "player2"]));
    const result = engine.applyMove({
      type: "move",
      playerId: "player2", // Not their turn
      timestamp: Date.now(),
      data: { pieceId: "p2-1", to: { row: 3, col: 0 } },
    });
    expect(result.valid).toBe(false);
  });

  it("should advance turn after a valid move", () => {
    const engine = new GameEngine(createInitialState(["player1", "player2"]));
    engine.applyMove({
      type: "move",
      playerId: "player1",
      timestamp: Date.now(),
      data: { pieceId: "p1-1", to: { row: 2, col: 0 } },
    });
    expect(engine.getState().currentTurn).toBe("player2");
  });

  it("should detect win condition", () => {
    const state = createWinningState("player1");
    const engine = new GameEngine(state);
    const result = engine.applyMove(/* winning move */);
    expect(result.gameOver).toBe(true);
    expect(result.winner).toBe("player1");
  });

  it("should support undo", () => {
    const engine = new GameEngine(createInitialState(["player1", "player2"]));
    const stateBefore = JSON.stringify(engine.getState());
    engine.applyMove(/* some move */);
    engine.undoLastMove();
    expect(JSON.stringify(engine.getState())).toBe(stateBefore);
  });
});
```

### Integration Tests: Multiplayer Flow

Test the full room lifecycle with simulated clients.

```typescript
// packages/server/src/__tests__/room.test.ts
import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { ColyseusTestServer, boot } from "@colyseus/testing";

describe("GameRoom", () => {
  let server: ColyseusTestServer;

  beforeAll(async () => {
    server = await boot(/* your server config */);
  });

  afterAll(async () => {
    await server.shutdown();
  });

  it("should allow two players to join and play", async () => {
    const room = await server.createRoom("game", { gameType: "chess" });

    const client1 = await server.connectTo(room, { displayName: "Alice" });
    const client2 = await server.connectTo(room, { displayName: "Bob" });

    expect(room.state.players.size).toBe(2);

    // Ready up
    client1.send("ready");
    client2.send("ready");

    // Wait for phase change
    await server.waitForMessage(client1, "notification");
    expect(room.state.phase).toBe("playing");
  });

  it("should handle disconnection and reconnection", async () => {
    const room = await server.createRoom("game", {});
    const client = await server.connectTo(room, { displayName: "Alice" });

    // Simulate disconnect
    client.close();

    // Player should be marked as disconnected
    const player = room.state.players.get(client.sessionId);
    expect(player?.connected).toBe(false);

    // Reconnect
    const reconnected = await server.connectTo(room, {
      reconnectionToken: client.reconnectionToken,
    });

    expect(reconnected.sessionId).toBe(client.sessionId);
    expect(room.state.players.get(client.sessionId)?.connected).toBe(true);
  });
});
```

### Visual Tests (Manual)

For rendering and animation, rely on manual testing with the debug panel. Automated visual testing of game boards is generally not worth the effort.

---

## Deployment

### Build for Production

```bash
# Build all packages
npm run build

# Server output: packages/server/dist/
# Client output: packages/client/dist/
```

### Fly.io Deployment (Recommended)

```dockerfile
# Dockerfile
FROM node:22-slim AS builder

WORKDIR /app
COPY package*.json ./
COPY packages/shared/package.json packages/shared/
COPY packages/server/package.json packages/server/
RUN npm ci

COPY tsconfig.base.json ./
COPY packages/shared/ packages/shared/
COPY packages/server/ packages/server/
RUN npm run build -w packages/shared && npm run build -w packages/server

# Production
FROM node:22-slim
WORKDIR /app

COPY --from=builder /app/package*.json ./
COPY --from=builder /app/packages/shared/package.json packages/shared/
COPY --from=builder /app/packages/server/package.json packages/server/
RUN npm ci --production

COPY --from=builder /app/packages/shared/dist packages/shared/dist
COPY --from=builder /app/packages/server/dist packages/server/dist

EXPOSE 2567
CMD ["node", "packages/server/dist/index.js"]
```

```toml
# fly.toml
app = "my-board-game"
primary_region = "ord"

[http_service]
  internal_port = 2567
  force_https = true

  [[http_service.checks]]
    interval = "30s"
    timeout = "5s"
    method = "GET"
    path = "/health"

[env]
  NODE_ENV = "production"
```

Serve the client build as static files from a CDN (Cloudflare Pages, Vercel, Netlify) pointed at the Fly.io server for WebSocket connections.

### Client Deployment (Static)

```bash
# Deploy client to Cloudflare Pages, Vercel, or Netlify
cd packages/client
npm run build
# Upload dist/ to your static host
```

Set the environment variable `VITE_SERVER_URL` to your production WebSocket server URL:

```
VITE_SERVER_URL=wss://my-board-game.fly.dev
```

### Health Check Endpoint

```typescript
// packages/server/src/index.ts
import { createServer } from "http";

const httpServer = createServer((req, res) => {
  if (req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({
      status: "ok",
      rooms: server.rooms.length,
      connections: server.transport.wss?.clients?.size || 0,
    }));
    return;
  }
  res.writeHead(404);
  res.end();
});

const server = new Server({ server: httpServer });
```

---

## Security Checklist

### Input Validation

All game moves are validated server-side. But also:

```typescript
// Rate limit messages per client
const MESSAGE_LIMITS: Record<string, { max: number; windowMs: number }> = {
  move: { max: 60, windowMs: 60_000 },      // 1 move/second average
  chat: { max: 30, windowMs: 60_000 },      // 30 messages/minute
  ready: { max: 5, windowMs: 10_000 },      // Prevent spam
};

// In room setup
for (const [type, limit] of Object.entries(MESSAGE_LIMITS)) {
  const counts = new Map<string, { count: number; resetAt: number }>();

  this.onMessage(type, (client, data) => {
    const now = Date.now();
    const entry = counts.get(client.sessionId);

    if (entry && now < entry.resetAt) {
      entry.count++;
      if (entry.count > limit.max) {
        client.send("error", { message: "Rate limited" });
        return;
      }
    } else {
      counts.set(client.sessionId, { count: 1, resetAt: now + limit.windowMs });
    }

    // Process message
    this.handleMessage(type, client, data);
  });
}
```

### Anti-Cheat Essentials

Board games have a simpler anti-cheat surface than action games:

1. **Server authoritative**: Never trust client state. Validate every move server-side.
2. **Hidden information**: Use Colyseus filters. Never send data the client shouldn't have.
3. **Timing**: Server tracks turn timers, not the client.
4. **Replay validation**: Store all moves. Any game can be replayed and verified.
5. **Rate limiting**: Prevent message flooding.

### Chat Sanitization

```typescript
function sanitizeChat(text: string): string {
  return text
    .trim()
    .slice(0, 500)                    // Max length
    .replace(/[<>]/g, "")            // Strip HTML
    .replace(/\n{3,}/g, "\n\n");     // Collapse excessive newlines
}
```

---

## Audio Setup

### Sound File Format

Use `.webm` (Opus codec) as primary, `.mp3` as fallback. WebM is smaller and higher quality.

```
packages/client/src/assets/sounds/
├── piece_move.webm
├── piece_capture.webm
├── card_deal.webm
├── card_flip.webm
├── dice_roll.webm
├── your_turn.webm
├── timer_warning.webm
├── game_win.webm
├── game_lose.webm
├── chat_message.webm
└── ui_click.webm
```

### Sound Manager with Web Audio API

```typescript
class GameAudio {
  private ctx: AudioContext | null = null;
  private buffers = new Map<string, AudioBuffer>();
  private masterVolume = 1.0;
  private muted = false;

  async init() {
    // Create AudioContext on first user interaction (browser requirement)
    this.ctx = new AudioContext();
  }

  async loadAll(manifest: Record<string, string>) {
    if (!this.ctx) await this.init();

    const entries = Object.entries(manifest);
    await Promise.all(entries.map(async ([name, url]) => {
      try {
        const response = await fetch(url);
        const data = await response.arrayBuffer();
        const buffer = await this.ctx!.decodeAudioData(data);
        this.buffers.set(name, buffer);
      } catch (e) {
        console.warn(`Failed to load sound: ${name}`, e);
      }
    }));
  }

  play(name: string, options: { volume?: number; pitch?: number } = {}) {
    if (this.muted || !this.ctx) return;

    const buffer = this.buffers.get(name);
    if (!buffer) return;

    const source = this.ctx.createBufferSource();
    const gain = this.ctx.createGain();

    source.buffer = buffer;
    source.playbackRate.value = options.pitch || 1.0;
    gain.gain.value = (options.volume || 1.0) * this.masterVolume;

    source.connect(gain).connect(this.ctx.destination);
    source.start();
  }

  setVolume(v: number) { this.masterVolume = Math.max(0, Math.min(1, v)); }
  toggleMute() { this.muted = !this.muted; return this.muted; }
}

// Usage
const audio = new GameAudio();
await audio.loadAll({
  piece_move: "/sounds/piece_move.webm",
  piece_capture: "/sounds/piece_capture.webm",
  your_turn: "/sounds/your_turn.webm",
  // ... etc
});

// Play sounds in response to game events
room.state.listen("currentTurn", (turn) => {
  if (turn === room.sessionId) {
    audio.play("your_turn");
  }
});
```

### Sound Design Tips for Board Games

- **Piece placement**: Short, satisfying "click" or "thud" (50-150ms)
- **Card dealing**: Quick "swish" sound (100-200ms)
- **Dice rolling**: Rattling sound with final impact (800-1200ms, sync with animation)
- **Turn notification**: Gentle chime, not jarring (200-400ms)
- **Timer warning**: Subtle tick when <10s remain
- **Win/lose**: Short musical phrase, not long fanfare (1-2s)
- **Chat message**: Soft blip (50ms)

Keep all game sounds short, clean, and non-fatiguing. Players hear them hundreds of times.

---

## Asset Pipeline

### Sprite Sheet Generation

For games with many small images (card faces, tokens), use a sprite sheet:

```typescript
// Simple CSS sprite sheet approach
// Generate with free tools like TexturePacker or ShoeBox

// CSS
.card-face {
  width: 70px;
  height: 100px;
  background-image: url('/sprites/cards.png');
  background-size: 910px 400px;  /* 13 cols × 4 rows */
}

.card-face[data-suit="hearts"][data-rank="ace"] {
  background-position: 0px 0px;
}
.card-face[data-suit="hearts"][data-rank="2"] {
  background-position: -70px 0px;
}
// ... generated for all cards
```

### SVG Assets

For scalable game pieces, use inline SVG or SVG sprites:

```html
<!-- SVG sprite sheet: define once, use many times -->
<svg style="display: none">
  <defs>
    <symbol id="piece-king-white" viewBox="0 0 45 45">
      <!-- King SVG paths -->
    </symbol>
    <symbol id="piece-queen-white" viewBox="0 0 45 45">
      <!-- Queen SVG paths -->
    </symbol>
    <!-- ... all pieces ... -->
  </defs>
</svg>

<!-- Usage -->
<svg class="piece" width="40" height="40">
  <use href="#piece-king-white" />
</svg>
```

Load SVG definitions once and reference them throughout the game. This is more efficient than individual SVG files.
