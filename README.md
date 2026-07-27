# Hack Club Build Hub

A reusable teaching library for Hack Club hackathons, clubs, and events Ã¢â‚¬â€
hands-on workshop tracks, an electronics knowledge base, and a future feed of
community builds.

Static site, no framework, no build step required to view it.

## Pages

| File | What it is |
|---|---|
| `index.html` | Homepage Ã¢â‚¬â€ mission, workshop cards, reference sections, search |
| `learn.html` | Docs viewer Ã¢â‚¬â€ sidebar nav, all workshops + guides, full-text search |
| `videos.html` | Build finder - ranked Build Hub/wiki results |
| `media.html` | Asset library Ã¢â‚¬â€ searchable grid of every image, GIF, PDF and video in the repo |
| `MOOD_BOARD.html` | The design language reference (open in a browser) |
| `index-template.html` | Component demo page from the design system |

## Content

All workshop and reference content lives as plain markdown in `content/docs/`.
The viewer reads it from `content/content.js`, which is generated:

```bash
python tools/build_content.py
```

**Edit the markdown, rerun the script, refresh the page.** Don't edit
`content/content.js` by hand.

The same script builds the media index behind `media.html` Ã¢â‚¬â€ every image, GIF,
PDF and embedded video the pages reference, plus the files sitting in
`content/docs/assets/` that nothing links to yet. It prints a warning for any
reference pointing at a file that isn't in the repo.

Front matter follows the just-the-docs conventions the content already uses
(`title`, `parent`, `nav_order`), and callouts like `{: .tip }` / `{: .warning }`
above a blockquote render as styled callout boxes.

## Build finder (`videos.html`)

The finder searches every generated workshop and wiki page locally. Results are
ranked using title, section, exact-phrase and keyword matches. No API key or
special server is required.

## Design

- `design-tokens.css` Ã¢â‚¬â€ colors, typography, spacing, core components
- `site.css` Ã¢â‚¬â€ site chrome (topbar, sidebar, rendered-markdown styles, callouts)
- `DESIGN_SYSTEM.md` / `DESIGN_GUIDE.md` Ã¢â‚¬â€ the written spec

The visual direction follows Hack Club's brand: bold red, clean white surfaces,
dark readable text, playful supporting colors, and practical electronics motifs.

## Local preview

Open `index.html` or serve the folder with any basic local web server, then
visit `videos.html` for the Build Hub and wiki finder.
