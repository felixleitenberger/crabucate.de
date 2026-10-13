#!/usr/bin/env python3
"""Erzeugt die vierzig Seiten unter /bestiary/ aus den Sprachdateien in i18n/.

Die Seite hat weiterhin keinen Build-Schritt: Das Ergebnis dieses Skripts wird
eingecheckt und ausgeliefert. Das Skript liegt unter notes/ und geht deshalb
nicht auf den Webspace. Es existiert, weil vier Seiten in zehn Sprachen
vierzig Dateien sind, die sich bis auf die Texte gleichen — von Hand gepflegt
laufen die auseinander.

    python3 notes/bestiary/build.py
"""

from __future__ import annotations

import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
I18N = pathlib.Path(__file__).resolve().parent / "i18n"
OUT = ROOT / "bestiary"

SITE = "https://crabucate.de"
APPSTORE = "https://apps.apple.com/app/id6808938974"

# Kennung, hreflang, og:locale, Name im Sprachwähler, Pfadstück unter /bestiary/.
# Englisch liegt direkt auf /bestiary/, weil App Store Connect genau diese vier
# Adressen kennt und die Review sie in ihrer eigenen Sprache nicht findet.
LANGS = [
    ("en",      "en",      "en_US", "English",     ""),
    ("de",      "de",      "de_DE", "Deutsch",     "de"),
    ("fr",      "fr",      "fr_FR", "Français",    "fr"),
    ("es",      "es",      "es_ES", "Español",     "es"),
    ("it",      "it",      "it_IT", "Italiano",    "it"),
    ("pt-br",   "pt-BR",   "pt_BR", "Português",   "pt-br"),
    ("ja",      "ja",      "ja_JP", "日本語",       "ja"),
    ("ko",      "ko",      "ko_KR", "한국어",       "ko"),
    ("zh-hans", "zh-Hans", "zh_CN", "简体中文",     "zh-hans"),
    ("zh-hant", "zh-Hant", "zh_TW", "繁體中文",     "zh-hant"),
]

SHOTS = ["01_today", "02_collection", "03_card_front", "04_card_back", "05_quiz"]


def e(text: str) -> str:
    return html.escape(text, quote=False)


def url_for(lang: str, page: str) -> str:
    """Absolute Adresse einer Seite. page ist '' | 'privacy' | 'terms' | 'support'."""
    parts = ["bestiary"]
    prefix = dict((code, path) for code, _, _, _, path in LANGS)[lang]
    if prefix:
        parts.append(prefix)
    if page:
        parts.append(page)
    return f"{SITE}/" + "/".join(parts) + "/"


def out_path(lang: str, page: str) -> pathlib.Path:
    prefix = dict((code, path) for code, _, _, _, path in LANGS)[lang]
    p = OUT
    if prefix:
        p = p / prefix
    if page:
        p = p / page
    return p / "index.html"


def depth(lang: str, page: str) -> int:
    """Wie viele Verzeichnisse zwischen der Datei und dem Wurzelverzeichnis liegen."""
    prefix = dict((code, path) for code, _, _, _, path in LANGS)[lang]
    return 1 + (1 if prefix else 0) + (1 if page else 0)


# ─────────────────────────────────────────────────────────────── Bausteine ──

THEME_SNIPPET = (
    "<script>(function(){var d=document.documentElement,t;try{t=localStorage.getItem('theme')}"
    "catch(e){}if(t==='light'||t==='dark')d.dataset.theme=t;d.className+=' js'})();</script>"
)

GLOBE = ('<svg class="lang-globe" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
         'stroke-width="1.7" aria-hidden="true"><circle cx="12" cy="12" r="9"/>'
         '<path d="M3.5 9h17M3.5 15h17M12 3a15 15 0 0 1 0 18a15 15 0 0 1 0-18z"/></svg>')
CARET = ('<svg class="lang-caret" viewBox="0 0 12 12" fill="none" stroke="currentColor" '
         'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
         '<path d="M2 4.5 6 8.5l4-4"/></svg>')
CHECK = ('<svg class="lang-check" viewBox="0 0 12 12" fill="none" stroke="currentColor" '
         'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
         '<path d="M1.5 6.5 4.5 9.5 10.5 3"/></svg>')

