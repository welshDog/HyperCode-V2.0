import os
import sys
import requests
from openai import OpenAI
import time

def test_openai_connectivity():
    print("\n[TEST] OpenAI Connectivity (Tier 2/3)...")
    api_key = os.getenv("OPENAI_API_KEY", "sk-dummy")
    
    if api_key == "sk-dummy" or not api_key:
        print("⚠️  Skipping OpenAI test: OPENAI_API_KEY is not set or is 'sk-dummy'")
        return

    client = OpenAI(api_key=api_key)
    try:
        start = time.time()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Ping"}],
            max_tokens=5
        )
        latency = (time.time() - start) * 1000
        print(f"✅ OpenAI Success! Latency: {latency:.0f}ms")
        print(f"   Response: {response.choices[0].message.content}")
        print(f"   Cost: ${response.usage.total_tokens / 1_000_000 * 0.60:.6f}")
    except Exception as e:
        print(f"❌ OpenAI Failed: {str(e)}")

def test_ollama_connectivity():
    print("\n[TEST] Ollama Connectivity (Tier 1)...")
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "codellama:7b",
        "prompt": "def hello():",
        "stream": False
    }
    
    try:
        # First check if model exists
        tags_res = requests.get("http://localhost:11434/api/tags")
        if tags_res.status_code == 200:
            models = [m['name'] for m in tags_res.json().get('models', [])]
            print(f"ℹ️  Available Models: {models}")
            if "codellama:7b" not in models:
                 print("⚠️  'codellama:7b' not found. Checking for any available model...")
                 if models:
                     payload["model"] = models[0]
                     print(f"   Using '{models[0]}' instead.")
                 else:
                     print("❌ No models found in Ollama. Run 'docker exec hypercode-ollama ollama pull codellama:7b'")
                     return

        start = time.time()
        response = requests.post(url, json=payload, timeout=30)
        latency = (time.time() - start) * 1000
        
        if response.status_code == 200:
            print(f"✅ Ollama Success! Latency: {latency:.0f}ms")
            print(f"   Response Preview: {response.json().get('response', '')[:50]}...")
        else:
            print(f"❌ Ollama Failed: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Ollama Failed: Connection refused. Is the container running?")
    except Exception as e:
        print(f"❌ Ollama Error: {str(e)}")

if __name__ == "__main__":
    print("🤖 HyperCode AI Connectivity Test")
    print("=================================")
    test_openai_connectivity()
    test_ollama_connectivity()
