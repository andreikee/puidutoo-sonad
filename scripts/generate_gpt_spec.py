#!/usr/bin/env python3
"""Generate data/gpt_image_prompts.json — a minimal spec file to hand to GPT for image generation.

Each entry: image file name, 1-2 sentence description (child-level), short prompt,
fixed size and style.
"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
terms = json.load(open(os.path.join(BASE, "data", "terms.json"), encoding="utf-8"))

spec = {
    "purpose": "Generate a set of child-friendly educational images for a woodwork vocabulary trainer (age 11, 5th grade).",
    "output": {
        "format": terms.get("image_format", "jpg"),
        "size": terms.get("image_size", "512x512"),
        "style": terms.get("image_style", ""),
    },
    "images": [],
}

for t in terms["terms"]:
    spec["images"].append({
        "filename": t["image_file"],
        "term_et": t["et"],
        "term_ru": t["ru"],
        "category": t["category"],
        "description": t["desc"],
        "prompt": t["prompt"],
    })

out = os.path.join(BASE, "data", "gpt_image_prompts.json")
json.dump(spec, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("wrote", out, f"({len(spec['images'])} images)")
