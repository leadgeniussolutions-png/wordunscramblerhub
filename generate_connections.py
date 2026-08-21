#!/usr/bin/env python3
"""Daily NYT Connections hints page generator.

Fetches the official puzzle JSON for a given date (default: today in
America/New_York), then writes:

  connections-hints-today/index.html      <- the daily page (canonical target)
  connections-hints/<YYYY-MM-DD>/index.html  <- permanent archive copy
  connections-hints.html                  <- archive index (rebuilt from disk)

Run daily just after midnight ET:  python3 generate_connections.py
Backfill a date:                   python3 generate_connections.py 2026-07-10
"""

import html
import json
import re
import sys
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

SITE_ROOT = Path(__file__).resolve().parent
BASE_URL = "https://wordunscramblerhub.com"  # no trailing slash
SITE_NAME = "Word Unscrambler Hub"
PUZZLE_TZ = ZoneInfo("America/New_York")
NYT_ENDPOINT = "https://www.nytimes.com/svc/connections/v2/{d}.json"

# NYT category order is always easiest -> hardest.
COLORS = [
    ("yellow", "Yellow", "the easiest group"),
    ("green", "Green", "the second-easiest group"),
    ("blue", "Blue", "the trickier group"),
    ("purple", "Purple", "the hardest group, usually wordplay"),
]


def fetch_puzzle(d: date) -> dict:
    url = NYT_ENDPOINT.format(d=d.isoformat())
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("status") != "OK" or not data.get("categories"):
        raise RuntimeError(f"Unexpected puzzle payload for {d}: {str(data)[:200]}")
    return data


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def pretty_date(d: date) -> str:
    return f"{d.strftime('%A, %B')} {d.day}, {d.year}"


def group_words(cat: dict) -> list[str]:
    return [c["content"] for c in sorted(cat["cards"], key=lambda c: c["position"])]


