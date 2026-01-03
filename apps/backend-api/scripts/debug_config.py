
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from taskman_api.config import get_settings


def log(msg):
    with open("debug_config.log", "a") as f:
        f.write(msg + "\n")

def main():
    # clear log
    with open("debug_config.log", "w") as f:
        f.write("Starting Debug...\n")

    log("Loading settings...")
    try:
        settings = get_settings()
        log(f"App Name: {settings.app_name}")
        log(f"Database Host: {settings.database.host}")
        log(f"Database Port: {settings.database.port}")
        log(f"Database User: {settings.database.user}")
        log(f"Connection String: {settings.database.async_connection_string}")

        log("\nEnvironment Variables:")
        for key, value in os.environ.items():
            if "APP_" in key:
                log(f"{key}={value}")
    except Exception as e:
        log(f"Error loading settings: {e}")

if __name__ == "__main__":
    main()
