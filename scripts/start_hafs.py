
import sys
import os
from pathlib import Path

# Add project root to python path to resolve 'scripts' package
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

try:
    from scripts.hafs.watcher import start_watching
except ImportError as e:
    print(f"Error importing HAFS: {e}")
    sys.exit(1)

if __name__ == "__main__":
    print(f"Starting HAFS from: {ROOT_DIR}")
    start_watching(str(ROOT_DIR))
