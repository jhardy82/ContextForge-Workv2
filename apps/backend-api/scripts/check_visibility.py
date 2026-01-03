import os
import subprocess
import sys
import time


def log_to_file(filename, content):
    abs_path = os.path.abspath(filename)
    print(f"Logging to: {abs_path}")
    with open(abs_path, "a", encoding="utf-8") as f:
        f.write(f"--- {time.ctime()} ---\n")
        f.write(content + "\n")
        f.flush()
        os.fsync(f.fileno())

def run_test():
    report = []
    report.append(f"CWD: {os.getcwd()}")
    report.append(f"Python Executable: {sys.executable}")
    report.append(f"Python Version: {sys.version}")

    # Test 1: Simple stdout
    print("Testing internal print...")
    sys.stdout.write("INTERNAL_PRINT_WORKS\n")
    sys.stdout.flush()

    # Test 2: Subprocess output
    try:
        print("Testing subprocess whoami...")
        res = subprocess.run(["whoami"], capture_output=True, text=True, shell=True)
        report.append(f"Whoami Output: {res.stdout.strip()}")
        report.append(f"Whoami Error: {res.stderr.strip()}")
    except Exception as e:
        report.append(f"Subprocess Error: {e}")

    # Test 3: Environment variables
    report.append(f"TERM: {os.environ.get('TERM', 'N/A')}")
    report.append(f"PAGER: {os.environ.get('PAGER', 'N/A')}")
    report.append(f"PROMPT: {os.environ.get('PROMPT', 'N/A')}")

    # Write report to file
    final_report = "\n".join(report)
    log_to_file("terminal_visibility_report.txt", final_report)
    print("Report written to terminal_visibility_report.txt")

if __name__ == "__main__":
    run_test()
