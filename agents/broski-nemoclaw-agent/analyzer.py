#!/usr/bin/env python3
"""BROski Analyzer — autonomous code health scanner for HyperCode V2.0."""
from __future__ import annotations

import ast
import json
import logging
import subprocess
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("broski.analyzer")


@dataclass
class Issue:
    """Represents a single code issue found during a scan."""

    file: str
    line: int | None
    severity: str
    category: str
    message: str
    auto_fixable: bool = False

    def to_dict(self) -> dict:
        """Return issue as a plain dict for JSON serialisation."""
        return self.__dict__


class BROskiAnalyzer:
    """Autonomous code analysis engine — ruff, secrets, AST checks."""

    SKIP: set[str] = {
        ".git", ".venv", "venv", "__pycache__",
        "node_modules", "backups", "reports", "htmlcov",
    }

    def __init__(self, root: str | Path) -> None:
        """Initialise with the repo root path."""
        self.root: Path = Path(root)
        self.out: Path = self.root / "reports" / "broski-analysis"

    def py_files(self) -> list[Path]:
        """Return all Python files, skipping noise dirs."""
        return [
            f for f in self.root.rglob("*.py")
            if not any(d in f.parts for d in self.SKIP)
        ]

    def run(self, args: list[str]) -> tuple[int, str]:
        """Run a subprocess command and return (returncode, stdout)."""
        try:
            r = subprocess.run(
                args, capture_output=True, text=True,
                cwd=self.root, timeout=120, check=False,
            )
            return r.returncode, r.stdout
        except FileNotFoundError as e:
            logger.error("Command %s not found: %s", args, e)
            return -1, ""
        except subprocess.TimeoutExpired as e:
            logger.error("Command %s timed out: %s", args, e)
            return -1, ""
        except Exception as e:
            logger.error("Command %s failed: %s", args, e)
            return -1, ""

    def ruff(self) -> list[Issue]:
        """Run ruff linter and return issues."""
        rc, out = self.run(["ruff", "check", ".", "--output-format", "json"])
        if rc == -1:
            return []
        try:
            return [
                Issue(
                    file=i.get("filename", ""),
                    line=i.get("location", {}).get("row"),
                    severity="high" if i.get("code", "").startswith(("S", "E9", "F8")) else "medium",
                    category=f"lint:{i.get('code', '')}",
                    message=i.get("message", ""),
                    auto_fixable=i.get("fix") is not None,
                )
                for i in json.loads(out)
            ]
        except Exception:
            return []

    def secrets(self) -> list[Issue]:
        """Run detect-secrets and return any credential issues found."""
        rc, out = self.run(["detect-secrets", "scan"])
        if rc == -1:
            return []
        try:
            data = json.loads(out)
            if not isinstance(data, dict) or "results" not in data:
                logger.warning("detect-secrets output missing 'results' key — skipping")
                return []
            issues: list[Issue] = []
            for fname, hits in data["results"].items():
                if not isinstance(hits, list):
                    continue
                for h in hits:
                    issues.append(
                        Issue(
                            file=fname,
                            line=h.get("line_number"),
                            severity="critical",
                            category="secret:detected",
                            message="Secret type: %s" % h.get("type", "unknown"),
                        )
                    )
            return issues
        except json.JSONDecodeError as e:
            logger.error("detect-secrets JSON parse failed: %s", e)
            return []
        except Exception as e:
            logger.error("detect-secrets scan failed unexpectedly: %s", e)
            return []

    def ast_check(self, files: list[Path]) -> list[Issue]:
        """Walk AST of each file, flagging bare excepts and syntax errors."""
        issues: list[Issue] = []
        for fp in files:
            try:
                tree = ast.parse(fp.read_text(errors="ignore"))
            except SyntaxError as e:
                issues.append(
                    Issue(
                        file=str(fp.relative_to(self.root)),
                        line=e.lineno,
                        severity="critical",
                        category="syntax:error",
                        message=str(e),
                    )
                )
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    issues.append(
                        Issue(
                            file=str(fp.relative_to(self.root)),
                            line=node.lineno,
                            severity="medium",
                            category="bare_except",
                            message="Bare except: catches everything",
                            auto_fixable=True,
                        )
                    )
        return issues

    def scan(self) -> None:
        """Run full health scan and write JSON report + console summary."""
        t0 = datetime.now(timezone.utc)
        files = self.py_files()
        issues = self.ruff() + self.secrets() + self.ast_check(files)

        score: float = max(
            0.0,
            100.0 - sum(
                {"critical": 20, "high": 10, "medium": 3, "low": 1}.get(i.severity, 0)
                for i in issues
            ),
        )
        dur = (datetime.now(timezone.utc) - t0).total_seconds()

        cnt_critical: int = sum(1 for i in issues if i.severity == "critical")
        cnt_high: int = sum(1 for i in issues if i.severity == "high")
        cnt_medium: int = sum(1 for i in issues if i.severity == "medium")
        cnt_low: int = sum(1 for i in issues if i.severity == "low")
        cnt_auto: int = sum(1 for i in issues if i.auto_fixable)

        report: dict = {
            "scan_id": uuid.uuid4().hex[:8],
            "timestamp": t0.isoformat(),
            "files_scanned": len(files),
            "health_score": score,
            "duration_seconds": dur,
            "counts": {
                "critical": cnt_critical,
                "high": cnt_high,
                "medium": cnt_medium,
                "low": cnt_low,
            },
            "auto_fixable": cnt_auto,
            "issues": [i.to_dict() for i in issues],
        }

        self.out.mkdir(parents=True, exist_ok=True)
        path = self.out / f"analysis_{report['scan_id']}.json"
        path.write_text(json.dumps(report, indent=2))

        print(
            f"\n{'='*50}\n"
            f"  BROski Health Scan {t0.strftime('%Y-%m-%d')}\n"
            f"{'='*50}\n"
            f"  Files scanned : {len(files)}\n"
            f"  Health score  : {score:.1f}/100\n"
            f"  Critical      : {cnt_critical}\n"
            f"  High          : {cnt_high}\n"
            f"  Medium        : {cnt_medium}\n"
            f"  Auto-fixable  : {cnt_auto}\n"
            f"  Duration      : {dur:.2f}s\n"
            f"  Report saved  : {path}\n"
            f"{'='*50}"
        )


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    print(f"Scanning: {root}")
    BROskiAnalyzer(root).scan()
