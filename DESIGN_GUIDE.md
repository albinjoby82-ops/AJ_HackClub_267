# Design & Vibe Guide — Hackathon Info Hub (v2)

Welcome! This folder contains all the design files and tokens for your electronics-focused hackathon/makerthon information hub. Here's what you've got and how to use it.

---

## 📁 What's Inside

### 1. **MOOD_BOARD.html**
Interactive visual reference showing colors, typography, components, circuit motifs, and design rules.
- **Open in browser** to see the full design system come to life
- Share this with your team for alignment
- Reference this while building

### 2. **DESIGN_SYSTEM.md**
Markdown documentation with all the specs you need:
- Color codes and usage
- Typography sizes and families
- Spacing scale
- Component specs (reel cards, search bar, chips, buttons, stat tiles)
- Circuit motif guidelines (traces, pin headers, silkscreen labels)
- Responsive breakpoints, dark mode

### 3. **design-tokens.css**
Ready-to-use CSS variables and base styles:
- Copy into your project
- Use as-is or customize the values
- Includes utility classes for quick styling
- Responsive grid and card styles
- Pre-built component classes (`.reel-card`, `.chip`, `.search-bar`, `.stat`, etc.)

### 4. **index-template.html**
A working example page wired up to `design-tokens.css` — search + platform filter chips, live-feed grid, event info tiles, dark mode toggle. Open it, view source, copy what you need.

---

## 🎨 The Vibe

**Visual Identity:**
- **Colors:** Near-white paper background, deep teal ink, one mint accent, one signal orange (used sparingly)
- **Typography:** Bold Phantom Sans headings and clean body copy, with monospace reserved for metadata and labels
- **Layout:** Light mode, hairline borders instead of boxes, generous whitespace, card-based reel feed
- **Feel:** Energetic, practical, and welcoming — a build guide, not corporate documentation

**Design Philosophy:**
- Clean and modern, not maximalist or neon
- Beginner-friendly (welcoming for all skill levels)
- Educational tone (empowering, not intimidating)
- The electronics identity comes from quiet PCB details (traces, pin headers, silkscreen labels), not sci-fi/cyberpunk styling

---

## 🚀 Quick Start

### Using design-tokens.css

1. **Copy the file** into your project (e.g., `/styles/design-tokens.css`)
2. **Import in your main CSS or HTML:**
   ```html
   <link rel="stylesheet" href="design-tokens.css">
   ```
3. **Start using CSS variables:**
   ```css
   .my-component {
     background: var(--color-mint);
     color: var(--color-ink);
     padding: var(--spacing-md);
     border-radius: var(--radius-lg);
   }
   ```

### Building Components

**Reel Card:**
```html
<div class="reel-card card" data-platform="youtube">
  <div class="reel-thumb" style="background: linear-gradient(160deg, #E9F7F1, #CBEEE0);">
    <span class="reel-platform">YOUTUBE</span>
    <span class="reel-play"></span>
  </div>
  <div class="card-content">
    <h4 class="card-title">Build Title</h4>
    <p class="card-meta">@username · 2.4K</p>
  </div>
</div>
```

**Search Bar (with filter chips):**
```html
<label class="search-bar">
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3E5C68" stroke-width="2" stroke-linecap="round">
    <circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>
  </svg>
  <input type="search" placeholder="Search YouTube, Instagram, TikTok...">
</label>

<div class="chip-row">
  <span class="chip is-active" data-platform="all">ALL</span>
  <span class="chip" data-platform="youtube">YOUTUBE</span>
  <span class="chip" data-platform="instagram">INSTAGRAM</span>
  <span class="chip" data-platform="tiktok">TIKTOK</span>
</div>
```

**Buttons:**
```html
<button class="btn btn-primary">Register Now</button>
<button class="btn btn-mint">Open Workshop</button>
<button class="btn btn-ghost">View Schedule</button>
<button class="btn btn-link">Rules &amp; judging →</button>
```

**Event Info Tile** (use `is-signal` for the one urgent item per page, e.g. a deadline):
```html
<div class="info-section">
  <h4>⏰ Event Date</h4>
  <p>March 15-17, 2026 • Location: TBD</p>
</div>
```

