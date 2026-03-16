---
name: remotion
description: Build programmatic videos with Remotion 4. Covers compositions, components, audio sync, rendering, and deployment. Use when creating video content with React/TypeScript.
---

# Remotion 4 Quick Reference

Build videos programmatically with React and TypeScript. Remotion treats video as a function of frames -- each frame is a React component render.

## Current Version

| Package | Version | Notes |
|---------|---------|-------|
| remotion | ~4.0.x | Remotion 4 is current stable. v5 migration guide exists but is not yet released. |
| @remotion/cli | ~4.0.x | CLI for studio, rendering, and Lambda |
| @remotion/renderer | ~4.0.x | Programmatic server-side rendering |
| @remotion/transitions | ~4.0.x | TransitionSeries and presentations (v4.0.53+) |
| @remotion/media-utils | ~4.0.x | Audio data, visualization, metadata |
| @remotion/media | ~4.0.x | WebCodecs-based Video component |
| @remotion/lambda | ~4.0.x | AWS Lambda serverless rendering |

## Project Setup

```bash
# Create a new project
npx create-video@latest my-video
cd my-video
npm start         # Opens Remotion Studio
```

### Project Structure

```
my-video/
  public/              # Static assets (images, audio, video files)
    music.mp3
    logo.png
  src/
    index.ts           # Entry file -- registers Root component
    Root.tsx            # Composition registry
    MyComposition.tsx   # Video component(s)
  remotion.config.ts   # CLI configuration (studio, render)
  package.json
  tsconfig.json
```

### Entry File (src/index.ts)

```tsx
import {registerRoot} from 'remotion';
import {Root} from './Root';
registerRoot(Root);
```

### Root File (src/Root.tsx)

```tsx
import {Composition} from 'remotion';
import {MyVideo} from './MyVideo';

export const Root: React.FC = () => {
  return (
    <>
      <Composition
        id="MyVideo"
        component={MyVideo}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{title: 'Hello World'}}
      />
    </>
  );
};
```

Every composition has four required properties: `width`, `height`, `durationInFrames`, and `fps`. The first frame is `0`, the last frame is `durationInFrames - 1`.

---

## Core Hooks

### useCurrentFrame()

Returns the current frame number. This is the primary driver for all animation.

```tsx
import {useCurrentFrame} from 'remotion';

export const MyComp: React.FC = () => {
  const frame = useCurrentFrame();
  return <div>Frame {frame}</div>;
};
```

### useVideoConfig()

Returns composition metadata: `fps`, `durationInFrames`, `width`, `height`.

```tsx
import {useVideoConfig} from 'remotion';

export const MyComp: React.FC = () => {
  const {fps, durationInFrames, width, height} = useVideoConfig();
  return <div>{width}x{height} at {fps}fps</div>;
};
```

---

## Animation

### interpolate()

Maps an input range to an output range. The workhorse for most animations.

```tsx
import {interpolate, useCurrentFrame} from 'remotion';

export const FadeIn: React.FC = () => {
  const frame = useCurrentFrame();

  const opacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: 'clamp',
  });

  return <div style={{opacity}}>Hello</div>;
};
```

**Parameters**: `interpolate(input, inputRange, outputRange, options?)`

| Option | Values | Default | Purpose |
|--------|--------|---------|---------|
| `extrapolateLeft` | `'extend'` `'clamp'` `'wrap'` `'identity'` | `'extend'` | Behavior below input range |
| `extrapolateRight` | `'extend'` `'clamp'` `'wrap'` `'identity'` | `'extend'` | Behavior above input range |
| `easing` | `(t: number) => number` | linear | Easing function |

Multi-point interpolation for complex animations:

```tsx
// Fade in, hold, fade out
const opacity = interpolate(
  frame,
  [0, 20, durationInFrames - 20, durationInFrames],
  [0, 1, 1, 0],
  {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
);
```

### spring()

Physics-based animation. Animates from 0 to 1 by default with natural overshoot.

