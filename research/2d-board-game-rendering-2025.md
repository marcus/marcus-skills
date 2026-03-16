# 2D Board Game Rendering & Animation in the Browser (2025-2026)

Comprehensive research findings on rendering technologies, animation approaches, and interaction patterns for browser-based board games.

---

## 1. Rendering Technology: Canvas 2D vs SVG vs WebGL vs HTML/CSS

### Performance Benchmarks (2024 MacBook Pro)

| Technology | 1K elements | 5K elements | 10K elements | 50K elements |
|------------|-------------|-------------|--------------|--------------|
| SVG        | 60fps       | 35fps       | 12fps        | unusable     |
| Canvas 2D  | 60fps       | 60fps       | 60fps        | 55fps        |
| WebGL      | 60fps       | 60fps       | 60fps        | 60fps        |

### Board Game Context

Board games are **not** action games. A typical board game has:
- 50-500 visual elements (board, tiles, pieces, cards, UI)
- Infrequent animations (piece moves, card flips, dice rolls)
- Lots of static state between player actions
- Need for precise click/tap targeting on pieces
- Text-heavy UI (scores, labels, card text)

This changes the calculus significantly compared to real-time action games.

### Recommendation Matrix

| Approach | Best For | Avoid When |
|----------|----------|------------|
| **HTML/CSS + DOM** | Simple board games (<100 pieces), card games, turn-based with minimal animation. Built-in accessibility, text rendering, responsive layout, event handling. | You need pixel-level control, custom rendering effects, or >500 animated elements. |
| **SVG** | Vector board art that must look crisp at any zoom, games with <1000 interactive elements, when you want DOM events on individual pieces. | Animating many elements simultaneously. Performance degrades above ~5000 nodes. |
| **Canvas 2D** | Mid-complexity boards, games needing smooth animation of many pieces, custom rendering effects, when you want a single scalable surface. | You need built-in event handling per element (must implement hit-testing yourself). |
| **WebGL (via PixiJS)** | Visually rich games, particle effects, shader-based effects, 1000+ simultaneously animated elements. | Simple board games where it adds unnecessary complexity. |
| **Hybrid DOM + Canvas** | **Best general approach for board games.** DOM for UI/text/buttons, Canvas for the board surface and animated pieces. | When the game is so simple that pure DOM/CSS suffices. |

### The Hybrid Approach (Recommended Default)

The strongest pattern for board games is a layered architecture:

```
z-index: 30  │  DOM layer: UI overlay (scores, buttons, menus, tooltips)
z-index: 20  │  Canvas layer: animated game pieces, effects
z-index: 10  │  DOM/CSS layer: static board background, grid lines
```

Reasons this wins for board games:
- **DOM for UI** gives you CSS responsive layout, media queries, text rendering, accessibility, and native event handling for free
- **Canvas for gameplay** gives you smooth animation, custom rendering, and a single coordinate system for the board
- **CSS for backgrounds** offloads static imagery to the GPU compositor, zero cost per frame

```html
<div id="game-container" style="position: relative;">
  <!-- Static board background via CSS -->
  <div id="board-bg" style="
    position: absolute; inset: 0;
    background-image: url('board.svg');
    background-size: contain;
    background-position: center;
  "></div>

  <!-- Canvas for animated game elements -->
  <canvas id="game-canvas" style="position: absolute; inset: 0;"></canvas>

  <!-- DOM UI overlay -->
  <div id="ui-overlay" style="position: absolute; inset: 0; pointer-events: none;">
    <div class="score-display" style="pointer-events: auto;">Score: 0</div>
    <div class="action-buttons" style="pointer-events: auto;">
      <button>End Turn</button>
    </div>
  </div>
</div>
```

---

## 2. Animation Libraries Comparison

### The Options

| Library | Bundle Size | Runs On | Hardware Accelerated | Framework Locked |
|---------|-------------|---------|---------------------|-----------------|
| **CSS transitions/animations** | 0 KB | Compositor thread | Yes (transform, opacity) | No |
| **Web Animations API (WAAPI)** | 0 KB | Compositor thread | Yes (transform, opacity) | No |
| **requestAnimationFrame (manual)** | 0 KB | Main thread | No (but animates anything) | No |
| **GSAP** | ~23 KB gzip | Main thread | No | No |
| **anime.js v4** | ~10-15 KB gzip | Main thread | No | No |
| **Framer Motion** | ~32 KB gzip | Main thread | Partial | React only |

### Performance Tiers

**Tier 1 - Compositor thread (best performance):**
CSS transitions, CSS animations, and WAAPI can all run animations **off the main thread** on the GPU compositor, but only for these properties: `transform`, `opacity`, `filter`, `clip-path`. These animations remain smooth even when JavaScript is busy.

**Tier 2 - Main thread, optimized:**
Libraries like GSAP and anime.js use requestAnimationFrame internally. They animate the same CSS properties but run on the main thread, meaning they can jank if the main thread is blocked. In practice this is rarely an issue for board games since the main thread is mostly idle.

**Tier 3 - Main thread, canvas:**
Manual requestAnimationFrame loops for canvas rendering. You have full control but must handle all interpolation, timing, and easing yourself.

### Recommendation for Board Games

**Build custom with WAAPI + requestAnimationFrame. Skip the animation libraries.**

Here is why:

1. Board games have **discrete, infrequent animations** (a piece slides from A to B, a card flips, a die rolls). These are not complex choreographed sequences.

2. **WAAPI** (`element.animate()`) is built into every browser, costs 0 bytes, runs on the compositor, and handles the common cases (move, fade, rotate) perfectly:

