import requests

# Define base URL
API_URL = "http://localhost:8000/api/v1"

def seed():
    print("🌱 Seeding Database...")
    
    # 1. Create Admin User (if not exists)
    user_data = {
        "email": "admin@hypercode.ai",
        "password": "adminpassword",
        "full_name": "Admin User",
        "role": "admin"
    }
    
    # Try to register (might fail if exists, which is fine)
    try:
        print("Creating User...")
        res = requests.post(f"{API_URL}/users/", json=user_data, timeout=10)
        if res.status_code == 200:
            print("✅ User created.")
        elif res.status_code == 400:
            print("ℹ️ User already exists.")
        else:
            print(f"❌ User creation failed: {res.text}")
            return
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    # 2. Login to get Token
    print("Logging in...")
    login_data = {
        "username": "admin@hypercode.ai",
        "password": "adminpassword"
    }
    res = requests.post(f"{API_URL}/auth/login/access-token", data=login_data, timeout=10)
    if res.status_code != 200:
        print(f"❌ Login failed: {res.text}")
        return
    
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Token received: {token[:10]}...")

    # 3. Create Project
    project_data = {
        "name": "BROski Project",
        "description": "The main mission.",
        "status": "active"
    }
    
    # Check if projects exist
    res = requests.get(f"{API_URL}/projects/", headers=headers, timeout=10)
    if res.status_code != 200:
        print(f"❌ Could not fetch projects: {res.status_code} - {res.text}")
        return

    projects = res.json()

    if not projects:
        print("Creating Project...")
        res = requests.post(f"{API_URL}/projects/", json=project_data, headers=headers, timeout=10)
        if res.status_code == 200:
            project_id = res.json()["id"]
            print(f"✅ Project created: ID {project_id}")
        else:
            print(f"❌ Project creation failed: {res.status_code} - {res.text}")
            return
    else:
        project_id = projects[0].get("id")
        if not project_id:
            print("❌ Project list returned but first project has no id.")
            return
        print(f"ℹ️ Project exists: ID {project_id}")

    print("\n🎉 Seeding Complete!")
    print(f"export JWT_TOKEN={token}")
    print(f"export PROJECT_ID={project_id}")
    
    # Write token to a file for easy access by other scripts/user
    with open("token.txt", "w") as f:
        f.write(token)
    with open("project_id.txt", "w") as f:
        f.write(str(project_id))

if __name__ == "__main__":
    seed()