**Stat Tile:**
```html
<div class="stat">
  <div class="stat-num">500+</div>
  <div class="stat-label">Members</div>
</div>
<div class="stat stat-signal"> <!-- orange rail, use once -->
  <div class="stat-num">48h</div>
  <div class="stat-label">To build</div>
</div>
```

**Reel Grid:**
```html
<div class="reel-grid">
  <!-- Reel cards here -->
</div>
```

---

## 🎯 Key Design Decisions

### Why These Colors?
- **Hack Club Red (#EC3750)** - The primary brand color and strongest visual signal
- **Blue (#338EDA)** - Links and supporting emphasis
- **Deep Red (#D62442)** - A readable red for accent text on white
- **Signal Orange (#F4652E)** - Reserved for the single most urgent thing per view (a deadline, "live now"). Never more than one per page.

### Why These Typography Choices?
- **Phantom Sans** for headings and UI - Bold, friendly, and consistent with Hack Club
- **Inter (sans-serif)** for body - Clean, modern, readable
- **Monospace** for metadata only - timestamps, view counts, filter chips — reads like PCB silkscreen printing

### Why Cards for Reels?
- 4:5 aspect ratio matches YouTube Shorts / Reels / TikTok natively
- Platform badge (mono pill) + play icon make the source instantly scannable
- Hover lift adds interactivity without overwhelming
- Grid layout adapts 4 → 3 → 2 → 1 columns by screen size

### Why Circuit Motifs Instead of Neon?
Cyberpunk/neon reads as generic "tech." Trace dividers, pin-header dots, and
silkscreen-style mono labels are literal EEE drafting conventions — quieter,
more credible and connect the interface to the hands-on electronics material
mark.

---

## 📱 Responsive Design

### Breakpoints:
- **Mobile:** up to 480px
- **Small tablet:** up to 760px
- **Desktop:** 1024px+

### Reel Grid Changes:
- **Mobile:** 1 column
- **Small tablet:** 2 columns
- **Tablet/laptop:** 3 columns
- **Desktop:** 4 columns

### Text Scaling:
All heading sizes reduce at smaller breakpoints. Use the `.reel-grid` class for automatic responsive behavior.

---

## 🌙 Dark Mode

Dark mode is built into the CSS (use `data-theme="dark"` on the `html` element):
```html
<html data-theme="dark">
```

The design system automatically adjusts:
- Paper/card backgrounds → dark teal (`#0D2432` / `#123240`)
- Text → light (`#F0F4F3`), muted text → soft mint-teal
- Deep Mint becomes the primary accent text color (better contrast than teal on dark)
- Shadows shift from soft/light to black-based, slightly stronger

---

## 🔄 Theme Toggle

`index-template.html` already wires this up. The core logic:

```javascript
function toggleTheme() {
  const html = document.documentElement;
  const current = html.getAttribute('data-theme');
  const newTheme = current === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
}

// On load, restore user's preference
window.addEventListener('load', () => {
  const saved = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
});
```

---

## ✨ Special Features

### Hover Effects
- **Cards:** Lift up (translateY(-3px)), shadow deepens — no scale, keep it understated
- **Buttons:** translateY(-1px) + background shift, no scale gimmicks
- **All transitions:** ~200ms ease (snappy, not sluggish)

### Circuit Motifs
- **Trace dividers:** SVG paths at 10-18% opacity, right-angle bends like PCB traces, terminating in a small solid dot (mint or orange)
- **Pin headers:** rows of small dots, one "hot" (solid Deep Mint) to mark active/progress state
- **Silkscreen labels:** mono, uppercase, tracked-out — used only for chips, badges, stat labels, eyebrows

### One Signal Color Per View
Signal Orange marks exactly one thing per page — the registration deadline,
a "live now" badge, etc. If you're reaching for orange twice on the same
screen, pick which one actually matters more and let the other be mint or
plain ink.

---

## 🎬 Building the Reel Feed

Your website will pull live content from YouTube, Instagram, and TikTok. Here's the recommended structure:

```html
<section class="container mt-lg mb-lg">
  <span class="eyebrow">Live build feed</span>
  <h2>Featured Builds</h2>

  <label class="search-bar mb-md">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3E5C68" stroke-width="2" stroke-linecap="round">
      <circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>
    </svg>
    <input type="search" placeholder="Search builds...">
  </label>

  <div class="chip-row mb-lg">
    <span class="chip is-active" data-platform="all">ALL</span>
    <span class="chip" data-platform="youtube">YOUTUBE</span>
    <span class="chip" data-platform="instagram">INSTAGRAM</span>
    <span class="chip" data-platform="tiktok">TIKTOK</span>
  </div>

  <div class="reel-grid">
    <!-- Loop through reels here -->
    <div class="reel-card card" data-platform="youtube">
      <div class="reel-thumb" style="background-image: url(thumbnail.jpg); background-size: cover;">
        <span class="reel-platform">YOUTUBE</span>
        <span class="reel-play"></span>
      </div>
      <div class="card-content">
        <h4 class="card-title">Build Title</h4>
        <p class="card-meta">@user · Views</p>
      </div>
    </div>
  </div>
</section>
```

---

## 📋 Design Checklist

Before launch, make sure:
- [ ] Colors match the palette (test in light AND dark modes)
- [ ] Typography hierarchy is clear (serif for headings, sans-serif for body, mono for metadata only)
- [ ] Reel cards display 4/row desktop, 3 tablet, 2 small tablet, 1 mobile
- [ ] Search bar is pill-shaped with mint focus glow, paired with platform chips
- [ ] Buttons use subtle translateY hover, not scale
- [ ] Info tiles/sections have left mint border; only one uses `is-signal` (orange)
- [ ] Sections separated by hairline borders, not filled color bands
- [ ] Spacing uses the defined scale (no random measurements)
- [ ] Circuit motifs (if used) sit at 10-18% opacity — decorative, not competing with content
- [ ] Dark mode is tested and readable

---

## 🔗 File Structure Recommendation

```
your-project/
├── styles/
│   ├── design-tokens.css      (CSS variables & base styles)
│   ├── main.css               (your custom styles)
│   └── responsive.css         (optional, for media queries)
├── index.html
├── assets/
│   └── images/
├── js/
│   └── theme-toggle.js        (optional, for dark mode)
└── DESIGN_SYSTEM.md           (reference guide)
```

---

## 💡 Tips for Success

1. **Use CSS Variables** — Makes it easy to change colors/spacing site-wide
2. **Follow the Spacing Scale** — Consistency looks professional
3. **Test on Real Devices** — Especially mobile (your users might be on phones at the event!)
4. **Keep Animations Subtle** — ~200ms is the sweet spot (fast but not jarring)
5. **Use High-Quality Photos Sparingly** — this system leans on typography and whitespace more than imagery; when you do use photos, keep them out of hero/card backgrounds so the hairline-and-whitespace language stays intact
6. **Dark Mode is a Feature** — Test it early, not late

---

## 🎨 Customization

### Change the Primary Color:
Edit `design-tokens.css`:
```css
:root {
  --color-ink: #YOUR_COLOR;
  --color-mint: #YOUR_ACCENT;
}
```

### Change Typography:
```css
:root {
  --font-serif: 'Your Serif Font', serif;
  --font-sans: 'Your Sans Font', sans-serif;
  --font-mono: 'Your Mono Font', monospace;
}
```

### Adjust Spacing:
```css
:root {
  --spacing-md: 20px; /* default is 24px */
  --spacing-lg: 48px; /* default is 40px */
}
```

All dependent styles will update automatically. That's the power of CSS variables!

---

## 🤝 Sharing with Your Team

1. Open **MOOD_BOARD.html** in browser
2. Share the link or screenshot
3. Reference **DESIGN_SYSTEM.md** for specs
4. Copy **design-tokens.css** into the project
5. Use **index-template.html** as your starting point
6. Start building!

---

## 📞 Questions?

- **"How do I embed Instagram reels?"** → Use Instagram's embed API or iframe
- **"How do I fetch YouTube video data?"** → YouTube Data API v3
- **"How do I add dark mode?"** → Already in design-tokens.css! Just toggle `data-theme`
- **"Can I change the colors?"** → Yes! Edit the CSS variables
- **"Where's the orange used?"** → Sparingly — one deadline/urgent badge per page, never decoratively

---

**Happy building! 🚀⚡**

This is your visual identity. Make it shine at your hackathon!

—Design System v2.0
