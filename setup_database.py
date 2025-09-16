#!/usr/bin/env python3
"""
Database setup script for Planora API
This script will create all database tables and insert mock data
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def check_environment():
    """Check if .env file exists and has required variables"""
    env_file = current_dir / ".env"
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please copy .env.example to .env and configure your database settings")
        return False

    # Read .env file and check for required variables
    with open(env_file, 'r') as f:
        env_content = f.read()

    required_vars = ['DATABASE_URL', 'SECRET_KEY']
    missing_vars = []

    for var in required_vars:
        if var not in env_content or f"{var}=" not in env_content:
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please update your .env file with the missing variables")
        return False

    return True

def setup_database():
    """Main setup function"""
    print("🚀 Setting up Planora API Database...")
    print("=" * 50)

    # Check environment
    if not check_environment():
        return False

    try:
        # Import after path is set
        from insert_mock_data import create_tables_and_insert_data

        # Create tables and insert data
        create_tables_and_insert_data()

        print("\n" + "=" * 50)
        print("🎉 Database setup completed successfully!")
        print("\n📊 Mock Data Summary:")
        print("   • 5 Roles (Super Admin, Admin, Project Manager, Developer, Tester)")
        print("   • 7 Users with different roles")
        print("   • 5 Projects with various statuses")
        print("   • 9 Tasks across different projects")
        print("   • 7 Audit log entries")

        print("\n🔐 Login Credentials:")
        print("   Super Admin: superadmin@planora.com / super123")
        print("   Admin: admin@planora.com / admin123")
        print("   Project Manager: pm@planora.com / pm123")

        print("\n🚀 Next Steps:")
        print("   1. Run: uvicorn main:app --reload")
        print("   2. Open: http://localhost:8000/docs")
        print("   3. Use the login credentials above to test the API")

        return True

    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        print("\nPlease check:")
        print("1. PostgreSQL is running")
        print("2. Database connection settings in .env")
        print("3. Database exists (create 'planora_db' database)")
        return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)