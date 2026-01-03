import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-u", "-m", "pytest", "-c", "pytest_full.ini", "--tb=no", "-q"],
    capture_output=True,
    text=True,
    cwd=r"c:\Users\James\Documents\Github\GHrepos\SCCMScripts\TaskMan-v2\backend-api"
)

print("=== STDOUT ===")
print(result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout)
print("\n=== STDERR ===")
print(result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr)
print(f"\n=== EXIT CODE: {result.returncode} ===")
