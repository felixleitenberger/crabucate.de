# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A static single-page website hosted on GitHub Pages at `crabucate.de`. There is no build step, no framework, and no dependencies — just `index.html`.

## Deployment

Pushing to `main` deploys automatically via GitHub Pages. The `CNAME` file points the custom domain to `crabucate.de`.

## Structure

Everything lives in `index.html`: CSS (in `<style>`), HTML, and any JavaScript. Fonts are loaded from Google Fonts (Playfair Display + IBM Plex Mono).

## Design tokens (CSS custom properties)

| Variable   | Value                  | Usage            |
|------------|------------------------|------------------|
| `--bg`     | `#0d0d0d`              | Page background  |
| `--fg`     | `#f0ece2`              | Body text        |
| `--accent` | `#c8b89a`              | Highlights, links |
| `--muted`  | `#5a5650`              | Secondary text   |
| `--line`   | `rgba(200,184,154,0.2)`| Dividers         |

