---
name: word-utility-site-designer
description: Comprehensive playbook, structural HTML layouts, CSS variables, and JavaScript patterns for designing, building, and optimizing premium, high-traffic, display-ad monetized word game utilities (Word Unscramblers, Wordle Solvers, Connections Helpers) modeled after leading competitors like word.tips.
---

# Word Utility Site Designer Skill & Playbook

This skill outlines the design architecture, competitive user experience, ad optimization strategies, and SEO schema requirements for building high-traffic word solver utilities (Scrabble Word Finders, Wordle Solvers, NYT Connections helpers) optimized to maximize display ad revenue (AdSense, Mediavine, Ezoic).

---

## 🎨 1. Premium Visual Identity (10x Design System)

Utility sites must capture and retain user attention immediately to reduce bounce rates. Avoid plain white default styles; instead, implement a high-end "Obsidian Cyberpunk" aesthetic:

### CSS Custom Design Tokens
Use unified custom properties for styling:
```css
:root {
  --bg-primary: #060813;           /* Ultra dark navy/obsidian */
  --bg-panel: rgba(15, 20, 36, 0.6); /* Translucent glass surface */
  --bg-input: rgba(8, 12, 24, 0.85);
  
  --border-static: rgba(255, 255, 255, 0.08);
  --border-glow-primary: rgba(139, 92, 246, 0.25); /* Violet glow */
  --border-glow-secondary: rgba(6, 182, 212, 0.25); /* Cyan glow */
  
  --accent-violet: #8b5cf6;
  --accent-cyan: #06b6d4;
  --accent-gradient: linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%);
  
  --text-primary: #f9fafb;
  --text-secondary: #9ca3af;
  
  --glass-blur: blur(16px) saturate(180%);
  --radius-panel: 24px;
  --radius-tile: 8px;
}
```

### Typographic Hierarchy
- **Primary Headings & Numeric Labels**: `Space Grotesk` (clean, bold, geometric).
- **Body & Word Results**: `Plus Jakarta Sans` or `Outfit` (modern, geometric sans-serif).

---

## ⚡ 2. User Engagement & Retention Mechanics

Since display ad revenue is directly proportional to page impressions and dwell time (competitor average session length is 4+ minutes), keep players engaged on-page with the following features:

### A. Real-Time Wildcard Keycap Highlighting
Provide immediate visual cues as the user types wildcard characters (`?`, `*`, or `Space`). Style them as keyboard keycaps that scale and glow on active triggers:
```javascript
const input = document.getElementById('rack-input');
input.addEventListener('input', () => {
  const val = input.value;
  document.getElementById('key-qmark').classList.toggle('active', val.includes('?'));
  document.getElementById('key-star').classList.toggle('active', val.includes('*'));
  document.getElementById('key-space').classList.toggle('active', val.includes(' '));
});
```

