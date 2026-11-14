#!/usr/bin/env python3
"""Finalize image set (one pass, no loops).

- Download curated photo thumbnails (data/curated_images.json) -> assets/images/<id>.jpg
- Keep generated diagrams assets/images/<id>.png for abstract terms
- Remove stale .jpg from the earlier first pass
- Write data/images.json: id -> {file, license, artist, title, page_url, generated}
"""
import json, os, sys, urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(BASE, "assets", "images")
CUR = json.load(open(os.path.join(BASE, "data", "curated_images.json"), encoding="utf-8"))
UA = {"User-Agent": "VocabularyTrainer/1.0 (educational contact: andrei.krivoshei@gmail.com)"}

DIAGRAMS = {"pikkus", "laius", "paksus", "korgus", "sugavus", "altvaade", "kavandamine"}

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=60).read()

manifest = {}
ok = fail = 0
for tid, v in sorted(CUR.items()):
    if tid in DIAGRAMS or not v:
        # diagram file already generated
        png = os.path.join(IMG, tid + ".png")
        manifest[tid] = {
            "file": tid + ".png",
            "license": "Generated diagram (original, CC0)",
            "artist": "Vocabulary trainer project",
            "title": f"Diagram: {tid}",
            "page_url": "",
            "generated": True,
        }
        if not os.path.exists(png):
            print("MISSING DIAGRAM", tid, file=sys.stderr), sys.exit(1)
        ok += 1
        continue
    out = os.path.join(IMG, tid + ".jpg")
    try:
        data = fetch(v["thumburl"])
        open(out, "wb").write(data)
        ok += 1
    except Exception as e:
        fail += 1
        print("FAIL", tid, e, file=sys.stderr)
        manifest[tid] = {"file": "", "license": "", "artist": "", "title": "", "page_url": "", "generated": False}
        continue
    manifest[tid] = {
        "file": tid + ".jpg",
        "license": v.get("license", ""),
        "artist": v.get("artist", ""),
        "title": v.get("title", ""),
        "page_url": v.get("thumburl", ""),
        "generated": False,
    }

# remove stale .jpg from first pass that are not part of final set
keep_jpg = {m["file"] for m in manifest.values() if m["file"].endswith(".jpg")}
for f in os.listdir(IMG):
    if f.endswith(".jpg") and f not in keep_jpg:
        os.remove(os.path.join(IMG, f))
        print("removed stale", f)

json.dump(manifest, open(os.path.join(BASE, "data", "images.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"DONE ok={ok} fail={fail} total={len(manifest)}")
sys.exit(1 if fail else 0)
