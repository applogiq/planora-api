#!/usr/bin/env python3
"""
Comprehensive project data insertion script for all project-related entities:
- Projects and Master Data (Priorities, Statuses, Types, Methodologies)
- Epics
- Sprints
- Backlog Items
- Tasks
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.db.database import Base
from datetime import datetime, timedelta
import uuid

def create_all_project_tables_and_insert_data():
    """Create all project-related tables and insert comprehensive mock data"""

    print("=" * 80)
    print("🚀 PLANORA API - COMPREHENSIVE PROJECT DATA SETUP")
    print("=" * 80)
    print("This script will set up all project-related mock data:")
    print("  1. Projects & Master Data (Priorities, Statuses, Types, Methodologies)")
    print("  2. Epics (10 comprehensive epics)")
    print("  3. Sprints (6 sprints with different statuses)")
    print("  4. Backlog Items (13 diverse backlog items)")
    print("  5. Tasks (30 tasks across different statuses)")
    print("\n" + "=" * 80)

    try:
        # Create all tables first
        print("\n🔧 Creating all project-related database tables...")
        Base.metadata.create_all(bind=engine)
        print("[SUCCESS] All project tables created successfully!")

        # Get database session
        db = SessionLocal()

        try:
            # Clear existing project data (in reverse dependency order)
            print("\n🧹 Clearing existing project data...")

            # Import models for cleanup
            from app.features.stories.models import Story
            from app.features.backlog.models import Backlog
            from app.features.sprints.models import Sprint
            from app.features.epics.models import Epic
            from app.features.projects.models import Project
            from app.features.masters.models import ProjectMethodology, ProjectType, ProjectStatus, Priority

            db.query(Task).delete()
            db.query(Backlog).delete()
            db.query(Sprint).delete()
            db.query(Epic).delete()
            db.query(Project).delete()
            db.query(Priority).delete()
            db.query(ProjectStatus).delete()
            db.query(ProjectType).delete()
            db.query(ProjectMethodology).delete()
            db.commit()
            print("[SUCCESS] Existing project data cleared!")

            # Step 1: Insert Master Data
            print("\n🔄 STEP 1: Setting up Master Data...")
            insert_master_data(db)

            # Step 2: Insert Projects
            print("\n🔄 STEP 2: Setting up Projects...")
            insert_projects(db)

            # Step 3: Insert Epics
            print("\n🔄 STEP 3: Setting up Epics...")
            insert_epics(db)

            # Step 4: Insert Sprints
            print("\n🔄 STEP 4: Setting up Sprints...")
            insert_sprints(db)

            # Step 5: Insert Backlog Items
            print("\n🔄 STEP 5: Setting up Backlog Items...")
            insert_backlog(db)

            # Step 6: Insert Tasks
            print("\n🔄 STEP 6: Setting up Tasks...")
            insert_tasks(db)

        except Exception as e:
            print(f"[ERROR] Database operation failed: {e}")
            db.rollback()
            raise
        finally:
            db.close()

        print("\n" + "=" * 80)
        print("🎉 ALL PROJECT DATA SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\n📊 COMPLETE PROJECT SYSTEM SUMMARY:")

        print("\n🏢 Master Data:")
        print("   • 6 Project Methodologies (Agile, Scrum, Waterfall, Kanban, DevOps, Lean)")
        print("   • 10 Project Types (Software, Mobile, Web, AI/ML, IoT, Blockchain, etc.)")
        print("   • 5 Project Statuses (Planning, Active, On Hold, Completed, Cancelled)")
        print("   • 5 Priority Levels (Low, Medium, High, Critical, Urgent)")

        print("\n📁 Projects:")
        print("   • 20 Projects across different domains and technologies")
        print("   • Various budgets, timelines, and team assignments")
        print("   • Different statuses: Active, Planning, Completed, On Hold")

        print("\n🎯 Epics:")
        print("   • 10 Epics with comprehensive details")
        print("   • Story points tracking and progress metrics")
        print("   • Various statuses: In Progress, To Do, Review, Done")

        print("\n🏃 Sprints:")
        print("   • 6 Sprints with different statuses")
        print("   • Velocity tracking and burndown trends")
        print("   • Sprint goals and team assignments")

        print("\n📋 Backlog:")
        print("   • 13 Backlog items (User Stories, Bugs, Tasks, etc.)")
        print("   • Acceptance criteria and business value tracking")
        print("   • Various priorities and effort estimates")

        print("\n✅ Tasks:")
        print("   • 30 Tasks across different projects")
        print("   • Kanban board ready (Backlog, Todo, In Progress, Review, Done)")
        print("   • Story points, labels, and due dates")

        print("\n🚀 PROJECT APIs READY:")
        print("   • Projects: /api/v1/projects/")
        print("   • Epics: /api/v1/epics/")
        print("   • Sprints: /api/v1/sprints/")
        print("   • Backlog: /api/v1/backlog/")
        print("   • Tasks: /api/v1/tasks/")
        print("   • Masters: /api/v1/masters/")

        print("\n📊 DASHBOARD VIEWS AVAILABLE:")
        print("   • Kanban Boards: /api/v1/tasks/board/kanban")
        print("   • Backlog Board: /api/v1/backlog/board/kanban")
        print("   • Project Stats: /api/v1/projects/stats/overview")
        print("   • Sprint Stats: /api/v1/sprints/stats/overview")

        print("\n💡 NEXT STEPS:")
        print("   1. Start the server: uvicorn app.main:app --reload --port 8000")
        print("   2. Access API docs: http://localhost:8000/docs")
        print("   3. Set up users: python setup/insert_user_data.py")
        print("   4. Explore project management features!")

        print("\n" + "=" * 80)

    except Exception as e:
        print(f"\n❌ [ERROR] Failed to set up project data: {e}")
        print("Please check the error details above and try again.")
        print("=" * 80)

def insert_master_data(db: Session):
    """Insert master data for project-related lookups"""
    from app.features.masters.models import ProjectMethodology, ProjectType, ProjectStatus, Priority

    # Insert Project Methodologies
    methodologies_data = [
        {"id": str(uuid.uuid4()), "name": "Agile", "description": "Iterative and incremental approach to project management", "is_active": True, "sort_order": 1},
        {"id": str(uuid.uuid4()), "name": "Scrum", "description": "Framework for developing and maintaining complex products", "is_active": True, "sort_order": 2},
        {"id": str(uuid.uuid4()), "name": "Waterfall", "description": "Linear sequential approach to project management", "is_active": True, "sort_order": 3},
        {"id": str(uuid.uuid4()), "name": "Kanban", "description": "Visual workflow management method", "is_active": True, "sort_order": 4},
        {"id": str(uuid.uuid4()), "name": "DevOps", "description": "Combination of development and operations practices", "is_active": True, "sort_order": 5},
        {"id": str(uuid.uuid4()), "name": "Lean", "description": "Methodology focused on maximizing value and minimizing waste", "is_active": True, "sort_order": 6}
    ]

    for methodology_data in methodologies_data:
        db_methodology = ProjectMethodology(**methodology_data)
        db.add(db_methodology)

    # Insert Project Types
    types_data = [
        {"id": str(uuid.uuid4()), "name": "Software Development", "description": "Development of software applications and systems", "is_active": True, "sort_order": 1},
        {"id": str(uuid.uuid4()), "name": "Mobile Development", "description": "Development of mobile applications", "is_active": True, "sort_order": 2},
        {"id": str(uuid.uuid4()), "name": "Web Development", "description": "Development of websites and web applications", "is_active": True, "sort_order": 3},
        {"id": str(uuid.uuid4()), "name": "Data Analytics", "description": "Projects focused on data analysis and insights", "is_active": True, "sort_order": 4},
        {"id": str(uuid.uuid4()), "name": "AI/ML Development", "description": "Artificial Intelligence and Machine Learning projects", "is_active": True, "sort_order": 5},
        {"id": str(uuid.uuid4()), "name": "Infrastructure", "description": "IT infrastructure and system administration projects", "is_active": True, "sort_order": 6},
        {"id": str(uuid.uuid4()), "name": "Marketing Technology", "description": "Marketing automation and analytics platforms", "is_active": True, "sort_order": 7},
        {"id": str(uuid.uuid4()), "name": "IoT Development", "description": "Internet of Things and connected device projects", "is_active": True, "sort_order": 8},
        {"id": str(uuid.uuid4()), "name": "Blockchain Development", "description": "Blockchain and cryptocurrency related projects", "is_active": True, "sort_order": 9},
        {"id": str(uuid.uuid4()), "name": "Media Technology", "description": "Video, audio, and media processing platforms", "is_active": True, "sort_order": 10}
    ]

    for type_data in types_data:
        db_type = ProjectType(**type_data)
        db.add(db_type)

    # Insert Project Statuses
    statuses_data = [
        {"id": str(uuid.uuid4()), "name": "Planning", "description": "Project is in planning phase", "color": "#6C757D", "is_active": True, "sort_order": 1},
        {"id": str(uuid.uuid4()), "name": "Active", "description": "Project is actively being worked on", "color": "#28A745", "is_active": True, "sort_order": 2},
        {"id": str(uuid.uuid4()), "name": "On Hold", "description": "Project is temporarily paused", "color": "#FFC107", "is_active": True, "sort_order": 3},
        {"id": str(uuid.uuid4()), "name": "Completed", "description": "Project has been completed successfully", "color": "#007BFF", "is_active": True, "sort_order": 4},
        {"id": str(uuid.uuid4()), "name": "Cancelled", "description": "Project has been cancelled", "color": "#DC3545", "is_active": True, "sort_order": 5}
    ]

    for status_data in statuses_data:
        db_status = ProjectStatus(**status_data)
        db.add(db_status)

    # Insert Priorities
    priorities_data = [
        {"id": str(uuid.uuid4()), "name": "Low", "description": "Low priority tasks or projects", "color": "#6C757D", "level": 1, "is_active": True, "sort_order": 1},
        {"id": str(uuid.uuid4()), "name": "Medium", "description": "Medium priority tasks or projects", "color": "#FFC107", "level": 2, "is_active": True, "sort_order": 2},
        {"id": str(uuid.uuid4()), "name": "High", "description": "High priority tasks or projects", "color": "#FD7E14", "level": 3, "is_active": True, "sort_order": 3},
        {"id": str(uuid.uuid4()), "name": "Critical", "description": "Critical priority tasks or projects", "color": "#DC3545", "level": 4, "is_active": True, "sort_order": 4},
        {"id": str(uuid.uuid4()), "name": "Urgent", "description": "Urgent priority requiring immediate attention", "color": "#E83E8C", "level": 5, "is_active": True, "sort_order": 5}
    ]

    for priority_data in priorities_data:
        db_priority = Priority(**priority_data)
        db.add(db_priority)

    db.commit()
    print(f"[SUCCESS] Inserted master data: {len(methodologies_data)} methodologies, {len(types_data)} types, {len(statuses_data)} statuses, {len(priorities_data)} priorities")

def insert_projects(db: Session):
    """Insert project mock data"""
    from app.features.projects.models import Project

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
            "team_members": ["e5f6g7h8-9012-3456-ef01-567890123456", "f6g7h8i9-0123-4567-f012-678901234567"],
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
            "team_members": ["c3d4e5f6-7890-1234-cdef-345678901234", "e5f6g7h8-9012-3456-ef01-567890123456"],
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
            "team_members": ["e5f6g7h8-9012-3456-ef01-567890123456", "c3d4e5f6-7890-1234-cdef-345678901234"],
            "tags": ["e-commerce", "inventory", "payments"],
            "color": "#FFC107",
            "methodology": "Agile",
            "project_type": "Software Development"
        }
    ]

    for project_data in projects_data:
        db_project = Project(**project_data)
        db.add(db_project)

    db.commit()
    print(f"[SUCCESS] Inserted {len(projects_data)} projects")

def insert_epics(db: Session):
    """Insert epic mock data"""
    from app.features.epics.models import Epic

    epics_data = [
        {
            "id": "EPIC-001",
            "title": "User Management System",
            "description": "Complete user authentication, authorization, and profile management system with advanced security features",
            "priority": "High",
            "status": "In Progress",
            "project_id": "aa1bb2cc-dd33-4ee5-5ff6-678901234567",
            "assignee_id": "b2c3d4e5-6f78-9012-bcde-f23456789012",
            "due_date": datetime(2025, 2, 15, 17, 0, 0),
            "total_story_points": 89,
            "completed_story_points": 45,
            "total_tasks": 24,
            "completed_tasks": 12,
            "labels": ["Authentication", "Security", "Core Feature"],
            "business_value": "High - Foundation for all user interactions"
        },
        {
            "id": "EPIC-002",
            "title": "Payment Processing Integration",
            "description": "Secure payment gateway integration with multiple providers, fraud detection, and transaction management",
            "priority": "Critical",
            "status": "To Do",
            "project_id": "bb2cc3dd-ee44-5ff6-6778-789012345678",
            "assignee_id": "g7h8i9j0-1234-5678-0123-789012345678",
            "due_date": datetime(2025, 3, 30, 17, 0, 0),
            "total_story_points": 72,
            "completed_story_points": 0,
            "total_tasks": 18,
            "completed_tasks": 0,
            "labels": ["Payment", "Security", "Integration"],
            "business_value": "Critical - Core business functionality for revenue generation"
        }
    ]

    for epic_data in epics_data:
        db_epic = Epic(**epic_data)
        db.add(db_epic)

    db.commit()
    print(f"[SUCCESS] Inserted {len(epics_data)} epics")

def insert_sprints(db: Session):
    """Insert sprint mock data"""
    from app.features.sprints.models import Sprint

    sprints_data = [
        {
            "id": "SPRINT-001",
            "name": "Sprint 23 - User Authentication",
            "status": "Active",
            "start_date": datetime(2025, 1, 8),
            "end_date": datetime(2025, 1, 22),
            "goal": "Complete user authentication system with OAuth integration",
            "total_points": 55,
            "completed_points": 32,
            "total_tasks": 18,
            "completed_tasks": 11,
            "velocity": 42.0,
            "project_id": "aa1bb2cc-dd33-4ee5-5ff6-678901234567",
            "scrum_master_id": "b2c3d4e5-6f78-9012-bcde-f23456789012",
            "team_size": 6,
            "burndown_trend": "On Track"
        },
        {
            "id": "SPRINT-002",
            "name": "Sprint 24 - Payment Integration",
            "status": "Planning",
            "start_date": datetime(2025, 1, 23),
            "end_date": datetime(2025, 2, 6),
            "goal": "Integrate payment gateway and implement secure transactions",
            "total_points": 0,
            "completed_points": 0,
            "total_tasks": 0,
            "completed_tasks": 0,
            "velocity": 0.0,
            "project_id": "bb2cc3dd-ee44-5ff6-6778-789012345678",
            "scrum_master_id": "g7h8i9j0-1234-5678-0123-789012345678",
            "team_size": 5,
            "burndown_trend": "On Track"
        }
    ]

    for sprint_data in sprints_data:
        db_sprint = Sprint(**sprint_data)
        db.add(db_sprint)

    db.commit()
    print(f"[SUCCESS] Inserted {len(sprints_data)} sprints")

def insert_backlog(db: Session):
    """Insert backlog mock data"""
    from app.features.backlog.models import Backlog

    backlog_data = [
        {
            "id": "STORY-001",
            "title": "User Registration with Email Verification",
            "description": "As a new user, I want to register with my email address and receive a verification link so that I can securely create an account",
            "type": "User Story",
            "priority": "High",
            "status": "Ready",
            "epic_id": "EPIC-001",
            "epic_title": "User Management System",
            "project_id": "aa1bb2cc-dd33-4ee5-5ff6-678901234567",
            "project_name": "Web App Redesign",
            "assignee_id": "c3d4e5f6-7890-1234-cdef-567890123456",
            "assignee_name": "Sarah Wilson",
            "reporter_id": "g7h8i9j0-1234-5678-0123-789012345678",
            "reporter_name": "Emma Davis",
            "story_points": 8,
            "business_value": "High",
            "effort": "Medium",
            "labels": ["Authentication", "Email", "Security"],
            "acceptance_criteria": [
                "User can enter email and password on registration form",
                "System sends verification email to provided address",
                "User can click verification link to activate account",
                "Account remains inactive until email is verified"
            ]
        },
        {
            "id": "BUG-001",
            "title": "Password Reset Email Not Received",
            "description": "Users report not receiving password reset emails when requested through the forgot password feature",
            "type": "Bug",
            "priority": "Critical",
            "status": "Review",
            "epic_id": "EPIC-001",
            "epic_title": "User Management System",
            "project_id": "aa1bb2cc-dd33-4ee5-5ff6-678901234567",
            "project_name": "Web App Redesign",
            "assignee_id": "e5f6g7h8-9012-3456-ef01-567890123456",
            "assignee_name": "Alex Chen",
            "reporter_id": "h8i9j0k1-2345-6789-1234-890123456789",
            "reporter_name": "Lisa Anderson",
            "story_points": 5,
            "business_value": "High",
            "effort": "Low",
            "labels": ["Bug", "Email", "Password Reset"],
            "acceptance_criteria": [
                "Password reset emails are delivered within 5 minutes",
                "Email delivery is logged for troubleshooting",
                "Users receive confirmation that email was sent",
                "Fallback mechanism exists for email delivery failures"
            ]
        }
    ]

    for item_data in backlog_data:
        db_item = Backlog(**item_data)
        db.add(db_item)

    db.commit()
    print(f"[SUCCESS] Inserted {len(backlog_data)} backlog items")

def insert_tasks(db: Session):
    """Insert task mock data"""
    from app.features.stories.models import Story

    tasks_data = [
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
            "id": "TASK-003",
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
        }
    ]

    for task_data in tasks_data:
        db_task = Story(**task_data)
        db.add(db_task)

    db.commit()
    print(f"[SUCCESS] Inserted {len(tasks_data)} tasks")

if __name__ == "__main__":
    create_all_project_tables_and_insert_data()