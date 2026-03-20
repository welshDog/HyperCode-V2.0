#!/usr/bin/env python3
import ast
import json
import logging
import subprocess
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("broski.analyzer")

@dataclass
class Issue:
    file: str
    line: Optional[int]
    severity: str
    category: str
    message: str
    auto_fixable: bool = False
    def to_dict(self): return self.__dict__

class BROskiAnalyzer:
    SKIP = {".git",".venv","venv","__pycache__","node_modules","backups","reports","htmlcov"}
    def __init__(self, root):
        self.root = Path(root)
        self.out = self.root / "reports" / "broski-analysis"

    def py_files(self):
        return [f for f in self.root.rglob("*.py")
                if not any(d in f.parts for d in self.SKIP)]

    def run(self, args):
        try:
            r = subprocess.run(args, capture_output=True, text=True, cwd=self.root, timeout=120)
            return r.returncode, r.stdout
        except FileNotFoundError as e:
            logger.error(f"Command {args} not found: {e}")
            return -1, ""
        except subprocess.TimeoutExpired as e:
            logger.error(f"Command {args} timed out: {e}")
            return -1, ""
        except Exception as e:
            logger.error(f"Command {args} failed: {e}")
            return -1, ""

    def ruff(self):
        rc, out = self.run(["ruff","check",".","--output-format","json"])
        if rc == -1: return []
        try:
            return [Issue(file=i.get("filename",""),
                line=i.get("location",{}).get("row"),
                severity="high" if i.get("code","").startswith(("S","E9","F8")) else "medium",
                category=f"lint:{i.get('code','')}",
                message=i.get("message",""),
                auto_fixable=i.get("fix") is not None) for i in json.loads(out)]
        except: return []

    def secrets(self):
        rc, out = self.run(["detect-secrets","scan"])
        if rc == -1: return []
        try:
            data = json.loads(out)
            if not isinstance(data, dict) or "results" not in data:
                logger.warning("detect-secrets output missing 'results' key — skipping")
                return []
            issues = []
            for fname, hits in data["results"].items():
                if not isinstance(hits, list):
                    continue
                for h in hits:
                    issues.append(Issue(file=fname, line=h.get("line_number"),
                        severity="critical", category="secret:detected",
                        message=f"Secret type: {h.get('type','unknown')}"))
            return issues
        except json.JSONDecodeError as e:
            logger.error(f"detect-secrets JSON parse failed: {e}")
            return []
        except Exception as e:
            logger.error(f"detect-secrets scan failed unexpectedly: {e}")
            return []

    def ast_check(self, files):
        issues = []
        for fp in files:
            try: tree = ast.parse(fp.read_text(errors="ignore"))
            except SyntaxError as e:
                issues.append(Issue(file=str(fp.relative_to(self.root)),
                    line=e.lineno, severity="critical",
                    category="syntax:error", message=str(e))); continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    issues.append(Issue(file=str(fp.relative_to(self.root)),
                        line=node.lineno, severity="medium",
                        category="bare_except",
                        message="Bare except: catches everything",
                        auto_fixable=True))
        return issues

    def scan(self):
        t0 = datetime.now(timezone.utc)
        files = self.py_files()
        issues = self.ruff() + self.secrets() + self.ast_check(files)
        score = max(0.0, 100.0 - sum(
            {"critical":20,"high":10,"medium":3,"low":1}.get(i.severity,0) for i in issues))
        dur = (datetime.now(timezone.utc) - t0).total_seconds()
        report = {"scan_id": uuid.uuid4().hex[:8],
            "timestamp": t0.isoformat(), "files_scanned": len(files),
            "health_score": score, "duration_seconds": dur,
            "counts": {s: sum(1 for i in issues if i.severity==s)
                       for s in ["critical","high","medium","low"]},
            "auto_fixable": sum(1 for i in issues if i.auto_fixable),
            "issues": [i.to_dict() for i in issues]}
        self.out.mkdir(parents=True, exist_ok=True)
        path = self.out / f"analysis_{report['scan_id']}.json"
        path.write_text(json.dumps(report, indent=2))
        print(f"""
{"="*50}
  BROski Health Scan {t0.strftime("%Y-%m-%d")}
{"="*50}
  Files scanned : {len(files)}
  Health score  : {score:.1f}/100
  Critical      : {report["counts"]["critical"]}
  High          : {report["counts"]["high"]}
  Medium        : {report["counts"]["medium"]}
  Auto-fixable  : {report["auto_fixable"]}
  Duration      : {dur:.2f}s
  Report saved  : {path}
{"="*50}""")

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    print(f"Scanning: {root}")
    BROskiAnalyzer(root).scan()
