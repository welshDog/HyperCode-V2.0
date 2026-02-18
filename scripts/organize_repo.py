#!/usr/bin/env python3
"""
Hyper AI File System - Repository Organizer (Phase 1)
-----------------------------------------------------
This script implements the initial structural hygiene for HyperCode V2.0.
It transforms the flat, messy root directory into a structured, neurodivergent-friendly,
AI-optimized hierarchy.

Features:
1. Moves files to `docs/`, `archive/`, etc. based on semantic rules.
2. Generates the initial `.ai/MASTER_INDEX.json` for agent navigation.
3. Creates `.ai/PROJECT_CONTEXT.md` for LLM system prompts.
"""

import os
import shutil
import json
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---

ROOT_DIR = Path(".")

# Files to specific destinations
FILE_MOVES = {
    # Reports
    "docs/reports": [
        "COMPREHENSIVE_PROJECT_ANALYSIS_2026.md",
        "POST_UPDATE_HEALTH_CHECK_COMPLETE.md",
        "POST_UPGRADE_HEALTH_REPORT.md",
        "GO_LIVE_VALIDATION_REPORT_2026-02-12.md",
        "TEST_UPGRADE_ANALYSIS_REPORT.md",
        "TEST_UPGRADE_COMPLETION_SUMMARY.md",
        "STATUS_REPORT_UPDATED.md",
        "Project_Status_Report.md",
        "ANALYSIS_REPORT_INDEX.md",
        "FULL_PROJECT_REPORT_2026.md",
        "POST_UPDATE_RECOVERY_COMPLETE.md",
        "POST_UPGRADE_COMPREHENSIVE_REPORT_2026.md",
        "STAGE_0_COMPLETION_REPORT.md",
        "STATUS_REPORT.md",
        "TEST_UPGRADE_EXECUTIVE_SUMMARY.md",
        "TEST_UPGRADE_QUICK_FIX_CHECKLIST.md",
        "TEST_VERIFICATION_REPORT_POST_FIXES.md",
        "THE HYPER HEALTH CHECK",
        "VERIFICATION_PROTOCOL.md",
        "VERIFICATION_REPORT.md",
        "BACKUP_VERIFICATION_REPORT.md",
        "Health_Assessment_Report.md"
    ],
    
    # Guides & How-To
    "docs/guides": [
        "guide infrastructure setup",
        "Agents help build project",
        "DEPLOYMENT_SUMMARY_ONE_PAGE.md",
        "Docker_Hardening_Plan.md",
        "BACKUP_STRATEGY.md",
        "TEST_UPGRADE_PROCEDURES_TEMPLATE.md"
    ],
    
    # Design & Strategy
    "docs/design": [
        "AGENT_STRATEGY.md",
        "FUTURE_CAPABILITIES_ROADMAP.md",
        "EXECUTIVE_SUMMARY_ACTION_PLAN.md",
        "🤖 The AI Index System.MD"
    ],
    
    # Core Documentation
    "docs": [
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        "LICENSE",
        "TEST_UPGRADE_DOCUMENT_INDEX.md",
        "TEST_UPGRADE_FINAL_INDEX.md"
    ],
    
    # Archive / Temporary
    "archive": [
        "CRITICAL_FIXES_COPY_PASTE.md",
        "FIX_VERIFICATION_COMPLETE.md",
        "OLLAMA_HEALTH_CHECK_FIX.md",
        "TEST_FINAL_VERIFICATION_REPORT.md",
        "PRODUCTION_DEPLOYMENT_APPROVED.md",
        "the Docker report update",
        "help1",
        "next1",
        "next2.md",
        "Hyper Agent Factory",
        "boom docker dead"
    ]
}

# Directories to ensure exist
DIRS_TO_CREATE = [
    "docs/guides",
    "docs/reports",
    "docs/design",
    ".ai",
    "archive",
    "scripts",
    "agents",
    "tests"
]

# --- Functions ---

