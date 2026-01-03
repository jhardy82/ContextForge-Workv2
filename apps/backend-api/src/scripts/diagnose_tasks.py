import json
import sys
from pathlib import Path
from typing import Any

import yaml

# Add src to python path to allow imports
current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

TRACKERS_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "trackers"

def load_file(file_path: Path) -> dict[str, Any] | list[Any] | None:
    try:
        with open(file_path, encoding="utf-8") as f:
            if file_path.suffix == ".json":
                return json.load(f)
            elif file_path.suffix in (".yaml", ".yml"):
                return yaml.safe_load(f)
    except Exception as e:
        return {"error": str(e)}
    return {}

def extract_id_from_filename(file_path: Path, prefix: str) -> str | None:
    stem = file_path.stem
    parts = stem.split(".")
    if len(parts) > 1:
        for part in parts:
            if part.startswith(prefix) or (prefix == "S-" and part.startswith("S-")):
                return part
        return parts[-1]
    return stem

def main():
    print(f"Diagnosing Tasks in: {TRACKERS_DIR / 'tasks'}")
    tasks_dir = TRACKERS_DIR / "tasks"

    if not tasks_dir.exists():
        print("Tasks directory not found")
        return

    results = []

    print(f"{'Filename':<50} | {'Status':<10} | {'Reason'}")
    print("-" * 100)

    for file_path in tasks_dir.iterdir():
        if not file_path.is_file() or file_path.suffix not in (".json", ".yaml", ".yml"):
            continue

        filename = file_path.name
        raw_data = load_file(file_path)

        if isinstance(raw_data, dict) and "error" in raw_data:
            print(f"{filename:<50} | ERROR      | Parse Error: {raw_data['error']}")
            continue

        if not isinstance(raw_data, dict):
            print(f"{filename:<50} | SKIPPED    | Not a dict")
            continue

        data = raw_data.get("task", raw_data)
        if not isinstance(data, dict):
             print(f"{filename:<50} | SKIPPED    | 'task' key not a dict")
             continue

        task_id = data.get("id")
        id_source = "data"

        if not task_id:
            task_id = extract_id_from_filename(file_path, "T-")
            id_source = "filename"

        if not task_id:
            print(f"{filename:<50} | SKIPPED    | No ID found in data or filename")
            continue

        print(f"{filename:<50} | OK         | ID: {task_id} (Source: {id_source})")

if __name__ == "__main__":
    main()
