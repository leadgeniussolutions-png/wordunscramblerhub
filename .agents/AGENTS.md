# Project Rules — Word Game Solver Utilities

## 1. Premium Display Ad Placements (Anti-Slop)
- **No Mock Wireframe Labels**: Never render static boxes labeled "Google AdSense Slot", "Ad Slot", or use mock diagrams (e.g., placeholder boxes and bars) in layout drafts.
- **High-Fidelity Mock Ads**: Always style ad placeholders as clean, clickable HTML links (`<a>` elements) representing real premium brands (such as Vercel, Stripe, Figma, Notion) with standard advertising dimensions:
  - Top Leaderboard: `970x90` / `728x90`
  - Sidebar Box: `300x250` / `300x600`
  - Bottom Anchor: `728x90` / `320x50`
- **Dynamic Programmatic Rotation**: When implementing ad auto-refresh scripts (e.g., active user timers), animate the ad rotation. Use GSAP or CSS transitions to slide up/fade out, swap the brand data (logos, text, links), and fade back in. This simulates a live programmatic header-bidding auction and preserves a polished UX.
