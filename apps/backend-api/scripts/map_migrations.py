import re
from pathlib import Path

versions_dir = Path("alembic/versions")
revision_map = {}

with open("migration_map_internal.txt", "w", encoding="utf-8") as out:
    out.write(f"{'File':<60} | {'Revision':<15} | {'Down Revision':<15}\n")
    out.write("-" * 95 + "\n")

    for f in versions_dir.glob("*.py"):
        content = f.read_text(encoding="utf-8")
        rev_match = re.search(r"revision\s*=\s*['\"]([^'\"]+)['\"]", content)
        down_match = re.search(r"down_revision\s*=\s*['\"]([^'\"]+)['\"]", content)

        rev = rev_match.group(1) if rev_match else "None"
        down = down_match.group(1) if down_match else "None"

        revision_map[rev] = {'file': f.name, 'down': down}
        out.write(f"{f.name:<60} | {rev:<15} | {down:<15}\n")

    out.write("\n--- Chain Analysis ---\n")

    all_revs = set(revision_map.keys())
    all_downs = set(r['down'] for r in revision_map.values() if r['down'] != "None")

    heads = all_revs - all_downs
    roots = [r for r, data in revision_map.items() if data['down'] == "None"]

    out.write(f"Heads: {heads}\n")
    out.write(f"Roots: {roots}\n")

    # Check for broken links
    for rev, data in revision_map.items():
        down = data['down']
        if down != "None" and down not in all_revs:
            out.write(f"BROKEN LINK: {rev} ({data['file']}) -> {down} (Missing)\n")
