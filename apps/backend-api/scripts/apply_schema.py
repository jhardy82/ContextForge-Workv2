import asyncio
import os
import sys
import traceback

# Immediate logging check
LOG_FILE = "schema_debug.log"
with open(LOG_FILE, "w") as f:
    f.write("Script started.\n")
    f.flush()

    try:
        f.write("Adding src to path...\n")
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
        f.flush()

        f.write("Importing init_db...\n")
        # Move import here to catch import errors
        from taskman_api.db.session import check_db_health, init_db

        f.write("Import successful.\n")
        f.flush()
    except Exception as e:
        f.write(f"Import Error: {e}\n")
        traceback.print_exc(file=f)
        sys.exit(1)


async def main():
    with open(LOG_FILE, "a") as f:
        f.write("Checking initial DB health...\n")
        try:
            health = await check_db_health()
            f.write(f"Health: {health}\n")

            f.write("\nApplying schema (creating tables)...\n")
            await init_db()
            f.write("Schema applied successfully.\n")

            f.write("\nVerifying DB health after schema application...\n")
            health = await check_db_health()
            f.write(f"Health: {health}\n")
            f.write("SUCCESS\n")

        except Exception as e:
            f.write(f"Error applying schema: {e}\n")
            traceback.print_exc(file=f)
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
