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
        from app.features.audit_logs.models import AuditLog
        from app.features.masters.models import ProjectMethodology, ProjectType, ProjectStatus, Priority, Department, Industry, TaskStatus
        from app.features.customers.models import Customer
        from app.features.files.models import File, FileFolder, StorageQuota

        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("  ✅ All SQLAlchemy models created successfully!")

        # Add task fields to stories table
        add_task_fields_success = add_task_fields_to_stories()
        if not add_task_fields_success:
            print("  ⚠️  Warning: Could not add task fields to stories table")

        # Create additional file tables (if not already created by SQLAlchemy)
        create_additional_file_tables_success = create_additional_file_tables()
        if not create_additional_file_tables_success:
            print("  ⚠️  Warning: Could not create additional file table constraints")

        return True

    except Exception as e:
        print(f"  ❌ Error creating tables with SQLAlchemy: {str(e)}")
        return False

def add_task_fields_to_stories():
    """Add task fields to stories table"""
    print("\n🔧 Adding task fields to tbl_project_stories...")

    # SQL statements to add task fields
    task_fields_sql = [
        "ALTER TABLE tbl_project_stories ADD COLUMN IF NOT EXISTS subtasks JSON",
        "ALTER TABLE tbl_project_stories ADD COLUMN IF NOT EXISTS comments JSON",
        "ALTER TABLE tbl_project_stories ADD COLUMN IF NOT EXISTS attached_files JSON",
        "ALTER TABLE tbl_project_stories ADD COLUMN IF NOT EXISTS progress INTEGER DEFAULT 0",
        "ALTER TABLE tbl_project_stories ADD COLUMN IF NOT EXISTS start_date DATE",
        "ALTER TABLE tbl_project_stories ADD COLUMN IF NOT EXISTS end_date DATE",
        "ALTER TABLE tbl_project_stories ADD COLUMN IF NOT EXISTS tags TEXT[]",
        "ALTER TABLE tbl_project_stories ADD COLUMN IF NOT EXISTS activity JSON",

        # Add comments
        "COMMENT ON COLUMN tbl_project_stories.subtasks IS 'JSON array of subtask objects with task_name, description, assignee, priority, due_date'",
        "COMMENT ON COLUMN tbl_project_stories.comments IS 'JSON array of comment objects with id, author_id, author_name, content, created_at'",
        "COMMENT ON COLUMN tbl_project_stories.attached_files IS 'JSON array of file attachment objects with id, filename, file_path, file_size, uploaded_by, uploaded_at'",
        "COMMENT ON COLUMN tbl_project_stories.progress IS 'Progress percentage (0-100)'",
        "COMMENT ON COLUMN tbl_project_stories.start_date IS 'Task start date'",
        "COMMENT ON COLUMN tbl_project_stories.end_date IS 'Task end date'",
        "COMMENT ON COLUMN tbl_project_stories.tags IS 'Array of tag strings for categorization'",
        "COMMENT ON COLUMN tbl_project_stories.activity IS 'JSON array of activity log objects with id, user_id, user_name, action, description, timestamp'",

        # Add indexes
        "CREATE INDEX IF NOT EXISTS idx_stories_progress ON tbl_project_stories(progress)",
        "CREATE INDEX IF NOT EXISTS idx_stories_start_date ON tbl_project_stories(start_date)",
        "CREATE INDEX IF NOT EXISTS idx_stories_end_date ON tbl_project_stories(end_date)",
        "CREATE INDEX IF NOT EXISTS idx_stories_tags ON tbl_project_stories USING GIN(tags)"
    ]

    try:
        with SessionLocal() as session:
            executed_count = 0
            for statement in task_fields_sql:
                try:
                    session.execute(text(statement))
                    session.commit()
                    executed_count += 1

                    # Log what was executed
                    if 'ALTER TABLE' in statement.upper():
                        print(f"  ✅ Added column to tbl_project_stories")
                    elif 'CREATE INDEX' in statement.upper():
                        print(f"  ✅ Created index")
                    elif 'COMMENT ON' in statement.upper():
                        print(f"  ✅ Added column comment")

                except Exception as e:
                    if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                        print(f"  ⚠️  Column/index already exists (skipping)")
                    else:
                        print(f"  ❌ Error executing statement: {str(e)[:100]}...")
                        session.rollback()
                        continue

            print(f"  🎉 Successfully executed {executed_count} task field statements")
            return True

    except Exception as e:
        print(f"  ❌ Error adding task fields: {str(e)}")
        return False

