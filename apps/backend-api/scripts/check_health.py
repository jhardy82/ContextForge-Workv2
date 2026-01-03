
import sys

import requests

BACKEND_URL = "http://localhost:3001"
FRONTEND_URL = "http://localhost:5174"

def check_url(url, name):
    print(f"Checking {name} at {url}...")
    try:
        response = requests.get(url, timeout=5)
        print(f"{name} status code: {response.status_code}")
        if response.status_code < 400:
            print(f"{name} is HEALTHY.")
            return True
        else:
            print(f"{name} returned error status.")
            return False
    except requests.exceptions.ConnectionError:
        print(f"{name} is UNREACHABLE.")
        return False
    except Exception as e:
        print(f"Error checking {name}: {e}")
        return False

def main():
    backend_ok = check_url(f"{BACKEND_URL}/health", "Backend API") # Assuming /health endpoint
    if not backend_ok:
         # Try root if health doesn't exist
         backend_ok = check_url(BACKEND_URL, "Backend API (Root)")

    frontend_ok = check_url(FRONTEND_URL, "Frontend")

    if backend_ok and frontend_ok:
        print("Both services are UP.")
        sys.exit(0)
    else:
        print("One or more services are DOWN.")
        sys.exit(1)

if __name__ == "__main__":
    main()
