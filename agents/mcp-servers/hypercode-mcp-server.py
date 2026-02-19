#!/usr/bin/env python3
"""
HyperCode MCP Server
Exposes HyperCode language tools to cagent agents
Allows agents to parse, validate, and execute HyperCode natively

This is the BRIDGE between cagent agents and your custom HyperCode DSL
"""

import asyncio
import sys
import json
import subprocess
from typing import Any, Optional
from datetime import datetime
import logging

# MCP SDK (install: pip install mcp)
from mcp.server import Server
from mcp.types import Tool, TextContent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hypercode-mcp")

# Initialize MCP Server
server = Server(name="hypercode")

# Tools that agents can discover and use
@server.tool()
async def parse_hypercode(source: str) -> dict:
    """
    Parse HyperCode source into Abstract Syntax Tree (AST)
    
    This tool lets agents understand HyperCode structure without executing it
    
    Args:
        source: HyperCode source code
        
    Returns:
        Dictionary with parsed AST, tokens, and metadata
        
    Example:
        Agent: "Parse this HyperCode"
        response = await parse_hypercode('print("hello")')
    """
    try:
        # Call your HyperCode parser (adjust path as needed)
        result = subprocess.run(
            [
                "python",
                "THE HYPERCODE/hypercode-engine/hypercode_engine/cli.py",
                "parse"
            ],
            input=source.encode(),
            capture_output=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": result.stderr.decode(),
                "what": "Failed to parse HyperCode",
                "why": "Syntax error or parser crash",
                "how_to_fix": "Check HyperCode syntax"
            }
        
        return {
            "success": True,
            "ast": json.loads(result.stdout.decode()),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "what": "Parser error",
            "why": str(e),
            "how_to_fix": "Check if HyperCode engine is running"
        }


@server.tool()
async def validate_hypercode(source: str) -> dict:
    """
    Validate HyperCode syntax without executing
    
    Agents use this to check if code is valid before suggesting it
    
    Args:
        source: HyperCode source code
        
    Returns:
        Validation result with friendly error messages
    """
    try:
        result = subprocess.run(
            [
                "python",
                "THE HYPERCODE/hypercode-engine/hypercode_engine/cli.py",
                "validate"
            ],
            input=source.encode(),
            capture_output=True,
            timeout=10
        )
        
        if result.returncode != 0:
            errors = result.stderr.decode()
            return {
                "valid": False,
                "errors": errors,
                "friendly_message": format_validation_error(errors)
            }
        
        return {
            "valid": True,
            "message": "HyperCode is syntactically valid"
        }
    
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }


@server.tool()
async def execute_hypercode(source: str, timeout: int = 30) -> dict:
    """
    Execute HyperCode and return results
    
    Agents use this to run HyperCode and see output
    
    Args:
        source: HyperCode source code
        timeout: Max execution time in seconds (default: 30)
        
    Returns:
        Execution result with stdout, stderr, exit code
    """
    try:
        result = subprocess.run(
            [
                "python",
                "THE HYPERCODE/hypercode-engine/hypercode_engine/cli.py",
                "run"
            ],
            input=source.encode(),
            capture_output=True,
            timeout=timeout
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.decode(),
            "stderr": result.stderr.decode(),
            "exit_code": result.returncode,
            "duration_seconds": timeout  # Approximate
        }
    
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stderr": f"Execution timeout after {timeout}s",
            "exit_code": 124,
            "what": "Timeout",
            "why": "Code ran longer than allowed",
            "how_to_fix": "Check for infinite loops or heavy computation"
        }
    
    except Exception as e:
        return {
            "success": False,
            "stderr": str(e),
            "exit_code": 1
        }


@server.tool()
async def get_hypercode_examples() -> dict:
    """
    Get HyperCode examples for agents to reference
    
    Agents use this to understand HyperCode patterns
    
    Returns:
        Dictionary of example code snippets
    """
    examples = {
        "hello_world": {
            "description": "Print hello world",
            "code": 'print("Hello HyperCode!")'
        },
        "loop": {
            "description": "Loop example",
            "code": 'for i in range(5):\n    print(i)'
        },
        "function": {
            "description": "Define and call function",
            "code": 'def greet(name):\n    return f"Hello {name}"\nprint(greet("World"))'
        },
        "conditional": {
            "description": "If/else example",
            "code": 'x = 10\nif x > 5:\n    print("x is big")\nelse:\n    print("x is small")'
        }
    }
    
    return {
        "examples": examples,
        "documentation_url": "http://localhost:3001/docs/hypercode"
    }


@server.tool()
async def format_hypercode_error(
    error_message: str,
    source_context: Optional[str] = None
) -> dict:
    """
    Convert raw HyperCode errors into neurodivergent-friendly format
    
    Agents use this to explain errors to users clearly
    
    Args:
        error_message: Raw error from parser/interpreter
        source_context: Original source code (for context)
        
    Returns:
        Friendly error message with WHAT, WHY, HOW TO FIX
    """
    
    # Parse error and create friendly message
    friendly = format_validation_error(error_message)
    
    return {
        "raw_error": error_message,
        "friendly_error": friendly,
        "suggestion": "Ask agent to explain this error in plain English"
    }


def format_validation_error(error: str) -> str:
    """Convert raw error to ND-friendly format"""
    
    lines = error.split('\n')
    
    # Try to extract line number
    line_match = None
    for line in lines:
        if 'line' in line.lower():
            line_match = line
            break
    
    message = "⚠️ Syntax Error\n\n"
    message += f"Raw: {lines[0]}\n"
    
    if line_match:
        message += f"Location: {line_match}\n"
    
    message += "\nHow to fix: Check your HyperCode syntax"
    
    return message


@server.tool()
async def check_hypercode_compatibility(
    hypercode_version: str = "1.0"
) -> dict:
    """
    Check HyperCode version and compatibility
    
    Returns:
        Version info and compatibility matrix
    """
    return {
        "version": hypercode_version,
        "python_version": "3.11+",
        "mlir_support": True,
        "quantum_paradigm": True,
        "bio_computing": True,
        "compatibility_matrix": {
            "1.0": "Current stable",
            "0.9": "Legacy support"
        }
    }


# Health check endpoint
@server.tool()
async def health() -> dict:
    """Check MCP server health"""
    return {
        "status": "healthy",
        "service": "hypercode-mcp",
        "timestamp": datetime.now().isoformat(),
        "tools_available": [
            "parse_hypercode",
            "validate_hypercode",
            "execute_hypercode",
            "get_hypercode_examples",
            "format_hypercode_error",
            "check_hypercode_compatibility",
            "health"
        ]
    }


async def main():
    """Run the MCP server"""
    logger.info("Starting HyperCode MCP Server")
    logger.info("Available tools:")
    logger.info("  - parse_hypercode: Parse HyperCode into AST")
    logger.info("  - validate_hypercode: Check syntax")
    logger.info("  - execute_hypercode: Run HyperCode")
    logger.info("  - get_hypercode_examples: Show examples")
    logger.info("  - format_hypercode_error: Friendly errors")
    logger.info("  - check_hypercode_compatibility: Version info")
    
    async with server:
        logger.info("HyperCode MCP Server running")
        # Keep server running
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
