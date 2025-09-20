#!/usr/bin/env python3
"""
Migration Script: Create All Tables
This script creates all tables in the Planora database using the SQL schema
and also using SQLAlchemy models.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from sqlalchemy import text
from app.db.database import engine, SessionLocal, Base

def create_tables_using_sql():
    """Create tables using raw SQL from the schema file"""

    print("\n🔧 Creating tables using SQL schema...")

    # Read the SQL schema file
    sql_file_path = Path(__file__).parent / "sql-queries" / "create_tables.sql"

    if not sql_file_path.exists():
        print(f"  ❌ SQL schema file not found: {sql_file_path}")
        return False

    try:
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()

        with SessionLocal() as session:
            # Split the SQL content by statements and execute each one
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]

            created_count = 0
            for statement in statements:
                if statement.upper().startswith(('CREATE TABLE', 'CREATE INDEX')):
                    try:
                        session.execute(text(statement))
                        session.commit()
                        created_count += 1

                        # Extract table/index name for logging
                        if 'CREATE TABLE' in statement.upper():
                            table_name = statement.split()[2]
                            print(f"  ✅ Created table: {table_name}")
                        elif 'CREATE INDEX' in statement.upper():
                            index_name = statement.split()[2]
                            print(f"  ✅ Created index: {index_name}")

                    except Exception as e:
                        print(f"  ❌ Error executing statement: {str(e)[:100]}...")
                        session.rollback()
                        continue

            print(f"  🎉 Successfully created {created_count} database objects")
            return True

    except Exception as e:
        print(f"  ❌ Error reading or executing SQL file: {str(e)}")
        return False

def create_tables_using_sqlalchemy():
    """Create tables using SQLAlchemy models"""

    print("\n🔧 Creating tables using SQLAlchemy models...")

    try:
        # Import all models to ensure they're registered with Base
        from app.features.users.models import User
        from app.features.roles.models import Role
        from app.features.projects.models import Project
        from app.features.epics.models import Epic
        from app.features.sprints.models import Sprint
        from app.features.stories.models import Story
        from app.features.backlog.models import Backlog
        from app.features.audit_logs.models import AuditLog
        from app.features.masters.models import ProjectMethodology, ProjectType, ProjectStatus, Priority, Department

        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("  ✅ All SQLAlchemy models created successfully!")
        return True

    except Exception as e:
        print(f"  ❌ Error creating tables with SQLAlchemy: {str(e)}")
        return False

def verify_tables_created():
    """Verify that all tables have been created"""
    print("\n🔍 Verifying all tables have been created...")

    expected_tables = [
        "tbl_master_priority",
        "tbl_master_project_status",
        "tbl_master_project_type",
        "tbl_master_project_methodology",
        "tbl_master_department",
        "tbl_roles",
        "tbl_users",
        "tbl_projects",
        "tbl_project_epics",
        "tbl_project_sprints",
        "tbl_project_stories",
        "tbl_project_backlog",
        "tbl_audit_logs"
    ]

    try:
        with SessionLocal() as session:
            # Get list of existing tables
            result = session.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                AND table_name LIKE 'tbl_%'
                ORDER BY table_name;
            """))

            existing_tables = [row[0] for row in result.fetchall()]

            print(f"  📊 Found {len(existing_tables)} tables in database:")

            missing_tables = []
            for table in expected_tables:
                if table in existing_tables:
                    print(f"     ✅ {table}")
                else:
                    print(f"     ❌ {table} (MISSING)")
                    missing_tables.append(table)

            if not missing_tables:
                print("  🎉 Verification successful: All expected tables exist!")
                return True
            else:
                print(f"  ⚠️  Warning: {len(missing_tables)} tables are missing")
                return False

    except Exception as e:
        print(f"  ❌ Verification failed: {str(e)}")
        return False

def main():
    """Main migration function"""
    print("=" * 80)
    print("🚀 PLANORA API - CREATE ALL TABLES MIGRATION")
    print("=" * 80)
    print("This script will create all tables for the Planora system:")
    print("  1. Master tables (priority, status, type, methodology)")
    print("  2. Core tables (roles, users)")
    print("  3. Project tables (projects, epics, sprints, tasks, backlog)")
    print("  4. System tables (audit_logs)")
    print("  5. Database indexes for performance")
    print("\n" + "=" * 80)

    try:
        # Method 1: Try creating with SQLAlchemy first (recommended)
        print("\n📋 METHOD 1: Creating tables using SQLAlchemy models...")
        sqlalchemy_success = create_tables_using_sqlalchemy()

        # Method 2: Fallback to SQL if SQLAlchemy fails
        if not sqlalchemy_success:
            print("\n📋 METHOD 2: Fallback to SQL schema creation...")
            sql_success = create_tables_using_sql()
            if not sql_success:
                print("\n❌ Both creation methods failed!")
                return False

        # Verify creation
        verification_success = verify_tables_created()

        if verification_success:
            print("\n" + "=" * 80)
            print("✅ CREATE ALL TABLES MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            print("🎯 Next steps:")
            print("  1. Run migration_insert_mock_data.py to populate with data")
            print("  2. Run migration_verify_mock_data.py to validate the data")
            print("=" * 80)
            return True
        else:
            print("\n" + "=" * 80)
            print("⚠️  CREATE ALL TABLES MIGRATION COMPLETED WITH WARNINGS!")
            print("=" * 80)
            return False

    except Exception as e:
        print(f"\n❌ Migration failed with error: {str(e)}")
        print("\n" + "=" * 80)
        print("❌ CREATE ALL TABLES MIGRATION FAILED!")
        print("=" * 80)
        return False

if __name__ == "__main__":
    print("Starting create all tables migration...")

    success = main()

    if not success:
        sys.exit(1)