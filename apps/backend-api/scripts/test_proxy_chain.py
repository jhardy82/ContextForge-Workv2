
import uuid

import requests


# Valid Payload based on 422 error feedback
def get_payload():
    return {
        "id": str(uuid.uuid4()),
        "title": "Proxy Test Task",
        "summary": "Testing Proxy Chain",
        "status": "new",  # Valid enum
        "priority": "p2", # Valid enum
        "description": "Created via python script to test Proxy",
        "owner": "user_123", # Required
        "assignees": [],
        "labels": [],
        "primary_project": "proj_default",
        "primary_sprint": "sprint_default"
    }

HEADERS = {"Content-Type": "application/json"}

def test_chain():
    print("--- Test 1: Direct Backend (3001) ---")
    be_url = "http://localhost:3001/api/v1/tasks"
    try:
        payload = get_payload()
        print(f"POST {be_url}")
        resp = requests.post(be_url, json=payload, headers=HEADERS)
        print(f"Status: {resp.status_code}")
        print(f"Body: {resp.text[:200]}...") # Truncate
        if resp.status_code == 201:
            print("SUCCESS: Backend accepted request.")
        else:
            print(f"FAILURE: Backend rejected request. {resp.status_code}")
    except Exception as e:
        print(f"EXCEPTION: {e}")

    print("\n--- Test 2: Frontend Proxy (5174) ---")
    fe_url = "http://localhost:5174/api/v1/tasks"
    try:
        payload = get_payload()
        print(f"POST {fe_url}")
        resp = requests.post(fe_url, json=payload, headers=HEADERS)
        print(f"Status: {resp.status_code}")
        print(f"Body: {resp.text[:200]}...") # Truncate
        if resp.status_code == 201:
            print("SUCCESS: Proxy forwarded request correctly.")
        elif resp.status_code == 405:
            print("FAILURE: Proxy returned 405 Method Not Allowed.")
            print(f"Headers: {resp.headers}")
        else:
             print(f"FAILURE: Proxy returned {resp.status_code}")
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    test_chain()
