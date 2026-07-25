# Braid CLI Evidence

Checked on 2026-07-25 PDT from `/Users/marcus/code/braid`.

## Read-only Smoke Checks

```bash
./bin/braid image list --json
./bin/braid image health --adapter bonsai --json
```

`image list` loaded the CLI and reported the current adapter registry. Gemini,
Codex, Flux Klein, Mflux, Bonsai, Boogu Comfy, and Krea 2 were available.
The Stable Diffusion 3.5 and Ideogram 4 variants were correctly withheld by
their non-commercial license gates.

Bonsai health returned:

```json
{
  "adapter": "bonsai",
  "ok": true,
  "message": "bonsai ready (repoDir=/Users/marcus/.cache/braid/bonsai-image, model=ternary-mlx, steps=4)",
  "latencyMs": 2
}
```

This smoke check does not generate an image or incur hosted API usage. A
previous local generation proof is intentionally not treated as current health;
run a fresh modest generation when an actual output is requested.
