import os
import sys
import json
import logging
import subprocess
import datetime
from flask import Flask, jsonify, request
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
app = Flask(__name__)

REPO_URL = "https://github.com/leadgeniussolutions-png/wordunscramblerhub.git"
WORK_DIR = "/tmp/wordunscramblerhub"
DOMAIN = "wordunscramblerhub.com"
INDEXNOW_KEY = "8f4b23c91d8a47e290f6b5a3c1e2d4b5"
SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

execution_history = []

def record_execution(agent_name, status, details):
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "agent": agent_name,
        "status": status,
        "details": details
    }
    execution_history.append(entry)
    if len(execution_history) > 50:
        execution_history.pop(0)

def ensure_repo():
    """Clones or pulls the latest repository code."""
    auth_repo = REPO_URL
    if GITHUB_TOKEN:
        auth_repo = f"https://x-access-token:{GITHUB_TOKEN}@github.com/leadgeniussolutions-png/wordunscramblerhub.git"
        
    if not os.path.exists(WORK_DIR):
        logging.info(f"Cloning repository into {WORK_DIR}...")
        subprocess.run(["git", "clone", auth_repo, WORK_DIR], check=True)
        subprocess.run(["git", "config", "user.name", "Google Cloud Autopilot Agent"], cwd=WORK_DIR, check=True)
        subprocess.run(["git", "config", "user.email", "cloud-autopilot@leadgeniussolutions.com"], cwd=WORK_DIR, check=True)
    else:
        logging.info(f"Pulling latest changes in {WORK_DIR}...")
        subprocess.run(["git", "pull", "--rebase"], cwd=WORK_DIR, check=True)

def push_changes(commit_msg):
    """Commits and pushes changes if any are present."""
    status = subprocess.run(["git", "status", "--porcelain"], cwd=WORK_DIR, capture_output=True, text=True).stdout.strip()
    if not status:
        logging.info("No file changes detected to commit.")
        return False
        
    subprocess.run(["git", "add", "."], cwd=WORK_DIR, check=True)
    subprocess.run(["git", "commit", "-m", commit_msg], cwd=WORK_DIR, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=WORK_DIR, check=True)
    logging.info("Successfully pushed changes to GitHub.")
    return True

def ping_indexnow(urls):
    payload = {
        "host": DOMAIN,
        "key": INDEXNOW_KEY,
        "keyLocation": f"https://{DOMAIN}/{INDEXNOW_KEY}.txt",
        "urlList": urls
    }
    results = {}
    for ep in ["https://api.indexnow.org/indexnow", "https://www.bing.com/indexnow", "https://yandex.com/indexnow"]:
        try:
            res = requests.post(ep, json=payload, timeout=10)
            results[ep] = f"{res.status_code} {res.reason}"
        except Exception as e:
            results[ep] = f"Error: {e}"
    return results

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "wordunscrambler-autopilot"}), 200

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "service": "wordunscrambler-autopilot",
        "domain": DOMAIN,
        "gcp_project": os.environ.get("GCP_PROJECT", "unified-runner-456102-g5"),
        "total_executions": len(execution_history),
        "recent_history": execution_history[-10:]
    }), 200

@app.route("/agents/daily-publisher", methods=["POST"])
def daily_publisher():
    """Agent 1: Daily NYT puzzle solver, publisher, and indexer."""
    logging.info("🚀 [Agent 1: Daily Publisher] Starting execution...")
    try:
        ensure_repo()
        
        # Execute generate_connections.py
        proc = subprocess.run(["python3", "generate_connections.py"], cwd=WORK_DIR, capture_output=True, text=True, check=True)
        logging.info(proc.stdout)
        
        pushed = push_changes(f"Auto-update daily NYT Connections hints for {datetime.date.today().isoformat()} [skip ci]")
        
        # Ping search engines
        urls = [
            f"https://{DOMAIN}/",
            f"https://{DOMAIN}/connections-hints-today/",
            f"https://{DOMAIN}/connections-hints.html"
        ]
        indexnow_res = ping_indexnow(urls)
        
        details = {
            "pushed_to_github": pushed,
            "indexnow": indexnow_res,
            "stdout": proc.stdout.strip()
        }
        record_execution("Daily Publisher", "SUCCESS", details)
        return jsonify({"success": True, "agent": "Daily Publisher", "details": details}), 200
        
    except Exception as e:
        err_msg = str(e)
        logging.error(f"❌ [Agent 1 Error]: {err_msg}")
        record_execution("Daily Publisher", "FAILED", {"error": err_msg})
        return jsonify({"success": False, "agent": "Daily Publisher", "error": err_msg}), 500

@app.route("/agents/programmatic-expander", methods=["POST"])
def programmatic_expander():
    """Agent 2: Programmatic SEO batch generator."""
    logging.info("🚀 [Agent 2: Programmatic Expander] Starting batch generation...")
    try:
        ensure_repo()
        
        proc = subprocess.run(["python3", "generate_programmatic_pages.py"], cwd=WORK_DIR, capture_output=True, text=True, check=True)
        logging.info(proc.stdout)
        
        pushed = push_changes(f"Programmatic SEO batch update — {datetime.date.today().isoformat()}")
        
        # Parse sitemap to get newly added URLs
        sitemap_path = os.path.join(WORK_DIR, "sitemap.xml")
        urls = []
        if os.path.exists(sitemap_path):
            import re
            with open(sitemap_path) as f:
                urls = re.findall(r'<loc>\s*([^<\s]+)\s*</loc>', f.read())
                
        indexnow_res = ping_indexnow(urls) if urls else {}
        
        details = {
            "pushed_to_github": pushed,
            "total_urls_in_sitemap": len(urls),
            "indexnow": indexnow_res
        }
        record_execution("Programmatic Expander", "SUCCESS", details)
        return jsonify({"success": True, "agent": "Programmatic Expander", "details": details}), 200
        
    except Exception as e:
        err_msg = str(e)
        logging.error(f"❌ [Agent 2 Error]: {err_msg}")
        record_execution("Programmatic Expander", "FAILED", {"error": err_msg})
        return jsonify({"success": False, "agent": "Programmatic Expander", "error": err_msg}), 500

@app.route("/agents/gsc-optimizer", methods=["POST"])
def gsc_optimizer():
    """Agent 3: GSC Performance & Opportunity Analyzer."""
    logging.info("🚀 [Agent 3: GSC Optimizer] Analyzing search console performance...")
    try:
        ensure_repo()
        
        proc = subprocess.run(["python3", "optimizer_agent.py"], cwd=WORK_DIR, capture_output=True, text=True)
        output_text = proc.stdout
        
        details = {
            "output": output_text.strip()
        }
        record_execution("GSC Optimizer", "SUCCESS", details)
        return jsonify({"success": True, "agent": "GSC Optimizer", "details": details}), 200
        
    except Exception as e:
        err_msg = str(e)
        logging.error(f"❌ [Agent 3 Error]: {err_msg}")
        record_execution("GSC Optimizer", "FAILED", {"error": err_msg})
        return jsonify({"success": False, "agent": "GSC Optimizer", "error": err_msg}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
