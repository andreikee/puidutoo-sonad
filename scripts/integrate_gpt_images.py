#!/usr/bin/env python3
"""Integrate GPT-generated images into the working image set (one pass, idempotent).

- Copy assets/images-gpt/<id>.jpg -> assets/images/<id>.jpg (overwriting old Wikimedia photos)
- Remove stale .png diagrams (now superseded by GPT .jpg versions)
- Regenerate data/images.json: file=<id>.jpg, license="AI-generated", generated=true
"""
import json, os, shutil, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GPT_DIR = os.path.join(BASE, "assets", "images-gpt")
IMG_DIR = os.path.join(BASE, "assets", "images")
DATA = os.path.join(BASE, "data")

terms = json.load(open(os.path.join(DATA, "terms.json"), encoding="utf-8"))

# 1) copy GPT jpgs over
copied = 0
for t in terms["terms"]:
    fname = t["image_file"]  # e.g. "puit.jpg"
    src = os.path.join(GPT_DIR, fname)
    if not os.path.exists(src):
        print("MISSING", fname, file=sys.stderr)
        sys.exit(1)
    shutil.copy2(src, os.path.join(IMG_DIR, fname))
    copied += 1

# 2) remove stale .png diagrams (and any file not matching a term's image_file)
keep = {t["image_file"] for t in terms["terms"]}
removed = []
for f in os.listdir(IMG_DIR):
    if f.endswith(".jpg") and f not in keep:
        os.remove(os.path.join(IMG_DIR, f)); removed.append(f)
    if f.endswith(".png"):
        os.remove(os.path.join(IMG_DIR, f)); removed.append(f)

# 3) rebuild images.json
manifest = {}
for t in terms["terms"]:
    manifest[t["id"]] = {
        "file": t["image_file"],
        "license": "AI-generated (project-owned)",
        "artist": "Generated with AI for this trainer",
        "title": t["et"],
        "page_url": "",
        "generated": True,
    }
json.dump(manifest, open(os.path.join(DATA, "images.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print(f"copied={copied} removed_stale={removed} manifest={len(manifest)}")
