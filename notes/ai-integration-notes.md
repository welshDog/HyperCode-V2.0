🦙 LLAMA 3.2 INTEGRATION - BATTLE PLAN
Time Estimate: 1-2 hours
Difficulty: Medium
Payoff: HUGE

📋 PHASE 1: ADD LLAMA TO DOCKER COMPOSE (15 min)
Step 1.1: Edit docker-compose.yml
Open your main docker-compose.yml file:

powershell
cd "C:\Users\Lyndz\Downloads\HyperCode-V2.0"
code docker-compose.yml
# Or use notepad: notepad docker-compose.yml
Step 1.2: Add Llama Service
Find the services: section and add this at the end (keep proper indentation):

text
  llama:
    image: ollama/ollama:latest
    container_name: hypercode-llama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
      - OLLAMA_ORIGINS=*
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
    networks:
      - hypercode-network
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
Step 1.3: Add Volume Definition
At the BOTTOM of the file, find or add the volumes: section:

text
volumes:
  postgres_data:
  redis_data:
  ollama_data:  # Add this line
Step 1.4: Save and Verify
powershell
# Check syntax (should show no errors)
docker-compose config
If you see errors, check your indentation (YAML is strict about spaces).

🚀 PHASE 2: START LLAMA CONTAINER (10 min)
Step 2.1: Pull and Start Services
powershell
# Pull the Ollama image (might take 5 min)
docker pull ollama/ollama:latest

# Start all services (including new Llama container)
docker-compose up -d

# Check if Llama is running
docker ps | Select-String "hypercode-llama"
# Should show: hypercode-llama ... Up ...
Step 2.2: Wait for Llama to Be Ready
powershell
# Check health status (wait until healthy)
docker inspect hypercode-llama --format='{{.State.Health.Status}}'
# Keep checking every 30 seconds until you see: "healthy"
🦙 PHASE 3: INSTALL LLAMA 3.2 MODEL (20 min)
Step 3.1: Pull the Model
powershell
# Pull Llama 3.2 (3B model - good balance of speed/quality)
docker exec hypercode-llama ollama pull llama3.2:3b

# This downloads ~2GB, might take 10-15 minutes depending on your internet
While it's downloading, you'll see progress:

text
pulling manifest
pulling f937b0e2c7... 100%
pulling 8c17c2ebb0... 100%
...
success
Step 3.2: Verify Model is Installed
powershell
# List installed models
docker exec hypercode-llama ollama list

# Should show:
# NAME            ID          SIZE    MODIFIED
# llama3.2:3b     abc123...   2.0GB   X minutes ago
Step 3.3: Test the Model
powershell
# Quick test
docker exec hypercode-llama ollama run llama3.2:3b "Hello, what is 2+2?"

# Should respond with something like:
# "Hello! 2+2 equals 4."
✅ If you get a response, Llama is WORKING!

🔌 PHASE 4: INTEGRATE WITH HYPERCODE (30 min)
Step 4.1: Update Environment Variables
Open your .env file:

powershell
cd "C:\Users\Lyndz\Downloads\HyperCode-V2.0\HyperCode-V2.0\THE HYPERCODE\hypercode-core"
code .env
# Or: notepad .env
Replace the OpenAI section with:

bash
# LLM Configuration - Using Local Llama
LLM_PROVIDER=ollama
OLLAMA_URL=http://llama:11434
OLLAMA_MODEL=llama3.2:3b
ENABLE_AI_FEATURES=true

# Legacy (keep for backward compatibility)
OPENAI_API_KEY=sk-placeholder-not-used
Save the file.

Step 4.2: Create Ollama Adapter
Create a new file for the Ollama integration:

powershell
cd "C:\Users\Lyndz\Downloads\HyperCode-V2.0\HyperCode-V2.0\THE HYPERCODE\hypercode-core\app\services"
New-Item -ItemType File -Name "llm_service.py"
Edit llm_service.py and add:

