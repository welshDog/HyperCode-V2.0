#!/bin/bash
# HyperCode V2.0 - Quick Health Fix Script

set -e

echo "🔧 HyperCode V2.0 - Agent Health Recovery"
echo "=========================================="
echo ""

# Step 1: Stop services
echo "1️⃣  Stopping services..."
docker compose down

# Step 2: Rebuild core
echo ""
echo "2️⃣  Rebuilding hypercode-core..."
docker compose build hypercode-core

# Step 3: Start services
echo ""
echo "3️⃣  Starting services..."
docker compose up -d

# Step 4: Wait for core to be healthy
echo ""
echo "4️⃣  Waiting for hypercode-core to be healthy (max 60s)..."
for i in {1..20}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ hypercode-core is healthy!"
        break
    fi
    echo "  Attempt $i/20... waiting"
    sleep 3
done

# Step 5: Start agents profile
echo ""
echo "5️⃣  Starting agents..."
docker compose up -d --profile agents

# Step 6: Wait for agents to register
echo ""
echo "6️⃣  Waiting for agents to register (max 60s)..."
sleep 10
for i in {1..5}; do
    count=$(docker ps --filter "status=running" | grep -E "specialist|engineer|strategist" | wc -l)
    echo "  Agents running: $count/4"
    sleep 10
done

# Step 7: Verify health
echo ""
echo "7️⃣  Verifying health..."
echo ""
docker ps --filter "label=com.docker.compose.project=hypercode-v20" --format "table {{.Names}}\t{{.Status}}" | grep -E "specialist|engineer|strategist|core|postgres|redis"

echo ""
echo "✅ Recovery complete! Check agents status:"
echo "   docker logs project-strategist --tail 20"
echo "   docker logs backend-specialist --tail 20"
echo ""
