import json
import urllib.request


def list_projects_api():
    url = "http://localhost:3001/api/v1/projects"
    print(f"Fetching from {url}")

    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode("utf-8"))
            projects = data.get("projects", [])

            with open("projects_list.txt", "w") as f:
                print("Existing Projects:", file=f)
                if not projects:
                    print("No projects found in API response.", file=f)
                for p in projects:
                    print(f"ID: {p.get('id')}, Name: {p.get('name')}", file=f)

            print(f"Found {len(projects)} projects.")

    except urllib.error.HTTPError as e:
        with open("projects_list.txt", "w") as f:
            print(f"Error fetching projects: {e}", file=f)
            print(f"Body: {e.read().decode('utf-8')}", file=f)
    except Exception as e:
        with open("projects_list.txt", "w") as f:
            print(f"Error fetching projects: {e}", file=f)


if __name__ == "__main__":
    list_projects_api()
