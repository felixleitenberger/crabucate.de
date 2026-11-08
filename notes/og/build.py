#!/usr/bin/env python3
"""Rendert die Vorschaubilder für geteilte Links (og:image), eins pro App und Sprache.

    python3 notes/og/build.py              # alle
    python3 notes/og/build.py platzwahl    # nur eine App

Links Icon und App-Name, rechts die Hero-Szene der App-Seite in derselben
Sprache. Quelle sind die fertigen Hero-Bilder unter images/<app>/hero/, also
nach einem neuen Hero erst notes/heroes/build.py, dann dieses Skript laufen
lassen. Ausgabe: images/og/<app>/<code>.jpg, 1200×630 (gerendert mit 2×, dann
verkleinert). Welche Seite welches Bild nennt, steht in den Seiten bzw. den
Generatoren unter notes/<app>/build.py.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
W, H = 1200, 630


def tz_names() -> dict[str, str]:
    names = {"de": "Team Zufall", "en": "Team Draw"}
    for f in sorted((ROOT / "notes/team-zufall/i18n").glob("*.json")):
        names[f.stem] = json.loads(f.read_text(encoding="utf-8"))["name"]
    return names


def heroes(app: str) -> list[str]:
    return sorted(p.stem for p in (ROOT / f"images/{app}/hero").glob("*.webp"))


# App -> (Farbe, Icon, {Sprache: (Name, Hero)})
def apps() -> dict[str, tuple[str, str, dict[str, tuple[str, str]]]]:
    tz = tz_names()
    return {
        "platzwahl": ("#F5923A", "images/platzwahl/icons/light/icon.png",
                      {c: ("Platzwahl", f"images/platzwahl/hero/{c}.webp") for c in heroes("platzwahl")}),
        "team-zufall": ("#F07D4A", "images/team-zufall/icons/light/icon.png",
                        {c: (tz[c], f"images/team-zufall/hero/{c}.webp") for c in heroes("team-zufall")}),
        "ruhe": ("#FF9300", "images/ruhe/icons/light/icon.png",
                 {c: ("Ruhe", f"images/ruhe/hero/{c}.webp") for c in heroes("ruhe")}),
        "bestiary": ("#E8622C", "images/bestiary/icon.png",
                     {c: ("Daily Bestiary", f"images/bestiary/hero/{c}.webp") for c in heroes("bestiary")}),
        "lehrer-arbeitszeit": ("#F79D39", "images/lehrer-arbeitszeit/icons/light/icon.png",
                               {"de": ("Lehrer Arbeitszeit Tracker", "images/lehrer-arbeitszeit/hero/light/hero.webp")}),
    }


PAGE = """<!doctype html><meta charset=utf-8><style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: {W}px; height: {H}px; overflow: hidden; }}
body {{ background: #FBF6EF; font-family: -apple-system, BlinkMacSystemFont, 'Hiragino Sans', 'PingFang SC', 'Apple SD Gothic Neo', sans-serif;
  position: relative; color: #241F1A; }}
.glow {{ position: absolute; right: -160px; top: 50%; width: 900px; height: 760px; transform: translateY(-50%);
  background: radial-gradient(ellipse at center, {color}33, transparent 65%); }}
.copy {{ position: absolute; left: 72px; top: 0; bottom: 0; width: 380px; display: flex; flex-direction: column; justify-content: center; }}
.icon {{ width: 132px; height: 132px; display: block; margin-bottom: 34px; filter: drop-shadow(0 14px 22px rgba(36,31,26,.18)); }}
h1 {{ font-size: {size}px; font-weight: 800; letter-spacing: -0.035em; line-height: 1.02; }}
.domain {{ position: absolute; left: 72px; bottom: 44px; font-size: 19px; font-weight: 600; letter-spacing: 0.02em; color: #8A8073; }}
.domain b {{ color: {color}; font-weight: 700; }}
.hero {{ position: absolute; right: {right}px; top: 50%; height: {hero_h}px; transform: translateY(-50%); }}
</style>
<div class=glow></div>
<div class=copy><img class=icon src="{icon}"><h1>{name}</h1></div>
<div class=domain><b>crabucate</b>.de</div>
<img class=hero src="{hero}">
"""


def render(app: str, color: str, icon: str, name: str, hero: str, out: pathlib.Path) -> None:
    size = 64 if len(name) <= 12 else 50
    # Team Zufalls Szene (Fernseher plus iPhone) ist fast quadratisch und füllt
    # ihre Fläche bis an den Rand; sie braucht weniger Höhe und Abstand rechts.
    hero_h, right = (520, 40) if app == "team-zufall" else (590, -36)
    page = PAGE.format(W=W, H=H, color=color, size=size, name=name, hero_h=hero_h, right=right,
                       icon=(ROOT / icon).as_uri(), hero=(ROOT / hero).as_uri())
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        f = pathlib.Path(tmp, "og.html")
        f.write_text(page, encoding="utf-8")
        png = pathlib.Path(tmp, "og.png")
        subprocess.run([CHROME, "--headless=new", "--hide-scrollbars", "--allow-file-access-from-files",
                        "--force-device-scale-factor=2", f"--window-size={W},{H}",
                        "--virtual-time-budget=3000", f"--screenshot={png}", f.as_uri()],
                       check=True, capture_output=True)
        Image.open(png).convert("RGB").resize((W, H), Image.LANCZOS).save(out, "JPEG", quality=84, optimize=True, progressive=True)
    print(f"{out.relative_to(ROOT)}  {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    table = apps()
    for app in sys.argv[1:] or table:
        color, icon, langs = table[app]
        for code, (name, hero) in langs.items():
            render(app, color, icon, name, hero, ROOT / f"images/og/{app}/{code}.jpg")
