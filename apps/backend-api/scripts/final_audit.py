import json
import os
import socket
import subprocess


def run_command(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return "", str(e)


def check_port(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((host, port))
        return True
    except:
        return False
    finally:
        s.close()


def diag():
    log_path = os.path.abspath("final_audit_log_absolute.txt")
    print(f"Writing log to: {log_path}")
    with open(log_path, "w", encoding="utf-8") as diag_log:

        def log(msg):
            print(msg)
            diag_log.write(msg + "\n")
            diag_log.flush()

        log(f"--- INFRASTRUCTURE DIAGNOSTIC (CWD: {os.getcwd()}) ---")

        # 1. Docker Mapping
        log("\n[1] Docker Mapping (Inspection):")
        stdout, stderr = run_command("docker inspect taskman-postgres")
        if stdout:
            try:
                data = json.loads(stdout)
                ports = data[0].get("NetworkSettings", {}).get("Ports", {})
                log(json.dumps(ports, indent=2))
            except:
                log("Failed to parse docker inspect output.")
                log(f"Raw Stdout: {stdout[:500]}")
        else:
            log(f"Error inspecting container: {stderr}")

        # 2. Host Port Binding Status
        log("\n[2] Host Port Binding (Netstat):")
        # Run netstat and capture all lines, then filter in python to be safer
        stdout, stderr = run_command("netstat -ano")
        found = False
        if stdout:
            for line in stdout.splitlines():
                if ":5434" in line:
                    log(line)
                    found = True
        if not found:
            log("No process found listening on 5434 in netstat output.")

        # 3. Connectivity Tests
        log("\n[3] Connectivity Tests:")
        for host in ["127.0.0.1", "localhost"]:
            res = "SUCCESS" if check_port(host, 5434) else "REFUSED"
            log(f"  {host}:5434 -> {res}")

        for host in ["127.0.0.1", "localhost"]:
            res = "SUCCESS" if check_port(host, 5432) else "REFUSED"
            log(f"  {host}:5432 -> {res} (Internal Default)")

        # 4. Environment Variables check
        log("\n[4] Relevant Env Vars:")
        for key in ["APP_DATABASE__HOST", "APP_DATABASE__PORT", "DATABASE_URL"]:
            log(f"  {key}: {os.environ.get(key, 'NOT SET')}")

        log("\n--- DIAGNOSTIC COMPLETE ---")


if __name__ == "__main__":
    diag()
