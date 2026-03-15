# Rendering and Animation

## Rendering Strategy Decision Tree

```
Is your board a standard grid (chess, checkers, Go)?
  → CSS Grid + HTML elements

Is your board hexagonal (Catan, hex wargames)?
  → CSS Grid with hex layout or SVG hexagons

Is your board freeform (Risk map, area control)?
  → SVG paths for regions + HTML overlays for tokens

Do you have 500+ simultaneously animated elements?
  → Canvas 2D

Do you need particle effects (explosions, sparkles)?
  → Canvas 2D overlay on top of DOM board

Everything else?
  → DOM with CSS transforms
```

---

## Board Layouts

### Square Grid Board (Chess, Checkers, Tic-Tac-Toe)

```typescript
interface BoardConfig {
  rows: number;
  cols: number;
  cellSize?: number;  // Auto-calculated if not provided
}

function createGridBoard(config: BoardConfig, container: HTMLElement): HTMLElement {
  const board = document.createElement("div");
  board.className = "game-board grid-board";
  board.style.cssText = `
    display: grid;
    grid-template-columns: repeat(${config.cols}, 1fr);
    grid-template-rows: repeat(${config.rows}, 1fr);
    aspect-ratio: ${config.cols} / ${config.rows};
    width: 100%;
    max-width: min(90vw, 90vh * ${config.cols / config.rows});
    margin: 0 auto;
    position: relative;
  `;

  // Create cells
  for (let row = 0; row < config.rows; row++) {
    for (let col = 0; col < config.cols; col++) {
      const cell = document.createElement("div");
      cell.className = "cell";
      cell.dataset.row = String(row);
      cell.dataset.col = String(col);
      cell.style.cssText = `
        aspect-ratio: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
      `;
      board.appendChild(cell);
    }
  }

  container.appendChild(board);
  return board;
}

// CSS for alternating cell colors (chess pattern)
const boardStyles = `
  .grid-board .cell:nth-child(odd) { background: var(--cell-light, #f0d9b5); }
  .grid-board .cell:nth-child(even) { background: var(--cell-dark, #b58863); }
  /* Adjust for even-width boards */
  .grid-board[data-cols-even] .cell:nth-child(odd) { background: var(--cell-dark); }
  .grid-board[data-cols-even] .cell:nth-child(even) { background: var(--cell-light); }
`;
```

### Hexagonal Grid Board (Catan, Hex Strategy)

Hex grids require offset coordinates. Two common layouts: flat-top and pointy-top.

```typescript
interface HexConfig {
  radius: number;      // Number of rings from center (Catan = 3)
  hexSize: number;     // Pixel size of each hex
  orientation: "flat" | "pointy";
}

function createHexBoard(config: HexConfig, container: HTMLElement): SVGElement {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  const hexes: SVGElement[] = [];

  // Generate hex positions using axial coordinates
  for (let q = -config.radius; q <= config.radius; q++) {
    for (let r = -config.radius; r <= config.radius; r++) {
      const s = -q - r;
      if (Math.abs(s) > config.radius) continue;

      const { x, y } = axialToPixel(q, r, config.hexSize, config.orientation);
      const hex = createHexagon(x, y, config.hexSize, config.orientation);
      hex.dataset.q = String(q);
      hex.dataset.r = String(r);
      svg.appendChild(hex);
      hexes.push(hex);
    }
  }

  // Size the SVG to fit all hexes
  const bbox = calculateBounds(hexes, config);
  svg.setAttribute("viewBox", `${bbox.x} ${bbox.y} ${bbox.width} ${bbox.height}`);
  svg.style.cssText = "width: 100%; max-width: min(90vw, 90vh); margin: 0 auto; display: block;";

  container.appendChild(svg);
  return svg;
}

function axialToPixel(q: number, r: number, size: number, orientation: string): { x: number; y: number } {
  if (orientation === "flat") {
    return {
      x: size * (3 / 2 * q),
      y: size * (Math.sqrt(3) / 2 * q + Math.sqrt(3) * r),
    };
  }
  // Pointy top
  return {
    x: size * (Math.sqrt(3) * q + Math.sqrt(3) / 2 * r),
    y: size * (3 / 2 * r),
  };
}

function createHexagon(cx: number, cy: number, size: number, orientation: string): SVGPolygonElement {
  const hex = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
  const angleOffset = orientation === "flat" ? 0 : 30;
  const points = Array.from({ length: 6 }, (_, i) => {
    const angle = (60 * i + angleOffset) * Math.PI / 180;
    return `${cx + size * Math.cos(angle)},${cy + size * Math.sin(angle)}`;
  }).join(" ");
  hex.setAttribute("points", points);
  return hex;
}
```

### Freeform Map Board (Risk, Area Control)

Use SVG paths for irregular regions. Each region is a clickable path.

```typescript
// Define regions as SVG path data (export from Illustrator/Figma/Inkscape)
const regions: Record<string, { path: string; center: { x: number; y: number } }> = {
  "north-america": {
    path: "M 100,50 L 250,30 L 300,120 L 200,180 L 80,150 Z",
    center: { x: 180, y: 100 },
  },
  // ... more regions
};

function createMapBoard(container: HTMLElement): SVGElement {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 1000 600");

  for (const [id, region] of Object.entries(regions)) {
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", region.path);
    path.dataset.region = id;
    path.classList.add("map-region");
    svg.appendChild(path);

    // Token placement point
    const marker = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    marker.setAttribute("cx", String(region.center.x));
    marker.setAttribute("cy", String(region.center.y));
    marker.setAttribute("r", "8");
    marker.classList.add("region-marker");
    svg.appendChild(marker);
  }

  container.appendChild(svg);
  return svg;
}
```

---

## Piece Rendering

### HTML Element Pieces

Best for: chess pieces, tokens, meeples — anything with a fixed position on the grid.

```typescript
interface PieceRenderer {
  create(piece: PieceData): HTMLElement;
  moveTo(element: HTMLElement, row: number, col: number): Promise<void>;
  capture(element: HTMLElement): Promise<void>;
  highlight(element: HTMLElement, type: "selected" | "valid-move" | "check"): void;
}

function createPieceElement(piece: PieceData): HTMLElement {
  const el = document.createElement("div");
  el.className = `piece piece-${piece.type} player-${piece.owner}`;
  el.dataset.pieceId = piece.id;
  el.style.cssText = `
    grid-column: ${piece.col + 1};
    grid-row: ${piece.row + 1};
    width: 80%;
    height: 80%;
    margin: 10%;
    z-index: 10;
    pointer-events: auto;
    cursor: grab;
    transition: filter 0.2s;
  `;

  // Use SVG or image for piece graphic
  if (piece.svgPath) {
    el.innerHTML = `<img src="${piece.svgPath}" alt="${piece.type}" draggable="false" style="width:100%;height:100%;">`;
  } else {
    // Unicode chess pieces as fallback
    el.textContent = PIECE_UNICODE[piece.type][piece.owner];
    el.style.fontSize = "min(5vw, 48px)";
    el.style.textAlign = "center";
    el.style.lineHeight = "1";
  }

  return el;
}

// Place pieces on the board using CSS Grid placement
function placePiece(board: HTMLElement, piece: HTMLElement) {
  // Pieces sit in the same grid as cells, overlaid
  piece.style.gridColumn = piece.dataset.col!;
  piece.style.gridRow = piece.dataset.row!;
  board.appendChild(piece);
}
```

### SVG Pieces

Best for: scalable pieces that need to transform smoothly, pieces on hex/map boards.

```typescript
function createSVGPiece(piece: PieceData, parentSvg: SVGElement): SVGGElement {
  const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
  group.dataset.pieceId = piece.id;

  const { x, y } = gridToPixel(piece.row, piece.col);
  group.setAttribute("transform", `translate(${x}, ${y})`);

  // Use <use> to reference piece definitions for efficiency
  const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
  use.setAttribute("href", `#piece-${piece.type}-${piece.owner}`);
  group.appendChild(use);

  parentSvg.appendChild(group);
  return group;
}
```

---

## Card Rendering

### Card Hand (Fan Layout)

```typescript
interface CardHandConfig {
  maxFanAngle: number;     // Total spread angle in degrees (e.g., 30)
  cardWidth: number;
  cardHeight: number;
  hoverLift: number;       // Pixels to lift on hover
  selectedLift: number;    // Pixels to lift when selected
}

function renderCardHand(
  cards: CardData[],
  container: HTMLElement,
  config: CardHandConfig
) {
  container.style.cssText = `
    position: relative;
    display: flex;
    justify-content: center;
    align-items: flex-end;
    height: ${config.cardHeight + config.selectedLift + 20}px;
    perspective: 800px;
  `;

  const n = cards.length;
  const angleStep = n > 1 ? config.maxFanAngle / (n - 1) : 0;
  const startAngle = -config.maxFanAngle / 2;

  cards.forEach((card, i) => {
    const el = createCardElement(card, config);
    const angle = startAngle + angleStep * i;
    const offsetX = (i - (n - 1) / 2) * (config.cardWidth * 0.4);

    el.style.cssText += `
      position: absolute;
      left: 50%;
      bottom: 0;
      transform: translateX(${offsetX}px) rotate(${angle}deg);
      transform-origin: bottom center;
      transition: transform 0.2s ease;
      z-index: ${i};
    `;

    // Hover: lift card up
    el.addEventListener("pointerenter", () => {
      el.style.transform = `translateX(${offsetX}px) translateY(-${config.hoverLift}px) rotate(${angle * 0.5}deg)`;
      el.style.zIndex = "100";
    });

    el.addEventListener("pointerleave", () => {
      if (!el.classList.contains("selected")) {
        el.style.transform = `translateX(${offsetX}px) rotate(${angle}deg)`;
        el.style.zIndex = String(i);
      }
    });

    container.appendChild(el);
  });
}

function createCardElement(card: CardData, config: CardHandConfig): HTMLElement {
  const el = document.createElement("div");
  el.className = `card ${card.faceUp ? "face-up" : "face-down"}`;
  el.dataset.cardId = card.id;
  el.style.cssText = `
    width: ${config.cardWidth}px;
    height: ${config.cardHeight}px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    cursor: pointer;
    user-select: none;
  `;

  // Card face and back
  el.innerHTML = `
    <div class="card-inner" style="
      width: 100%; height: 100%;
      position: relative;
      transform-style: preserve-3d;
      transition: transform 0.5s;
    ">
      <div class="card-front" style="
        position: absolute; inset: 0;
        backface-visibility: hidden;
        border-radius: 8px;
        background: white;
        display: flex; align-items: center; justify-content: center;
      ">${card.faceUp ? renderCardFace(card) : ""}</div>
      <div class="card-back" style="
        position: absolute; inset: 0;
        backface-visibility: hidden;
        transform: rotateY(180deg);
        border-radius: 8px;
        background: var(--card-back, #2c5282);
      "></div>
    </div>
  `;

  return el;
}
```

### Card Flip Animation

```typescript
function flipCard(cardEl: HTMLElement, newFaceContent: string): Promise<void> {
  const inner = cardEl.querySelector(".card-inner") as HTMLElement;
  const front = cardEl.querySelector(".card-front") as HTMLElement;

  const animation = inner.animate([
    { transform: "rotateY(0deg)" },
    { transform: "rotateY(90deg)" },
  ], { duration: 200, easing: "ease-in", fill: "forwards" });

  return animation.finished.then(() => {
    front.innerHTML = newFaceContent;
    cardEl.classList.replace("face-down", "face-up");

    const flip2 = inner.animate([
      { transform: "rotateY(90deg)" },
      { transform: "rotateY(0deg)" },
    ], { duration: 200, easing: "ease-out", fill: "forwards" });

    return flip2.finished as Promise<void>;
  });
}
```

---

## Animation System

### Animation Queue

Many board game animations must play sequentially (move piece, then capture, then draw card). Build a simple animation queue:

```typescript
type AnimationFn = () => Promise<void>;

class AnimationQueue {
  private queue: AnimationFn[] = [];
  private running = false;

  /** Add animation to end of queue */
  enqueue(fn: AnimationFn): Promise<void> {
    return new Promise((resolve) => {
      this.queue.push(async () => {
        await fn();
        resolve();
      });
      this.flush();
    });
  }

  /** Add multiple animations to play simultaneously */
  parallel(...fns: AnimationFn[]): Promise<void> {
    return this.enqueue(() => Promise.all(fns.map(fn => fn())).then(() => {}));
  }

  /** Add a delay */
  delay(ms: number): Promise<void> {
    return this.enqueue(() => new Promise(r => setTimeout(r, ms)));
  }

  private async flush() {
    if (this.running) return;
    this.running = true;

    while (this.queue.length > 0) {
      const fn = this.queue.shift()!;
      await fn();
    }

    this.running = false;
  }
}

// Usage
const animQueue = new AnimationQueue();

function onMoveReceived(move: MoveData) {
  animQueue.enqueue(() => animatePieceSlide(move.pieceId, move.from, move.to));
  if (move.captured) {
    animQueue.enqueue(() => animateCapture(move.captured));
  }
  if (move.promotion) {
    animQueue.enqueue(() => animatePromotion(move.pieceId, move.promotion));
  }
  // Sound plays alongside animation
  playSound("piece_move");
}
```

### Easing Functions

Standard easing functions for board game animations. No library needed.

```typescript
// Core easing functions
const easing = {
  // Default for piece movement — decelerates to stop
  easeOutCubic: "cubic-bezier(0.33, 1, 0.68, 1)",

  // Smooth start and stop — good for camera pans
  easeInOutCubic: "cubic-bezier(0.65, 0, 0.35, 1)",

  // Slight overshoot — satisfying piece placement
  easeOutBack: "cubic-bezier(0.34, 1.56, 0.64, 1)",

  // Bouncy — dice landing, token dropping
  easeOutBounce: "cubic-bezier(0.22, 1, 0.36, 1)",

  // Snappy — card dealing, quick transitions
  easeOutQuint: "cubic-bezier(0.22, 1, 0.36, 1)",

  // Linear — progress bars, timers
  linear: "linear",
} as const;

// For requestAnimationFrame-based animations, use parametric functions
function easeOutCubic(t: number): number {
  return 1 - Math.pow(1 - t, 3);
}

function easeOutElastic(t: number): number {
  if (t === 0 || t === 1) return t;
  return Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * (2 * Math.PI / 3)) + 1;
}

function easeOutBounce(t: number): number {
  if (t < 1 / 2.75) return 7.5625 * t * t;
  if (t < 2 / 2.75) return 7.5625 * (t -= 1.5 / 2.75) * t + 0.75;
  if (t < 2.5 / 2.75) return 7.5625 * (t -= 2.25 / 2.75) * t + 0.9375;
  return 7.5625 * (t -= 2.625 / 2.75) * t + 0.984375;
}
```

### Animated Piece Movement (Web Animations API)

```typescript
function animatePieceSlide(
  piece: HTMLElement,
  from: GridPosition,
  to: GridPosition,
  duration = 300
): Promise<void> {
  const board = piece.parentElement!;
  const cellWidth = board.clientWidth / COLS;
  const cellHeight = board.clientHeight / ROWS;

  const dx = (to.col - from.col) * cellWidth;
  const dy = (to.row - from.row) * cellHeight;

  const animation = piece.animate([
    { transform: "translate(0, 0)" },
    { transform: `translate(${dx}px, ${dy}px)` },
  ], {
    duration,
    easing: easing.easeOutCubic,
    fill: "forwards",
  });

  return animation.finished.then(() => {
    // Commit to grid position
    piece.style.gridColumn = String(to.col + 1);
    piece.style.gridRow = String(to.row + 1);
    animation.cancel(); // Clear the animation transform
  });
}
```

### Dice Rolling Animation

```typescript
interface DiceConfig {
  faces: number;       // 6 for d6
  size: number;        // pixel size
  rollDuration: number; // ms
}

function animateDiceRoll(
  container: HTMLElement,
  result: number,
  config: DiceConfig = { faces: 6, size: 60, rollDuration: 1200 }
): Promise<number> {
  const dice = document.createElement("div");
  dice.className = "dice";
  dice.style.cssText = `
    width: ${config.size}px;
    height: ${config.size}px;
    font-size: ${config.size * 0.6}px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12%;
    background: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    font-weight: bold;
    user-select: none;
  `;
  container.appendChild(dice);

  // Rapid number cycling phase
  let frame = 0;
  const totalFrames = config.rollDuration / 16; // ~60fps
  const cyclePhase = totalFrames * 0.7; // 70% cycling, 30% settling

  return new Promise((resolve) => {
    function tick() {
      frame++;

      if (frame < cyclePhase) {
        // Cycling random numbers — speed decreases over time
        const speed = 1 - (frame / cyclePhase) * 0.8;
        if (Math.random() < speed) {
          dice.textContent = String(Math.ceil(Math.random() * config.faces));
        }
        // Shake animation
        const shake = (1 - frame / cyclePhase) * 4;
        const rx = (Math.random() - 0.5) * shake;
        const ry = (Math.random() - 0.5) * shake;
        dice.style.transform = `translate(${rx}px, ${ry}px) rotate(${rx * 5}deg)`;
      } else {
        // Show final result
        dice.textContent = String(result);
        dice.style.transform = "translate(0, 0) rotate(0deg)";

        // Settle bounce
        const settleProgress = (frame - cyclePhase) / (totalFrames - cyclePhase);
        const bounce = easeOutBounce(settleProgress);
        const scale = 1 + (1 - bounce) * 0.2;
        dice.style.transform = `scale(${scale})`;
      }

      if (frame < totalFrames) {
        requestAnimationFrame(tick);
      } else {
        resolve(result);
      }
    }

    requestAnimationFrame(tick);
  });
}
```

### Highlight and Selection Effects

```typescript
// Valid move indicators
function showValidMoves(cells: GridPosition[]) {
  cells.forEach(({ row, col }) => {
    const cell = getCell(row, col);
    if (!cell) return;

    const dot = document.createElement("div");
    dot.className = "valid-move-indicator";
    dot.style.cssText = `
      position: absolute;
      width: 30%;
      height: 30%;
      border-radius: 50%;
      background: rgba(0, 0, 0, 0.2);
      pointer-events: none;
      top: 50%; left: 50%;
      transform: translate(-50%, -50%);
    `;

    // Fade in
    dot.animate([
      { opacity: 0, transform: "translate(-50%, -50%) scale(0.5)" },
      { opacity: 1, transform: "translate(-50%, -50%) scale(1)" },
    ], { duration: 150, fill: "forwards" });

    cell.appendChild(dot);
  });
}

// Piece selection glow
function selectPiece(piece: HTMLElement) {
  piece.classList.add("selected");
  piece.animate([
    { filter: "drop-shadow(0 0 0 transparent)" },
    { filter: "drop-shadow(0 0 8px rgba(66, 153, 225, 0.8))" },
  ], { duration: 200, fill: "forwards" });
}
```

---

## Input Handling

### Unified Mouse + Touch Input

```typescript
interface InputHandler {
  onCellClick: (row: number, col: number) => void;
  onPiecePickUp: (pieceId: string) => void;
  onPieceDrop: (pieceId: string, row: number, col: number) => void;
  onPieceDragCancel: (pieceId: string) => void;
}

function setupInput(board: HTMLElement, handler: InputHandler) {
  let dragState: {
    pieceId: string;
    element: HTMLElement;
    ghost: HTMLElement;
    startRow: number;
    startCol: number;
  } | null = null;

  // Use pointer events for unified mouse + touch
  board.addEventListener("pointerdown", (e) => {
    const piece = (e.target as HTMLElement).closest(".piece") as HTMLElement;
    if (piece) {
      e.preventDefault();
      startDrag(piece, e);
      return;
    }

    const cell = (e.target as HTMLElement).closest(".cell") as HTMLElement;
    if (cell) {
      handler.onCellClick(
        Number(cell.dataset.row),
        Number(cell.dataset.col)
      );
    }
  });

  function startDrag(piece: HTMLElement, e: PointerEvent) {
    const pieceId = piece.dataset.pieceId!;
    handler.onPiecePickUp(pieceId);

    // Create drag ghost
    const ghost = piece.cloneNode(true) as HTMLElement;
    ghost.style.cssText += `
      position: fixed;
      pointer-events: none;
      z-index: 1000;
      opacity: 0.8;
      transform: scale(1.1);
      transition: none;
    `;
    document.body.appendChild(ghost);
    updateGhostPosition(ghost, e);

    // Dim original
    piece.style.opacity = "0.3";

    dragState = {
      pieceId,
      element: piece,
      ghost,
      startRow: Number(piece.dataset.row),
      startCol: Number(piece.dataset.col),
    };

    // Capture pointer for reliable drag
    board.setPointerCapture(e.pointerId);
  }

  board.addEventListener("pointermove", (e) => {
    if (!dragState) return;
    updateGhostPosition(dragState.ghost, e);

    // Highlight cell under cursor
    const cell = getCellUnderPoint(e.clientX, e.clientY);
    highlightDropTarget(cell);
  });

  board.addEventListener("pointerup", (e) => {
    if (!dragState) return;

    const cell = getCellUnderPoint(e.clientX, e.clientY);
    dragState.ghost.remove();
    dragState.element.style.opacity = "1";

    if (cell) {
      handler.onPieceDrop(
        dragState.pieceId,
        Number(cell.dataset.row),
        Number(cell.dataset.col)
      );
    } else {
      handler.onPieceDragCancel(dragState.pieceId);
    }

    dragState = null;
    clearDropTargets();
  });

  function updateGhostPosition(ghost: HTMLElement, e: PointerEvent) {
    ghost.style.left = `${e.clientX - ghost.offsetWidth / 2}px`;
    ghost.style.top = `${e.clientY - ghost.offsetHeight / 2}px`;
  }

  function getCellUnderPoint(x: number, y: number): HTMLElement | null {
    // Hide ghost temporarily to get element under it
    if (dragState?.ghost) dragState.ghost.style.display = "none";
    const el = document.elementFromPoint(x, y)?.closest(".cell") as HTMLElement;
    if (dragState?.ghost) dragState.ghost.style.display = "";
    return el;
  }
}
```

### Click-to-Move Alternative

For mobile or accessibility, support click-to-select then click-to-place:

```typescript
class ClickToMoveHandler {
  private selectedPiece: string | null = null;

  handleCellClick(row: number, col: number) {
    if (this.selectedPiece) {
      // Second click — attempt move
      this.onMove(this.selectedPiece, row, col);
      this.deselect();
    }
  }

  handlePieceClick(pieceId: string) {
    if (this.selectedPiece === pieceId) {
      // Click same piece — deselect
      this.deselect();
    } else if (this.selectedPiece) {
      // Click different piece — either capture or re-select
      if (this.isOpponentPiece(pieceId)) {
        this.onCapture(this.selectedPiece, pieceId);
        this.deselect();
      } else {
        this.deselect();
        this.select(pieceId);
      }
    } else {
      // First click — select
      this.select(pieceId);
    }
  }

  private select(pieceId: string) {
    this.selectedPiece = pieceId;
    highlightPiece(pieceId);
    showValidMoves(getValidMovesFor(pieceId));
  }

  private deselect() {
    if (this.selectedPiece) {
      unhighlightPiece(this.selectedPiece);
      clearValidMoves();
    }
    this.selectedPiece = null;
  }
}
```

---

## Responsive Design

### Scaling the Board

The board should fill available space while maintaining aspect ratio. Use CSS containment:

```css
.game-container {
  width: 100vw;
  height: 100vh;
  display: grid;
  grid-template-rows: auto 1fr auto;  /* header, board, controls */
  grid-template-columns: 1fr;
  overflow: hidden;
}

.board-area {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  min-height: 0;  /* Allow shrinking */
}

.game-board {
  /* Board sizes itself to fit container while maintaining aspect ratio */
  width: 100%;
  max-width: min(90vw, calc(90vh - 8rem));
  aspect-ratio: 1;
}

/* Mobile: stack player info below board */
@media (max-width: 768px) {
  .game-container {
    grid-template-rows: auto 1fr auto auto;
  }
  .player-sidebar { display: none; }
  .player-bar-mobile { display: flex; }
}

/* Desktop: player info on sides */
@media (min-width: 769px) {
  .game-container {
    grid-template-columns: 200px 1fr 200px;
  }
  .player-bar-mobile { display: none; }
}
```

### Viewport / Camera for Large Boards

For boards larger than the viewport (large maps, scrollable areas):

```typescript
class BoardCamera {
  private x = 0;
  private y = 0;
  private zoom = 1;
  private minZoom = 0.5;
  private maxZoom = 3;

  constructor(private board: HTMLElement, private viewport: HTMLElement) {
    this.setupPanAndZoom();
  }

  private setupPanAndZoom() {
    let isPanning = false;
    let startX = 0, startY = 0;

    this.viewport.addEventListener("pointerdown", (e) => {
      if (e.target === this.viewport || (e.target as HTMLElement).classList.contains("board-bg")) {
        isPanning = true;
        startX = e.clientX - this.x;
        startY = e.clientY - this.y;
        this.viewport.setPointerCapture(e.pointerId);
      }
    });

    this.viewport.addEventListener("pointermove", (e) => {
      if (!isPanning) return;
      this.x = e.clientX - startX;
      this.y = e.clientY - startY;
      this.applyTransform();
    });

    this.viewport.addEventListener("pointerup", () => {
      isPanning = false;
    });

    // Pinch zoom and scroll zoom
    this.viewport.addEventListener("wheel", (e) => {
      e.preventDefault();
      const delta = e.deltaY > 0 ? 0.9 : 1.1;
      const newZoom = Math.max(this.minZoom, Math.min(this.maxZoom, this.zoom * delta));

      // Zoom toward cursor position
      const rect = this.viewport.getBoundingClientRect();
      const cx = e.clientX - rect.left;
      const cy = e.clientY - rect.top;

      this.x = cx - (cx - this.x) * (newZoom / this.zoom);
      this.y = cy - (cy - this.y) * (newZoom / this.zoom);
      this.zoom = newZoom;
      this.applyTransform();
    }, { passive: false });
  }

  private applyTransform() {
    this.board.style.transform = `translate(${this.x}px, ${this.y}px) scale(${this.zoom})`;
    this.board.style.transformOrigin = "0 0";
  }

  /** Animate camera to focus on a specific position */
  focusOn(worldX: number, worldY: number, targetZoom = 1.5): Promise<void> {
    const rect = this.viewport.getBoundingClientRect();
    const targetX = rect.width / 2 - worldX * targetZoom;
    const targetY = rect.height / 2 - worldY * targetZoom;

    const animation = this.board.animate([
      { transform: `translate(${this.x}px, ${this.y}px) scale(${this.zoom})` },
      { transform: `translate(${targetX}px, ${targetY}px) scale(${targetZoom})` },
    ], { duration: 400, easing: "cubic-bezier(0.22, 1, 0.36, 1)", fill: "forwards" });

    return animation.finished.then(() => {
      this.x = targetX;
      this.y = targetY;
      this.zoom = targetZoom;
      animation.cancel();
      this.applyTransform();
    });
  }
}
```

---

## Canvas 2D Overlay (Effects Layer)

For particle effects, trails, or procedural graphics that don't fit DOM rendering:

```typescript
class EffectsCanvas {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private particles: Particle[] = [];
  private running = false;

  constructor(container: HTMLElement) {
    this.canvas = document.createElement("canvas");
    this.canvas.style.cssText = `
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 100;
    `;
    this.ctx = this.canvas.getContext("2d")!;
    container.appendChild(this.canvas);

    // Match canvas resolution to display size
    const resize = () => {
      const rect = container.getBoundingClientRect();
      this.canvas.width = rect.width * devicePixelRatio;
      this.canvas.height = rect.height * devicePixelRatio;
      this.ctx.scale(devicePixelRatio, devicePixelRatio);
    };
    resize();
    new ResizeObserver(resize).observe(container);
  }

  /** Burst of particles at a position (for captures, wins, etc.) */
  burst(x: number, y: number, color: string, count = 20) {
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 50 + Math.random() * 150;
      this.particles.push({
        x, y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        life: 1,
        decay: 0.02 + Math.random() * 0.02,
        size: 2 + Math.random() * 4,
        color,
      });
    }
    this.startLoop();
  }

  private startLoop() {
    if (this.running) return;
    this.running = true;
    let lastTime = performance.now();

    const tick = (now: number) => {
      const dt = (now - lastTime) / 1000;
      lastTime = now;

      this.ctx.clearRect(0, 0, this.canvas.width / devicePixelRatio, this.canvas.height / devicePixelRatio);

      this.particles = this.particles.filter(p => {
        p.x += p.vx * dt;
        p.y += p.vy * dt;
        p.vy += 200 * dt; // gravity
        p.life -= p.decay;

        if (p.life <= 0) return false;

        this.ctx.globalAlpha = p.life;
        this.ctx.fillStyle = p.color;
        this.ctx.beginPath();
        this.ctx.arc(p.x, p.y, p.size * p.life, 0, Math.PI * 2);
        this.ctx.fill();

        return true;
      });

      this.ctx.globalAlpha = 1;

      if (this.particles.length > 0) {
        requestAnimationFrame(tick);
      } else {
        this.running = false;
      }
    };

    requestAnimationFrame(tick);
  }
}

interface Particle {
  x: number; y: number;
  vx: number; vy: number;
  life: number;
  decay: number;
  size: number;
  color: string;
}
```
