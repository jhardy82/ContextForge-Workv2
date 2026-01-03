
import datetime
import shutil
import socket
import subprocess

# Configuration
LOG_FILE = "infrastructure_diagnosis.log"
PORTS_TO_CHECK = [54322, 3001, 5174, 5432, 8000]
DOCKER_CMD = shutil.which("docker")

def log(message, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    print(log_entry)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n")

def check_port(port):
    log(f"Checking port {port}...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('127.0.0.1', port))
            if result == 0:
                log(f"Port {port} is OPEN (Listening).")
                # Try to identify process (Windows specific)
                try:
                    # Using netstat to find PID
                    cmd = f"netstat -ano | findstr :{port}"
                    output = subprocess.check_output(cmd, shell=True).decode()
                    log(f"Netstat output for {port}:\n{output}", "DEBUG")
                except subprocess.CalledProcessError:
                    pass
                return True
            else:
                log(f"Port {port} is CLOSED (Not Listening).", "WARNING")
                return False
    except Exception as e:
        log(f"Error checking port {port}: {e}", "ERROR")
        return False

def check_docker():
    log("Checking Docker status...")
    if not DOCKER_CMD:
        log("Docker executable not found in PATH.", "ERROR")
        return False

    try:
        # Check docker info
        subprocess.check_call([DOCKER_CMD, "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log("Docker daemon is running.")

        # Check running containers
        log("Checking running containers...")
        output = subprocess.check_output([DOCKER_CMD, "ps", "--format", "{{.Names}} {{.Status}} {{.Ports}}"]).decode()
        if output.strip():
            log(f"Running Containers:\n{output}")
        else:
            log("No running containers found.", "WARNING")

        # Check specifically for supabase
        if "supabase" in output.lower():
             log("Supabase containers detected.")
        else:
             log("No Supabase containers detected.", "WARNING")

        return True

    except subprocess.CalledProcessError:
        log("Docker daemon is NOT running or not accessible.", "ERROR")
        return False
    except Exception as e:
        log(f"Error checking docker: {e}", "ERROR")
        return False

def main():
    log("=== Starting Infrastructure Diagnosis (Python) ===")

    docker_ok = check_docker()

    ports_status = {}
    for port in PORTS_TO_CHECK:
        ports_status[port] = check_port(port)

    log("=== Diagnosis Complete ===")

    # Summary
    if not docker_ok:
        log("CRITICAL: Docker is not running. Start Docker Desktop.", "ERROR")

    if not ports_status.get(54322):
         log("CRITICAL: Local Supabase DB (Port 54322) is not listening. Run 'npx supabase start'.", "ERROR")

    if not ports_status.get(3001):
         log("INFO: Backend API (Port 3001) is not running.", "INFO")

if __name__ == "__main__":
    main()
