import logging
import json
from app.agents.brain import brain
from app.core.storage import get_storage
from datetime import datetime

logger = logging.getLogger(__name__)

class ArchitectAgent:
    """
    The Architect: Orchestrates a multi-agent workflow to build software.
    Acts as the 'Planner' and 'Manager' described in the Research Report.
    """
    def __init__(self):
        self.role = "System Architect"

    async def process(self, goal: str, context: dict = None) -> str:
        """
        Executes the Multi-Agent Workflow: Plan -> Code -> Review.
        """
        logger.info(f"[{self.role}] Initializing Swarm for goal: {goal}")
        
        # 1. PLANNER AGENT
        logger.info(f"[{self.role}] Phase 1: Planning...")
        plan_prompt = (
            f"Act as a Senior Software Architect. "
            f"Goal: {goal}\n"
            f"Create a detailed, step-by-step implementation plan. "
            f"Return ONLY a JSON array of steps, where each step has a 'title' and 'description'."
        )
        plan_json_str = await brain.think("Planner Agent", plan_prompt)
        
        # Simple cleanup to ensure JSON
        try:
            # Strip markdown code blocks if present
            clean_json = plan_json_str.replace("```json", "").replace("```", "").strip()
            steps = json.loads(clean_json)
        except Exception:
            logger.warning(f"[{self.role}] Failed to parse JSON plan. Using raw text fallback.")
            steps = [{"title": "Execute Goal", "description": goal}]

        # 2. CODER AGENT (Loop through steps)
        logger.info(f"[{self.role}] Phase 2: Coding...")
        code_artifacts = []
        
        for i, step in enumerate(steps):
            step_title = step.get('title', f'Step {i+1}')
            step_desc = step.get('description', '')
            
            logger.info(f"[{self.role}] executing step {i+1}: {step_title}")
            
            code_prompt = (
                f"Act as a Senior Python Developer. "
                f"Task: {step_title}\n"
                f"Description: {step_desc}\n"
                f"Context: We are building '{goal}'.\n"
                f"Write the necessary code. Include comments. Return ONLY the code."
            )
            code = await brain.think("Coder Agent", code_prompt)
            code_artifacts.append(f"### Step {i+1}: {step_title}\n\n```python\n{code}\n```")

        # 3. REVIEWER AGENT
        logger.info(f"[{self.role}] Phase 3: Reviewing...")
        full_code = "\n".join(code_artifacts)
        review_prompt = (
            f"Act as a QA Security Engineer. "
            f"Review the following code for security vulnerabilities and best practices:\n"
            f"{full_code}\n"
            f"Provide a summary of issues and a 'Pass/Fail' grade."
        )
        review = await brain.think("Reviewer Agent", review_prompt)

        # 4. COMPILE REPORT
        final_report = (
            f"# 🏗️ Multi-Agent Build Report: {goal}\n\n"
            f"## 1. Architecture Plan\n"
            f"{json.dumps(steps, indent=2)}\n\n"
            f"## 2. Implementation\n"
            f"{full_code}\n\n"
            f"## 3. Security Review\n"
            f"{review}\n"
        )

        storage = get_storage()

        # 5. ARCHIVE
        if context and context.get("task_id"):
            task_id = context.get("task_id")
            filename = f"build_{task_id}.md"
            metadata = {
                "agent": self.role,
                "goal": goal,
                "created_at": datetime.utcnow().isoformat(),
                "task_id": str(task_id)
            }
            try:
                s3_key = storage.upload_file(final_report, filename, metadata)
                final_report += f"\n\n---\n**Archived in MinIO**: `{s3_key}`"
            except Exception as e:
                logger.error(f"[{self.role}] Upload failed: {e}")

        return final_report

# Global Instance
architect = ArchitectAgent()
