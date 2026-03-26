#!/usr/bin/env python3
"""
🩺 BROski Health Check — HyperCode V2.0
Runs a full diagnostic on local services + GitHub status
Usage: python scripts/hypercode_health_check.py

Port map verified: 2026-03-26 against HYPERFOCUSzone live docker ps
"""

import socket
import subprocess
import urllib.request
import urllib.error
import json
from datetime import datetime

# ─────────────────────────────────────────
# CONFIG — REAL PORTS (verified from docker ps)
# ─────────────────────────────────────────
GITHUB_REPO = "welshDog/HyperCode-V2.0"

SERVICES = [
    # ── CORE BACKEND ──
    {"name": "🧠 HyperCode Backend",      "host": "localhost", "port": 8000, "path": "/health"},

    # ── AGENTS ──
    {"name": "🩺 Healer Agent",            "host": "localhost", "port": 8010, "path": "/health"},
    {"name": "🎛️  Crew Orchestrator",      "host": "localhost", "port": 8081, "path": "/health"},
    {"name": "🦅 Super BROski Agent",      "host": "localhost", "port": 8015, "path": "/health"},
    {"name": "📊 Throttle Agent",           "host": "localhost", "port": 8014, "path": "/health"},
    {"name": "🧪 Test Agent",               "host": "localhost", "port": 8013, "path": "/health"},
    {"name": "📝 Tips & Tricks Writer",     "host": "localhost", "port": 8011, "path": "/health"},

    # ── DASHBOARDS & UI ──
    {"name": "📊 Mission Control",          "host": "localhost", "port": 8088, "path": "/"},
    {"name": "🌍 Hyper Mission UI",         "host": "localhost", "port": 8099, "path": "/"},
    {"name": "📈 Grafana",                  "host": "localhost", "port": 3001, "path": "/"},
    {"name": "🔍 cAdvisor",                 "host": "localhost", "port": 8090, "path": "/"},
    {"name": "📁 Prometheus",               "host": "localhost", "port": 9090, "path": "/-/healthy"},

    # ── MCP STACK ──
    {"name": "🔗 MCP Gateway",              "host": "localhost", "port": 8820, "path": "/health"},
    {"name": "🔗 MCP REST Adapter",         "host": "localhost", "port": 8821, "path": "/health"},

    # ── AI / LLM ──
    {"name": "🤖 Ollama LLM",               "host": "localhost", "port": 11434, "path": "/api/tags"},
    {"name": "🧠 Chroma Vector DB",         "host": "localhost", "port": 8009, "path": "/api/v1/heartbeat"},

    # ── DATA ── (TCP only — no HTTP path)
    {"name": "🗄️  Redis",                   "host": "localhost", "port": 6379, "path": None},
    {"name": "🐘 PostgreSQL",               "host": "localhost", "port": 5432, "path": None},
    {"name": "🪣 MinIO Storage",            "host": "localhost", "port": 9000, "path": None},
]

# ─────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):     print(f"  {GREEN}✅ {msg}{RESET}")
def fail(msg):   print(f"  {RED}❌ {msg}{RESET}")
def warn(msg):   print(f"  {YELLOW}⚠️  {msg}{RESET}")
def info(msg):   print(f"  {CYAN}ℹ️  {msg}{RESET}")
def header(msg): print(f"\n{BOLD}{CYAN}{msg}{RESET}")

def check_port(host, port, timeout=2):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def check_http(host, port, path, timeout=3):
    url = f"http://{host}:{port}{path}"
    try:
        req = urllib.request.urlopen(url, timeout=timeout)
        return req.status, True
    except urllib.error.HTTPError as e:
        return e.code, True
    except Exception:
        return None, False

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

def check_github():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/commits/main"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BROski-HealthCheck/1.0"})
        response = urllib.request.urlopen(req, timeout=5)
        data = json.loads(response.read())
        msg  = data["commit"]["message"].split("\n")[0][:60]
        date = data["commit"]["author"]["date"]
        sha  = data["sha"][:7]
        return True, sha, msg, date
    except Exception as e:
        return False, None, str(e), None