```javascript
// Slide a DOM piece from one board position to another
function slidePiece(element, fromX, fromY, toX, toY, duration = 400) {
  return element.animate([
    { transform: `translate(${fromX}px, ${fromY}px)` },
    { transform: `translate(${toX}px, ${toY}px)` }
  ], {
    duration,
    easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)', // easeOutQuad
    fill: 'forwards'
  }).finished; // Returns a Promise
}

// Usage with async/await
await slidePiece(pieceEl, 0, 0, 200, 300);
// Animation complete, update game state
```

3. **requestAnimationFrame** handles canvas animations where WAAPI cannot reach:

```javascript
function animateCanvasObject(obj, targetX, targetY, duration = 400) {
  const startX = obj.x, startY = obj.y;
  const startTime = performance.now();

  return new Promise(resolve => {
    function frame(now) {
      const elapsed = now - startTime;
      const t = Math.min(elapsed / duration, 1);
      const eased = easeOutCubic(t);

      obj.x = startX + (targetX - startX) * eased;
      obj.y = startY + (targetY - startY) * eased;

      if (t < 1) {
        requestAnimationFrame(frame);
      } else {
        resolve();
      }
    }
    requestAnimationFrame(frame);
  });
}
```

4. **GSAP** is now free (Webflow acquired GreenSock in 2024), but its timeline/sequencing features are overkill for board games. The only scenario where GSAP earns its 23KB is if you need complex choreographed sequences with overlapping animations - unlikely for most board games.

5. **Framer Motion** is React-only and 32KB. If you are already in React and want declarative animations, it is fine, but it is not solving a board-game-specific problem.

6. **anime.js v4** is the lightest external option (~10-15KB) with good modular imports and TypeScript support. Consider it if you find yourself reinventing too many WAAPI wrappers.

---

## 3. Sprite Sheet Handling and Asset Management

### When You Need Sprite Sheets

Board games typically do **not** need traditional sprite sheet animation (frame-by-frame character animation). What they do need:

- **Texture atlases**: Combine many small images (piece icons, card faces, tile textures) into one or a few large images to reduce HTTP requests and improve batching
- **Card face sheets**: A single image with all card faces in a grid
- **Dice face sheets**: All face states in one image

### Simple Atlas Pattern (No Library Needed)

```javascript
// atlas-manifest.json
{
  "image": "pieces-atlas.png",
  "frames": {
    "pawn-red":   { "x": 0,   "y": 0,   "w": 64, "h": 64 },
    "pawn-blue":  { "x": 64,  "y": 0,   "w": 64, "h": 64 },
    "knight-red": { "x": 128, "y": 0,   "w": 64, "h": 64 },
    "knight-blue":{ "x": 192, "y": 0,   "w": 64, "h": 64 }
  }
}
```

```javascript
class TextureAtlas {
  constructor(image, manifest) {
    this.image = image;
    this.frames = manifest.frames;
  }

  static async load(manifestUrl) {
    const manifest = await fetch(manifestUrl).then(r => r.json());
    const image = await new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = manifest.image;
    });
    return new TextureAtlas(image, manifest);
  }

  draw(ctx, frameName, destX, destY, destW, destH) {
    const f = this.frames[frameName];
    if (!f) throw new Error(`Unknown frame: ${frameName}`);
    ctx.drawImage(
      this.image,
      f.x, f.y, f.w, f.h,     // source rect
      destX, destY,             // destination position
      destW ?? f.w, destH ?? f.h // destination size
    );
  }
}
```

### Asset Preloader Pattern

```javascript
class AssetLoader {
  #loaded = new Map();
  #pending = [];

  addImage(key, url) {
    this.#pending.push({ key, url, type: 'image' });
    return this;
  }

  addAtlas(key, manifestUrl) {
    this.#pending.push({ key, url: manifestUrl, type: 'atlas' });
    return this;
  }

  addAudio(key, url) {
    this.#pending.push({ key, url, type: 'audio' });
    return this;
  }

  async load(onProgress) {
    const total = this.#pending.length;
    let completed = 0;

    await Promise.all(this.#pending.map(async (item) => {
      let asset;
      switch (item.type) {
        case 'image':
          asset = await this.#loadImage(item.url);
          break;
        case 'atlas':
          asset = await TextureAtlas.load(item.url);
          break;
        case 'audio':
          asset = await this.#loadAudio(item.url);
          break;
      }
      this.#loaded.set(item.key, asset);
      completed++;
      onProgress?.(completed / total);
    }));

    this.#pending = [];
  }

  get(key) {
    return this.#loaded.get(key);
  }

  #loadImage(url) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = () => reject(new Error(`Failed to load: ${url}`));
      img.src = url;
    });
  }

  #loadAudio(url) {
    return new Promise((resolve, reject) => {
      const audio = new Audio();
      audio.oncanplaythrough = () => resolve(audio);
      audio.onerror = () => reject(new Error(`Failed to load: ${url}`));
      audio.src = url;
    });
  }
}

// Usage
const assets = new AssetLoader();
assets
  .addAtlas('pieces', '/assets/pieces-atlas.json')
  .addImage('board', '/assets/board.svg')
  .addAudio('move', '/assets/move.mp3');

await assets.load(progress => {
  loadingBar.style.width = `${progress * 100}%`;
});
```

### Recommendations

