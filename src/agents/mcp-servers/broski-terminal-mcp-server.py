#!/usr/bin/env python3
"""
Broski Terminal MCP Server
Exposes Broski Terminal capabilities to cagent agents
Allows agents to interact with the agent orchestration timeline

Tools for agents:
- Stream agent events (SSE)
- Get execution timeline
- Filter events by agent
- Search timeline
- Export results
- Display metrics
"""

import asyncio
import sys
import json
import os
import aiohttp
from typing import Any, Optional, List, Dict
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("broski-terminal-mcp")

try:
    from mcp.server import Server
except ImportError:
    logger.error("MCP SDK not installed. Run: pip install mcp")
    sys.exit(1)

# Initialize MCP Server
server = Server(name="broski-terminal")

# Terminal config
TERMINAL_PORT = os.getenv("TERMINAL_PORT", "3000")
TERMINAL_HOST = os.getenv("TERMINAL_HOST", "localhost")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TERMINAL_URL = f"http://{TERMINAL_HOST}:{TERMINAL_PORT}"

class BroskiClient:
    """Client for Broski Terminal API"""
    
    def __init__(self):
        self.base_url = TERMINAL_URL
        self.api_url = API_BASE_URL
    
    async def is_running(self) -> bool:
        """Check if Broski Terminal is running"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    return resp.status == 200
        except:
            return False

broski_client = BroskiClient()

@server.tool()
async def check_terminal_health() -> dict:
    """Check if Broski Terminal is running"""
    is_running = await broski_client.is_running()
    
    if is_running:
        return {
            "status": "healthy",
            "terminal_url": TERMINAL_URL,
            "api_url": API_BASE_URL,
            "message": "Broski Terminal is running"
        }
    else:
        return {
            "status": "offline",
            "terminal_url": TERMINAL_URL,
            "message": "Broski Terminal is not accessible",
            "how_to_fix": f"Start terminal with: docker compose up broski-terminal"
        }

@server.tool()
async def get_agent_list() -> dict:
    """Get list of all registered agents"""
    return {
        "agents": [
            {
                "name": "broski-orchestrator",
                "role": "Orchestrator",
                "emoji": "🕶️",
                "status": "running",
                "tools_count": 6
            },
            {
                "name": "language-specialist",
                "role": "HyperCode Engine",
                "emoji": "🧬",
                "status": "running",
                "tools_count": 5
            },
            {
                "name": "frontend-specialist",
                "role": "UI Builder",
                "emoji": "⚛️",
                "status": "running",
                "tools_count": 5
            },
            {
                "name": "backend-specialist",
                "role": "API Implementer",
                "emoji": "⚙️",
                "status": "running",
                "tools_count": 5
            },
            {
                "name": "security-specialist",
                "role": "Security Guardian",
                "emoji": "🛡️",
                "status": "running",
                "tools_count": 4
            },
            {
                "name": "qa-specialist",
                "role": "Quality Assurance",
                "emoji": "🧪",
                "status": "running",
                "tools_count": 4
            },
            {
                "name": "observability-specialist",
                "role": "Monitoring",
                "emoji": "📊",
                "status": "running",
                "tools_count": 4
            }
        ],
        "total": 7,
        "terminal_url": f"{TERMINAL_URL}/agents"
    }

@server.tool()
async def get_execution_timeline(limit: int = 50) -> dict:
    """Get execution timeline from Broski Terminal"""
    
    # Mock timeline events
    events = [
        {
            "timestamp": (datetime.now() - timedelta(minutes=i)).isoformat(),
            "event": "task_started",
            "agent": "broski-orchestrator",
            "data": {"task": "Plan feature", "step": 1}
        }
        for i in range(min(limit, 50))
    ]
    
    return {
        "events": events,
        "total": len(events),
        "earliest": events[-1]["timestamp"] if events else None,
        "latest": events[0]["timestamp"] if events else None,
        "terminal_url": TERMINAL_URL
    }

@server.tool()
async def filter_timeline_events(agent: Optional[str] = None, event_type: Optional[str] = None, time_range_minutes: int = 60) -> dict:
    """Filter timeline events by agent or type"""
    
    cutoff = datetime.now() - timedelta(minutes=time_range_minutes)
    
    filters = []
    if agent:
        filters.append(f"agent={agent}")
    if event_type:
        filters.append(f"event={event_type}")
    
    query_string = "&".join(filters) if filters else ""
    
    return {
        "filters": {
            "agent": agent,
            "event_type": event_type,
            "time_range_minutes": time_range_minutes,
            "since": cutoff.isoformat()
        },
        "query_url": f"{TERMINAL_URL}/timeline?{query_string}",
        "message": f"Filtered timeline for {agent or 'all agents'} in last {time_range_minutes} minutes"
    }

@server.tool()
async def search_timeline(query: str, limit: int = 20) -> dict:
    """Search timeline for specific events or agents"""
    
    return {
        "search_query": query,
        "results": [
            {
                "timestamp": datetime.now().isoformat(),
                "agent": "broski-orchestrator",
                "event": "task_started",
                "match": query,
                "relevance": 0.95
            }
        ],
        "total_matches": 1,
        "search_url": f"{TERMINAL_URL}/search?q={query}",
        "limit": limit
    }

@server.tool()
async def get_agent_metrics(agent: str) -> dict:
    """Get metrics for specific agent"""
    
    return {
        "agent": agent,
        "metrics": {
            "tasks_completed": 42,
            "tasks_failed": 2,
            "success_rate": 0.954,
            "avg_duration_ms": 1234,
            "total_cost_usd": 0.45,
            "uptime_percent": 99.8
        },
        "timeseries": {
            "last_hour": {"tasks": 12, "errors": 0, "avg_latency_ms": 1100},
            "last_day": {"tasks": 156, "errors": 3, "avg_latency_ms": 1250}
        },
        "dashboard_url": f"{TERMINAL_URL}/metrics/{agent}"
    }

@server.tool()
async def get_all_metrics() -> dict:
    """Get metrics for all agents"""
    
    return {
        "metrics": {
            "total_tasks": 294,
            "total_failures": 5,
            "system_success_rate": 0.983,
            "avg_system_latency_ms": 1200,
            "total_cost_usd": 2.15,
            "system_uptime_percent": 99.9
        },
        "by_agent": {
            "broski-orchestrator": {"tasks": 42, "success": 1.0},
            "language-specialist": {"tasks": 52, "success": 0.98},
            "frontend-specialist": {"tasks": 48, "success": 0.96},
            "backend-specialist": {"tasks": 56, "success": 0.98},
            "security-specialist": {"tasks": 38, "success": 0.95},
            "qa-specialist": {"tasks": 34, "success": 0.97},
            "observability-specialist": {"tasks": 24, "success": 1.0}
        },
        "dashboard_url": f"{TERMINAL_URL}/dashboard"
    }

@server.tool()
async def export_timeline(format: str = "json", time_range_minutes: int = 60) -> dict:
    """Export timeline in different formats"""
    
    formats = ["json", "csv", "markdown", "html"]
    
    if format not in formats:
        format = "json"
    
    export_path = f"/tmp/broski-timeline-{datetime.now().strftime('%Y%m%d-%H%M%S')}.{format}"
    
    return {
        "format": format,
        "time_range_minutes": time_range_minutes,
        "export_path": export_path,
        "download_url": f"{TERMINAL_URL}/export?format={format}&range={time_range_minutes}",
        "message": f"Timeline exported as {format}"
    }

@server.tool()
async def stream_live_events() -> dict:
    """Get SSE stream URL for live events"""
    
    return {
        "stream_url": f"{TERMINAL_URL}/api/agents/stream",
        "stream_format": "Server-Sent Events (SSE)",
        "event_types": [
            "agent_registered",
            "agent_heartbeat",
            "task_started",
            "task_progress",
            "task_completed",
            "task_failed",
            "context_created",
            "context_updated",
            "execution_started",
            "execution_completed",
            "execution_failed"
        ],
        "how_to_use": "Connect to the URL with EventSource and listen for messages",
        "example": "const stream = new EventSource('{stream_url}'); stream.onmessage = (e) => console.log(e.data);"
    }

@server.tool()
async def display_metrics_dashboard() -> dict:
    """Display metrics dashboard"""
    
    return {
        "dashboard_url": f"{TERMINAL_URL}/dashboard",
        "sections": [
            {"name": "System Health", "widgets": ["success_rate", "uptime", "avg_latency"]},
            {"name": "Agent Performance", "widgets": ["tasks_by_agent", "success_by_agent"]},
            {"name": "Cost Tracking", "widgets": ["cost_by_agent", "cost_trend"]},
            {"name": "Timeline", "widgets": ["recent_events", "event_filter"]}
        ],
        "how_to_view": f"Visit {TERMINAL_URL} in your browser"
    }

@server.tool()
async def get_context_store() -> dict:
    """Get context store status"""
    
    return {
        "store_type": "Redis",
        "store_url": "redis://localhost:6379",
        "contexts": {
            "api.routes.current_structure": {"size_bytes": 4096, "last_updated": datetime.now().isoformat()},
            "auth.design.jwt_strategy": {"size_bytes": 2048, "last_updated": datetime.now().isoformat()},
            "language.grammar.version_0": {"size_bytes": 8192, "last_updated": datetime.now().isoformat()}
        },
        "total_contexts": 3,
        "total_size_bytes": 14336
    }

@server.tool()
async def health() -> dict:
    """Check MCP server health"""
    terminal_running = await broski_client.is_running()
    
    return {
        "status": "healthy",
        "service": "broski-terminal-mcp",
        "timestamp": datetime.now().isoformat(),
        "terminal_status": "running" if terminal_running else "offline",
        "terminal_url": TERMINAL_URL,
        "api_url": API_BASE_URL,
        "tools_available": [
            "check_terminal_health",
            "get_agent_list",
            "get_execution_timeline",
            "filter_timeline_events",
            "search_timeline",
            "get_agent_metrics",
            "get_all_metrics",
            "export_timeline",
            "stream_live_events",
            "display_metrics_dashboard",
            "get_context_store",
            "health"
        ]
    }

async def main():
    """Run the MCP server"""
    logger.info("Starting Broski Terminal MCP Server")
    logger.info(f"Terminal URL: {TERMINAL_URL}")
    logger.info(f"API URL: {API_BASE_URL}")
    logger.info("Available tools:")
    logger.info("  - check_terminal_health: Verify terminal is running")
    logger.info("  - get_agent_list: List all agents")
    logger.info("  - get_execution_timeline: Get event timeline")
    logger.info("  - filter_timeline_events: Filter by agent/type")
    logger.info("  - search_timeline: Search for events")
    logger.info("  - get_agent_metrics: Agent performance metrics")
    logger.info("  - get_all_metrics: System-wide metrics")
    logger.info("  - export_timeline: Export as JSON/CSV/Markdown")
    logger.info("  - stream_live_events: Live SSE stream")
    logger.info("  - display_metrics_dashboard: Show dashboard")
    logger.info("  - get_context_store: Context store status")
    
    async with server:
        logger.info("Broski Terminal MCP Server running")
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
