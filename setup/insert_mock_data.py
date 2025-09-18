import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.features.users.models import User
from app.features.roles.models import Role
from app.features.projects.models import Project
from app.features.tasks.models import Task
from app.features.audit_logs.models import AuditLog
from app.db.database import Base
from app.core.security import get_password_hash
from datetime import datetime, timedelta
import uuid

def create_tables_and_insert_data():
    """Create all tables and insert comprehensive mock data"""

    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("[SUCCESS] Database tables created successfully!")

    # Get database session
    db = SessionLocal()

    try:
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("Clearing existing data...")
        db.query(AuditLog).delete()
        db.query(Task).delete()
        db.query(Project).delete()
        db.query(User).delete()
        db.query(Role).delete()
        db.commit()

        # Insert Roles
        print("Inserting roles...")
        insert_roles(db)

        # Insert Users
        print("Inserting users...")
        insert_users(db)

        # Insert Projects
        print("Inserting projects...")
        insert_projects(db)

        # Insert Tasks
        print("Inserting tasks...")
        insert_tasks(db)

        # Insert Audit Logs
        print("Inserting audit logs...")
        insert_audit_logs(db)

        print("[SUCCESS] All mock data inserted successfully!")

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        db.rollback()
    finally:
        db.close()

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

def insert_projects(db: Session):
    """Insert project mock data"""
    projects_data = [
        {
            "id": "aa1bb2cc-dd33-4ee5-5ff6-678901234567",
            "name": "Web App Redesign",
            "description": "Complete redesign of the main web application with new UI/UX",
            "status": "Active",
            "progress": 75,
            "start_date": datetime(2024, 10, 1),
            "end_date": datetime(2025, 2, 28),
            "budget": 150000.0,
            "spent": 112500.0,
            "customer": "Acme Corporation",
            "customer_id": "CUST-001",
            "priority": "High",
            "team_lead_id": "c3d4e5f6-7890-1234-cdef-345678901234",
            "team_members": ["e5f6g7h8-9012-3456-ef01-567890123456", "f6g7h8i9-0123-4567-f012-678901234567", "c3d4e5f6-7890-1234-cdef-345678901234"],
            "tags": ["frontend", "design", "react"],
            "color": "#28A745",
            "methodology": "Agile",
            "project_type": "Software Development"
        },
        {
            "id": "bb2cc3dd-ee44-5ff6-6778-789012345678",
            "name": "Mobile Banking App",
            "description": "Secure mobile banking application with biometric authentication",
            "status": "Active",
            "progress": 60,
            "start_date": datetime(2024, 11, 15),
            "end_date": datetime(2025, 4, 15),
            "budget": 200000.0,
            "spent": 120000.0,
            "customer": "Global Bank Corp",
            "customer_id": "CUST-002",
            "priority": "Critical",
            "team_lead_id": "b2c3d4e5-6f78-9012-bcde-f23456789012",
            "team_members": ["c3d4e5f6-7890-1234-cdef-345678901234", "e5f6g7h8-9012-3456-ef01-567890123456", "d4e5f6g7-8901-2345-def0-456789012345"],
            "tags": ["mobile", "security", "fintech"],
            "color": "#17A2B8",
            "methodology": "Scrum",
            "project_type": "Mobile Development"
        },
        {
            "id": "cc3dd4ee-ff55-6667-7889-890123456789",
            "name": "E-commerce Platform",
            "description": "Full-featured e-commerce solution with inventory management",
            "status": "Active",
            "progress": 45,
            "start_date": datetime(2024, 12, 1),
            "end_date": datetime(2025, 6, 30),
            "budget": 300000.0,
            "spent": 135000.0,
            "customer": "Retail Solutions Inc",
            "customer_id": "CUST-003",
            "priority": "High",
            "team_lead_id": "f6g7h8i9-0123-4567-f012-678901234567",
            "team_members": ["e5f6g7h8-9012-3456-ef01-567890123456", "c3d4e5f6-7890-1234-cdef-345678901234", "b2c3d4e5-6f78-9012-bcde-f23456789012"],
            "tags": ["e-commerce", "inventory", "payments"],
            "color": "#FFC107",
            "methodology": "Agile",
            "project_type": "Software Development"
        },
        {
            "id": "PROJ-004",
            "name": "Analytics Dashboard",
            "description": "Real-time analytics and reporting dashboard",
            "status": "On Hold",
            "progress": 30,
            "start_date": datetime(2024, 9, 1),
            "end_date": datetime(2025, 3, 31),
            "budget": 120000.0,
            "spent": 36000.0,
            "customer": "Data Insights Ltd",
            "customer_id": "CUST-004",
            "priority": "Medium",
            "team_lead_id": "c3d4e5f6-7890-1234-cdef-345678901234",
            "team_members": ["e5f6g7h8-9012-3456-ef01-567890123456", "d4e5f6g7-8901-2345-def0-456789012345"],
            "tags": ["analytics", "dashboard", "reporting"],
            "color": "#FD7E14",
            "methodology": "Kanban",
            "project_type": "Data Analytics"
        },
        {
            "id": "PROJ-005",
            "name": "CRM System",
            "description": "Customer relationship management system",
            "status": "Completed",
            "progress": 100,
            "start_date": datetime(2024, 6, 1),
            "end_date": datetime(2024, 11, 30),
            "budget": 180000.0,
            "spent": 175000.0,
            "customer": "Sales Force Pro",
            "customer_id": "CUST-005",
            "priority": "High",
            "team_lead_id": "b2c3d4e5-6f78-9012-bcde-f23456789012",
            "team_members": ["d4e5f6g7-8901-2345-def0-456789012345", "c3d4e5f6-7890-1234-cdef-345678901234", "f6g7h8i9-0123-4567-f012-678901234567"],
            "tags": ["crm", "sales", "customer-management"],
            "color": "#28A745",
            "methodology": "Waterfall",
            "project_type": "Software Development"
        },
        {
            "id": "aa1bb2cc-3dd4-5ee6-ff78-90ab12cd34ef",
            "name": "AI Chatbot Integration",
            "description": "Integrate AI-powered chatbot for customer support",
            "status": "Active",
            "progress": 85,
            "start_date": datetime(2024, 8, 1),
            "end_date": datetime(2025, 1, 31),
            "budget": 95000.0,
            "spent": 80750.0,
            "customer": "Tech Support Co",
            "customer_id": "CUST-006",
            "priority": "High",
            "team_lead_id": "g7h8i9j0-1234-5678-0123-789012345678",
            "team_members": ["h8i9j0k1-2345-6789-1234-890123456789", "i9j0k1l2-3456-789a-2345-90123456789a"],
            "tags": ["ai", "chatbot", "customer-support"],
            "color": "#6F42C1",
            "methodology": "Agile",
            "project_type": "AI/ML Development"
        },
        {
            "id": "bb2cc3dd-4ee5-6ff7-8901-ab23cd45ef67",
            "name": "Cloud Migration",
            "description": "Migrate legacy systems to cloud infrastructure",
            "status": "Active",
            "progress": 40,
            "start_date": datetime(2024, 12, 1),
            "end_date": datetime(2025, 8, 31),
            "budget": 250000.0,
            "spent": 100000.0,
            "customer": "Enterprise Systems Ltd",
            "customer_id": "CUST-007",
            "priority": "Critical",
            "team_lead_id": "j0k1l2m3-4567-89ab-3456-0123456789ab",
            "team_members": ["l2m3n4o5-6789-abcd-5678-23456789abcd", "m3n4o5p6-789a-bcde-6789-3456789abcde"],
            "tags": ["cloud", "migration", "infrastructure"],
            "color": "#E83E8C",
            "methodology": "DevOps",
            "project_type": "Infrastructure"
        },
        {
            "id": "cc3dd4ee-5ff6-7890-1ab2-cd34ef56789a",
            "name": "Social Media Dashboard",
            "description": "Social media analytics and management platform",
            "status": "Planning",
            "progress": 15,
            "start_date": datetime(2025, 1, 15),
            "end_date": datetime(2025, 7, 15),
            "budget": 140000.0,
            "spent": 21000.0,
            "customer": "Social Metrics Inc",
            "customer_id": "CUST-008",
            "priority": "Medium",
            "team_lead_id": "k1l2m3n4-5678-9abc-4567-123456789abc",
            "team_members": ["n4o5p6q7-89ab-cdef-789a-456789abcdef", "o5p6q7r8-9abc-def0-89ab-56789abcdef0"],
            "tags": ["social-media", "analytics", "dashboard"],
            "color": "#20C997",
            "methodology": "Agile",
            "project_type": "Marketing Technology"
        },
        {
            "id": "dd4ee5ff-6789-01ab-2cd3-ef4567890abc",
            "name": "IoT Device Management",
            "description": "IoT device monitoring and control system",
            "status": "Active",
            "progress": 55,
            "start_date": datetime(2024, 10, 15),
            "end_date": datetime(2025, 5, 15),
            "budget": 180000.0,
            "spent": 99000.0,
            "customer": "Smart Devices Corp",
            "customer_id": "CUST-009",
            "priority": "High",
            "team_lead_id": "l2m3n4o5-6789-abcd-5678-23456789abcd",
            "team_members": ["p6q7r8s9-abcd-ef01-9abc-6789abcdef01", "q7r8s9t0-bcde-f012-abcd-789abcdef012"],
            "tags": ["iot", "monitoring", "devices"],
            "color": "#FD7E14",
            "methodology": "Scrum",
            "project_type": "IoT Development"
        },
        {
            "id": "ee5ff678-9012-ab34-cd56-ef789012345a",
            "name": "Blockchain Wallet",
            "description": "Secure cryptocurrency wallet application",
            "status": "Active",
            "progress": 70,
            "start_date": datetime(2024, 9, 1),
            "end_date": datetime(2025, 3, 31),
            "budget": 220000.0,
            "spent": 154000.0,
            "customer": "Crypto Solutions Ltd",
            "customer_id": "CUST-010",
            "priority": "Critical",
            "team_lead_id": "m3n4o5p6-789a-bcde-6789-3456789abcde",
            "team_members": ["r8s9t0u1-cdef-0123-bcde-89abcdef0123", "s9t0u1v2-def0-1234-cdef-9abcdef01234"],
            "tags": ["blockchain", "cryptocurrency", "security"],
            "color": "#6610F2",
            "methodology": "Agile",
            "project_type": "Blockchain Development"
        },
        {
            "id": "ff67890a-bc12-def3-4567-890123456789",
            "name": "Video Streaming Platform",
            "description": "Live video streaming and content delivery platform",
            "status": "Active",
            "progress": 65,
            "start_date": datetime(2024, 7, 1),
            "end_date": datetime(2025, 2, 28),
            "budget": 350000.0,
            "spent": 227500.0,
            "customer": "StreamTech Media",
            "customer_id": "CUST-011",
            "priority": "High",
            "team_lead_id": "n4o5p6q7-89ab-cdef-789a-456789abcdef",
            "team_members": ["t0u1v2w3-ef01-2345-def0-abcdef012345", "u1v2w3x4-f012-3456-ef01-bcdef0123456"],
            "tags": ["streaming", "video", "media"],
            "color": "#DC3545",
            "methodology": "Agile",
            "project_type": "Media Technology"
        },
        {
            "id": "0123456a-bcde-f789-0123-456789abcdef",
            "name": "Health Monitoring App",
            "description": "Personal health tracking and monitoring mobile app",
            "status": "Planning",
            "progress": 20,
            "start_date": datetime(2025, 2, 1),
            "end_date": datetime(2025, 9, 30),
            "budget": 160000.0,
            "spent": 32000.0,
            "customer": "HealthTech Solutions",
            "customer_id": "CUST-012",
            "priority": "Medium",
            "team_lead_id": "o5p6q7r8-9abc-def0-89ab-56789abcdef0",
            "team_members": ["v2w3x4y5-0123-4567-f012-cdef01234567", "w3x4y5z6-1234-5678-0123-def012345678"],
            "tags": ["health", "mobile", "monitoring"],
            "color": "#198754",
            "methodology": "Lean",
            "project_type": "Health Technology"
        },
        {
            "id": "123456ab-cdef-0789-1234-56789abcdef0",
            "name": "Document Management System",
            "description": "Enterprise document storage and collaboration platform",
            "status": "Active",
            "progress": 80,
            "start_date": datetime(2024, 6, 15),
            "end_date": datetime(2025, 1, 15),
            "budget": 130000.0,
            "spent": 104000.0,
            "customer": "DocFlow Enterprise",
            "customer_id": "CUST-013",
            "priority": "High",
            "team_lead_id": "p6q7r8s9-abcd-ef01-9abc-6789abcdef01",
            "team_members": ["x4y5z6a7-2345-6789-1234-ef0123456789", "f6g7h8i9-0123-4567-f012-678901234567"],
            "tags": ["documents", "collaboration", "enterprise"],
            "color": "#0DCAF0",
            "methodology": "Waterfall",
            "project_type": "Enterprise Software"
        },
        {
            "id": "23456abc-def0-1789-2345-6789abcdef01",
            "name": "Learning Management System",
            "description": "Online education and course management platform",
            "status": "Active",
            "progress": 90,
            "start_date": datetime(2024, 5, 1),
            "end_date": datetime(2024, 12, 31),
            "budget": 200000.0,
            "spent": 180000.0,
            "customer": "EduTech Institute",
            "customer_id": "CUST-014",
            "priority": "High",
            "team_lead_id": "q7r8s9t0-bcde-f012-abcd-789abcdef012",
            "team_members": ["h8i9j0k1-2345-6789-1234-890123456789", "i9j0k1l2-3456-789a-2345-90123456789a"],
            "tags": ["education", "learning", "courses"],
            "color": "#6F42C1",
            "methodology": "Agile",
            "project_type": "Education Technology"
        },
        {
            "id": "3456abcd-ef01-2789-3456-789abcdef012",
            "name": "Smart Home Automation",
            "description": "Integrated smart home control and automation system",
            "status": "Active",
            "progress": 50,
            "start_date": datetime(2024, 11, 1),
            "end_date": datetime(2025, 6, 30),
            "budget": 175000.0,
            "spent": 87500.0,
            "customer": "HomeTech Innovations",
            "customer_id": "CUST-015",
            "priority": "Medium",
            "team_lead_id": "r8s9t0u1-cdef-0123-bcde-89abcdef0123",
            "team_members": ["j0k1l2m3-4567-89ab-3456-0123456789ab", "k1l2m3n4-5678-9abc-4567-123456789abc"],
            "tags": ["smart-home", "automation", "iot"],
            "color": "#FFC107",
            "methodology": "Scrum",
            "project_type": "IoT Development"
        },
        {
            "id": "456abcde-f012-3789-4567-89abcdef0123",
            "name": "Food Delivery Platform",
            "description": "Multi-restaurant food ordering and delivery platform",
            "status": "Completed",
            "progress": 100,
            "start_date": datetime(2024, 3, 1),
            "end_date": datetime(2024, 10, 31),
            "budget": 280000.0,
            "spent": 275000.0,
            "customer": "QuickEats Ltd",
            "customer_id": "CUST-016",
            "priority": "High",
            "team_lead_id": "s9t0u1v2-def0-1234-cdef-9abcdef01234",
            "team_members": ["l2m3n4o5-6789-abcd-5678-23456789abcd", "m3n4o5p6-789a-bcde-6789-3456789abcde"],
            "tags": ["food-delivery", "marketplace", "mobile"],
            "color": "#28A745",
            "methodology": "Agile",
            "project_type": "Mobile Development"
        },
        {
            "id": "56abcdef-0123-4789-5678-9abcdef01234",
            "name": "Virtual Reality Training",
            "description": "VR-based employee training and simulation platform",
            "status": "Planning",
            "progress": 10,
            "start_date": datetime(2025, 3, 1),
            "end_date": datetime(2025, 12, 31),
            "budget": 320000.0,
            "spent": 32000.0,
            "customer": "VR Training Corp",
            "customer_id": "CUST-017",
            "priority": "Medium",
            "team_lead_id": "t0u1v2w3-ef01-2345-def0-abcdef012345",
            "team_members": ["n4o5p6q7-89ab-cdef-789a-456789abcdef", "o5p6q7r8-9abc-def0-89ab-56789abcdef0"],
            "tags": ["vr", "training", "simulation"],
            "color": "#6610F2",
            "methodology": "Agile",
            "project_type": "VR/AR Development"
        },
        {
            "id": "6abcdef0-1234-5789-6789-abcdef012345",
            "name": "Real Estate Portal",
            "description": "Property listing and management platform",
            "status": "Active",
            "progress": 35,
            "start_date": datetime(2024, 12, 15),
            "end_date": datetime(2025, 7, 31),
            "budget": 190000.0,
            "spent": 66500.0,
            "customer": "PropertyTech Solutions",
            "customer_id": "CUST-018",
            "priority": "Medium",
            "team_lead_id": "u1v2w3x4-f012-3456-ef01-bcdef0123456",
            "team_members": ["p6q7r8s9-abcd-ef01-9abc-6789abcdef01", "q7r8s9t0-bcde-f012-abcd-789abcdef012"],
            "tags": ["real-estate", "property", "listings"],
            "color": "#20C997",
            "methodology": "Kanban",
            "project_type": "Web Development"
        },
        {
            "id": "abcdef01-2345-6789-789a-bcdef0123456",
            "name": "Fitness Tracking API",
            "description": "API service for fitness data aggregation and analysis",
            "status": "Active",
            "progress": 75,
            "start_date": datetime(2024, 8, 15),
            "end_date": datetime(2025, 2, 15),
            "budget": 110000.0,
            "spent": 82500.0,
            "customer": "FitData Analytics",
            "customer_id": "CUST-019",
            "priority": "High",
            "team_lead_id": "v2w3x4y5-0123-4567-f012-cdef01234567",
            "team_members": ["r8s9t0u1-cdef-0123-bcde-89abcdef0123", "s9t0u1v2-def0-1234-cdef-9abcdef01234"],
            "tags": ["fitness", "api", "analytics"],
            "color": "#FD7E14",
            "methodology": "Agile",
            "project_type": "API Development"
        },
        {
            "id": "bcdef012-3456-789a-89ab-cdef01234567",
            "name": "Inventory Management System",
            "description": "Automated inventory tracking and management solution",
            "status": "On Hold",
            "progress": 25,
            "start_date": datetime(2024, 9, 15),
            "end_date": datetime(2025, 4, 30),
            "budget": 145000.0,
            "spent": 36250.0,
            "customer": "Warehouse Solutions Inc",
            "customer_id": "CUST-020",
            "priority": "Low",
            "team_lead_id": "w3x4y5z6-1234-5678-0123-def012345678",
            "team_members": ["t0u1v2w3-ef01-2345-def0-abcdef012345", "u1v2w3x4-f012-3456-ef01-bcdef0123456"],
            "tags": ["inventory", "warehouse", "automation"],
            "color": "#6C757D",
            "methodology": "Lean",
            "project_type": "Operations Technology"
        }
    ]

    for project_data in projects_data:
        db_project = Project(**project_data)
        db.add(db_project)

    db.commit()
    print(f"[SUCCESS] Inserted {len(projects_data)} projects")

