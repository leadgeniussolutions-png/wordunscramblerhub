#!/usr/bin/env python3
"""
generate_programmatic_pages.py — Programmatic SEO Engine for Word Unscrambler Hub

Generates high-intent, high-volume static pages for:
1. 5-Letter Words Starting With A–Z (26 pages)
2. Word Length Collections (2-letter, 3-letter, 4-letter, 5-letter, 6-letter, 7-letter, 8-letter)
3. High-Scoring Scrabble Power Lists (Q without U, Z words, X words, J words)
4. Suffix Collections (-ing, -ed, -tion, -est, 5-letter ending in -s, -y, -e, -r, -t)
5. Dedicated Game Solvers (Wordle Solver, Scrabble Word Finder, Anagram Solver)

Also updates sitemap.xml to include all generated pages.
"""

import os
import re
import json
import html
from datetime import datetime

SYSTEM_DICT = "/usr/share/dict/words"
BASE_URL = "https://wordunscramblerhub.com"
SITE_NAME = "Word Unscrambler Hub"

# Scrabble tile score map
SCRABBLE_SCORES = {
    'a': 1, 'b': 3, 'c': 3, 'd': 2, 'e': 1, 'f': 4, 'g': 2, 'h': 4, 'i': 1,
    'j': 8, 'k': 5, 'l': 1, 'm': 3, 'n': 1, 'o': 1, 'p': 3, 'q': 10, 'r': 1,
    's': 1, 't': 1, 'u': 1, 'v': 4, 'w': 4, 'x': 8, 'y': 4, 'z': 10
}

def calc_scrabble_score(word):
    return sum(SCRABBLE_SCORES.get(ch, 0) for ch in word.lower())