TOGGLE = """<button class="theme-toggle" type="button" title="Theme" aria-label="Theme">
        <svg class="ico-auto" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor" stroke="none"/></svg>
        <svg class="ico-light" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M18.7 5.3l-1.4 1.4M6.7 17.3l-1.4 1.4"/></svg>
        <svg class="ico-dark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z"/></svg>
      </button>"""

CHROME_CSS = """
    /* Die Farben der App (--db, --db-text, --db-dim) stehen in base.css bei
       denen der anderen drei Apps — die Startseite braucht sie fuer ihre
       Kachel genauso. Hier steht nur, was diese Seitenfamilie ausmacht. */
    body {
      background: var(--bg);
      color: var(--fg);
      font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Arial, sans-serif;
      overflow-x: hidden;
    }

    nav {
      position: fixed;
      top: 0; left: 0; right: 0;
      z-index: 100;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 1.2rem clamp(1.5rem, 6vw, 5rem);
      background: var(--nav-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--line);
    }

    .nav-logo {
      display: flex;
      align-items: center;
      gap: 0.6rem;
      font-weight: 700;
      font-size: 1.1rem;
      color: var(--fg);
      text-decoration: none;
      letter-spacing: -0.01em;
    }

    .nav-logo img {
      width: 30px;
      height: 30px;
      border-radius: 7px;
      object-fit: cover;
      flex-shrink: 0;
    }

    .back-link {
      font-size: 0.8rem;
      color: var(--muted);
      text-decoration: none;
      display: flex;
      align-items: center;
      gap: 0.4rem;
      transition: color 0.2s;
    }

    .back-link:hover { color: var(--fg); }

    footer {
      text-align: center;
      padding: 3rem 1.5rem 3.5rem;
      font-size: 0.8rem;
      color: var(--muted);
      border-top: 1px solid var(--line);
      position: relative;
      z-index: 1;
    }

    .foot-links { line-height: 2; }
    .foot-sep { opacity: 0.35; margin: 0 0.15rem; }

"""

PROSE_CSS = """
    main {
      padding: calc(60px + 5rem) clamp(1.5rem, 9vw, 9rem) 6rem;
      max-width: 760px;
      margin: 0 auto;
      position: relative;
      z-index: 1;
    }

    .page-label {
      font-size: 0.72rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--db-text);
      margin-bottom: 1rem;
    }

    h1 {
      font-size: clamp(1.8rem, 4vw, 2.8rem);
      font-weight: 800;
      letter-spacing: -0.03em;
      color: var(--fg);
      margin-bottom: 0.5rem;
    }

    .meta {
      font-size: 0.8rem;
      color: var(--muted);
      margin-bottom: 3.5rem;
    }

    h2 {
      font-size: 1rem;
      font-weight: 600;
      color: var(--fg);
      margin-top: 2.5rem;
      margin-bottom: 0.6rem;
    }

    h3 {
      font-size: 0.9rem;
      font-weight: 600;
      color: var(--fg);
      margin-top: 1.5rem;
      margin-bottom: 0.4rem;
    }

    p { font-size: 0.875rem; line-height: 1.9; color: var(--muted); margin-bottom: 0.75rem; }
    ul, ol { margin: 0 0 0.75rem 1.1rem; padding: 0; }
    li { font-size: 0.875rem; line-height: 1.9; color: var(--muted); margin-bottom: 0.2rem; }

    .address {
      font-size: 0.875rem;
      line-height: 1.9;
      color: var(--muted);
      border-left: 2px solid var(--line);
      padding-left: 1.1rem;
      margin-bottom: 0.75rem;
    }

    a { color: var(--db-text); text-decoration: none; border-bottom: 1px solid transparent; transition: border-color 0.2s; }
    a:hover { border-color: currentColor; }
    .nav-logo, .back-link, .foot-links a { border-bottom: 0; }
"""

