import requests
import json
import time

def test_ai_endpoint():
    url = "http://localhost:8000/api/v1/ai/generate"  # Note: 8000 is exposed port for hypercode-core in docker-compose
    
    payload = {
        "task_description": "Create a Python function that reverses a string",
        "user_requirements": "Use slicing, include docstring and type hints"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success! Response:")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print("❌ Failed. Response:")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

if __name__ == "__main__":
    test_ai_endpoint()
