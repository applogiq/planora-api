#!/usr/bin/env python3
"""
Migration Script: Drop All Tables
This script safely drops all tables in the Planora database in the correct order
to avoid foreign key constraint violations.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from sqlalchemy import text
from app.db.database import engine, SessionLocal

def drop_all_tables():
    """Drop all tables in the correct order to avoid constraint violations"""

    print("=" * 80)
    print("🗑️  PLANORA API - DROP ALL TABLES MIGRATION")
    print("=" * 80)
    print("This script will drop all tables in the correct order:")
    print("  1. Dependent tables first (audit_logs, project_tasks, etc.)")
    print("  2. Reference tables (projects, users, etc.)")
    print("  3. Master tables (roles, priority, etc.)")
    print("\n" + "=" * 80)

    # Define tables in drop order (reverse dependency order)
    tables_to_drop = [
        "tbl_audit_logs",
        "tbl_customers",
        "tbl_project_stories",
        "tbl_project_sprints",
        "tbl_project_epics",
        "tbl_projects",
        "tbl_users",
        "tbl_roles",
        "tbl_master_department",
        "tbl_master_industry",
        "tbl_master_project_methodology",
        "tbl_master_project_type",
        "tbl_master_project_status",
        "tbl_master_priority"
    ]

    try:
        with SessionLocal() as session:
            print("\n🔧 Starting table drop process...")

            # Drop tables one by one
            dropped_count = 0
            for table_name in tables_to_drop:
                try:
                    # Check if table exists first
                    result = session.execute(text(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables
                            WHERE table_schema = 'public'
                            AND table_name = '{table_name}'
                        );
                    """))
                    table_exists = result.scalar()

                    if table_exists:
                        session.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE;"))
                        session.commit()
                        print(f"  ✅ Dropped table: {table_name}")
                        dropped_count += 1
                    else:
                        print(f"  ⚠️  Table not found: {table_name}")

                except Exception as e:
                    print(f"  ❌ Error dropping table {table_name}: {str(e)}")
                    session.rollback()
                    continue

            print(f"\n🎉 Migration completed successfully!")
            print(f"   Total tables dropped: {dropped_count}")
            print(f"   Database is now clean and ready for fresh setup.")

    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        return False

    return True

def verify_tables_dropped():
    """Verify that all tables have been dropped"""
    print("\n🔍 Verifying all tables have been dropped...")

    try:
        with SessionLocal() as session:
            # Get list of remaining tables
            result = session.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                AND table_name LIKE 'tbl_%'
                ORDER BY table_name;
            """))

            remaining_tables = [row[0] for row in result.fetchall()]

            if not remaining_tables:
                print("  ✅ Verification successful: No tables remaining")
                return True
            else:
                print(f"  ⚠️  Warning: {len(remaining_tables)} tables still exist:")
                for table in remaining_tables:
                    print(f"     - {table}")
                return False

    except Exception as e:
        print(f"  ❌ Verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting drop all tables migration...")

    # Ask for confirmation
    response = input("\n⚠️  WARNING: This will permanently delete ALL data. Continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ Migration cancelled by user")
        sys.exit(1)

    # Execute migration
    success = drop_all_tables()

    if success:
        # Verify tables are dropped
        verify_tables_dropped()
        print("\n" + "=" * 80)
        print("✅ DROP ALL TABLES MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ DROP ALL TABLES MIGRATION FAILED!")
        print("=" * 80)
        sys.exit(1)