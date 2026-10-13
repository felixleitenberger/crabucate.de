#!/usr/bin/env python3
"""Rendert die Hero-Bilder der App-Seiten aus den rohen Simulator-Aufnahmen.

    python3 notes/heroes/build.py            # alle
    python3 notes/heroes/build.py ruhe       # nur eine App

Jede Szene ist eine kleine HTML-Seite: echte Screenshots in CSS-Geräterahmen
(iPad, iPhone), gedreht und überlappend, auf transparentem Grund. Headless
Chrome fotografiert sie mit doppelter Pixeldichte, cwebp packt sie als WebP mit
Alphakanal. Der Schatten liegt im Alphakanal, deshalb funktionieren die Bilder
auf hellem und dunklem Grund.

Die Quellen liegen NICHT im Repo, sondern in den App-Projekten nebenan
(~/Developer/<App>/…) — dort, wo fastlane bzw. die Screenshot-Pipeline sie
ablegt. Fehlt eine Quelle, bricht das Skript mit ihrem Pfad ab.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEV = ROOT.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
W, H = 1280, 900          # CSS-Pixel der Bühne; gerendert wird mit Faktor 2
PAD_X, PAD_Y = 40, 30     # Rand, damit der Schatten nicht an der Bildkante abreißt

RUHE_RAW = DEV / "Ruhe/screenshots/public/screenshots/apple"
BESTIARY_RAW = DEV / "Wildcards/fastlane/screenshots"
PLATZWAHL_RAW = DEV / "Platzwahl/appstore_screenshots/raw"
TRACKER_RAW = DEV / "Lehrer Arbeitszeit/Screenshots"
TZ_RAW = ROOT / "images/team-zufall/screenshots/light"

# Seiten-Kennung -> Ordner der Rohaufnahmen
RUHE_LANGS = {
    "de": "de", "en": "en", "fr": "fr", "es": "es", "it": "it", "pt-br": "pt-BR",
    "nl": "nl", "da": "da", "sv": "sv", "nb": "nb", "fi": "fi", "pl": "pl",
    "cs": "cs", "tr": "tr", "uk": "uk", "ja": "ja", "ko": "ko",
    "zh-hans": "zh-Hans", "zh-hant": "zh-Hant",
}
BESTIARY_LANGS = {
    "en": "en-US", "de": "de-DE", "fr": "fr-FR", "es": "es-ES", "it": "it",
    "pt-br": "pt-BR", "ja": "ja", "ko": "ko", "zh-hans": "zh-Hans", "zh-hant": "zh-Hant",
}

CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: %dpx; height: %dpx; background: transparent; overflow: hidden; }
.dev { position: absolute; background: #0d0d0f;
  box-shadow: 0 0 0 1.5px #4a4a4f, 0 0 0 3px #1b1b1d,
              0 34px 50px -26px rgba(20,10,0,.50), 0 12px 22px -10px rgba(20,10,0,.28); }
.scene { position: absolute; left: %dpx; top: %dpx; }
.dev img { position: absolute; display: block; object-fit: cover; }
.island { position: absolute; background: #000; border-radius: 999px; z-index: 2; }
""" % (W, H, PAD_X, PAD_Y)


def need(p: pathlib.Path) -> str:
    if not p.exists():
        sys.exit(f"Quelle fehlt: {p}")
    return p.as_uri()


def ipad(src: pathlib.Path, x: float, y: float, w: float, ratio: float, rot: float = 0, z: int = 1) -> str:
    """Querformat, wenn ratio > 1 (Breite/Höhe des Screens)."""
    bez = w * 0.026
    sw = w - 2 * bez
    sh = sw / ratio
    h = sh + 2 * bez
    r = min(w, h) * 0.055
    return (f'<div class="dev" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
            f'border-radius:{r}px;transform:rotate({rot}deg);z-index:{z}">'
            f'<img src="{need(src)}" style="left:{bez}px;top:{bez}px;width:{sw}px;height:{sh}px;'
            f'border-radius:{r - bez * 0.7}px"></div>')


