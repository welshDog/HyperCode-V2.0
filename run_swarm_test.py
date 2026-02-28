import requests
import json
import os

API_URL = "http://localhost:8000/api/v1"

def run_test():
    # 1. Read Token
    try:
        with open("token.txt", "r") as f:
            token = f.read().strip()
    except FileNotFoundError:
        print("❌ token.txt not found. Run seed_data.py first.")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 2. Prepare Task Payload
    task_payload = {
        "title": "Agent Research Test 01",
        "description": "Research the latest advancements in Quantum Machine Learning algorithms.",
        "project_id": 1,
        "status": "todo",
        "priority": "high",
        "type": "research" # This triggers the ResearchAgent
    }

    print(f"🚀 Firing Payload into HyperCode Core: {task_payload['title']}...")
    try:
        res = requests.post(f"{API_URL}/tasks/", json=task_payload, headers=headers)
        if res.status_code == 200:
            task = res.json()
            print(f"✅ Task Created Successfully! ID: {task['id']}")
            print(f"Title: {task['title']}")
            print("Check logs now: docker logs -f celery-worker")
        else:
            print(f"❌ Failed: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    run_test()
