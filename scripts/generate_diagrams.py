#!/usr/bin/env python3
"""Generate clean labeled diagrams for the 7 abstract terms (deterministic, no network).

Output assets/images/<id>.png (diagrams) + print attribution note.
Terms: pikkus, laius, paksus, korgus, sugavus, altvaade, kavandamine
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "assets", "images")
os.makedirs(OUT, exist_ok=True)

W, H = 640, 420
BG = (255, 252, 242)
INK = (40, 40, 45)
ACC = (214, 90, 60)   # warm accent for arrows/labels
SOFT = (90, 130, 170)

def font(sz, bold=False):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")
    try:
        return ImageFont.truetype(p, sz)
    except Exception:
        return ImageFont.load_default()

def new_img():
    return Image.new("RGB", (W, H), BG), ImageDraw.Draw(Image.new("RGB", (W, H), BG))

def arrow(d, x1, y1, x2, y2, color=ACC, wd=6):
    d.line([x1, y1, x2, y2], fill=color, width=wd)
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    L = 16
    for s in (1, -1):
        aa = a + math.pi + s * 0.5
        d.line([x2, y2, x2 + L * math.cos(aa), y2 + L * math.sin(aa)], fill=color, width=wd)

def label(d, xy, txt, f, color=INK, anchor_inner=False):
    d.text(xy, txt, fill=color, font=f)

def draw_box_dimension(mode):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    f_small = font(26)
    f_big = font(30, True)
    # A 3D-ish wooden box as three shaded rects
    top = [(140, 90), (360, 90), (410, 50), (190, 50)]
    front = [(140, 90), (360, 90), (360, 250), (140, 250)]
    side = [(360, 90), (410, 50), (410, 210), (360, 250)]
    d.polygon(top, fill=(200, 150, 105))     # top light
    d.polygon(front, fill=(165, 116, 76))    # front mid
    d.polygon(side, fill=(130, 88, 55))      # side darker
    for poly in (top, front, side):
        d.line(poly + [poly[0]], fill=INK, width=3)
    if mode == "pikkus":   # length: horizontal arrow along front bottom
        arrow(d, 150, 290, 350, 290)
        d.text((205, 306), "pikkus — длина", fill=INK, font=f_small)
    elif mode == "laius":  # width: arrow across top
        arrow(d, 145, 40, 405, 40)
        d.text((215, 12), "laius — ширина", fill=INK, font=f_small)
    elif mode == "korgus": # height: vertical arrow on right
        arrow(d, 450, 250, 450, 55)
        d.text((465, 130), "kõrgus — высота", fill=INK, font=f_small)
    elif mode == "sugavus": # depth: arrow into box (along side depth)
        arrow(d, 320, 60, 440, 40)
        d.text((300, 20), "sügavus — глубина", fill=INK, font=f_small)
    elif mode == "paksus": # thickness: a thin plank edge with arrow
        d.rectangle([150, 150, 490, 220], fill=(165, 116, 76), outline=INK, width=3)
        d.line([150, 180, 490, 180], fill=(200, 165, 120), width=2)
        arrow(d, 520, 220, 520, 150)
        d.text((180, 100), "paksus — толщина", fill=INK, font=f_small)
    return img

def draw_bottom_view():
    # "вид снизу" — a simple box seen from below: square with light bottom face + legs
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    f = font(26)
    d.rectangle([180, 110, 460, 300], fill=(165, 116, 76), outline=INK, width=4)
    d.rectangle([200, 130, 440, 280], outline=(120, 80, 50), width=2)  # inner panel
    for cx in (220, 420):
        d.ellipse([cx - 14, 306, cx + 14, 334], fill=(90, 90, 95))     # legs seen from below
        d.ellipse([cx - 14, 60, cx + 14, 88], fill=(90, 90, 95))
    d.text((180, 360), "altvaade — вид снизу", fill=INK, font=f)
    return img

def draw_sketching():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    f = font(26)
    # a pencil drawing lines + rough box sketch
    for x in (150, 190, 230, 270):
        d.line([x, 300, x + 170, 140], fill=(120, 120, 125), width=2)
    d.rectangle([250, 120, 460, 280], outline=INK, width=4)
    d.line([250, 120, 355, 70], fill=INK, width=3)
    d.line([460, 120, 355, 70], fill=INK, width=3)
    d.line([355, 70, 355, 230], fill=INK, width=3)
    d.line([250, 280, 355, 230], fill=INK, width=3)
    d.line([460, 280, 355, 230], fill=INK, width=3)
    # pencil
    d.polygon([(60, 220), (90, 220), (95, 250), (55, 250)], fill=(230, 170, 60), outline=INK, width=2)
    d.polygon([(60, 250), (82, 250), (78, 280), (64, 280)], fill=(240, 200, 120))
    d.polygon([(64, 280), (78, 280), (73, 300), (69, 300)], fill=(60, 60, 65))
    d.text((140, 360), "kavandamine — эскизирование", fill=INK, font=f)
    return img

JOBS = {
    "pikkus": draw_box_dimension("pikkus"),
    "laius": draw_box_dimension("laius"),
    "paksus": draw_box_dimension("paksus"),
    "korgus": draw_box_dimension("korgus"),
    "sugavus": draw_box_dimension("sugavus"),
    "altvaade": draw_bottom_view(),
    "kavandamine": draw_sketching(),
}

for tid, img in JOBS.items():
    p = os.path.join(OUT, tid + ".png")
    img.save(p)
    print("generated", p)
print("done", len(JOBS))