- Use **SVG** for board artwork and piece graphics where possible (infinite scalability, small file size, can be embedded in DOM)
- Use **texture atlases** when you have many small raster images (card game with 52+ unique card faces)
- Use **power-of-two dimensions** (256x256, 512x512, 1024x1024) for atlas images for GPU compatibility
- **Trim transparent pixels** in atlas frames to pack more tightly
- Tools like TexturePacker or the free SpritePilot can generate atlases and JSON manifests
- For small piece counts (<20 unique images), individual files are fine with HTTP/2 multiplexing

---

## 4. Responsive & Scalable Board Layouts

### The Core Challenge

A board game has a fixed aspect ratio (the board is usually square or a specific rectangle), but screens vary from 320px phone to 2560px desktop, landscape or portrait.

### Strategy: Virtual Resolution + CSS Scaling

Design the game at a fixed "virtual" resolution, then scale it to fit the viewport:

```javascript
class GameViewport {
  constructor(canvas, virtualWidth, virtualHeight) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.virtualW = virtualWidth;
    this.virtualH = virtualHeight;
    this.scale = 1;
    this.offsetX = 0;
    this.offsetY = 0;

    this.resize();
    window.addEventListener('resize', () => this.resize());
  }

  resize() {
    const dpr = window.devicePixelRatio || 1;
    const parentW = this.canvas.parentElement.clientWidth;
    const parentH = this.canvas.parentElement.clientHeight;

    // Fit virtual resolution into available space (letterbox)
    const scaleX = parentW / this.virtualW;
    const scaleY = parentH / this.virtualH;
    this.scale = Math.min(scaleX, scaleY);

    // Center the board
    const displayW = this.virtualW * this.scale;
    const displayH = this.virtualH * this.scale;
    this.offsetX = (parentW - displayW) / 2;
    this.offsetY = (parentH - displayH) / 2;

    // Set canvas pixel dimensions for DPR
    this.canvas.width = parentW * dpr;
    this.canvas.height = parentH * dpr;
    this.canvas.style.width = `${parentW}px`;
    this.canvas.style.height = `${parentH}px`;

    // Apply combined transform
    this.ctx.setTransform(
      this.scale * dpr, 0,
      0, this.scale * dpr,
      this.offsetX * dpr,
      this.offsetY * dpr
    );
  }

  // Convert screen coordinates to virtual (game) coordinates
  screenToVirtual(screenX, screenY) {
    const rect = this.canvas.getBoundingClientRect();
    return {
      x: (screenX - rect.left - this.offsetX) / this.scale,
      y: (screenY - rect.top - this.offsetY) / this.scale
    };
  }
}

// Usage: design everything in 1000x1000 virtual space
const viewport = new GameViewport(canvas, 1000, 1000);
// Draw at virtual coordinates - automatically scales
ctx.fillRect(100, 100, 50, 50); // always at the same board position
```

### High-DPI / Retina Support

The critical pattern for crisp canvas rendering on retina displays:

```javascript
function setupHiDPICanvas(canvas, width, height) {
  const dpr = window.devicePixelRatio || 1;

  // Set display size via CSS
  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;

  // Set actual pixel buffer size
  canvas.width = width * dpr;
  canvas.height = height * dpr;

  // Scale drawing context so 1 unit = 1 CSS pixel
  const ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);

  return ctx;
}
```

Without this, canvas content looks blurry on phones and retina laptops.

### CSS-Based Board Layout (For DOM-Rendered Games)

For simpler games where the board is DOM elements:

```css
.board-container {
  /* Fill available space while maintaining aspect ratio */
  width: 100%;
  max-width: 100vh; /* Prevent board from being taller than viewport */
  aspect-ratio: 1 / 1;
  margin: 0 auto;

  display: grid;
  grid-template-columns: repeat(8, 1fr); /* 8x8 chess-like grid */
  grid-template-rows: repeat(8, 1fr);
  gap: 1px;
}

.board-cell {
  position: relative;
  /* Pieces size themselves relative to cell */
}

.game-piece {
  position: absolute;
  width: 80%;
  height: 80%;
  top: 10%;
  left: 10%;
  /* Animate movement with transforms */
  transition: transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .board-container {
    max-width: 100vw;
  }
}

/* Use container queries for component-level responsiveness */
@container game-area (max-width: 400px) {
  .piece-label { display: none; }
  .score-display { font-size: 0.8rem; }
}
```

---

## 5. Touch and Mouse Input: Drag-and-Drop Game Pieces

### Use Pointer Events (Not Mouse + Touch Separately)

Pointer Events unify mouse, touch, and pen input. This is the modern standard (supported in all browsers since ~2020):

