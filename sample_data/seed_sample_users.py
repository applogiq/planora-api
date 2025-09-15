



#!/usr/bin/env python3
"""
Seed the database with sample users with different roles
Password for all users: Applogiq@123
"""

import sys
from pathlib import Path
import uuid

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import User, UserProfile, Role, Permission, UserRole, RolePermission

# Sample users data
SAMPLE_PASSWORD = "Applogiq@123"
SAMPLE_USERS = [
    {
        "email": "admin@planora.com",
        "first_name": "Admin",
        "last_name": "User",
        "role": "Admin",
        "bio": "System administrator with full access to all features"
    },
    {
        "email": "owner@planora.com", 
        "first_name": "Owner",
        "last_name": "User",
        "role": "Owner",
        "bio": "Organization owner with complete control"
    },
    {
        "email": "pm@planora.com",
        "first_name": "Project",
        "last_name": "Manager",
        "role": "PM",
        "bio": "Project manager responsible for project coordination"
    },
    {
        "email": "developer@planora.com",
        "first_name": "Developer",
        "last_name": "User", 
        "role": "Developer",
        "bio": "Software developer working on project tasks"
    },
    {
        "email": "designer@planora.com",
        "first_name": "Designer",
        "last_name": "User",
        "role": "Designer", 
        "bio": "UI/UX designer creating user interfaces"
    },
    {
        "email": "tester@planora.com",
        "first_name": "Tester",
        "last_name": "User",
        "role": "Tester",
        "bio": "Quality assurance tester ensuring product quality"
    },
    {
        "email": "viewer@planora.com",
        "first_name": "Viewer",
        "last_name": "User", 
        "role": "Viewer",
        "bio": "Read-only user with limited access"
    },
    {
        "email": "guest@planora.com",
        "first_name": "Guest",
        "last_name": "User",
        "role": "Guest", 
        "bio": "Guest user with minimal access"
    }
]

# Role definitions with permissions
ROLES_PERMISSIONS = {
    "Admin": [
        "admin.manage", "user.manage", "tenant.manage",
        "project.create", "project.update", "project.delete", "project.manage",
        "task.create", "task.update", "task.delete", "task.assign",
        "report.view", "report.manage", "report.export",
        "integration.manage", "automation.manage"
    ],
    "Owner": [
        "admin.manage", "user.manage", "tenant.manage", 
        "project.create", "project.update", "project.delete", "project.manage",
        "task.create", "task.update", "task.delete", "task.assign",
        "report.view", "report.manage", "report.export",
        "integration.manage", "automation.manage"
    ],
    "PM": [
        "project.create", "project.update", "project.manage",
        "task.create", "task.update", "task.delete", "task.assign",
        "report.view", "report.manage", "user.invite"
    ],
    "Developer": [
        "task.create", "task.update", "task.comment",
        "project.view", "report.view"
    ],
    "Designer": [
        "task.create", "task.update", "task.comment",
        "project.view", "report.view"
    ],
    "Tester": [
        "task.create", "task.update", "task.comment",
        "project.view", "report.view"
    ],
    "Viewer": [
        "project.view", "task.view", "report.view"
    ],
    "Guest": [
        "project.view", "task.view"
    ]
}

def create_permissions(session):
    """Create all permissions"""
    permissions = []
    all_permission_keys = set()
    
    # Collect all unique permissions
    for role_perms in ROLES_PERMISSIONS.values():
        all_permission_keys.update(role_perms)
    
    for perm_key in sorted(all_permission_keys):
        permission = Permission(
            key=perm_key,
            description=f"Permission to {perm_key.replace('.', ' ')}"
        )
        permissions.append(permission)
        session.add(permission)
    
    session.commit()
    print(f"Created {len(permissions)} permissions")
    return permissions

def create_roles(session):
    """Create sample roles"""
    # Get all permissions
    permissions = session.query(Permission).all()
    permission_map = {p.key: p for p in permissions}

    # Create roles with permissions
    roles = {}
    for role_name, permission_keys in ROLES_PERMISSIONS.items():
        role = Role(
            name=role_name,
            description=f"{role_name} role with specific permissions"
        )
        session.add(role)
        session.flush()  # Get the role ID
        
        # Add permissions to role
        for perm_key in permission_keys:
            if perm_key in permission_map:
                role_permission = RolePermission(
                    role_id=role.id,
                    permission_id=permission_map[perm_key].id
                )
                session.add(role_permission)
        
        roles[role_name] = role
    
    session.commit()
    print(f"Created {len(roles)} roles")
    return roles

def create_sample_users(session, roles):
    """Create sample users with profiles and roles"""
    password_hash = get_password_hash(SAMPLE_PASSWORD)
    
    created_users = []
    for user_data in SAMPLE_USERS:
        # Create user
        user = User(
            email=user_data["email"],
            password_hash=password_hash,
            is_active=True
        )
        session.add(user)
        session.flush()  # Get the user ID
        
        # Create user profile
        profile = UserProfile(
            user_id=user.id,
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            bio=user_data["bio"],
            timezone="UTC"
        )
        session.add(profile)
        
        # Assign role to user
        role_name = user_data["role"]
        if role_name in roles:
            user_role = UserRole(
                user_id=user.id,
                role_id=roles[role_name].id
            )
            session.add(user_role)
        
        created_users.append(user)
        print(f"Created user: {user_data['email']} with role: {role_name}")
    
    session.commit()
    print(f"Created {len(created_users)} users")
    return created_users

def main():
    """Main function to seed the database"""
    print("Seeding Planora database with sample users...")
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Sample password for all users: {SAMPLE_PASSWORD}")
    
    # Create engine and session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Check if data already exists
        existing_tenant = session.query(Tenant).first()
        if existing_tenant:
            print("Database already contains data. Skipping seeding.")
            print("If you want to re-seed, please clear the database first.")
            return
        
        print("\n1. Creating permissions...")
        permissions = create_permissions(session)
        
        print("\n2. Creating roles...")
        roles = create_roles(session)

        print("\n3. Creating sample users...")
        users = create_sample_users(session, roles)
        
        print(f"\n✅ Database seeding completed successfully!")
        print(f"\nSample users created:")
        print(f"{'Email':<25} {'Role':<12} {'Name'}")
        print("-" * 50)
        
        for user_data in SAMPLE_USERS:
            print(f"{user_data['email']:<25} {user_data['role']:<12} {user_data['first_name']} {user_data['last_name']}")
        
        print(f"\nAll users have the password: {SAMPLE_PASSWORD}")
        print(f"Tenant: {tenant.name}")
        print(f"You can now login to the API using any of these credentials.")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        session.rollback()
        return False
    finally:
        session.close()
    
    return True

if __name__ == "__main__":
    main()