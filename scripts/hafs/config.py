
import os
from pathlib import Path

# Base Paths
ROOT_DIR = Path(os.getcwd())
AI_DIR = ROOT_DIR / ".ai"
DOCS_DIR = ROOT_DIR / "docs"
AGENTS_DIR = ROOT_DIR / "agents"

# Index Paths
MASTER_INDEX_PATH = AI_DIR / "MASTER_INDEX.json"
PROJECT_CONTEXT_PATH = AI_DIR / "PROJECT_CONTEXT.md"

# Ignore Patterns
IGNORE_DIRS = {
    ".git", ".venv", "node_modules", "__pycache__", 
    ".idea", ".vscode", "dist", "build", "coverage", 
    "tmp", "temp", "logs", ".pytest_cache", ".mypy_cache"
}

IGNORE_FILES = {
    ".DS_Store", "Thumbs.db", "*.log", "*.pyc", "*.pyo"
}

# File Types of Interest
CODE_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".c", ".cpp"}
DOC_EXTENSIONS = {".md", ".txt", ".rst"}
CONFIG_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".ini", ".env"}

# Semantic Layers
LAYERS = {
    "core": ["hypercode-core", "core"],
    "agents": ["agents", "crew"],
    "ui": ["broski-terminal", "frontend", "ui"],
    "infra": ["docker", "k8s", "terraform", "ansible"],
    "docs": ["docs"],
    "scripts": ["scripts"]
}
