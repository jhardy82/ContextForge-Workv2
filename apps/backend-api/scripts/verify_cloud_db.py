import asyncio
import datetime
import ssl
import sys
import urllib.parse

from dotenv import load_dotenv

load_dotenv()


async def verify_schema():
    # Helper to write to log
    def log(msg):
        with open("verify_output_final.log", "a", encoding="utf-8") as f:
            f.write(f"{msg}\n")

    # Init log
    with open("verify_output_final.log", "w", encoding="utf-8") as f:
        f.write(f"Verification Run: {datetime.datetime.now()}\n")

    # Start
    log("Starting verification...")

    # Load from Env or Fallback (matching the successful hardcoded values if needed, but let's try env first)
    # Actually, let's use the known good credentials to BE SURE.
    # The user accepted hardcoding for migration, let's use it for verification to close the loop,
    # then cleaning up is a separate step.
    host = "aws-1-us-west-1.pooler.supabase.com"
    user = "postgres.cwohzhbuftwssqopbxdi"
    port = "5432"
    database = "postgres"
    password = "ContextForge!@#$"
    encoded_password = urllib.parse.quote_plus(password)
    dsn = f"postgresql://{user}:{encoded_password}@{host}:{port}/{database}"

    # SSL Context
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    import asyncpg

    try:
        log(f"Connecting to {host}...")
        conn = await asyncpg.connect(dsn, timeout=10, ssl=ctx)
        log("Connected.")

        # Check Tables
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        found_tables = [r["table_name"] for r in tables]
        log(f"\nFound Tables ({len(found_tables)}):")
        for t in found_tables:
            log(f"- {t}")

        expected = [
            "projects",
            "sprints",
            "tasks",
            "action_lists",
            "checklists",
            "plans",
            "conversation_sessions",
        ]
        missing = [t for t in expected if t not in found_tables]

        if not missing:
            log("\n✅ SUCCESS: All core tables found!")
            await conn.close()
            return True
        else:
            log(f"\n❌ FAILURE: Missing tables: {missing}")
            await conn.close()
            return False

    except Exception as e:
        log(f"\n❌ CONNECTION ERROR: {e}")
        return False


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    success = asyncio.run(verify_schema())
    sys.exit(0 if success else 1)
