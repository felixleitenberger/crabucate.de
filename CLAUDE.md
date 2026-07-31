# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A static website at `crabucate.de`, hosted on IONOS webhosting. There is no build step, no framework, and no dependencies — 37 hand-written HTML pages.

## Deployment

Pushing to `main` triggers `.github/workflows/deploy.yml`, which mirrors the repository to the webspace over SFTP using `lftp`. The document root is `/public`.

Credentials live in GitHub repository secrets: `IONOS_SFTP_HOST`, `IONOS_SFTP_USER`, `IONOS_SFTP_PASSWORD`.

The workflow mirrors with `--delete`, so files removed here are removed on the server. Repository-only files (`CLAUDE.md`, `app.md`, `notes/`, `og-image.html`, `.github/`, `.claude/`) are excluded — extend that list when adding files that must not be published. `notes/` holds the per-app working documents (App-Store-Checklisten, Textentwürfe, Datenschutz-Quelltexte) that must never reach the webspace.

`.htaccess` handles what GitHub Pages used to do implicitly: HTTPS enforcement, `www` → apex redirect, compression, cache headers, and `ErrorDocument 404 /404.html`.

## Structure

German pages live at the root, English mirrors under `/en/`. SEO guide pages sit in `/guides/` (9) and `/en/guides/` (8).

`lehrer-arbeitszeit.html` and `lehrer-arbeitszeit-privacy.html` are **deliberately German-only** and have no `/en/` counterpart: the app ships the Ferien- and Feiertagstermine of the sixteen German states and is useless elsewhere. Their `hreflang` therefore names only `de`, and the English start page lists two apps, not three. Do not "fix" that asymmetry by machine-translating the pages.

Images are grouped per app: `images/<app>/icons/{light,dark}/icon.png` and
`images/<app>/screenshots/{light,dark}/`. Assets both apps share — the crab logo, the two App Store
badges, the empty iPad bezel — sit directly in `images/`. Only files the site actually references
are kept; App Store deliverables and raw simulator captures were removed and are recoverable from
git history if a submission needs them.

When checking which images are still in use, read `src`/`srcset`/`url()` **attribute values**, not
a free-text pattern. Filenames have contained spaces, quotes and parentheses, and a naive pattern
silently misses them.

There is still no build step. Shared code lives in `/assets/`, page-specific code stays inline:

| Where | What |
|-------|------|
| `assets/base.css` | Design tokens, dark mode, reset, nav/footer/toggle chrome — everything that was byte-identical across pages |
| `assets/theme.js` | The theme toggle, loaded with `defer` |
| inline `<style>` | Everything specific to one page or page family (layout, hero, guide article styles) |
| inline `<script>` in `<head>` | Only the 150-byte anti-flash snippet, see below |

Link `/assets/` with **relative** paths — `assets/…` at the root, `../assets/…` under `/en/` and
`/guides/`, `../../assets/…` under `/en/guides/`. Absolute paths look fine on the server but break
when a page is opened straight from disk, which silently drops all styling and leaves default blue
links. `404.html` is the one exception and must stay absolute: Apache serves it for a request at
any depth, and the browser resolves relative URLs against the requested URL, not the error page's
location.

Load order matters: `base.css` comes before the inline `<style>`, so a page can override any shared rule simply by declaring it. That is how pages with a different `nav`, `footer`, `body` or `.nav-logo` keep their own version — those genuinely differ and were deliberately left inline.

When adding a rule, ask whether it is identical everywhere. If yes it belongs in `base.css`; if not, keep it inline. Do not move `nav`, `footer`, `.nav-logo` or `body` into `base.css` without checking all 34 pages — they have several legitimate variants.

The font stack is system-native (`-apple-system, BlinkMacSystemFont, …`), no webfonts.

DE and EN counterparts reference each other via `hreflang` and each carry a `canonical` link — keep both in sync when adding pages, and add new URLs to `sitemap.xml`.

## Design tokens (CSS custom properties)

All defined once in `assets/base.css`:

