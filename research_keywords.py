#!/usr/bin/env python3
import os
import sys
import json
import requests
from requests.auth import HTTPBasicAuth

DFS_KEY_PATH = "/Users/lgs/.config/dataforseo/auth.json"

def get_keyword_suggestions(seeds, auth_path):
    print(f"Querying DataForSEO Keyword Suggestions for seeds: {seeds}...")
    try:
        if not os.path.exists(auth_path):
            print(f"DataForSEO auth file not found at {auth_path}")
            return []
            
        with open(auth_path) as f:
            auth = json.load(f)
        
        login = auth.get("login")
        password = auth.get("password")
        if not login or not password:
            print("Credentials missing login/password keys")
            return []
            
        url = "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_suggestions/live"
        all_suggestions = []
        
        for seed in seeds:
            payload = [{
                "keyword": seed,
                "location_name": "United States",
                "language_name": "English",
                "limit": 300,
                "include_clickstream_data": True
            }]
            
            try:
                response = requests.post(url, json=payload, auth=HTTPBasicAuth(login, password), timeout=30)
                data = response.json()
                
                if data.get("status_code") != 20000:
                    print(f"  DataForSEO error for '{seed}': {data.get('status_message')}")
                    continue
                    
                tasks = data.get("tasks", [])
                for task in tasks:
                    if task.get("status_code") != 20000:
                        print(f"  Task error for '{seed}': {task.get('status_message')}")
                        continue
                    for r in task.get("result", []):
                        items = r.get("items", [])
                        print(f"  Fetched {len(items)} suggestions for seed keyword '{seed}'")
                        for item in items:
                            kw_info = item.get("keyword_info", {}) or {}
                            kw_props = item.get("keyword_properties", {}) or {}
                            
                            # Extraction
                            keyword = item.get("keyword")
                            search_volume = kw_info.get("search_volume", 0)
                            cpc = kw_info.get("cpc", 0.0)
                            competition = kw_info.get("competition", 0.0)
                            difficulty = kw_props.get("keyword_difficulty", None)
                            search_intent = item.get("search_intent_info", {}).get("intent_type", "N/A") if item.get("search_intent_info") else "N/A"
                            
                            all_suggestions.append({
                                "keyword": keyword,
                                "search_volume": search_volume,
                                "cpc": cpc,
                                "competition": competition,
                                "difficulty": difficulty,
                                "intent": search_intent,
                                "seed": seed
                            })
            except Exception as e:
                print(f"  Error querying seed '{seed}': {e}")
                
        return all_suggestions
    except Exception as e:
        print(f"Error querying DataForSEO: {e}")
        return []

def main():
    raw_path = "keyword_suggestions_raw.json"
    seeds = ["word scramble", "word unscrambler", "anagram solver", "scrabble word finder", "jumble solver"]
    
    if os.path.exists(raw_path):
        print(f"Loading raw suggestions from local file {raw_path}...")
        with open(raw_path) as f:
            results = json.load(f)
    else:
        results = get_keyword_suggestions(seeds, DFS_KEY_PATH)
        
    if not results:
        print("No keyword suggestions fetched.")
        return
        
    # Save raw results
    raw_path = "keyword_suggestions_raw.json"
    with open(raw_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved {len(results)} raw suggestions to {raw_path}")
    
    # Filter for low difficulty and high search volume
    # Let's define "low difficulty" as difficulty <= 40 (out of 100), and search volume >= 500
    winnable_keywords = []
    high_volume_keywords = []
    
    for kw in results:
        diff = kw["difficulty"]
        vol = kw["search_volume"]
        
        # Ensure vol is treated as integer (default to 0 if None)
        vol_val = vol if vol is not None else 0
        
        # Keep track of high volume keywords
        if vol_val >= 1000:
            high_volume_keywords.append(kw)
            
        if diff is not None and diff <= 45 and vol_val >= 1000:
            winnable_keywords.append(kw)
            
    # Sort winnable by search volume descending
    winnable_sorted = sorted(winnable_keywords, key=lambda x: x["search_volume"], reverse=True)
    # Sort high volume by volume descending
    high_volume_sorted = sorted(high_volume_keywords, key=lambda x: x["search_volume"], reverse=True)
    
    print(f"Found {len(winnable_sorted)} winnable keywords (Difficulty <= 45, Volume >= 1000)")
    
    # Save processed analysis
    analysis = {
        "summary": {
            "total_suggestions": len(results),
            "winnable_count": len(winnable_sorted),
            "high_volume_count": len(high_volume_sorted)
        },
        "winnable": winnable_sorted[:100],
        "high_volume": high_volume_sorted[:100]
    }
    
    analysis_path = "keyword_analysis_processed.json"
    with open(analysis_path, "w") as f:
        json.dump(analysis, f, indent=2)
    print(f"Saved processed analysis to {analysis_path}")

if __name__ == "__main__":
    main()
