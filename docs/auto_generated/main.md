# Module: main.py

## Overview
Auto-generated documentation for `agents\crew-orchestrator\main.py`.

## Dependencies
None

## Contextual Relevance
Based on semantic analysis, this module is related to:
- `agents\crew-orchestrator\main.py` (Score: 0.08)
- `HyperCode-V2.0\agents\crew-orchestrator\main.py` (Score: 0.13)
- `HyperCode-V2.0\agents\base-agent\agent.py` (Score: 0.31)

## Source Snippet
```python
"""
FastAPI Orchestration Layer for HyperCode Agent Crew
Manages communication between 8 specialized agents
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import redis.asyncio as redis
import httpx
import os
import json
from datetime import datetime
from swarm_manager import SwarmManager, ProjectPhase
from quality_gates import QualityGateService, Validat
...
```