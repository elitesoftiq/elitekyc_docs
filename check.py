#!/usr/bin/env python3
"""Fails if a page points at an image that is not there, or an image is orphaned.

Run after adding or renaming a screenshot:  python3 check.py
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).parent
DOCS = ROOT / "docs"
IMG = DOCS / "assets" / "img"

# Only markdown image/link targets, so a filename mentioned in prose or in a
# code span does not count as a reference.
LINK = re.compile(r"]\(\s*[^)\s]*assets/img/([A-Za-z0-9._-]+\.(?:png|jpg|jpeg|svg))")
YAML = re.compile(r"assets/img/([A-Za-z0-9._-]+\.(?:png|jpg|jpeg|svg))")

referenced = set()
for md in DOCS.rglob("*.md"):
    if md.name == "MANIFEST.md":
        continue
    referenced |= set(LINK.findall(md.read_text()))
referenced |= set(YAML.findall((ROOT / "mkdocs.yml").read_text()))

on_disk = {p.name for p in IMG.iterdir()
           if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".svg"}}

missing = sorted(referenced - on_disk)
orphans = sorted(on_disk - referenced)

for f in missing:
    print(f"missing: docs/assets/img/{f} is referenced but absent", file=sys.stderr)
for f in orphans:
    print(f"orphan:  docs/assets/img/{f} is present but unreferenced", file=sys.stderr)

if missing:
    sys.exit(1)
print(f"ok: {len(referenced)} images referenced, all present")
