#!/usr/bin/env python3
"""
Planora API Complete Database Setup Script

This script provides a clean, single-command setup for the entire Planora database:
1. Creates all database tables using migration files
2. Inserts comprehensive mock data
3. Provides verification and status reporting

Usage:
    python setup/setup_planora.py                    # Full setup with mock data
    python setup/setup_planora.py --tables-only      # Create tables only
    python setup/setup_planora.py --data-only        # Insert mock data only
    python setup/setup_planora.py --verify           # Verify existing setup
"""

import sys
import os
import argparse
import psycopg2
from pathlib import Path
from datetime import datetime

# Add the current directory to Python path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

def get_db_connection():
    """Get database connection from environment"""
    try:
        # Read database URL from .env file
        env_path = current_dir / '.env'
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('DATABASE_URL='):
                    db_url = line.split('=', 1)[1].strip()
                    # Parse postgresql://user:password@host:port/db
                    db_url = db_url.replace('postgresql://', '')
                    user_pass, host_port_db = db_url.split('@')
                    user, password = user_pass.split(':')
                    host_port, db = host_port_db.split('/')
                    host, port = host_port.split(':')

                    return psycopg2.connect(
                        host=host,
                        port=port,
                        database=db,
                        user=user,
                        password=password
                    )
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def execute_sql_file(conn, sql_file_path, description):
    """Execute SQL file and return success status"""
    try:
        print(f"   🔄 {description}...")

        with open(sql_file_path, 'r') as f:
            sql_content = f.read()

        cur = conn.cursor()
        cur.execute(sql_content)
        conn.commit()
        cur.close()

        print(f"   ✅ {description} completed successfully")
        return True

    except Exception as e:
        print(f"   ❌ {description} failed: {e}")
        conn.rollback()
        return False

def execute_python_script(script_path, description):
    """Execute Python script and return success status"""
    try:
        print(f"   🔄 {description}...")

        # Import and execute the script
        spec = __import__(f"setup.{script_path.stem}", fromlist=[''])
        if hasattr(spec, 'insert_master_data'):
            spec.insert_master_data()
        elif hasattr(spec, 'insert_core_data'):
            spec.insert_core_data()
        elif hasattr(spec, 'insert_project_data'):
            spec.insert_project_data()
        else:
            print(f"   ❌ No suitable function found in {script_path}")
            return False

        print(f"   ✅ {description} completed successfully")
        return True

    except Exception as e:
        print(f"   ❌ {description} failed: {e}")
        return False

def create_tables():
    """Create all database tables using migration files"""
    print("\n🏗️  CREATING DATABASE TABLES")
    print("=" * 60)

    conn = get_db_connection()
    if not conn:
        return False

    setup_dir = Path(__file__).parent

    # Execute migration files in order
    migrations = [
        (setup_dir / "migrate_master_tables.sql", "Creating master tables"),
        (setup_dir / "migrate_core_tables.sql", "Creating core tables"),
        (setup_dir / "migrate_project_tables.sql", "Creating project tables")
    ]

    success_count = 0
    for sql_file, description in migrations:
        if sql_file.exists():
            if execute_sql_file(conn, sql_file, description):
                success_count += 1
        else:
            print(f"   ⚠️  Migration file not found: {sql_file}")

    conn.close()

    print(f"\n📊 Table Creation Summary: {success_count}/{len(migrations)} completed")
    return success_count == len(migrations)

def insert_mock_data():
    """Insert all mock data using mockup files"""
    print("\n📦 INSERTING MOCK DATA")
    print("=" * 60)

    setup_dir = Path(__file__).parent

    # Execute mockup scripts in dependency order
    mockup_scripts = [
        (setup_dir / "mockup_master_data.py", "Inserting master data"),
        (setup_dir / "mockup_core_data.py", "Inserting core data"),
        (setup_dir / "mockup_project_data.py", "Inserting project data")
    ]

    success_count = 0
    for script_file, description in mockup_scripts:
        if script_file.exists():
            if execute_python_script(script_file, description):
                success_count += 1
        else:
            print(f"   ⚠️  Mockup script not found: {script_file}")

    print(f"\n📊 Data Insertion Summary: {success_count}/{len(mockup_scripts)} completed")
    return success_count == len(mockup_scripts)

