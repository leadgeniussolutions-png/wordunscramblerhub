#!/usr/bin/env python3
import os
import sys
import json
import requests
import xml.etree.ElementTree as ET
from requests.auth import HTTPBasicAuth
from urllib.parse import urlparse

# Credential Paths
DFS_KEY_PATH = "/Users/lgs/.config/dataforseo/auth.json"

def fetch_google_trends():
    """
    Fetches the daily trending searches in the US from Google Trends RSS.
    Returns a list of dicts: [{'keyword': str, 'traffic': str, 'description': str}]
    """
    print("Fetching daily Google Trends from RSS...")
    url = "https://trends.google.com/trending/rss?geo=US"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        channel = root.find("channel")
        items = channel.findall("item")
        
        trends = []
        # Google Trends namespace for ht:approx_traffic
        ns = {"ht": "https://trends.google.com/trending/rss"}
        
        for item in items:
            title = item.find("title").text if item.find("title") is not None else ""
            traffic = item.find("ht:approx_traffic", ns).text if item.find("ht:approx_traffic", ns) is not None else "Unknown"
            description = item.find("description").text if item.find("description") is not None else ""
            
            if title:
                trends.append({
                    "keyword": title,
                    "traffic": traffic,
                    "description": description
                })
        
        print(f"Successfully fetched {len(trends)} trending keywords from Google Trends.")
        return trends
    except Exception as e:
        print(f"Error fetching Google Trends: {e}")
        return []

def get_serp_dataforseo(keywords, auth_path):
    """
    Uses DataForSEO to search Google for the keywords and find top organic results.
    """
    print(f"Querying DataForSEO organic SERPs for {len(keywords)} keywords individually...")
    try:
        if not os.path.exists(auth_path):
            print(f"DataForSEO auth file not found at {auth_path}")
            return {}
            
        with open(auth_path) as f:
            auth = json.load(f)
        
        login = auth.get("login")
        password = auth.get("password")
        if not login or not password:
            print("Credentials missing login/password keys")
            return {}
            
        url = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"
        results = {}
        
        for kw in keywords:
            payload = [{
                "keyword": kw,
                "location_name": "United States",
                "language_name": "English",
                "device": "desktop",
                "depth": 10  # Only get top 10 results to keep it fast
            }]
            
            try:
                res = requests.post(url, json=payload, auth=HTTPBasicAuth(login, password), timeout=30)
                res_json = res.json()
                
                if res_json.get("status_code") != 20000:
                    print(f"  DataForSEO error for '{kw}': {res_json.get('status_message')}")
                    continue
                    
                tasks = res_json.get("tasks", [])
                for task in tasks:
                    if task.get("status_code") != 20000:
                        continue
                    for r in task.get("result", []):
                        items = r.get("items", [])
                        organic_sites = []
                        for item in items:
                            if item.get("type") == "organic":
                                title = item.get("title")
                                site_url = item.get("url")
                                domain = item.get("domain")
                                description = item.get("description")
                                rank = item.get("rank_absolute")
                                
                                organic_sites.append({
                                    "rank": rank,
                                    "title": title,
                                    "url": site_url,
                                    "domain": domain,
                                    "description": description
                                })
                        results[kw] = organic_sites
            except Exception as e:
                print(f"  Error querying keyword '{kw}': {e}")
                
        return results
    except Exception as e:
        print(f"DataForSEO error: {e}")
        return {}


def check_adsense_monetization(domain):
    """
    Checks if a domain uses Google AdSense by hitting its homepage and inspecting it.
    Returns: (uses_adsense: bool, ad_client_id: str/None)
    """
    # Exclude giant platforms that do not use standard AdSense
    major_platforms = [
        "wikipedia.org", "youtube.com", "facebook.com", "instagram.com", "twitter.com",
        "x.com", "linkedin.com", "amazon.com", "reddit.com", "pinterest.com", "netflix.com",
        "apple.com", "microsoft.com", "google.com", "github.com", "nytimes.com", "cnn.com",
        "imdb.com", "espn.com", "weather.com", "yahoo.com", "ebay.com", "walmart.com",
        "target.com", "etsy.com", "tripadvisor.com"
    ]
    if domain.lower() in major_platforms or any(domain.lower().endswith("." + p) for p in major_platforms):
        return False, None
        
    url = f"http://{domain}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # 1. Try checking ads.txt first - it is the most reliable signature
    ads_txt_url = f"http://{domain}/ads.txt"
    try:
        r = requests.get(ads_txt_url, headers=headers, timeout=5, allow_redirects=True)
        if r.status_code == 200 and "google.com" in r.text.lower():
            # Parse publisher ID
            import re
            match = re.search(r"google\.com,\s*(pub-\d+)", r.text, re.I)
            if match:
                return True, match.group(1)
            return True, "pub-found-in-ads.txt"
    except Exception:
        pass

    # 2. If ads.txt doesn't resolve or work, check homepage HTML
    try:
        r = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
        if r.status_code == 200:
            html = r.text
            # Look for AdSense client tags
            import re
            pub_match = re.search(r"ca-pub-\d+", html)
            if pub_match:
                return True, pub_match.group(0)
            
            # General script tags
            if "adsbygoogle" in html or "pagead2.googlesyndication" in html:
                return True, "AdSense JS Found"
    except Exception:
        pass
        
    return False, None

