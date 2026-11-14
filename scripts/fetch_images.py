#!/usr/bin/env python3
"""Download one illustrative image per term from Wikimedia Commons (free licenses).

Output: assets/images/<term_id>.jpg (downloaded as-is; extension normalized later).
Writes assets/image_sources.json mapping term_id -> {title, page_url, license, artist}.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "terms.json")
IMG_DIR = os.path.join(BASE, "assets", "images")
SOURCES = os.path.join(BASE, "assets", "image_sources.json")

API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "VocabularyTrainer/1.0 (educational, contact: andrei.krivoshei@gmail.com)"

def api(params):
    params = dict(params, format="json")
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def search_first_file(query):
    """Return best file info dict or None."""
    # Try File namespace search
    try:
        d = api({
            "action": "query", "generator": "search",
            "gsrsearch": f'filetype:bitmap {query}', "gsrnamespace": 6,
            "gsrlimit": 5, "prop": "imageinfo",
            "iiprop": "url|extmetadata|size|mime", "iiurlwidth": 640,
        })
    except Exception:
        return None
    pages = (d.get("query", {}) or {}).get("pages", {}) or {}
    if not pages:
        # fallback: plain search in File ns
        try:
            d = api({
                "action": "query", "generator": "search",
                "gsrsearch": query, "gsrnamespace": 6, "gsrlimit": 5,
                "prop": "imageinfo", "iiprop": "url|extmetadata|size|mime", "iiurlwidth": 640,
            })
        except Exception:
            return None
        pages = (d.get("query", {}) or {}).get("pages", {}) or {}
    if not pages:
        return None
    for p in pages.values():
        ii = (p.get("imageinfo") or [None])[0]
        if not ii:
            continue
        mimetype = ii.get("mime", "")
        if mimetype not in ("image/jpeg", "image/png", "image/webp"):
            continue
        ext = ii.get("extmetadata", {}) or {}
        lic = (ext.get("LicenseShortName") or {}).get("value", "")
        artist = ((ext.get("Artist") or {}).get("value", "") or "")
        # strip HTML from artist/remove credit markup for brevity
        artist = artist.replace("<br/>", " ").replace("<br>", " ")
        import re
        artist = re.sub(r"<[^>]+>", "", artist).strip()
        return {
            "title": p.get("title", ""),
            "page_url": ii.get("descriptionurl", ""),
            "thumb_url": ii.get("thumburl") or ii.get("url", ""),
            "license": lic,
            "artist": artist,
        }
    return None

def download(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    with open(path, "wb") as f:
        f.write(data)
    return len(data)

def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    terms = json.load(open(DATA, encoding="utf-8"))["terms"]
    sources = {}
    ok = fail = 0
    for i, t in enumerate(terms):
        tid = t["id"]
        out = os.path.join(IMG_DIR, tid + ".jpg")
        if os.path.exists(out) and os.path.getsize(out) > 0:
            ok += 1
            continue
        info = search_first_file(t.get("query", t["et"]))
        if not info or not info["thumb_url"]:
            fail += 1
            print(f"[{i+1}/{len(terms)}] {tid}: NO IMAGE", file=sys.stderr)
            continue
        try:
            size = download(info["thumb_url"], out)
        except Exception as e:
            fail += 1
            print(f"[{i+1}/{len(terms)}] {tid}: DL FAIL {e}", file=sys.stderr)
            continue
        sources[tid] = {
            "title": info["title"],
            "page_url": info["page_url"],
            "license": info["license"],
            "artist": info["artist"],
        }
        ok += 1
        print(f"[{i+1}/{len(terms)}] {tid}: OK ({size} bytes) {info['title']}")
        time.sleep(0.6)  # be polite to the API
    json.dump(sources, open(SOURCES, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\nDONE ok={ok} fail={fail}")
    sys.exit(1 if fail else 0)

if __name__ == "__main__":
    main()
