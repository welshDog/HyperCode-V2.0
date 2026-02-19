#!/bin/bash
# BROski Pantheon 2.0 - Quick Start Validation (Linux/macOS)

echo "🔥 BROski Pantheon 2.0 - System Check"
echo "========================================"

check_cmd() {
    if command -v "$1" >/dev/null 2>&1; then
        echo "✅ Found $1"
        return 0
    else
        echo "❌ Missing $1"
        return 1
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo "✅ Found $1"
        return 0
    else
        echo "❌ Missing $1"
        return 1
    fi
}

# 1. Check Docker
echo -e "\n1. Checking Docker Environment..."
if check_cmd "docker"; then
    docker --version
    if docker info >/dev/null 2>&1; then
        echo "✅ Docker Daemon is running"
    else
        echo "❌ Docker Daemon is NOT running. Please start Docker Desktop."
        exit 1
    fi
else
    echo "❌ Docker not installed. Install Docker Desktop 4.49+"
    exit 1
fi

# 2. Check Files
echo -e "\n2. Checking Pantheon Files..."
missing_files=0
check_file "./cagent-pantheon.yaml" || ((missing_files++))
check_file "./agents/mcp-servers/hypercode-mcp-server.py" || ((missing_files++))

if [ $missing_files -gt 0 ]; then
    echo "❌ Missing critical files. Check the implementation summary."
else
    echo "✅ All critical files present"
fi

# 3. Check Python & MCP
echo -e "\n3. Checking Python & MCP..."
if check_cmd "python3"; then
    python3 --version
    if python3 -c "import mcp" >/dev/null 2>&1; then
        echo "✅ Python 'mcp' package installed"
    else
        echo "⚠️  Python 'mcp' package NOT found."
        echo "   Run: pip install mcp"
    fi
else
    echo "❌ Python3 not found."
fi

# 4. Check Local Model
echo -e "\n4. Checking Local Model (smollm2)..."
if docker model list 2>/dev/null | grep -q "smollm2"; then
    echo "✅ smollm2 model found"
else
    echo "⚠️  smollm2 model NOT found."
    echo "   Run: docker model pull smollm2"
fi

echo -e "\n========================================"
echo "🎉 Validation Complete!"
echo "Next Steps:"
echo "1. Install MCP: pip install mcp"
echo "2. Pull Model: docker model pull smollm2"
echo "3. Run Test: See PANTHEON_INTEGRATION_GUIDE.md"
