# Section A requirements audit

Checked against the Section A brief, requirement by requirement, not from memory.
Counts are of individual requirement bullets, not of headings.

Automated checks (`python docs/audits/check.py`) confirm: front matter schema on
all nine pages, no em dashes anywhere, and every relative link resolving.

Last run: 2026-08-15

## Source caveat

**The Master Documentation Plan referred to in the brief is not in this
repository.** Searched the working tree, all local branches and the full git
history, including `micromouse-reveal/docs/`. The only master document found is
a video trailer prompt, unrelated to documentation.

Requirements were therefore taken from the Section A brief itself, which
enumerates A1 to A9 in detail, and event facts were taken from `micromouse.html`,
the public event page in this repository. If the Master Documentation Plan exists
elsewhere, re-run this audit against it. Anything it requires beyond the brief is
not yet covered.

## Coverage

| ID | Requirements | Covered | Missing info | Visuals | Links checked | Status |
|---|---|---|---|---|---|---|
| A1 | 15 | 15 | None | 3 | Yes | Ready |
| A2 | 16 | 16 | Times, teams, tools, food, prizes | 2 | Yes | Draft |
| A3 | 12 | 12 | 26 clauses undecided | 3 | Yes | Blocked |
| A4 | 7 | 7 | Pre-event code, starter repo | 1 | Yes | Draft |
| A5 | 9 | 9 | Registration, eligibility, logistics | 0 | Yes | Draft |
| A6 | 17 | 16 | Exact board model | 2 | Yes | Draft |
| A7 | 6 | 6 | Nearly all sponsor detail | 0 | Yes | Blocked |
| A8 | 15 | 15 | Room, times, catering, access | 2 | Yes | Draft |
| A9 | 8 | 8 | Named contacts, channel, policy | 0 | Yes | Blocked |
| **Total** | **105** | **104** | 34 distinct decisions | **13** | Yes | |

`Visuals` counts diagrams and images placed in the page, including committed
placeholders. Full detail in [assets/ASSET_INDEX.md](../assets/ASSET_INDEX.md).

## Per page

### A1 What is Micromouse? (15/15) Ready
Autonomous robot, unknown maze, no human input, sensing, exploration, mapping,
route planning, speed run, control, algorithms, international competition, brief
history, beginner suitability, Explore/Understand/Optimise/Race spine, video
embed location. History verified against UKMARS, Micromouse Online, IEEE Spectrum
and APEC before publication. No unresolved decisions, so this page can publish as
soon as IMG-A1-01 and VID-A1-01 are supplied.

### A2 Competition format (16/16) Draft
Build sprint, day schedule, teams, supplied equipment, tools, mentors, practice
mazes, mini diagonal maze, competition maze, food, prizes, sponsors, competitor
equipment, visual timeline, the six hour statement, the "a slow mouse that solves
the maze is still a successful build" statement. Blocked on S1, S8, S11, S12,
S17, S22.

### A3 Rules and scoring (12/12) Blocked
Numbered clauses across 3.1 to 3.12, judge-citable. Robot eligibility,
dimensions, starting procedure, timing, handling, scoring, plus disqualification,
appeals and safety. `# Decisions still required` table at the top, maze layout
SVG, run procedure flow, maze photograph placeholder. International convention is
present but fenced into a clearly labelled reference section with source links,
explicitly marked as not our rules. **Nothing invented.** 26 clauses carry
decision markers; the page cannot publish until at least B1 to B14 land.

### A4 AI coding agent policy (7/7) Draft
Allowed, encouraged, sponsor credits cross-linked, team responsibility,
explainability, pre-event restrictions, shared resources versus team work. 271
words of prose, comfortably one screen. Blocked on S9.

### A5 Registration and FAQ (9/9) Draft
Nine categories, 44 questions, none invented for padding. Registration status
stated plainly at the top rather than faked. Blocked on S2 to S7 and most of the
`SOON` queue. Deliberately carries no visuals: it is a lookup page.

### A6 Laptop setup (16/17) Draft
IDE and toolchain, ESP32-C6 board support, required core version, drivers, Git,
GitHub, AI coding agent CLI, login, admin permissions, USB data cable, board
selection, port selection, compilation, flashing, serial monitor,
`# You are ready if...` checklist, verification chain diagram.

**The one gap:** the required core version is stated as arduino-esp32 3.0.0 or
later, verified against the Espressif release notes, but the exact board shipped
in the kit is not confirmed (S16). Every other version claim on the page was
verified against a primary source. No CH34x driver URL is given because Espressif
does not document one; the row names the chip vendor instead.

### A7 Sponsor credits (6/6) Blocked
Repeatable structure applied: You get, Before the event, Redeem, Limits,
Problems. Anthropic block written, additional partners templated for the two open
technical slots, UCD School credited without inventing a credits offer. **No
redemption instruction has been invented.** The page is a scaffold waiting on B17
and B18 and cannot publish before then.

### A8 Venue, travel and what to bring (15/15) Draft
UCD, UCD Village, exact room, arrival, public transport, cycling, parking,
accessibility, food, dietary requirements, filming, contact, `# Bring`,
`# We provide`, map asset brief. Travel facts verified against myucd.ucd.ie,
Transport for Ireland and UCD Estates, with sources cited inline. The Saturday
conflict on both the DART shuttle and pay and display hours is called out
explicitly rather than glossed. No parking price or space availability stated.

### A9 Code of conduct (8/8) Blocked
Expected behaviour, unacceptable behaviour, harassment defined plainly, reporting,
named contacts placeholder, consequences, safety, escalation. Report block sits
near the top, not buried. Original text following recognised structures
(Contributor Covenant, Berlin Code of Conduct, Hack Club), with a maintainer note
naming them. The applicable UCD policies were found and linked, and this document
is framed as supplementing rather than replacing them. Blocked on B15 and B16: a
code of conduct with no named contact does not function.

## Passes completed

| Pass | Result |
|---|---|
| Concision | A8's map asset brief (2,000 characters) moved out of the competitor page into the asset index. Pages were drafted under a terse brief and are already tight: A4 271 words, A1 498, A2 501. A3 (1,981) and A6 (1,534) are long because a clause-numbered rulebook and a three-platform install guide have an irreducible size. No further cut made without losing instructions |
| Consistency | Terminology table in EVENT_FACTS.md applied. Event name, date, venue, six hour wording, team terminology, beginner messaging, kit contents, AI policy and rules terminology aligned across all nine pages. Front matter schema identical on all nine, verified by script |
| Links | Automated. All relative links resolve, including into `content/docs/` for the house safety wiki. Eight filename mismatches between pages were found and fixed |
| Visuals | Five diagrams generated as real Mermaid or SVG, not placeholders. The A3 maze concept was upgraded from a weak Mermaid sketch to a proper SVG grid. Eight photograph, map, screenshot and video assets need a human and have committed placeholders plus briefs |
| Requirements | This document |
| Git diff | Reviewed. Only `docs/` is added. Twelve files were already modified in the working tree before this work started and were not touched |

## Not verified

- The Master Documentation Plan, as above.
- Every fact in the `Not yet confirmed` list in
  [EVENT_FACTS.md](../EVENT_FACTS.md). These are ours to decide, not ours to
  research.
- Rendering of the Mermaid diagrams in the final publishing target. They are
  valid Mermaid but the site's Markdown viewer has not been tested against them.
- UCD Estates pages returned HTTP 403 to direct fetch, so cycling and parking
  detail is linked rather than transcribed.

---

[Documentation home](../index.md) · [Decision queue](HUMAN_DECISIONS_REQUIRED.md) · [Competitor docs](../competitor/index.md)
