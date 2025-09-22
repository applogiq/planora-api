#!/usr/bin/env python3
"""
Comprehensive Mock Data Setup Script for Planora API
This script coordinates the insertion of all existing mock data:
- Users, Roles, and Audit Logs
- Projects, Epics, Sprints, Tasks
- Master data (Priorities, Statuses, Types, Methodologies)
"""

import sys
import os
from pathlib import Path
import io

# Unicode handling is done automatically in Python 3

# Add the current directory to Python path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.db.database import Base

def create_tables_and_insert_data():
    """Create all tables and insert comprehensive mock data"""

    print("=" * 80)
    print("🚀 PLANORA API - COMPREHENSIVE MOCK DATA SETUP")
    print("=" * 80)
    print("This script will set up the complete Planora system with mock data:")
    print("  1. Users, Roles & Audit Logs (25 users across different roles)")
    print("  2. Master Data (Priorities, Statuses, Types, Methodologies)")
    print("  3. Projects (20 projects across different domains)")
    print("  4. Epics (10 comprehensive epics)")
    print("  5. Sprints (6 sprints with different statuses)")
    print("  6. Tasks (30 tasks across different statuses)")
    print("\n" + "=" * 80)

    try:
        # Create all tables first
        print("\n🔧 Creating all database tables...")
        Base.metadata.create_all(bind=engine)
        print("[SUCCESS] All tables created successfully!")

        # Import and run user data setup
        print("\n🔄 STEP 1: Setting up Users, Roles & Audit Logs...")
        try:
            from insert_user_data import create_user_tables_and_insert_data
            create_user_tables_and_insert_data()
        except Exception as e:
            print(f"[WARNING] User data setup encountered issues: {e}")
            print("Continuing with project data setup...")

        # Import and run project data setup
        print("\n🔄 STEP 2: Setting up Projects & Master Data...")
        try:
            from insert_all_project_data import create_all_project_tables_and_insert_data
            create_all_project_tables_and_insert_data()
        except Exception as e:
            print(f"[WARNING] Project data setup encountered issues: {e}")
            print("Continuing with file management data setup...")

        # Import and run file management data setup
        print("\n🔄 STEP 3: Setting up File Management Data...")
        try:
            from insert_file_data import insert_file_management_data
            insert_file_management_data()
        except Exception as e:
            print(f"[WARNING] File management data setup encountered issues: {e}")
            print("Mock data setup completed with some warnings...")

        # Final summary
        print("\n" + "=" * 80)
        print("🎉 COMPLETE PLANORA MOCK DATA SETUP FINISHED!")
        print("=" * 80)

        # Get counts from database
        db = SessionLocal()
        try:
            from app.features.users.models import User
            from app.features.roles.models import Role
            from app.features.projects.models import Project
            from app.features.stories.models import Story
            from app.features.sprints.models import Sprint
            from app.features.epics.models import Epic
            from app.features.audit_logs.models import AuditLog
            from app.features.files.models import File, FileFolder, StorageQuota

            user_count = db.query(User).count()
            role_count = db.query(Role).count()
            project_count = db.query(Project).count()
            story_count = db.query(Story).count()
            sprint_count = db.query(Sprint).count()
            epic_count = db.query(Epic).count()
            audit_count = db.query(AuditLog).count()
            file_count = db.query(File).count()
            folder_count = db.query(FileFolder).count()
            quota_count = db.query(StorageQuota).count()

            print(f"\n📊 FINAL DATABASE SUMMARY:")
            print(f"   • {role_count} Roles")
            print(f"   • {user_count} Users")
            print(f"   • {project_count} Projects")
            print(f"   • {epic_count} Epics")
            print(f"   • {sprint_count} Sprints")
            print(f"   • {story_count} Stories")
            print(f"   • {file_count} Files")
            print(f"   • {folder_count} File Folders")
            print(f"   • {quota_count} Storage Quotas")
            print(f"   • {audit_count} Audit Log Entries")

        except Exception as e:
            print(f"[INFO] Could not get database counts: {e}")
        finally:
            db.close()

        print("\n🚀 PLANORA API IS READY!")
        print("\n💡 NEXT STEPS:")
        print("   1. Start the server: uvicorn main:app --reload --port 8000")
        print("   2. Access API docs: http://localhost:8000/docs")
        print("   3. Login credentials:")
        print("      • Super Admin: superadmin@planora.com / super123")
        print("      • Admin: admin@planora.com / admin123")
        print("      • All others: [email] / password123")
        print("\n🌟 AVAILABLE API ENDPOINTS:")
        print("   • Users: /api/v1/users/")
        print("   • Projects: /api/v1/projects/")
        print("   • Tasks: /api/v1/tasks/")
        print("   • Sprints: /api/v1/sprints/")
        print("   • Epics: /api/v1/epics/")
        print("   • Audit Logs: /api/v1/audit-logs/")
        print("   • Masters: /api/v1/masters/")
        print("\n📊 DASHBOARD FEATURES:")
        print("   • Kanban Boards: /api/v1/tasks/board/kanban")
        print("   • Project Stats: /api/v1/projects/stats/overview")
        print("   • Sprint Analytics: /api/v1/sprints/stats/overview")

        print("\n" + "=" * 80)

    except Exception as e:
        print(f"\n❌ [ERROR] Failed to set up mock data: {e}")
        print("Please check the error details above and try again.")
        print("You can also run individual scripts:")
        print("  • python setup/insert_user_data.py")
        print("  • python setup/insert_all_project_data.py")
        print("=" * 80)

if __name__ == "__main__":
    create_tables_and_insert_data()