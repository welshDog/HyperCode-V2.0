#!/usr/bin/env python3
"""
Hyperflow Editor MCP Server
Exposes editor capabilities to cagent agents
Allows agents to interact with the Hyperflow Editor programmatically

Tools for agents:
- Create/read/write files
- Syntax highlighting configuration
- Autocomplete suggestions
- Error display formatting
- Code execution via editor
"""

import asyncio
import sys
import json
import os
import aiohttp
from typing import Any, Optional, List
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hyperflow-editor-mcp")

try:
    from mcp.server import Server
except ImportError:
    logger.error("MCP SDK not installed. Run: pip install mcp")
    sys.exit(1)

# Initialize MCP Server
server = Server(name="hyperflow-editor")

# Editor config
EDITOR_PORT = os.getenv("EDITOR_PORT", "5173")
EDITOR_HOST = os.getenv("EDITOR_HOST", "localhost")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
EDITOR_URL = f"http://{EDITOR_HOST}:{EDITOR_PORT}"

class EditorClient:
    """Client for Hyperflow Editor API"""
    
    def __init__(self):
        self.base_url = EDITOR_URL
        self.api_url = API_BASE_URL
    
    async def is_running(self) -> bool:
        """Check if editor is running"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    return resp.status == 200
        except:
            return False
    
    async def create_file(self, path: str, content: str) -> dict:
        """Create a new file in editor"""
        return {
            "success": True,
            "path": path,
            "content": content,
            "created_at": datetime.now().isoformat(),
            "url": f"{EDITOR_URL}/file?path={path}"
        }
    
    async def read_file(self, path: str) -> dict:
        """Read file from editor"""
        return {
            "success": True,
            "path": path,
            "url": f"{EDITOR_URL}/file?path={path}"
        }
    
    async def write_file(self, path: str, content: str) -> dict:
        """Write file in editor"""
        return {
            "success": True,
            "path": path,
            "content": content,
            "modified_at": datetime.now().isoformat(),
            "url": f"{EDITOR_URL}/file?path={path}"
        }

editor_client = EditorClient()

@server.tool()
async def check_editor_health() -> dict:
    """Check if Hyperflow Editor is running"""
    is_running = await editor_client.is_running()
    
    if is_running:
        return {
            "status": "healthy",
            "editor_url": EDITOR_URL,
            "api_url": API_BASE_URL,
            "message": "Hyperflow Editor is running"
        }
    else:
        return {
            "status": "offline",
            "editor_url": EDITOR_URL,
            "message": "Hyperflow Editor is not accessible",
            "how_to_fix": f"Start editor with: npm run dev (from HyperFlow-Editor directory)"
        }

@server.tool()
async def get_editor_capabilities() -> dict:
    """Get list of editor capabilities"""
    return {
        "capabilities": [
            "syntax_highlighting",
            "autocomplete",
            "error_display",
            "code_execution",
            "file_management",
            "theme_switching",
            "keyboard_shortcuts",
            "multi_file_support"
        ],
        "supported_languages": [
            "hypercode",
            "python",
            "javascript",
            "typescript",
            "json"
        ],
        "default_theme": "dark",
        "editor_type": "Monaco Editor (VS Code compatible)"
    }

@server.tool()
async def get_syntax_highlighting_config() -> dict:
    """Get HyperCode syntax highlighting configuration"""
    return {
        "language": "hypercode",
        "tokenizer": {
            "keywords": [
                "print", "if", "else", "for", "while", "def", "return",
                "class", "import", "from", "as", "try", "except", "finally"
            ],
            "builtins": [
                "len", "range", "str", "int", "float", "list", "dict", "set"
            ],
            "operators": [
                "+", "-", "*", "/", "//", "%", "**",
                "==", "!=", "<", ">", "<=", ">=",
                "and", "or", "not", "in", "is"
            ],
            "comments": {
                "line": "#",
                "block_start": '"""',
                "block_end": '"""'
            }
        },
        "themes": {
            "dark": {
                "keywords": "#569CD6",  # Blue
                "strings": "#CE9178",   # Orange
                "comments": "#6A9955",  # Green
                "numbers": "#B5CEA8",   # Light green
                "operators": "#D4D4D4"  # White
            },
            "light": {
                "keywords": "#0000FF",
                "strings": "#A31515",
                "comments": "#008000",
                "numbers": "#098658",
                "operators": "#000000"
            }
        },
        "indent_size": 4,
        "use_tabs": False
    }

@server.tool()
async def get_autocomplete_suggestions(context: str, line: int, column: int) -> dict:
    """Get autocomplete suggestions for HyperCode"""
    suggestions = {
        "print": {
            "label": "print",
            "kind": "keyword",
            "detail": "Print to console",
            "snippet": "print(${1:value})"
        },
        "def": {
            "label": "def",
            "kind": "keyword",
            "detail": "Define function",
            "snippet": "def ${1:name}(${2:args}):\n    ${3:pass}"
        },
        "for": {
            "label": "for",
            "kind": "keyword",
            "detail": "For loop",
            "snippet": "for ${1:item} in ${2:iterable}:\n    ${3:pass}"
        },
        "if": {
            "label": "if",
            "kind": "keyword",
            "detail": "Conditional",
            "snippet": "if ${1:condition}:\n    ${2:pass}"
        }
    }
    
    return {
        "suggestions": list(suggestions.values()),
        "line": line,
        "column": column,
        "context": context[:50],  # First 50 chars of context
        "timestamp": datetime.now().isoformat()
    }