def iphone(src: pathlib.Path, x: float, y: float, h: float, rot: float = 0, z: int = 2,
           ratio: float = 1320 / 2868) -> str:
    bez = h * 0.016
    sh = h - 2 * bez
    sw = sh * ratio
    w = sw + 2 * bez
    r = w * 0.17
    iw, ih = sw * 0.30, sw * 0.088
    return (f'<div class="dev" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
            f'border-radius:{r}px;transform:rotate({rot}deg);z-index:{z}">'
            f'<img src="{need(src)}" style="left:{bez}px;top:{bez}px;width:{sw}px;height:{sh}px;'
            f'border-radius:{r - bez * 0.8}px">'
            f'<div class="island" style="left:{(w - iw) / 2}px;top:{bez + sw * 0.03}px;'
            f'width:{iw}px;height:{ih}px"></div></div>')


def render(body: str, out: pathlib.Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        page = pathlib.Path(tmp, "scene.html")
        page.write_text(f"<!doctype html><meta charset=utf-8><style>{CSS}</style><body><div class=scene>{body}</div>",
                        encoding="utf-8")
        png = pathlib.Path(tmp, "scene.png")
        subprocess.run([CHROME, "--headless=new", "--hide-scrollbars", "--allow-file-access-from-files",
                        "--force-device-scale-factor=2", "--default-background-color=00000000",
                        f"--window-size={W},{H}", "--virtual-time-budget=3000",
                        f"--screenshot={png}", page.as_uri()],
                       check=True, capture_output=True)
        subprocess.run(["cwebp", "-quiet", "-q", "84", "-alpha_q", "90", "-m", "6",
                        str(png), "-o", str(out)], check=True)
    print(f"{out.relative_to(ROOT)}  {out.stat().st_size // 1024} KB")


# ── Szenen ──────────────────────────────────────────────────────────────────

def ruhe() -> None:
    # Ampel in drei Farben: Gelb links, Grün mit vollem Kranz in der Mitte, Rot rechts.
    for code, raw in RUHE_LANGS.items():
        ph, pd = RUHE_RAW / "iphone" / raw, RUHE_RAW / "ipad" / raw
        body = (iphone(ph / "02-yellow.png", 150, 175, 600, rot=-7, z=1)
                + ipad(pd / "01-hero.png", 345, 30, 510, 2064 / 2752, z=2)
                + iphone(ph / "03-red.png", 773, 175, 600, rot=7, z=1))
        render(body, ROOT / f"images/ruhe/hero/{code}.webp")


def bestiary() -> None:
    for code, raw in BESTIARY_LANGS.items():
        d = BESTIARY_RAW / raw
        body = (iphone(d / "01_today.png", 175, 120, 640, rot=-8, z=1)
                + iphone(d / "04_card_back.png", 730, 120, 640, rot=8, z=1)
                + iphone(d / "03_card_front.png", 425, 30, 740, z=2))
        render(body, ROOT / f"images/bestiary/hero/{code}.webp")


def platzwahl() -> None:
    for code in ("de", "en"):
        r = 2420 / 1668
        body = (ipad(PLATZWAHL_RAW / f"{code}_05_druckeAus.png", 380, 24, 790, r, z=1)
                + ipad(PLATZWAHL_RAW / f"{code}_01_perfekterSitzplan.png", 30, 196, 820, r, z=2))
        render(body, ROOT / f"images/platzwahl/hero/{code}.webp")


def team_zufall() -> None:
    r = 2752 / 2064
    body = (ipad(TZ_RAW / "app-01-overview.png", 400, 24, 770, r, z=1)
            + ipad(TZ_RAW / "app-03-teams.png", 30, 176, 790, r, z=2))
    render(body, ROOT / "images/team-zufall/hero.webp")


def tracker() -> None:
    # Unter light/ und dark/, weil theme.js die dunkle Quelle am Pfadsegment erkennt.
    for mode in ("light", "dark"):
        body = (ipad(TRACKER_RAW / f"ipad_{mode}_analyse.png", 30, 70, 900, 2752 / 2064, z=1)
                + iphone(TRACKER_RAW / f"iphone_{mode}_tracker.png", 820, 110, 680, z=2))
        render(body, ROOT / f"images/lehrer-arbeitszeit/hero/{mode}/hero.webp")


SCENES = {"ruhe": ruhe, "bestiary": bestiary, "platzwahl": platzwahl,
          "team-zufall": team_zufall, "tracker": tracker}

if __name__ == "__main__":
    for name in sys.argv[1:] or SCENES:
        SCENES[name]()
