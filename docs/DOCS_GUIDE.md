# How this documentation system works

Read this before editing anything in `docs/`. It is written for both humans and
future Claude Code sessions.

## Layout

```text
docs/
├── DOCS_GUIDE.md      you are here: rules for editing
├── EVENT_FACTS.md     single source of truth for shared event facts
├── index.md           documentation home, all sections
├── manifest.yaml      machine-readable index of every page
├── competitor/        Section A, competitor-facing pages A1-A9
├── assets/            ASSET_INDEX.md plus images, diagrams, icons
└── audits/            requirement audit and the human decision queue
```

Sections planned: **A** competitor (this work), **B** technical, **C** internal
operations. Only A exists so far.

## Rules

1. **Shared facts come from [EVENT_FACTS.md](EVENT_FACTS.md).** Never restate the
   date, venue, kit contents or terminology from memory.
2. **One fact, one home.** If two pages need the same detail, the detail lives in
   one page and the other links to it. See the cross-linking table in
   EVENT_FACTS.md.
3. **Never invent an event decision.** Use `[DECISION REQUIRED: ...]` for a
   choice the committee must make, `[INFO REQUIRED: ...]` for a fact that exists
   but we do not have. Every marker must also appear in
   [audits/HUMAN_DECISIONS_REQUIRED.md](audits/HUMAN_DECISIONS_REQUIRED.md).
4. **Visual first.** If a diagram, table or timeline is faster than prose, use
   it. Diagrams are Mermaid or inline SVG committed to the repository, never a
   placeholder note.
5. **The ten second rule.** A stressed competitor must find any answer within ten
   seconds. If they cannot, restructure with headings, tables or a summary block.
6. **Irish/British English. No em dashes.**

## Front matter

Every page in `competitor/` carries exactly these fields, in this order:

```yaml
---
id: A1
title: What is Micromouse?
section: competitor
priority: P0
audience: competitors
status: draft
---
```

`status` is one of `draft`, `review`, `ready`, `blocked`. `blocked` means the page
cannot be published until a human decision lands.

## Navigation

Every competitor page ends with a navigation block in this exact shape:

```markdown
---

[Competitor documentation home](index.md) · Previous: [A2 Competition format](02-competition-format.md) · Next: [A4 AI coding agent policy](04-ai-agent-policy.md)

Related: [A6 Laptop setup](06-laptop-setup.md)
```

Links are relative and must resolve inside the repository.

## Adding a page

1. Add the file under the right section directory with the numbered filename.
2. Add front matter.
3. Add a row to [manifest.yaml](manifest.yaml).
4. Add a row to the section index.
5. Add navigation, and fix the neighbouring pages' Next/Previous links.
6. Register any new visual in [assets/ASSET_INDEX.md](assets/ASSET_INDEX.md).

## Publishing

These pages are plain Markdown so they can be dropped into the site under
`hackclub.ucdelecsoc.com/micromouse`. The existing site renders Markdown from
`content/docs/` via `python tools/build_content.py`. When Section A is approved,
either copy `docs/competitor/` into `content/docs/` and add just-the-docs front
matter keys (`layout`, `parent`, `nav_order`), or point the micromouse page at
these files directly. Do not run the build script against `docs/` as it stands:
the front matter schema here is deliberately different.
