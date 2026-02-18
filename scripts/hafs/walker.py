
import json
from pathlib import Path
from typing import List, Dict, Any

from .config import MASTER_INDEX_PATH

class ContextWalker:
    def __init__(self):
        self.index_path = MASTER_INDEX_PATH
        self.graph = self._load_index()

    def _load_index(self) -> Dict:
        if not self.index_path.exists():
            return {"nodes": {}, "edges": []}
        try:
            with open(self.index_path, "r") as f:
                data = json.load(f)
                return data.get("graph", {"nodes": {}, "edges": []})
        except json.JSONDecodeError:
            return {"nodes": {}, "edges": []}

    def get_context(self, file_path: str) -> Dict[str, Any]:
        """
        Retrieve context for a specific file.
        Returns:
            - Metadata for the file.
            - Direct dependencies (imports).
            - Reverse dependencies (importers).
        """
        file_path = str(Path(file_path)) # Normalize
        if file_path not in self.graph["nodes"]:
            return {"error": "File not found in index."}

        node = self.graph["nodes"][file_path]
        
        # Direct dependencies
        imports = []
        for edge in self.graph["edges"]:
            if edge["source"] == file_path:
                imports.append(edge["target"])

        # Reverse dependencies
        imported_by = []
        for edge in self.graph["edges"]:
            if edge["target"] == file_path:
                imported_by.append(edge["source"])

        return {
            "file": file_path,
            "metadata": node,
            "imports": imports,
            "imported_by": imported_by
        }

    def predict_next(self, file_path: str) -> List[str]:
        """
        Suggest relevant files based on current context.
        Strategy:
        1. Direct imports.
        2. Files in the same directory (siblings).
        3. Test files (heuristic).
        """
        context = self.get_context(file_path)
        if "error" in context:
            return []

        suggestions = set()
        
        # 1. Imports
        suggestions.update(context["imports"])
        
        # 2. Siblings (files in same dir)
        parent_dir = str(Path(file_path).parent)
        for node_path in self.graph["nodes"]:
            if str(Path(node_path).parent) == parent_dir and node_path != file_path:
                suggestions.add(node_path)
        
        # 3. Tests (heuristic)
        base_name = Path(file_path).stem
        for node_path in self.graph["nodes"]:
            if f"test_{base_name}" in node_path or f"{base_name}_test" in node_path:
                suggestions.add(node_path)

        return list(suggestions)[:10] # Limit to 10
