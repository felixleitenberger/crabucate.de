#!/usr/bin/env python3
"""Erzeugt die Team-Zufall-Seiten in den weiteren Sprachen der App unter /team-zufall/<code>/.

    python3 notes/team-zufall/build.py

Deutsch und Englisch bleiben handgeschrieben (team-zufall.html und
en/team-zufall.html). Die deutsche Seite ist die Vorlage: Stil und
Feature-Icons liest das Skript aus team-zufall.html, damit alle Sprachen gleich
aussehen. Wer dort etwas am Aussehen ändert, lässt das Skript danach einmal
laufen.

Die App heißt in jeder Sprache anders (Team Draw, Team Tirage, チーム抽選 …);
der Name steht als "name" in der jeweiligen Sprachdatei und ersetzt dort {n}.
Datenschutz und Nutzungsbedingungen gibt es nur auf Deutsch und Englisch, die
generierten Seiten verlinken die englischen.

Das Skript schreibt außerdem den Sprachwähler und die hreflang-Liste der beiden
handgeschriebenen Seiten und den Team-Zufall-Block in sitemap.xml. Eine weitere
Sprache ist eine Datei in i18n/ plus eine Zeile in LANGS; die Screenshots
gehören nach images/team-zufall/screenshots/<code>/.
"""

from __future__ import annotations

import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
I18N = pathlib.Path(__file__).resolve().parent / "i18n"
SITE = "https://crabucate.de"

# Kennung (= Pfad unter /team-zufall/ und Name der JSON-Datei), hreflang, Name im Sprachwähler.
LANGS = [
    ("de",      "de",      "Deutsch"),
    ("en",      "en",      "English"),
    ("fr",      "fr",      "Français"),
    ("es",      "es",      "Español"),
    ("it",      "it",      "Italiano"),
    ("pt-br",   "pt-BR",   "Português"),
    ("nl",      "nl",      "Nederlands"),
    ("da",      "da",      "Dansk"),
    ("sv",      "sv",      "Svenska"),
    ("nb",      "nb",      "Norsk"),
    ("fi",      "fi",      "Suomi"),
    ("pl",      "pl",      "Polski"),
    ("tr",      "tr",      "Türkçe"),
    ("uk",      "uk",      "Українська"),
    ("ru",      "ru",      "Русский"),
    ("id",      "id",      "Bahasa Indonesia"),
    ("ja",      "ja",      "日本語"),
    ("ko",      "ko",      "한국어"),
    ("zh-hans", "zh-Hans", "简体中文"),
]
HANDWRITTEN = ("de", "en")

APPSTORE = "https://apps.apple.com/app/id6768655282"
SHOTS = 6


def e(text: str) -> str:
    return html.escape(text, quote=False)


def a(text: str) -> str:
    return html.escape(text, quote=True)


def rel(code: str) -> str:
    """Pfad der Seite relativ zum Wurzelverzeichnis."""
    return {"de": "team-zufall.html", "en": "en/team-zufall.html"}.get(code, f"team-zufall/{code}/")


def url(code: str) -> str:
    return f"{SITE}/{rel(code)}"


def localize(obj, name: str):
    """Setzt den App-Namen der Sprache überall für {n} ein."""
    if isinstance(obj, str):
        return obj.replace("{n}", name)
    if isinstance(obj, list):
        return [localize(x, name) for x in obj]
    if isinstance(obj, dict):
        return {k: localize(v, name) for k, v in obj.items()}
    return obj


# ──────────────────────────────────────────────────── aus der Vorlage lesen ──

TEMPLATE = (ROOT / "team-zufall.html").read_text(encoding="utf-8")
CSS = TEMPLATE.split("<style>", 1)[1].split("</style>", 1)[0]
ICONS = re.findall(r'<div class="feat-icon">(.*?)</div>', TEMPLATE)
assert len(ICONS) == 6, "team-zufall.html sollte sechs Feature-Icons haben"
TOGGLE = re.search(r'(<button class="theme-toggle".*?</button>)', TEMPLATE, re.S).group(1)
GLOBE = re.search(r'(<svg class="lang-globe".*?</svg>)', TEMPLATE).group(1)
CARET = re.search(r'(<svg class="lang-caret".*?</svg>)', TEMPLATE).group(1)
CHECK = re.search(r'(<svg class="lang-check".*?</svg>)', TEMPLATE).group(1)
THEME_SNIPPET = re.search(r"(<script>\(function\(\)\{var d=.*?</script>)", TEMPLATE).group(1)


# ─────────────────────────────────────────────────────────────── Bausteine ──

def alternates() -> str:
    lines = [f'  <link rel="alternate" hreflang="{hl}" href="{url(code)}" />' for code, hl, _ in LANGS]
    lines.append(f'  <link rel="alternate" hreflang="x-default" href="{url("de")}" />')
    return "\n".join(lines)


