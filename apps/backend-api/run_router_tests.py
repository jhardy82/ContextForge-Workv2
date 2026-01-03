import subprocess
import sys


def run_tests():
    output_file = "test_run_results.txt"
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-v",
        "tests/unit/routers/test_projects.py",
        "tests/unit/routers/test_sprints.py",
    ]

    print(f"Running command: {' '.join(command)}")

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("STDOUT:\n")
            f.write(result.stdout)
            f.write("\n\nSTDERR:\n")
            f.write(result.stderr)

        print(f"Execution complete. Exit code: {result.returncode}")
        print(f"Output written to {output_file}")

    except Exception as e:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"SCRIPT_ERROR: {str(e)}")
        print(f"Script failed: {e}")


if __name__ == "__main__":
    run_tests()
