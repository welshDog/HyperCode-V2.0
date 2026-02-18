
import os
import logging
import sys
from pathlib import Path
from typing import List, Optional, Any

# Add project root to python path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

try:
    from scripts.hafs.embeddings import EmbeddingEngine
    from scripts.hafs.semantic import extract_dependencies
except ImportError as e:
    print(f"Error importing HAFS: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HAFS.Documenter")

class AutoDocumenter:
    def __init__(self, root_dir: Path = ROOT_DIR):
        self.root_dir = root_dir
        self.embedding_engine = EmbeddingEngine(root_dir)

    def generate_docs(self, file_path: Path) -> str:
        """
        Generate documentation for a specific file using semantic context.
        """
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            # Create a simple dependency string
            deps = extract_dependencies(file_path)
            
            # Find semantically similar code to use as examples/context
            # Use the first 500 chars as a query signature
            query = content[:500] if len(content) > 500 else content
            similar_code = self.embedding_engine.search(query, n_results=3)
            
            # Template for documentation (Simulated LLM Generation)
            doc_content = f"# Module: {file_path.name}\n\n"
            doc_content += f"## Overview\nAuto-generated documentation for `{file_path.relative_to(self.root_dir)}`.\n\n"
            
            doc_content += "## Dependencies\n"
            if deps:
                for d in deps:
                    doc_content += f"- {d}\n"
            else:
                doc_content += "None\n"

            doc_content += "\n## Contextual Relevance\nBased on semantic analysis, this module is related to:\n"
            for r in similar_code:
                # distance might be None or float
                score = r['distance'] if r['distance'] is not None else 0.0
                doc_content += f"- `{r['id']}` (Score: {score:.2f})\n"
                
            doc_content += "\n## Source Snippet\n```python\n"
            doc_content += (content[:500] + "\n...\n```") if len(content) > 500 else (content + "\n```")
            
            return doc_content
            
        except Exception as e:
            logger.error(f"Documentation failed for {file_path}: {e}")
            return f"Error generating docs: {e}"

    def save_docs(self, file_path: Path, output_dir: Path):
        """Save generated docs to markdown file."""
        doc = self.generate_docs(file_path)
        # Use stem for filename
        output_path = output_dir / f"{file_path.stem}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            f.write(doc)
        logger.info(f"Generated docs: {output_path}")

if __name__ == "__main__":
    # Test
    documenter = AutoDocumenter()
    # Normalize path
    target = (ROOT_DIR / "agents/crew-orchestrator/main.py").resolve()
    output = (ROOT_DIR / "docs/auto_generated").resolve()
    
    if target.exists():
        print(f"--- Documenting {target} ---")
        documenter.save_docs(target, output)
    else:
        print(f"Error: Target file {target} does not exist.")
