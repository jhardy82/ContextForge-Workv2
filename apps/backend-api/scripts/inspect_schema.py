#!/usr/bin/env python
"""Inspect actual database schema for model alignment."""

import asyncio
import sys

from sqlalchemy import text

# Add parent to path
sys.path.insert(0, str(__file__).replace("scripts/inspect_schema.py", ""))

from db.session import engine


async def main():
    async with engine.connect() as conn:
        # Get all tables
        result = await conn.execute(
            text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        )
        print("=== TABLES IN DATABASE ===")
        tables = [row[0] for row in result]
        for t in tables:
            print(f"  - {t}")

        # Get tasks table schema
        print("\n=== TASKS TABLE SCHEMA ===")
        result = await conn.execute(
            text("""
            SELECT column_name, data_type, is_nullable,
                   character_maximum_length, numeric_precision
            FROM information_schema.columns
            WHERE table_name = 'tasks'
            ORDER BY ordinal_position
        """)
        )
        for row in result:
            col, dtype, nullable, char_len, num_prec = row
            size = f"({char_len})" if char_len else f"({num_prec})" if num_prec else ""
            print(f"  {col:30} {dtype}{size:15} {'NULL' if nullable == 'YES' else 'NOT NULL'}")

        # Get sprints table schema
        print("\n=== SPRINTS TABLE SCHEMA ===")
        result = await conn.execute(
            text("""
            SELECT column_name, data_type, is_nullable,
                   character_maximum_length, numeric_precision
            FROM information_schema.columns
            WHERE table_name = 'sprints'
            ORDER BY ordinal_position
        """)
        )
        for row in result:
            col, dtype, nullable, char_len, num_prec = row
            size = f"({char_len})" if char_len else f"({num_prec})" if num_prec else ""
            print(f"  {col:30} {dtype}{size:15} {'NULL' if nullable == 'YES' else 'NOT NULL'}")

        # Get projects table schema
        print("\n=== PROJECTS TABLE SCHEMA ===")
        result = await conn.execute(
            text("""
            SELECT column_name, data_type, is_nullable,
                   character_maximum_length, numeric_precision
            FROM information_schema.columns
            WHERE table_name = 'projects'
            ORDER BY ordinal_position
        """)
        )
        for row in result:
            col, dtype, nullable, char_len, num_prec = row
            size = f"({char_len})" if char_len else f"({num_prec})" if num_prec else ""
            print(f"  {col:30} {dtype}{size:15} {'NULL' if nullable == 'YES' else 'NOT NULL'}")

        # Check if action_lists exists
        print("\n=== ACTION_LISTS TABLE ===")
        result = await conn.execute(
            text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'action_lists'
            ORDER BY ordinal_position
        """)
        )
        rows = list(result)
        if rows:
            for row in rows:
                print(f"  {row[0]:30} {row[1]}")
        else:
            print("  (table does not exist)")


if __name__ == "__main__":
    asyncio.run(main())