def create_additional_file_tables():
    """Create additional file table constraints and indexes that may not be in SQLAlchemy models"""
    print("\n🔧 Creating additional file table indexes and constraints...")

    # Additional SQL statements for file tables optimization
    file_tables_sql = [
        # Additional indexes for better performance
        "CREATE INDEX IF NOT EXISTS idx_files_entity ON tbl_files(entity_type, entity_id)",
        "CREATE INDEX IF NOT EXISTS idx_files_category ON tbl_files(category)",
        "CREATE INDEX IF NOT EXISTS idx_files_uploaded_by ON tbl_files(uploaded_by_id)",
        "CREATE INDEX IF NOT EXISTS idx_files_created_at ON tbl_files(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_files_is_deleted ON tbl_files(is_deleted)",
        "CREATE INDEX IF NOT EXISTS idx_file_folders_entity ON tbl_file_folders(entity_type, entity_id)",
        "CREATE INDEX IF NOT EXISTS idx_file_folders_parent ON tbl_file_folders(parent_folder_id)",
        "CREATE INDEX IF NOT EXISTS idx_storage_quotas_entity ON tbl_storage_quotas(entity_type, entity_id)",

        # Create default storage quotas for existing projects
        """
        INSERT INTO tbl_storage_quotas (id, entity_type, entity_id, total_quota_bytes, max_files)
        SELECT
            'quota_' || p.id,
            'project',
            p.id,
            10737418240,  -- 10GB
            1000
        FROM tbl_projects p
        WHERE NOT EXISTS (
            SELECT 1 FROM tbl_storage_quotas sq
            WHERE sq.entity_type = 'project' AND sq.entity_id = p.id
        )
        ON CONFLICT (entity_type, entity_id) DO NOTHING
        """
    ]

    try:
        with SessionLocal() as session:
            executed_count = 0
            for statement in file_tables_sql:
                try:
                    session.execute(text(statement))
                    session.commit()
                    executed_count += 1

                    # Log what was executed
                    if 'CREATE INDEX' in statement.upper():
                        print(f"  ✅ Created file table index")
                    elif 'INSERT INTO' in statement.upper():
                        print(f"  ✅ Created default storage quotas")

                except Exception as e:
                    if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                        print(f"  ⚠️  Index/quota already exists (skipping)")
                    else:
                        print(f"  ❌ Error executing statement: {str(e)[:100]}...")
                        session.rollback()
                        continue

            print(f"  🎉 Successfully executed {executed_count} file table statements")
            return True

    except Exception as e:
        print(f"  ❌ Error creating additional file tables: {str(e)}")
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
        "tbl_master_industry",
        "tbl_customers",
        "tbl_roles",
        "tbl_users",
        "tbl_projects",
        "tbl_project_epics",
        "tbl_project_sprints",
        "tbl_project_stories",
        "tbl_audit_logs",
        "tbl_files",
        "tbl_file_folders",
        "tbl_storage_quotas",
        "tbl_master_task_status"
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
    print("  1. Master tables (priority, status, type, methodology, department, industry, task_status)")
    print("  2. Core tables (roles, users)")
    print("  3. Customer tables (customers)")
    print("  4. Project tables (projects, epics, sprints, stories with task support)")
    print("  5. File management tables (files, file_folders, storage_quotas)")
    print("  6. System tables (audit_logs)")
    print("  7. Task management fields (subtasks, comments, attachments, progress, dates, tags, activity)")
    print("  8. Database indexes and constraints for performance")
    print("  9. Default storage quotas for projects")
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