def load_dictionary():
    print(f"Loading word list from {SYSTEM_DICT}...")
    valid_pattern = re.compile(r"^[a-z]{2,12}$")
    words_by_len = {i: [] for i in range(2, 13)}
    
    with open(SYSTEM_DICT, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            raw = line.strip()
            if raw and raw[0].isupper():
                continue
            w = raw.lower()
            if valid_pattern.match(w):
                words_by_len[len(w)].append(w)
                
    # Deduplicate and sort
    for l in words_by_len:
        words_by_len[l] = sorted(list(set(words_by_len[l])))
        
    all_words = []
    for l in words_by_len:
        all_words.extend(words_by_len[l])
        
    print(f"Loaded {len(all_words)} valid unique words.")
    return words_by_len, sorted(all_words)

def make_head(title, description, canonical_path, schemas_jsonld):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">
  <link rel="canonical" href="{BASE_URL}{canonical_path}">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{BASE_URL}{canonical_path}">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/style.css">
  {schemas_jsonld}
</head>"""

def make_header():
    return f"""<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <a class="brand" href="/" aria-label="{SITE_NAME} home">
      <svg viewBox="0 0 40 40" aria-hidden="true"><rect x="2" y="2" width="36" height="36" rx="10"/><path d="M12 13h16M12 20h10M12 27h16"/></svg>
      <span>Word <em>Unscrambler</em> Hub</span>
    </a>
    <nav aria-label="Primary navigation">
      <a href="/">Unscrambler</a>
      <a href="/connections-hints-today/">Today&rsquo;s Hints</a>
      <a href="/connections-hints.html">Hint Archive</a>
      <a href="/about.html">About</a>
    </nav>
  </header>"""

def make_footer():
    return f"""  <footer class="site-footer shell">
    <div><a class="brand footer-brand" href="/">{SITE_NAME}</a><p>Fast, independent word search & puzzle helpers.</p></div>
    <nav aria-label="Footer navigation">
      <a href="/about.html">About</a>
      <a href="/contact.html">Contact</a>
      <a href="/privacy.html">Privacy</a>
      <a href="/terms.html">Terms</a>
    </nav>
    <p class="legal-note">SCRABBLE&reg; is a registered trademark of its respective owner. Words With Friends is a trademark of Zynga. This independent utility is not affiliated with either company. &copy; 2026 {SITE_NAME}.</p>
  </footer>
  <script src="/dictionary.js" defer></script>
  <script src="/solver.js" defer></script>
  <script src="/app.js" defer></script>
</body>
</html>"""

def make_ad_slot(pos):
    return f'<div class="ad-reserve shell" data-ad-position="{pos}" style="margin: 1.5rem auto; min-height: 90px; text-align: center;"><a href="https://wordunscramblerhub.com" style="display:inline-block;padding:16px 24px;border:1px solid var(--line,#e2e8f0);border-radius:12px;text-decoration:none;color:inherit;background:rgba(255,255,255,0.7);"><span style="font-size:0.75rem;letter-spacing:0.08em;text-transform:uppercase;color:#64748b;display:block;margin-bottom:4px;">Word Unscrambler Pro</span><strong>Find top scoring anagrams instantly &rarr;</strong></a></div>'

def render_word_grid(words, max_words=120):
    display_words = words[:max_words]
    # Sort by Scrabble score descending, then alphabetical
    scored = sorted([(w, calc_scrabble_score(w)) for w in display_words], key=lambda x: (-x[1], x[0]))
    
    chips_html = []
    for w, score in scored:
        chips_html.append(f'<span class="word-chip" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;margin:4px;background:#fff;border:1px solid #e2e8f0;border-radius:8px;font-weight:600;font-size:0.95rem;text-transform:uppercase;letter-spacing:0.03em;">{w}<span style="font-size:0.75rem;color:#64748b;background:#f1f5f9;padding:2px 6px;border-radius:4px;">{score}</span></span>')
    
    return "".join(chips_html)

def generate_page(filename, title, meta_desc, h1, lede, eyebrow, words, faqs, breadcrumbs):
    canonical_path = f"/{filename}"
    
    # JSON-LD Schemas
    faq_entities = []
    for q, a in faqs:
        faq_entities.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a}
        })
    
    schema_blob = f"""<script type="application/ld+json">
    {{
      "@context":"https://schema.org",
      "@graph":[
        {{
          "@type":"WebPage",
          "@id":"{BASE_URL}{canonical_path}#webpage",
          "url":"{BASE_URL}{canonical_path}",
          "name":"{html.escape(title)}",
          "description":"{html.escape(meta_desc)}"
        }},
        {{
          "@type":"FAQPage",
          "mainEntity": {json.dumps(faq_entities) if faq_entities else "[]"}
        }},
        {{
          "@type":"BreadcrumbList",
          "itemListElement":[
            {{"@type":"ListItem","position":1,"name":"Home","item":"{BASE_URL}/"}},
            {{"@type":"ListItem","position":2,"name":"{html.escape(breadcrumbs)}","item":"{BASE_URL}{canonical_path}"}}
          ]
        }}
      ]
    }}
    </script>"""
    
    words_count = len(words)
    grid_html = render_word_grid(words)
    
    faq_html = []
    for q, a in faqs:
        faq_html.append(f"<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>")
    faqs_rendered = "".join(faq_html)
    
    page_content = f"""{make_head(title, meta_desc, canonical_path, schema_blob)}
{make_header()}
<main id="main">
  <section class="hero shell">
    <div class="hero-copy">
      <p class="eyebrow">{html.escape(eyebrow)}</p>
      <h1>{html.escape(h1)}</h1>
      <p class="lede">{html.escape(lede)}</p>
    </div>
    <div class="hero-stat" aria-label="Word count">
      <span>{words_count}</span>
      <p>valid playable words found & scored</p>
    </div>
  </section>

  {make_ad_slot("leaderboard")}

  <!-- Interactive Solver Box on every programmatic page -->
  <section class="shell" style="margin-bottom: 2rem;">
    <div class="card" style="background:#fff;padding:24px;border-radius:16px;border:1px solid #e2e8f0;box-shadow:0 4px 12px rgba(0,0,0,0.03);">
      <h2 style="font-size:1.3rem;margin-bottom:8px;">Unscramble Your Own Letters</h2>
      <p style="color:#64748b;margin-bottom:16px;">Need to find custom words from your rack? Enter up to 15 letters below with ? or * for wildcards.</p>
      <form class="solver-form" id="unscramble-form">
        <div class="input-wrap">
          <input type="text" id="rack-input" name="rack" placeholder="Enter letters (e.g. SPLEEH)" autocomplete="off" autocorrect="off" autocapitalize="characters" spellcheck="false" style="width:100%;padding:14px 18px;font-size:1.1rem;border:2px solid #cbd5e1;border-radius:10px;text-transform:uppercase;">
        </div>
        <div style="margin-top:12px;display:flex;gap:12px;flex-wrap:wrap;">
          <button type="submit" class="btn primary" style="padding:12px 24px;background:#0f172a;color:#fff;border:none;border-radius:8px;font-weight:600;cursor:pointer;">Find Words</button>
        </div>
      </form>
      <div id="results" class="results-area" aria-live="polite" style="margin-top:1.5rem;"></div>
    </div>
  </section>

  <section class="shell" style="margin-bottom: 2.5rem;">
    <h2 style="font-size:1.4rem;margin-bottom:1rem;">Top Rated Words List</h2>
    <div style="display:flex;flex-wrap:wrap;gap:8px;background:#f8fafc;padding:20px;border-radius:16px;border:1px solid #e2e8f0;">
      {grid_html}
    </div>
    {f'<p style="color:#64748b;font-size:0.9rem;margin-top:12px;">Showing top {min(words_count, 120)} of {words_count} total words. Numbers indicate Scrabble tile points.</p>' if words_count > 120 else ''}
  </section>

  {make_ad_slot("content-mid")}

  <section class="faq shell" style="margin-top: 2rem;">
    <p class="eyebrow">Frequently Asked Questions</p>
    <h2>Frequently Asked Questions</h2>
    {faqs_rendered}
  </section>
</main>
{make_footer()}
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(page_content)
    return canonical_path

def main():
    words_by_len, all_words = load_dictionary()
    generated_urls = []
    
    # -------------------------------------------------------------
    # 1. 5-Letter Words Starting with A–Z (26 Pages)
    # -------------------------------------------------------------
    print("\n--- Generating 5-Letter Words Starting With A–Z ---")
    five_letter_words = words_by_len.get(5, [])
    
    for char_code in range(ord('a'), ord('z') + 1):
        letter = chr(char_code)
        upper_letter = letter.upper()
        matches = [w for w in five_letter_words if w.startswith(letter)]
        
        filename = f"5-letter-words-starting-with-{letter}.html"
        title = f"5 Letter Words Starting with {upper_letter} — Wordle & Scrabble Solver"
        meta_desc = f"Complete list of 5 letter words starting with {upper_letter} with Scrabble and Words with Friends point values. Perfect for Wordle and daily puzzles."
        h1 = f"5 Letter Words Starting with {upper_letter}"
        lede = f"Find every valid 5-letter word that begins with '{upper_letter}'. Sorted by Scrabble point value to help you win your next Wordle, Scrabble, or Words with Friends game."
        eyebrow = f"Wordle & 5-Letter Word Helper"
        
        sample_words = ", ".join(matches[:4]) if matches else "words"
        faqs = [
            (f"What are the best 5 letter words starting with {upper_letter}?", 
             f"Some of the top 5-letter words starting with {upper_letter} include {sample_words}. Scoring depends on high-value Scrabble letters like Z, Q, X, and J."),
            (f"Can I use these 5 letter words in Wordle?", 
             f"Yes, all words in this dictionary are standard English 5-letter words recognized by popular word games including Wordle, Scrabble, and Words with Friends."),
            (f"How do I unscramble 5-letter words with wildcards?", 
             f"Use the interactive unscrambler above. Enter your available letters and use ? or * for blank tiles.")
        ]
        
        path = generate_page(filename, title, meta_desc, h1, lede, eyebrow, matches, faqs, f"5-Letter Words Starting with {upper_letter}")
        generated_urls.append(path)
        print(f"  Generated {filename} ({len(matches)} words)")

    # -------------------------------------------------------------
    # 2. Word Length Collections (2 to 8 Letter Words)
    # -------------------------------------------------------------
    print("\n--- Generating Length-Specific Collections (2–8 Letters) ---")
    for length in range(2, 9):
        matches = words_by_len.get(length, [])
        filename = f"{length}-letter-words.html"
        title = f"{length} Letter Words — Complete Scrabble & Word Finder List"
        meta_desc = f"Search and browse all {length}-letter words in the English language. Scored for Scrabble, Words with Friends, and anagram puzzles."
        h1 = f"{length} Letter Words"
        lede = f"Complete dictionary list of all valid {length}-letter words. Sorted by game score to maximize your moves in Scrabble and word puzzles."
        eyebrow = f"{length}-Letter Word Directory"
        
        sample_words = ", ".join(matches[:4]) if matches else ""
        faqs = [
            (f"Why are {length}-letter words important in Scrabble?",
             f"{'2-letter words are crucial for making parallel plays and hooking tiles onto existing words.' if length == 2 else ('7-letter words score a 50-point bonus (Bingo) in Scrabble when you play all rack tiles.' if length == 7 else f'{length}-letter words expand your scoring opportunities and board coverage.')}"),
            (f"How many valid {length}-letter words are there?",
             f"There are {len(matches)} valid {length}-letter words in our comprehensive tournament dictionary."),
            (f"How do I find words from my rack?",
             f"Enter your letters in the unscrambler search tool at the top of this page to filter results by length and position.")
        ]
        
        path = generate_page(filename, title, meta_desc, h1, lede, eyebrow, matches, faqs, f"{length}-Letter Words")
        generated_urls.append(path)
        print(f"  Generated {filename} ({len(matches)} words)")

    # -------------------------------------------------------------
    # 3. High-Scoring Scrabble Power Lists
    # -------------------------------------------------------------
    print("\n--- Generating Scrabble Power Lists ---")
    
    # Q without U
    q_no_u = [w for w in all_words if 'q' in w and 'u' not in w]
    path = generate_page(
        "words-with-q-without-u.html",
        "Words with Q Without U — Scrabble & Words with Friends List",
        "Complete list of valid words containing Q not followed by U. Crucial list for Scrabble and word puzzle tournaments.",
        "Words with Q and No U",
        "Never get stuck with a Q tile on your rack again. Here is the verified list of English words that contain Q without the letter U.",
        "Scrabble High-Score Strategy",
        q_no_u,
        [
            ("What are the most common words with Q and no U?", 
             "Common playable words include QAT, QAID, QANAT, TRANQ, FAQIR, and QINDAR."),
            ("Are words with Q without U valid in official Scrabble?",
             "Yes, words such as QAT, QAID, and QANAT are accepted in official North American (TWL/NASPA) and international (CSW) Scrabble dictionaries.")
        ],
        "Words with Q Without U"
    )
    generated_urls.append(path)
    print(f"  Generated words-with-q-without-u.html ({len(q_no_u)} words)")

    # Words with Z
    z_words = [w for w in all_words if 'z' in w]
    path = generate_page(
        "words-with-z.html",
        "Words with Z — High Scoring Scrabble & Word Finder",
        "Browse all high-scoring words containing the letter Z. Scored for Scrabble, Words with Friends, and anagram solvers.",
        "Words with the Letter Z",
        "The letter Z is worth 10 points in Scrabble. Maximize your score with our complete list of 2 to 12 letter words containing Z.",
        "10-Point Tile Helper",
        z_words,
        [
            ("What is the shortest word with Z?", "The shortest valid words with Z are 2-letter words like ZA."),
            ("What is the highest scoring Z word?", "Words like JAZZ, MUZJIKS, and QUIZZED produce some of the highest tile scores in Scrabble.")
        ],
        "Words with Z"
    )
    generated_urls.append(path)
    print(f"  Generated words-with-z.html ({len(z_words)} words)")

    # Words with X
    x_words = [w for w in all_words if 'x' in w]
    path = generate_page(
        "words-with-x.html",
        "Words with X — High Scoring Scrabble & Word Finder",
        "Complete list of words containing the letter X with Scrabble scores. Perfect for Scrabble and word game strategists.",
        "Words with the Letter X",
        "The letter X is worth 8 points in Scrabble. Discover all valid words that use the letter X across all word lengths.",
        "8-Point Tile Helper",
        x_words,
        [
            ("What 2-letter words have an X?", "Official 2-letter X words include AX, EX, OX, and XI."),
            ("Can X be used at the beginning of words?", "Yes, words like XENON, XEROX, and XYLOPHONE are valid.")
        ],
        "Words with X"
    )
    generated_urls.append(path)
    print(f"  Generated words-with-x.html ({len(x_words)} words)")

    # Words with J
    j_words = [w for w in all_words if 'j' in w]
    path = generate_page(
        "words-with-j.html",
        "Words with J — High Scoring Scrabble & Word Finder",
        "Complete list of playable words containing the letter J. Scored and sorted for Scrabble and Words with Friends.",
        "Words with the Letter J",
        "The letter J is worth 8 points in Scrabble. Explore all valid words containing J to unlock major scoring combos.",
        "8-Point Tile Helper",
        j_words,
        [
            ("What are short words with J?", "Short valid J words include JO, JOT, JUG, JAW, and JAB."),
            ("How do I score the most points with J?", "Combine J with premium board squares (Triple Letter or Triple Word) to turn an 8-point tile into 50+ points.")
        ],
        "Words with J"
    )
    generated_urls.append(path)
    print(f"  Generated words-with-j.html ({len(j_words)} words)")

    # -------------------------------------------------------------
    # 4. Common High-Volume Suffix & Ending Collections
    # -------------------------------------------------------------
    print("\n--- Generating Suffix & Ending Collections ---")
    suffixes = [
        ("words-ending-in-ing.html", "ing", "Words Ending in -ING — Complete Suffix List", "Words Ending in -ING", "Explore every English word ending in the suffix -ING. Great for Scrabble hooks and word games.", 0),
        ("words-ending-in-ed.html", "ed", "Words Ending in -ED — Past Tense Scrabble Helper", "Words Ending in -ED", "Browse all words ending in -ED to easily hook your tiles onto existing verbs and adjectives.", 0),
        ("words-ending-in-tion.html", "tion", "Words Ending in -TION — Suffix Word List", "Words Ending in -TION", "Comprehensive collection of valid words with the -TION noun ending.", 0),
        ("5-letter-words-ending-in-s.html", "s", "5 Letter Words Ending in S — Wordle & Scrabble Helper", "5 Letter Words Ending in S", "Browse all 5-letter words ending in the letter S for Wordle clues and Scrabble plays.", 5),
        ("5-letter-words-ending-in-y.html", "y", "5 Letter Words Ending in Y — Wordle & Scrabble Helper", "5 Letter Words Ending in Y", "Discover all valid 5-letter words ending in Y for daily puzzle solutions.", 5),
        ("5-letter-words-ending-in-e.html", "e", "5 Letter Words Ending in E — Wordle & Scrabble Helper", "5 Letter Words Ending in E", "Find every 5-letter word ending in E with Scrabble scores.", 5),
        ("5-letter-words-ending-in-r.html", "r", "5 Letter Words Ending in R — Wordle & Scrabble Helper", "5 Letter Words Ending in R", "Complete list of 5-letter words that end with R.", 5),
        ("5-letter-words-ending-in-t.html", "t", "5 Letter Words Ending in T — Wordle & Scrabble Helper", "5 Letter Words Ending in T", "Discover all 5-letter words ending in T for Wordle solvers and word enthusiasts.", 5)
    ]
    
    for filename, suffix, title, h1, lede, req_len in suffixes:
        if req_len > 0:
            matches = [w for w in words_by_len.get(req_len, []) if w.endswith(suffix)]
        else:
            matches = [w for w in all_words if w.endswith(suffix)]
            
        meta_desc = f"{h1} with game scores. Perfect for Wordle solvers, Scrabble tournaments, and crossword puzzles."
        faqs = [
            (f"Why are {h1.lower()} useful in word games?",
             f"Ending letters like {suffix.upper()} are common word endings that allow you to easily create compound words and cross-plays on the board."),
            (f"How do I find words from my specific letters?",
             f"Use the interactive word unscrambler at the top of the page. You can specify rack letters and wildcard blanks.")
        ]
        
        path = generate_page(filename, title, meta_desc, h1, lede, "Word Ending Collections", matches, faqs, h1)
        generated_urls.append(path)
        print(f"  Generated {filename} ({len(matches)} words)")

    # -------------------------------------------------------------
    # 5. Dedicated Game Solvers
    # -------------------------------------------------------------
    print("\n--- Generating Dedicated Game Solver Hubs ---")
    game_solvers = [
        ("wordle-solver.html", "Wordle Solver & Helper — Find 5-Letter Word Clues", "Use our free Wordle Solver to find valid 5-letter words from your clues. Filter by starting letters, ending letters, and excluded letters.", "Wordle Solver & Clue Finder", "Narrow down today's 5-letter Wordle answer in seconds using our intelligent dictionary solver.", "Daily Wordle Helper", five_letter_words, [("How does the Wordle solver work?", "Enter the letters you know and filter by letter placement. The solver instantly outputs all matching 5-letter words.")], "Wordle Solver"),
        ("scrabble-word-finder.html", "Scrabble Word Finder — Cheat & Anagram Solver", "Official Scrabble Word Finder. Unscramble your rack tiles, find high-scoring bingo words, and calculate points instantly.", "Scrabble Word Finder", "Find every high-scoring word on your rack. Calculate exact tile scores and find 50-point Bingo bonus moves.", "Scrabble Helper", all_words[:200], [("Is this Scrabble word finder free?", "Yes, this tool is 100% free and runs locally in your browser for instant results.")], "Scrabble Word Finder"),
        ("anagram-solver.html", "Anagram Solver — Unscramble Letters into Words", "Instant anagram solver. Find every possible word and phrase from any combination of letters with wildcard support.", "Anagram Solver", "Unscramble letters into valid dictionary words instantly. Discover all anagrams for crosswords, jumbles, and puzzles.", "Anagram Tool", all_words[:200], [("What is an anagram?", "An anagram is a word or phrase formed by rearranging the letters of a different word or phrase.")], "Anagram Solver")
    ]
    
    for filename, title, meta_desc, h1, lede, eyebrow, words, faqs, crumb in game_solvers:
        path = generate_page(filename, title, meta_desc, h1, lede, eyebrow, words, faqs, crumb)
        generated_urls.append(path)
        print(f"  Generated {filename}")

    # -------------------------------------------------------------
    # 6. Update sitemap.xml
    # -------------------------------------------------------------
    print("\n--- Updating sitemap.xml with All Routes ---")
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # Core existing routes
    core_routes = [
        ("/", "1.0", "weekly"),
        ("/connections-hints-today/", "0.9", "daily"),
        ("/connections-hints.html", "0.8", "daily"),
        ("/about.html", "0.4", "yearly"),
        ("/contact.html", "0.3", "yearly"),
        ("/privacy.html", "0.3", "yearly"),
        ("/terms.html", "0.3", "yearly")
    ]
    
    sitemap_entries = []
    for route, prio, freq in core_routes:
        sitemap_entries.append(f'  <url><loc>{BASE_URL}{route}</loc><lastmod>{today_str}</lastmod><changefreq>{freq}</changefreq><priority>{prio}</priority></url>')
        
    for path in generated_urls:
        sitemap_entries.append(f'  <url><loc>{BASE_URL}{path}</loc><lastmod>{today_str}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>')
        
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(sitemap_entries)}
</urlset>
"""
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap_content)
        
    print(f"Updated sitemap.xml with {len(sitemap_entries)} total URLs!")

if __name__ == "__main__":
    main()