```tsx
import {spring, useCurrentFrame, useVideoConfig} from 'remotion';

export const ScaleIn: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const scale = spring({
    frame,
    fps,
    config: {damping: 200},
  });

  return <div style={{transform: `scale(${scale})`}}>Pop!</div>;
};
```

**Parameters**:

| Param | Default | Purpose |
|-------|---------|---------|
| `frame` | required | Current frame (from `useCurrentFrame()`) |
| `fps` | required | Frame rate (from `useVideoConfig()`) |
| `from` | `0` | Start value |
| `to` | `1` | End value |
| `config.mass` | `1` | Higher = slower |
| `config.stiffness` | `100` | Higher = bouncier |
| `config.damping` | `10` | Higher = less bounce. Use `200` for no overshoot. |
| `config.overshootClamping` | `false` | Clamp at target value |
| `durationInFrames` | undefined | Stretch to exact duration |
| `delay` | `0` | Frames to wait before starting |
| `reverse` | `false` | Reverse the animation |

### measureSpring()

Calculate how many frames a spring animation takes to settle:

```tsx
import {measureSpring} from 'remotion';

const duration = measureSpring({
  fps: 30,
  config: {damping: 200},
}); // e.g., 23 frames
```

### Easing

Built-in easing functions for use with `interpolate()`:

```tsx
import {Easing, interpolate} from 'remotion';

const value = interpolate(frame, [0, 60], [0, 1], {
  easing: Easing.bezier(0.25, 0.1, 0.25, 1),
  extrapolateLeft: 'clamp',
  extrapolateRight: 'clamp',
});
```

Available easings: `linear`, `ease`, `quad`, `cubic`, `poly(n)`, `sin`, `circle`, `exp`, `elastic`, `back`, `bounce`, `bezier(x1, y1, x2, y2)`.

Modifiers: `Easing.in(fn)`, `Easing.out(fn)`, `Easing.inOut(fn)`.

