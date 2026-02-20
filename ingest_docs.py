import sys
import os
import asyncio
from typing import List, Dict, Any

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from agents.nexus.weaver.agent import WeaverAgent

async def main():
    weaver = WeaverAgent()
    docs_dir = "./docs"
    contexts = []
    
    print(f"Scanning {docs_dir} for documentation...")
    
    count = 0
    max_docs = 20 # Limit for prototype testing to avoid huge ingestion time
    
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    contexts.append({
                        "type": "documentation",
                        "content": f"File: {file}\nPath: {file_path}\n\n{content}",
                        "file_path": file_path
                    })
                    count += 1
                    if count >= max_docs:
                        break
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
        if count >= max_docs:
            break
                    
    print(f"Found {len(contexts)} documents (limited to {max_docs} for testing).")
    
    # Process in chunks to verify batching and rate limiting
    chunk_size = 5
    for i in range(0, len(contexts), chunk_size):
        batch = contexts[i:i+chunk_size]
        print(f"Ingesting batch {i//chunk_size + 1} ({len(batch)} items)...")
        results = await weaver.ingest_batch(batch, rate_limit_delay=0.2)
        
        # Verify results
        success_count = sum(1 for r in results if r.get("status") == "success")
        print(f"Batch {i//chunk_size + 1} completed. Success: {success_count}/{len(batch)}")
        
    print("Ingestion complete.")

if __name__ == "__main__":
    asyncio.run(main())