def analyze_and_report():
    trends = fetch_google_trends()
    if not trends:
        print("No trending keywords fetched. Exiting.")
        return
        
    # Get top 8 trends to analyze to keep it fast
    selected_trends = trends[:8]
    keywords = [t["keyword"] for t in selected_trends]
    
    serp_data = get_serp_dataforseo(keywords, DFS_KEY_PATH)
    
    # Compile findings
    report_items = []
    
    for trend in selected_trends:
        kw = trend["keyword"]
        traffic = trend["traffic"]
        desc = trend["description"]
        
        print(f"\nAnalyzing Trend: '{kw}' (Traffic: {traffic})")
        
        sites = serp_data.get(kw, [])
        adsense_sites = []
        all_sites_info = []
        
        # Check top 6 organic sites for each trend to see if they monetize with AdSense
        for site in sites[:6]:
            domain = site["domain"]
            url = site["url"]
            title = site["title"]
            
            uses_adsense, pub_id = check_adsense_monetization(domain)
            
            site_info = {
                "rank": site["rank"],
                "title": title,
                "domain": domain,
                "url": url,
                "uses_adsense": uses_adsense,
                "pub_id": pub_id
            }
            all_sites_info.append(site_info)
            if uses_adsense:
                adsense_sites.append(site_info)
                print(f"  [AdSense Found] {domain} (ID: {pub_id})")
            else:
                print(f"  [No AdSense] {domain}")
                
        report_items.append({
            "keyword": kw,
            "traffic": traffic,
            "description": desc,
            "adsense_sites": adsense_sites,
            "all_sites": all_sites_info
        })
        
    # Generate Markdown Report
    generate_markdown_report(report_items)

def generate_markdown_report(report_items):
    md_content = []
    md_content.append("# Google Trends & AdSense Monetization Analysis\n")
    md_content.append("Analysis of real-time trending keywords in the United States, ranking websites, and their AdSense implementation.\n")
    md_content.append("## Executive Summary\n")
    
    adsense_count = 0
    total_sites_checked = 0
    adsense_domains = set()
    
    for item in report_items:
        total_sites_checked += len(item["all_sites"])
        for s in item["adsense_sites"]:
            adsense_count += 1
            adsense_domains.add(s["domain"])
            
    md_content.append(f"- **Total Trends Analyzed**: {len(report_items)}")
    md_content.append(f"- **Total Ranking Websites Analyzed**: {total_sites_checked}")
    md_content.append(f"- **Websites Monetized via AdSense**: {adsense_count} ({len(adsense_domains)} unique domains)")
    md_content.append(f"- **AdSense Penetration Rate**: {((adsense_count / total_sites_checked) * 100):.1f}% of top organic ranking results (excluding major platforms like Wikipedia/social media)\n")
    
    md_content.append("## Trending Niches & Monetized Competitors\n")
    
    for item in report_items:
        md_content.append(f"### Trend: **{item['keyword']}**")
        md_content.append(f"- **Daily Search Volume**: `{item['traffic']}`")
        if item['description']:
            md_content.append(f"- **Context**: {item['description']}\n")
            
        md_content.append("| Rank | Website Domain | Page Title | AdSense Status | Publisher ID / Signature |")
        md_content.append("| :--- | :--- | :--- | :--- | :--- |")
        
        for site in item["all_sites"]:
            status_emoji = "✅ Yes" if site["uses_adsense"] else "❌ No"
            pub_id_str = f"`{site['pub_id']}`" if site["pub_id"] else "-"
            # Shorten title if too long
            title_short = site["title"][:50] + "..." if len(site["title"]) > 50 else site["title"]
            md_content.append(f"| {site['rank']} | [{site['domain']}](http://{site['domain']}) | {title_short} | {status_emoji} | {pub_id_str} |")
            
        md_content.append("\n")
        
    md_content.append("## Actionable Insights for Starting a Business\n")
    md_content.append("### 1. Identify Utility & Directory Opportunities")
    md_content.append("High-traffic websites using AdSense are often utility sites (calculators, unscramblers, file converters) or directory sites (local business listings, specialized directories). These websites have low content-maintenance overhead and can generate passive revenue once ranked.")
    
    md_content.append("### 2. Micro-Niche Targeting")
    md_content.append("Instead of broad categories, target narrow, high-CPC queries that appear in search trends (e.g., specific software tutorials, niche finance tools). Using Google Trends to find rising topics allows you to create targeted pages before major competitors catch up.")
    
    md_content.append("### 3. SEO-Driven Traffic Acquisition")
    md_content.append("Build site architectures optimized for SEO (perfect heading structures, clean schema, fast loading times on Cloudflare Pages) to win top positions for organic trends. Combining display ads (AdSense) with high-value local lead gen leads to diversified monetization streams.")
    
    output_path = "/Users/lgs/.gemini/antigravity-ide/brain/1c32b9fb-6cb7-4e69-8491-2cd10335b91e/research_notes.md"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(md_content))
        
    print(f"\nReport successfully generated and saved to {output_path}")

if __name__ == "__main__":
    analyze_and_report()
