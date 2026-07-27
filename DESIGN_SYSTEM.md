# Design System — Hack Club Build Hub

Bright, practical, and distinctly Hack Club. Clean white surfaces, dark readable
text, Hack Club red as the hero color, and supporting colors used with purpose.
Circuit motifs connect the interface to the hands-on electronics material.

## Color Palette

### Ink / Text
- **Dark** - `#1F2D3D` — Headings and primary text
- **Slate** - `#3C4858` — Secondary/body text
- **Blue** - `#338EDA` — Links and secondary emphasis

### Brand Accent
- **Hack Club Red** - `#EC3750` — Hero color, primary actions, focus rings
- **Deep Red** - `#D62442` — Accent text and labels that need stronger contrast

### Signal (use once per view — never more)
- **Signal Orange** - `#F4652E` — The single most urgent thing on a page: a deadline, "live now". Two oranges on one view means neither one matters anymore.

### Surfaces
- **Paper** - `#FAFCFB` — Page background
- **Card** - `#FFFFFF` — Card/panel background
- **Line** - `#E3ECE9` — Hairline borders
- **Line Strong** - `#B9CFC9` — Dashed/wireframe borders

### Dark Mode (Secondary)
- **Paper** - `#0D2432`
- **Card** - `#123240`
- **Text** - `#F0F4F3`
- **Ink Soft (dark)** - `#9FBFC7`

---

## Typography

### Headings
**Font Family:** Phantom Sans / system sans-serif — bold, friendly, and direct
- **H1 (Display)** - clamp(38–56px), weight 600, line-height 1.15, letter-spacing -0.01em
- **H2** - 30px, weight 600, line-height 1.2
- **H3** - 21px, weight 600, line-height 1.3
- **H4** - 18px, weight 600

### Body & UI
**Font Family:** Inter, -apple-system, sans-serif — neutral, readable
- **Body** - 16px, regular, line-height 1.6
- **Small** - 13px, regular
- **Buttons** - 14px, semibold

### Monospace ("Silkscreen")
**Font Family:** JetBrains Mono, Cascadia Code, Consolas
- Reserved strictly for **metadata**: eyebrows, filter chips, timestamps, reel counts, stat labels
- Eyebrows: 11px, uppercase, letter-spacing 0.12em, color Deep Mint
- Never used for body copy or headings

---

## Layout & Spacing

### Grid System
- **Container Width** - 1060px max
- **Gutter** - 20px (desktop), 14px (mobile)
- **Mobile** - Full width with 16px padding

### Spacing Scale
- **xs** - 8px
- **sm** - 16px
- **md** - 24px
- **lg** - 40px
- **xl** - 64px

### Section rhythm
Sections stack with a hairline `border-top` (`--color-line`) and 64–72px of
padding — no filled background bands. Whitespace *is* the layout; if a
section feels busy, remove a border before adding a fill.

---

## Components

### Reel Cards (Live Build Feed)
- **Aspect ratio** - 4:5 thumbnail (matches Reels/Shorts/TikTok)
- **Border Radius** - 14px
- **Shadow** - `0 1px 2px rgba(15,59,76,.05), 0 8px 24px rgba(15,59,76,.06)`
- **Platform badge** - small mono pill, top-left of thumbnail (`YOUTUBE` / `INSTAGRAM` / `TIKTOK`)
- **Play icon** - white circle, centered, subtle drop shadow
- **Hover** - lift (translateY(-3px)), shadow deepens
- **Grid** - 4 cards/row desktop → 3 tablet → 2 small tablet → 1 mobile

### Search Bar
- **Shape** - pill (border-radius: 999px), not a plain rectangle
- **Border** - 1px solid Line, focus → Mint border + soft mint glow (`0 0 0 4px rgba(92,219,171,.18)`)
- **Icon** - inline search icon, ink-soft stroke
- **Pairs with** platform filter chips directly beneath it

### Filter Chips ("Silkscreen labels")
- Mono font, 12px, pill shape
- Inactive: white background, Line border, ink-soft text
- Active: solid Ink Teal background, white text

### Buttons
- **Primary** - Ink Teal fill, white text
- **Mint** - Mint fill, ink text (secondary CTA, more energetic)
- **Ghost** - transparent, Line border, ink text
- **Link** - no fill, Deep Mint text, used inline ("Rules & judging →")
- **Hover** - translateY(-1px) + background shift, no scale gimmicks

### Stat Tiles
- White card, hairline border, 2px accent "rail" across the top (Mint by default, Orange for the one signal stat per view)
- Serif number (38px, weight 600) + mono uppercase label beneath

### Event Info Tiles
- White card, icon + serif H4 + small body text
- One tile may carry the `is-signal` treatment (orange heading, orange-tinted border) for the single most urgent item — e.g. registration deadline

---

## Circuit Motifs (the EEE identity)

Keep these subtle — decorative, never competing with content.

### Trace Dividers
- SVG line paths at 10–18% opacity (Ink Teal stroke), right-angle bends like a PCB trace
- Terminate in a small solid dot (Mint or Orange) marking a "component"

### Pin Headers
- Rows of small dots (7px circles, Ink Teal at 22% opacity)
- One dot "hot" (solid Deep Mint) marks progress/active state — used for step indicators, timelines

### Silkscreen Labels
- Mono, uppercase, letter-spacing 0.06–0.12em
- Used for chips, badges, stat labels, eyebrows — the "printed" details on a circuit board, not the board itself

---

## Dark Mode Adjustments

- Paper → `#0D2432`, Card → `#123240`
- Text → `#F0F4F3`, Ink Soft → `#9FBFC7`
- Deep Mint promoted to primary accent text color (better contrast than teal on dark)
- Shadows shift from soft/light to `rgba(0,0,0,...)`, slightly stronger

---

## Responsive Breakpoints

- **Mobile** - up to 480px
- **Small tablet** - up to 760px
- **Desktop** - 1024px and above

### Reel Grid
- **Mobile** - 1 column
- **Small tablet** - 2 columns
- **Tablet/laptop** - 3 columns
- **Desktop** - 4 columns

---

## Design Rules of Thumb

1. **Whitespace is the layout.** Hairline borders and air, not boxes and fills.
2. **One orange per view.** It marks the single most urgent thing — a deadline, a live event. More than one and nothing reads as urgent.
3. **Traces stay quiet.** Circuit motifs at 10–18% opacity, decorative only.
4. **Mono means metadata.** Never body copy or headings — timestamps, counts, chips only.