def insert_tasks(db: Session):
    """Insert task mock data"""
    tasks_data = [
        # Backlog Tasks
        {
            "id": "TASK-001",
            "title": "Implement OAuth2 Social Login",
            "description": "Add Google, Facebook, and GitHub authentication options",
            "status": "backlog",
            "priority": "high",
            "assignee_id": "e5f6g7h8-9012-3456-ef01-567890123456",
            "project_id": "cc3dd4ee-ff55-6667-7889-890123456789",
            "sprint": "Sprint 24",
            "labels": ["backend", "security"],
            "due_date": datetime(2025, 2, 15),
            "story_points": 8,
            "comments_count": 3,
            "attachments_count": 2
        },
        {
            "id": "TASK-002",
            "title": "Design Product Comparison Feature",
            "description": "Create UI for comparing multiple products side by side",
            "status": "backlog",
            "priority": "medium",
            "assignee_id": "f6g7h8i9-0123-4567-f012-678901234567",
            "project_id": "cc3dd4ee-ff55-6667-7889-890123456789",
            "sprint": "Sprint 24",
            "labels": ["frontend", "design"],
            "due_date": datetime(2025, 2, 20),
            "story_points": 5,
            "comments_count": 1,
            "attachments_count": 0
        },
        # Todo Tasks
        {
            "id": "TASK-013",
            "title": "User Profile Dashboard",
            "description": "Create comprehensive user profile management page",
            "status": "todo",
            "priority": "high",
            "assignee_id": "e5f6g7h8-9012-3456-ef01-567890123456",
            "project_id": "aa1bb2cc-dd33-4ee5-5ff6-678901234567",
            "sprint": "Sprint 23",
            "labels": ["frontend", "profile"],
            "due_date": datetime(2025, 1, 30),
            "story_points": 8,
            "comments_count": 2,
            "attachments_count": 1
        },
        {
            "id": "TASK-014",
            "title": "Inventory Management System",
            "description": "Build stock tracking and management features",
            "status": "todo",
            "priority": "high",
            "assignee_id": "f6g7h8i9-0123-4567-f012-678901234567",
            "project_id": "cc3dd4ee-ff55-6667-7889-890123456789",
            "sprint": "Sprint 23",
            "labels": ["backend", "inventory"],
            "due_date": datetime(2025, 1, 28),
            "story_points": 13,
            "comments_count": 1,
            "attachments_count": 2
        },
        # In Progress Tasks
        {
            "id": "TASK-023",
            "title": "JWT Token Management",
            "description": "Implement secure JWT refresh token mechanism",
            "status": "in-progress",
            "priority": "critical",
            "assignee_id": "c3d4e5f6-7890-1234-cdef-345678901234",
            "project_id": "bb2cc3dd-ee44-5ff6-6778-789012345678",
            "sprint": "Sprint 23",
            "labels": ["backend", "security"],
            "due_date": datetime(2025, 1, 27),
            "story_points": 5,
            "comments_count": 5,
            "attachments_count": 1
        },
        {
            "id": "TASK-024",
            "title": "Shopping Cart Persistence",
            "description": "Maintain cart state across browser sessions",
            "status": "in-progress",
            "priority": "high",
            "assignee_id": "f6g7h8i9-0123-4567-f012-678901234567",
            "project_id": "cc3dd4ee-ff55-6667-7889-890123456789",
            "sprint": "Sprint 23",
            "labels": ["frontend", "persistence"],
            "due_date": datetime(2025, 1, 29),
            "story_points": 5,
            "comments_count": 3,
            "attachments_count": 0
        },
        # Review Tasks
        {
            "id": "TASK-031",
            "title": "API Documentation",
            "description": "Complete API documentation with examples",
            "status": "review",
            "priority": "medium",
            "assignee_id": "c3d4e5f6-7890-1234-cdef-345678901234",
            "project_id": "aa1bb2cc-dd33-4ee5-5ff6-678901234567",
            "sprint": "Sprint 23",
            "labels": ["documentation", "api"],
            "due_date": datetime(2025, 1, 26),
            "story_points": 3,
            "comments_count": 1,
            "attachments_count": 0
        },
        # Done Tasks
        {
            "id": "TASK-040",
            "title": "Database Schema Design",
            "description": "Design and implement core database schema",
            "status": "done",
            "priority": "high",
            "assignee_id": "e5f6g7h8-9012-3456-ef01-567890123456",
            "project_id": "bb2cc3dd-ee44-5ff6-6778-789012345678",
            "sprint": "Sprint 22",
            "labels": ["database", "backend"],
            "due_date": datetime(2025, 1, 20),
            "story_points": 8,
            "comments_count": 4,
            "attachments_count": 2
        },
        {
            "id": "TASK-041",
            "title": "Login Page Design",
            "description": "Create responsive login page with modern UI",
            "status": "done",
            "priority": "medium",
            "assignee_id": "f6g7h8i9-0123-4567-f012-678901234567",
            "project_id": "aa1bb2cc-dd33-4ee5-5ff6-678901234567",
            "sprint": "Sprint 22",
            "labels": ["frontend", "design"],
            "due_date": datetime(2025, 1, 18),
            "story_points": 5,
            "comments_count": 2,
            "attachments_count": 1
        }
    ]

    for task_data in tasks_data:
        db_task = Task(**task_data)
        db.add(db_task)

    db.commit()
    print(f"[SUCCESS] Inserted {len(tasks_data)} tasks")

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

if __name__ == "__main__":
    create_tables_and_insert_data()