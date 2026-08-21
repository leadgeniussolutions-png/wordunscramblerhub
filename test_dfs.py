#!/usr/bin/env python3
import json
import requests
from requests.auth import HTTPBasicAuth

DFS_KEY_PATH = "/Users/lgs/.config/dataforseo/auth.json"

with open(DFS_KEY_PATH) as f:
    auth = json.load(f)

login = auth.get("login")
password = auth.get("password")

url = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"

keywords = [
    "youtube tv",
    "vini jr",
    "new jersey weather",
    "norway royal family",
    "fox one",
    "erling haaland",
    "bruno guimarães",
    "neymar"
]

payload = []
for kw in keywords:
    payload.append({
        "keyword": kw,
        "location_name": "United States",
        "language_name": "English",
        "device": "desktop"
    })

res = requests.post(url, json=payload, auth=HTTPBasicAuth(login, password))
data = res.json()

print("Overall Status Code:", data.get("status_code"))
print("Tasks count:", len(data.get("tasks", [])))

for idx, task in enumerate(data.get("tasks", [])):
    kw_requested = payload[idx]["keyword"]
    print(f"Task {idx}: Requested Kw: '{kw_requested}'")
    print(f"  Status Code: {task.get('status_code')}")
    print(f"  Status Message: {task.get('status_message')}")
    if "result" in task and task["result"]:
        r = task["result"][0]
        print(f"  Result Kw: '{r.get('keyword')}'")
        print(f"  Items: {len(r.get('items', []))}")
    else:
        print(f"  No result or empty")