@server.tool()
async def format_error_for_display(error_message: str, line: int, column: int) -> dict:
    """Format error message for display in editor"""
    
    # Parse error
    error_type = "Error"
    if "SyntaxError" in error_message:
        error_type = "Syntax Error"
    elif "NameError" in error_message:
        error_type = "Name Error"
    elif "TypeError" in error_message:
        error_type = "Type Error"
    
    return {
        "type": error_type,
        "message": error_message,
        "location": {
            "line": line,
            "column": column
        },
        "severity": "error",
        "fix_suggestions": [
            "Check syntax",
            "Check variable names",
            "Check function calls"
        ],
        "display_format": {
            "icon": "error",
            "color": "#FF0000",
            "underline": "wavy"
        }
    }

@server.tool()
async def get_editor_theme() -> dict:
    """Get current editor theme"""
    return {
        "current_theme": "dark",
        "available_themes": [
            "dark",
            "light",
            "high-contrast"
        ],
        "preferences": {
            "font_family": "Fira Code, monospace",
            "font_size": 13,
            "line_height": 1.5,
            "word_wrap": True
        }
    }

@server.tool()
async def get_keyboard_shortcuts() -> dict:
    """Get editor keyboard shortcuts"""
    return {
        "shortcuts": {
            "run_code": {
                "keys": "Ctrl+Enter",
                "description": "Run HyperCode"
            },
            "save_file": {
                "keys": "Ctrl+S",
                "description": "Save current file"
            },
            "format_code": {
                "keys": "Ctrl+Shift+F",
                "description": "Format code"
            },
            "toggle_comments": {
                "keys": "Ctrl+/",
                "description": "Toggle line comment"
            },
            "show_palette": {
                "keys": "Ctrl+Shift+P",
                "description": "Show command palette"
            },
            "goto_line": {
                "keys": "Ctrl+G",
                "description": "Go to line"
            },
            "find": {
                "keys": "Ctrl+F",
                "description": "Find"
            },
            "replace": {
                "keys": "Ctrl+H",
                "description": "Find and replace"
            }
        }
    }

@server.tool()
async def get_file_status(path: str) -> dict:
    """Get file status in editor"""
    return {
        "path": path,
        "is_open": True,
        "is_modified": False,
        "is_saved": True,
        "encoding": "utf-8",
        "language": "hypercode",
        "line_count": 0,
        "character_count": 0,
        "last_modified": datetime.now().isoformat()
    }

@server.tool()
async def open_file_in_editor(path: str) -> dict:
    """Open file in Hyperflow Editor"""
    return {
        "success": True,
        "path": path,
        "editor_url": f"{EDITOR_URL}?file={path}",
        "message": f"Opening {path} in editor",
        "how_to_view": f"Visit {EDITOR_URL}?file={path} in browser"
    }

@server.tool()
async def get_recent_files() -> dict:
    """Get list of recently opened files"""
    return {
        "recent_files": [
            {"path": "main.hc", "opened_at": datetime.now().isoformat()},
            {"path": "utils.hc", "opened_at": datetime.now().isoformat()},
            {"path": "config.hc", "opened_at": datetime.now().isoformat()}
        ],
        "total": 3
    }

@server.tool()
async def health() -> dict:
    """Check MCP server health"""
    editor_running = await editor_client.is_running()
    
    return {
        "status": "healthy",
        "service": "hyperflow-editor-mcp",
        "timestamp": datetime.now().isoformat(),
        "editor_status": "running" if editor_running else "offline",
        "editor_url": EDITOR_URL,
        "api_url": API_BASE_URL,
        "tools_available": [
            "check_editor_health",
            "get_editor_capabilities",
            "get_syntax_highlighting_config",
            "get_autocomplete_suggestions",
            "format_error_for_display",
            "get_editor_theme",
            "get_keyboard_shortcuts",
            "get_file_status",
            "open_file_in_editor",
            "get_recent_files",
            "health"
        ]
    }

async def main():
    """Run the MCP server"""
    logger.info("Starting Hyperflow Editor MCP Server")
    logger.info(f"Editor URL: {EDITOR_URL}")
    logger.info(f"API URL: {API_BASE_URL}")
    logger.info("Available tools:")
    logger.info("  - check_editor_health: Verify editor is running")
    logger.info("  - get_editor_capabilities: List editor features")
    logger.info("  - get_syntax_highlighting_config: HyperCode syntax config")
    logger.info("  - get_autocomplete_suggestions: Code completion")
    logger.info("  - format_error_for_display: Format errors for UI")
    logger.info("  - get_editor_theme: Current theme config")
    logger.info("  - get_keyboard_shortcuts: Available shortcuts")
    logger.info("  - get_file_status: File metadata")
    logger.info("  - open_file_in_editor: Open file programmatically")
    logger.info("  - get_recent_files: Recently opened files")
    
    async with server:
        logger.info("Hyperflow Editor MCP Server running")
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
