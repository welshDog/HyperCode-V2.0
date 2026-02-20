#!/usr/bin/env python3
"""
HyperCode Centralized Health Monitor
Aggregates health checks from all services and provides real-time dashboard
"""

import json
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Tuple
import sys

try:
    import httpx
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.text import Text
except ImportError:
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "httpx", "rich"], check=True)
    import httpx
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.text import Text

console = Console()

# Service endpoints and ports
SERVICES = {
    "hypercode-core": ("http://localhost:8000", "health"),
    "broski-terminal": ("http://localhost:3000", "api/health"),
    "hyperflow-editor": ("http://localhost:5173", None),  # No health endpoint
    "celery-worker": ("http://localhost", "celery-ping"),
    "frontend-specialist": ("http://localhost:8002", "health"),
    "security-engineer": ("http://localhost:8007", "health"),
    "system-architect": ("http://localhost:8008", "health"),
    "crew-orchestrator": ("http://localhost:8080", "health"),
    "hafs-service": ("http://localhost:8001", "health"),
    "redis": ("http://localhost:6379", None),
    "postgres": ("postgresql://localhost:5432", None),
    "prometheus": ("http://localhost:9090", "-/healthy"),
    "grafana": ("http://localhost:3001", "api/health"),
    "jaeger": ("http://localhost:16686", "api/services"),
}


def check_service_health(service_name: str, base_url: str, endpoint: str = None) -> Tuple[str, str, float]:
    """Check individual service health"""
    start = time.time()
    try:
        if endpoint is None:
            return (service_name, "⏭️ skip", 0)
        
        url = f"{base_url}/{endpoint}".replace("//", "/").replace(":/", "://")
        
        response = httpx.get(url, timeout=3.0)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            return (service_name, "🟢 healthy", elapsed)
        else:
            return (service_name, f"🟡 {response.status_code}", elapsed)
    
    except httpx.TimeoutException:
        elapsed = time.time() - start
        return (service_name, "🔴 timeout", elapsed)
    except Exception as e:
        elapsed = time.time() - start
        error_type = type(e).__name__
        return (service_name, f"🔴 {error_type}", elapsed)


def get_docker_status() -> Dict[str, str]:
    """Get container status from Docker"""
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", "docker-compose.yml", "ps", "--format", "{{.Names}}|{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        status_map = {}
        for line in result.stdout.strip().split("\n"):
            if line and "|" in line:
                name, status = line.split("|")
                status_map[name.strip()] = status.strip()
        
        return status_map
    except Exception as e:
        console.print(f"[red]Error getting Docker status: {e}[/red]")
        return {}


def create_health_table(health_data: List[Tuple[str, str, float]]) -> Table:
    """Create rich table for health status"""
    table = Table(title="Service Health Status", show_header=True, header_style="bold magenta")
    
    table.add_column("Service", style="cyan", width=25)
    table.add_column("Status", style="green", width=20)
    table.add_column("Response (ms)", style="yellow", width=15)
    table.add_column("Docker Status", style="blue", width=20)
    
    docker_status = get_docker_status()
    
    for service, health_status, elapsed in health_data:
        docker_state = docker_status.get(service, "unknown")
        table.add_row(
            service,
            health_status,
            f"{elapsed*1000:.0f}",
            docker_state
        )
    
    return table


def create_summary_panel(health_data: List[Tuple[str, str, float]]) -> Panel:
    """Create summary panel"""
    healthy = sum(1 for _, status, _ in health_data if "healthy" in status)
    unhealthy = sum(1 for _, status, _ in health_data if "timeout" in status or "error" in status.lower())
    skipped = sum(1 for _, status, _ in health_data if "skip" in status)
    
    summary_text = Text()
    summary_text.append(f"🟢 Healthy: {healthy}", style="green bold")
    summary_text.append(f" | ")
    summary_text.append(f"🔴 Unhealthy: {unhealthy}", style="red bold")
    summary_text.append(f" | ")
    summary_text.append(f"⏭️ Skipped: {skipped}", style="yellow bold")
    summary_text.append(f"\nLast Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return Panel(summary_text, title="Summary", border_style="cyan")


def monitor_live():
    """Live monitoring dashboard"""
    layout = Layout()
    layout.split_column(
        Layout(name="summary", size=5),
        Layout(name="table")
    )
    
    def render_dashboard():
        health_data = []
        for service, (base_url, endpoint) in SERVICES.items():
            health_data.append(check_service_health(service, base_url, endpoint))
        
        layout["summary"].update(create_summary_panel(health_data))
        layout["table"].update(create_health_table(health_data))
        return layout
    
    try:
        with Live(render_dashboard(), refresh_per_second=0.2, console=console) as live:
            while True:
                live.update(render_dashboard())
                time.sleep(5)
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitor stopped[/yellow]")


def single_check():
    """Single health check run"""
    console.print("[bold]Checking HyperCode services...[/bold]\n")
    
    health_data = []
    for service, (base_url, endpoint) in SERVICES.items():
        health_data.append(check_service_health(service, base_url, endpoint))
    
    console.print(create_health_table(health_data))
    console.print(create_summary_panel(health_data))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        monitor_live()
    else:
        single_check()
