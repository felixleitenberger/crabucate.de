#!/usr/bin/env python3
"""Erzeugt die Ruhe-Seiten in den weiteren Sprachen der App unter /ruhe/<code>/.

    python3 notes/ruhe/build.py

Deutsch und Englisch bleiben handgeschrieben (ruhe.html, ruhe-privacy.html und
ihre /en/-Gegenstücke): App Store Connect kennt genau diese Adressen. Sie sind
die Vorlage — Stil und Feature-Icons liest das Skript aus ruhe.html bzw.
ruhe-privacy.html, damit alle Sprachen gleich aussehen. Wer dort etwas am
Aussehen ändert, lässt das Skript danach einmal laufen.

Dazu kommt der Ratgeber „Classroom Management“ unter
/ruhe/<code>/classroom-management/; seine DE/EN-Fassung liegt handgeschrieben in
guides/ bzw. en/guides/ und liefert das CSS.

Das Skript schreibt außerdem den Sprachwähler und die hreflang-Liste in diese
sechs handgeschriebenen Seiten und den Ruhe-Block in sitemap.xml. Eine weitere
Sprache ist eine Datei in i18n/ plus eine Zeile in LANGS; die Screenshots
gehören nach images/ruhe/screenshots/<code>/.
"""

from __future__ import annotations

import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
I18N = pathlib.Path(__file__).resolve().parent / "i18n"
SITE = "https://crabucate.de"

# Kennung (= Pfad unter /ruhe/ und Name der JSON-Datei), hreflang, Name im Sprachwähler.
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
    ("cs",      "cs",      "Čeština"),
    ("tr",      "tr",      "Türkçe"),
    ("uk",      "uk",      "Українська"),
    ("ja",      "ja",      "日本語"),
    ("ko",      "ko",      "한국어"),
    ("zh-hans", "zh-Hans", "简体中文"),
    ("zh-hant", "zh-Hant", "繁體中文"),
]
HANDWRITTEN = ("de", "en")

APPSTORE = "https://apps.apple.com/app/id6817002986"

SHOTS = ["01_belohnt", "02_ampel", "03_timer", "04_beamer", "05_datenschutz"]


def e(text: str) -> str:
    return html.escape(text, quote=False)


def a(text: str) -> str:
    return html.escape(text, quote=True)


def rel(code: str, page: str) -> str:
    """Pfad einer Seite relativ zum Wurzelverzeichnis. page ist '', 'privacy' oder 'guide'."""
    if page == "guide":
        return {"de": "guides/classroom-management.html",
                "en": "en/guides/classroom-management.html"}.get(code, f"ruhe/{code}/classroom-management/")
    if code == "de":
        return "ruhe-privacy.html" if page else "ruhe.html"
    if code == "en":
        return "en/ruhe-privacy.html" if page else "en/ruhe.html"
    return f"ruhe/{code}/" + ("privacy/" if page else "")


def url(code: str, page: str) -> str:
    return f"{SITE}/{rel(code, page)}"


# Inline-Markup in den Sprachdateien, damit dort keine HTML-Attribute stehen:
# **fett**, [[privacy:Text]], [[revenuecat:Text]], [[apple:Text]], {mail}.
LINKS = {
    "privacy": "privacy/",
    "revenuecat": "https://www.revenuecat.com/privacy/",
    "apple": "https://www.apple.com/legal/privacy/",
}

# Im Ratgeber (/ruhe/<code>/classroom-management/): Platzwahl und Team Zufall
# gibt es nur auf Deutsch und Englisch, also zeigen sie auf die englische Seite.
GUIDE_LINKS = {
    "platzwahl": "../../../en/platzwahl.html",
    "teamzufall": "../../../en/team-zufall.html",
    "ruhe": "../",
}


