import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import os
from openai import OpenAI

class CortexAgent:
    """
    CORTEX: The Thinking Core
    Responsibility: Intent Understanding & Task Decomposition
    """
    def __init__(self):
        self.name = "CORTEX"
        self.role = "Thinking Core"
        self.context_memory = []
        
        # Initialize Perplexity Client
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            print(f"[{self.name}] ⚠️ PERPLEXITY_API_KEY not found. Falling back to mock logic.")
            self.client = None
        else:
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.perplexity.ai"
            )
    
    async def analyze_intent(self, user_input: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyzes raw user input to extract intent, complexity, and required actions.
        Uses Perplexity API (sonar-pro) if available, otherwise mock logic.
        """
        print(f"[{self.name}] Analyzing intent for: '{user_input}'")
        
        if self.client:
            try:
                return await self._analyze_with_perplexity(user_input, user_context)
            except Exception as e:
                print(f"[{self.name}] ❌ Perplexity API Error: {e}. Falling back to mock.")
        
        # Mock LLM Logic for Prototype
        intent_payload = {
            "original_input": user_input,
            "timestamp": datetime.now().isoformat(),
            "intent_type": "unknown",
            "complexity": "low",
            "suggested_specialists": [],
            "reasoning": ""
        }
        
        if "refactor" in user_input.lower():
            intent_payload["intent_type"] = "code_modification"
            intent_payload["complexity"] = "medium"
            intent_payload["suggested_specialists"] = ["backend-specialist", "qa-engineer"]
            intent_payload["reasoning"] = "User wants code improvement. Requires Backend for changes and QA for verification."
            
        elif "test" in user_input.lower():
            intent_payload["intent_type"] = "verification"
            intent_payload["complexity"] = "low"
            intent_payload["suggested_specialists"] = ["qa-engineer"]
            intent_payload["reasoning"] = "User explicitly requested testing."
            
        elif "design" in user_input.lower() or "architecture" in user_input.lower():
            intent_payload["intent_type"] = "system_design"
            intent_payload["complexity"] = "high"
            intent_payload["suggested_specialists"] = ["architect", "backend-specialist"]
            intent_payload["reasoning"] = "High-level design request detected."

        self.context_memory.append(intent_payload)
        return intent_payload

    async def _analyze_with_perplexity(self, user_input: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calls Perplexity API to analyze intent.
        """
        system_prompt = """
        You are CORTEX, the central intelligence of the HyperCode system.
        Analyze the user's input and extract structured intent.
        
        Return JSON ONLY with this schema:
        {
            "intent_type": "code_modification" | "verification" | "system_design" | "unknown",
            "complexity": "low" | "medium" | "high",
            "suggested_specialists": ["list", "of", "agent_ids"],
            "reasoning": "Brief explanation of why"
        }
        
        Available Agents:
        - backend-specialist (Python/API/DB)
        - frontend-specialist (React/UI)
        - qa-engineer (Testing)
        - architect (System Design)
        - security-engineer (Auth/Security)
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        # Add context if available
        if user_context:
            messages.insert(1, {"role": "system", "content": f"User Context: {json.dumps(user_context)}"})

        response = self.client.chat.completions.create(
            model="sonar-pro", # Use the reasoning model
            messages=messages,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content
        
        # Clean markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        try:
            parsed_intent = json.loads(content)
            # Enrich with metadata
            parsed_intent["original_input"] = user_input
            parsed_intent["timestamp"] = datetime.now().isoformat()
            
            self.context_memory.append(parsed_intent)
            return parsed_intent
        except json.JSONDecodeError:
            print(f"[{self.name}] ❌ Failed to parse JSON from Perplexity: {content}")
            raise

    async def handoff_to_orchestrator(self, intent_payload: Dict[str, Any]):
        """
        Simulates handing off the refined intent to BROski (Orchestrator).
        """
        print(f"[{self.name}] Handoff to BROski -> {json.dumps(intent_payload, indent=2)}")
        return {"status": "handed_off", "target": "BROski", "payload": intent_payload}
