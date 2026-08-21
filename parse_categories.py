#!/usr/bin/env python3
import json
import re

def main():
    with open("keyword_suggestions_raw.json") as f:
        data = json.load(f)
        
    categories = {
        "Core Brand / Tool Terms": [],
        "Length-Specific Solvers": [],
        "Letter-Specific Lists (Starts/Ends/Contains)": [],
        "Game-Specific Solvers (Scrabble, Wordle, WWF)": [],
        "Other Utility terms": []
    }
    
    for item in data:
        kw = item["keyword"].lower()
        vol = item["search_volume"] or 0
        diff = item["difficulty"]
        
        # We classify based on regex
        if re.search(r"\b(word unscrambler|anagram solver|jumble solver|word solver|word scramble|scramble word)\b", kw):
            if re.search(r"\b(3|4|5|6|7|8|9|three|four|five|six|seven|eight|nine)\s*-?\s*letter\b", kw):
                categories["Length-Specific Solvers"].append(item)
            else:
                categories["Core Brand / Tool Terms"].append(item)
        elif re.search(r"\b(scrabble|wordle|words with friends|wwf)\b", kw):
            categories["Game-Specific Solvers (Scrabble, Wordle, WWF)"].append(item)
        elif re.search(r"\b(words? (starting|ending|containing|with))\b", kw) or re.search(r"\bwords? (that )?(start|end|have)\b", kw):
            categories["Letter-Specific Lists (Starts/Ends/Contains)"].append(item)
        else:
            if re.search(r"\b(3|4|5|6|7|8|9|three|four|five|six|seven|eight|nine)\s*-?\s*letter\b", kw):
                categories["Length-Specific Solvers"].append(item)
            else:
                categories["Other Utility terms"].append(item)
                
    # Sort each category by volume
    for cat in categories:
        categories[cat] = sorted(categories[cat], key=lambda x: x["search_volume"] or 0, reverse=True)
        
    # Print a summary
    print("--- Categorization Summary ---")
    for cat, items in categories.items():
        unique_kws = list({i["keyword"]: i for i in items}.values())
        print(f"{cat}: {len(unique_kws)} unique keywords. Top 5:")
        for i in unique_kws[:5]:
            print(f"  - '{i['keyword']}' (Vol: {i['search_volume']}, KD: {i['difficulty']})")
            
    # Save the categorization
    with open("keyword_categories.json", "w") as f:
        json.dump(categories, f, indent=2)

if __name__ == "__main__":
    main()