Visualize at [easings.net](https://easings.net/).

---

## Timing and Sequencing

### Sequence

Time-shifts children. Children's `useCurrentFrame()` resets to 0 at the sequence start.

```tsx
import {Sequence, AbsoluteFill} from 'remotion';

export const MyVideo: React.FC = () => {
  return (
    <AbsoluteFill>
      <Sequence from={0} durationInFrames={60}>
        <Title />
      </Sequence>
      <Sequence from={60} durationInFrames={90}>
        <Content />
      </Sequence>
      <Sequence from={150}>
        <Outro />
      </Sequence>
    </AbsoluteFill>
  );
};
```

**Key props**:

| Prop | Default | Purpose |
|------|---------|---------|
| `from` | `0` | Frame to start showing |
| `durationInFrames` | `Infinity` | How long to show |
| `layout` | `'absolute-fill'` | `'none'` to skip wrapper div |
| `name` | undefined | Label in Studio timeline |
| `premountFor` | undefined | Premount N frames before `from` |
| `style` | undefined | CSS on wrapper (not with `layout="none"`) |

Nesting sequences accumulates offsets: inner `from={60}` inside outer `from={30}` = starts at frame 90.

### Series

Sequential playback without manual `from` calculations:

```tsx
import {Series} from 'remotion';

export const MyVideo: React.FC = () => {
  return (
    <Series>
      <Series.Sequence durationInFrames={60}>
        <Intro />
      </Series.Sequence>
      <Series.Sequence durationInFrames={90}>
        <Main />
      </Series.Sequence>
      <Series.Sequence durationInFrames={60}>
        <Outro />
      </Series.Sequence>
    </Series>
  );
};
```

`offset` prop shifts timing: positive delays, negative overlaps with previous sequence.

### Loop

Repeat content:

```tsx
import {Loop} from 'remotion';

<Loop durationInFrames={50} times={3}>
  <PulsingDot />
</Loop>
```

`Loop.useLoop()` returns `{durationInFrames, iteration}` inside a loop (v4.0.142+).

### AbsoluteFill

Full-screen absolutely positioned container for layering:

```tsx
import {AbsoluteFill} from 'remotion';

<AbsoluteFill>
  <AbsoluteFill><Background /></AbsoluteFill>
  <AbsoluteFill><Foreground /></AbsoluteFill>
</AbsoluteFill>
```

Renders as a div with `position: absolute; top: 0; left: 0; right: 0; bottom: 0; width: 100%; height: 100%; display: flex; flex-direction: column`.

---

## Transitions

The `@remotion/transitions` package (v4.0.53+) provides `TransitionSeries` for animated transitions between scenes.

```bash
npm install @remotion/transitions
```

### TransitionSeries

```tsx
import {linearTiming, TransitionSeries} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {slide} from '@remotion/transitions/slide';
import {wipe} from '@remotion/transitions/wipe';

export const MyVideo: React.FC = () => {
  return (
    <TransitionSeries>
      <TransitionSeries.Sequence durationInFrames={60}>
        <SceneA />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({durationInFrames: 30})}
      />
      <TransitionSeries.Sequence durationInFrames={90}>
        <SceneB />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition
        presentation={slide({direction: 'from-right'})}
        timing={linearTiming({durationInFrames: 20})}
      />
      <TransitionSeries.Sequence durationInFrames={60}>
        <SceneC />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};
```

**Duration math**: During a transition both scenes render simultaneously. Total duration = sum of sequences minus sum of transitions. E.g. `60 + 90 + 60 - 30 - 20 = 160` frames.

### Presentations

| Presentation | Import | Options |
|-------------|--------|---------|
| `fade()` | `@remotion/transitions/fade` | `shouldFadeOutExitingScene` (default false) |
| `slide()` | `@remotion/transitions/slide` | `direction`: `from-left`, `from-right`, `from-top`, `from-bottom` |
| `wipe()` | `@remotion/transitions/wipe` | `direction`: 8 directions including diagonals |

### Timing Functions

| Function | Import | Notes |
|----------|--------|-------|
| `linearTiming({durationInFrames})` | `@remotion/transitions` | Constant speed |
| `springTiming({config, durationInFrames})` | `@remotion/transitions` | Spring physics. Use `durationRestThreshold: 0.001` for smooth cutoff. |

### TransitionSeries.Overlay (v4.0.415+)

Renders content at a cut point without affecting timeline duration:

```tsx
<TransitionSeries.Overlay durationInFrames={20} offset={-10}>
  <FlashEffect />
</TransitionSeries.Overlay>
```

---

## Media Components

### Static Files

Place assets in `public/` and reference with `staticFile()`:

```tsx
import {staticFile} from 'remotion';

const src = staticFile('my-image.png'); // resolves to /my-image.png
```

`staticFile()` auto-encodes URI-unsafe characters. Do not pre-encode filenames.

### Img

Enhanced `<img>` that delays rendering until loaded:

```tsx
import {Img, staticFile} from 'remotion';

<Img src={staticFile('photo.png')} style={{width: '100%'}} />
```

From v4.0.0, failed images trigger `cancelRender()` unless handled via `onError`. Max resolution: 539 megapixels.

### OffthreadVideo (Recommended for Rendering)

Extracts frames via FFmpeg outside the browser. Frame-perfect accuracy, widest codec support.

```tsx
import {OffthreadVideo, staticFile} from 'remotion';

<OffthreadVideo
  src={staticFile('screen-recording.mp4')}
  volume={0.8}
  playbackRate={1.5}
  style={{width: '100%'}}
/>
```

Key props: `src`, `volume`, `playbackRate`, `muted`, `transparent`, `trimBefore`, `trimAfter`, `toneFrequency`, `toneMapped`.

Not supported in client-side rendering. Cannot loop (wrap in `<Loop>` instead).

### Html5Video

Browser-native `<video>`. Supports looping. Less frame-accurate than OffthreadVideo.

```tsx
import {Html5Video, staticFile} from 'remotion';

<Html5Video src={staticFile('clip.mp4')} loop muted />
```

### Video (from @remotion/media)

WebCodecs-based. Fastest rendering. Supports partial downloads and looping. Experimental. Falls back to OffthreadVideo for unsupported formats.

```tsx
import {Video} from '@remotion/media';

<Video src={staticFile('clip.mp4')} />
```

### Video Tag Comparison

| Component | Speed | Frame Accuracy | Looping | Client Rendering |
|-----------|-------|---------------|---------|-----------------|
| `OffthreadVideo` | Fast | Frame-perfect | No (use Loop) | No |
| `Html5Video` | Medium | Not guaranteed | Yes | No |
| `Video` (@remotion/media) | Fastest | Good | Yes | Yes |

**Recommendation**: Use `OffthreadVideo` for production rendering. Use `Video` from `@remotion/media` when you need client-side rendering or maximum speed.

---

## Audio

### Html5Audio (previously Audio)

```tsx
import {Html5Audio, staticFile} from 'remotion';

<Html5Audio src={staticFile('narration.mp3')} />
```

**Volume control**:

```tsx
// Static
<Html5Audio src={staticFile('bg.mp3')} volume={0.3} />

// Dynamic fade-in over 30 frames
<Html5Audio
  src={staticFile('voice.mp3')}
  volume={(f) =>
    interpolate(f, [0, 30], [0, 1], {extrapolateLeft: 'clamp'})
  }
/>
```

**Trimming** (in frames):

```tsx
<Html5Audio src={staticFile('audio.mp3')} trimBefore={60} trimAfter={120} />
```

Other props: `playbackRate`, `muted`, `loop`, `toneFrequency`.

### Audio Visualization

```tsx
import {useAudioData, visualizeAudio} from '@remotion/media-utils';
import {Html5Audio, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

export const AudioBars: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const audioData = useAudioData(staticFile('music.mp3'));

  if (!audioData) return null;

  const visualization = visualizeAudio({
    fps,
    frame,
    audioData,
    numberOfSamples: 32, // must be power of 2
    smoothing: true,
  });

  return (
    <div style={{display: 'flex', alignItems: 'flex-end', height: 200}}>
      {visualization.map((v, i) => (
        <div
          key={i}
          style={{
            width: 10,
            height: 200 * v,
            backgroundColor: 'white',
            marginRight: 2,
          }}
        />
      ))}
    </div>
  );
};
```

`visualizeAudio()` returns an array of 0-1 values. Lower indices = bass, higher = treble. Use `optimizeFor: 'speed'` for Lambda rendering.

---

## Data-Driven Videos

### Zod Schemas for Props

Define props with Zod for type safety and visual editing in Remotion Studio:

```bash
npx remotion add @remotion/zod-types zod
```

```tsx
import {z} from 'zod';
import {Composition} from 'remotion';

const videoSchema = z.object({
  title: z.string(),
  subtitle: z.string(),
  backgroundColor: z.string(),
});

type VideoProps = z.infer<typeof videoSchema>;

const MyVideo: React.FC<VideoProps> = ({title, subtitle, backgroundColor}) => {
  return <div style={{backgroundColor}}><h1>{title}</h1><p>{subtitle}</p></div>;
};

// In Root.tsx
<Composition
  id="MyVideo"
  component={MyVideo}
  schema={videoSchema}
  defaultProps={{title: 'Hello', subtitle: 'World', backgroundColor: '#000'}}
  durationInFrames={150}
  fps={30}
  width={1920}
  height={1080}
/>
```

The `@remotion/zod-types` package adds special types: `zColor()`, `zTextarea()`, `zMatrix()`.

### calculateMetadata()

Dynamically compute composition metadata based on props or fetched data:

```tsx
import {CalculateMetadataFunction, Composition} from 'remotion';

const calculateMetadata: CalculateMetadataFunction<MyProps> = async ({
  props,
  defaultProps,
  abortSignal,
}) => {
  const data = await fetch('https://api.example.com/video-data', {
    signal: abortSignal,
  }).then((r) => r.json());

  return {
    props: {...props, data},
    durationInFrames: data.scenes.length * 150,
    fps: 30,
    width: 1920,
    height: 1080,
  };
};

// In Root.tsx
<Composition
  id="DataVideo"
  component={DataVideo}
  calculateMetadata={calculateMetadata}
  defaultProps={{data: null}}
  durationInFrames={300}
  fps={30}
  width={1920}
  height={1080}
/>
```

Runs once before rendering. Can set `durationInFrames`, `width`, `height`, `fps`, `props`, `defaultCodec`, and `defaultOutName`.

---

## Async Data and Loading

### delayRender / continueRender

Pause rendering until async data loads:

```tsx
import {useCallback, useEffect, useState} from 'react';
import {continueRender, delayRender} from 'remotion';

export const AsyncComp: React.FC = () => {
  const [handle] = useState(() => delayRender('Loading data...'));
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch('https://api.example.com/data')
      .then((r) => r.json())
      .then((d) => {
        setData(d);
        continueRender(handle);
      })
      .catch((err) => cancelRender(err));
  }, [handle]);

  if (!data) return null;

  return <div>{data.title}</div>;
};
```

Default timeout: 30 seconds. Override with `delayRender('label', {timeoutInMilliseconds: 10000})`.

### prefetch()

Pre-load media assets for the Player:

```tsx
import {prefetch} from 'remotion';

const {free, waitUntilDone} = prefetch('https://example.com/video.mp4', {
  method: 'blob-url',
});
await waitUntilDone();
// Asset is now cached. Call free() when done.
```

---

## Deterministic Randomness

Never use `Math.random()` -- it produces different values across render threads.

```tsx
import {random} from 'remotion';

const value = random('my-seed');       // always 0.073...
const x = random(`particle-x-${i}`);  // deterministic per index
const truly = random(null);            // true randomness (opt-in)
```

---

## Rendering

### CLI Rendering

```bash
# Render a video
npx remotion render MyVideo output.mp4

# Render with options
npx remotion render MyVideo output.mp4 \
  --codec=h264 \
  --crf=18 \
  --concurrency=4

# Render a still frame
npx remotion still MyVideo frame.png --frame=30

# Render as image sequence
npx remotion render MyVideo --sequence

# Render audio only
npx remotion render MyVideo output.mp3 --codec=mp3

# Render a GIF
npx remotion render MyVideo output.gif

# Pass props
npx remotion render MyVideo output.mp4 --props='{"title":"Custom"}'

# Benchmark concurrency
npx remotion benchmark
```

**Key CLI flags**:

| Flag | Purpose |
|------|---------|
| `--codec` | h264, h265, vp8, vp9, prores, mp3, aac, wav, h264-mkv |
| `--crf` | Quality (lower = better). H.264 default ~18 |
| `--concurrency` | Parallel frame rendering. Find optimal with `benchmark` |
| `--scale` | Output scale factor (e.g., 0.5 for half resolution) |
| `--jpeg-quality` | JPEG quality 0-100 |
| `--frames` | Render specific range (e.g., `0-59`) |
| `--muted` | Skip audio |
| `--hardware-acceleration` | GPU acceleration (v4.0.228+) |
| `--log` | Verbosity: error, warn, info, verbose |

### Programmatic Rendering (SSR)

```tsx
import {bundle} from '@remotion/bundler';
import {renderMedia, selectComposition} from '@remotion/renderer';

const bundled = await bundle({entryPoint: './src/index.ts'});

const composition = await selectComposition({
  serveUrl: bundled,
  id: 'MyVideo',
  inputProps: {},
});

await renderMedia({
  composition,
  serveUrl: bundled,
  codec: 'h264',
  outputLocation: 'output.mp4',
});
```

### Lambda Rendering

Serverless rendering on AWS. Fastest and most scalable option.

```bash
# Setup
npx remotion lambda policies role    # Create AWS role
npx remotion lambda functions deploy  # Deploy Lambda function
npx remotion lambda sites create src/index.ts  # Deploy site to S3

# Render
npx remotion lambda render <site-url> MyVideo
```

Programmatic:

```tsx
import {renderMediaOnLambda, getRenderProgress} from '@remotion/lambda';

const {renderId, bucketName} = await renderMediaOnLambda({
  region: 'us-east-1',
  functionName: 'remotion-render',
  composition: 'MyVideo',
  serveUrl: siteUrl,
  codec: 'h264',
  inputProps: {},
});
```

Constraints: videos under ~80 min at 1080p, ~5GB max output, 1000 concurrent Lambdas per region (increasable).

### Still Frames

```bash
npx remotion still MyVideo poster.png --frame=0
```

```tsx
import {renderStill} from '@remotion/renderer';

await renderStill({
  composition,
  serveUrl: bundled,
  output: 'poster.png',
  frame: 0,
});
```

---

## Remotion Studio

The development environment for previewing and editing compositions.

```bash
npx remotion studio
```

Features:
- Live preview of all compositions
- Visual props editor (requires Zod schema)
- Render button with progress tracking and queuing
- Timeline visualization of sequences
- Can be deployed for team access

---

## Player Component

Embed Remotion videos in any React app:

```bash
npm install @remotion/player
```

```tsx
import {Player} from '@remotion/player';
import {MyVideo} from './MyVideo';

export const App = () => {
  return (
    <Player
      component={MyVideo}
      durationInFrames={150}
      fps={30}
      compositionWidth={1920}
      compositionHeight={1080}
      style={{width: 800}}
      controls
      inputProps={{title: 'Hello'}}
    />
  );
};
```

**Player best practices**:
- Memoize `inputProps` with `useMemo()` to prevent unnecessary re-renders
- Keep Player isolated from frequently updating state (e.g., current time)
- Pass browser events to `.play()` and `.toggle()` to satisfy autoplay restrictions

---

## Performance

### Rendering Speed

- Use `npx remotion benchmark` to find optimal `--concurrency` value
- JPEG is faster than PNG (PNG required for transparency)
- VP8/VP9 encode slower due to compression
- Lower resolution with `--scale` when quality isn't critical
- Use `--log=verbose` to identify slowest frames
- Prefer `Video` from `@remotion/media` for fastest rendering

### Component Performance

- Use `useMemo()` and `useCallback()` to cache expensive computations
- Memoize components with `React.memo()` when props don't change every frame
- Minimize external data fetching; cache in localStorage when possible
- Avoid GPU effects (blur, drop-shadow, WebGL) in cloud rendering -- pre-render to images instead

### Bundle Optimization

- Keep bundles small for faster Lambda cold starts
- Avoid large dependencies in video components
- Use dynamic imports for heavy libraries

---

## Common Patterns

### Narration Sync

Place audio and visuals in the same timeline using Sequences:

```tsx
export const NarratedVideo: React.FC = () => {
  return (
    <AbsoluteFill>
      {/* Background music at low volume */}
      <Html5Audio src={staticFile('bg-music.mp3')} volume={0.15} />

      {/* Narration audio */}
      <Sequence from={0}>
        <Html5Audio src={staticFile('narration.mp3')} />
      </Sequence>

      {/* Visuals synced to narration timestamps */}
      <Sequence from={0} durationInFrames={90}>
        <TitleCard text="Welcome" />
      </Sequence>
      <Sequence from={90} durationInFrames={120}>
        <ScreenRecording src={staticFile('demo.mp4')} />
      </Sequence>
      <Sequence from={210} durationInFrames={60}>
        <CallToAction />
      </Sequence>
    </AbsoluteFill>
  );
};
```

### Screen Recording with Overlays

```tsx
export const DemoOverlay: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const cursorScale = spring({frame: frame - 30, fps, config: {damping: 200}});

  return (
    <AbsoluteFill>
      <OffthreadVideo src={staticFile('screen-recording.mp4')} />
      <AbsoluteFill>
        {/* Animated callout */}
        <Sequence from={30} durationInFrames={90}>
          <div
            style={{
              position: 'absolute',
              top: 200,
              left: 400,
              transform: `scale(${cursorScale})`,
              background: 'rgba(255,0,0,0.3)',
              borderRadius: 8,
              padding: 20,
              border: '2px solid red',
            }}
          >
            <p style={{color: 'white', fontSize: 24}}>Click here!</p>
          </div>
        </Sequence>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
```

### Text Animation

```tsx
export const AnimatedTitle: React.FC<{text: string}> = ({text}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
      <h1 style={{fontSize: 80, display: 'flex'}}>
        {text.split('').map((char, i) => {
          const delay = i * 3;
          const y = interpolate(frame - delay, [0, 10], [40, 0], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          const opacity = interpolate(frame - delay, [0, 10], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          return (
            <span key={i} style={{transform: `translateY(${y}px)`, opacity}}>
              {char === ' ' ? '\u00A0' : char}
            </span>
          );
        })}
      </h1>
    </AbsoluteFill>
  );
};
```

### Progress Bar

```tsx
export const ProgressBar: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();

  const progress = interpolate(frame, [0, durationInFrames], [0, 100], {
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        height: 4,
        width: `${progress}%`,
        backgroundColor: '#3b82f6',
      }}
    />
  );
};
```

### Fade-to-Black Transition

```tsx
export const FadeToBlack: React.FC<{children: React.ReactNode}> = ({children}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();

  const fadeOut = interpolate(
    frame,
    [durationInFrames - 15, durationInFrames],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );

  return (
    <AbsoluteFill>
      {children}
      <AbsoluteFill style={{backgroundColor: `rgba(0,0,0,${fadeOut})`}} />
    </AbsoluteFill>
  );
};
```

---

## TypeScript Configuration

Remotion projects use TypeScript by default. Key tsconfig settings:

```json
{
  "compilerOptions": {
    "target": "ES2018",
    "module": "commonjs",
    "jsx": "react-jsx",
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "lib": ["es2018", "dom"]
  }
}
```

Props must use `type` (not `interface`) when passing to compositions.

---

## Configuration File

`remotion.config.ts` at project root configures CLI behavior:

```tsx
import {Config} from '@remotion/cli/config';

Config.setOverwriteOutput(true);
Config.setVideoImageFormat('jpeg');
Config.setConcurrency(4);
```

Flat API in v4 -- no more nested namespaces like `Config.Bundling.x()`.

---

## Key v4 Changes from v3

- FFmpeg bundled (no external install needed) via Rust binary
- Studio replaces Preview (visual props editor, render button)
- `Config` import moved to `@remotion/cli/config`, flat API
- `quality` renamed to `jpegQuality`
- `parallelism` renamed to `concurrency`
- `<Audio>` renamed to `<Html5Audio>`
- `<Video>` (from remotion) renamed to `<Html5Video>`
- New `<Video>` from `@remotion/media` (WebCodecs-based)
- Props must be `type`, not `interface`
- `defaultProps` required for components with props
- `imageFormat` split into `setVideoImageFormat()` / `setStillImageFormat()`
- New packages: `@remotion/rive`, `@remotion/shapes`, `@remotion/tailwind`
- New `calculateMetadata()` API for data-driven compositions
- `selectComposition()` API for picking compositions programmatically
- Minimum Node 16.0.0

---

## Sources

- [Remotion Documentation](https://www.remotion.dev/docs/)
- [Remotion 4.0 Blog Post](https://www.remotion.dev/blog/4-0)
- [Remotion LLM System Prompt](https://www.remotion.dev/llms.txt)
- [Remotion GitHub](https://github.com/remotion-dev/remotion)
