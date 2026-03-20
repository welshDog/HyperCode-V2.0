"""
Healer Agent Mission: Health Check Validator (Local Mode)
Systematically verifies all documented health checks in the HyperCode ecosystem.
Supports both internal Docker networking and localhost for dev.
"""
import asyncio
import httpx
import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import redis.asyncio as redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("healer.validator")

class HealthCheckValidator:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.results: List[Dict[str, Any]] = []
        self.start_time = datetime.now()
        
    async def initialize(self):
        try:
            self.redis = await redis.from_url(self.redis_url, decode_responses=True)
            if self.redis:
                await self.redis.ping()
            logger.info("Validator connected to Redis. BRO, let's go! 🚀")
        except Exception as e:
            logger.warning(f"Could not connect to Redis at {self.redis_url}. Using limited mode. {e}")
            self.redis = None

    async def run_mission(self):
        """
        Main mission loop:
        1. Identify targets (from docs/guides)
        2. Execute health checks (Normal, Edge, Failure)
        3. Benchmark performance
        4. Generate report
        """
        logger.info("🎯 Starting Mission: HYPERCODE_HEALTH_CHECK_VALIDATION_001")
        
        # Target endpoints based on TIPS_03 to TIPS_10
        # Try localhost for local dev machine access
        targets = [
            {"name": "hypercode-core", "url": "http://localhost:8000/", "type": "FastAPI"},
            {"name": "redis", "url": "redis://localhost:6379", "type": "Redis"},
            {"name": "postgres", "url": "http://localhost:5432", "type": "Postgres"},
            {"name": "tips-tricks-writer", "url": "http://localhost:8011/health", "type": "Agent"},
            {"name": "crew-orchestrator", "url": "http://localhost:8081/health", "type": "Orchestrator"},
            {"name": "healer-agent", "url": "http://localhost:8010/health", "type": "Healer"}
        ]
        
        for target in targets:
            logger.info(f"Checking {target['name']}...")
            result = await self.validate_target(target)
            self.results.append(result)
            
        await self.generate_report()

    async def validate_target(self, target: Dict[str, str]) -> Dict[str, Any]:
        """Validates a single target with normal and benchmarking."""
        start_time = datetime.now()
        status = "FAIL"
        details = ""
        latency = 0
        
        try:
            if target["type"] in ["FastAPI", "Agent", "Orchestrator", "Healer"]:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    t0 = datetime.now()
                    r = await client.get(target["url"])
                    t1 = datetime.now()
                    latency = int((t1 - t0).total_seconds() * 1000) # ms
                    
                    if r.status_code == 200:
                        status = "PASS"
                        details = f"Healthy response"
                    else:
                        details = f"Status code: {r.status_code}"
            
            elif target["type"] == "Redis":
                if self.redis:
                    t0 = datetime.now()
                    ping = await self.redis.ping()
                    t1 = datetime.now()
                    latency = int((t1 - t0).total_seconds() * 1000) # ms
                    if ping:
                        status = "PASS"
                        details = "Redis PONG successful"
                else:
                    details = "Redis client not initialized"
            
            elif target["type"] == "Postgres":
                # For now, just a TCP check since pg_isready is harder to call natively
                import socket
                t0 = datetime.now()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('localhost', 5432))
                t1 = datetime.now()
                latency = int((t1 - t0).total_seconds() * 1000) # ms
                if result == 0:
                    status = "PASS"
                    details = "Postgres TCP port open"
                else:
                    details = f"Port 5432 closed or unreachable (Error {result})"
                sock.close()
            
        except Exception as e:
            details = f"Unreachable: {type(e).__name__}"
            # logger.error(f"Validation failed for {target['name']}: {e}")

        return {
            "target": target["name"],
            "type": target["type"],
            "status": status,
            "latency_ms": latency,
            "details": details,
            "indicator": "🟢" if status == "PASS" else "🔴",
            "timestamp": datetime.now().isoformat()
        }

    async def generate_report(self):
        """Generates a neurodivergent-friendly report."""
        report_path = "docs/reports/HEALTH_CHECK_VALIDATION_REPORT.md"
        
        content = f"""# 🛡️ Health Check Validation Report
**Mission ID**: HYPERCODE_HEALTH_CHECK_VALIDATION_001
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status**: {"🟢 HEALTHY" if all(r['status'] == 'PASS' for r in self.results) else "🟡 DEGRADED"}

---

## 🟢 1. Summary (Low Complexity)
Bro, we just swept the entire infrastructure to make sure our new **Tips Architect** guides match reality. 

- **Targets Scanned**: {len(self.results)}
- **Passed**: {len([r for r in self.results if r['status'] == 'PASS'])}
- **Failed**: {len([r for r in self.results if r['status'] == 'FAIL'])}

---

## 🟡 2. Detailed Results (Medium Complexity)

| Target | Status | Latency (ms) | Details |
| :--- | :--- | :--- | :--- |
"""
        for r in self.results:
            latency_str = f"{int(r['latency_ms'])}ms" if r['latency_ms'] > 0 else "N/A"
            content += f"| {r['indicator']} {r['target']} | **{r['status']}** | {latency_str} | {r['details']} |\n"

        content += """
---

## 🔴 3. Discrepancies & Recommendations (High Complexity)
**Edge Case Analysis**: 
- **Latency Spikes**: Any target over 200ms needs optimization (see TIPS_04).
- **Zombie Risk**: If status is PASS but latency is high, the agent might be struggling.

**Recommendations**:
1. **Optimize Healer**: If the Healer itself is slow, it might miss alerts.
2. **Update Docs**: If any endpoint returned a structure different from our guides, update the TIPS_XX files immediately.

---

**Mission Complete, Bro. 🚀**
"""
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        logger.info(f"Report generated at {report_path}")

async def main():
    # Try localhost first for local execution
    validator = HealthCheckValidator()
    await validator.initialize()
    await validator.run_mission()

if __name__ == "__main__":
    asyncio.run(main())