def page_head(title: str, description: str, canonical_path: str, extra_jsonld: list[dict]) -> str:
    jsonld = "\n".join(
        f'<script type="application/ld+json">{json.dumps(block, ensure_ascii=False)}</script>'
        for block in extra_jsonld
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{BASE_URL}{canonical_path}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{BASE_URL}{canonical_path}">
  <link rel="stylesheet" href="/style.css">
  {jsonld}
</head>"""


def site_header(active: str) -> str:
    def cur(name):
        return ' aria-current="page"' if name == active else ""
    return f"""<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <a class="brand" href="/" aria-label="{esc(SITE_NAME)} home">
      <svg viewBox="0 0 40 40" aria-hidden="true"><rect x="2" y="2" width="36" height="36" rx="10"/><path d="M12 13h16M12 20h10M12 27h16"/></svg>
      <span>Word <em>Unscrambler</em> Hub</span>
    </a>
    <nav aria-label="Primary navigation">
      <a{cur('solver')} href="/">Unscrambler</a>
      <a{cur('today')} href="/connections-hints-today/">Today&rsquo;s Hints</a>
      <a{cur('archive')} href="/connections-hints.html">Hint Archive</a>
      <a href="/about.html">About</a>
    </nav>
  </header>
"""


def site_footer(today: date) -> str:
    return f"""  <footer class="site-footer shell">
    <div><a class="brand footer-brand" href="/">Word <em>Unscrambler</em> Hub</a><p>Fast, independent helpers for word-game players.</p></div>
    <nav aria-label="Footer navigation"><a href="/about.html">About</a><a href="/contact.html">Contact</a><a href="/privacy.html">Privacy</a><a href="/terms.html">Terms</a></nav>
    <p class="legal-note">Connections is a trademark of The New York Times Company. This site is not affiliated with, endorsed by, or sponsored by The New York Times. Hints and answers are provided for reference after you have tried the puzzle yourself. &copy; {today.year} {esc(SITE_NAME)}.</p>
  </footer>
</body>
</html>
"""


def hint_ladder(categories: list[dict]) -> str:
    """Three-rung reveal: one starter word -> category themes -> full answers."""
    starters = "".join(
        f'<li><strong class="dot-{key}">{esc(label)}:</strong> one of the words in this group is <strong>{esc(group_words(cat)[0])}</strong></li>'
        for (key, label, _), cat in zip(COLORS, categories)
    )
    themes = "".join(
        f"""<details class="puzzle-group group-{key}">
        <summary>{esc(label)} group theme ({esc(hardness)})</summary>
        <p>The connection is: <strong>{esc(cat["title"].title())}</strong></p>
      </details>"""
        for (key, label, hardness), cat in zip(COLORS, categories)
    )
    answers = "".join(
        f"""<details class="puzzle-group group-{key}">
        <summary>{esc(label)}: {esc(cat["title"].title())}</summary>
        <p><strong>{esc(", ".join(group_words(cat)))}</strong></p>
      </details>"""
        for (key, label, _), cat in zip(COLORS, categories)
    )
    return f"""
      <h2 id="hints">Hint 1: one word from each group</h2>
      <p>Start here if you just need a foothold. These four words are <em>not</em> in the same group as each other.</p>
      <div class="notice"><ul style="margin:0;padding-left:1.1rem">{starters}</ul></div>

      <h2 id="themes">Hint 2: today&rsquo;s category themes</h2>
      <p>Tap a color to reveal only that group&rsquo;s theme. Reveal one at a time and go back to your grid before opening the next.</p>
      <div class="puzzle-groups">{themes}</div>

      <h2 id="answers">Today&rsquo;s Connections answers</h2>
      <p>Full spoilers below. Tap a group to reveal its four words.</p>
      <div class="puzzle-groups">{answers}</div>
"""


def strategy_and_faq(d: date, num: int) -> str:
    return f"""
      <h2 id="how-to-play">How to get better at Connections</h2>
      <ul>
        <li><strong>Find the trap first.</strong> Every puzzle plants words that fit two groups. Before guessing, spot the word that could belong to multiple categories &mdash; the purple group usually claims it.</li>
        <li><strong>Work backwards from purple.</strong> If four words share an obvious theme, be suspicious: the easy read is often the misdirect. Lock in the wordplay group first when you can see it.</li>
        <li><strong>Use your one-away wisely.</strong> A &ldquo;one away&rdquo; result tells you three of the four are right. Swap your least-confident word, not a random one.</li>
        <li><strong>Say the words out loud.</strong> Homophone and hidden-word categories (a purple favorite) are far easier to hear than to see.</li>
      </ul>

      <section class="faq" aria-labelledby="faq-title">
        <h2 id="faq-title">Connections FAQ</h2>
        <details>
          <summary>What time does a new Connections puzzle come out?</summary>
          <p>A new puzzle releases at midnight in your local time zone, every day. We publish hints for puzzle #{num + 1} shortly after midnight Eastern Time.</p>
        </details>
        <details>
          <summary>How do the four difficulty colors work?</summary>
          <p>Yellow is the most straightforward group, followed by green, then blue. Purple is the hardest and usually involves wordplay &mdash; homophones, hidden words, or words that precede/follow a common word.</p>
        </details>
        <details>
          <summary>How many mistakes are allowed in Connections?</summary>
          <p>Four. After four wrong guesses the puzzle ends and the answers are revealed. Using the hints above one rung at a time is the best way to protect your streak without spoiling the whole grid.</p>
        </details>
        <details>
          <summary>Where can I find hints for previous puzzles?</summary>
          <p>Every day&rsquo;s hints and answers stay up permanently in our <a href="/connections-hints.html">Connections hint archive</a>.</p>
        </details>
      </section>

      <p>Stuck on other word games too? Our free <a href="/">word unscrambler</a> checks every word your letters can make, instantly and privately in your browser.</p>
"""


def article_jsonld(title: str, description: str, path: str, d: date) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "datePublished": f"{d.isoformat()}T05:05:00Z",
        "dateModified": f"{d.isoformat()}T05:05:00Z",
        "mainEntityOfPage": f"{BASE_URL}{path}",
        "author": {"@type": "Organization", "name": SITE_NAME, "url": BASE_URL},
        "publisher": {"@type": "Organization", "name": SITE_NAME},
    }


def faq_jsonld(num: int) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "What time does a new Connections puzzle come out?",
                "acceptedAnswer": {"@type": "Answer", "text": "A new NYT Connections puzzle releases at midnight in your local time zone every day."},
            },
            {
                "@type": "Question",
                "name": "How do the four difficulty colors work in Connections?",
                "acceptedAnswer": {"@type": "Answer", "text": "Yellow is the easiest group, then green, then blue. Purple is the hardest and usually involves wordplay such as homophones or hidden words."},
            },
            {
                "@type": "Question",
                "name": "How many mistakes are allowed in Connections?",
                "acceptedAnswer": {"@type": "Answer", "text": "Four wrong guesses are allowed. After the fourth mistake the puzzle ends and the answers are revealed."},
            },
        ],
    }


def render_page(puzzle: dict, d: date, is_today: bool, yesterday_exists: bool) -> str:
    num = puzzle["id"]
    cats = puzzle["categories"]
    if is_today:
        path = "/connections-hints-today/"
        title = f"Connections Hint Today — NYT #{num} Hints & Answers ({d.strftime('%B')} {d.day}, {d.year})"
        h1 = "Connections hints for today"
        desc = (
            f"Gentle hints and full answers for today's NYT Connections puzzle #{num} "
            f"({pretty_date(d)}). Reveal one clue at a time — category themes first, spoilers last."
        )
    else:
        path = f"/connections-hints/{d.isoformat()}/"
        title = f"NYT Connections Hints & Answers — {d.strftime('%B')} {d.day}, {d.year} (Puzzle #{num})"
        h1 = f"Connections hints — {pretty_date(d)}"
        desc = (
            f"Hints, category themes, and full answers for NYT Connections puzzle #{num} "
            f"from {pretty_date(d)}."
        )

    yesterday_link = ""
    if yesterday_exists:
        y = d - timedelta(days=1)
        yesterday_link = f'<a class="archive-link" href="/connections-hints/{y.isoformat()}/">Yesterday&rsquo;s hints &amp; answers ({y.strftime("%B")} {y.day})</a>'

    head = page_head(title, desc, path, [article_jsonld(title, desc, path, d), faq_jsonld(num)])
    editor = puzzle.get("editor", "")
    editor_line = f"<span>Edited by {esc(editor)}</span>" if editor else ""

    return f"""{head}
{site_header('today' if is_today else 'archive')}
  <main id="main">
    <article class="article-page">
      <p class="eyebrow">NYT Connections &middot; Puzzle #{num}</p>
      <h1>{esc(h1)}</h1>
      <div class="article-meta">
        <time datetime="{d.isoformat()}">{esc(pretty_date(d))}</time>
        {editor_line}
        <span>Hints first, spoilers last</span>
      </div>

      <p>Need a nudge on {"today&rsquo;s" if is_today else "this"} Connections grid without wrecking the fun? Work down the ladder below: start with a single word from each group, reveal a category theme only if you&rsquo;re still stuck, and open the full answers as a last resort. Nothing is spoiled until you tap it.</p>

      <div class="notice"><strong>Jump to:</strong> <a href="#hints">Word hints</a> &middot; <a href="#themes">Category themes</a> &middot; <a href="#answers">Full answers</a></div>

      {hint_ladder(cats)}

      {strategy_and_faq(d, num)}

      <p>{yesterday_link}</p>
      <p><a class="archive-link" href="/connections-hints.html">Browse the full Connections hint archive</a></p>
    </article>
  </main>
{site_footer(d)}"""


def rebuild_archive_index(today: date) -> None:
    archive_dir = SITE_ROOT / "connections-hints"
    entries = sorted(
        (p.name for p in archive_dir.iterdir() if p.is_dir() and re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.name)),
        reverse=True,
    ) if archive_dir.exists() else []

    items = "".join(
        f'<li><a href="/connections-hints/{name}/">Connections hints &amp; answers &mdash; {esc(pretty_date(date.fromisoformat(name)))}</a></li>'
        for name in entries
    )
    title = "NYT Connections Hints Archive — Every Puzzle's Clues & Answers"
    desc = "Browse hints, category themes, and answers for every past NYT Connections puzzle, organized by date."
    head = page_head(title, desc, "/connections-hints.html", [])
    page = f"""{head}
{site_header('archive')}
  <main id="main">
    <article class="article-page">
      <p class="eyebrow">Archive</p>
      <h1>Connections hints, every day</h1>
      <p>Missed a puzzle or checking an old streak? Every day&rsquo;s hints and answers stay up permanently. For the current puzzle, see <a href="/connections-hints-today/">today&rsquo;s hints</a>.</p>
      <ul>{items}</ul>
    </article>
  </main>
{site_footer(today)}"""
    (SITE_ROOT / "connections-hints.html").write_text(page, encoding="utf-8")


def main() -> None:
    if len(sys.argv) > 1:
        d = date.fromisoformat(sys.argv[1])
    else:
        d = datetime.now(PUZZLE_TZ).date()

    print(f"Fetching Connections puzzle for {d} ...")
    puzzle = fetch_puzzle(d)
    print(f"  Puzzle #{puzzle['id']}: {', '.join(c['title'] for c in puzzle['categories'])}")

    archive_path = SITE_ROOT / "connections-hints" / d.isoformat()
    archive_path.mkdir(parents=True, exist_ok=True)
    yesterday_exists = (SITE_ROOT / "connections-hints" / (d - timedelta(days=1)).isoformat() / "index.html").exists()

    is_current = d == datetime.now(PUZZLE_TZ).date()
    if is_current:
        today_dir = SITE_ROOT / "connections-hints-today"
        today_dir.mkdir(exist_ok=True)
        (today_dir / "index.html").write_text(render_page(puzzle, d, True, yesterday_exists), encoding="utf-8")
        print(f"  Wrote {today_dir / 'index.html'}")

    (archive_path / "index.html").write_text(render_page(puzzle, d, False, yesterday_exists), encoding="utf-8")
    print(f"  Wrote {archive_path / 'index.html'}")

    rebuild_archive_index(d)
    print("  Rebuilt connections-hints.html archive index")
    print("Done.")


if __name__ == "__main__":
    main()
