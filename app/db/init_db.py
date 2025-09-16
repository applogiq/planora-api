from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.features.users.crud import crud_user
from app.features.roles.crud import crud_role
from app.features.users.schemas import UserCreate
from app.features.roles.schemas import RoleCreate
from app.features.users.models import User
from app.features.roles.models import Role
import uuid

def init_db(db: Session) -> None:
    # Create default roles
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

    # Create roles
    for role_data in roles_data:
        existing_role = crud_role.get(db, id=role_data["id"])
        if not existing_role:
            role = Role(
                id=role_data["id"],
                name=role_data["name"],
                description=role_data["description"],
                permissions=role_data["permissions"],
                is_active=role_data["is_active"]
            )
            db.add(role)
            db.commit()
            db.refresh(role)

    # Create default users
    users_data = [
        {
            "id": "superadmin456",
            "email": "superadmin@planora.com",
            "password": "super123",
            "name": "Super Administrator",
            "role_id": "role_super_admin",
            "avatar": "SA",
            "department": "Management",
            "skills": ["Leadership", "Strategy", "Project Management"],
            "phone": "+1 (555) 000-0002",
            "timezone": "America/New_York"
        },
        {
            "id": "admin123",
            "email": "admin@planora.com",
            "password": "admin123",
            "name": "System Administrator",
            "role_id": "role_admin",
            "avatar": "SA",
            "department": "IT",
            "skills": ["System Administration", "Security", "DevOps"],
            "phone": "+1 (555) 000-0001",
            "timezone": "America/New_York"
        },
        {
            "id": "pm789",
            "email": "pm@planora.com",
            "password": "pm123",
            "name": "Project Manager",
            "role_id": "role_project_manager",
            "avatar": "PM",
            "department": "Project Management",
            "skills": ["Agile", "Scrum", "Risk Management"],
            "phone": "+1 (555) 000-0003",
            "timezone": "America/Los_Angeles"
        }
    ]

    # Create users
    for user_data in users_data:
        existing_user = crud_user.get(db, id=user_data["id"])
        if not existing_user:
            user = User(
                id=user_data["id"],
                email=user_data["email"],
                password=get_password_hash(user_data["password"]),
                name=user_data["name"],
                role_id=user_data["role_id"],
                avatar=user_data["avatar"],
                is_active=True,
                department=user_data["department"],
                skills=user_data["skills"],
                phone=user_data["phone"],
                timezone=user_data["timezone"]
            )
            db.add(user)
            db.commit()
            db.refresh(user)