INDEX_CSS = """
    /* Das Grundgeruest (Buehne, Leiste, Features, FAQ) kommt aus
       assets/app.css. Hier steht nur, was Bestiary anders macht. */
    :root { --app: var(--db); --app-text: var(--db-text); --app-dim: var(--db-dim); }

    main { position: relative; z-index: 1; }

    .shots figure { flex: 0 0 auto; width: clamp(200px, 21vw, 240px); scroll-snap-align: center; }
    .shots figure img { width: 100%; }
    .shots figcaption { margin-top: 0.9rem; font-size: 0.82rem; line-height: 1.5; color: var(--muted); text-align: center; text-wrap: balance; }

    /* Collector, Datenschutz, Bildnachweise: Pflichtangaben, ruhig gesetzt */
    .fine { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 2rem 2.5rem; }
    .fine h3 { font-size: 1.02rem; font-weight: 650; letter-spacing: -0.01em; margin-bottom: 0.6rem; }
    .fine p { font-size: 0.86rem; line-height: 1.65; color: var(--muted); margin-bottom: 0.7rem; }
    .fine > div { border-top: 1px solid var(--line); padding-top: 1.4rem; }
    .legal-row { display: flex; flex-wrap: wrap; gap: 0.4rem 1.1rem; margin-top: 0.4rem; }
    .legal-row a { font-size: 0.86rem; font-weight: 600; color: var(--app-text); text-decoration: none; }
    .legal-row a:hover { text-decoration: underline; }
    @media (max-width: 860px) { .fine { grid-template-columns: 1fr; } }
"""


def head(lang_code: str, hreflang: str, locale: str, title: str, description: str,
         canonical: str, up: str, extra_css: str, robots: str = "index, follow",
         app_css: bool = False) -> str:
    alts = "\n".join(
        f'  <link rel="alternate" hreflang="{hl}" href="{url_for(code, PAGE_OF[canonical])}" />'
        for code, hl, _, _, _ in LANGS
    )
    return f"""<!DOCTYPE html>
<html lang="{hreflang}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  {THEME_SNIPPET}
  <meta name="color-scheme" content="light dark" />
  <meta name="theme-color" content="#FBF6EF" media="(prefers-color-scheme: light)" />
  <meta name="theme-color" content="#17120E" media="(prefers-color-scheme: dark)" />
  <title>{e(title)}</title>
  <meta name="description" content="{html.escape(description)}" />
  <link rel="canonical" href="{canonical}" />
{alts}
  <link rel="alternate" hreflang="x-default" href="{url_for('en', PAGE_OF[canonical])}" />
  <meta name="robots" content="{robots}" />

  <meta property="og:type" content="website" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:title" content="{html.escape(title)}" />
  <meta property="og:description" content="{html.escape(description)}" />
  <meta property="og:locale" content="{locale}" />

  <link rel="stylesheet" href="{up}assets/base.css" />{f'''
  <link rel="stylesheet" href="{up}assets/app.css" />''' if app_css else ""}
  <style>
{extra_css}  </style>
</head>
<body>
"""


PAGE_OF: dict[str, str] = {}

_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
        'stroke-linecap="round" stroke-linejoin="round">{}</svg>')
FEATURE_ICONS = [_SVG.format(x) for x in (
    '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4"/>',
    '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="10" r="1.6"/><path d="M21 16l-5-5-8 8"/>',
    '<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.7.3-1 .9-1 1.7M12 17h.01"/>',
    '<rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="9" rx="1.5"/><rect x="3" y="15" width="7" height="6" rx="1.5"/><rect x="14" y="15" width="7" height="6" rx="1.5"/>',
    '<path d="M12 3l2.4 5.2 5.6.6-4.2 3.8 1.2 5.6L12 15.4 7 18.2l1.2-5.6L4 8.8l5.6-.6z"/>',
)]


def lang_menu(data: dict, lang: str, page: str, up: str) -> str:
    """Der Sprachwaehler oben rechts, mit allen zehn Sprachen dieser Seite.

    Die Adressen zeigen jeweils auf dieselbe Seite in der anderen Sprache, nicht
    auf deren Startseite: Wer die Datenschutzerklaerung auf Koreanisch sucht,
    landet auf der koreanischen Datenschutzerklaerung.
    """
    label = e(data["common"]["language_choose"])
    own = dict((code, name) for code, _, _, name, _ in LANGS)[lang]

    items = []
    for code, hreflang, _, name, prefix in LANGS:
        if code == lang:
            items.append(f'          <span class="lang-item lang-item--active" '
                         f'aria-current="true">{CHECK}{e(name)}</span>')
        else:
            target = f"{up}bestiary/" + (f"{prefix}/" if prefix else "") + (f"{page}/" if page else "")
            items.append(f'          <a class="lang-item" hreflang="{hreflang}" lang="{hreflang}" '
                         f'href="{target}">{CHECK}{e(name)}</a>')

    return (f'      <details class="lang-menu">\n'
            f'        <summary aria-label="{label}" title="{label}">'
            f'{GLOBE}<span class="lang-current">{e(own)}</span>{CARET}</summary>\n'
            f'        <div class="lang-panel">\n'
            + "\n".join(items) + "\n"
            f'        </div>\n'
            f'      </details>')


