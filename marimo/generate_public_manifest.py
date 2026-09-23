#!/usr/bin/env python3
"""Regenerate marimo/public/manifest.json to match marimo/public/*.cex.

`marimo export html-wasm` copies `public/` alongside the exported
notebook and serves each file there by its own exact name over plain
HTTP -- there is no directory-listing endpoint, so `reader.py` and
`reader_w_graphviz.py` can't discover which analysis files exist there
the way they can for a real local directory (`Path.glob()`). Instead
they read the explicit filename list this script writes
(`public/manifest.json`).

Run this any time a file is added to, removed from, or renamed in
`public/` -- before the next `marimo export html-wasm` -- to keep the
exported bundle's manifest in sync with what's actually there. (The
notebooks re-sort whatever filenames the manifest lists into citation
order themselves via `analysis_sort_key()`, so this script doesn't need
to -- plain alphabetical order here just keeps the JSON file's own diffs
small and readable.)

Usage: python3 marimo/generate_public_manifest.py
"""

import json
from pathlib import Path

PUBLIC_DIR = Path(__file__).parent / "public"


def main():
    names = sorted(p.name for p in PUBLIC_DIR.glob("*.cex"))
    manifest_path = PUBLIC_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(names, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(names)} filename(s) to {manifest_path}")


if __name__ == "__main__":
    main()
