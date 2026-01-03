from alembic.config import Config
from alembic.script import ScriptDirectory

# Load the config
alembic_cfg = Config("alembic.ini")
script = ScriptDirectory.from_config(alembic_cfg)

import os

out_path = r"C:\Users\James\Documents\Github\GHrepos\SCCMScripts\TaskMan-v2\backend-api\debug_alembic_internal.txt"
print(f"Writing to {out_path}...")

try:
    with open(out_path, "w", encoding="utf-8") as out:
        out.write(f"CWD: {os.getcwd()}\n")
        out.write("--- Revision Map Keys (All Revision HashIDs) ---\n")
        try:
            for rev in script.get_revisions("base", "head"):
                 out.write(f"Rev: {rev.revision} | Down: {rev.down_revision} | File: {rev.path}\n")
        except Exception as e:
            out.write(f"Error getting revisions: {e}\n")
            import traceback
            out.write(traceback.format_exc())

        out.write("\n--- Inspecting filesystem directly via ScriptDirectory ---\n")
        for file in script._list_py_files(script.versions):
            out.write(f"Found file: {file}\n")
except Exception as e:
    print(f"CRITICAL FAULURE: {e}")
    import traceback
    traceback.print_exc()
