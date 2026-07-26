---
name: braid-cli
description: Use Braid's CLI for local image generation and distributed inference inspection. Use when generating images with local models, checking Braid image adapters, probing local inference health, or inspecting Braid workers, queues, claims, source scores, and dead-letter jobs.
---

# Braid CLI

Use Braid's repository entrypoint. Resolve the checkout without assuming an
agent harness:

```bash
BRAID_REPO="${BRAID_REPO:-$HOME/code/braid}"
test -x "$BRAID_REPO/bin/braid"
cd "$BRAID_REPO"
```

`bin/braid` sources `~/.secrets`, adds the repository's Node executables to
`PATH`, and runs the TypeScript CLI. Never print its environment or secrets.

## Image Generation

List adapters, then health-check the intended adapter:

```bash
./bin/braid image list --json
./bin/braid image health --adapter bonsai --json
```

Generate to an explicit path with parseable output:

```bash
./bin/braid image generate \
  --adapter bonsai \
  --size 512x512 \
  --steps 4 \
  --seed 1234 \
  --output /tmp/braid-image.png \
  --json \
  --prompt "..."
```

Prefer healthy local adapters before hosted fallbacks:

- `bonsai`: MLX-native Bonsai Image 4B; a fast proof is `512x512` with 4
  steps. Dimensions must be multiples of 16 between 256 and 2048.
- `mflux`: local MLX/FLUX.2; use at least 2 steps. The repository default is 4.
- `flux-klein`: Draw Things HTTP; it needs the Draw Things server, usually on
  port 7859.
- `boogu-comfy`, `krea2`, `ideogram4`: Comfy-backed. Reuse the shared server;
  use `image server ensure` only when starting it is in scope.
- `gemini`, `codex`: hosted or subscription-backed fallbacks.
- `null`: placeholder only; never use it as proof of real output.

Do not override non-commercial license gates for production or commercial work.
Use the resolved profile's explicit non-commercial setting only when the work
qualifies and the user accepts that constraint.

## Distributed Inference

Inspect state before changing it:

```bash
./bin/braid inference worker --probe
./bin/braid inference workers
./bin/braid inference jobs --kind source.score.v2
./bin/braid inference claims
./bin/braid inference source-scores
./bin/braid inference dlq-list
```

The primary host owns workflow rows, artifacts, and publishing. Workers pull
jobs, run local models, and upload results; they do not publish. For setup or
debugging, read
`$BRAID_REPO/docs/reference/distributed-inference-workers.md` before changing
configuration.

## Safety

- Use `--json` when downstream work needs the output path, dimensions, bytes,
  or timing.
- Use explicit output paths under `/tmp` or Braid's `state/tmp/image/`.
- Do not deploy, publish, send a newsletter, or upload to social/media services
  unless the user explicitly asks.
- Do not spawn an untracked background model service. Reuse or deliberately
  start the repository-managed service.

See [references/proof.md](references/proof.md) for the latest known-good
read-only smoke evidence. Refresh it when the live adapters materially change.
