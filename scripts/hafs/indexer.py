
import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from .config import ROOT_DIR, IGNORE_DIRS, IGNORE_FILES, CODE_EXTENSIONS, LAYERS
from .semantic import extract_dependencies
from .utils import get_logger
from .embeddings import EmbeddingEngine

logger = get_logger("HAFS.Indexer")

class Indexer:
    def __init__(self, root_dir: Path = ROOT_DIR):
        self.root_dir = root_dir
        self.index_path = root_dir / ".ai" / "MASTER_INDEX.json"
        self.context_path = root_dir / ".ai" / "PROJECT_CONTEXT.md"
        self.graph = {"nodes": {}, "edges": []}
        self.taxonomy = {}
        self.embedding_engine = EmbeddingEngine(root_dir) # Initialize embeddings
        
    def scan(self, with_embeddings: bool = False):
        """Full repository scan and index generation."""
        logger.info(f"Starting scan of {self.root_dir}...")
        start_time = time.time()
        
        self.graph = {"nodes": {}, "edges": []} # Reset
        self.taxonomy = {layer: [] for layer in LAYERS}
        
        files_to_embed = []
        
        for root, dirs, files in os.walk(self.root_dir):
            # Prune ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]
            
            rel_root = Path(root).relative_to(self.root_dir)
            
            for file in files:
                if file in IGNORE_FILES or file.startswith("."):
                    continue
                    
                file_path = Path(root) / file
                rel_path = rel_root / file
                
                # Index the file
                self._index_file(file_path, str(rel_path))
                
                if with_embeddings and file_path.suffix in CODE_EXTENSIONS:
                    files_to_embed.append(file_path)

        self._save_index()
        self._generate_context()
        
        if with_embeddings and files_to_embed:
            logger.info(f"Generating embeddings for {len(files_to_embed)} files...")
            self.embedding_engine.index_files(files_to_embed)
        
        duration = time.time() - start_time
        logger.info(f"Scan complete in {duration:.2f}s. Indexed {len(self.graph['nodes'])} files.")

    def update_file(self, file_path: Path):
        """Update index for a single file (Reactive)."""
        try:
            rel_path = file_path.relative_to(self.root_dir)
            logger.info(f"Updating index for: {rel_path}")
            self._index_file(file_path, str(rel_path))
            self._save_index()
            
            # Update embedding if code
            if file_path.suffix in CODE_EXTENSIONS:
                 self.embedding_engine.index_files([file_path])
                 
        except ValueError:
            pass # Path not relative to root

    def _index_file(self, full_path: Path, rel_path: str):
        """Extract metadata and dependencies for a file."""
        file_type = "unknown"
        suffix = full_path.suffix.lower()
        
        if suffix in CODE_EXTENSIONS:
            file_type = "code"
        elif suffix in {".md", ".txt"}:
            file_type = "doc"
        
        # Determine Layer
        layer = "other"
        for l_name, keywords in LAYERS.items():
            if any(k in rel_path.lower() for k in keywords):
                layer = l_name
                break
        
        # Semantic Analysis
        deps = []
        if file_type == "code":
            deps = extract_dependencies(full_path)
            
        # Add Node
        node_data = {
            "type": file_type,
            "layer": layer,
            "size": full_path.stat().st_size,
            "last_modified": full_path.stat().st_mtime,
            "dependencies": deps
        }
        self.graph["nodes"][rel_path] = node_data
        
        # Add Edges (Basic Linking)
        # In a real graph, we'd resolve 'deps' to actual file paths.
        # For now, we store them as raw dependency strings.
        for dep in deps:
            self.graph["edges"].append({
                "source": rel_path,
                "target": dep, 
                "relation": "imports"
            })

    def _save_index(self):
        """Persist the graph to JSON."""
        output = {
            "meta": {
                "version": "2.1.0",
                "last_updated": datetime.now().isoformat(),
                "generator": "HAFS.Indexer"
            },
            "graph": self.graph
        }
        
        self.index_path.parent.mkdir(exist_ok=True)
        with open(self.index_path, "w") as f:
            json.dump(output, f, indent=2)

    def _generate_context(self):
        """Generate a markdown summary of the project state."""
        # Simple summary for now
        node_count = len(self.graph["nodes"])
        layers = {}
        for path, data in self.graph["nodes"].items():
            l = data.get("layer", "other")
            layers[l] = layers.get(l, 0) + 1
            
        content = f"""# HyperCode V2.0 - Project Context
        
**Last Updated:** {datetime.now().isoformat()}
**Total Files:** {node_count}

## Layer Distribution
"""
        for l, count in layers.items():
            content += f"- **{l}**: {count} files\n"
            
        content += "\n## Key Entry Points\n"
        # Heuristic for entry points
        for path in self.graph["nodes"]:
            if "main" in path or "app" in path or "index" in path:
                if len(path.split("/")) < 4: # High level
                    content += f"- `{path}`\n"

        with open(self.context_path, "w") as f:
            f.write(content)

if __name__ == "__main__":
    import sys
    with_embeddings = "--embeddings" in sys.argv
    indexer = Indexer()
    indexer.scan(with_embeddings=with_embeddings)
