#!/usr/bin/env python3
"""
Mockup data for core tables (roles, users, audit logs)
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import SessionLocal
from app.core.security import get_password_hash
from datetime import datetime, timedelta
import uuid

def insert_core_data():
    """Insert mock data for core tables"""

    db = SessionLocal()

    try:
        print("🔄 Inserting core data (roles, users, audit logs)...")

        # Insert data in dependency order
        insert_roles(db)
        insert_users(db)
        insert_audit_logs(db)

        db.commit()
        print("✅ Core data inserted successfully!")

    except Exception as e:
        print(f"❌ Error inserting core data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def insert_roles(db: Session):
    """Insert role mock data"""

    # Clear existing data
    db.execute(text("DELETE FROM tbl_roles"))

    roles_data = [
        {
            "id": "role_super_admin",
            "name": "Super Admin",
            "description": "Full system access with all permissions",
            "permissions": ["*"],
            "is_active": True
        },
        {
            "id": "role_admin",
            "name": "Administrator",
            "description": "Administrative access to most system functions",
            "permissions": ["user:*", "project:*", "task:*", "audit:read"],
            "is_active": True
        },
        {
            "id": "role_project_manager",
            "name": "Project Manager",
            "description": "Manage projects, tasks, and team assignments",
            "permissions": ["project:*", "task:*", "user:read", "sprint:*", "epic:*"],
            "is_active": True
        },
        {
            "id": "role_developer",
            "name": "Developer",
            "description": "Work on tasks and update project progress",
            "permissions": ["task:read", "task:update", "project:read", "sprint:read"],
            "is_active": True
        },
        {
            "id": "role_tester",
            "name": "Tester",
            "description": "Test features and report bugs",
            "permissions": ["task:read", "task:update", "project:read", "bug:*"],
            "is_active": True
        }
    ]

    for role_data in roles_data:
        db.execute(text("""
            INSERT INTO tbl_roles (id, name, description, permissions, is_active, created_at)
            VALUES (:id, :name, :description, :permissions, :is_active, NOW())
        """), {
            "id": role_data["id"],
            "name": role_data["name"],
            "description": role_data["description"],
            "permissions": role_data["permissions"],
            "is_active": role_data["is_active"]
        })

    print(f"   ✓ Inserted {len(roles_data)} roles")

def insert_users(db: Session):
    """Insert user mock data"""

    # Clear existing data
    db.execute(text("DELETE FROM tbl_users"))

    users_data = [
        # Super Admin
        {
            "id": "a1b2c3d4-5e6f-7890-abcd-ef1234567890",
            "email": "superadmin@planora.com",
            "password": get_password_hash("super123"),
            "name": "System Administrator",
            "role_id": "role_super_admin",
            "avatar": "/public/user-profile/default.png",
            "department": "IT",
            "skills": ["System Administration", "Security", "Database Management"],
            "phone": "+1-555-0001",
            "timezone": "UTC",
            "is_active": True
        },
        # Admin
        {
            "id": "b2c3d4e5-6f78-9012-bcde-f23456789012",
            "email": "admin@planora.com",
            "password": get_password_hash("admin123"),
            "name": "John Doe",
            "role_id": "role_admin",
            "avatar": "/public/user-profile/default.png",
            "department": "Management",
            "skills": ["Project Management", "Team Leadership", "Strategy"],
            "phone": "+1-555-0002",
            "timezone": "America/New_York",
            "is_active": True
        },
        # Project Managers
        {
            "id": "c3d4e5f6-7890-1234-cdef-345678901234",
            "email": "jane.smith@planora.com",
            "password": get_password_hash("password123"),
            "name": "Jane Smith",
            "role_id": "role_project_manager",
            "avatar": "/public/user-profile/default.png",
            "department": "Project Management",
            "skills": ["Agile", "Scrum", "Risk Management"],
            "phone": "+1-555-0003",
            "timezone": "America/Los_Angeles",
            "is_active": True
        },
        {
            "id": "d4e5f6g7-8901-2345-def0-456789012345",
            "email": "bob.wilson@planora.com",
            "password": get_password_hash("password123"),
            "name": "Bob Wilson",
            "role_id": "role_project_manager",
            "avatar": "/public/user-profile/default.png",
            "department": "Project Management",
            "skills": ["Waterfall", "Budget Management", "Stakeholder Management"],
            "phone": "+1-555-0004",
            "timezone": "America/Chicago",
            "is_active": True
        },
        # Developers
        {
            "id": "e5f6g7h8-9012-3456-ef01-567890123456",
            "email": "alice.brown@planora.com",
            "password": get_password_hash("password123"),
            "name": "Alice Brown",
            "role_id": "role_developer",
            "avatar": "/public/user-profile/default.png",
            "department": "Engineering",
            "skills": ["Python", "FastAPI", "PostgreSQL", "React"],
            "phone": "+1-555-0005",
            "timezone": "America/New_York",
            "is_active": True
        },
        {
            "id": "f6g7h8i9-0123-4567-f012-678901234567",
            "email": "charlie.davis@planora.com",
            "password": get_password_hash("password123"),
            "name": "Charlie Davis",
            "role_id": "role_developer",
            "avatar": "/public/user-profile/default.png",
            "department": "Engineering",
            "skills": ["JavaScript", "Node.js", "MongoDB", "Vue.js"],
            "phone": "+1-555-0006",
            "timezone": "Europe/London",
            "is_active": True
        },
        {
            "id": "g7h8i9j0-1234-5678-0123-789012345678",
            "email": "diana.miller@planora.com",
            "password": get_password_hash("password123"),
            "name": "Diana Miller",
            "role_id": "role_developer",
            "avatar": "/public/user-profile/default.png",
            "department": "Engineering",
            "skills": ["Java", "Spring Boot", "MySQL", "Angular"],
            "phone": "+1-555-0007",
            "timezone": "Asia/Tokyo",
            "is_active": True
        },
        # Testers
        {
            "id": "h8i9j0k1-2345-6789-1234-890123456789",
            "email": "erik.johnson@planora.com",
            "password": get_password_hash("password123"),
            "name": "Erik Johnson",
            "role_id": "role_tester",
            "avatar": "/public/user-profile/default.png",
            "department": "Quality Assurance",
            "skills": ["Manual Testing", "Automated Testing", "Selenium", "JIRA"],
            "phone": "+1-555-0008",
            "timezone": "America/Denver",
            "is_active": True
        },
        {
            "id": "i9j0k1l2-3456-789a-2345-90123456789a",
            "email": "sophia.garcia@planora.com",
            "password": get_password_hash("password123"),
            "name": "Sophia Garcia",
            "role_id": "role_tester",
            "avatar": "/public/user-profile/default.png",
            "department": "Quality Assurance",
            "skills": ["API Testing", "Performance Testing", "Cypress", "TestRail"],
            "phone": "+1-555-0009",
            "timezone": "America/Mexico_City",
            "is_active": True
        },
        # Additional Developers
        {
            "id": "j0k1l2m3-4567-89ab-3456-0123456789ab",
            "email": "michael.chen@planora.com",
            "password": get_password_hash("password123"),
            "name": "Michael Chen",
            "role_id": "role_developer",
            "avatar": "/public/user-profile/default.png",
            "department": "Engineering",
            "skills": ["C#", ".NET Core", "SQL Server", "Blazor"],
            "phone": "+1-555-0010",
            "timezone": "Australia/Sydney",
            "is_active": True
        }
    ]

    for user_data in users_data:
        db.execute(text("""
            INSERT INTO tbl_users (id, email, password, name, role_id, avatar, department, skills, phone, timezone, is_active, created_at)
            VALUES (:id, :email, :password, :name, :role_id, :avatar, :department, :skills, :phone, :timezone, :is_active, NOW())
        """), {
            "id": user_data["id"],
            "email": user_data["email"],
            "password": user_data["password"],
            "name": user_data["name"],
            "role_id": user_data["role_id"],
            "avatar": user_data.get("avatar", "/public/user-profile/default.png"),
            "department": user_data["department"],
            "skills": user_data["skills"],
            "phone": user_data["phone"],
            "timezone": user_data["timezone"],
            "is_active": user_data["is_active"]
        })

    print(f"   ✓ Inserted {len(users_data)} users")

def insert_audit_logs(db: Session):
    """Insert audit log mock data"""

    # Clear existing data
    db.execute(text("DELETE FROM tbl_audit_logs"))

    audit_logs = [
        {
            "id": str(uuid.uuid4()),
            "user_id": "a1b2c3d4-5e6f-7890-abcd-ef1234567890",
            "user_name": "System Administrator",
            "action": "LOGIN",
            "resource": "Authentication",
            "details": "User logged in successfully",
            "timestamp": datetime.now() - timedelta(days=1),
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "status": "success"
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": "b2c3d4e5-6f78-9012-bcde-f23456789012",
            "user_name": "John Doe",
            "action": "CREATE",
            "resource": "Project",
            "details": "Created new project: Mobile Banking App",
            "timestamp": datetime.now() - timedelta(hours=12),
            "ip_address": "192.168.1.101",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "status": "success"
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": "c3d4e5f6-7890-1234-cdef-345678901234",
            "user_name": "Jane Smith",
            "action": "UPDATE",
            "resource": "Task",
            "details": "Updated task status to In Progress",
            "timestamp": datetime.now() - timedelta(hours=6),
            "ip_address": "192.168.1.102",
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "status": "success"
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": "e5f6g7h8-9012-3456-ef01-567890123456",
            "user_name": "Alice Brown",
            "action": "UPDATE",
            "resource": "User Profile",
            "details": "Updated profile picture",
            "timestamp": datetime.now() - timedelta(hours=3),
            "ip_address": "192.168.1.103",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "status": "success"
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": "h8i9j0k1-2345-6789-1234-890123456789",
            "user_name": "Erik Johnson",
            "action": "CREATE",
            "resource": "Bug Report",
            "details": "Created bug report for login issue",
            "timestamp": datetime.now() - timedelta(hours=1),
            "ip_address": "192.168.1.104",
            "user_agent": "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15",
            "status": "success"
        }
    ]

    for log_data in audit_logs:
        db.execute(text("""
            INSERT INTO tbl_audit_logs (id, user_id, user_name, action, resource, details, timestamp, ip_address, user_agent, status)
            VALUES (:id, :user_id, :user_name, :action, :resource, :details, :timestamp, :ip_address, :user_agent, :status)
        """), {
            "id": log_data["id"],
            "user_id": log_data["user_id"],
            "user_name": log_data["user_name"],
            "action": log_data["action"],
            "resource": log_data["resource"],
            "details": log_data["details"],
            "timestamp": log_data["timestamp"],
            "ip_address": log_data["ip_address"],
            "user_agent": log_data["user_agent"],
            "status": log_data["status"]
        })

    print(f"   ✓ Inserted {len(audit_logs)} audit logs")

if __name__ == "__main__":
    insert_core_data()