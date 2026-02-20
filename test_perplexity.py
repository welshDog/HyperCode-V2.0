"""
Test Perplexity API connectivity
"""
import os
import sys
from openai import OpenAI

# Perplexity uses OpenAI-compatible API
# client initialization moved inside test function to pick up env var changes

def test_perplexity():
    print("\n[TEST] Perplexity API Connectivity...")
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key or api_key.startswith("pplx-dummy"):
        print("⚠️  Skipping: PERPLEXITY_API_KEY is missing or dummy.")
        return

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.perplexity.ai"
    )

    try:
        response = client.chat.completions.create(
            model="sonar",  # Fast model
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": "Write a Python function that adds two numbers."}
            ],
            max_tokens=200
        )
        
        print("✅ Perplexity Connection: SUCCESS")
        print(f"Model: {response.model}")
        print(f"Tokens Used: {response.usage.total_tokens}")
        print(f"Estimated Cost: ${response.usage.total_tokens / 1_000_000 * 0.20:.6f}")
        print(f"\nResponse:\n{response.choices[0].message.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Perplexity Connection: FAILED")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("🤖 HyperCode Perplexity Connectivity Test")
    print("=========================================")
    
    # Check for key in args or env
    if len(sys.argv) > 1:
        os.environ["PERPLEXITY_API_KEY"] = sys.argv[1]
        
    test_perplexity()
