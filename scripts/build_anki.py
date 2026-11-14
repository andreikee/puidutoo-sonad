#!/usr/bin/env python3
"""Build an Anki deck (.apkg) from terms.json + images.json.

Card front: image + Estonian word  ->  back: Russian translation.
Also adds a second note type (Ru->Et) for reverse recall.
"""
import base64, json, os, sys
import genanki

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(BASE, "assets", "images")
OUT_DIR = os.path.join(BASE, "dist")
os.makedirs(OUT_DIR, exist_ok=True)

terms = json.load(open(os.path.join(BASE, "data", "terms.json"), encoding="utf-8"))
imgs = json.load(open(os.path.join(BASE, "data", "images.json"), encoding="utf-8"))

DECK_ID = 2059400110
MODEL_ET_RU = 2059400111
MODEL_RU_ET = 2059400112

def media_files():
    out = {}
    for t in terms["terms"]:
        f = imgs[t["id"]]["file"]
        p = os.path.join(IMG, f)
        out[f] = p
    return out

css = """.card {
  font-family: system-ui, -apple-system, Roboto, sans-serif;
  text-align: center;
  color: #3a3a42;
  font-size: 20px;
}
.et { font-size: 2.2em; font-weight: 800; margin: 10px 0; color: #5b4020; }
.ru { font-size: 1.4em; color: #8a5a2a; margin-bottom: 10px; }
img { max-width: 100%; max-height: 320px; margin: 8px 0; border-radius: 12px; }
"""

def front_side(img_field):
    return f'''<div class="card">{{{{Image}}}}</div><div class="et">{{{{{img_field}}}}}</div>'''

model_et_ru = genanki.Model(
    MODEL_ET_RU, "VocabEtRu",
    fields=[{"name": "Image"}, {"name": "Estonian"}, {"name": "Russian"}],
    templates=[{
        "name": "Et->Ru",
        "qfmt": '<div class="card">{{Image}}</div><div class="et">{{Estonian}}</div>',
        "afmt": '<div class="card">{{Image}}</div><div class="et">{{Estonian}}</div><hr><div class="ru">{{Russian}}</div>',
    }],
    css=css,
)
model_ru_et = genanki.Model(
    MODEL_RU_ET, "VocabRuEt",
    fields=[{"name": "Image"}, {"name": "Estonian"}, {"name": "Russian"}],
    templates=[{
        "name": "Ru->Et",
        "qfmt": '<div class="card">{{Image}}</div><div class="ru">{{Russian}}</div>',
        "afmt": '<div class="card">{{Image}}</div><div class="ru">{{Russian}}</div><hr><div class="et">{{Estonian}}</div>',
    }],
    css=css,
)

deck = genanki.Deck(DECK_ID, "Puidutöö sõnad (Технология — дерево)")
pkg = genanki.Package(deck)
pkg.media_files = list(media_files().values())

for t in terms["terms"]:
    f = imgs[t["id"]]["file"]
    fields = [f'<img src="{f}">', t["et"], t["ru"]]
    deck.add_note(genanki.Note(model=model_et_ru, fields=fields))
    deck.add_note(genanki.Note(model=model_ru_et, fields=fields))

out = os.path.join(OUT_DIR, "puidutoo_sonad.apkg")
pkg.write_to_file(out)
print("wrote", out, f"{os.path.getsize(out)/1024/1024:.1f} MB", "notes:", len(terms["terms"]) * 2)
