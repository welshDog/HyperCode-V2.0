import logging
from app.agents.brain import brain
from app.core.storage import storage
from datetime import datetime

logger = logging.getLogger(__name__)

class ResearchAgent:
    """
    The Archivist: A specialized agent for deep technical research.
    Uses Perplexity to find cutting-edge information and format it for the Living Digital Paper.
    """
    def __init__(self):
        self.role = "Research Specialist"
    
    async def process(self, topic: str, context: dict = None) -> str:
        """
        Conducts research on a given topic and uploads report to MinIO.
        """
        logger.info(f"[{self.role}] Starting research on: {topic}")
        
        prompt = (
            f"Act as an expert technical researcher and archivist. "
            f"Compose a comprehensive analytical report that thoroughly examines the following subject: '{topic}'. "
            f"The report must be suitable for presentation to stakeholders and decision-makers. "
            f"Format the output as a structured technical summary with: "
            f"1. Executive Summary "
            f"2. Methodology & Approach "
            f"3. Key Findings & Data Analysis (with supporting evidence) "
            f"4. Code Examples or Architectural Patterns (where applicable) "
            f"5. Actionable Recommendations "
            f"6. Conclusion "
            f"7. References & Citations. "
            f"Ensure the report follows professional formatting standards, includes relevant charts or tables where applicable. "
            f"Keep the tone professional, concise, and optimized for a neurodivergent audience (clear headers, bullet points, spatial logic)."
        )
        
        # 1. Think
        report_content = await brain.think(self.role, prompt)
        
        # 2. Upload to MinIO (if context provided)
        if context and context.get("task_id"):
            task_id = context.get("task_id")
            filename = f"research_{task_id}.md"
            
            metadata = {
                "agent": self.role,
                "topic": topic,
                "created_at": datetime.utcnow().isoformat(),
                "task_id": str(task_id)
            }
            
            try:
                # Upload using the robust storage service
                s3_key = storage.upload_file(report_content, filename, metadata)
                if s3_key:
                    logger.info(f"[{self.role}] Report uploaded to Object Storage: {s3_key}")
                    # Append MinIO link to the output (for visibility)
                    report_content += f"\n\n---\n**Archived in MinIO**: `{s3_key}`"
            except Exception as e:
                logger.error(f"[{self.role}] Failed to upload report to MinIO: {e}")
                report_content += f"\n\n---\n**Archive Error**: Could not upload to Object Storage ({str(e)})"

        return report_content

# Global instance
researcher = ResearchAgent()
