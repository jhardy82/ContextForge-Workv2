#!/usr/bin/env python
"""Count tasks in PostgreSQL database."""

import asyncio
import sys
from pathlib import Path

from sqlalchemy import text

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import logging
import traceback

from taskman_api.db.session import manager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def main():
    try:
        logger.info("Connecting to database...")
        # Verify config is loaded
        from taskman_api.config import get_settings

        settings = get_settings()

        logger.info(
            f"Database Config: Host={settings.database.host}, Port={settings.database.port}"
        )

        async with manager.PrimarySession() as session:
            logger.info("Executing count query...")
            result = await session.execute(text("SELECT COUNT(*) FROM tasks"))
            count = result.scalar()
            logger.info(f"Tasks in database: {count}")

            # Also show first few
            result = await session.execute(text("SELECT id, title, status FROM tasks LIMIT 5"))
            rows = result.fetchall()
            for row in rows:
                logger.info(f"  - {row[0]}: {row[1]} ({row[2]})")

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