def lang_panel(current: str, up: str) -> str:
    items = []
    for code, hl, name in LANGS:
        if code == current:
            items.append(f'          <span class="lang-item lang-item--active" aria-current="true">'
                         f'{CHECK}{e(name)}</span>')
        else:
            items.append(f'          <a class="lang-item" hreflang="{hl}" lang="{hl}" '
                         f'href="{up}{rel(code)}">{CHECK}{e(name)}</a>')
    return '<div class="lang-panel">\n' + "\n".join(items) + "\n        </div>"


def ld(obj: dict) -> str:
    body = json.dumps(obj, ensure_ascii=False, indent=2).replace("</", "<\\/")
    return '\n  <script type="application/ld+json">\n' + body + "\n  </script>"


# ───────────────────────────────────────────────────────────────── Seite ──

def render(d: dict, code: str, hl: str, lang_name: str) -> str:
    up = "../../"
    name = d["name"]
    icon = f"""<picture>
          <source srcset="{up}images/team-zufall/icons/dark/icon.png" media="(prefers-color-scheme: dark)" />
          <img src="{up}images/team-zufall/icons/light/icon.png" alt="{a(d["icon_alt"])}" class="stage-icon" />
        </picture>"""
    badge = f"""<a class="app-store-badge" href="{APPSTORE}" target="_blank" rel="noopener">
            <img src="{up}images/Download_on_the_App_Store_Badge_US_RGB_blk_092917.svg" alt="{a(d["badge_alt"])}" />
          </a>"""
    meta = "".join(f"\n            <li>{e(m)}</li>" for m in d["meta"])
    shots = "\n".join(
        f'    <img src="{up}images/team-zufall/screenshots/{code}/{i:02d}.png" width="552" height="1199"'
        + ("" if i == 1 else ' loading="lazy"') + f' alt="{a(alt)}" />'
        for i, alt in enumerate(d["shots"], 1)
    )
    assert len(d["shots"]) == SHOTS, code
    features = "\n".join(
        f"""      <div class="feat">
        <div class="feat-icon">{svg}</div>
        <h3>{e(t)}</h3>
        <p>{e(p)}</p>
      </div>"""
        for svg, (t, p) in zip(ICONS, d["features"], strict=True)
    )
    how = "\n".join(f"      <li><h3>{e(t)}</h3><p>{e(p)}</p></li>" for t, p in d["how"])
    faq = "\n".join(
        f'    <details class="qa"><summary><h3>{e(q)}</h3></summary>\n      <p>{e(ans)}</p></details>'
        for q, ans in d["faq"]
    )
    # Den Classroom-Management-Ratgeber gibt es nur in den Sprachen von Ruhe.
    guide = ""
    if "guide" in d:
        g = d["guide"]
        guide = f"""
  <!-- RATGEBER -->
  <section class="sec">
    <h2 class="sec-title">{e(g["eyebrow"])}</h2>
    <ul class="guide-links">
      <li><a href="{up}ruhe/{code}/classroom-management/"><strong>{e(g["card_title"])}</strong><span>{e(g["card_text"])}</span></a></li>
    </ul>
  </section>
"""
    org = {"@type": "Organization", "name": "crabucate", "url": SITE}
    extra = (
        ld({"@context": "https://schema.org", "@type": "MobileApplication", "name": name,
            "operatingSystem": "iOS", "applicationCategory": "EducationApplication",
            "description": d["description"], "inLanguage": hl, "url": APPSTORE, "author": org})
        + ld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}}
            for q, ans in d["faq"]]})
    )
    label = a(d["lang_choose"])
    return f"""<!DOCTYPE html>
<html lang="{hl}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  {THEME_SNIPPET}
  <meta name="color-scheme" content="light dark" />
  <meta name="theme-color" content="#FBF6EF" media="(prefers-color-scheme: light)" />
  <meta name="theme-color" content="#17120E" media="(prefers-color-scheme: dark)" />
  <title>{e(d["title"])}</title>
  <meta name="description" content="{a(d["description"])}" />
  <link rel="canonical" href="{url(code)}" />
{alternates()}
  <meta name="robots" content="index, follow" />{extra}
  <link rel="stylesheet" href="{up}assets/base.css" />
  <link rel="stylesheet" href="{up}assets/app.css" />
  <style>{CSS}</style>
</head>
<body>

  <nav>
    <a href="{up}" class="nav-logo">
      <img src="{up}images/crabucateSquare.jpg" alt="" />
      crabucate
    </a>
    <div class="nav-right">
      <a href="{up}" class="nav-link">{e(d["all_apps"])}</a>
      <details class="lang-menu">
        <summary aria-label="{label}" title="{label}">{GLOBE}<span class="lang-current">{e(lang_name)}</span>{CARET}</summary>
        {lang_panel(code, up)}
      </details>
      {TOGGLE}
    </div>
  </nav>

  <main>
  <!-- STAGE -->
  <section class="stage">
    <div class="stage-inner">
      <div class="stage-copy">
        {icon}
        <p class="stage-new"><b>{e(d["new_label"])}</b>{e(d["new_text"])}</p>
        <h1>{e(name)}</h1>
        <p class="tagline">{e(d["tagline"])}</p>
        <div class="stage-cta">
          {badge}
          <ul class="hero-meta">{meta}
          </ul>
        </div>
      </div>
      <div class="stage-art">
        <img src="{up}images/team-zufall/hero/{code}.webp" width="2400" height="1960" alt="{a(d["hero_alt"])}" />
      </div>
    </div>
  </section>

  <!-- SCREENSHOTS -->
  <div class="shots">
{shots}
  </div>

  <!-- FEATURES -->
  <section class="sec">
    <h2 class="sec-title">{e(d["features_eyebrow"])}</h2>
    <div class="feats">
{features}
    </div>
  </section>

  <!-- SO GEHT'S -->
  <section class="sec">
    <h2 class="sec-title">{e(d["how_eyebrow"])}</h2>
    <ol class="steps">
{how}
    </ol>
  </section>
{guide}
  <!-- FAQ -->
  <section class="sec faq">
    <h2 class="sec-title">{e(d["faq_eyebrow"])}</h2>
{faq}
  </section>

  <!-- SCHLUSS -->
  <section class="closing">
    <picture>
      <source srcset="{up}images/team-zufall/icons/dark/icon.png" media="(prefers-color-scheme: dark)" />
      <img src="{up}images/team-zufall/icons/light/icon.png" alt="" class="closing-icon" loading="lazy" />
    </picture>
    <h2>{e(d["final_title"])}</h2>
    <a class="app-store-badge" href="{APPSTORE}" target="_blank" rel="noopener">
      <img src="{up}images/Download_on_the_App_Store_Badge_US_RGB_blk_092917.svg" alt="{a(d["badge_alt"])}" />
    </a>
  </section>
  </main>

  <footer>
    © 2026 crabucate · <a href="mailto:info@crabucate.de">info@crabucate.de</a> · <a href="{up}en/impressum.html">{e(d["imprint"])}</a> · <a href="{up}en/privacy.html">{e(d["privacy"])}</a> · <a href="{up}en/terms.html">{e(d["terms"])}</a>
  </footer>

  <script src="{up}assets/theme.js" defer></script>
  <script src="{up}assets/lang.js" defer></script>
</body>
</html>
"""


