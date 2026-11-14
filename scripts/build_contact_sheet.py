#!/usr/bin/env python3
"""One-pass: download curated thumbnails + build a labeled contact sheet for visual QA.

- Reads data/curated_images.json (from subagent).
- Downloads thumburl -> /tmp/curated/<id>.jpg (skip nulls).
- Builds /tmp/contact_sheet.png grid, caption = id on top-left.
"""
import json, os, urllib.request, sys, io
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUR = json.load(open(os.path.join(BASE, "data", "curated_images.json"), encoding="utf-8"))
OUT = "/tmp/curated"
os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "VocabularyTrainer/1.0 (educational contact: andrei.krivoshei@gmail.com)"}

CELL_W, CELL_H = 260, 200
LABEL_H = 22
COLS = 8

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=60).read()

cells = []  # (id, image, ok_bool)
for tid in sorted(CUR):
    v = CUR[tid]
    if not v or not v.get("thumburl"):
        cells.append((tid, None, False))
        continue
    p = os.path.join(OUT, tid + ".jpg")
    try:
        if not os.path.exists(p):
            data = fetch(v["thumburl"])
            open(p, "wb").write(data)
        img = Image.open(p).convert("RGB")
        cells.append((tid, img, True))
    except Exception as e:
        print("FAIL", tid, e, file=sys.stderr)
        cells.append((tid, None, False))

rows = (len(cells) + COLS - 1) // COLS
sheet = Image.new("RGB", (COLS * CELL_W, rows * (CELL_H + LABEL_H)), (245, 245, 245))
d = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
except Exception:
    font = ImageFont.load_default()

for i, (tid, img, ok) in enumerate(cells):
    r, c = divmod(i, COLS)
    x, y = c * CELL_W, r * (CELL_H + LABEL_H)
    if ok:
        img.thumbnail((CELL_W - 8, CELL_H - 8))
        ox = x + (CELL_W - img.width) // 2
        oy = y + LABEL_H + (CELL_H - img.height) // 2
        sheet.paste(img, (ox, oy))
        status = ""
    else:
        d.rectangle([x, y + LABEL_H, x + CELL_W, y + LABEL_H + CELL_H], fill=(230, 90, 90))
        status = " (NO IMG)"
    d.text((x + 4, y + 3), tid + status, fill=(20, 20, 20), font=font)

sheet.save("/tmp/contact_sheet.png")
print("saved /tmp/contact_sheet.png", sheet.size, "cells:", len(cells), "ok:", sum(1 for _,_,o in cells if o))