```javascript
class DraggableSystem {
  constructor(canvas, viewport) {
    this.canvas = canvas;
    this.viewport = viewport; // GameViewport from section 4
    this.pieces = [];         // game objects with { x, y, width, height }
    this.dragging = null;     // { piece, offsetX, offsetY }

    // Critical CSS: prevent browser touch behaviors
    canvas.style.touchAction = 'none';  // prevents scroll/zoom on touch
    canvas.style.userSelect = 'none';   // prevents text selection

    canvas.addEventListener('pointerdown', e => this.onDown(e));
    canvas.addEventListener('pointermove', e => this.onMove(e));
    canvas.addEventListener('pointerup', e => this.onUp(e));
    canvas.addEventListener('pointercancel', e => this.onUp(e));

    // Prevent default drag behavior (image ghosting etc.)
    canvas.addEventListener('dragstart', e => e.preventDefault());
  }

  onDown(e) {
    // Only handle primary button (left click / first touch)
    if (e.button !== 0) return;

    const pos = this.viewport.screenToVirtual(e.clientX, e.clientY);

    // Hit test: find topmost piece under pointer (iterate in reverse for z-order)
    for (let i = this.pieces.length - 1; i >= 0; i--) {
      const piece = this.pieces[i];
      if (this.hitTest(pos, piece)) {
        // Capture pointer to this element - receives all future events
        // even if pointer leaves the canvas
        this.canvas.setPointerCapture(e.pointerId);

        this.dragging = {
          piece,
          pointerId: e.pointerId,
          offsetX: pos.x - piece.x,
          offsetY: pos.y - piece.y
        };

        // Move piece to top of z-order
        this.pieces.splice(i, 1);
        this.pieces.push(piece);
        break;
      }
    }
  }

  onMove(e) {
    if (!this.dragging || e.pointerId !== this.dragging.pointerId) return;

    const pos = this.viewport.screenToVirtual(e.clientX, e.clientY);
    this.dragging.piece.x = pos.x - this.dragging.offsetX;
    this.dragging.piece.y = pos.y - this.dragging.offsetY;

    // Request redraw (if not already in a render loop)
    this.needsRedraw = true;
  }

  onUp(e) {
    if (!this.dragging || e.pointerId !== this.dragging.pointerId) return;

    const piece = this.dragging.piece;
    this.dragging = null;

    // Snap to grid (common in board games)
    const snapped = this.snapToGrid(piece.x, piece.y);

    // Validate move with game logic
    if (this.isValidPlacement(piece, snapped)) {
      // Animate snap
      this.animateSnap(piece, snapped.x, snapped.y);
    } else {
      // Animate return to original position
      this.animateSnap(piece, piece.originalX, piece.originalY);
    }
  }

  hitTest(pos, piece) {
    return pos.x >= piece.x
      && pos.x <= piece.x + piece.width
      && pos.y >= piece.y
      && pos.y <= piece.y + piece.height;
  }

  snapToGrid(x, y) {
    const cellSize = 100; // virtual units
    return {
      x: Math.round(x / cellSize) * cellSize,
      y: Math.round(y / cellSize) * cellSize
    };
  }

  animateSnap(piece, targetX, targetY, duration = 200) {
    const startX = piece.x, startY = piece.y;
    const startTime = performance.now();

    const frame = (now) => {
      const t = Math.min((now - startTime) / duration, 1);
      const eased = easeOutCubic(t);
      piece.x = startX + (targetX - startX) * eased;
      piece.y = startY + (targetY - startY) * eased;
      this.needsRedraw = true;
      if (t < 1) requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
  }
}
```

### Key Gotchas

1. **`touch-action: none` in CSS** is mandatory. Without it, the browser intercepts touch gestures for scrolling/zooming.
2. **`setPointerCapture()`** ensures you keep receiving events even if the pointer leaves the canvas.
3. **Check `e.button === 0`** to ignore right-clicks and middle-clicks.
4. **Track `e.pointerId`** if you need to handle multi-touch (e.g., two players dragging simultaneously).
5. **`pointercancel`** fires when the browser takes over (e.g., OS gesture). Always treat it like `pointerup`.

### For DOM-Based Pieces

If pieces are DOM elements rather than canvas objects, the same Pointer Events pattern applies but you attach listeners to each piece element and use CSS `transform: translate()` for positioning:

```javascript
piece.addEventListener('pointerdown', (e) => {
  piece.setPointerCapture(e.pointerId);
  const rect = piece.getBoundingClientRect();
  offsetX = e.clientX - rect.left;
  offsetY = e.clientY - rect.top;
});

piece.addEventListener('pointermove', (e) => {
  if (!piece.hasPointerCapture(e.pointerId)) return;
  piece.style.transform = `translate(${e.clientX - offsetX}px, ${e.clientY - offsetY}px)`;
});
```

---

## 6. Camera / Viewport for Scrollable & Zoomable Boards

For large boards that do not fit on screen (e.g., a Catan map, a dungeon crawler, a war game map):

### Camera Model

```javascript
class Camera {
  constructor() {
    this.x = 0;      // canvas-space offset X
    this.y = 0;      // canvas-space offset Y
    this.zoom = 1;   // 1.0 = 100%
    this.minZoom = 0.25;
    this.maxZoom = 4;
  }

  // Convert screen pixel position to world/board coordinates
  screenToWorld(screenX, screenY) {
    return {
      x: screenX / this.zoom - this.x,
      y: screenY / this.zoom - this.y
    };
  }

  // Convert world coordinates to screen pixel position
  worldToScreen(worldX, worldY) {
    return {
      x: (worldX + this.x) * this.zoom,
      y: (worldY + this.y) * this.zoom
    };
  }

  // Pan by screen-space delta
  pan(deltaScreenX, deltaScreenY) {
    // Divide by zoom so panning speed is consistent regardless of zoom level
    this.x += deltaScreenX / this.zoom;
    this.y += deltaScreenY / this.zoom;
  }

  // Zoom toward a specific screen point (keeps that point stationary)
  zoomAt(screenX, screenY, zoomDelta) {
    const worldBefore = this.screenToWorld(screenX, screenY);

    this.zoom = Math.max(this.minZoom,
      Math.min(this.maxZoom, this.zoom * zoomDelta));

    const worldAfter = this.screenToWorld(screenX, screenY);

    // Adjust position so the point under cursor stays fixed
    this.x += worldAfter.x - worldBefore.x;
    this.y += worldAfter.y - worldBefore.y;
  }

  // Apply camera transform to a canvas context before drawing
  applyToContext(ctx) {
    ctx.setTransform(this.zoom, 0, 0, this.zoom,
      this.x * this.zoom, this.y * this.zoom);
  }
}
```

