import os
import re

ROOT_DIR = r"src\taskman_api"

REPLACEMENTS = [
    (r"from db(\.| )", r"from taskman_api.db\1"),
    (r"from schemas(\.| )", r"from taskman_api.schemas\1"),
    (r"from models(\.| )", r"from taskman_api.models\1"),
    (r"from routers(\.| )", r"from taskman_api.routers\1"),
    (r"from repositories(\.| )", r"from taskman_api.repositories\1"),
    (r"from core(\.| )", r"from taskman_api.core\1"),
    (r"from middleware(\.| )", r"from taskman_api.middleware\1"),
    (r"import db(\.| )", r"import taskman_api.db\1"),
    (r"import schemas(\.| )", r"import taskman_api.schemas\1"),
    (r"import models(\.| )", r"import taskman_api.models\1"),
    (r"import routers(\.| )", r"import taskman_api.routers\1"),
    (r"import repositories(\.| )", r"import taskman_api.repositories\1"),
    (r"import core(\.| )", r"import taskman_api.core\1"),
    (r"import middleware(\.| )", r"import taskman_api.middleware\1"),
    (r"taskman_api\.db\.models", r"taskman_api.models"),
    (r"taskman_api\.db\.repositories", r"taskman_api.repositories"),
]

def fix_imports():
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                new_content = content
                for pattern, replacement in REPLACEMENTS:
                    new_content = re.sub(pattern, replacement, new_content)
                
                if new_content != content:
                    print(f"Fixing imports in {file_path}")
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)

if __name__ == "__main__":
    fix_imports()
