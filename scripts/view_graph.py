
import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

PORT = 8000
ROOT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT_DIR / "docs" / "design"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT_DIR), **kwargs)

def main():
    os.chdir(ROOT_DIR)
    url = f"http://localhost:{PORT}/docs/design/hafs_graph.html"
    print(f"Serving Hyper AI File System Graph at {url}")
    print("Press Ctrl+C to stop.")
    
    # Open browser automatically
    webbrowser.open(url)
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server.")

if __name__ == "__main__":
    main()