### Input Handling for Pan & Zoom

```javascript
function setupCameraControls(canvas, camera) {
  let isPanning = false;
  let lastX, lastY;

  canvas.style.touchAction = 'none';

  // Pan: click/touch and drag
  canvas.addEventListener('pointerdown', e => {
    // Middle mouse button or two-finger touch for panning
    // (or any button if no game piece was hit)
    isPanning = true;
    lastX = e.clientX;
    lastY = e.clientY;
    canvas.setPointerCapture(e.pointerId);
  });

  canvas.addEventListener('pointermove', e => {
    if (!isPanning) return;
    const dx = e.clientX - lastX;
    const dy = e.clientY - lastY;
    camera.pan(dx, dy);
    lastX = e.clientX;
    lastY = e.clientY;
    requestRedraw();
  });

  canvas.addEventListener('pointerup', () => { isPanning = false; });

  // Zoom: scroll wheel (or ctrl+scroll, or pinch-zoom)
  canvas.addEventListener('wheel', e => {
    e.preventDefault();

    // Ctrl+wheel = zoom, plain wheel = pan (following map app conventions)
    if (e.ctrlKey) {
      // Pinch-zoom on trackpad fires as ctrl+wheel
      const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
      camera.zoomAt(e.clientX, e.clientY, zoomFactor);
    } else {
      camera.pan(-e.deltaX, -e.deltaY);
    }

    requestRedraw();
  }, { passive: false });
}
```

### When You Need This

Most board games do **not** need pan/zoom. A standard chess/checkers/Go board fits on any screen. You need this for:
- Large hex-map strategy games
- Scrollable game worlds
- Games where the board is much larger than the viewport
- Zoomable detail on dense boards

For fixed-size boards, the GameViewport from Section 4 (scale-to-fit) is sufficient.

---

## 7. Performance Optimization: What Actually Matters for Board Games

### What Does NOT Matter

Board games are not particle simulators or action games. Do not optimize for:
- Raw draw call throughput (you have <500 objects)
- Physics engine performance
- Sprite batching (irrelevant at board game object counts)
- Frame-perfect collision detection

### What DOES Matter

**1. Only redraw when something changes.**

Board games are 90% idle. Do not run a 60fps render loop that redraws the same static board every frame.

```javascript
class GameRenderer {
  #dirty = true;

  markDirty() {
    if (this.#dirty) return; // already scheduled
    this.#dirty = true;
    requestAnimationFrame(() => this.render());
  }

  render() {
    if (!this.#dirty) return;
    this.#dirty = false;

    // Full render
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.drawBoard();
    this.drawPieces();
    this.drawEffects();
  }

  // During animation, switch to continuous loop
  startAnimationLoop() {
    const loop = () => {
      if (!this.animating) return;
      this.#dirty = true;
      this.render();
      requestAnimationFrame(loop);
    };
    this.animating = true;
    requestAnimationFrame(loop);
  }

  stopAnimationLoop() {
    this.animating = false;
  }
}
```

**2. Layer static and dynamic content.**

Use separate canvases: one for the static board that renders once, one for pieces that update when they move.

```javascript
// Render board background once (or on resize)
function renderBoardOnce(bgCanvas, bgCtx) {
  // Draw grid, textures, decorations
  drawGrid(bgCtx);
  drawSquareColors(bgCtx);
  drawLabels(bgCtx);
  // Never touch this canvas again until resize
}

// Only redraw the piece layer when pieces change
function renderPieces(pieceCanvas, pieceCtx, pieces) {
  pieceCtx.clearRect(0, 0, pieceCanvas.width, pieceCanvas.height);
  for (const piece of pieces) {
    drawPiece(pieceCtx, piece);
  }
}
```

**3. Disable canvas alpha if your background is opaque.**

```javascript
const ctx = canvas.getContext('2d', { alpha: false });
```

This tells the browser it does not need to composite this canvas with transparency, saving work.

**4. Use integer coordinates to avoid sub-pixel anti-aliasing.**

```javascript
ctx.drawImage(sprite, Math.round(x), Math.round(y));
```

**5. Avoid expensive operations in the hot path.**
- `shadowBlur` is very expensive
- Text rendering is expensive - cache rendered text as images if you draw lots of it on canvas
- `getImageData()` / `putImageData()` are slow - avoid per-frame
- Gradient creation - create once, reuse

**6. Pre-render complex shapes to offscreen canvases.**

```javascript
function createPieceSprite(draw, width, height) {
  const offscreen = document.createElement('canvas');
  offscreen.width = width;
  offscreen.height = height;
  const ctx = offscreen.getContext('2d');
  draw(ctx, width, height);
  return offscreen; // Use as image source in drawImage()
}

// Create once at startup
const knightSprite = createPieceSprite((ctx, w, h) => {
  // Complex knight drawing with gradients, shadows, etc.
  ctx.shadowBlur = 5;
  ctx.shadowColor = 'rgba(0,0,0,0.3)';
  // ... detailed drawing
}, 64, 64);

// Draw cheaply every frame
ctx.drawImage(knightSprite, piece.x, piece.y);
```

**7. OffscreenCanvas + Web Workers** for truly heavy rendering. Generally overkill for board games, but useful if you have a complex minimap or procedural board generation. Moves rendering off the main thread entirely.

### Performance Budget for Board Games

