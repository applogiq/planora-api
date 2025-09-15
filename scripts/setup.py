#!/usr/bin/env python3
"""
Setup script for Planora API
This script helps initialize the application with default data
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.base import SessionLocal, engine
from app.models import *
from app.core.security import get_password_hash
import uuid


def create_default_permissions(db: Session):
    """Create default permissions"""
    default_permissions = [
        ("admin.manage", "Full administrative access"),
        ("project.create", "Create new projects"),
        ("project.manage", "Manage projects"),
        ("project.view", "View projects"),
        ("project.delete", "Delete projects"),
        ("task.create", "Create new tasks"),
        ("task.update", "Update tasks"),
        ("task.delete", "Delete tasks"),
        ("task.view", "View tasks"),
        ("task.assign", "Assign tasks to users"),
        ("user.manage", "Manage users"),
        ("user.view", "View users"),
        ("user.invite", "Invite new users"),
        ("report.view", "View reports"),
        ("report.manage", "Manage reports"),
        ("report.export", "Export reports"),
        ("integration.manage", "Manage integrations"),
        ("integration.view", "View integrations"),
        ("automation.manage", "Manage automation rules"),
        ("automation.view", "View automation rules"),
        ("timetrack.manage", "Manage time tracking"),
        ("timetrack.view", "View time tracking"),
        ("comment.create", "Create comments"),
        ("comment.update", "Update own comments"),
        ("comment.delete", "Delete own comments"),
        ("attachment.upload", "Upload attachments"),
        ("attachment.download", "Download attachments"),
        ("board.manage", "Manage boards"),
        ("board.view", "View boards"),
        ("sprint.manage", "Manage sprints"),
        ("sprint.view", "View sprints"),
    ]
    
    existing_permissions = {p.key for p in db.query(Permission).all()}
    
    for key, description in default_permissions:
        if key not in existing_permissions:
            permission = Permission(
                id=uuid.uuid4(),
                key=key,
                description=description
            )
            db.add(permission)
            print(f"Created permission: {key}")
    
    db.commit()


def create_default_integration_providers(db: Session):
    """Create default integration providers"""
    default_providers = [
        ("slack", "Slack", "Slack workspace integration"),
        ("github", "GitHub", "GitHub repository integration"),
        ("gitlab", "GitLab", "GitLab repository integration"),
        ("gcal", "Google Calendar", "Google Calendar integration"),
        ("outlook", "Outlook Calendar", "Microsoft Outlook Calendar integration"),
        ("jira", "Jira", "Atlassian Jira integration"),
        ("trello", "Trello", "Trello board integration"),
        ("teams", "Microsoft Teams", "Microsoft Teams integration"),
        ("asana", "Asana", "Asana project management integration"),
        ("linear", "Linear", "Linear issue tracking integration"),
    ]
    
    existing_providers = {p.key for p in db.query(IntegrationProvider).all()}
    
    for key, display_name, description in default_providers:
        if key not in existing_providers:
            provider = IntegrationProvider(
                key=key,
                display_name=display_name,
                description=description
            )
            db.add(provider)
            print(f"Created integration provider: {key}")
    
    db.commit()


def create_demo_tenant_and_user(db: Session, tenant_name: str = "Demo Organization", 
                               admin_email: str = "admin@demo.com", 
                               admin_password: str = "admin123"):
    """Create demo tenant with admin user"""
    
    # Check if demo tenant already exists
    existing_tenant = db.query(Tenant).filter(Tenant.name == tenant_name).first()
    if existing_tenant:
        print(f"Demo tenant '{tenant_name}' already exists")
        return existing_tenant
    
    # Create tenant
    tenant = Tenant(
        id=uuid.uuid4(),
        name=tenant_name,
        plan="enterprise"
    )
    db.add(tenant)
    db.flush()
    
    # Create admin user
    admin_user = User(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        email=admin_email,
        password_hash=get_password_hash(admin_password),
        is_active=True
    )
    db.add(admin_user)
    db.flush()
    
    # Create user profile
    profile = UserProfile(
        id=uuid.uuid4(),
        user_id=admin_user.id,
        first_name="Demo",
        last_name="Admin",
        bio="Demo administrator account"
    )
    db.add(profile)
    
    # Create default roles for the tenant
    roles_data = [
        ("Owner", "Organization owner with full access"),
        ("Admin", "Administrator with broad access"),
        ("PM", "Project manager with project oversight"),
        ("Member", "Team member with standard access"),
        ("Viewer", "Read-only access to projects")
    ]
    
    role_permissions = {
        "Owner": [
            "admin.manage", "project.create", "project.manage", "project.view", "project.delete",
            "task.create", "task.update", "task.delete", "task.view", "task.assign",
            "user.manage", "user.view", "user.invite", "report.view", "report.manage", "report.export",
            "integration.manage", "integration.view", "automation.manage", "automation.view",
            "timetrack.manage", "timetrack.view", "comment.create", "comment.update", "comment.delete",
            "attachment.upload", "attachment.download", "board.manage", "board.view",
            "sprint.manage", "sprint.view"
        ],
        "Admin": [
            "project.create", "project.manage", "project.view", "project.delete",
            "task.create", "task.update", "task.delete", "task.view", "task.assign",
            "user.view", "user.invite", "report.view", "report.manage", "report.export",
            "integration.manage", "integration.view", "automation.manage", "automation.view",
            "timetrack.manage", "timetrack.view", "comment.create", "comment.update", "comment.delete",
            "attachment.upload", "attachment.download", "board.manage", "board.view",
            "sprint.manage", "sprint.view"
        ],
        "PM": [
            "project.create", "project.manage", "project.view",
            "task.create", "task.update", "task.view", "task.assign",
            "user.view", "report.view", "report.manage", "automation.view",
            "timetrack.view", "comment.create", "comment.update", "comment.delete",
            "attachment.upload", "attachment.download", "board.manage", "board.view",
            "sprint.manage", "sprint.view"
        ],
        "Member": [
            "project.view", "task.create", "task.update", "task.view",
            "user.view", "report.view", "timetrack.view",
            "comment.create", "comment.update", "comment.delete",
            "attachment.upload", "attachment.download", "board.view", "sprint.view"
        ],
        "Viewer": [
            "project.view", "task.view", "user.view", "report.view",
            "timetrack.view", "board.view", "sprint.view"
        ]
    }
    
    # Get all permissions
    permissions = {p.key: p for p in db.query(Permission).all()}
    
    created_roles = {}
    for role_name, description in roles_data:
        role = Role(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            name=role_name,
            description=description
        )
        db.add(role)
        db.flush()
        created_roles[role_name] = role
        
        # Assign permissions to role
        for permission_key in role_permissions.get(role_name, []):
            if permission_key in permissions:
                role_permission = RolePermission(
                    role_id=role.id,
                    permission_id=permissions[permission_key].id
                )
                db.add(role_permission)
        
        print(f"Created role: {role_name}")
    
    # Assign Owner role to admin user
    user_role = UserRole(
        user_id=admin_user.id,
        role_id=created_roles["Owner"].id
    )
    db.add(user_role)
    
    db.commit()
    
    print(f"Created demo tenant: {tenant_name}")
    print(f"Created admin user: {admin_email} (password: {admin_password})")
    
    return tenant


def create_sample_data(db: Session, tenant: Tenant):
    """Create sample projects and tasks"""
    
    # Get admin user
    admin_user = db.query(User).filter(User.tenant_id == tenant.id).first()
    
    if not admin_user:
        print("No admin user found for tenant")
        return
    
    # Create sample projects
    projects_data = [
        {
            "key": "WEB",
            "name": "Website Redesign",
            "description": "Complete redesign of company website with modern UI/UX",
            "status": "active"
        },
        {
            "key": "MOBILE",
            "name": "Mobile App Development",
            "description": "Native mobile app for iOS and Android platforms",
            "status": "active"
        },
        {
            "key": "MARKET",
            "name": "Marketing Campaign Q1",
            "description": "Q1 marketing campaign planning and execution",
            "status": "planning"
        }
    ]
    
    created_projects = []
    for project_data in projects_data:
        project = Project(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            owner_user_id=admin_user.id,
            **project_data
        )
        db.add(project)
        db.flush()
        
        # Add admin as project member
        member = ProjectMember(
            project_id=project.id,
            user_id=admin_user.id,
            role="Owner"
        )
        db.add(member)
        
        created_projects.append(project)
        print(f"Created sample project: {project.name}")
    
    # Create sample tasks for first project
    if created_projects:
        web_project = created_projects[0]
        
        # Create a board for the project
        board = Board(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            project_id=web_project.id,
            name="Main Board"
        )
        db.add(board)
        db.flush()
        
        # Create board columns
        columns_data = [
            ("Backlog", None, 0),
            ("To Do", 5, 1),
            ("In Progress", 3, 2),
            ("Review", 2, 3),
            ("Done", None, 4)
        ]
        
        for col_name, wip_limit, position in columns_data:
            column = BoardColumn(
                id=uuid.uuid4(),
                board_id=board.id,
                name=col_name,
                wip_limit=wip_limit,
                position=position
            )
            db.add(column)
        
        # Create sample tasks
        tasks_data = [
            {
                "title": "Design homepage mockup",
                "description_md": "Create wireframes and mockups for the new homepage design",
                "type": "task",
                "status": "todo",
                "priority": "high"
            },
            {
                "title": "Implement responsive navigation",
                "description_md": "Build responsive navigation component with mobile support",
                "type": "task",
                "status": "in_progress",
                "priority": "medium"
            },
            {
                "title": "Set up CI/CD pipeline",
                "description_md": "Configure continuous integration and deployment pipeline",
                "type": "task",
                "status": "todo",
                "priority": "low"
            }
        ]
        
        task_counter = 1
        for task_data in tasks_data:
            task = Task(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                project_id=web_project.id,
                key=f"{web_project.key}-{task_counter}",
                assignee_id=admin_user.id,
                reporter_id=admin_user.id,
                **task_data
            )
            db.add(task)
            task_counter += 1
            print(f"Created sample task: {task.title}")
    
    db.commit()
    print("Sample data creation completed")


def main():
    """Main setup function"""
    print("Setting up Planora API...")
    
    # Create database tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Create default data
        print("Creating default permissions...")
        create_default_permissions(db)
        
        print("Creating default integration providers...")
        create_default_integration_providers(db)
        
        # Ask user if they want to create demo data
        create_demo = input("Create demo tenant and sample data? (y/N): ").lower().strip()
        
        if create_demo == 'y':
            tenant_name = input("Demo tenant name (Demo Organization): ").strip() or "Demo Organization"
            admin_email = input("Admin email (admin@demo.com): ").strip() or "admin@demo.com"
            admin_password = input("Admin password (admin123): ").strip() or "admin123"
            
            print("Creating demo tenant and admin user...")
            tenant = create_demo_tenant_and_user(db, tenant_name, admin_email, admin_password)
            
            create_sample = input("Create sample projects and tasks? (y/N): ").lower().strip()
            if create_sample == 'y':
                print("Creating sample data...")
                create_sample_data(db, tenant)
        
        print("\nSetup completed successfully!")
        print("\nNext steps:")
        print("1. Start the development server: uvicorn app.main:app --reload")
        print("2. Visit http://localhost:8000/docs for API documentation")
        print("3. Use the demo credentials to test the API")
        
    except Exception as e:
        print(f"Error during setup: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()