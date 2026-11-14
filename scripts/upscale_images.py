#!/usr/bin/env python3
"""Upscale working images to 1024x1024 with Lanczos, in place (git-backed, reversible).

Overwrites assets/images/*.jpg with a 1024x1024 version.
"""
import os
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(BASE, "assets", "images")

TARGET = 1024
files = sorted(f for f in os.listdir(IMG) if f.endswith(".jpg"))
n = 0
for f in files:
    p = os.path.join(IMG, f)
    im = Image.open(p).convert("RGB")
    if im.size != (TARGET, TARGET):
        im = im.resize((TARGET, TARGET), Image.LANCZOS)
    im.save(p, "JPEG", quality=90, optimize=True)
    n += 1
print("upscaled", n, "files in-place ->", TARGET, "x", TARGET)
