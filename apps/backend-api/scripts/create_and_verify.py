import sys

import requests

BASE_URL = "http://localhost:3001/api/v1"


def create_project():
    url = f"{BASE_URL}/projects"
    import uuid
    from datetime import datetime

    project_id = f"P-{str(uuid.uuid4())}"
    payload = {
        "id": project_id,
        "name": "Integration Test Project",
        "title": "Integration Test Project",
        "mission": "To verify the system",
        "start_date": datetime.now().date().isoformat(),
        "description": "Created by verification script",
        "owner": "unassigned",
        "status": "active",
        "priority": "normal",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "created_utc": datetime.now().isoformat(),
        "updated_utc": datetime.now().isoformat(),
    }
    print(f"Creating Project: {url}")
    print(f"Payload: {payload}")
    try:
        response = requests.post(url, json=payload)
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"Project Created: {data['id']}")
            return data["id"]
        else:
            print(f"Error creating project: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Exception creating project: {e}")
        return None


def create_task(project_id):
    url = f"{BASE_URL}/tasks"
    payload = {
        "title": "Integration Test Task",
        "summary": "Task linked to new project",
        "description": "Verifying full flow",
        "owner": "unassigned",
        "status": "new",
        "priority": "p2",
        "primary_project": project_id,
        "assignees": ["unassigned"],
        "estimate_points": 5,
    }
    print(f"Creating Task linked to {project_id}: {url}")
    try:
        response = requests.post(url, json=payload)
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"Task Created: {data['id']}")
            return True
        else:
            print(f"Error creating task: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Exception creating task: {e}")
        return False


if __name__ == "__main__":
    print("--- Starting Integration Verification ---")
    project_id = create_project()
    if project_id:
        success = create_task(project_id)
        if success:
            print("--- Verification SUCCESS ---")
        else:
            print("--- Verification FAILED at Task Creation ---")
            sys.exit(1)
    else:
        print("--- Verification FAILED at Project Creation ---")
        sys.exit(1)
