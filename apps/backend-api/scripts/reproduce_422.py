import json
import urllib.request
import uuid


def reproduce():
    url = "http://localhost:3001/api/v1/tasks"

    # Simulate the payload exactly as DashboardV3 constructs it
    task_id = f"T-{str(uuid.uuid4())}"

    payload = {
        "id": task_id,
        "title": "Success Task 2",
        "summary": "Success Task 2",
        "description": "No description provided",
        "owner": "unassigned",
        "status": "new",
        "priority": "p2",
        "primary_project": "P-20251227220531",
        "primary_sprint": "S-20251227224325",
        "due_at": None,
        "assignees": ["unassigned"],
        "related_projects": [],
        "related_sprints": [],
        "labels": [],
    }

    with open("reproduce_result.txt", "w") as f:
        print(f"Sending POST to {url}", file=f)
        print(f"Payload: {json.dumps(payload, indent=2)}", file=f)

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req) as response:
                print(f"Status Code: {response.getcode()}", file=f)
                print("Response Body:", file=f)
                print(response.read().decode("utf-8"), file=f)
        except urllib.error.HTTPError as e:
            print(f"Status Code: {e.code}", file=f)
            print("Response Body:", file=f)
            print(e.read().decode("utf-8"), file=f)
        except Exception as e:
            print(f"Error: {e}", file=f)


if __name__ == "__main__":
    reproduce()