Realistically, on a modern device a board game should target:
- **Static board render**: <16ms (one-time)
- **Piece layer redraw**: <4ms (leaves 12ms headroom in a 16ms frame)
- **Animation frames**: 60fps during movement, idle otherwise
- **Input latency**: <50ms from touch to visual feedback

You are unlikely to hit performance problems with Canvas 2D for a board game unless you are doing something egregiously wrong (redrawing 1000 shadow-blurred shapes every frame, etc.).

---

## 8. PixiJS: Appropriate or Overkill?

### What PixiJS Is

PixiJS v8 (current) is a WebGL/WebGPU 2D rendering engine. It is **not** a game framework - it provides rendering, a scene graph, and basic interactivity, but not game logic, physics, or AI.

### When PixiJS Is Worth It for Board Games

- Your board game has **rich visual effects**: particle systems, shader effects, blend modes, glow, etc.
- You are rendering **1000+ sprites** with complex transforms
- You need **consistent high performance** across devices with GPU acceleration
- You want built-in **sprite, text, and graphics primitives** without building your own scene graph
- Your game has **card animations with complex transforms** (3D perspective, masking, etc.)

### When PixiJS Is Overkill

- Your game has <200 visual elements
- You do not need particle effects or shaders
- A pure CSS/DOM approach meets your visual needs
- You want to minimize bundle size (PixiJS v8 is ~100KB+ gzipped depending on tree-shaking)
- You are building a simple card game or turn-based strategy with basic visuals

### PixiJS v8 Notable Features for Board Games

- **Smart rendering**: Only updates elements that changed. If nothing moved, no code executes.
- **Tree-shaking**: Import only what you need to reduce bundle size.
- **WebGPU backend**: Modern rendering path for newest browsers, with Canvas 2D fallback.
- **pixelLine**: 1px-wide lines regardless of zoom (useful for grids).
- **PerspectiveMesh**: 3D perspective effects for card games.

### Konva.js: The Board Game Sweet Spot?

Konva is a Canvas 2D framework (not WebGL) with a focus on **interactivity**:

| Feature | Konva | PixiJS | Raw Canvas |
|---------|-------|--------|------------|
| Drag & drop | Built-in | Basic | DIY |
| Event bubbling | Yes (DOM-like) | Yes | DIY |
| Hit detection | Automatic | Basic | DIY |
| Transform handles (resize/rotate) | Built-in (Transformer) | No | DIY |
| Animation/Tweens | Built-in | No | DIY |
| React/Vue/Svelte bindings | Yes | Community | N/A |
| Performance (8K objects) | ~23fps | ~60fps | Depends |
| Bundle size | ~40KB gzip | ~100KB+ gzip | 0 |

**Konva is a strong fit for board games** because it solves the exact problems board games have:
- Click/drag/drop on canvas objects
- Event handling per shape
- Layering and grouping
- Built-in animation
- Framework integration

The performance tradeoff (23fps vs 60fps at 8K objects) is irrelevant for board games that have <500 objects.

### Recommendation

| Scenario | Use |
|----------|-----|
| Simple board game (<100 objects, basic visuals) | Raw Canvas 2D or DOM/CSS |
| Mid-complexity board game with drag-and-drop | **Konva.js** or raw Canvas with custom hit-testing |
| Visually rich game with effects and many sprites | **PixiJS** |
| Card game with 3D flip/fan effects | PixiJS (PerspectiveMesh) or CSS 3D transforms |
| Prototype / learning | DOM/CSS first, add Canvas if needed |

---

## 9. CSS-Based vs Canvas: Decision Framework

### Use Pure CSS/DOM When:

1. **Board is a grid** (chess, checkers, tic-tac-toe, Scrabble): CSS Grid or Flexbox handles layout naturally.
2. **Pieces are discrete, countable objects** (<100) that move between grid positions.
3. **Text is prominent** (card games with card text, score displays).
4. **You want accessibility** (screen readers can read DOM elements).
5. **Animations are simple transitions** (slide piece from cell A to cell B).
6. **Responsiveness matters more than visual polish** (CSS media queries and container queries work automatically).

CSS/DOM advantages over Canvas:
- Text rendering is free and high quality
- Event handling is free (click, hover, focus)
- Layout is free (Grid, Flexbox)
- Accessibility is free (ARIA, tab order)
- Responsive design tools work (media queries, container queries, clamp())
- CSS transitions/animations run on the compositor (GPU-accelerated)
- Inspector/devtools work naturally

### Use Canvas When:

1. **You need smooth, continuous animation** of objects along arbitrary paths (not just grid-to-grid).
2. **Many objects overlap** and you need precise z-ordering and compositing.
3. **Custom rendering** (procedurally drawn boards, dynamic visual effects).
4. **Pixel-level control** (hit regions that do not correspond to rectangles).
5. **Performance at scale** (>500 animated objects).
6. **Pan/zoom** on a large board surface.

### CSS Board Game Pattern

