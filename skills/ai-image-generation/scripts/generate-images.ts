#!/usr/bin/env npx tsx
/**
 * Generate images from a JSON manifest using OpenAI or Gemini APIs.
 *
 * Usage:
 *   npx tsx generate-images.ts --provider openai              # all pending
 *   npx tsx generate-images.ts --provider gemini              # all pending
 *   npx tsx generate-images.ts --provider openai --id my-block
 *   npx tsx generate-images.ts --provider openai --batch 5
 *   npx tsx generate-images.ts --provider openai --dry-run
 *   npx tsx generate-images.ts --status
 *
 * Expects:
 *   - A manifest.json in the working directory (or pass --manifest path)
 *   - OPENAI_API_KEY or GEMINI_API_KEY environment variable
 *
 * Manifest shape:
 *   {
 *     "meta": { "style_guide": "...", "default_size": "1024x576", "format": "webp" },
 *     "images": [
 *       { "block_id": "x", "prompt": "...", "filename": "x.webp", "status": "pending", ... }
 *     ]
 *   }
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
import { join, dirname } from "path";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ImageEntry {
  module?: string;
  block_id: string;
  prompt: string;
  alt?: string;
  filename: string;
  status: "pending" | "generated" | "approved" | "integrated";
}

interface Manifest {
  meta: {
    style_guide: string;
    default_size: string;
    format: string;
    [key: string]: unknown;
  };
  images: ImageEntry[];
}

type Provider = "openai" | "gemini";

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

function parseArgs() {
  const args = process.argv.slice(2);
  const flags: Record<string, string | boolean> = {};
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === "--status") flags.status = true;
    else if (a === "--dry-run") flags.dryRun = true;
    else if (a === "--provider" && args[i + 1]) flags.provider = args[++i];
    else if (a === "--id" && args[i + 1]) flags.id = args[++i];
    else if (a === "--module" && args[i + 1]) flags.module = args[++i];
    else if (a === "--batch" && args[i + 1]) flags.batch = args[++i];
    else if (a === "--model" && args[i + 1]) flags.model = args[++i];
    else if (a === "--manifest" && args[i + 1]) flags.manifest = args[++i];
    else if (a === "--output-dir" && args[i + 1]) flags.outputDir = args[++i];
  }
  return flags;
}

// ---------------------------------------------------------------------------
// Manifest
// ---------------------------------------------------------------------------

function loadManifest(path: string): Manifest {
  if (!existsSync(path)) {
    console.error(`Manifest not found: ${path}`);
    process.exit(1);
  }
  return JSON.parse(readFileSync(path, "utf-8"));
}

function saveManifest(path: string, manifest: Manifest): void {
  writeFileSync(path, JSON.stringify(manifest, null, 2) + "\n");
}

function showStatus(manifest: Manifest): void {
  const c = { pending: 0, generated: 0, approved: 0, integrated: 0 };
  for (const img of manifest.images) c[img.status]++;
  console.log(`  pending: ${c.pending}  generated: ${c.generated}  approved: ${c.approved}  integrated: ${c.integrated}  total: ${manifest.images.length}`);
}

function selectEntries(manifest: Manifest, flags: Record<string, string | boolean>): ImageEntry[] {
  let entries = manifest.images.filter((i) => i.status === "pending");
  if (flags.id) entries = entries.filter((i) => i.block_id === flags.id);
  if (flags.module) entries = entries.filter((i) => i.module === flags.module);
  if (flags.batch) entries = entries.slice(0, parseInt(flags.batch as string, 10));
  return entries;
}

// ---------------------------------------------------------------------------
// OpenAI
// ---------------------------------------------------------------------------

async function generateOpenAI(prompt: string, model: string, size: string, format: string): Promise<Buffer> {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) throw new Error("OPENAI_API_KEY not set");

  const body: Record<string, unknown> = {
    model,
    prompt,
    n: 1,
    size,
    quality: "medium",
  };

  if (format === "webp" || format === "jpeg" || format === "png") {
    body.output_format = format;
    if (format === "webp") body.output_compression = 85;
  }

  const res = await fetch("https://api.openai.com/v1/images/generations", {
    method: "POST",
    headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) throw new Error(`OpenAI ${res.status}: ${await res.text()}`);
  const json = (await res.json()) as { data: { b64_json: string }[] };
  if (!json.data?.[0]?.b64_json) throw new Error("No image data in response");
  return Buffer.from(json.data[0].b64_json, "base64");
}

// ---------------------------------------------------------------------------
// Gemini
// ---------------------------------------------------------------------------

async function generateGemini(prompt: string, model: string, aspectRatio: string): Promise<Buffer> {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) throw new Error("GEMINI_API_KEY not set");

  const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:predict`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "x-goog-api-key": apiKey, "Content-Type": "application/json" },
    body: JSON.stringify({
      instances: [{ prompt }],
      parameters: { sampleCount: 1, aspectRatio },
    }),
  });

  if (!res.ok) throw new Error(`Gemini ${res.status}: ${await res.text()}`);
  const json = (await res.json()) as {
    generatedImages?: { image: { imageBytes: string } }[];
    predictions?: { bytesBase64Encoded: string }[];
  };

  const b64 = json.generatedImages?.[0]?.image?.imageBytes ?? json.predictions?.[0]?.bytesBase64Encoded;
  if (!b64) throw new Error("No image data in response");
  return Buffer.from(b64, "base64");
}

// ---------------------------------------------------------------------------
// Format conversion
// ---------------------------------------------------------------------------

async function saveImage(buf: Buffer, path: string): Promise<void> {
  if (path.endsWith(".webp")) {
    try {
      const sharp = (await import("sharp")).default;
      writeFileSync(path, await sharp(buf).webp({ quality: 85 }).toBuffer());
      return;
    } catch {
      const png = path.replace(/\.webp$/, ".png");
      writeFileSync(png, buf);
      console.warn(`    sharp not available — saved as PNG: ${png}`);
      return;
    }
  }
  writeFileSync(path, buf);
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function mapOpenAISize(size: string): string {
  const [w, h] = size.split("x").map(Number);
  if (w > h) return "1536x1024";
  if (h > w) return "1024x1536";
  return "1024x1024";
}

function mapGeminiAspect(size: string): string {
  const [w, h] = size.split("x").map(Number);
  if (!w || !h) return "1:1";
  const r = w / h;
  if (r > 1.6) return "16:9";
  if (r > 1.2) return "4:3";
  if (r < 0.65) return "9:16";
  if (r < 0.85) return "3:4";
  return "1:1";
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const flags = parseArgs();
  const manifestPath = (flags.manifest as string) || "manifest.json";
  const manifest = loadManifest(manifestPath);

  if (flags.status) { showStatus(manifest); return; }

  const provider = flags.provider as Provider | undefined;
  if (!provider || !["openai", "gemini"].includes(provider)) {
    console.error("Usage: generate-images.ts --provider <openai|gemini> [options]");
    console.error("\nOptions:");
    console.error("  --manifest <path>    Path to manifest.json (default: ./manifest.json)");
    console.error("  --output-dir <path>  Output directory (default: same dir as manifest)");
    console.error("  --id <block_id>      Single image by block ID");
    console.error("  --module <id>        All pending in one module");
    console.error("  --batch <n>          First n pending images");
    console.error("  --model <name>       Override model (default: gpt-image-1 / imagen-4.0-generate-001)");
    console.error("  --dry-run            Preview without API calls");
    console.error("  --status             Show manifest counts");
    process.exit(1);
  }

  const entries = selectEntries(manifest, flags);
  if (entries.length === 0) { console.log("No pending images match."); showStatus(manifest); return; }

  const outputDir = (flags.outputDir as string) || dirname(manifestPath);
  mkdirSync(outputDir, { recursive: true });

  const model = (flags.model as string) || (provider === "openai" ? "gpt-image-1" : "imagen-4.0-generate-001");
  const format = manifest.meta.format || "webp";

  console.log(`Provider: ${provider}  Model: ${model}  Selected: ${entries.length}\n`);

  if (flags.dryRun) {
    for (const e of entries) console.log(`  [DRY-RUN] ${e.block_id} → ${e.filename}`);
    return;
  }

  let ok = 0, fail = 0;
  for (let i = 0; i < entries.length; i++) {
    const e = entries[i];
    const fullPrompt = `${manifest.meta.style_guide}\n\n${e.prompt}`;
    const outPath = join(outputDir, e.filename);
    console.log(`[${i + 1}/${entries.length}] ${e.block_id}`);

    try {
      const buf = provider === "openai"
        ? await generateOpenAI(fullPrompt, model, mapOpenAISize(manifest.meta.default_size), format)
        : await generateGemini(fullPrompt, model, mapGeminiAspect(manifest.meta.default_size));

      await saveImage(buf, outPath);
      e.status = "generated";
      saveManifest(manifestPath, manifest);
      console.log(`  ✓ ${outPath}`);
      ok++;
    } catch (err) {
      console.error(`  ✗ ${err instanceof Error ? err.message : err}`);
      fail++;
    }

    if (i < entries.length - 1) await sleep(1500);
  }

  console.log(`\nDone: ${ok} generated, ${fail} failed`);
  showStatus(manifest);
}

main().catch((e) => { console.error("Fatal:", e); process.exit(1); });
