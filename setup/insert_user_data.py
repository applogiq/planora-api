#!/usr/bin/env python3
"""
Insert User, Role, and AuditLog mock data
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.features.users.models import User
from app.features.roles.models import Role
from app.features.audit_logs.models import AuditLog
from app.db.database import Base
from app.core.security import get_password_hash
from datetime import datetime, timedelta
import uuid

def insert_roles(db: Session):
    """Insert role mock data"""
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
            "description": "System administration with user management",
            "permissions": ["user:read", "user:write", "user:delete", "role:read", "role:write", "project:read", "project:write", "settings:read", "settings:write"],
            "is_active": True
        },
        {
            "id": "role_project_manager",
            "name": "Project Manager",
            "description": "Project management and team coordination",
            "permissions": ["project:read", "project:write", "task:read", "task:write", "team:read", "report:read", "customer:read"],
            "is_active": True
        },
        {
            "id": "role_developer",
            "name": "Developer",
            "description": "Development tasks and project participation",
            "permissions": ["project:read", "task:read", "task:write", "report:read"],
            "is_active": True
        },
        {
            "id": "role_tester",
            "name": "Tester",
            "description": "Quality assurance and testing activities",
            "permissions": ["project:read", "task:read", "task:write", "report:read"],
            "is_active": True
        }
    ]

    for role_data in roles_data:
        db_role = Role(**role_data)
        db.add(db_role)

    db.commit()
    print(f"[SUCCESS] Inserted {len(roles_data)} roles")

def insert_users(db: Session):
    """Insert user mock data"""
    users_data = [
        {
            "id": "f0f0f9ae-49c4-42c6-bd4a-a7c83124015f",
            "email": "superadmin@planora.com",
            "password": get_password_hash("super123"),
            "name": "Super Administrator",
            "role_id": "role_super_admin",
            "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=1),
            "department": "Management",
            "skills": ["Leadership", "Strategy", "Project Management"],
            "phone": "+1 (555) 000-0001",
            "timezone": "America/New_York"
        },
        {
            "id": "a1b2c3d4-5e6f-7890-abcd-ef1234567890",
            "email": "admin@planora.com",
            "password": get_password_hash("admin123"),
            "name": "System Administrator",
            "role_id": "role_admin",
            "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(minutes=30),
            "department": "IT",
            "skills": ["System Administration", "Security", "DevOps"],
            "phone": "+1 (555) 000-0002",
            "timezone": "America/New_York"
        },
        {
            "id": "b2c3d4e5-6f78-9012-bcde-f23456789012",
            "email": "john.doe@planora.com",
            "password": get_password_hash("password123"),
            "name": "John Doe",
            "role_id": "role_project_manager",
            "avatar": "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=2),
            "department": "Project Management",
            "skills": ["Agile", "Scrum", "Risk Management"],
            "phone": "+1 (555) 000-0003",
            "timezone": "America/Los_Angeles"
        },
        {
            "id": "c3d4e5f6-7890-1234-cdef-345678901234",
            "email": "jane.smith@planora.com",
            "password": get_password_hash("password123"),
            "name": "Jane Smith",
            "role_id": "role_developer",
            "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=3),
            "department": "Engineering",
            "skills": ["React", "Node.js", "TypeScript", "Python"],
            "phone": "+1 (555) 000-0004",
            "timezone": "America/Chicago"
        },
        {
            "id": "d4e5f6g7-8901-2345-def0-456789012345",
            "email": "bob.wilson@planora.com",
            "password": get_password_hash("password123"),
            "name": "Bob Wilson",
            "role_id": "role_tester",
            "avatar": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(days=1),
            "department": "Quality Assurance",
            "skills": ["Manual Testing", "Automation", "Selenium", "Jest"],
            "phone": "+1 (555) 000-0005",
            "timezone": "America/Denver"
        },
        {
            "id": "e5f6g7h8-9012-3456-ef01-567890123456",
            "email": "alice.brown@planora.com",
            "password": get_password_hash("password123"),
            "name": "Alice Brown",
            "role_id": "role_developer",
            "avatar": "https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=5),
            "department": "Engineering",
            "skills": ["Java", "Spring Boot", "MySQL", "Docker"],
            "phone": "+1 (555) 000-0006",
            "timezone": "America/New_York"
        },
        {
            "id": "f6g7h8i9-0123-4567-f012-678901234567",
            "email": "charlie.davis@planora.com",
            "password": get_password_hash("password123"),
            "name": "Charlie Davis",
            "role_id": "role_developer",
            "avatar": "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=4),
            "department": "Engineering",
            "skills": ["React", "CSS", "Figma", "UX/UI Design"],
            "phone": "+1 (555) 000-0007",
            "timezone": "America/Los_Angeles"
        },
        {
            "id": "g7h8i9j0-1234-5678-0123-789012345678",
            "email": "diana.miller@planora.com",
            "password": get_password_hash("password123"),
            "name": "Diana Miller",
            "role_id": "role_project_manager",
            "avatar": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=6),
            "department": "Marketing",
            "skills": ["Marketing Strategy", "Content Creation", "Analytics"],
            "phone": "+1 (555) 000-0008",
            "timezone": "America/Denver"
        },
        {
            "id": "h8i9j0k1-2345-6789-1234-890123456789",
            "email": "erik.johnson@planora.com",
            "password": get_password_hash("password123"),
            "name": "Erik Johnson",
            "role_id": "role_developer",
            "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=8),
            "department": "Engineering",
            "skills": ["Python", "Django", "Docker"],
            "phone": "+1 (555) 000-0009",
            "timezone": "America/Los_Angeles"
        },
        {
            "id": "i9j0k1l2-3456-789a-2345-90123456789a",
            "email": "sophia.garcia@planora.com",
            "password": get_password_hash("password123"),
            "name": "Sophia Garcia",
            "role_id": "role_developer",
            "avatar": "https://images.unsplash.com/photo-1537511446984-935f663eb1f4?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=12),
            "department": "Design",
            "skills": ["Graphic Design", "Branding", "Illustration"],
            "phone": "+1 (555) 000-0010",
            "timezone": "America/Chicago"
        },
        {
            "id": "j0k1l2m3-4567-89ab-3456-0123456789ab",
            "email": "michael.chen@planora.com",
            "password": get_password_hash("password123"),
            "name": "Michael Chen",
            "role_id": "role_developer",
            "avatar": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=1),
            "department": "Engineering",
            "skills": ["React", "TypeScript", "GraphQL"],
            "phone": "+1 (555) 000-0011",
            "timezone": "America/New_York"
        },
        {
            "id": "k1l2m3n4-5678-9abc-4567-123456789abc",
            "email": "emma.rodriguez@planora.com",
            "password": get_password_hash("password123"),
            "name": "Emma Rodriguez",
            "role_id": "role_project_manager",
            "avatar": "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=3),
            "department": "Operations",
            "skills": ["Operations Management", "Process Improvement", "Data Analysis"],
            "phone": "+1 (555) 000-0012",
            "timezone": "America/Los_Angeles"
        },
        {
            "id": "l2m3n4o5-6789-abcd-5678-23456789abcd",
            "email": "david.thompson@planora.com",
            "password": get_password_hash("password123"),
            "name": "David Thompson",
            "role_id": "role_developer",
            "avatar": "https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=5),
            "department": "Engineering",
            "skills": ["C#", ".NET", "Azure"],
            "phone": "+1 (555) 000-0013",
            "timezone": "America/Chicago"
        },
        {
            "id": "m3n4o5p6-789a-bcde-6789-3456789abcde",
            "email": "olivia.white@planora.com",
            "password": get_password_hash("password123"),
            "name": "Olivia White",
            "role_id": "role_developer",
            "avatar": "https://images.unsplash.com/photo-1507591064344-4c6ce005b128?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=7),
            "department": "Design",
            "skills": ["Product Design", "User Research", "Prototyping"],
            "phone": "+1 (555) 000-0014",
            "timezone": "America/Denver"
        },
        {
            "id": "n4o5p6q7-89ab-cdef-789a-456789abcdef",
            "email": "ryan.martinez@planora.com",
            "password": get_password_hash("password123"),
            "name": "Ryan Martinez",
            "role_id": "role_developer",
            "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=9),
            "department": "Engineering",
            "skills": ["PHP", "Laravel", "MySQL"],
            "phone": "+1 (555) 000-0015",
            "timezone": "America/New_York"
        },
        {
            "id": "o5p6q7r8-9abc-def0-89ab-56789abcdef0",
            "email": "sarah.taylor@planora.com",
            "password": get_password_hash("password123"),
            "name": "Sarah Taylor",
            "role_id": "role_project_manager",
            "avatar": "https://images.unsplash.com/photo-1522556189639-b150ed9c4330?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=11),
            "department": "Product",
            "skills": ["Product Management", "Market Research", "Strategy"],
            "phone": "+1 (555) 000-0016",
            "timezone": "America/Los_Angeles"
        },
        {
            "id": "p6q7r8s9-abcd-ef01-9abc-6789abcdef01",
            "email": "james.anderson@planora.com",
            "password": get_password_hash("password123"),
            "name": "James Anderson",
            "role_id": "role_developer",
            "avatar": "https://images.unsplash.com/photo-1541101767792-f9b2b1c4f127?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=2),
            "department": "Engineering",
            "skills": ["Go", "Kubernetes", "Microservices"],
            "phone": "+1 (555) 000-0017",
            "timezone": "America/Chicago"
        },
        {
            "id": "q7r8s9t0-bcde-f012-abcd-789abcdef012",
            "email": "lisa.jackson@planora.com",
            "password": get_password_hash("password123"),
            "name": "Lisa Jackson",
            "role_id": "role_developer",
            "avatar": "https://images.unsplash.com/photo-1493666438817-866a91353ca9?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=4),
            "department": "Design",
            "skills": ["Motion Graphics", "Video Editing", "Animation"],
            "phone": "+1 (555) 000-0018",
            "timezone": "America/Denver"
        },
        {
            "id": "r8s9t0u1-cdef-0123-bcde-89abcdef0123",
            "email": "kevin.harris@planora.com",
            "password": get_password_hash("password123"),
            "name": "Kevin Harris",
            "role_id": "role_developer",
            "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=6),
            "department": "Engineering",
            "skills": ["Ruby", "Rails", "PostgreSQL"],
            "phone": "+1 (555) 000-0019",
            "timezone": "America/New_York"
        },
        {
            "id": "s9t0u1v2-def0-1234-cdef-9abcdef01234",
            "email": "natalie.clark@planora.com",
            "password": get_password_hash("password123"),
            "name": "Natalie Clark",
            "role_id": "role_project_manager",
            "avatar": "https://images.unsplash.com/photo-1558222218-b7b54eede3f3?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=8),
            "department": "Quality Assurance",
            "skills": ["Quality Management", "Testing Strategy", "Automation"],
            "phone": "+1 (555) 000-0020",
            "timezone": "America/Los_Angeles"
        },
        {
            "id": "t0u1v2w3-ef01-2345-def0-abcdef012345",
            "email": "daniel.lewis@planora.com",
            "password": get_password_hash("password123"),
            "name": "Daniel Lewis",
            "role_id": "role_developer",
            "avatar": "https://images.unsplash.com/photo-1606115174399-c9b31c4b24bb?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=10),
            "department": "Engineering",
            "skills": ["Flutter", "Dart", "Mobile Development"],
            "phone": "+1 (555) 000-0021",
            "timezone": "America/Chicago"
        },
        {
            "id": "u1v2w3x4-f012-3456-ef01-bcdef0123456",
            "email": "maria.gonzalez@planora.com",
            "password": get_password_hash("password123"),
            "name": "Maria Gonzalez",
            "role_id": "role_tester",
            "avatar": "https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=12),
            "department": "External",
            "skills": ["Business Analysis", "Requirements Gathering", "Communication"],
            "phone": "+1 (555) 000-0022",
            "timezone": "America/Denver"
        },
        {
            "id": "v2w3x4y5-0123-4567-f012-cdef01234567",
            "email": "alex.walker@planora.com",
            "password": get_password_hash("password123"),
            "name": "Alex Walker",
            "role_id": "role_developer",
            "avatar": "https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=1),
            "department": "Engineering",
            "skills": ["Vue.js", "Nuxt.js", "Tailwind CSS"],
            "phone": "+1 (555) 000-0023",
            "timezone": "America/New_York"
        },
        {
            "id": "w3x4y5z6-1234-5678-0123-def012345678",
            "email": "grace.moore@planora.com",
            "password": get_password_hash("password123"),
            "name": "Grace Moore",
            "role_id": "role_developer",
            "avatar": "https://images.unsplash.com/photo-1599566150163-29194dcaad36?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=3),
            "department": "Design",
            "skills": ["Design Systems", "Accessibility", "User Testing"],
            "phone": "+1 (555) 000-0024",
            "timezone": "America/Los_Angeles"
        },
        {
            "id": "x4y5z6a7-2345-6789-1234-ef0123456789",
            "email": "chris.taylor@planora.com",
            "password": get_password_hash("password123"),
            "name": "Chris Taylor",
            "role_id": "role_developer",
            "avatar": "https://images.unsplash.com/photo-1619895862022-09114b41f16f?w=150&h=150&fit=crop&crop=face",
            "is_active": True,
            "last_login": datetime.now() - timedelta(hours=5),
            "department": "Engineering",
            "skills": ["Swift", "iOS Development", "CoreData"],
            "phone": "+1 (555) 000-0025",
            "timezone": "America/Chicago"
        }
    ]

    for user_data in users_data:
        db_user = User(**user_data)
        db.add(db_user)

    db.commit()
    print(f"[SUCCESS] Inserted {len(users_data)} users")

def insert_audit_logs(db: Session):
    """Insert audit log mock data"""
    audit_logs_data = [
        {
            "id": "audit_001",
            "user_id": "a1b2c3d4-5e6f-7890-abcd-ef1234567890",
            "user_name": "System Administrator",
            "action": "LOGIN",
            "resource": "Authentication",
            "details": "Successful login from web interface",
            "timestamp": datetime.now() - timedelta(minutes=30),
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "status": "success"
        },
        {
            "id": "audit_002",
            "user_id": "b2c3d4e5-6f78-9012-bcde-f23456789012",
            "user_name": "Project Manager",
            "action": "CREATE",
            "resource": "Project",
            "details": "Created new project: Mobile Banking App",
            "timestamp": datetime.now() - timedelta(hours=2),
            "ip_address": "192.168.1.101",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "status": "success"
        },
        {
            "id": "audit_003",
            "user_id": "c3d4e5f6-7890-1234-cdef-345678901234",
            "user_name": "Senior Developer",
            "action": "UPDATE",
            "resource": "Task",
            "details": "Updated task status from 'In Progress' to 'Done'",
            "timestamp": datetime.now() - timedelta(hours=3),
            "ip_address": "192.168.1.102",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "status": "success"
        },
        {
            "id": "audit_004",
            "user_id": "d4e5f6g7-8901-2345-def0-456789012345",
            "user_name": "QA Tester",
            "action": "LOGIN_FAILED",
            "resource": "Authentication",
            "details": "Failed login attempt - incorrect password",
            "timestamp": datetime.now() - timedelta(hours=4),
            "ip_address": "192.168.1.103",
            "user_agent": "Mozilla/5.0 (Ubuntu; Linux x86_64) AppleWebKit/537.36",
            "status": "failure"
        },
        {
            "id": "audit_005",
            "user_id": "a1b2c3d4-5e6f-7890-abcd-ef1234567890",
            "user_name": "System Administrator",
            "action": "DELETE",
            "resource": "User",
            "details": "Deleted inactive user account: old.user@planora.com",
            "timestamp": datetime.now() - timedelta(days=1),
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "status": "success"
        },
        {
            "id": "audit_006",
            "user_id": "f6g7h8i9-0123-4567-f012-678901234567",
            "user_name": "Lisa Park",
            "action": "UPDATE",
            "resource": "Task",
            "details": "Updated task: Shopping Cart Persistence",
            "timestamp": datetime.now() - timedelta(hours=1),
            "ip_address": "192.168.1.104",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "status": "success"
        },
        {
            "id": "audit_007",
            "user_id": "e5f6g7h8-9012-3456-ef01-567890123456",
            "user_name": "Rajesh Kumar",
            "action": "CREATE",
            "resource": "Task",
            "details": "Created new task: Implement OAuth2 Social Login",
            "timestamp": datetime.now() - timedelta(hours=6),
            "ip_address": "192.168.1.105",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "status": "success"
        }
    ]

    for log_data in audit_logs_data:
        db_log = AuditLog(**log_data)
        db.add(db_log)

    db.commit()
    print(f"[SUCCESS] Inserted {len(audit_logs_data)} audit logs")

def create_user_tables_and_insert_data():
    """Create user-related tables and insert mock data"""

    # Create tables
    print("Creating user-related database tables...")
    Base.metadata.create_all(bind=engine)
    print("[SUCCESS] User-related tables created successfully!")

    # Get database session
    db = SessionLocal()

    try:
        # Clear existing data (optional)
        print("Clearing existing user data...")
        db.query(AuditLog).delete()
        db.query(User).delete()
        db.query(Role).delete()
        db.commit()

        # Insert data in order (roles first, then users, then audit logs)
        print("Inserting roles...")
        insert_roles(db)

        print("Inserting users...")
        insert_users(db)

        print("Inserting audit logs...")
        insert_audit_logs(db)

        print("\n" + "=" * 60)
        print("🎉 User data setup completed successfully!")
        print("\n👥 User Data Summary:")
        print("   • 5 Roles (Super Admin, Admin, Project Manager, Developer, Tester)")
        print("   • 25 Users across different departments")
        print("   • 7 Audit log entries with various actions")
        print("\n📊 User Distribution:")
        print("   • 1 Super Admin")
        print("   • 1 Administrator")
        print("   • 5 Project Managers")
        print("   • 16 Developers")
        print("   • 2 Testers")

        print("\n🔐 Login Credentials:")
        print("   • Super Admin: superadmin@planora.com / super123")
        print("   • Admin: admin@planora.com / admin123")
        print("   • All others: [email] / password123")

        print("\n🚀 User APIs available at:")
        print("   • GET /api/v1/users/ - List all users")
        print("   • POST /api/v1/users/ - Create new user")
        print("   • GET /api/v1/users/{id} - Get user details")
        print("   • PUT /api/v1/users/{id} - Update user")
        print("   • GET /api/v1/roles/ - List all roles")
        print("   • GET /api/v1/audit-logs/ - List audit logs")

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_user_tables_and_insert_data()