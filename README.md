# Hack Club Build Hub

A reusable teaching library for Hack Club hackathons, clubs, and events —
hands-on workshop tracks, an electronics knowledge base, and a future feed of
community builds.

Static site, no framework, no build step required to view it.

## Pages

| File | What it is |
|---|---|
| `index.html` | Homepage — mission, workshop cards, reference sections, search |
| `learn.html` | Docs viewer — sidebar nav, all workshops + guides, full-text search |
| `videos.html` | Build finder — ranked Build Hub/wiki results plus a YouTube search tab |
| `media.html` | Asset library — searchable grid of every image, GIF, PDF and video in the repo |
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

The same script builds the media index behind `media.html` — every image, GIF,
PDF and embedded video the pages reference, plus the files sitting in
`content/docs/assets/` that nothing links to yet. It prints a warning for any
reference pointing at a file that isn't in the repo.

Front matter follows the just-the-docs conventions the content already uses
(`title`, `parent`, `nav_order`), and callouts like `{: .tip }` / `{: .warning }`
above a blockquote render as styled callout boxes.

## Build finder (`videos.html`)

One query powers two focused tabs:

- **Build Hub & Wiki** — searches every generated workshop and wiki page locally.
  Results are ranked using title, section, exact-phrase and keyword matches.
- **YouTube** — retrieves embeddable YouTube results through the protected local
  endpoint, displays thumbnails and metadata in the Build Hub, paginates with a
  “Load more” button, and plays selections in a full-screen embedded player.

The endpoint caches repeated searches for 15 minutes, rate-limits callers, and
keeps the YouTube API key out of the browser.

### YouTube search setup

Create a YouTube Data API v3 key, then start the included server:

```powershell
$env:YOUTUBE_API_KEY='your-key-here'
python tools/dev_server.py --port 8000
```

Open `http://127.0.0.1:8000/videos.html`. A basic static server can still display
the site and wiki search, but the YouTube results require `tools/dev_server.py`.

## Design

- `design-tokens.css` — colors, typography, spacing, core components
- `site.css` — site chrome (topbar, sidebar, rendered-markdown styles, callouts)
- `DESIGN_SYSTEM.md` / `DESIGN_GUIDE.md` — the written spec

The visual direction follows Hack Club's brand: bold red, clean white surfaces,
dark readable text, playful supporting colors, and practical electronics motifs.

## Local preview

Run `python tools/dev_server.py --port 8000`, then open
`http://127.0.0.1:8000/`. Markdown rendering and YouTube embeds use external
services, so those features require an internet connection.
