
import asyncio
import sys

import asyncpg
from dotenv import load_dotenv

# Load environment variables (to get connection string if needed, but we'll default to localhost)
load_dotenv()

async def check_connection():
    # Database connection parameters
    # Defaulting to standard local config. User might need to change password in the script or usage.
    # We'll try to connect to the default 'postgres' database initially to verify service is up.

    # We will try a few potential passwords if not provided, or strictly follow the "contextforge" suggestion
    dsn = "postgresql://postgres:contextforge@localhost:5432/postgres"

    print(f"Attempting to connect to: {dsn}")

    try:
        conn = await asyncpg.connect(dsn)
        print("✅ SUCCESS: Connected to PostgreSQL 16 on WSL2 (localhost:5432)")

        # Verify version
        version = await conn.fetchval("SELECT version()")
        print(f"ℹ️  Server Version: {version}")

        # Verify pgvector extension
        try:
             # Check if vector extension is installed/available
             # We check pg_extension table
             rows = await conn.fetch("SELECT * FROM pg_extension WHERE extname = 'vector'")
             if rows:
                 print("✅ SUCCESS: 'vector' extension is installed.")
             else:
                 print("⚠️  WARNING: 'vector' extension NOT found in 'postgres' db (It might need to be created).")
        except Exception as e:
            print(f"⚠️  Error checking extensions: {e}")

        await conn.close()
        return True

    except ConnectionRefusedError:
        print("❌ FAILURE: Connection Refused. Is the service running? Is 'listen_addresses' set to '*' or 'localhost' in postgresql.conf?")
        return False
    except asyncpg.InvalidPasswordError:
        print("❌ FAILURE: Invalid Password. Please check the password set for the 'postgres' user.")
        return False
    except Exception as e:
        print(f"❌ FAILURE: An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(check_connection())
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
