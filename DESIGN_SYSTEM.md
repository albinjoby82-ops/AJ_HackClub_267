# Design System — Hackathon Info Hub

## Color Palette

### Primary Colors
- **Deep Teal** - `#0F3B4C` — Main background, text contrast
- **Dark Teal** - `#1A5A6F` — Secondary backgrounds, borders
- **Mint Turquoise** - `#5CDBAB` — Accents, CTAs, highlights
- **Soft Mint** - `#9FE5D4` — Subtle accents, overlays

### Accent Colors
- **Energy Orange** - `#FF5722` — Important alerts, featured events
- **Soft White** - `#F5F8F7` — Main text, backgrounds
- **Light Gray** - `#E8ECEB` — Subtle dividers, borders

### Dark Mode (Secondary)
- **Background** - `#0D2F39`
- **Surface** - `#1A4A5A`
- **Text** - `#F0F4F3`

---

## Typography

### Headings
**Font Family:** Georgia, Garamond, Serif (elegant, educational feel)
- **H1** - 48px, Bold, Line-height 1.2
- **H2** - 36px, Bold, Line-height 1.3
- **H3** - 28px, Bold, Line-height 1.4
- **H4** - 20px, Bold, Line-height 1.4

### Body Text
**Font Family:** Inter, -apple-system, sans-serif (clean, modern)
- **Paragraph** - 16px, Regular, Line-height 1.6
- **Small** - 14px, Regular, Line-height 1.5
- **Button** - 16px, Medium, Uppercase

---

## Layout & Spacing

### Grid System
- **Container Width** - 1200px max
- **Columns** - 12-column grid
- **Gutter** - 24px
- **Mobile** - Full width with 16px padding

### Spacing Scale
- **xs** - 8px
- **sm** - 16px
- **md** - 24px
- **lg** - 40px
- **xl** - 64px

---

## Components

### Cards (Reel Display)
- **Dimensions** - 300px × 400px (ideal for Instagram/TikTok aspect ratio)
- **Border Radius** - 12px
- **Shadow** - `0 4px 12px rgba(15, 59, 76, 0.15)`
- **Padding** - 16px
- **Hover** - Slight lift (transform: translateY(-4px)), shadow deepens
- **Grid** - 3-4 cards per row (responsive)

### Search Bar
- **Height** - 48px
- **Border Radius** - 24px (pill shape)
- **Border** - 2px solid #5CDBAB
- **Background** - #F5F8F7
- **Padding** - 12px 24px
- **Focus State** - Border color → #FF5722, shadow: 0 0 0 3px rgba(255, 87, 34, 0.1)

### Buttons
- **Primary** - Background: #5CDBAB, Text: #0F3B4C, Border-radius: 8px, Padding: 12px 32px
- **Secondary** - Background: transparent, Border: 2px solid #5CDBAB, Text: #5CDBAB
- **Hover** - Background: #9FE5D4 (primary), scale: 1.02

### Event Info Sections
- **Background** - Light tint: rgba(92, 219, 171, 0.08)
- **Border-left** - 4px solid #5CDBAB
- **Padding** - 24px
- **Border-radius** - 8px

---

## Design Elements

### Geometric Accents
- **Diagonal Chevrons** - 45° angle shapes, Mint or Orange
- **Placement** - Section dividers, backgrounds, borders
- **Opacity** - 8-12% for subtle effect

### Photography Integration
- **Overlay** - Dark teal gradient 40-60% opacity over images
- **Border Treatment** - Angled corners (clip-path) or frame within diagonal shape
- **Aspect Ratio** - Prefer 16:9 for full-width hero sections

### Icons
- **Style** - Minimal line-work (stroke: 2px)
- **Size** - 24px (standard), 32px (large), 16px (small)
- **Color** - Primary: #5CDBAB, Secondary: #0F3B4C

---

## Dark Mode Adjustments

- Text: #F0F4F3 (lighter)
- Backgrounds: darken by 15-20%
- Card shadows: rgba(0, 0, 0, 0.4)
- Borders: slightly more visible (higher contrast)

---

## Responsive Breakpoints

- **Mobile** - 320px to 768px
- **Tablet** - 768px to 1024px
- **Desktop** - 1024px and above

### Card Grid
- **Mobile** - 1 column
- **Tablet** - 2 columns
- **Desktop** - 3-4 columns

