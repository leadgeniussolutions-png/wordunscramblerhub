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
