
import re
import os
from pathlib import Path
from typing import List, Set, Optional

from .config import ROOT_DIR

# Regex Patterns
PY_IMPORT_RE = re.compile(r"^\s*(?:from|import)\s+([\w\.]+)")
TS_IMPORT_RE = re.compile(r"^\s*import\s+.*from\s+['\"]([^'\"]+)['\"]")
JS_REQUIRE_RE = re.compile(r"require\(['\"]([^'\"]+)['\"]\)")

def extract_dependencies(file_path: Path) -> List[str]:
    """Extract imported modules/files from a source file."""
    deps = set()
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        suffix = file_path.suffix.lower()

        if suffix == ".py":
            raw_imports = _extract_py_imports(content)
            deps.update(_resolve_py_imports(raw_imports, file_path))
        elif suffix in {".ts", ".tsx", ".js", ".jsx"}:
            raw_imports = _extract_js_imports(content)
            deps.update(_resolve_js_imports(raw_imports, file_path))
        
    except Exception as e:
        # Silently fail on read errors for robustness
        pass
        
    return list(deps)

def _extract_py_imports(content: str) -> Set[str]:
    imports = set()
    for line in content.splitlines():
        match = PY_IMPORT_RE.match(line)
        if match:
            # Capture the full import path (e.g., "agents.crew.main")
            module = match.group(1)
            if module:
                imports.add(module)
    return imports

def _resolve_py_imports(imports: Set[str], source_file: Path) -> Set[str]:
    resolved = set()
    for imp in imports:
        # Handle relative imports (e.g., from .utils import x)
        if imp.startswith('.'):
            # Resolve relative to source file
            # Logic: Count dots to determine parent level
            dots = len(imp) - len(imp.lstrip('.'))
            base_name = imp.lstrip('.')
            
            # Simple resolution: just look for the file in the relative path
            # This is a heuristic; full python resolution is complex.
            
            # Case: .utils -> sibling
            if dots == 1:
                target_dir = source_file.parent
            # Case: ..utils -> parent
            else:
                target_dir = source_file.parents[dots-2] # -1 for 0-index, -1 for parent logic? 
                # . -> current (0 parents), .. -> parent (1 parent)
                # dots=1 -> parents[-1] (invalid), dots=2 -> parents[0]
                if dots > 1:
                     target_dir = source_file.parents[dots-2]
                else:
                    target_dir = source_file.parent

            # Construct potential path
            if base_name:
                potential_py = target_dir / f"{base_name}.py"
                potential_pkg = target_dir / base_name / "__init__.py"
                
                if potential_py.exists():
                    try:
                        resolved.add(str(potential_py.relative_to(ROOT_DIR)))
                    except ValueError: pass
                elif potential_pkg.exists():
                    try:
                        resolved.add(str((target_dir / base_name).relative_to(ROOT_DIR)))
                    except ValueError: pass
            
        else:
            # Absolute import (e.g. "agents.crew")
            # Convert dots to slashes
            parts = imp.split('.')
            path_parts = ROOT_DIR.joinpath(*parts)
            
            potential_py = path_parts.with_suffix(".py")
            potential_pkg = path_parts / "__init__.py"
            
            if potential_py.exists():
                 try:
                    resolved.add(str(potential_py.relative_to(ROOT_DIR)))
                 except ValueError: pass
            elif potential_pkg.exists():
                 try:
                    resolved.add(str(path_parts.relative_to(ROOT_DIR)))
                 except ValueError: pass
            else:
                # Might be a top-level module in a subdir (e.g. 'scripts' -> 'scripts/')
                if path_parts.is_dir():
                     try:
                        resolved.add(str(path_parts.relative_to(ROOT_DIR)))
                     except ValueError: pass

    return resolved

def _extract_js_imports(content: str) -> Set[str]:
    imports = set()
    for line in content.splitlines():
        # ES6 Imports
        match_ts = TS_IMPORT_RE.match(line)
        if match_ts:
            imports.add(match_ts.group(1))
            continue
            
        # CommonJS Require
        match_js = JS_REQUIRE_RE.search(line)
        if match_js:
            imports.add(match_js.group(1))
            
    return imports

def _resolve_js_imports(imports: Set[str], source_file: Path) -> Set[str]:
    resolved = set()
    for imp in imports:
        if imp.startswith('.'):
            # Relative import
            target_path = (source_file.parent / imp).resolve()
            
            # Try extensions
            for ext in ['.ts', '.tsx', '.js', '.jsx', '.json']:
                potential = target_path.with_suffix(ext)
                if potential.exists():
                    try:
                        resolved.add(str(potential.relative_to(ROOT_DIR)))
                        break
                    except ValueError: pass
            
            # Try index files
            if target_path.is_dir():
                for ext in ['.ts', '.tsx', '.js', '.jsx']:
                     potential = target_path / f"index{ext}"
                     if potential.exists():
                        try:
                            resolved.add(str(potential.relative_to(ROOT_DIR)))
                            break
                        except ValueError: pass
        elif imp.startswith('@/'):
            # Alias import (often mapped to src/ or app/)
            # This requires reading tsconfig, but we'll use a heuristic for 'app/'
            # Assuming @ maps to project root or specific src dir
             pass # Skip complex alias resolution for now to avoid errors

    return resolved