def check_github_ci():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs?per_page=1"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BROski-HealthCheck/1.0"})
        response = urllib.request.urlopen(req, timeout=5)
        data = json.loads(response.read())
        if data["workflow_runs"]:
            run = data["workflow_runs"][0]
            return True, run["status"], run["conclusion"], run["name"]
        return True, "none", "none", "No runs found"
    except Exception as e:
        return False, None, None, str(e)

def main():
    print(f"\n{BOLD}{'='*58}")
    print(f"  🩺 BROski♾ HYPERCODE HEALTH CHECK — HYPERFOCUSzone")
    print(f"  🏴󠁧󠁢󠁷󠁬󠁳󠁿  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*58}{RESET}")

    score = 0
    total = 0
    offline = []

    # ── LOCAL SERVICES ──
    header("🖥️  LOCAL SERVICES")
    for svc in SERVICES:
        total += 1
        port_alive = check_port(svc["host"], svc["port"])
        if not port_alive:
            fail(f"{svc['name']} — port {svc['port']} OFFLINE")
            offline.append(svc['name'])
            continue
        if svc["path"]:
            status_code, http_alive = check_http(svc["host"], svc["port"], svc["path"])
            if http_alive:
                ok(f"{svc['name']} — :{svc['port']} ONLINE (HTTP {status_code})")
                score += 1
            else:
                warn(f"{svc['name']} — :{svc['port']} port open, HTTP not responding")
                score += 0.5
        else:
            ok(f"{svc['name']} — :{svc['port']} ONLINE (TCP)")
            score += 1

    # ── DOCKER ──
    header("🐋 DOCKER STATUS")
    total += 1
    docker_alive, containers = check_docker()
    if docker_alive:
        ok(f"Docker engine ONLINE — {len(containers)} container(s) running")
        score += 1
        for c in containers[:10]:
            info(f"  └─ {c}")
        if len(containers) > 10:
            info(f"  └─ ... and {len(containers)-10} more")
    else:
        fail("Docker engine OFFLINE")
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
            ok(f"CI: {name} — {conclusion.upper()} ✅")
            score += 1
        elif conclusion in ("failure", "cancelled"):
            fail(f"CI: {name} — {conclusion.upper()}")
        elif status == "in_progress":
            warn(f"CI: {name} — RUNNING ⏳")
            score += 0.5
        elif conclusion == "none":
            ok(f"CI: No recent runs — workflows paused 💤")
            score += 1
        else:
            warn(f"CI: {name} — {status}/{conclusion}")
            score += 0.5
    else:
        warn(f"CI check failed: {name}")

    # ── OFFLINE SUMMARY ──
    if offline:
        header("🚨 OFFLINE SERVICES")
        for o in offline:
            warn(f"{o} — check docker-compose or agent config")

    # ── FINAL SCORE ──
    pct = int((score / total) * 100)
    print(f"\n{BOLD}{'='*58}")
    if pct >= 80:
        print(f"  🔥 HYPERSTATUS: {GREEN}FULLY OPERATIONAL — {pct}%{RESET}{BOLD}")
        print(f"  🦅 BROski Power Level: LEGENDARY ♾")
    elif pct >= 60:
        print(f"  ⚡ HYPERSTATUS: {YELLOW}GOOD — {pct}%{RESET}{BOLD}")
        print(f"  🛠️  BROski Power Level: SOLID FOUNDATION")
    elif pct >= 40:
        print(f"  ⚡ HYPERSTATUS: {YELLOW}PARTIAL — {pct}%{RESET}{BOLD}")
        print(f"  🛠️  BROski Power Level: NEEDS SOME LOVE")
    else:
        print(f"  🚨 HYPERSTATUS: {RED}CRITICAL — {pct}%{RESET}{BOLD}")
        print(f"  🩺 BROski Power Level: HEALER NEEDED")
    print(f"  Score: {score:.1f}/{total} services healthy")
    print(f"{'='*58}{RESET}\n")

if __name__ == "__main__":
    main()