def inline(text: str, links: dict = LINKS) -> str:
    text = e(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    def link(m: re.Match) -> str:
        target = links[m.group(1)]
        ext = ' target="_blank" rel="noopener"' if target.startswith("http") else ""
        return f'<a href="{target}"{ext}>{m.group(2)}</a>'

    text = re.sub(r"\[\[(\w+):(.+?)\]\]", link, text)
    return text.replace("{mail}", '<a href="mailto:info@crabucate.de">info@crabucate.de</a>')


# ──────────────────────────────────────────────────── aus der Vorlage lesen ──

def style_of(path: pathlib.Path) -> str:
    text = path.read_text(encoding="utf-8")
    return text.split("<style>", 1)[1].split("</style>", 1)[0]


TEMPLATE = (ROOT / "ruhe.html").read_text(encoding="utf-8")
INDEX_CSS = style_of(ROOT / "ruhe.html")
PRIVACY_CSS = style_of(ROOT / "ruhe-privacy.html")
GUIDE_CSS = style_of(ROOT / "guides/classroom-management.html")
ICONS = re.findall(r'<div class="feat-icon">(.*?)</div>', TEMPLATE)
assert len(ICONS) == 6, "ruhe.html sollte sechs Feature-Icons haben"
TOGGLE = re.search(r'(<button class="theme-toggle".*?</button>)', TEMPLATE, re.S).group(1)
GLOBE = re.search(r'(<svg class="lang-globe".*?</svg>)', TEMPLATE).group(1)
CARET = re.search(r'(<svg class="lang-caret".*?</svg>)', TEMPLATE).group(1)
CHECK = re.search(r'(<svg class="lang-check".*?</svg>)', TEMPLATE).group(1)
THEME_SNIPPET = re.search(r"(<script>\(function\(\)\{var d=.*?</script>)", TEMPLATE).group(1)


# ─────────────────────────────────────────────────────────────── Bausteine ──

def alternates(page: str) -> str:
    lines = [f'  <link rel="alternate" hreflang="{hl}" href="{url(code, page)}" />'
             for code, hl, _ in LANGS]
    lines.append(f'  <link rel="alternate" hreflang="x-default" href="{url("de", page)}" />')
    return "\n".join(lines)


def lang_panel(current: str, page: str, up: str) -> str:
    items = []
    for code, hl, name in LANGS:
        if code == current:
            items.append(f'          <span class="lang-item lang-item--active" aria-current="true">'
                         f'{CHECK}{e(name)}</span>')
        else:
            items.append(f'          <a class="lang-item" hreflang="{hl}" lang="{hl}" '
                         f'href="{up}{rel(code, page)}">{CHECK}{e(name)}</a>')
    return '<div class="lang-panel">\n' + "\n".join(items) + "\n        </div>"


def head(hl: str, title: str, description: str, code: str, page: str, up: str, css: str,
         extra: str = "") -> str:
    desc = f'\n  <meta name="description" content="{a(description)}" />' if description else ""
    return f"""<!DOCTYPE html>
<html lang="{hl}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  {THEME_SNIPPET}
  <meta name="color-scheme" content="light dark" />
  <meta name="theme-color" content="#FBF6EF" media="(prefers-color-scheme: light)" />
  <meta name="theme-color" content="#17120E" media="(prefers-color-scheme: dark)" />
  <title>{e(title)}</title>{desc}
  <link rel="canonical" href="{url(code, page)}" />
{alternates(page)}
  <meta name="robots" content="index, follow" />{extra}
  <link rel="stylesheet" href="{up}assets/base.css" />
  <style>{css}</style>
</head>
<body>
"""


def nav(d: dict, code: str, name: str, page: str, up: str, back_href: str, back_cls: str,
        back_label: str) -> str:
    label = a(d["lang_choose"])
    return f"""
  <nav>
    <a href="{up}" class="nav-logo">
      <img src="{up}images/crabucateSquare.jpg" alt="" />
      crabucate
    </a>
    <div class="nav-right">
      <a href="{back_href}" class="{back_cls}">{e(back_label)}</a>
      <details class="lang-menu">
        <summary aria-label="{label}" title="{label}">{GLOBE}<span class="lang-current">{e(name)}</span>{CARET}</summary>
        {lang_panel(code, page, up)}
      </details>
      {TOGGLE}
    </div>
  </nav>
"""


SCRIPTS = """
  <script src="{up}assets/theme.js" defer></script>
  <script src="{up}assets/lang.js" defer></script>
</body>
</html>
"""


# ───────────────────────────────────────────────────────────────── Seiten ──

def render_index(d: dict, code: str, hl: str, name: str) -> str:
    up = "../../"
    shots = "\n".join(
        f'    <img src="{up}images/ruhe/screenshots/{code}/{shot}.png" width="552" height="1200"'
        + ("" if i == 0 else ' loading="lazy"') + f' alt="{a(alt)}" />'
        for i, (shot, alt) in enumerate(zip(SHOTS, d["shots"], strict=True))
    )
    features = "\n".join(
        f"""      <div class="feature-card">
        <div class="feat-icon">{icon}</div>
        <h3>{e(t)}</h3>
        <p>{inline(p)}</p>
      </div>"""
        for icon, (t, p) in zip(ICONS, d["features"], strict=True)
    )
    how = "\n".join(
        f"""      <li>
        <h3>{e(t)}</h3>
        <p>{inline(p)}</p>
      </li>"""
        for t, p in d["how"]
    )
    faq = "\n".join(
        f"""    <div class="faq-item">
      <h3>{e(q)}</h3>
      <p>{inline(ans)}</p>
    </div>"""
        for q, ans in d["faq"]
    )
    g = d["guide"]
    meta = '<span class="sep">·</span>'.join(
        f"<span>{e(m)}</span>" for m in ["iPad & iPhone", *d["meta"]]
    )
    return (
        head(hl, d["title"], d["description"], code, "", up, INDEX_CSS)
        + nav(d, code, name, "", up, up, "nav-link", d["all_apps"])
        + f"""
  <!-- HERO -->
  <section class="hero">
    <picture>
      <source srcset="{up}images/ruhe/icons/dark/icon.png" media="(prefers-color-scheme: dark)" />
      <img src="{up}images/ruhe/icons/light/icon.png" alt="{a(d["icon_alt"])}" class="hero-icon" />
    </picture>
    <h1>Ruhe</h1>
    <p class="tagline">{e(d["tagline"])}</p>
    <a class="app-store-badge" href="{APPSTORE}" target="_blank" rel="noopener">
      <img src="{up}images/Download_on_the_App_Store_Badge_US_RGB_blk_092917.svg" alt="{a(d["badge_alt"])}" />
    </a>
    <p class="hero-meta">
      {meta}
    </p>
  </section>

  <!-- SCREENSHOTS -->
  <div class="shots">
{shots}
  </div>

  <hr class="divider" />

  <!-- FEATURES -->
  <section class="features">
    <p class="section-eyebrow">{e(d["features_eyebrow"])}</p>
    <div class="features-grid">
{features}
    </div>
  </section>

  <hr class="divider" />

  <!-- HOW -->
  <section class="how">
    <p class="section-eyebrow">{e(d["how_eyebrow"])}</p>
    <ol class="how-steps">
{how}
    </ol>
  </section>

  <hr class="divider" />

  <!-- GUIDE -->
  <section class="guides">
    <p class="section-eyebrow">{e(g["eyebrow"])}</p>
    <a class="guide-card" href="classroom-management/">
      <h3>{e(g["card_title"])}</h3>
      <p>{e(g["card_text"])}</p>
      <span class="guide-more">{e(g["more"])}</span>
    </a>
  </section>

  <hr class="divider" />

  <!-- SUPPORT -->
  <section class="faq" id="support">
    <p class="faq-eyebrow">{e(d["support_eyebrow"])}</p>
{faq}
  </section>

  <section class="final-cta">
    <p class="final-cta-title">{e(d["final_title"])}</p>
    <p class="final-cta-sub">{e(d["final_sub"])}</p>
  </section>

  <footer>
    © 2026 crabucate · <a href="mailto:info@crabucate.de">info@crabucate.de</a> · <a href="{up}en/impressum.html">{e(d["imprint"])}</a> · <a href="privacy/">{e(d["privacy"])}</a>
  </footer>
"""
        + SCRIPTS.format(up=up)
    )


def render_privacy(d: dict, code: str, hl: str, name: str) -> str:
    up = "../../../"
    p = d["privacy_page"]
    body = []
    for heading, paras in p["sections"]:
        body.append(f"    <h2>{e(heading)}</h2>")
        for para in paras:
            if isinstance(para, list):
                body.append("    <ul>" + "".join(f"<li>{inline(x)}</li>" for x in para) + "</ul>")
            else:
                body.append(f"    <p>{inline(para)}</p>")
    sections = "\n".join(body)
    return (
        head(hl, p["title"], "", code, "privacy", up, PRIVACY_CSS)
        + nav(d, code, name, "privacy", up, "../", "back-link", "← Ruhe")
        + f"""
  <main>
    <p class="page-label">{e(p["label"])}</p>
    <h1>{e(p["h1"])}</h1>
    <p class="meta">{e(p["meta"])}</p>

{sections}

    <h2>{e(p["contact_title"])}</h2>
    <p>{e(p["contact"])} <a id="priv-mail" href="#">info(at)crabucate.de</a></p>
  </main>

  <footer>
    <a href="{up}">crabucate</a> · <a href="../">Ruhe</a> · <a href="{up}en/impressum.html">{e(d["imprint"])}</a>
  </footer>

  <script>
    (function () {{
      var a = document.getElementById('priv-mail');
      a.href = 'mailto:info@crabucate.de';
      a.textContent = 'info@crabucate.de';
    }})();
  </script>
"""
        + SCRIPTS.format(up=up)
    )


GUIDE_APPS = [  # Klassen-Suffix, Name, Icon-Ordner, Ziel im Generat
    ("pw", "Platzwahl", "platzwahl", GUIDE_LINKS["platzwahl"]),
    ("tz", "Team Zufall", "team-zufall", GUIDE_LINKS["teamzufall"]),
    ("ru", "Ruhe", "ruhe", GUIDE_LINKS["ruhe"]),
]
LESSON_TOOLS = ["Platzwahl", "–", "Team Zufall", "Ruhe", "Ruhe"]


def ld(obj: dict) -> str:
    body = json.dumps(obj, ensure_ascii=False, indent=2).replace("</", "<\\/")
    return '\n  <script type="application/ld+json">\n' + body + "\n  </script>"


def render_guide(d: dict, code: str, hl: str, name: str) -> str:
    up = "../../../"
    g = d["guide"]
    page_url = url(code, "guide")
    org = {"@type": "Organization", "name": "crabucate", "url": SITE}
    extra = (
        ld({"@context": "https://schema.org", "@type": "Article", "headline": g["h1"],
            "description": g["description"], "inLanguage": hl,
            "datePublished": "2026-10-12", "dateModified": "2026-10-12",
            "author": org, "publisher": org, "mainEntityOfPage": page_url})
        + ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "crabucate", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Ruhe", "item": url(code, "")},
            {"@type": "ListItem", "position": 3, "name": g["h1"], "item": page_url}]})
        + ld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in g["faq"]]})
    )

    def blocks(items: list) -> str:
        out = []
        for item in items:
            if isinstance(item, list):
                out.append("  <ul>\n" + "\n".join(
                    f"    <li><strong>{e(t)}</strong> {inline(x, GUIDE_LINKS)}</li>" for t, x in item)
                    + "\n  </ul>")
            else:
                out.append(f"  <p>{inline(item, GUIDE_LINKS)}</p>")
        return "\n".join(out)

    shots = [
        f'  <img class="shot" src="{up}images/platzwahl/screenshots/light/en_01_perfekterSitzplan.png" alt="{a(g["shot_alts"][0])}" loading="lazy" />',
        f'  <img class="shot" src="{up}images/team-zufall/screenshots/light/marketing-03-result.png" alt="{a(g["shot_alts"][1])}" loading="lazy" />',
        f'  <img class="shot shot--phone" src="{up}images/ruhe/screenshots/{code}/02_ampel.png" width="552" height="1200" alt="{a(g["shot_alts"][2])}" loading="lazy" />',
    ]
    steps = []
    for i, st in enumerate(g["steps"]):
        part = (f'  <span class="step-label">{e(st["label"])}</span>\n'
                f'  <h2>{e(st["h"])}</h2>\n{blocks(st["body"])}')
        if 1 <= i <= 3:
            part += "\n\n" + shots[i - 1]
        steps.append(part)
    rows = "\n".join(
        f"      <tr><td>{e(ph)}</td><td>{e(what)}</td><td>{tool}</td></tr>"
        for (ph, what), tool in zip(g["lesson_rows"], LESSON_TOOLS, strict=True))
    head_cells = "".join(f"<th>{e(c)}</th>" for c in g["lesson_head"])
    cards = "\n".join(
        f"""    <a class="app-card app-card--{k}" href="{href}">
      <picture>
        <source srcset="{up}images/{folder}/icons/dark/icon.png" media="(prefers-color-scheme: dark)" />
        <img src="{up}images/{folder}/icons/light/icon.png" alt="{a(app)}" />
      </picture>
      <span class="card-name">{app}</span>
      <span class="card-role">{e(role)}</span>
      <span class="card-cta">{e(g["card_cta"])}</span>
    </a>"""
        for (k, app, folder, href), role in zip(GUIDE_APPS, g["roles"], strict=True))
    faq = "\n".join(
        f"""    <div class="faq-item">
      <h3>{e(q)}</h3>
      <p>{e(ans)}</p>
    </div>"""
        for q, ans in g["faq"])
    return (
        head(hl, g["title"], g["description"], code, "guide", up, GUIDE_CSS, extra)
        + nav(d, code, name, "guide", up, "../", "nav-link", "← Ruhe")
        + f"""
  <article>
    <p class="breadcrumb">
      <a href="{up}">crabucate</a><span>/</span><a href="../">Ruhe</a><span>/</span>{e(g["crumb"])}
    </p>

    <h1>{e(g["h1"])}</h1>
    <p class="intro">{e(g["intro"])}</p>

  <h2>{e(g["what_h"])}</h2>
{blocks(g["what"])}

{chr(10).join(s + chr(10) for s in steps)}
  <h2>{e(g["lesson_h"])}</h2>
  <table class="lesson">
    <thead>
      <tr>{head_cells}</tr>
    </thead>
    <tbody>
{rows}
    </tbody>
  </table>

  <div class="app-trio">
{cards}
  </div>

  <h2>{e(g["faq_h"])}</h2>
  <div class="faq-mini">
{faq}
  </div>

  </article>

  <footer>
    © 2026 crabucate · <a href="mailto:info@crabucate.de">info@crabucate.de</a> · <a href="{up}en/impressum.html">{e(d["imprint"])}</a>
  </footer>
"""
        + SCRIPTS.format(up=up)
    )