```css
/* A complete CSS-only board game layout */
.game-layout {
  display: grid;
  grid-template-areas:
    "info  board  info2"
    "hand  hand   hand";
  grid-template-columns: 200px 1fr 200px;
  grid-template-rows: 1fr auto;
  height: 100dvh;
  gap: 8px;
  padding: 8px;
}

.board {
  grid-area: board;
  display: grid;
  grid-template-columns: repeat(var(--cols, 8), 1fr);
  grid-template-rows: repeat(var(--rows, 8), 1fr);
  aspect-ratio: 1;
  max-height: 100%;
  margin: 0 auto;
}

.cell {
  position: relative;
  border: 1px solid #ddd;
}

.cell::before {
  content: '';
  display: block;
  padding-top: 100%; /* Force square cells */
}

.piece {
  position: absolute;
  inset: 10%;
  border-radius: 50%;
  cursor: grab;
  /* GPU-accelerated movement */
  transition: transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  will-change: transform;
}

.piece.dragging {
  cursor: grabbing;
  z-index: 100;
  transition: none; /* Disable transition during drag */
}

/* Card hand at bottom */
.hand {
  grid-area: hand;
  display: flex;
  justify-content: center;
  gap: -20px; /* Overlap cards */
}

/* Responsive: stack layout on mobile */
@media (max-width: 768px) {
  .game-layout {
    grid-template-areas:
      "board"
      "info"
      "hand";
    grid-template-columns: 1fr;
    grid-template-rows: 1fr auto auto;
  }
}
```

---

## 10. Animation Easing & Interpolation for Board Games

### Easing Functions to Build Custom (No Library Needed)

These pure functions take `t` (0 to 1) and return an eased value:

```javascript
const Ease = {
  // Most useful for board games:

  // Smooth deceleration - piece slides and gently stops
  outCubic: t => 1 - Math.pow(1 - t, 3),

  // Smooth acceleration then deceleration - natural feeling
  inOutCubic: t => t < 0.5
    ? 4 * t * t * t
    : 1 - Math.pow(-2 * t + 2, 3) / 2,

  // Quick start, gentle stop - snappy piece placement
  outQuart: t => 1 - Math.pow(1 - t, 4),

  // Overshoot then settle - playful piece snap
  outBack: t => {
    const c1 = 1.70158;
    const c3 = c1 + 1;
    return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
  },

  // Bounce at the end - dice landing, token dropping
  outBounce: t => {
    const n1 = 7.5625, d1 = 2.75;
    if (t < 1 / d1)       return n1 * t * t;
    if (t < 2 / d1)       return n1 * (t -= 1.5 / d1) * t + 0.75;
    if (t < 2.5 / d1)     return n1 * (t -= 2.25 / d1) * t + 0.9375;
    return n1 * (t -= 2.625 / d1) * t + 0.984375;
  },

  // Elastic wobble - card spring, notification pop
  outElastic: t => {
    if (t === 0 || t === 1) return t;
    return Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * (2 * Math.PI / 3)) + 1;
  },

  // Linear - for rotation, progress bars
  linear: t => t,
};
```

### Spring Physics (Custom, No Library)

For organic, physical-feeling motion (pieces that overshoot and settle):

```javascript
class SpringAnimation {
  constructor({ stiffness = 180, damping = 12, mass = 1 }) {
    this.stiffness = stiffness;
    this.damping = damping;
    this.mass = mass;
  }

  // Animate a value from `from` to `to`, calling `onUpdate` each frame
  animate(from, to, onUpdate) {
    let position = from;
    let velocity = 0;
    const target = to;

    return new Promise(resolve => {
      const step = () => {
        // Spring force: F = -k * displacement
        const displacement = position - target;
        const springForce = -this.stiffness * displacement;

        // Damping force: F = -d * velocity
        const dampingForce = -this.damping * velocity;

        // Acceleration: a = F / m
        const acceleration = (springForce + dampingForce) / this.mass;

        // Euler integration (good enough for UI)
        velocity += acceleration * (1 / 60); // assume 60fps timestep
        position += velocity * (1 / 60);

        onUpdate(position);

        // Check if settled (close enough to target with low velocity)
        if (Math.abs(velocity) < 0.01 && Math.abs(position - target) < 0.1) {
          onUpdate(target); // snap to exact target
          resolve();
        } else {
          requestAnimationFrame(step);
        }
      };
      requestAnimationFrame(step);
    });
  }
}

// Usage
const spring = new SpringAnimation({ stiffness: 200, damping: 15 });
await spring.animate(0, 300, (x) => {
  piece.style.transform = `translateX(${x}px)`;
});
```

### Board Game Animation Recipes

**Piece slide (grid to grid):**
```javascript
async function movePiece(el, fromCell, toCell, opts = {}) {
  const fromRect = fromCell.getBoundingClientRect();
  const toRect = toCell.getBoundingClientRect();
  const dx = toRect.left - fromRect.left;
  const dy = toRect.top - fromRect.top;

  await el.animate([
    { transform: 'translate(0, 0)' },
    { transform: `translate(${dx}px, ${dy}px)` }
  ], {
    duration: opts.duration ?? 350,
    easing: opts.easing ?? 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
    fill: 'forwards'
  }).finished;

  // Re-parent element to new cell
  toCell.appendChild(el);
  el.getAnimations().forEach(a => a.cancel());
}
```

**Card flip (CSS 3D transform):**
```css
.card {
  perspective: 800px;
  width: 120px;
  height: 168px;
}

.card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.card.flipped .card-inner {
  transform: rotateY(180deg);
}

.card-front, .card-back {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  border-radius: 8px;
}

.card-back {
  transform: rotateY(180deg);
}
```

**Card fan (hand of cards):**
```javascript
function layoutCardFan(cards, containerWidth) {
  const cardCount = cards.length;
  const maxSpread = 40; // degrees total spread
  const spreadAngle = Math.min(maxSpread, cardCount * 6);
  const startAngle = -spreadAngle / 2;
  const stepAngle = cardCount > 1 ? spreadAngle / (cardCount - 1) : 0;

  cards.forEach((card, i) => {
    const angle = startAngle + (stepAngle * i);
    const yOffset = Math.abs(angle) * 0.5; // arc: center cards higher
    card.style.transformOrigin = 'bottom center';
    card.style.transform = `
      rotate(${angle}deg)
      translateY(${yOffset}px)
    `;
    card.style.zIndex = i;
    card.style.transition = 'transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
  });
}
```

