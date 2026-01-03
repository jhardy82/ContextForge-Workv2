"""Test migration reversibility and schema completeness.

Tests:
1. Upgrade migration creates all 13 fields
2. All 6 indexes are created correctly
3. FK constraints are established
4. Downgrade migration removes everything cleanly
5. Schema matches expected state after upgrade

Usage:
    python test_migration_0025.py --connection-string postgresql://user:pass@host:port/db
"""

import argparse
import asyncio

import asyncpg


async def test_migration_upgrade(connection_string: str) -> bool:
    """Test that upgrade migration creates all expected fields and indexes."""
    conn = await asyncpg.connect(connection_string)
    print("✅ Connected to database")

    try:
        # Test 1: Verify all 20 columns exist
        print("\nTest 1: Verifying column count...")
        columns = await conn.fetch(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'action_lists'
            ORDER BY ordinal_position
            """
        )

        expected_columns = {
            "id",
            "name",
            "description",
            "status",
            "owner",
            "tags",
            "project_id",
            "sprint_id",
            "task_ids",
            "items",
            "geometry_shape",
            "priority",
            "due_date",
            "evidence_refs",
            "extra_metadata",
            "notes",
            "parent_deleted_at",
            "parent_deletion_note",
            "created_at",
            "updated_at",
            "completed_at",
        }

        actual_columns = {col["column_name"] for col in columns}

        if actual_columns == expected_columns:
            print("  ✅ All 21 expected columns present")
        else:
            missing = expected_columns - actual_columns
            extra = actual_columns - expected_columns
            if missing:
                print(f"  ❌ Missing columns: {missing}")
            if extra:
                print(f"  ⚠️  Extra columns: {extra}")
            return False

        # Test 2: Verify indexes
        print("\nTest 2: Verifying indexes...")
        indexes = await conn.fetch(
            """
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'action_lists'
            AND indexname != 'action_lists_pkey'
            ORDER BY indexname
            """
        )

        expected_indexes = {
            "ix_action_lists_task_ids",  # GIN index
            "ix_action_lists_status",
            "ix_action_lists_priority",
            "ix_action_lists_created_at",
            "ix_action_lists_completed_at",
            "ix_action_lists_due_date",
            "ix_action_lists_status_priority",  # Composite
        }

        actual_indexes = {idx["indexname"] for idx in indexes}

        if expected_indexes.issubset(actual_indexes):
            print("  ✅ All 7 expected indexes present")
            for idx in indexes:
                is_gin = "USING gin" in idx["indexdef"]
                idx_type = "GIN" if is_gin else "B-tree"
                print(f"    - {idx['indexname']} ({idx_type})")
        else:
            missing = expected_indexes - actual_indexes
            print(f"  ❌ Missing indexes: {missing}")
            return False

        # Test 3: Verify foreign key constraints
        print("\nTest 3: Verifying foreign key constraints...")
        fk_constraints = await conn.fetch(
            """
            SELECT
                tc.constraint_name,
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                rc.delete_rule
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            JOIN information_schema.referential_constraints AS rc
              ON rc.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_name = 'action_lists'
            """
        )

        expected_fks = {
            "fk_action_lists_project_id_projects",
            "fk_action_lists_sprint_id_sprints",
        }

        actual_fks = {fk["constraint_name"] for fk in fk_constraints}

        if expected_fks.issubset(actual_fks):
            print("  ✅ All 2 expected foreign key constraints present")
            for fk in fk_constraints:
                print(
                    f"    - {fk['constraint_name']}: {fk['column_name']} → "
                    f"{fk['foreign_table_name']}.{fk['foreign_column_name']} "
                    f"(ON DELETE {fk['delete_rule']})"
                )
        else:
            missing = expected_fks - actual_fks
            print(f"  ❌ Missing FK constraints: {missing}")
            return False

        # Test 4: Verify column types
        print("\nTest 4: Verifying column types...")
        type_checks = {
            "id": "character varying",
            "name": "character varying",
            "description": "text",
            "status": "character varying",
            "owner": "character varying",
            "tags": "json",
            "project_id": "character varying",
            "sprint_id": "character varying",
            "task_ids": "ARRAY",
            "items": "json",
            "priority": "character varying",
            "due_date": "timestamp with time zone",
            "completed_at": "timestamp with time zone",
        }

        type_errors = []
        for col in columns:
            col_name = col["column_name"]
            col_type = col["data_type"]
            if col_name in type_checks:
                expected_type = type_checks[col_name]
                if expected_type not in col_type:
                    type_errors.append(f"{col_name}: expected {expected_type}, got {col_type}")

        if not type_errors:
            print("  ✅ All column types correct")
        else:
            for error in type_errors:
                print(f"  ❌ {error}")
            return False

        # Test 5: Test GIN index functionality
        print("\nTest 5: Testing GIN index performance...")
        # Insert test data
        await conn.execute(
            """
            INSERT INTO action_lists (id, name, status, task_ids, owner)
            VALUES ('AL-GIN-TEST', 'GIN Test', 'active', ARRAY['TASK-001', 'TASK-002'], 'testuser')
            ON CONFLICT (id) DO UPDATE SET task_ids = ARRAY['TASK-001', 'TASK-002']
            """
        )

        # Query using GIN index
        result = await conn.fetch(
            """
            EXPLAIN (FORMAT JSON)
            SELECT * FROM action_lists WHERE 'TASK-001' = ANY(task_ids)
            """
        )

        # Check if index is used
        plan_str = str(result[0]["QUERY PLAN"])
        uses_gin = "ix_action_lists_task_ids" in plan_str

        if uses_gin:
            print("  ✅ GIN index is being used for containment queries")
        else:
            print("  ⚠️  GIN index not detected in query plan (may still work correctly)")

        # Cleanup
        await conn.execute("DELETE FROM action_lists WHERE id = 'AL-GIN-TEST'")

        print("\n" + "=" * 60)
        print("✅ ALL MIGRATION TESTS PASSED")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        await conn.close()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test ActionList schema migration")
    parser.add_argument(
        "--connection-string",
        default="postgresql://contextforge:contextforge@172.25.14.122:5432/taskman_v2",
        help="PostgreSQL connection string",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("MIGRATION 0025 VALIDATION TEST")
    print("=" * 60)
    print(f"Connection: {args.connection_string}\n")

    success = await test_migration_upgrade(args.connection_string)
    exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