def ensure_directories():
    """Create necessary directories if they don't exist."""
    for dir_name in DIRS_TO_CREATE:
        path = ROOT_DIR / dir_name
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Ensure directory: {path}")

def move_files():
    """Move files based on configuration."""
    moved_count = 0
    for target_dir, filenames in FILE_MOVES.items():
        target_path = ROOT_DIR / target_dir
        target_path.mkdir(parents=True, exist_ok=True)
        
        for filename in filenames:
            source = ROOT_DIR / filename
            if source.exists():
                dest = target_path / filename
                try:
                    shutil.move(str(source), str(dest))
                    logger.info(f"📦 Moved: {filename} -> {target_dir}/")
                    moved_count += 1
                except Exception as e:
                    logger.error(f"❌ Failed to move {filename}: {e}")
            else:
                pass # Silent skip if file doesn't exist (it might have been moved already)
    
    logger.info(f"✨ Total files moved: {moved_count}")

def generate_ai_index():
    """Generate .ai/MASTER_INDEX.json for Agent Navigation."""
    index = {
        "meta": {
            "version": "2.0.0",
            "last_updated": datetime.now().isoformat(),
            "generator": "scripts/organize_repo.py"
        },
        "taxonomy": {
            "root": ["README.md", "docker-compose.yml", "QUICKSTART.md"],
            "core_logic": "THE HYPERCODE/",
            "agents": "agents/",
            "docs": "docs/",
            "ui": "BROski Business Agents/broski-terminal/"
        },
        "quick_access": {
            "strategy": "docs/design/AGENT_STRATEGY.md",
            "status": "docs/reports/Project_Status_Report.md",
            "architecture": "docs/design/HYPER_AI_FILE_SYSTEM.md",
            "api_gateway": "agents/crew-orchestrator/main.py"
        }
    }
    
    index_path = ROOT_DIR / ".ai" / "MASTER_INDEX.json"
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)
    logger.info(f"🧠 Generated AI Index: {index_path}")

def generate_project_context():
    """Generate .ai/PROJECT_CONTEXT.md for LLM System Prompts."""
    content = """# HyperCode V2.0 - System Context

## Mission
A neurodivergent-friendly, multi-agent development ecosystem.

## Architecture
- **Agents**: Independent containers (FastAPI/Python) communicating via HTTP/Redis.
- **Orchestrator**: `agents/crew-orchestrator` manages phase transitions and handoffs.
- **Frontend**: `broski-terminal` (Next.js) visualizes the swarm state.
- **Core**: `hypercode-core` provides shared services (Memory, Auth).

## Current Phase
**Production/Optimization**

## Key Locations
- **Agents**: `agents/`
- **Docs**: `docs/`
- **Infra**: `docker-compose.yml`, `k8s/`
"""
    context_path = ROOT_DIR / ".ai" / "PROJECT_CONTEXT.md"
    with open(context_path, "w") as f:
        f.write(content)
    logger.info(f"🧠 Generated Project Context: {context_path}")

def create_docs_index():
    """Create docs/INDEX.md if it doesn't exist."""
    index_path = ROOT_DIR / "docs" / "INDEX.md"
    if not index_path.exists():
        content = """# HyperCode V2.0 Documentation Index

- **[Guides](guides/)**: Practical how-to guides.
- **[Reports](reports/)**: Analysis and status reports.
- **[Design](design/)**: Architecture and strategy documents.
- **[Archive](../archive/)**: Deprecated documents.
"""
        with open(index_path, "w") as f:
            f.write(content)
        logger.info(f"📚 Generated Docs Index: {index_path}")

def main():
    logger.info("🚀 Starting Hyper AI File System Reorganization...")
    ensure_directories()
    move_files()
    generate_ai_index()
    generate_project_context()
    create_docs_index()
    logger.info("✅ Reorganization Complete. The Neural Layer is active.")

if __name__ == "__main__":
    main()
