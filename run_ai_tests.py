import requests
import json
import os
import time

BASE_URL = "http://localhost:8000/api/v1/ai"

def run_tests():
    print("🧪 Running AI Test Battery...\n")
    
    # Create directories
    os.makedirs("test_results/basic", exist_ok=True)
    os.makedirs("test_results/complex", exist_ok=True)
    os.makedirs("test_results/revision", exist_ok=True)

    # Test 1: Fibonacci
    print("Test 1: Fibonacci...")
    payload1 = {
        "task_description": "Create a function that calculates fibonacci numbers using memoization"
    }
    try:
        r1 = requests.post(f"{BASE_URL}/generate", json=payload1)
        if r1.status_code == 200:
            data = r1.json()
            result = {
                "success": data.get("success"),
                "quality": data.get("quality_score"),
                "iterations": data.get("iterations")
            }
            with open("test_results/basic/fibonacci.json", "w") as f:
                json.dump(result, f, indent=2)
            print(json.dumps(result, indent=2))
        else:
            print(f"Failed: {r1.status_code} - {r1.text}")
    except Exception as e:
        print(f"Error: {e}")
    print("")

    # Test 2: BST
    print("Test 2: Binary Search Tree...")
    payload2 = {
        "task_description": "Implement a binary search tree class with insert, search, and delete methods"
    }
    try:
        r2 = requests.post(f"{BASE_URL}/generate", json=payload2)
        if r2.status_code == 200:
            data = r2.json()
            result = {
                "success": data.get("success"),
                "quality": data.get("quality_score"),
                "iterations": data.get("iterations")
            }
            with open("test_results/basic/bst.json", "w") as f:
                json.dump(result, f, indent=2)
            print(json.dumps(result, indent=2))
        else:
            print(f"Failed: {r2.status_code} - {r2.text}")
    except Exception as e:
        print(f"Error: {e}")
    print("")

    # Test 3: FastAPI Auth
    print("Test 3: FastAPI Authentication...")
    payload3 = {
        "task_description": "Create a FastAPI authentication system with JWT tokens",
        "user_requirements": "Include user registration, login, token refresh, and password hashing with bcrypt"
    }
    try:
        r3 = requests.post(f"{BASE_URL}/generate", json=payload3)
        if r3.status_code == 200:
            data = r3.json()
            result = {
                "success": data.get("success"),
                "quality": data.get("quality_score"),
                "iterations": data.get("iterations"),
                "code_length": len(data.get("code", ""))
            }
            with open("test_results/complex/jwt_auth.json", "w") as f:
                json.dump(result, f, indent=2)
            print(json.dumps(result, indent=2))
        else:
            print(f"Failed: {r3.status_code} - {r3.text}")
    except Exception as e:
        print(f"Error: {e}")
    print("")

    # Test 4: Calculator
    print("Test 4: Revision Loop Test...")
    payload4 = {
        "task_description": "Make a calculator",
        # Note: 'max_iterations' isn't in our pydantic model yet, but we can send it
        # It won't do anything unless we update the model, but let's follow the script
    }
    try:
        r4 = requests.post(f"{BASE_URL}/generate", json=payload4)
        if r4.status_code == 200:
            data = r4.json()
            result = {
                "success": data.get("success"),
                "quality": data.get("quality_score"),
                "iterations": data.get("iterations")
            }
            with open("test_results/revision/calculator.json", "w") as f:
                json.dump(result, f, indent=2)
            print(json.dumps(result, indent=2))
        else:
            print(f"Failed: {r4.status_code} - {r4.text}")
    except Exception as e:
        print(f"Error: {e}")
    print("")

    # Budget Status
    print("💰 Budget Status:")
    try:
        r5 = requests.get(f"{BASE_URL}/budget/status")
        if r5.status_code == 200:
            print(json.dumps(r5.json(), indent=2))
        else:
            print(f"Failed: {r5.status_code} - {r5.text}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n✅ Test Battery Complete!")

if __name__ == "__main__":
    run_tests()
