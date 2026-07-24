# MakerLabs Info Hub

The UCD ElecSoc MakerLabs website — lab guides, the maker wiki, and (soon) a
live feed of community builds from YouTube, Instagram and TikTok.

Static site, no framework, no build step required to view it.

## Pages

| File | What it is |
|---|---|
| `index.html` | Homepage — mission, lab cards, wiki sections, search |
| `learn.html` | Docs viewer — sidebar nav, all labs + wiki, full-text search |
| `MOOD_BOARD.html` | The design language reference (open in a browser) |
| `index-template.html` | Component demo page from the design system |

## Content

All lab and wiki content lives as plain markdown in `content/docs/`
(imported from [UCDElecSoc/MakerLabs26](https://github.com/UCDElecSoc/MakerLabs26)).
The viewer reads it from `content/content.js`, which is generated:

```bash
python tools/build_content.py
```

**Edit the markdown, rerun the script, refresh the page.** Don't edit
`content/content.js` by hand.

Front matter follows the just-the-docs conventions the content already uses
(`title`, `parent`, `nav_order`), and callouts like `{: .tip }` / `{: .warning }`
above a blockquote render as styled callout boxes.

## Design

- `design-tokens.css` — colors, typography, spacing, core components
- `site.css` — site chrome (topbar, sidebar, rendered-markdown styles, callouts)
- `DESIGN_SYSTEM.md` / `DESIGN_GUIDE.md` — the written spec

The vibe in one line: light paper, teal ink, mint accent, one signal-orange
highlight per view, and quiet PCB motifs (traces, pin headers, silkscreen
labels) instead of neon.

## Local preview

Just open `index.html` in a browser — everything works from `file://`.
(Markdown rendering uses marked.js from a CDN, so you need to be online.)