### B. Inline Click-to-Define Word Modal
Prevent users from leaving the tab to check word definitions. Load definitions dynamically via a free Dictionary API into a glassmorphic modal overlay:
```javascript
function showDefinition(word) {
  const modal = document.getElementById('definition-modal');
  const container = document.getElementById('definitions-container');
  modal.classList.add('visible');
  
  fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${word}`)
    .then(r => r.json())
    .then(data => {
      let html = '';
      data[0].meanings.forEach(m => {
        html += `<p class="part-speech">${m.partOfSpeech}</p><ol>`;
        m.definitions.slice(0, 2).forEach(d => html += `<li>${d.definition}</li>`);
        html += '</ol>';
      });
      container.innerHTML = html;
    })
    .catch(() => {
      container.innerHTML = `<p>Definition not found.</p><a href="https://google.com/search?q=definition+of+${word}" target="_blank">Search Google &rarr;</a>`;
    });
}
```

---

## 💰 3. Ad Placement & CTR Optimization (Revenue Mechanics)

To maximize display ad yield without looking like a wireframe or template (which screams "AI-generated"), we enforce strict high-fidelity ad slot simulation constraints:

- **No Cheap Placeholder Ads**: Avoid drawing mock rectangles with visual bars, grids, or using static text labels like "Google AdSense Slot" or "Sponsored Slot".
- **High-Fidelity Mock Ads**: Always style ad placeholders as clean, clickable link containers (`<a>` tags) representing real premium brands (such as Vercel, Stripe, Figma, Notion) with standard advertising dimensions.
- **Dynamic Programmatic Rotation**: When implementing ad auto-refresh scripts, use a transition routine (`rotateAd`) to slide/fade out, swap the active brand anchor/logo/details, and fade back in. This simulates a real header-bidding refresh and keeps the interface looking polished and organic.

### Optimized Ad Layout Slots
1. **Top Leaderboard banner (`970x90` / `728x90` responsive)**: Placed below the header, above the main content area.
2. **Sticky Sidebar ad (`300x250` / `300x600` skyscraper)**: Pinned inside the right-hand column so it remains 100% visible while users scroll down lists.
3. **Bottom Anchor banner (`728x90` / `320x50`)**: Sticky banner pinned to the bottom viewport.

### Programmatic Rotation & Auto-Refresh Script
Dwell times are long. Implement a safe refresh loop to rotate mock ad content every 30-45 seconds of active user sessions:
```javascript
const alternateAds = {
  top: [
    { brand: "Vercel", title: "Develop. Preview. Ship.", text: "Deploy globally in seconds.", btn: "Start Free", url: "https://vercel.com" },
    { brand: "Stripe", title: "Payments for the internet", text: "Infrastructure for global commerce.", btn: "Start Stripe", url: "https://stripe.com" }
  ]
};

function rotateAd(slotId, adData) {
  const frame = document.getElementById(slotId);
  if (!frame) return;
  
  // Slide out, swap content, slide in
  gsap.to(frame, {
    opacity: 0,
    y: -10,
    duration: 0.3,
    onComplete: () => {
      frame.setAttribute('href', adData.url);
      frame.innerHTML = `
        <div class="mock-ad-brand"><span>${adData.brand}</span></div>
        <div class="mock-ad-content">
          <span class="mock-ad-title">${adData.title}</span>
          <span class="mock-ad-text">${adData.text}</span>
        </div>
        <span class="mock-ad-btn">${adData.btn}</span>
      `;
      gsap.to(frame, { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' });
    }
  });
}
```


---

## 🔍 4. Programmatic SEO (pSEO) & Structured Data

To capture search volumes for variations like `5-letter words starting with A` or `Connections hint today`, structure the HTML page with clean, crawlable semantic details.

### A. Schema Trinity Markup
Embed structured JSON-LD schemas inside the page head:
1. **`WebApplication`**: Declares the solving tool, including browser requirements and price (`$0.00`).
2. **`FAQPage`**: Standard Accordion questions and direct answers for crawl snippets.
3. **`BreadcrumbList`**: Structured breadcrumbs for rich Google Search listings.

### B. LGS Factual Content Accordions
FAQ and information sections must have H3 search questions with **30-60 word factual direct-answers** immediately below them:
```html
<div class="faq-item">
  <h3>How do I unscramble letters with wildcards?</h3>
  <p>To unscramble letters with wildcards, enter a question mark (?), asterisk (*), or space in the input box to represent blank tiles. The solver treats these as placeholder credits, matching them against any letter in the dictionary to find all possible valid word permutations.</p>
</div>
```

---

## ⚡ 5. Performance & Dictionary Compilation

Google's Core Web Vitals (LCP, INP) heavily penalize websites with slow interactive feedback. Keep computations client-side:
- **Compressed space-separated database**: Group words by length inside `window.DICTIONARY` as single space-separated strings.
- **Fast Array Splitting**: Only split `window.DICTIONARY[len].split(' ')` on-demand when performing a search.
- **Binary / Frequency Map Subset Check**: Keep loop iterations clean by comparing character frequency maps (e.g. `wordCharCount[c] <= inputCharCount[c] + wildcardsAvailable`) to solve inputs in under 10ms.