**Token placement with bounce:**
```javascript
async function placeToken(el, targetX, targetY) {
  // Start above the target, scale from 0
  await el.animate([
    {
      transform: `translate(${targetX}px, ${targetY - 60}px) scale(0.3)`,
      opacity: 0
    },
    {
      transform: `translate(${targetX}px, ${targetY - 10}px) scale(1.1)`,
      opacity: 1,
      offset: 0.6 // 60% through the animation
    },
    {
      transform: `translate(${targetX}px, ${targetY + 3}px) scale(0.95)`,
      offset: 0.8
    },
    {
      transform: `translate(${targetX}px, ${targetY}px) scale(1)`,
      opacity: 1
    }
  ], {
    duration: 500,
    easing: 'ease-out',
    fill: 'forwards'
  }).finished;
}
```

**Dice roll (CSS 3D):**
```css
.die {
  width: 60px;
  height: 60px;
  transform-style: preserve-3d;
  transition: transform 1s cubic-bezier(0.2, 0.8, 0.3, 1);
}

/* Each face positioned in 3D space */
.die-face { position: absolute; inset: 0; backface-visibility: hidden; }
.die-face-1 { transform: translateZ(30px); }
.die-face-2 { transform: rotateY(180deg) translateZ(30px); }
.die-face-3 { transform: rotateY(90deg) translateZ(30px); }
.die-face-4 { transform: rotateY(-90deg) translateZ(30px); }
.die-face-5 { transform: rotateX(90deg) translateZ(30px); }
.die-face-6 { transform: rotateX(-90deg) translateZ(30px); }
```

```javascript
function rollDie(dieEl, result) {
  // Map result (1-6) to rotation that shows that face
  const rotations = {
    1: 'rotateX(0deg) rotateY(0deg)',
    2: 'rotateX(0deg) rotateY(180deg)',
    3: 'rotateX(0deg) rotateY(-90deg)',
    4: 'rotateX(0deg) rotateY(90deg)',
    5: 'rotateX(-90deg) rotateY(0deg)',
    6: 'rotateX(90deg) rotateY(0deg)',
  };

  // Add extra full rotations for drama
  const spins = 2;
  const extraX = 360 * spins;
  const extraY = 360 * spins;

  // Parse target rotation and add spins
  dieEl.style.transform = `
    rotateX(${extraX}deg) rotateY(${extraY}deg)
    ${rotations[result]}
  `;
}
```

### Which Easing for Which Board Game Action

| Action | Easing | Duration | Why |
|--------|--------|----------|-----|
| Piece slide on grid | `outCubic` or `outQuart` | 250-400ms | Quick start, gentle stop feels responsive |
| Card draw from deck | `outCubic` | 300ms | Smooth, not flashy |
| Card flip | `cubic-bezier(0.4, 0, 0.2, 1)` | 400-500ms | Material Design standard, feels natural |
| Card fan rearrange | `inOutCubic` | 300ms | Symmetric ease for shuffling motion |
| Token drop/placement | `outBounce` or custom overshoot | 400-600ms | Physical feel, satisfying placement |
| Dice roll | `cubic-bezier(0.2, 0.8, 0.3, 1)` | 800-1200ms | Fast start, slow settle |
| Score counter change | `outQuart` | 200ms | Snappy number update |
| Board zoom | `outCubic` | 200ms | Responsive, no overshoot |
| Captured piece removal | `outQuart` + opacity | 300ms | Quick fade + scale down |
| Error shake (invalid move) | `outElastic` | 400ms | Attention-getting wobble |

---

## Summary Recommendations

### Minimal-Library Stack for Board Games

1. **Rendering**: HTML/CSS for UI + Canvas 2D for the board (hybrid approach). No rendering library needed for most board games.

2. **Animation**: Web Animations API (`element.animate()`) for DOM elements, `requestAnimationFrame` with custom easing functions for canvas. No animation library needed.

3. **Input**: Pointer Events API (built into browsers). No library needed.

4. **Asset Loading**: Custom preloader (50 lines of code). No library needed.

5. **Sprite Atlases**: Custom TextureAtlas class (30 lines of code) + TexturePacker or SpritePilot for generating atlases.

### When to Reach for a Library

| Need | Recommended Library | Why |
|------|-------------------|-----|
| Canvas with built-in drag/drop, events, grouping | **Konva.js** (~40KB) | Solves the exact interaction problems board games have |
| High-performance rendering with effects | **PixiJS** (~100KB+) | Only if you need WebGL-level visuals |
| Complex choreographed animation sequences | **GSAP** (~23KB, now free) | Only if custom WAAPI wrappers feel insufficient |
| Lightweight framework-agnostic animation | **anime.js v4** (~15KB) | Good middle ground if you want a tiny animation helper |

### What to Build Custom

- Easing functions (10 lines each, copy from this document)
- Spring physics animation (30 lines)
- Asset preloader (50 lines)
- Texture atlas loader (30 lines)
- Camera/viewport (40 lines)
- Drag-and-drop system (60 lines)
- Game render loop with dirty tracking (30 lines)

Total custom code for a full board game rendering system: ~250 lines, 0 KB of dependencies.
