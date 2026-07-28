# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A static website at `crabucate.de`, hosted on IONOS webhosting. There is no build step, no framework, and no dependencies — 35 hand-written HTML pages.

## Deployment

Pushing to `main` triggers `.github/workflows/deploy.yml`, which mirrors the repository to the webspace over SFTP using `lftp`. The document root is `/public`.

Credentials live in GitHub repository secrets: `IONOS_SFTP_HOST`, `IONOS_SFTP_USER`, `IONOS_SFTP_PASSWORD`.

The workflow mirrors with `--delete`, so files removed here are removed on the server. Repository-only files (`CLAUDE.md`, `app.md`, `og-image.html`, `.github/`, `.claude/`) are excluded — extend that list when adding files that must not be published.

`.htaccess` handles what GitHub Pages used to do implicitly: HTTPS enforcement, `www` → apex redirect, compression, cache headers, and `ErrorDocument 404 /404.html`.

## Structure

German pages live at the root, English mirrors under `/en/`. SEO guide pages sit in `/guides/` (9) and `/en/guides/` (8). Images are in `/images/`.

Each page is fully self-contained: CSS in an inline `<style>` block, no shared stylesheet, no webfonts. Changing a shared visual detail means touching every page. The font stack is system-native (`-apple-system, BlinkMacSystemFont, …`).

DE and EN counterparts reference each other via `hreflang` and each carry a `canonical` link — keep both in sync when adding pages, and add new URLs to `sitemap.xml`.

## Design tokens (CSS custom properties)

Repeated identically in every page's `:root`:

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

Guide pages use `--app` / `--app-text` / `--app-dim` instead of the `--tz`/`--pw` pairs,
carrying whichever app's colours that guide belongs to.

## Dark mode

Automatic via `@media (prefers-color-scheme: dark)` — no toggle, no JavaScript. Each page
carries its own dark block directly after `:root`, overriding only the tokens above. Adding a
page means adding that block too; everything else follows from the tokens.

Two things do not come from tokens: the app icons swap via `<picture>` + `<source media="(prefers-color-scheme: dark)">`
(`images/*-icon.png` / `*-icon-dark.png`), and the black Apple badge is flipped to the white one
with `img[src*="App_Store_Badge"] { filter: invert(1); }`.

Box-shadows keep their light values on purpose — at 5–16 % alpha they simply fade out on dark,
where `--card-bg` and `--line` carry the elevation instead.

Headless Chrome cannot emulate `prefers-color-scheme` (`--force-prefers-color-scheme` is a no-op).
To screenshot dark mode, copy the site and swap `light` ↔ `dark` in the media queries.
