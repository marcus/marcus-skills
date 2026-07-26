---
name: braid-cli
description: Use Braid's CLI to operate the daily podcast pipeline, generate images with local models, and inspect distributed inference. Use when checking whether the daily run succeeded, inspecting or recovering a workflow run, running preflight, rebuilding or deploying the site or an episode, opening the Braid dashboard, generating images with local adapters, or inspecting Braid workers, queues, claims, source scores, and dead-letter jobs.
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

## What Braid Is

A daily AI/agentic-coding podcast, built and published from this repo to
`braid.opentangle.com`. A run curates from Marcus's X timeline plus supplement
feeds, summarizes locally on Ollama, narrates with hosted TTS, renders a static
site and an episode video, then uploads feed, site, and artifacts.

`aerie.local` is the production host. Publishing commands are host-guarded and
refuse to run when the hostname does not match `BRAID_PROD_HOST`, so the same
command is safe to read from a laptop and only ships from the right machine.

Adapters sit behind interfaces everywhere — timeline source, summarizer, TTS,
image generation, object store, state — so "which adapter" is usually a resolved
config question, not a code question. Ask `config` rather than reading source.

## Daily Run

Check freshness before assuming anything is wrong:

```bash
./bin/braid health --json                 # last_run_at vs --max-age-hours (default 26)
./bin/braid workflow list --json
./bin/braid workflow status --json        # run + steps + lock state
```

Plan a run without creating workflow rows:

```bash
./bin/braid run --dry-run --json          # prints the resolved DispatchPlan
./bin/braid config ...                    # resolved config, no rows created
```

`run` executes the full curate → narrate → publish sequence. It is the
expensive, outward-facing command: run it when Marcus asks for a run, not to
test a change. `--kind experimental|draft|workflow_test`, `--no-image`, and
`--no-tts` narrow what a deliberate run costs. `-a, --adapter` selects the agent
runtime (`claude` or `codex`).

Before a run that will ship:

```bash
./bin/braid preflight --json
./bin/braid preflight --list              # checks available for the resolved profile
./bin/braid preflight-publish --json      # composite ship-readiness gate
```

A hard failure in `preflight-publish` means the daily run should be blocked —
report it rather than working around it.

## Recovering a Failed Run

Diagnose first; the CLI has a purpose-built proposer:

```bash
./bin/braid run recover                   # inspect last failed/paused run, propose a plan
./bin/braid workflow resolve --json       # run id from podcast slug + episode date
```

Then apply the narrowest fix that works — a single step before a cascade:

```bash
./bin/braid workflow retry-step ...
./bin/braid workflow rerun-from ...       # step plus everything downstream
./bin/braid workflow resume ...
./bin/braid workflow approve-blocked ...  # acknowledges a blocked step, then retries
./bin/braid workflow pause ...            # requested_pause on a running workflow
./bin/braid workflow cancel ...           # stops future scheduling for that run
```

`workflow verify-deploy` re-HEADs every key in a run's deploy manifest and
reports drift — the read-only way to answer "did that actually publish?"

`docs/runbooks/recover-failed-daily-run.md` is the long form. For a published
episode that needs correcting, `docs/runbooks/revise-published-episode.md` and
the `episode` subcommands (`rebuild`, `verify`, `backfill-show-notes`,
`backfill-id3`) repair without re-synthesizing unless asked.

## Dashboard

```bash
./bin/braid dashboard status --json
./bin/braid dashboard ensure --detach
```

Binds `0.0.0.0:4875` by default, so it is reachable from other machines on the
LAN. Reuse a healthy tracked dashboard rather than starting a second one;
`--force-port` can kill an untracked listener and is a deliberate choice, not a
default.

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
  unless the user explicitly asks. `site upload`, `site deploy`, `deploy`,
  `episode reset --apply`, and the `x-follow`/`x-unfollow` commands all reach
  the outside world.
- Do not spawn an untracked background model service. Reuse or deliberately
  start the repository-managed service.
- `docs/reference/cli-write-classification.md` is the inventory of which
  commands write what, and which guard each one carries. Consult it before
  assuming a command is read-only.

## Where to Read Further

| Question | Doc |
|---|---|
| How the pipeline fits together | `README.md`, `docs/diagrams/podcast-generation-pipeline.svg` |
| Current state of the platform | `docs/reference/current-platform-state.md` |
| Which commands write, and their guards | `docs/reference/cli-write-classification.md` |
| Publishing order and invariants | `docs/reference/episode-publishing-sequence.md` |
| Distributed inference setup | `docs/reference/distributed-inference-workers.md` |
| Operational recovery | `docs/runbooks/` |

See [references/proof.md](references/proof.md) for the latest known-good
read-only smoke evidence. Refresh it when the live adapters materially change.
