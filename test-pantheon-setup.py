#!/usr/bin/env python3
"""
BROski Pantheon 2.0 - Phase 1 Validation Test
Verify that cagent + Docker Model Runner + HyperCode MCP are ready

Run this to check your setup before deploying
"""

import sys
import json
import subprocess
import os
from typing import Dict, Tuple
from datetime import datetime

# Colors for output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def run_command(cmd, silent=False) -> Tuple[bool, str]:
    """Run shell command and return success status and output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout + result.stderr
        return result.returncode == 0, output.strip()
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)

def test_docker() -> bool:
    """Test Docker installation and version"""
    print_info("Testing Docker Desktop...")
    
    success, output = run_command("docker --version")
    if success:
        print_success(f"Docker: {output}")
        return True
    else:
        print_error("Docker not found or not running")
        print_info("Install Docker Desktop 4.49+ from https://docker.com/download")
        return False

def test_docker_model_runner() -> bool:
    """Test Docker Model Runner"""
    print_info("Testing Docker Model Runner...")
    
    # Try to pull a small model
    success, output = run_command("docker model ls 2>/dev/null || docker model --help 2>/dev/null")
    
    if success:
        print_success("Docker Model Runner available")
        return True
    else:
        print_warning("Docker Model Runner not found")
        print_info("It's built into Docker Desktop 4.49+")
        return False

def test_cagent() -> bool:
    """Test cagent installation"""
    print_info("Testing cagent...")
    
    # Try docker-based cagent first
    success, output = run_command("docker run --rm docker.io/docker/cagent:latest --version 2>/dev/null")
    
    if success:
        print_success("Docker cagent available (docker run docker.io/docker/cagent:latest)")
        return True
    
    # Try local cagent
    success, output = run_command("cagent --version")
    if success:
        print_success(f"cagent installed: {output}")
        return True
    
    print_warning("cagent not found")
    print_info("It's bundled with Docker Desktop 4.49+")
    return False

def test_files() -> bool:
    """Test required files exist"""
    print_info("Testing required files...")
    
    required_files = {
        "./cagent-pantheon.yaml": "cagent manifest",
        "./agents/mcp-servers/hypercode-mcp-server.py": "HyperCode MCP server",
        "./agents/HYPER-AGENT-BIBLE.md": "Agent philosophy",
        "./BROski Business Agents/CREW_MANIFESTO.md": "Crew manifesto",
        "./docker-compose.yml": "Docker Compose manifest",
    }
    
    all_found = True
    for file_path, description in required_files.items():
        if os.path.exists(file_path):
            print_success(f"{description}: {file_path}")
        else:
            print_error(f"{description} NOT FOUND: {file_path}")
            all_found = False
    
    return all_found

def test_hypercode_engine() -> bool:
    """Test HyperCode engine exists"""
    print_info("Testing HyperCode engine...")
    
    engine_path = "./THE HYPERCODE/hypercode-engine"
    if os.path.exists(engine_path):
        print_success(f"HyperCode engine found: {engine_path}")
        return True
    else:
        print_warning(f"HyperCode engine not found at {engine_path}")
        print_info("This is needed for MCP server to work")
        return False

def test_agents_directory() -> bool:
    """Test agents directory structure"""
    print_info("Testing agents directory...")
    
    agents_path = "./agents"
    if os.path.exists(agents_path):
        print_success(f"Agents directory: {agents_path}")
        
        # Count specialist directories
        specialist_dirs = [
            "01-frontend-specialist",
            "02-backend-specialist",
            "03-database-architect",
            "04-qa-engineer",
            "05-devops-engineer",
            "06-security-engineer",
            "07-system-architect",
            "08-project-strategist"
        ]
        
        found = 0
        for specialist in specialist_dirs:
            if os.path.exists(f"{agents_path}/{specialist}"):
                found += 1
        
        print_info(f"Specialists found: {found}/{len(specialist_dirs)}")
        return True
    else:
        print_error("Agents directory not found")
        return False

def test_env_file() -> bool:
    """Test .env configuration"""
    print_info("Testing environment configuration...")
    
    if not os.path.exists(".env"):
        print_warning(".env file not found")
        
        if os.path.exists(".env.example"):
            print_info("Found .env.example - copy to .env to configure")
        else:
            print_warning("Neither .env nor .env.example found")
            return False
    else:
        print_success(".env file exists")
        
        # Check for key variables
        with open(".env", "r") as f:
            env_content = f.read()
        
        key_vars = ["API_KEY", "ANTHROPIC_API_KEY", "POSTGRES_PASSWORD"]
        for var in key_vars:
            if var in env_content:
                print_info(f"  ✓ {var} configured")
    
    return True

def test_python() -> bool:
    """Test Python version"""
    print_info("Testing Python...")
    
    success, output = run_command("python --version")
    if success:
        print_success(f"Python: {output}")
        return True
    
    # Try python3
    success, output = run_command("python3 --version")
    if success:
        print_success(f"Python: {output}")
        return True
    
    print_error("Python not found")
    return False

def run_tests() -> Dict[str, bool]:
    """Run all validation tests"""
    print_header("BROski Pantheon 2.0 - Setup Validation")
    
    tests = {
        "Docker Desktop": test_docker,
        "Docker Model Runner": test_docker_model_runner,
        "cagent": test_cagent,
        "Python": test_python,
        "Required Files": test_files,
        "HyperCode Engine": test_hypercode_engine,
        "Agents Directory": test_agents_directory,
        "Environment Config": test_env_file,
    }
    
    results = {}
    
    for test_name, test_func in tests.items():
        print_header(f"Test: {test_name}")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print_error(f"Test failed with error: {e}")
            results[test_name] = False
    
    return results

def print_summary(results: Dict[str, bool]):
    """Print test summary and recommendations"""
    print_header("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"Passed: {passed}/{total}\n")
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if result else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"{status} - {test_name}")
    
    print()
    
    if passed == total:
        print_success("All tests passed! Ready for Phase 2")
        print_info("Next steps:")
        print_info("  1. Review cagent-pantheon.yaml")
        print_info("  2. Run: docker model pull smollm2")
        print_info("  3. Test BROski: docker run -v $(pwd):/app -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY docker.io/docker/cagent:latest run /app/cagent-pantheon.yaml")
        return 0
    else:
        failed_tests = [name for name, result in results.items() if not result]
        print_warning(f"Some tests failed: {', '.join(failed_tests)}")
        print_info("Please fix these before proceeding to Phase 2")
        return 1

def main():
    """Main entry point"""
    results = run_tests()
    exit_code = print_summary(results)
    
    print_header("End of Validation")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
