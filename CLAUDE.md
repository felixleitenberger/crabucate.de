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

| Variable     | Value                  | Usage                  |
|--------------|------------------------|------------------------|
| `--bg`       | `#FBF6EF`              | Page background        |
| `--fg`       | `#241F1A`              | Body text              |
| `--accent`   | `#B04D1C`              | Highlights, links      |
| `--muted`    | `#6B6358`              | Secondary text         |
| `--line`     | `rgba(176,77,28,0.15)` | Dividers               |
| `--card-bg`  | `#FFFFFF`              | Cards                  |
| `--tz`       | `#F07D4A`              | Team Zufall accent     |
| `--tz-text`  | `#B8481A`              | Team Zufall text       |
| `--pw`       | `#F5923A`              | Platzwahl accent       |
| `--pw-text`  | `#9C570D`              | Platzwahl text         |
