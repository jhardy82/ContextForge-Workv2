import os
import re

ROOT_DIR = r"tests"

REPLACEMENTS = [
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
