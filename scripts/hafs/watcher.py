
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from .indexer import Indexer
from .utils import get_logger

logger = get_logger("HAFS.Watcher")

class HafsEventHandler(FileSystemEventHandler):
    def __init__(self, indexer):
        self.indexer = indexer

    def on_modified(self, event):
        if not event.is_directory:
            self.indexer.update_file(Path(event.src_path))

    def on_created(self, event):
        if not event.is_directory:
            self.indexer.update_file(Path(event.src_path))

    def on_moved(self, event):
        # For moved files, we should ideally remove the old entry too.
        # But a full re-scan is expensive. Let's just index the new location for now.
        if not event.is_directory:
            self.indexer.update_file(Path(event.dest_path))

def start_watching(path: str = "."):
    root_path = Path(path).resolve()
    indexer = Indexer(root_path)
    
    # Initial Scan
    logger.info("Performing initial scan...")
    indexer.scan()
    
    event_handler = HafsEventHandler(indexer)
    observer = Observer()
    observer.schedule(event_handler, str(root_path), recursive=True)
    observer.start()
    
    logger.info(f"HAFS Watcher active on: {root_path}")
    logger.info("Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("Stopping HAFS Watcher...")
    
    observer.join()

if __name__ == "__main__":
    start_watching()
