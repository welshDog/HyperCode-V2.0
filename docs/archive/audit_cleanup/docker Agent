##  “Gordon Docker Agent” CI healthcheck step

Here’s a minimal **CI script** idea that mimics what Gordon did. You can adapt this into GitHub Actions, GitLab CI, etc.

### a) Bash script: `ci/healthcheck_gordon.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

PROJECT_LABEL="hypercode-v20"

echo "🔎 Gordon Docker CI Healthcheck starting..."

# 1. Check containers are up
echo "📦 Checking containers..."
docker ps --filter "label=com.docker.compose.project=${PROJECT_LABEL}" \
  --format "table {{.Names}}\t{{.Status}}"

# 2. Basic count check (expect at least 10 containers; tweak as needed)
COUNT=$(docker ps --filter "label=com.docker.compose.project=${PROJECT_LABEL}" -q | wc -l)
if [ "$COUNT" -lt 10 ]; then
  echo "❌ Expected at least 10 containers, found ${COUNT}"
  exit 1
fi

# 3. Core health endpoints
echo "🌡️ Checking core /health..."
HEALTH=$(curl -sf http://localhost:8000/health || echo "")
echo "Response: ${HEALTH}"
if [[ "${HEALTH}" != *"healthy"* ]]; then
  echo "❌ /health not reporting healthy"
  exit 1
fi

echo "🧠 Checking core /ready..."
READY=$(curl -sf http://localhost:8000/ready || echo "")
echo "Response: ${READY}"
if [[ "${READY}" != *"database\":\"connected"* ]] || [[ "${READY}" != *"redis\":\"connected"* ]]; then
  echo "❌ /ready not fully ready"
  exit 1
fi

# 4. Log scan for obvious runtime errors
echo "🧾 Scanning logs for critical errors..."
ERRORS=$(docker logs --tail 500 $(docker ps --filter "label=com.docker.compose.project=${PROJECT_LABEL}" -q) 2>&1 | \
  grep -Ei "ModuleNotFoundError|Traceback|ERROR" || true)

if [ -n "${ERRORS}" ]; then
  echo "❌ Found errors in logs:"
  echo "${ERRORS}"
  exit 1
fi

echo "✅ Gordon Docker CI Healthcheck passed: system looks healthy."
```

### b) Example GitHub Actions job

```yaml
jobs:
  gordon-docker-healthcheck:
    runs-on: ubuntu-latest
    services:
      docker:
        image: docker:24-dind
        privileged: true
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker
        uses: docker/setup-buildx-action@v3

      - name: Start HyperCode stack
        run: |
          docker compose up -d --profile agents
          echo "⏳ Waiting for services to stabilise..."
          sleep 150  # align with healthcheck start_period

      - name: Run Gordon Docker CI Healthcheck
        run: |
          chmod +x ci/healthcheck_gordon.sh
          ./ci/healthcheck_gordon.sh
```

This gives you:

- A **README flex** that directly counters “no verifiable implementation”. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/107547080/18f507c3-97c4-4065-9cff-7513838497aa/FIXES_FOR_UNHEALTHY_AGENTS.md)
- A **repeatable CI health gate** that enforces “Gordon would sign off on this build”. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/107547080/18f507c3-97c4-4065-9cff-7513838497aa/FIXES_FOR_UNHEALTHY_AGENTS.md)

If you want, next step I can help tighten the wording even more for a super minimal README badge-style status, or adjust the CI to assert exactly 15 containers instead of “≥ 10”.