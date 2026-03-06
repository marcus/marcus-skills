#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = SKILL_DIR / "assets" / "example-system"
TEXT_EXTENSIONS = {".html", ".css", ".js", ".json"}


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "design-system"


def initials(value: str) -> str:
    letters = [part[0] for part in re.split(r"[^A-Za-z0-9]+", value) if part]
    return "".join(letters[:3]).upper() or "DS"


def replace_tokens(root: Path, mapping: dict[str, str]) -> None:
    for path in root.rglob("*"):
        if path.is_dir() or path.suffix not in TEXT_EXTENSIONS:
            continue
        content = path.read_text(encoding="utf-8")
        for key, value in mapping.items():
            content = content.replace(key, value)
        path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy the bundled example design system into a target directory.")
    parser.add_argument("output_dir", help="Directory to create or replace")
    parser.add_argument("--system-name", default="Northstar Design System")
    parser.add_argument("--client-name", default="Asteron")
    parser.add_argument("--tagline", default="Editorial clarity for modern product teams")
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    if output_dir.exists():
        shutil.rmtree(output_dir)

    shutil.copytree(TEMPLATE_DIR, output_dir)

    system_slug = slugify(args.system_name)
    system_initials = initials(args.system_name)
    mapping = {
        "__SYSTEM_NAME__": args.system_name,
        "Northstar Design System": args.system_name,
        "__SYSTEM_SLUG__": system_slug,
        "northstar-design-system": system_slug,
        "__SYSTEM_INITIALS__": system_initials,
        "NDS": system_initials,
        "__CLIENT_NAME__": args.client_name,
        "Asteron": args.client_name,
        "__TAGLINE__": args.tagline,
        "Editorial clarity for modern product teams": args.tagline,
    }
    replace_tokens(output_dir, mapping)
    print(f"Scaffolded {args.system_name} into {output_dir}")


if __name__ == "__main__":
    main()
