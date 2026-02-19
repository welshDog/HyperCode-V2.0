import os
import requests
import json
import sys

# Configuration from environment
LLM_API_URL = os.getenv("LLM_API_URL", "http://host.docker.internal:8080/v1/chat/completions")
MODEL_NAME = os.getenv("MODEL_NAME", "hf.co/Qwen/Qwen2.5-Coder-7B-Instruct")
API_KEY = os.getenv("OPENAI_API_KEY", None)

def load_soul():
    """Loads the SOUL.md file to use as the system prompt."""
    try:
        with open("SOUL.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("❌ Error: SOUL.md not found. Please ensure it exists in the same directory.")
        sys.exit(1)

def query_llm(system_prompt, user_input, history=[]):
    """Sends the prompt to the Docker Model Runner API."""
    
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": user_input})

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 2000,
        "stream": False
    }

    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    try:
        response = requests.post(LLM_API_URL, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
        
    except requests.exceptions.ConnectionError:
        return f"❌ Cannot connect to {LLM_API_URL}. Is the model running?"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def main():
    print("🦅 Agent X Initializing HyperCode Syntax Tutor...")
    print(f"🔌 Connecting to: {LLM_API_URL} ({MODEL_NAME})")
    soul = load_soul()
    print("✨ Tutor Ready! (Type 'exit' to quit)")
    print("-" * 50)
    
    history = []
    
    while True:
        try:
            user_input = input("\n👤 You: ")
            if user_input.lower() in ["exit", "quit"]:
                print("👋 HyperTutor: Happy coding! Keep flowing!")
                break
            
            print("🤖 HyperTutor is thinking...", end="\r")
            response = query_llm(soul, user_input, history)
            
            print(" " * 30, end="\r") # Clear "thinking" line
            print(f"🎓 HyperTutor:\n{response}")
            
            # Keep a small history window
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})
            if len(history) > 10: # Keep last 5 exchanges
                history = history[-10:]
                
        except KeyboardInterrupt:
            break
        except EOFError:
            print("\n👋 HyperTutor: Input closed. Exiting.")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
