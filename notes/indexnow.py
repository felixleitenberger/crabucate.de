#!/usr/bin/env python3
"""Meldet geänderte Seiten per IndexNow an Bing, Yandex, Seznam, Naver und Co.

    python3 notes/indexnow.py                     # alle URLs aus sitemap.xml
    python3 notes/indexnow.py platzwahl.html ...  # nur diese Pfade

Erst nach dem Deploy aufrufen: Die Suchmaschinen prüfen den Schlüssel unter
https://crabucate.de/<key>.txt. Die Schlüsseldatei liegt im Wurzelverzeichnis
und muss dort bleiben. Google nimmt an IndexNow nicht teil; dort reicht die
Sitemap in der Search Console.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = "https://crabucate.de"


def key() -> str:
    keys = [p for p in ROOT.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}", p.stem)]
    if len(keys) != 1:
        sys.exit(f"Erwarte genau eine Schlüsseldatei <32 hex>.txt im Wurzelverzeichnis, gefunden: {keys}")
    return keys[0].stem


def urls(args: list[str]) -> list[str]:
    if args:
        return [f"{SITE}/{a.lstrip('/')}" for a in args]
    return re.findall(r"<loc>([^<]+)</loc>", (ROOT / "sitemap.xml").read_text(encoding="utf-8"))


if __name__ == "__main__":
    k = key()
    body = {"host": "crabucate.de", "key": k, "keyLocation": f"{SITE}/{k}.txt", "urlList": urls(sys.argv[1:])}
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req) as r:
        print(r.status, len(body["urlList"]), "URLs gemeldet")