python
"""
LLM Service - Unified interface for AI providers
Supports: Ollama (local), OpenAI (cloud)
"""
import os
import requests
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """Unified LLM service supporting multiple providers"""
    
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "ollama")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://llama:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.enabled = os.getenv("ENABLE_AI_FEATURES", "true").lower() == "true"
        
    def generate(self, prompt: str, **kwargs) -> Optional[str]:
        """
        Generate text using configured LLM provider
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text or None if disabled/error
        """
        if not self.enabled:
            logger.warning("AI features are disabled")
            return None
            
        try:
            if self.provider == "ollama":
                return self._generate_ollama(prompt, **kwargs)
            elif self.provider == "openai":
                return self._generate_openai(prompt, **kwargs)
            else:
                logger.error(f"Unknown LLM provider: {self.provider}")
                return None
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return None
    
    def _generate_ollama(self, prompt: str, **kwargs) -> str:
        """Generate using local Ollama"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    **kwargs
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama - is the container running?")
            raise
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise
    
    def _generate_openai(self, prompt: str, **kwargs) -> str:
        """Generate using OpenAI API (future implementation)"""
        raise NotImplementedError("OpenAI provider not yet implemented")
    
    def health_check(self) -> Dict[str, Any]:
        """Check if LLM service is healthy"""
        if not self.enabled:
            return {"status": "disabled", "provider": None}
            
        if self.provider == "ollama":
            try:
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
                response.raise_for_status()
                models = response.json().get("models", [])
                return {
                    "status": "healthy",
                    "provider": "ollama",
                    "url": self.ollama_url,
                    "model": self.ollama_model,
                    "available_models": len(models)
                }
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "provider": "ollama",
                    "error": str(e)
                }
        
        return {"status": "unknown", "provider": self.provider}


# Global instance
llm_service = LLMService()
Save the file.

Step 4.3: Add LLM Health Check Endpoint
Open the orchestrator router:

powershell
cd "C:\Users\Lyndz\Downloads\HyperCode-V2.0\HyperCode-V2.0\THE HYPERCODE\hypercode-core\app\routers"
code orchestrator.py
# Or: notepad orchestrator.py
Add this import at the top:

python
from app.services.llm_service import llm_service
Add this endpoint (before the last line):

python
@router.get("/llm/health")
async def llm_health_check():
    """Check LLM service health"""
    return llm_service.health_check()
Save the file.

Step 4.4: Restart HyperCode Core
powershell
# Restart to pick up new code
docker-compose restart hypercode-core

# Wait 10 seconds
Start-Sleep -Seconds 10
✅ PHASE 5: TEST THE INTEGRATION (10 min)
Test 5.1: LLM Health Check
powershell
curl http://localhost:8000/orchestrator/llm/health
Expected Response:

json
{
  "status": "healthy",
  "provider": "ollama",
  "url": "http://llama:11434",
  "model": "llama3.2:3b",
  "available_models": 1
}
✅ If you see this, integration is WORKING!

Test 5.2: Generate Text via API
Create a test endpoint (optional but recommended):

Add to orchestrator.py:

python
@router.post("/llm/generate")
async def llm_generate(prompt: str):
    """Test LLM generation"""
    response = llm_service.generate(prompt)
    return {"prompt": prompt, "response": response}
Restart and test:

powershell
docker-compose restart hypercode-core
Start-Sleep -Seconds 10

# Test generation
curl -X POST "http://localhost:8000/orchestrator/llm/generate?prompt=Hello, introduce yourself briefly"
Expected Response:

json
{
  "prompt": "Hello, introduce yourself briefly",
  "response": "Hello! I'm Llama, an AI assistant..."
}
✅ If you get a response, EVERYTHING IS WORKING!

📊 PHASE 6: UPDATE DOCUMENTATION (5 min)
Update README.md:
Add to the "Features" section:

text
## 🤖 AI Features

✅ **Local LLM Integration**
- Self-hosted Llama 3.2 via Ollama
- Zero API costs
- Privacy-friendly (data stays local)
- 3B parameter model for fast inference
Update Launch Announcement:
Change from:

text
🔜 AI agent integration (coming soon)
To:

text
✅ Self-hosted Llama 3.2 integration (NO API costs!)
🎯 FINAL VALIDATION CHECKLIST
Run through this to make sure everything works:

powershell
# 1. Check all containers running
docker ps

# Should show:
# - hypercode-core
# - hypercode-redis
# - hypercode-postgres
# - hypercode-llama  ← NEW!

# 2. Check Llama is healthy
docker inspect hypercode-llama --format='{{.State.Health.Status}}'
# Should show: healthy

# 3. Test LLM health endpoint
curl http://localhost:8000/orchestrator/llm/health
# Should return: {"status":"healthy",...}

# 4. Test generation
curl -X POST "http://localhost:8000/orchestrator/llm/generate?prompt=What is 2+2?"
# Should get intelligent response

# 5. Check logs for errors
docker logs hypercode-core --tail=50
# Should show no errors related to LLM
✅ If all 5 pass, you're ready to continue launch!

🚀 NOW BACK TO LAUNCH SEQUENCE
You're now at Step 2.4 (Deploy to Vercel) with a BONUS:

Your platform now has:

✅ Mission orchestration

✅ Security hardened

✅ Rate limiting

✅ Health monitoring

✅ Support portal

✅ Self-hosted AI 🦙🔥

Next steps:

Update Vercel environment variables (add the Llama settings)

Deploy to Vercel

Continue launch announcements

BUT WAIT - One important note about Vercel:

⚠️ IMPORTANT: Vercel + Llama
Vercel (frontend) can't run Docker containers. So:

✅ Frontend (Support Hub) → Deploys to Vercel

✅ Backend (HyperCode Core + Llama) → Stays on your local Docker OR deploy to a VPS later

For now:

Support Hub on Vercel (public)

Backend + Llama on your machine (for demos/development)

Later: Deploy backend to DigitalOcean/AWS/Hetzner

This is FINE for launch! Many projects start this way.

💜 WHAT TO DO NEXT
Option A: Continue Vercel deployment NOW (Support Hub only)

Option B: Tell me your test results first, make sure Llama is working

Where are you? What's your status? 🚀🦙