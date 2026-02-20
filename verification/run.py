import pytest
import os
import sys
import datetime
import subprocess
import json
import time

def generate_report(results, report_file="VERIFICATION_REPORT.md"):
    """Generate a markdown report from test results."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""# HyperCode V2.0 Verification Report
**Date:** {timestamp}
**Environment:** {os.getenv("ENVIRONMENT", "Production")}
**Executor:** Agent X - The Architect

## 1. Executive Summary
This report summarizes the automated verification of the HyperCode V2.0 system.

## 2. Test Execution
- **Total Tests:** {results['total']}
- **Passed:** {results['passed']}
- **Failed:** {results['failed']}
- **Skipped:** {results['skipped']}
- **Duration:** {results['duration']:.2f}s

### Detailed Results
| Test Case | Outcome | Message |
|-----------|---------|---------|
"""
    for test in results['details']:
        outcome = "✅ PASS" if test['outcome'] == "passed" else "❌ FAIL" if test['outcome'] == "failed" else "⚠️ SKIP"
        report += f"| `{test['nodeid']}` | {outcome} | {test.get('message', '')} |\n"

    report += """
## 3. System Metrics (Snapshot)
"""
    try:
        # Docker Stats snapshot
        docker_stats = subprocess.run(
            ["docker", "stats", "--no-stream", "--format", "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"],
            capture_output=True, text=True
        )
        if docker_stats.returncode == 0:
            report += "```\n" + docker_stats.stdout + "\n```\n"
        else:
            report += "> Docker stats unavailable.\n"
    except Exception as e:
        report += f"> Error fetching metrics: {e}\n"

    report += """
## 4. Conclusion
"""
    if results['failed'] == 0:
        report += "**✅ GO FOR LAUNCH**\n\nAll critical verification checks passed. The system is stable and ready for operation."
    else:
        report += "**❌ NO GO**\n\nCritical failures detected. Immediate remediation required before launch."

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"Report generated: {report_file}")
    return report_file

class ReportPlugin:
    def __init__(self):
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "duration": 0,
            "details": []
        }
        self.start_time = 0

    def pytest_sessionstart(self, session):
        self.start_time = time.time()

    def pytest_sessionfinish(self, session, exitstatus):
        self.results["duration"] = time.time() - self.start_time

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            self.results["total"] += 1
            self.results[report.outcome] += 1
            detail = {
                "nodeid": report.nodeid,
                "outcome": report.outcome,
                "message": ""
            }
            if report.failed:
                detail["message"] = str(report.longrepr).split('\n')[-1] # Simple message
            self.results["details"].append(detail)
        elif report.skipped:
             self.results["total"] += 1
             self.results["skipped"] += 1
             self.results["details"].append({
                 "nodeid": report.nodeid,
                 "outcome": "skipped",
                 "message": report.longrepr[2] if isinstance(report.longrepr, tuple) else str(report.longrepr)
             })

if __name__ == "__main__":
    plugin = ReportPlugin()
    # Run pytest programmatically
    ret_code = pytest.main(["-v", "verification/test_system.py"], plugins=[plugin])
    
    generate_report(plugin.results)
    sys.exit(ret_code)
