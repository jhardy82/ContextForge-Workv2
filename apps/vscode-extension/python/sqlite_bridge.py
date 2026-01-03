import json
import os
import sqlite3
import sys


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def load_data(db_path):
    if not os.path.exists(db_path):
        return {"error": f"Database file not found: {db_path}"}

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        # Load Projects
        cursor.execute("SELECT * FROM projects")
        projects = cursor.fetchall()

        # Load Sprints
        cursor.execute("SELECT * FROM sprints")
        sprints = cursor.fetchall()

        # Load Tasks
        cursor.execute("SELECT * FROM tasks")
        tasks_raw = cursor.fetchall()

        tasks = []
        for t in tasks_raw:
            # Map schema fields to interface fields
            task = {
                "id": t.get("id"),
                "title": t.get("title"),
                "description": t.get("summary"),
                "status": t.get("status"),
                "priority": t.get("priority"),
                "project_id": t.get("project_id"),
                "sprint_id": t.get("sprint_id"),
                "owner": t.get("owner"),
                "created_at": t.get("created_at"),
                "updated_at": t.get("updated_at"),
                # Map other fields if necessary
            }
            tasks.append(task)

        conn.close()

        return {"projects": projects, "sprints": sprints, "tasks": tasks}

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Database path required"}))
        sys.exit(1)

    db_path = sys.argv[1]
    result = load_data(db_path)
    print(json.dumps(result))