# ─────────────────────────────────────────────── handgeschriebene Seiten ──

def patch_handwritten() -> None:
    """Sprachwähler und hreflang-Liste der beiden DE/EN-Seiten auf den Stand von LANGS bringen."""
    for code in HANDWRITTEN:
        path = ROOT / rel(code)
        up = "../" * rel(code).count("/")
        text = path.read_text(encoding="utf-8")
        text, n1 = re.subn(r'<div class="lang-panel">.*?</div>',
                           lambda _: lang_panel(code, up), text, count=1, flags=re.S)
        text, n2 = re.subn(r'(  <link rel="alternate" hreflang="[^"]+" href="[^"]+" />\n)+',
                           lambda _: alternates() + "\n", text, count=1)
        assert n1 == 1 and n2 == 1, f"{path}: Sprachwähler oder hreflang nicht gefunden"
        path.write_text(text, encoding="utf-8")


SITEMAP_START = "  <!-- Team Zufall, weitere Sprachen — erzeugt von notes/team-zufall/build.py, nicht von Hand pflegen -->"
SITEMAP_END = "  <!-- /Team Zufall, weitere Sprachen -->"


def write_sitemap() -> None:
    lines = [SITEMAP_START]
    for code, _, _ in LANGS:
        if code in HANDWRITTEN:
            continue
        lines += ["  <url>", f"    <loc>{url(code)}</loc>", "    <changefreq>monthly</changefreq>",
                  "    <priority>0.8</priority>", "  </url>"]
    lines.append(SITEMAP_END)

    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    if SITEMAP_START in text:
        before, rest = text.split(SITEMAP_START, 1)
        _, after = rest.split(SITEMAP_END, 1)
        text = before + "\n".join(lines) + after
    else:
        text = text.replace("\n</urlset>", "\n\n" + "\n".join(lines) + "\n\n</urlset>")
    path.write_text(text, encoding="utf-8")


def main() -> None:
    written = 0
    for code, hl, lang_name in LANGS:
        if code in HANDWRITTEN:
            continue
        d = json.loads((I18N / f"{code}.json").read_text(encoding="utf-8"))
        d = localize(d, d["name"])
        target = ROOT / rel(code) / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(d, code, hl, lang_name), encoding="utf-8")
        written += 1
    patch_handwritten()
    write_sitemap()
    print(f"{written} Seiten unter /team-zufall/ geschrieben, DE/EN-Seite und sitemap.xml aktualisiert")


if __name__ == "__main__":
    main()
