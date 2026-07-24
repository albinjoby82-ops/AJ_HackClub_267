# Design & Vibe Guide — Hackathon Info Hub

Welcome! This folder contains all the design files and tokens for your electronics-focused hackathon/makerthon information hub. Here's what you've got and how to use it.

---

## 📁 What's Inside

### 1. **MOOD_BOARD.html** 
Interactive visual reference showing colors, typography, components, and design guidelines. 
- **Open in browser** to see the full design system come to life
- Share this with your team for alignment
- Reference this while building

### 2. **DESIGN_SYSTEM.md**
Markdown documentation with all the specs you need:
- Color codes and usage
- Typography sizes and families
- Spacing scale
- Component specs (cards, buttons, search bar, etc.)
- Responsive breakpoints
- Dark mode guidelines

### 3. **design-tokens.css**
Ready-to-use CSS variables and base styles:
- Copy into your project
- Use as-is or customize the values
- Includes utility classes for quick styling
- Responsive grid and card styles
- Pre-built component classes

---

## 🎨 The Vibe

**Visual Identity:**
- **Colors:** Deep teal primary, mint turquoise accents, energy orange for alerts
- **Typography:** Elegant serif for headings (Georgia/Garamond), clean sans-serif for body (Inter/system fonts)
- **Layout:** Light mode by default, geometric accents, angled shapes, card-based design
- **Feel:** Professional yet approachable, modern, educational, energetic

**Design Philosophy:**
- Sleek but informative (not minimalist, not cluttered)
- Beginner-friendly (welcoming for all skill levels)
- Educational tone (empowering, not intimidating)
- Responsive (mobile-first, but beautiful on all screens)

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
     background: var(--color-accent);
     color: var(--color-text);
     padding: var(--spacing-md);
     border-radius: var(--radius-lg);
   }
   ```

### Building Components

**Reel Card:**
```html
<div class="reel-card card">
  <img class="card-image" src="video-thumbnail.jpg" alt="Reel">
  <div class="card-content">
    <h4 class="card-title">Build Title</h4>
    <p class="card-meta">@username • 2.4K views</p>
  </div>
</div>
```

**Search Bar:**
```html
<input 
  type="search" 
  class="search-bar" 
  placeholder="Search YouTube, Instagram, TikTok..."
>
```

**Button:**
```html
<button class="btn btn-primary">Register Now</button>
<button class="btn btn-secondary">Learn More</button>
```

**Event Info Section:**
```html
<div class="info-section">
  <h4>⏰ Event Date</h4>
  <p>March 15-17, 2026 • Location: TBD</p>
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
- **Deep Teal (#0F3B4C)** - Trust, professionalism, tech-forward
- **Mint Turquoise (#5CDBAB)** - Energy, approachability, fresh
- **Energy Orange (#FF5722)** - Urgency, attention for important events

### Why These Typography Choices?
- **Georgia/Garamond (serif)** for headings - Elegant, established, educational
- **Inter/System sans-serif** for body - Clean, modern, readable
- Hierarchy: Large serif headings with smaller sans-serif supporting text

### Why Cards for Reels?
- Natural YouTube/Instagram/TikTok aspect ratio (3:4)
- Scannable at a glance
- Hover effects add interactivity without overwhelming
- Grid layout adapts to mobile/tablet/desktop

---

## 📱 Responsive Design

### Breakpoints:
- **Mobile:** 320px – 767px
- **Tablet:** 768px – 1023px
- **Desktop:** 1024px+

### Grid Changes:
- **Mobile:** 1 column of reel cards
- **Tablet:** 2 columns
- **Desktop:** 3-4 columns

### Text Scaling:
All heading sizes reduce at smaller breakpoints. Use the `.reel-grid` class for automatic responsive behavior.

---

## 🌙 Dark Mode

Dark mode is built into the CSS (use `data-theme="dark"` on the `html` element):
```html
<html data-theme="dark">
```

The design system automatically adjusts:
- Background colors → darker
- Text colors → lighter
- Contrast → increased
- Shadows → stronger (more visible on dark)

---

## 🔄 Theme Toggle

To add light/dark mode toggle to your site:

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
- **Cards:** Lift up (transform: translateY(-4px)), shadow deepens
- **Buttons:** Scale slightly (1.02), maintain color change
- **All transitions:** 0.3s ease (smooth, not jarring)

### Geometric Accents
- Use diagonal chevrons (45° angles) for visual interest
- Mint or orange at 8-12% opacity for subtlety
- Perfect for section dividers, backgrounds, or borders

### Image Overlays
All images use a dark teal gradient (40-60% opacity) to:
- Ensure text legibility
- Maintain consistent design feel
- Add visual depth

---

## 🎬 Building the Reel Feed

Your website will pull live content from YouTube, Instagram, and TikTok. Here's the recommended structure:

```html
<section class="container mt-lg mb-lg">
  <h2>Featured Builds</h2>
  
  <input type="search" class="search-bar mb-lg" placeholder="Search builds...">
  
  <div class="reel-grid">
    <!-- Loop through reels here -->
    <div class="reel-card card">
      <img class="card-image" src="thumbnail.jpg">
      <div class="card-content">
        <h4 class="card-title">Build Title</h4>
        <p class="card-meta">@user • Platform • Views</p>
      </div>
    </div>
  </div>
</section>
```

---

## 📋 Design Checklist

Before launch, make sure:
- [ ] Colors match the palette (test in light AND dark modes)
- [ ] Typography hierarchy is clear (serif for headings, sans-serif for body)
- [ ] Cards display 3-4 per row on desktop, 2 on tablet, 1 on mobile
- [ ] Search bar has proper focus state (orange border, shadow)
- [ ] Buttons scale and animate on hover
- [ ] Info sections have left mint border
- [ ] All images have the dark teal overlay
- [ ] Spacing uses the defined scale (no random measurements)
- [ ] Hover states work smoothly (0.3s transitions)
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
4. **Keep Animations Subtle** — 0.3s is the sweet spot (fast but not jarring)
5. **Use High-Quality Images** — Good photography makes the design shine
6. **Dark Mode is a Feature** — Test it early, not late

---

## 🎨 Customization

### Change the Primary Color:
Edit `design-tokens.css`:
```css
:root {
  --color-primary-dark: #YOUR_COLOR;
  --color-primary: #YOUR_COLOR;
}
```

### Change Typography:
```css
:root {
  --font-serif: 'Your Serif Font', serif;
  --font-sans: 'Your Sans Font', sans-serif;
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
5. Start building!

---

## 📞 Questions?

- **"How do I embed Instagram reels?"** → Use Instagram's embed API or iframe
- **"How do I fetch YouTube video data?"** → YouTube Data API v3
- **"How do I add dark mode?"** → Already in design-tokens.css! Just toggle `data-theme`
- **"Can I change the colors?"** → Yes! Edit the CSS variables

---

**Happy building! 🚀⚡**

This is your visual identity. Make it shine at your hackathon! 

—Your Design System v1.0
