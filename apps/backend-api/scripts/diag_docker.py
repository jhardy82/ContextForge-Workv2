import subprocess


def run_cmd(cmd):
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print("--- STDOUT ---")
        print(result.stdout)
        print("--- STDERR ---")
        print(result.stderr)
        return result.stdout
    except Exception as e:
        print(f"Error: {e}")
        return ""

if __name__ == "__main__":
    print("--- DOCKER INFO ---")
    run_cmd(["docker", "ps", "--filter", "name=taskman-postgres"])
    print("\n--- DOCKER PORT ---")
    run_cmd(["docker", "port", "taskman-postgres"])
    print("\n--- DOCKER INSPECT (PortBindings) ---")
    # Using python to filter inspect output if possible, or just dump it
    run_cmd(["docker", "inspect", "--format", "{{range .NetworkSettings.Ports}}{{.}}{{end}}", "taskman-postgres"])
