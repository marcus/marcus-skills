#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""Generate or edit images with Google's Nano Banana Pro API."""

import argparse
import os
import sys
from io import BytesIO
from pathlib import Path


DEFAULT_MODEL = "gemini-3-pro-image-preview"


def get_api_key(provided_key: str | None) -> str | None:
    """Return an explicit API key or the configured environment key."""
    return provided_key or os.environ.get("GEMINI_API_KEY")


def import_dependencies():
    """Import runtime dependencies after argument and key validation."""
    from google import genai
    from google.genai import types
    from PIL import Image

    return genai, types, Image


def save_png(image, output_path: Path, image_class) -> None:
    """Save an API image payload as an RGB PNG."""
    if image.mode == "RGBA":
        rgb_image = image_class.new("RGB", image.size, (255, 255, 255))
        rgb_image.paste(image, mask=image.getchannel("A"))
        rgb_image.save(output_path, "PNG")
    elif image.mode == "RGB":
        image.save(output_path, "PNG")
    else:
        image.convert("RGB").save(output_path, "PNG")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate or edit images with Nano Banana Pro"
    )
    parser.add_argument("--prompt", "-p", help="Image description or edit prompt")
    parser.add_argument("--filename", "-f", help="Output PNG path")
    parser.add_argument(
        "--input-image", "-i", help="Optional source image for an edit"
    )
    parser.add_argument(
        "--resolution",
        "-r",
        choices=["1K", "2K", "4K"],
        help="Output resolution (default: 1K for generation; inferred for edits)",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Gemini image model (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--api-key",
        "-k",
        help="API key override; GEMINI_API_KEY is safer and preferred",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check dependencies and API-key configuration without making an API call",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    api_key = get_api_key(args.api_key)
    if not api_key:
        print(
            "Error: No API key provided. Set GEMINI_API_KEY or pass --api-key.",
            file=sys.stderr,
        )
        return 1

    try:
        genai, types, image_class = import_dependencies()
    except ImportError as exc:
        print(f"Error: Missing runtime dependency: {exc}", file=sys.stderr)
        return 1

    if args.check:
        print("Nano Banana Pro preflight OK: dependencies and API key are configured.")
        return 0

    if not args.prompt:
        parser.error("--prompt is required unless --check is used")
    if not args.filename:
        parser.error("--filename is required unless --check is used")

    output_path = Path(args.filename).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    input_image = None
    output_resolution = args.resolution or "1K"
    if args.input_image:
        input_path = Path(args.input_image).expanduser()
        try:
            input_image = image_class.open(input_path)
            input_image.load()
        except Exception as exc:
            print(f"Error loading input image: {exc}", file=sys.stderr)
            return 1

        if args.resolution is None:
            max_dimension = max(input_image.size)
            if max_dimension >= 3000:
                output_resolution = "4K"
            elif max_dimension >= 1500:
                output_resolution = "2K"

    contents = [input_image, args.prompt] if input_image else args.prompt
    action = "Editing" if input_image else "Generating"
    print(f"{action} image at {output_resolution} with {args.model}...")

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=args.model,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(image_size=output_resolution),
            ),
        )

        image_saved = False
        for part in response.parts or []:
            if part.text is not None:
                print(f"Model response: {part.text}")
            elif part.inline_data is not None:
                image_data = part.inline_data.data
                if isinstance(image_data, str):
                    import base64

                    image_data = base64.b64decode(image_data)
                image = image_class.open(BytesIO(image_data))
                save_png(image, output_path, image_class)
                image_saved = True

        if not image_saved:
            print("Error: No image was generated in the response.", file=sys.stderr)
            return 1
    except Exception as exc:
        print(f"Error generating image: {exc}", file=sys.stderr)
        return 1

    print(f"Image saved: {output_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
