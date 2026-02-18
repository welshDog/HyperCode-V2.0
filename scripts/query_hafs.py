
import sys
import json
import argparse
from pathlib import Path

# Add project root to python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

try:
    from scripts.hafs.walker import ContextWalker
    from scripts.hafs.embeddings import EmbeddingEngine
except ImportError as e:
    print(f"Error importing HAFS: {e}")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Query Hyper AI File System Context")
    parser.add_argument("query", help="File path or semantic query")
    parser.add_argument("--semantic", "-s", action="store_true", help="Perform semantic search")
    args = parser.parse_args()
    
    if args.semantic:
        print(f"--- Semantic Search for: '{args.query}' ---")
        engine = EmbeddingEngine()
        results = engine.search(args.query)
        for r in results:
            print(f"\n[Score: {r['distance']:.4f}] {r['id']}")
            print(f"Snippet: {r['snippet']}")
    else:
        walker = ContextWalker()
        
        # Try to resolve path relative to root
        target_path = Path(args.query)
        
        print(f"--- Querying Context for: {args.query} ---")
        context = walker.get_context(args.query)
        
        if "error" in context:
            print(f"Error: {context['error']}")
        else:
            print(json.dumps(context, indent=2))
            
        print("\n--- Predictive Suggestions ---")
        suggestions = walker.predict_next(args.query)
        for s in suggestions:
            print(f"- {s}")

if __name__ == "__main__":
    main()