def verify_setup():
    """Verify database setup and show statistics"""
    print("\n🔍 VERIFYING DATABASE SETUP")
    print("=" * 60)

    conn = get_db_connection()
    if not conn:
        return False

    try:
        cur = conn.cursor()

        # Check tables exist
        cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name LIKE 'tbl_%'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cur.fetchall()]

        print(f"📋 Database Tables ({len(tables)} found):")
        for table in tables:
            print(f"   ✓ {table}")

        print(f"\n📊 Data Verification:")

        # Count records in each major table
        data_counts = {}
        for table in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                data_counts[table] = count

                # Show counts for main tables
                if table in ['tbl_users', 'tbl_roles', 'tbl_projects', 'tbl_project_tasks', 'tbl_project_epics', 'tbl_project_sprints', 'tbl_project_backlog']:
                    print(f"   • {table}: {count} records")
            except:
                data_counts[table] = 0

        # Show summary
        total_records = sum(data_counts.values())
        print(f"\n📈 Total Records: {total_records}")

        # Check for essential data
        essential_checks = [
            ("tbl_roles", 3, "At least 3 roles should exist"),
            ("tbl_users", 5, "At least 5 users should exist"),
            ("tbl_master_priority", 3, "At least 3 priorities should exist"),
            ("tbl_projects", 1, "At least 1 project should exist")
        ]

        print(f"\n🔍 Essential Data Checks:")
        all_checks_passed = True
        for table, min_count, description in essential_checks:
            count = data_counts.get(table, 0)
            if count >= min_count:
                print(f"   ✅ {description} ({count} found)")
            else:
                print(f"   ❌ {description} ({count} found, minimum {min_count})")
                all_checks_passed = False

        cur.close()
        conn.close()

        if all_checks_passed:
            print(f"\n🎉 Database setup verification completed successfully!")
            print(f"📅 Verification completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"\n⚠️  Database setup has some issues. Please check the data insertion.")

        return all_checks_passed

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        conn.close()
        return False

def main():
    """Main function to handle command line arguments and execute setup"""
    parser = argparse.ArgumentParser(
        description="Planora API Database Setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python setup/setup_planora.py                    # Full setup (tables + data)
    python setup/setup_planora.py --tables-only      # Create tables only
    python setup/setup_planora.py --data-only        # Insert mock data only
    python setup/setup_planora.py --verify           # Verify existing setup

This script provides a clean, organized approach to database setup using:
• Migration files (migrate_*.sql) for table creation
• Mockup files (mockup_*.py) for data insertion
• Automatic verification and reporting
        """
    )

    parser.add_argument(
        '--tables-only',
        action='store_true',
        help='Create database tables only (no mock data)'
    )

    parser.add_argument(
        '--data-only',
        action='store_true',
        help='Insert mock data only (assumes tables exist)'
    )

    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify existing database setup'
    )

    args = parser.parse_args()

    print("🚀 PLANORA API DATABASE SETUP")
    print("=" * 80)
    print("Clean, modular database setup with migration and mockup files")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    success = True

    if args.verify:
        # Verify existing setup
        success = verify_setup()

    elif args.tables_only:
        # Create tables only
        success = create_tables()
        if success:
            verify_setup()

    elif args.data_only:
        # Insert mock data only
        success = insert_mock_data()
        if success:
            verify_setup()

    else:
        # Full setup (default)
        tables_success = create_tables()
        data_success = insert_mock_data() if tables_success else False
        success = tables_success and data_success

        if success:
            verify_setup()

    print("\n" + "=" * 80)
    if success:
        print("🎉 PLANORA DATABASE SETUP COMPLETED SUCCESSFULLY!")
        print("\n💡 Next Steps:")
        print("   1. Start the server: python -m uvicorn app.main:app --reload --port 8000")
        print("   2. Access API docs: http://localhost:8000/docs")
        print("   3. Login credentials:")
        print("      • Super Admin: superadmin@planora.com / super123")
        print("      • Admin: admin@planora.com / admin123")
        print("      • Others: [email] / password123")
    else:
        print("❌ SETUP ENCOUNTERED ERRORS")
        print("Please check the error messages above and try again.")

    print("=" * 80)
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())