#!/usr/bin/env python3
"""
Migration Script: Insert All Mock Data
This script coordinates the insertion of all mock data from the organized mock-data folder
ensuring each table has a minimum of 25 entries.
"""

import sys
import os
from pathlib import Path
import io
import importlib.util

# Set stdout to handle Unicode properly
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add the current directory to Python path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import SessionLocal, engine
from app.db.database import Base

# Import all models in correct order to avoid circular import issues
from app.features.masters.models import ProjectMethodology, ProjectType, ProjectStatus, Priority
from app.features.roles.models import Role
from app.features.users.models import User
from app.features.projects.models import Project
from app.features.epics.models import Epic
from app.features.sprints.models import Sprint
from app.features.stories.models import Story
from app.features.backlog.models import Backlog
from app.features.audit_logs.models import AuditLog

def load_module_from_path(module_name, file_path):
    """Dynamically load a Python module from a file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def execute_mock_data_scripts():
    """Execute all mock data scripts directly"""
    print(f"\n🚀 Executing mock data scripts...")

    successful_scripts = 0
    total_scripts = 0

    try:
        # Add mock-data directory to path
        mock_data_dir = Path(__file__).parent / "mock-data"
        sys.path.insert(0, str(mock_data_dir))

        # Execute master data
        print(f"\n🔄 Executing master data insertion...")
        try:
            from insert_master_data import insert_master_data
            insert_master_data()
            print(f"  ✅ Master data inserted successfully")
            successful_scripts += 1
        except Exception as e:
            print(f"  ❌ Error inserting master data: {str(e)}")
        total_scripts += 1

        # Execute user data
        print(f"\n🔄 Executing user data insertion...")
        try:
            from insert_user_data import create_user_tables_and_insert_data
            create_user_tables_and_insert_data()
            print(f"  ✅ User data inserted successfully")
            successful_scripts += 1
        except Exception as e:
            print(f"  ❌ Error inserting user data: {str(e)}")
        total_scripts += 1

        # Execute project data
        print(f"\n🔄 Executing project data insertion...")
        try:
            from insert_all_project_data import create_all_project_tables_and_insert_data
            create_all_project_tables_and_insert_data()
            print(f"  ✅ Project data inserted successfully")
            successful_scripts += 1
        except Exception as e:
            print(f"  ❌ Error inserting project data: {str(e)}")
        total_scripts += 1

        # Execute backlog data
        print(f"\n🔄 Executing backlog data insertion...")
        try:
            from insert_backlog_data import create_backlog_tables_and_insert_data
            create_backlog_tables_and_insert_data()
            print(f"  ✅ Backlog data inserted successfully")
            successful_scripts += 1
        except Exception as e:
            print(f"  ❌ Error inserting backlog data: {str(e)}")
        total_scripts += 1

        return successful_scripts, total_scripts

    except Exception as e:
        print(f"  ❌ Error in mock data execution: {str(e)}")
        return successful_scripts, total_scripts
    finally:
        # Clean up path
        if str(mock_data_dir) in sys.path:
            sys.path.remove(str(mock_data_dir))

def get_table_counts():
    """Get current row counts for all tables"""
    try:
        with SessionLocal() as session:
            tables = [
                "tbl_master_priority",
                "tbl_master_project_status",
                "tbl_master_project_type",
                "tbl_master_project_methodology",
                "tbl_roles",
                "tbl_users",
                "tbl_projects",
                "tbl_project_epics",
                "tbl_project_sprints",
                "tbl_project_stories",
                "tbl_project_backlog",
                "tbl_audit_logs"
            ]

            counts = {}
            for table in tables:
                try:
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    counts[table] = result.scalar()
                except Exception:
                    counts[table] = 0

            return counts

    except Exception as e:
        print(f"Error getting table counts: {str(e)}")
        return {}

def main():
    """Main migration function"""
    print("=" * 80)
    print("📥 PLANORA API - INSERT ALL MOCK DATA MIGRATION")
    print("=" * 80)
    print("This script will insert comprehensive mock data:")
    print("  1. Master data (priorities, statuses, types, methodologies)")
    print("  2. Users and roles (minimum 25 users)")
    print("  3. Projects data (minimum 25 projects)")
    print("  4. Epics, sprints, tasks, and backlog items")
    print("  5. Audit logs for tracking")
    print("\n" + "=" * 80)

    # Get initial table counts
    print("\n📊 Checking initial table state...")
    initial_counts = get_table_counts()

    for table, count in initial_counts.items():
        print(f"  📋 {table}: {count} rows")

    # Execute mock data scripts
    successful_scripts, total_scripts = execute_mock_data_scripts()

    # Get final table counts
    print("\n📊 Checking final table state...")
    final_counts = get_table_counts()

    print("\n📈 Data insertion summary:")
    print("  " + "-" * 50)

    tables_with_sufficient_data = 0
    tables_with_insufficient_data = 0

    for table in final_counts:
        initial = initial_counts.get(table, 0)
        final = final_counts[table]
        added = final - initial

        status = "✅" if final >= 25 else "⚠️ "
        print(f"  {status} {table}: {initial} → {final} (+{added})")

        if final >= 25:
            tables_with_sufficient_data += 1
        else:
            tables_with_insufficient_data += 1

    # Summary
    print("\n" + "=" * 80)
    print("📊 MIGRATION SUMMARY:")
    print("=" * 80)
    print(f"  📜 Scripts executed: {successful_scripts}/{total_scripts}")
    print(f"  ✅ Tables with ≥25 rows: {tables_with_sufficient_data}")
    print(f"  ⚠️  Tables with <25 rows: {tables_with_insufficient_data}")

    if successful_scripts == total_scripts and tables_with_insufficient_data == 0:
        print(f"\n🎉 ALL MOCK DATA INSERTED SUCCESSFULLY!")
        print(f"   All tables have sufficient data (≥25 rows)")
        print("=" * 80)
        print("🎯 Next steps:")
        print("  1. Run migration_verify_mock_data.py to validate the data")
        print("  2. Start the API server and test endpoints")
        print("=" * 80)
        return True
    elif successful_scripts > 0:
        print(f"\n⚠️  MOCK DATA INSERTION COMPLETED WITH WARNINGS!")
        if tables_with_insufficient_data > 0:
            print(f"   {tables_with_insufficient_data} tables have less than 25 rows")
        print("=" * 80)
        return False
    else:
        print(f"\n❌ MOCK DATA INSERTION FAILED!")
        print("   No scripts executed successfully")
        print("=" * 80)
        return False

if __name__ == "__main__":
    print("Starting insert all mock data migration...")

    # Ask for confirmation
    response = input("\n🤔 This will insert mock data into the database. Continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ Migration cancelled by user")
        sys.exit(1)

    success = main()

    if not success:
        sys.exit(1)