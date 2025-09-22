#!/usr/bin/env python3
"""
Insert File Management mock data
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.features.files.models import File, FileFolder, StorageQuota
from app.db.database import Base
from datetime import datetime, timedelta
import uuid

def insert_storage_quotas(db: Session):
    """Insert storage quota mock data"""
    quotas_data = [
        {
            "id": "quota_global",
            "entity_type": "global",
            "entity_id": "system",
            "total_quota_bytes": 1073741824000,  # 1TB
            "used_bytes": 52428800000,  # 50GB used
            "max_files": 100000,
            "current_files": 1245
        },
        {
            "id": "quota_project_tech_modernization",
            "entity_type": "project",
            "entity_id": "prj_tech_modernization",
            "total_quota_bytes": 10737418240,  # 10GB
            "used_bytes": 2147483648,  # 2GB used
            "max_files": 5000,
            "current_files": 156
        },
        {
            "id": "quota_project_mobile_app",
            "entity_type": "project",
            "entity_id": "prj_mobile_app",
            "total_quota_bytes": 5368709120,  # 5GB
            "used_bytes": 1073741824,  # 1GB used
            "max_files": 2500,
            "current_files": 89
        },
        {
            "id": "quota_user_john_doe",
            "entity_type": "user",
            "entity_id": "user_john_doe",
            "total_quota_bytes": 1073741824,  # 1GB
            "used_bytes": 104857600,  # 100MB used
            "max_files": 500,
            "current_files": 23
        }
    ]

    for quota_data in quotas_data:
        existing_quota = db.query(StorageQuota).filter(StorageQuota.id == quota_data["id"]).first()
        if not existing_quota:
            quota = StorageQuota(**quota_data)
            db.add(quota)
            print(f"    ✅ Created storage quota: {quota_data['entity_type']} - {quota_data['entity_id']}")

    db.commit()

def insert_file_folders(db: Session):
    """Insert file folder mock data"""
    folders_data = [
        {
            "id": "folder_tech_docs",
            "name": "Technical Documentation",
            "description": "Technical specifications and documentation",
            "entity_type": "project",
            "entity_id": "prj_tech_modernization",
            "parent_folder_id": None,
            "created_by_id": "user_john_doe",
            "created_by_name": "John Doe"
        },
        {
            "id": "folder_tech_wireframes",
            "name": "Wireframes",
            "description": "UI/UX wireframes and mockups",
            "entity_type": "project",
            "entity_id": "prj_tech_modernization",
            "parent_folder_id": "folder_tech_docs",
            "created_by_id": "user_jane_smith",
            "created_by_name": "Jane Smith"
        },
        {
            "id": "folder_mobile_assets",
            "name": "Mobile App Assets",
            "description": "Images, icons, and design assets for mobile app",
            "entity_type": "project",
            "entity_id": "prj_mobile_app",
            "parent_folder_id": None,
            "created_by_id": "user_alice_johnson",
            "created_by_name": "Alice Johnson"
        },
        {
            "id": "folder_epic_auth_specs",
            "name": "Authentication Specs",
            "description": "Authentication system specifications",
            "entity_type": "epic",
            "entity_id": "epic_user_auth",
            "parent_folder_id": None,
            "created_by_id": "user_bob_wilson",
            "created_by_name": "Bob Wilson"
        }
    ]

    for folder_data in folders_data:
        existing_folder = db.query(FileFolder).filter(FileFolder.id == folder_data["id"]).first()
        if not existing_folder:
            folder = FileFolder(**folder_data)
            db.add(folder)
            print(f"    ✅ Created file folder: {folder_data['name']}")

    db.commit()

def insert_files(db: Session):
    """Insert file mock data"""
    files_data = [
        {
            "id": "file_tech_requirements",
            "filename": "tech_requirements_v2_1.pdf",
            "original_filename": "Technical Requirements v2.1.pdf",
            "file_path": "public/project/prj_tech_modernization/tech_requirements_v2_1.pdf",
            "file_size": 2048576,  # 2MB
            "content_type": "application/pdf",
            "file_extension": ".pdf",
            "category": "document",
            "entity_type": "project",
            "entity_id": "prj_tech_modernization",
            "entity_title": "Technology Platform Modernization",
            "description": "Comprehensive technical requirements document",
            "tags": "requirements,technical,specifications",
            "is_public": False,
            "uploaded_by_id": "user_john_doe",
            "uploaded_by_name": "John Doe"
        },
        {
            "id": "file_mobile_mockup",
            "filename": "mobile_app_mockup_final.png",
            "original_filename": "Mobile App Mockup - Final Version.png",
            "file_path": "public/project/prj_mobile_app/mobile_app_mockup_final.png",
            "file_size": 5242880,  # 5MB
            "content_type": "image/png",
            "file_extension": ".png",
            "category": "image",
            "entity_type": "project",
            "entity_id": "prj_mobile_app",
            "entity_title": "Mobile Application Development",
            "description": "Final design mockup for mobile application",
            "tags": "mockup,design,mobile,ui",
            "is_public": True,
            "uploaded_by_id": "user_alice_johnson",
            "uploaded_by_name": "Alice Johnson"
        },
        {
            "id": "file_auth_wireframe",
            "filename": "login_wireframe_v3.pdf",
            "original_filename": "Login Screen Wireframe v3.pdf",
            "file_path": "public/epic/epic_user_auth/login_wireframe_v3.pdf",
            "file_size": 1048576,  # 1MB
            "content_type": "application/pdf",
            "file_extension": ".pdf",
            "category": "document",
            "entity_type": "epic",
            "entity_id": "epic_user_auth",
            "entity_title": "User Authentication System",
            "description": "Wireframe for login screen design",
            "tags": "wireframe,login,authentication,ui",
            "is_public": False,
            "uploaded_by_id": "user_jane_smith",
            "uploaded_by_name": "Jane Smith"
        }
    ]

    for file_data in files_data:
        existing_file = db.query(File).filter(File.id == file_data["id"]).first()
        if not existing_file:
            file = File(**file_data)
            db.add(file)
            print(f"    ✅ Created file: {file_data['original_filename']}")

    db.commit()

def insert_file_management_data():
    """Insert all file management mock data"""
    print("\n📁 Inserting File Management Mock Data...")

    with SessionLocal() as db:
        try:
            print("\n  📊 Inserting Storage Quotas...")
            insert_storage_quotas(db)

            print("\n  📂 Inserting File Folders...")
            insert_file_folders(db)

            print("\n  📄 Inserting Files...")
            insert_files(db)

            print("\n  ✅ File management mock data inserted successfully!")
            return True

        except Exception as e:
            print(f"\n  ❌ Error inserting file management data: {str(e)}")
            db.rollback()
            return False

def main():
    """Main function to run file management data insertion"""
    print("=" * 80)
    print("📁 PLANORA API - FILE MANAGEMENT MOCK DATA INSERTION")
    print("=" * 80)

    success = insert_file_management_data()

    if success:
        print("\n" + "=" * 80)
        print("✅ FILE MANAGEMENT MOCK DATA INSERTION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ FILE MANAGEMENT MOCK DATA INSERTION FAILED!")
        print("=" * 80)
        sys.exit(1)

if __name__ == "__main__":
    main()