def nav(up: str, back_href: str, back_label: str, menu: str) -> str:
    return f"""
  <nav>
    <a href="{up}" class="nav-logo">
      <img src="{up}images/crabucateSquare.jpg" alt="" />
      crabucate
    </a>
    <div class="nav-right">
      <a href="{back_href}" class="back-link">{back_label}</a>
{menu}
      {TOGGLE}
    </div>
  </nav>
"""


def footer(data: dict, lang: str, page: str, up: str) -> str:
    c = data["common"]
    app_root = "../" * (depth(lang, page) - depth(lang, "")) or "./"
    imprint = f"{up}impressum.html" if lang == "de" else f"{up}en/impressum.html"

    links = []
    links.append(f'<a href="{up}">crabucate</a>')
    if page:
        links.append(f'<a href="{app_root}">Daily Bestiary</a>')
    for slug, key in (("privacy", "privacy"), ("terms", "terms"), ("support", "support")):
        if slug == page:
            links.append(f'<span>{e(c["nav_" + key])}</span>')
        else:
            links.append(f'<a href="{app_root}{slug}/">{e(c["nav_" + key])}</a>')
    links.append(f'<a href="{imprint}">{e(c["imprint"])}</a>')

    sep = '<span class="foot-sep">·</span>'
    return f"""
  <footer>
    <div class="foot-links">{sep.join(links)}</div>
  </footer>

  <script src="{up}assets/theme.js" defer></script>
  <script src="{up}assets/lang.js" defer></script>
</body>
</html>
"""


MAIL_SCRIPT = """
  <script>
    (function () {
      var boxes = document.querySelectorAll('.mail');
      for (var i = 0; i < boxes.length; i++) {
        var a = boxes[i];
        a.href = 'mailto:' + 'info' + '@' + 'crabucate.de';
        a.textContent = 'info' + '@' + 'crabucate.de';
      }
    })();
  </script>
"""

MAIL_LINK = '<a class="mail" href="#">info(at)crabucate.de</a>'


def blocks(items: list) -> str:
    """Rendert die Textbausteine einer Rechtsseite."""
    out = []
    for block in items:
        if "h3" in block:
            out.append(f'      <h3>{e(block["h3"])}</h3>')
        elif "p" in block:
            out.append(f'      <p>{block["p"]}</p>')
        elif "ul" in block:
            lis = "\n".join(f"        <li>{x}</li>" for x in block["ul"])
            out.append(f"      <ul>\n{lis}\n      </ul>")
        elif "ol" in block:
            lis = "\n".join(f"        <li>{x}</li>" for x in block["ol"])
            out.append(f"      <ol>\n{lis}\n      </ol>")
        elif "address" in block:
            out.append(f'      <p class="address">{block["address"]}</p>')
        else:
            raise ValueError(f"Unbekannter Baustein: {block!r}")
    return "\n".join(out)


# ───────────────────────────────────────────────────────────────── Seiten ──

def render_prose(data: dict, lang: str, hreflang: str, locale: str, page: str) -> str:
    d = data[page]
    c = data["common"]
    up = "../" * depth(lang, page)
    canonical = url_for(lang, page)
    PAGE_OF[canonical] = page
    app_root = "../"

    body = [
        head(lang, hreflang, locale, d["title"], d["description"], canonical, up,
             CHROME_CSS + PROSE_CSS, robots=d.get("robots", "index, follow")),
        nav(up, app_root, "← Daily Bestiary", lang_menu(data, lang, page, up)),
        "\n  <main>",
        f'    <p class="page-label">{e(d["label"])}</p>',
        f'    <h1>{e(d["h1"])}</h1>',
        f'    <p class="meta">Daily Bestiary · {e(c["updated"])}</p>',
    ]
    for section in d["sections"]:
        body.append(f'\n      <h2>{e(section["h"])}</h2>')
        body.append(blocks(section["blocks"]))
    body.append("  </main>")
    body.append(MAIL_SCRIPT)
    body.append(footer(data, lang, page, up))
    return "\n".join(body)


