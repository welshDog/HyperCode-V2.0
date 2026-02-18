
import requests
import json
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HAFS.Corrector")

HAFS_API_URL = "http://localhost:8001"

class SelfCorrector:
    """
    Agentic module for diagnosing and correcting code errors using HAFS semantic search.
    """
    
    def __init__(self, api_url: str = HAFS_API_URL):
        self.api_url = api_url

    def diagnose(self, error_message: str, file_path: str = None) -> Dict[str, Any]:
        """
        Query HAFS to find code relevant to the error.
        """
        try:
            payload = {"error_message": error_message}
            if file_path:
                payload["file_path"] = file_path
                
            response = requests.post(f"{self.api_url}/diagnose", json=payload)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Failed to diagnose error: {e}")
            return {"error": str(e)}

    def suggest_fix(self, diagnosis: Dict[str, Any]) -> str:
        """
        Generate a fix suggestion based on the diagnosis results.
        (In a full implementation, this would call an LLM with the retrieved context).
        """
        if "results" not in diagnosis or not diagnosis["results"]:
            return "No relevant code found for this error."
            
        top_result = diagnosis["results"][0]
        file = top_result["id"]
        snippet = top_result["snippet"]
        
        return f"Suggested Fix Location: {file}\nContext:\n{snippet}\n\nAnalysis: The error '{diagnosis['query']}' is likely related to the code in {file}. Check the snippet above."

if __name__ == "__main__":
    # Test
    corrector = SelfCorrector()
    print("--- Diagnosing Test Error ---")
    diagnosis = corrector.diagnose("ImportError: cannot import name 'ContextWalker'")
    print(json.dumps(diagnosis, indent=2))
    print("\n--- Suggestion ---")
    print(corrector.suggest_fix(diagnosis))