| Variable     | Light                  | Dark                   | Usage                  |
|--------------|------------------------|------------------------|------------------------|
| `--bg`       | `#FBF6EF`              | `#17120E`              | Page background        |
| `--fg`       | `#241F1A`              | `#F3ECE3`              | Body text              |
| `--accent`   | `#B04D1C`              | `#E98544`              | Highlights, links      |
| `--muted`    | `#6B6358`              | `#A3998B`              | Secondary text         |
| `--line`     | `rgba(176,77,28,0.15)` | `rgba(233,133,68,0.22)`| Dividers               |
| `--card-bg`  | `#FFFFFF`              | `#211A15`              | Cards                  |
| `--nav-bg`   | `rgba(251,246,239,0.85)`| `rgba(23,18,14,0.85)` | Sticky nav backdrop    |
| `--prose`    | `#4A443C`              | `#CAC0B2`              | Guide body copy        |
| `--tz`       | `#F07D4A`              | unchanged              | Team Zufall accent     |
| `--tz-text`  | `#B8481A`              | `#F2925E`              | Team Zufall text       |
| `--pw`       | `#F5923A`              | unchanged              | Platzwahl accent       |
| `--pw-text`  | `#9C570D`              | `#F0A65B`              | Platzwahl text         |
| `--la`       | `#F79D39`              | unchanged              | Lehrer-Arbeitszeit accent |
| `--la-text`  | `#8F4F0E`              | `#F5B06A`              | Lehrer-Arbeitszeit text |

`lehrer-arbeitszeit.html` declares five further tokens in its own inline `:root` — `--frame-a/-b/-c`
and `--frame-rim` for the CSS iPhone mockup, plus `--soll`, `--ist` and `--over` for the
Jahresarbeitszeit calculator. They are page-local on purpose (nothing else uses them) but repeat the
dual-block pattern from `base.css`: media query first, `:root[data-theme="dark"]` second. The
calculator reads `--ist`/`--over` back out via `getComputedStyle` to build the two-tone bar, so those
two must stay resolvable custom properties — inlining the colours in the JS would break the toggle.

That page also renders its screenshots without a bezel image: the frame is pure CSS on `.phone`, and
the pill over the status bar (`.phone-island`) is positioned in percent so it scales with the
mockup. The screenshots themselves are raw simulator captures at 828 px (iPhone) and 1600 px (iPad)
width, run through `pngquant`; the whole app folder is ~1.2 MB.

Guide pages add three aliases in their own inline `:root`, pointing at whichever app that guide
belongs to — `--app: var(--pw); --app-text: var(--pw-text); --app-dim: var(--pw-dim);` (or the
`--tz` trio). They must stay `var()` references, never literal colours: the dark overrides apply to
`--pw-text`, so a hardcoded `--app-text` would silently keep its light value in dark mode.

## Dark mode

Follows the OS by default; the nav toggle cycles between auto, light and dark and persists an
explicit choice in `localStorage.theme` (no entry means auto). All of it lives in `assets/base.css`
and `assets/theme.js` — a new page needs nothing beyond the `<link>`, the `<script>`, the head
snippet and the button markup.

`base.css` carries the dark tokens twice on purpose:

```css
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { …tokens… } }
:root[data-theme="dark"] { …tokens… }
```

The media query serves the automatic case, the attribute selector the manual one. Both have
specificity (0,2,0), so source order decides and the manual block must stay second.

The `<html>` element gets `data-theme` from a blocking inline script in `<head>`. That snippet
stays inline deliberately: an external file would only run after a round-trip and the page would
flash the wrong theme until then. It also sets `class="js"`, which is what reveals the button —
without JavaScript it stays hidden and the media query alone still gives automatic dark mode.

The cycle order depends on the system theme so the first click always changes something visible.
With a light system it runs auto → dark → light → auto; with a dark system auto → light → dark →
auto. A fixed order would make `auto → light` a no-op on a light system and the button would seem
to need two clicks.

`theme.js` recognises the dark source by the `/dark/` segment of its path, so icon files must stay
inside their `light/` and `dark/` folders — renaming those folders breaks the toggle silently.

The app icons carry their own rounded corners with transparent outside, and their curve is rounder
than the `border-radius` the CSS clips them with — so never put a `background` behind an icon
element. It shows up as a coloured crescent along the edge, which is what `.tile-icon--tz` and the
Team Zufall `.hero-icon` used to do. Icon elements get no background and no glow, on either app.

Three things do not come from tokens. The app icons swap via `<picture>` + `<source media="(prefers-color-scheme: dark)">`
(`images/<app>/icons/light/icon.png` / `.../dark/icon.png`), the black Apple badge is flipped to the white one with
`img[src*="App_Store_Badge"] { filter: invert(1); }`, and both of those plus the `theme-color`
metas are media-query driven — so the toggle script rewrites their `media` attributes to
`all` / `not all` when a manual choice is active. A new `<picture>` or `theme-color` needs no
extra wiring; the script finds them by selector.

Box-shadows keep their light values on purpose — at 5–16 % alpha they simply fade out on dark,
where `--card-bg` and `--line` carry the elevation instead.

Headless Chrome cannot emulate `prefers-color-scheme` (`--force-prefers-color-scheme` is a no-op).
To screenshot dark mode, copy the site and swap `light` ↔ `dark` in the media queries.
