# Project Memory: Word Game Solver Site Optimization

## 1. Type Safety in Keyword Research APIs
- **Lesson**: DataForSEO Labs keywords API responses may return `None` for monthly search volume or keyword difficulty metrics.
- **Why it matters**: Direct mathematical comparisons (like `>=`) against a `NoneType` will crash the filtering loop.
- **How to apply**: Always default missing numeric values (e.g. `vol_val = vol if vol is not None else 0`) and check for `is not None` before comparing.

## 2. Browser Global Scope vs Node.js Module Wrapping
- **Lesson**: Functions defined in local JavaScript source files (like `solver.js`) are global in browser script tags but local to module scope in Node environment.
- **Why it matters**: Running standard Node `require()` during automated script testing will throw `TypeError: solveUnscrambler is not a function`.
- **How to apply**: Read the JS source files as text and execute them via `eval()` in Node tests to properly simulate browser global `window` behavior.

## 3. High Dwell Time & AdSense Auto-Refresh
- **Lesson**: Dwell times on gaming/word utility sites average over 4 minutes, making auto-refreshing display ad units highly profitable.
- **Why it matters**: Re-fetching ad slots every 30-45 seconds of active user interaction multiplies ad impressions per session.
- **How to apply**: Bind ad refresh triggers to `mousemove`, `keypress`, and `click` listeners using a debounced timer, refreshing only when the tab visibility state is active.

## 4. Programmatic Static SEO Architecture
- **Lesson**: Word game solvers generate millions of pageviews through long-tail programmatic pages (starts with, ends with, letter counts).
- **Why it matters**: Pre-rendering static HTML pages with client-side interactive fallback yields instant TTFB, zero backend compute costs on Cloudflare Pages, and high indexation rates.
- **How to apply**: Generate structured HTML hubs with embedded WebApplication and FAQPage schemas, and link them bidirectionally in the homepage footer/mesh.

## 5. Automated Daily Publishing via GitHub Actions
- **Lesson**: Daily puzzle search volume peaks right as new games unlock.
- **Why it matters**: Automating daily generation at 05:05 UTC via GitHub Actions + IndexNow ensures fresh content is indexed before peak morning search volume without manual intervention.

