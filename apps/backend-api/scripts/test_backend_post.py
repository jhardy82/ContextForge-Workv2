import requests

URL = "http://localhost:3001/api/v1/tasks"
HEADERS = {"Content-Type": "application/json"}
PAYLOAD = {
    "title": "Direct Backend Test Task",
    "status": "todo",
    "priority": "medium",
    "description": "Created via python script to test 405 error",
    "primary_project": "proj_default",
    "primary_sprint": "sprint_default",
}


def test_create_task():
    with open("post_test_result.txt", "w") as f:
        f.write(f"POSTing to {URL}...\n")
        try:
            response = requests.post(URL, json=PAYLOAD, headers=HEADERS)
            f.write(f"Status Code: {response.status_code}\n")
            f.write(f"Response: {response.text}\n")

            if response.status_code == 201:
                f.write("SUCCESS: Task created.\n")
            elif response.status_code == 405:
                f.write("FAILURE: 405 Method Not Allowed.\n")
            else:
                f.write(f"FAILURE: Unexpected status block {response.status_code}\n")

        except Exception as e:
            f.write(f"Exception: {e}\n")


if __name__ == "__main__":
    test_create_task()