# ─────────────────────────────────────────────── handgeschriebene Seiten ──

def patch_handwritten() -> None:
    """Sprachwähler und hreflang-Liste der sechs DE/EN-Seiten auf den Stand von LANGS bringen."""
    for code in HANDWRITTEN:
        for page in ("", "privacy", "guide"):
            path = ROOT / rel(code, page)
            up = "../" * rel(code, page).count("/")
            text = path.read_text(encoding="utf-8")
            text, n1 = re.subn(r'<div class="lang-panel">.*?</div>',
                               lambda _: lang_panel(code, page, up), text, count=1, flags=re.S)
            text, n2 = re.subn(r'(  <link rel="alternate" hreflang="[^"]+" href="[^"]+" />\n)+',
                               lambda _: alternates(page) + "\n", text, count=1)
            assert n1 == 1 and n2 == 1, f"{path}: Sprachwähler oder hreflang nicht gefunden"
            path.write_text(text, encoding="utf-8")


SITEMAP_START = "  <!-- Ruhe, weitere Sprachen — erzeugt von notes/ruhe/build.py, nicht von Hand pflegen -->"
SITEMAP_END = "  <!-- /Ruhe, weitere Sprachen -->"


def write_sitemap() -> None:
    lines = [SITEMAP_START]
    for code, _, _ in LANGS:
        if code in HANDWRITTEN:
            continue
        for page in ("", "privacy", "guide"):
            lines += ["  <url>",
                      f"    <loc>{url(code, page)}</loc>",
                      f"    <changefreq>{'yearly' if page == 'privacy' else 'monthly'}</changefreq>",
                      f"    <priority>{ {'': '0.8', 'privacy': '0.3', 'guide': '0.7'}[page] }</priority>",
                      "  </url>"]
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
    for code, hl, name in LANGS:
        if code in HANDWRITTEN:
            continue
        d = json.loads((I18N / f"{code}.json").read_text(encoding="utf-8"))
        for page, markup in (("", render_index(d, code, hl, name)),
                             ("privacy", render_privacy(d, code, hl, name)),
                             ("guide", render_guide(d, code, hl, name))):
            target = ROOT / rel(code, page) / "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(markup, encoding="utf-8")
            written += 1
    patch_handwritten()
    write_sitemap()
    print(f"{written} Seiten unter /ruhe/ geschrieben, DE/EN-Seiten und sitemap.xml aktualisiert")


if __name__ == "__main__":
    main()