def render_index(data: dict, lang: str, hreflang: str, locale: str) -> str:
    d = data["index"]
    c = data["common"]
    up = "../" * depth(lang, "")
    canonical = url_for(lang, "")
    PAGE_OF[canonical] = ""
    shots_dir = f"{up}images/bestiary/screenshots/{lang}/"
    badge = "Download_on_the_App_Store_Badge_DE_RGB_blk_092917.svg" if lang == "de" \
        else "Download_on_the_App_Store_Badge_US_RGB_blk_092917.svg"

    app_ld = {
        "@context": "https://schema.org",
        "@type": "MobileApplication",
        "name": "Daily Bestiary",
        "operatingSystem": "iOS",
        "applicationCategory": "EducationApplication",
        "description": d["description"],
        "inLanguage": hreflang,
        "url": APPSTORE,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
        "author": {"@type": "Organization", "name": "crabucate", "url": SITE},
    }
    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "inLanguage": hreflang,
        "mainEntity": [
            {"@type": "Question", "name": q["q"],
             "acceptedAnswer": {"@type": "Answer", "text": q["a"]}}
            for q in d["faq"]
        ],
    }

    features = "\n".join(
        f'          <div class="feat">\n            <div class="feat-icon">{icon}</div>\n'
        f'            <h3>{e(f["t"])}</h3>\n            <p>{f["d"]}</p>\n          </div>'
        for icon, f in zip(FEATURE_ICONS, d["features"], strict=True)
    )
    shots = "\n".join(
        f'        <figure>\n'
        f'          <img src="{shots_dir}{name}.png" width="405" height="880" loading="lazy" '
        f'alt="{html.escape(cap)}" />\n'
        f'          <figcaption>{e(cap)}</figcaption>\n        </figure>'
        for name, cap in zip(SHOTS, d["shots"])
    )
    faq = "\n".join(
        f'        <details class="qa"><summary><h3>{e(q["q"])}</h3></summary>\n'
        f'          <p>{q["a"]}</p></details>'
        for q in d["faq"]
    )

    def paras(key):
        return "\n".join(f"          <p>{p}</p>" for p in d[key])

    badge_link = (f'<a class="app-store-badge" href="{APPSTORE}"><img src="{up}images/{badge}" '
                  f'alt="{html.escape(d["badge_alt"])}" /></a>')

    parts = [
        head(lang, hreflang, locale, d["title"], d["description"], canonical, up,
             CHROME_CSS + INDEX_CSS, app_css=True),
        f'  <script type="application/ld+json">\n{json.dumps(app_ld, ensure_ascii=False, indent=2)}\n  </script>',
        f'  <script type="application/ld+json">\n{json.dumps(faq_ld, ensure_ascii=False, indent=2)}\n  </script>',
        nav(up, f"{up}", f'← {e(c["all_apps"])}', lang_menu(data, lang, "", up)),
        "\n  <main>",
        '    <section class="stage">',
        '      <div class="stage-inner">',
        '        <div class="stage-copy">',
        f'          <img class="stage-icon" src="{up}images/bestiary/icon.png" width="108" height="108" alt="Daily Bestiary" />',
        "          <h1>Daily Bestiary</h1>",
        f'          <p class="tagline">{e(d["tagline"])}</p>',
        '          <div class="stage-cta">',
        f'            {badge_link}',
        f'            <ul class="hero-meta"><li>{e(d["eyebrow"])}</li></ul>',
        "          </div>",
        "        </div>",
        '        <div class="stage-art">',
        f'          <img src="{up}images/bestiary/hero/{lang}.webp" width="2560" height="1800" alt="{html.escape(d["shots"][2])}" />',
        "        </div>",
        "      </div>",
        "    </section>",

        f'    <div class="shots" aria-label="{html.escape(d["shots_title"])}">\n{shots}\n    </div>',

        '    <section class="sec">',
        f'      <h2 class="sec-title">{e(d["features_title"])}</h2>',
        f'      <div class="feats">\n{features}\n      </div>',
        "    </section>",

        '    <section class="sec">',
        '      <div class="fine">',
        '        <div>',
        f'          <h3>{e(d["collector_title"])}</h3>',
        paras("collector"),
        "        </div>",
        '        <div>',
        f'          <h3>{e(d["privacy_title"])}</h3>',
        paras("privacy"),
        '          <div class="legal-row">',
        f'            <a href="privacy/">{e(c["nav_privacy"])}</a>',
        f'            <a href="terms/">{e(c["nav_terms"])}</a>',
        f'            <a href="support/">{e(c["nav_support"])}</a>',
        "          </div>",
        "        </div>",
        '        <div>',
        f'          <h3>{e(d["credits_title"])}</h3>',
        paras("credits"),
        "        </div>",
        "      </div>",
        "    </section>",

        '    <section class="sec faq">',
        f'      <h2 class="sec-title">{e(d["faq_title"])}</h2>',
        faq,
        "    </section>",

        '    <section class="closing">',
        f'      <img class="closing-icon" src="{up}images/bestiary/icon.png" width="108" height="108" alt="" loading="lazy" />',
        f'      <h2>{e(d["tagline"])}</h2>',
        f'      {badge_link}',
        "    </section>",
        "  </main>",
        MAIL_SCRIPT,
        footer(data, lang, "", up),
    ]
    return "\n".join(parts)


