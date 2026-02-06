# Quickstart

Goal: Run core service and dashboard, then execute a mission demo.

## Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Node.js 18+ (optional for frontend dev)

## Steps

1) Clone repo
```bash
git clone https://github.com/welshDog/HyperCode-V2.0.git
cd HyperCode-V2.0
```

2) Start core with Docker Compose
```bash
docker-compose up -d
```
Services:
- hypercode-core → http://localhost:8000
- redis → redis://localhost:6379
- prometheus → http://localhost:9090

3) Open Agents Dashboard
- Path: agents/dashboard/index.html
- Open in browser
- Paste dev JWT token if required

4) Run Mission Demo
- Fill objectives/constraints/success criteria
- Click “Run Mission Demo”
- Watch timeline update through: create → assign → start → verify → complete

5) Verify via API (optional)
```bash
# Create mission
curl -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{
    "title": "Strategist Demo: Checkout",
    "priority": 50,
    "payload": {
      "requirements": { "capabilities": ["frontend","backend","qa"] },
      "objectives": "Implement checkout",
      "constraints": "Use existing API"
    }
  }' \
  http://localhost:8000/orchestrator/mission

# Assign
curl -H "Authorization: Bearer <token>" -X POST http://localhost:8000/orchestrator/assign

# Start → Verify → Complete
curl -H "Authorization: Bearer <token>" -X POST http://localhost:8000/orchestrator/<id>/start
curl -H "Authorization: Bearer <token>" -X POST http://localhost:8000/orchestrator/<id>/verify
curl -H "Authorization: Bearer <token>" -X POST http://localhost:8000/orchestrator/<id>/complete

# Status
curl -H "Authorization: Bearer <token>" http://localhost:8000/orchestrator/<id>
```

## Screenshots/Video
- Suggested: 30s screen recording creating mission and walking phases

## Troubleshooting
- Prometheus restart: ensure volumes map to prometheus.yml correctly
- Auth: use dev token header alg=none, body scopes string
- Redis not available: fakeredis fallback used in dev
