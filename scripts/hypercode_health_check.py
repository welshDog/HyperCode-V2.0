#!/usr/bin/env python3
"""
🩺 BROski Health Check — HyperCode V2.0
Runs a full diagnostic on local services + GitHub status
Usage: python scripts/hypercode_health_check.py
"""

import socket
import subprocess
import sys
import urllib.request
import urllib.error
import json
from datetime import datetime

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
GITHUB_REPO = "welshDog/HyperCode-V2.0"

SERVICES = [
    {"name": "🧠 HyperCode Backend",   "host": "localhost", "port": 8000, "path": "/health"},
    {"name": "🩺 Healer Agent",         "host": "localhost", "port": 8008, "path": "/health"},
    {"name": "🎛️  Crew Orchestrator",   "host": "localhost", "port": 8081, "path": "/health"},
    {"name": "🖥️  BROski Terminal",      "host": "localhost", "port": 3000, "path": "/"},
    {"name": "📊 Mission Control",      "host": "localhost", "port": 8088, "path": "/"},
    {"name": "📈 Grafana",              "host": "localhost", "port": 3001, "path": "/"},
    {"name": "🗄️  Redis",               "host": "localhost", "port": 6379, "path": None},
    {"name": "🐘 PostgreSQL",           "host": "localhost", "port": 5432, "path": None},
]

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):   print(f"  {GREEN}✅ {msg}{RESET}")
def fail(msg): print(f"  {RED}❌ {msg}{RESET}")
def warn(msg): print(f"  {YELLOW}⚠️  {msg}{RESET}")
def info(msg): print(f"  {CYAN}ℹ️  {msg}{RESET}")
def header(msg): print(f"\n{BOLD}{CYAN}{msg}{RESET}")

# ─────────────────────────────────────────
# CHECK 1 — TCP PORT ALIVE?
# ─────────────────────────────────────────
def check_port(host, port, timeout=2):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

# ─────────────────────────────────────────
# CHECK 2 — HTTP ENDPOINT ALIVE?
# ─────────────────────────────────────────
def check_http(host, port, path, timeout=3):
    url = f"http://{host}:{port}{path}"
    try:
        req = urllib.request.urlopen(url, timeout=timeout)
        return req.status, True
    except urllib.error.HTTPError as e:
        return e.code, True  # port alive, HTTP error
    except Exception:
        return None, False

# ─────────────────────────────────────────
# CHECK 3 — DOCKER STATUS
# ─────────────────────────────────────────
def check_docker():
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            containers = [c for c in result.stdout.strip().split("\n") if c]
            return True, containers
        return False, []
    except Exception:
        return False, []

# ─────────────────────────────────────────
# CHECK 4 — GITHUB LATEST COMMIT
# ─────────────────────────────────────────
def check_github():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/commits/main"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BROski-HealthCheck/1.0"})
        response = urllib.request.urlopen(req, timeout=5)
        data = json.loads(response.read())
        msg = data["commit"]["message"].split("\n")[0][:60]
        date = data["commit"]["author"]["date"]
        sha = data["sha"][:7]
        return True, sha, msg, date
    except Exception as e:
        return False, None, str(e), None

# ─────────────────────────────────────────
# CHECK 5 — GITHUB CI STATUS
# ─────────────────────────────────────────
def check_github_ci():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs?per_page=1"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BROski-HealthCheck/1.0"})
        response = urllib.request.urlopen(req, timeout=5)
        data = json.loads(response.read())
        if data["workflow_runs"]:
            run = data["workflow_runs"][0]
            return True, run["status"], run["conclusion"], run["name"]
        return True, "unknown", "none", "No runs found"
    except Exception as e:
        return False, None, None, str(e)

# ─────────────────────────────────────────
# MAIN REPORT
# ─────────────────────────────────────────
def main():
    print(f"\n{BOLD}{'='*55}")
    print(f"  🩺 BROski♾ HYPERCODE HEALTH CHECK")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}{RESET}")

    score = 0
    total = 0

    # ── LOCAL SERVICES ──
    header("🖥️  LOCAL SERVICES")
    for svc in SERVICES:
        total += 1
        port_alive = check_port(svc["host"], svc["port"])

        if not port_alive:
            fail(f"{svc['name']} — port {svc['port']} OFFLINE")
            continue

        if svc["path"]:
            status_code, http_alive = check_http(svc["host"], svc["port"], svc["path"])
            if http_alive:
                ok(f"{svc['name']} — port {svc['port']} ONLINE (HTTP {status_code})")
                score += 1
            else:
                warn(f"{svc['name']} — port {svc['port']} open but HTTP failed")
                score += 0.5
        else:
            ok(f"{svc['name']} — port {svc['port']} ONLINE")
            score += 1

    # ── DOCKER ──
    header("🐋 DOCKER STATUS")
    total += 1
    docker_alive, containers = check_docker()
    if docker_alive:
        ok(f"Docker engine ONLINE — {len(containers)} container(s) running")
        score += 1
        if containers:
            for c in containers[:8]:
                info(f"  └─ {c}")
        else:
            warn("No containers running — try: docker-compose up -d")
    else:
        fail("Docker engine OFFLINE or not responding")
        warn("Fix: restart Docker Desktop from system tray")

    # ── GITHUB ──
    header("🐙 GITHUB STATUS")
    total += 1
    gh_ok, sha, msg, date = check_github()
    if gh_ok:
        ok(f"Latest commit: [{sha}] {msg}")
        info(f"Pushed: {date}")
        score += 1
    else:
        fail(f"GitHub API unreachable: {msg}")

    # ── CI/CD ──
    total += 1
    ci_ok, status, conclusion, name = check_github_ci()
    if ci_ok:
        if conclusion == "success":
            ok(f"CI Pipeline: {name} — {conclusion.upper()} ✅")
            score += 1
        elif conclusion in ("failure", "cancelled"):
            fail(f"CI Pipeline: {name} — {conclusion.upper()}")
        elif status == "in_progress":
            warn(f"CI Pipeline: {name} — RUNNING... ⏳")
            score += 0.5
        else:
            warn(f"CI Pipeline: {name} — {status} / {conclusion}")
            score += 0.5
    else:
        warn(f"CI status check failed: {name}")

    # ── FINAL SCORE ──
    pct = int((score / total) * 100)
    print(f"\n{BOLD}{'='*55}")
    if pct >= 80:
        print(f"  🔥 HYPERSTATUS: {GREEN}FULLY OPERATIONAL — {pct}%{RESET}{BOLD}")
        print(f"  🦅 BROski Power Level: LEGENDARY")
    elif pct >= 50:
        print(f"  ⚡ HYPERSTATUS: {YELLOW}PARTIAL — {pct}%{RESET}{BOLD}")
        print(f"  🛠️  BROski Power Level: NEEDS SOME LOVE")
    else:
        print(f"  🚨 HYPERSTATUS: {RED}CRITICAL — {pct}%{RESET}{BOLD}")
        print(f"  🩺 BROski Power Level: HEALER NEEDED")
    print(f"  Score: {score:.1f}/{total}")
    print(f"{'='*55}{RESET}\n")

if __name__ == "__main__":
    main()