SITEMAP_START = "  <!-- Daily Bestiary — erzeugt von notes/bestiary/build.py, nicht von Hand pflegen -->"
SITEMAP_END = "  <!-- /Daily Bestiary -->"


def write_sitemap() -> None:
    """Ersetzt den Bestiary-Block in sitemap.xml.

    Anders als bei den uebrigen Eintraegen stehen hier keine
    `xhtml:link`-Alternativen: bei zehn Sprachen waeren das 440 Zeilen fuer
    eine Angabe, die in jeder der vierzig Seiten ohnehin im `<head>` steht.
    """
    lines = [SITEMAP_START]
    for code, _, _, _, _ in LANGS:
        for page in ("", "privacy", "terms", "support"):
            priority = "0.9" if not page else "0.3"
            freq = "monthly" if not page else "yearly"
            lines.append("  <url>")
            lines.append(f"    <loc>{url_for(code, page)}</loc>")
            lines.append(f"    <changefreq>{freq}</changefreq>")
            lines.append(f"    <priority>{priority}</priority>")
            lines.append("  </url>")
    lines.append(SITEMAP_END)

    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    if SITEMAP_START in text:
        head, rest = text.split(SITEMAP_START, 1)
        _, tail = rest.split(SITEMAP_END, 1)
        text = head + "\n".join(lines) + tail
    else:
        text = text.replace("\n</urlset>", "\n\n" + "\n".join(lines) + "\n\n</urlset>")
    path.write_text(text, encoding="utf-8")


def main() -> None:
    # Erst alle Adressen bekannt machen, damit die hreflang-Liste vollständig ist.
    for code, _, _, _, _ in LANGS:
        for page in ("", "privacy", "terms", "support"):
            PAGE_OF[url_for(code, page)] = page

    written = 0
    for code, hreflang, locale, _, _ in LANGS:
        path = I18N / f"{code}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        pages = {
            "": render_index(data, code, hreflang, locale),
            "privacy": render_prose(data, code, hreflang, locale, "privacy"),
            "terms": render_prose(data, code, hreflang, locale, "terms"),
            "support": render_prose(data, code, hreflang, locale, "support"),
        }
        for page, markup in pages.items():
            # Die Adresse steht nirgends im Quelltext als zusammenhaengende
            # Zeichenkette; das Skript am Seitenende setzt sie erst im Browser
            # zusammen. Das haelt sie aus den einfachen Sammlern heraus.
            markup = markup.replace("__MAIL__", MAIL_LINK)
            target = out_path(code, page)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(markup, encoding="utf-8")
            written += 1
    write_sitemap()
    print(f"{written} Seiten geschrieben nach {OUT}, sitemap.xml aktualisiert")


if __name__ == "__main__":
    main()
