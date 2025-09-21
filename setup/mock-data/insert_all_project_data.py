#!/usr/bin/env python3
"""
Comprehensive project data insertion script for all project-related entities:
- Projects and Master Data (Priorities, Statuses, Types, Methodologies)
- Epics
- Sprints
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
    print("  1. Master Data (Priorities, Statuses, Types, Methodologies, Departments, Industries)")
    print("  2. Customers (10 customers with diverse industries)")
    print("  3. Projects (20 projects with customer associations)")
    print("  4. Epics (10 comprehensive epics)")
    print("  5. Sprints (6 sprints with different statuses)")
    print("  6. Tasks (30 tasks across different statuses)")
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
            from app.features.sprints.models import Sprint
            from app.features.epics.models import Epic
            from app.features.projects.models import Project
            from app.features.masters.models import ProjectMethodology, ProjectType, ProjectStatus, Priority, Department, Industry

            db.query(Story).delete()
            db.query(Sprint).delete()
            db.query(Epic).delete()
            db.query(Project).delete()
            db.query(Industry).delete()
            db.query(Department).delete()
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
            project_ids = insert_projects(db)

            # Step 3: Insert Epics
            print("\n🔄 STEP 3: Setting up Epics...")
            insert_epics(db)

            # Step 4: Insert Sprints
            print("\n🔄 STEP 4: Setting up Sprints...")
            insert_sprints(db)

            # Step 5: Insert Stories
            print("\n🔄 STEP 5: Setting up Stories...")
            insert_tasks(db, project_ids)

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
        print("   • 5 Departments (Engineering, Product, Design, QA, DevOps)")
        print("   • 8 Industries (Technology, Healthcare, Finance, E-commerce, etc.)")

        print("\n👥 Customers:")
        print("   • 3 Sample Customers with complete profiles")
        print("   • Diverse industries and contact information")
        print("   • Revenue tracking and project associations")

        print("\n📁 Projects:")
        print("   • 6 Projects covering all methodologies (Agile, Scrum, Waterfall, Kanban, DevOps, Lean)")
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

        print("\n✅ Tasks:")
        print("   • 30 Tasks (5 per project) across all 6 projects")
        print("   • Story points, labels, and due dates")
        print("   • Diverse task statuses: completed, in-progress, todo, backlog")

        print("\n🚀 PROJECT APIs READY:")
        print("   • Customers: /api/v1/customers/")
        print("   • Projects: /api/v1/projects/")
        print("   • Epics: /api/v1/epics/")
        print("   • Sprints: /api/v1/sprints/")
        print("   • Tasks: /api/v1/tasks/")
        print("   • Masters: /api/v1/masters/")
        print("   • Industries: /api/v1/masters/industry")

        print("\n📊 DASHBOARD VIEWS AVAILABLE:")
        print("   • Kanban Boards: /api/v1/tasks/board/kanban")
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
    from app.features.masters.models import ProjectMethodology, ProjectType, ProjectStatus, Priority, Department, Industry

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

    # Insert Departments
    departments_data = [
        {"id": str(uuid.uuid4()), "name": "Engineering", "description": "Software development and technical teams", "is_active": True, "sort_order": 1},
        {"id": str(uuid.uuid4()), "name": "Product Management", "description": "Product strategy and roadmap management", "is_active": True, "sort_order": 2},
        {"id": str(uuid.uuid4()), "name": "Design", "description": "User experience and interface design teams", "is_active": True, "sort_order": 3},
        {"id": str(uuid.uuid4()), "name": "Quality Assurance", "description": "Software testing and quality control", "is_active": True, "sort_order": 4},
        {"id": str(uuid.uuid4()), "name": "DevOps", "description": "Infrastructure and deployment operations", "is_active": True, "sort_order": 5}
    ]

    for department_data in departments_data:
        db_department = Department(**department_data)
        db.add(db_department)

    # Insert Industries
    industries_data = [
        {"id": str(uuid.uuid4()), "name": "Technology", "description": "Technology and software development companies", "is_active": True, "sort_order": 1},
        {"id": str(uuid.uuid4()), "name": "Healthcare", "description": "Healthcare and medical services industry", "is_active": True, "sort_order": 2},
        {"id": str(uuid.uuid4()), "name": "Finance", "description": "Banking, finance, and insurance services", "is_active": True, "sort_order": 3},
        {"id": str(uuid.uuid4()), "name": "E-commerce", "description": "Online retail and e-commerce platforms", "is_active": True, "sort_order": 4},
        {"id": str(uuid.uuid4()), "name": "Education", "description": "Educational institutions and e-learning platforms", "is_active": True, "sort_order": 5},
        {"id": str(uuid.uuid4()), "name": "Manufacturing", "description": "Manufacturing and industrial production", "is_active": True, "sort_order": 6},
        {"id": str(uuid.uuid4()), "name": "Energy", "description": "Energy and utilities sector", "is_active": True, "sort_order": 7},
        {"id": str(uuid.uuid4()), "name": "Automotive", "description": "Automotive industry and vehicle manufacturing", "is_active": True, "sort_order": 8}
    ]

    for industry_data in industries_data:
        db_industry = Industry(**industry_data)
        db.add(db_industry)

    db.commit()
    print(f"[SUCCESS] Inserted master data: {len(methodologies_data)} methodologies, {len(types_data)} types, {len(statuses_data)} statuses, {len(priorities_data)} priorities, {len(departments_data)} departments, {len(industries_data)} industries")


def insert_projects(db: Session):
    """Insert project mock data"""
    from app.features.projects.models import Project

    # Define project IDs for referencing in tasks
    project_ids = {
        "web_app": "aa1bb2cc-dd33-4ee5-5ff6-678901234567",
        "mobile_banking": "bb2cc3dd-ee44-5ff6-6778-789012345678",
        "ecommerce": "cc3dd4ee-ff55-6667-7889-890123456789",
        "devops": str(uuid.uuid4()),
        "legacy_migration": str(uuid.uuid4()),
        "support_kanban": str(uuid.uuid4()),
        "process_optimization": str(uuid.uuid4())
    }

    projects_data = [
        {
            "id": project_ids["web_app"],
            "name": "Web App Redesign",
            "description": "Complete redesign of the main web application with new UI/UX",
            "status": "Active",
            "progress": 75,
            "start_date": datetime(2024, 10, 1),
            "end_date": datetime(2025, 2, 28),
            "budget": 150000.0,
            "spent": 112500.0,
            "customer": "TechCorp Solutions",
            "customer_id": None,
            "priority": "High",
            "team_lead_id": "c3d4e5f6-7890-1234-cdef-345678901234",
            "team_members": ["e5f6g7h8-9012-3456-ef01-567890123456", "f6g7h8i9-0123-4567-f012-678901234567"],
            "tags": ["frontend", "design", "react"],
            "color": "#28A745",
            "methodology": "Agile",
            "project_type": "Software Development"
        },
        {
            "id": project_ids["mobile_banking"],
            "name": "Mobile Banking App",
            "description": "Secure mobile banking application with biometric authentication",
            "status": "Active",
            "progress": 60,
            "start_date": datetime(2024, 11, 15),
            "end_date": datetime(2025, 4, 15),
            "budget": 200000.0,
            "spent": 120000.0,
            "customer": "Global Finance Inc",
            "customer_id": None,
            "priority": "Critical",
            "team_lead_id": "b2c3d4e5-6f78-9012-bcde-f23456789012",
            "team_members": ["c3d4e5f6-7890-1234-cdef-345678901234", "e5f6g7h8-9012-3456-ef01-567890123456"],
            "tags": ["mobile", "security", "fintech"],
            "color": "#17A2B8",
            "methodology": "Scrum",
            "project_type": "Mobile Development"
        },
        {
            "id": project_ids["ecommerce"],
            "name": "E-commerce Platform",
            "description": "Full-featured e-commerce solution with inventory management",
            "status": "Active",
            "progress": 45,
            "start_date": datetime(2024, 12, 1),
            "end_date": datetime(2025, 6, 30),
            "budget": 300000.0,
            "spent": 135000.0,
            "customer": "Retail Solutions Inc",
            "customer_id": None,
            "priority": "High",
            "team_lead_id": "f6g7h8i9-0123-4567-f012-678901234567",
            "team_members": ["e5f6g7h8-9012-3456-ef01-567890123456", "c3d4e5f6-7890-1234-cdef-345678901234"],
            "tags": ["e-commerce", "inventory", "payments"],
            "color": "#FFC107",
            "methodology": "Agile",
            "project_type": "Software Development"
        },
        {
            "id": project_ids["devops"],
            "name": "DevOps Pipeline Automation",
            "description": "Automated CI/CD pipeline with monitoring and deployment strategies",
            "status": "Active",
            "progress": 65,
            "start_date": datetime(2024, 9, 1),
            "end_date": datetime(2025, 3, 31),
            "budget": 180000.0,
            "spent": 117000.0,
            "customer": "TechCorp Solutions",
            "customer_id": None,
            "priority": "High",
            "team_lead_id": "g7h8i9j0-1234-5678-0123-789012345678",
            "team_members": ["d4e5f6g7-8901-2345-def0-456789012345", "h8i9j0k1-2345-6789-1234-890123456789"],
            "tags": ["devops", "automation", "ci-cd"],
            "color": "#6F42C1",
            "methodology": "DevOps",
            "project_type": "Infrastructure"
        },
        {
            "id": project_ids["legacy_migration"],
            "name": "Legacy System Migration",
            "description": "Systematic migration of legacy systems using waterfall methodology",
            "status": "Planning",
            "progress": 15,
            "start_date": datetime(2025, 1, 1),
            "end_date": datetime(2025, 12, 31),
            "budget": 450000.0,
            "spent": 67500.0,
            "customer": "Global Finance Inc",
            "customer_id": None,
            "priority": "Critical",
            "team_lead_id": "i9j0k1l2-3456-789a-2345-90123456789a",
            "team_members": ["j0k1l2m3-4567-89ab-3456-0123456789ab", "k1l2m3n4-5678-9abc-4567-123456789abc"],
            "tags": ["migration", "legacy", "database"],
            "color": "#20C997",
            "methodology": "Waterfall",
            "project_type": "Infrastructure"
        },
        {
            "id": project_ids["support_kanban"],
            "name": "Support Ticket Management",
            "description": "Kanban-based customer support ticket management system",
            "status": "Active",
            "progress": 80,
            "start_date": datetime(2024, 8, 15),
            "end_date": datetime(2025, 2, 15),
            "budget": 120000.0,
            "spent": 96000.0,
            "customer": "Retail Solutions Inc",
            "customer_id": None,
            "priority": "Medium",
            "team_lead_id": "l2m3n4o5-6789-abcd-5678-23456789abcd",
            "team_members": ["m3n4o5p6-789a-bcde-6789-3456789abcde", "n4o5p6q7-89ab-cdef-789a-456789abcdef"],
            "tags": ["support", "kanban", "tickets"],
            "color": "#FD7E14",
            "methodology": "Kanban",
            "project_type": "Software Development"
        },
        {
            "id": project_ids["process_optimization"],
            "name": "Process Optimization Initiative",
            "description": "Lean methodology implementation for workflow optimization",
            "status": "Active",
            "progress": 40,
            "start_date": datetime(2024, 10, 15),
            "end_date": datetime(2025, 6, 15),
            "budget": 95000.0,
            "spent": 38000.0,
            "customer": "TechCorp Solutions",
            "customer_id": None,
            "priority": "Medium",
            "team_lead_id": "o5p6q7r8-9abc-def0-89ab-56789abcdef0",
            "team_members": ["p6q7r8s9-abcd-ef01-9abc-6789abcdef01", "q7r8s9t0-bcde-f012-abcd-789abcdef012"],
            "tags": ["optimization", "lean", "process"],
            "color": "#E83E8C",
            "methodology": "Lean",
            "project_type": "Software Development"
        }
    ]

    for project_data in projects_data:
        db_project = Project(**project_data)
        db.add(db_project)

    db.commit()
    print(f"[SUCCESS] Inserted {len(projects_data)} projects")

    # Return project_ids for use in tasks
    return project_ids

def insert_epics(db: Session):
    """Insert epic mock data"""
    from app.features.epics.models import Epic

    epics_data = [
        {
            "id": str(uuid.uuid4()),
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
            "id": str(uuid.uuid4()),
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
            "id": str(uuid.uuid4()),
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
            "id": str(uuid.uuid4()),
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

def insert_tasks(db: Session, project_ids: dict):
    """Insert task mock data - 5 tasks per project"""
    from app.features.stories.models import Story

    tasks_data = [
        # Web App Redesign Project (5 tasks)
        {
            "id": str(uuid.uuid4()),
            "title": "UI Component Library Setup",
            "description": "Create reusable UI components for the new design system",
            "status": "completed",
            "priority": "high",
            "assignee_id": "e5f6g7h8-9012-3456-ef01-567890123456",
            "project_id": project_ids["web_app"],
            "sprint": "Sprint 23",
            "labels": ["frontend", "design-system"],
            "due_date": datetime(2025, 1, 15),
            "story_points": 8,
            "comments_count": 3,
            "attachments_count": 2
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Responsive Layout Implementation",
            "description": "Implement responsive layouts for mobile and tablet views",
            "status": "in-progress",
            "priority": "high",
            "assignee_id": "f6g7h8i9-0123-4567-f012-678901234567",
            "project_id": project_ids["web_app"],
            "sprint": "Sprint 23",
            "labels": ["frontend", "responsive"],
            "due_date": datetime(2025, 1, 25),
            "story_points": 13,
            "comments_count": 5,
            "attachments_count": 1
        },
        {
            "id": str(uuid.uuid4()),
            "title": "User Authentication Redesign",
            "description": "Redesign login and registration flows with new UI",
            "status": "todo",
            "priority": "critical",
            "assignee_id": "c3d4e5f6-7890-1234-cdef-345678901234",
            "project_id": project_ids["web_app"],
            "sprint": "Sprint 24",
            "labels": ["frontend", "auth"],
            "due_date": datetime(2025, 2, 5),
            "story_points": 8,
            "comments_count": 2,
            "attachments_count": 3
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Navigation Menu Overhaul",
            "description": "Implement new navigation structure and menu design",
            "status": "todo",
            "priority": "medium",
            "assignee_id": "e5f6g7h8-9012-3456-ef01-567890123456",
            "project_id": project_ids["web_app"],
            "sprint": "Sprint 24",
            "labels": ["frontend", "navigation"],
            "due_date": datetime(2025, 2, 10),
            "story_points": 5,
            "comments_count": 1,
            "attachments_count": 0
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Performance Optimization",
            "description": "Optimize bundle size and loading performance",
            "status": "backlog",
            "priority": "medium",
            "assignee_id": "f6g7h8i9-0123-4567-f012-678901234567",
            "project_id": project_ids["web_app"],
            "sprint": "Sprint 25",
            "labels": ["performance", "optimization"],
            "due_date": datetime(2025, 2, 20),
            "story_points": 8,
            "comments_count": 0,
            "attachments_count": 1
        },

        # Mobile Banking App Project (5 tasks)
        {
            "id": str(uuid.uuid4()),
            "title": "Biometric Authentication",
            "description": "Implement fingerprint and face ID authentication",
            "status": "in-progress",
            "priority": "critical",
            "assignee_id": "c3d4e5f6-7890-1234-cdef-345678901234",
            "project_id": project_ids["mobile_banking"],
            "sprint": "Sprint 23",
            "labels": ["mobile", "security", "biometric"],
            "due_date": datetime(2025, 1, 30),
            "story_points": 13,
            "comments_count": 8,
            "attachments_count": 2
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Account Balance Display",
            "description": "Create secure account balance and transaction history view",
            "status": "completed",
            "priority": "high",
            "assignee_id": "b2c3d4e5-6f78-9012-bcde-f23456789012",
            "project_id": project_ids["mobile_banking"],
            "sprint": "Sprint 22",
            "labels": ["mobile", "account", "ui"],
            "due_date": datetime(2025, 1, 20),
            "story_points": 8,
            "comments_count": 4,
            "attachments_count": 1
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Money Transfer Feature",
            "description": "Implement secure money transfer between accounts",
            "status": "todo",
            "priority": "high",
            "assignee_id": "d4e5f6g7-8901-2345-def0-456789012345",
            "project_id": project_ids["mobile_banking"],
            "sprint": "Sprint 24",
            "labels": ["mobile", "transfer", "security"],
            "due_date": datetime(2025, 2, 15),
            "story_points": 13,
            "comments_count": 2,
            "attachments_count": 0
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Push Notifications",
            "description": "Set up push notifications for transactions and alerts",
            "status": "todo",
            "priority": "medium",
            "assignee_id": "e5f6g7h8-9012-3456-ef01-567890123456",
            "project_id": project_ids["mobile_banking"],
            "sprint": "Sprint 24",
            "labels": ["mobile", "notifications"],
            "due_date": datetime(2025, 2, 25),
            "story_points": 5,
            "comments_count": 1,
            "attachments_count": 0
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Offline Mode Support",
            "description": "Enable basic app functionality when offline",
            "status": "backlog",
            "priority": "low",
            "assignee_id": "f6g7h8i9-0123-4567-f012-678901234567",
            "project_id": project_ids["mobile_banking"],
            "sprint": "Sprint 25",
            "labels": ["mobile", "offline"],
            "due_date": datetime(2025, 3, 5),
            "story_points": 8,
            "comments_count": 0,
            "attachments_count": 0
        },

        # E-commerce Platform Project (5 tasks)
        {
            "id": str(uuid.uuid4()),
            "title": "Shopping Cart Persistence",
            "description": "Implement cart persistence across browser sessions",
            "status": "completed",
            "priority": "high",
            "assignee_id": "e5f6g7h8-9012-3456-ef01-567890123456",
            "project_id": project_ids["ecommerce"],
            "sprint": "Sprint 22",
            "labels": ["ecommerce", "cart", "persistence"],
            "due_date": datetime(2025, 1, 18),
            "story_points": 5,
            "comments_count": 3,
            "attachments_count": 1
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Payment Gateway Integration",
            "description": "Integrate multiple payment methods (Stripe, PayPal, etc.)",
            "status": "in-progress",
            "priority": "critical",
            "assignee_id": "c3d4e5f6-7890-1234-cdef-345678901234",
            "project_id": project_ids["ecommerce"],
            "sprint": "Sprint 23",
            "labels": ["ecommerce", "payments", "integration"],
            "due_date": datetime(2025, 2, 1),
            "story_points": 13,
            "comments_count": 6,
            "attachments_count": 2
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Inventory Management System",
            "description": "Build comprehensive inventory tracking and management",
            "status": "todo",
            "priority": "high",
            "assignee_id": "f6g7h8i9-0123-4567-f012-678901234567",
            "project_id": project_ids["ecommerce"],
            "sprint": "Sprint 24",
            "labels": ["ecommerce", "inventory", "management"],
            "due_date": datetime(2025, 2, 12),
            "story_points": 21,
            "comments_count": 2,
            "attachments_count": 1
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Product Search & Filtering",
            "description": "Implement advanced search and filtering capabilities",
            "status": "todo",
            "priority": "medium",
            "assignee_id": "g7h8i9j0-1234-5678-0123-789012345678",
            "project_id": project_ids["ecommerce"],
            "sprint": "Sprint 24",
            "labels": ["ecommerce", "search", "filtering"],
            "due_date": datetime(2025, 2, 18),
            "story_points": 8,
            "comments_count": 1,
            "attachments_count": 0
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Order Tracking System",
            "description": "Build order status tracking and notification system",
            "status": "backlog",
            "priority": "medium",
            "assignee_id": "h8i9j0k1-2345-6789-1234-890123456789",
            "project_id": project_ids["ecommerce"],
            "sprint": "Sprint 25",
            "labels": ["ecommerce", "orders", "tracking"],
            "due_date": datetime(2025, 2, 28),
            "story_points": 8,
            "comments_count": 0,
            "attachments_count": 0
        },

        # DevOps Pipeline Automation Project (5 tasks)
        {
            "id": str(uuid.uuid4()),
            "title": "CI/CD Pipeline Setup",
            "description": "Configure automated build and deployment pipeline",
            "status": "completed",
            "priority": "critical",
            "assignee_id": "g7h8i9j0-1234-5678-0123-789012345678",
            "project_id": project_ids["devops"],
            "sprint": "Sprint 22",
            "labels": ["devops", "ci-cd", "automation"],
            "due_date": datetime(2025, 1, 20),
            "story_points": 13,
            "comments_count": 5,
            "attachments_count": 3
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Monitoring & Alerting",
            "description": "Set up comprehensive monitoring and alerting system",
            "status": "in-progress",
            "priority": "high",
            "assignee_id": "d4e5f6g7-8901-2345-def0-456789012345",
            "project_id": project_ids["devops"],
            "sprint": "Sprint 23",
            "labels": ["devops", "monitoring", "alerts"],
            "due_date": datetime(2025, 2, 3),
            "story_points": 8,
            "comments_count": 4,
            "attachments_count": 1
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Container Orchestration",
            "description": "Implement Kubernetes deployment and management",
            "status": "todo",
            "priority": "high",
            "assignee_id": "h8i9j0k1-2345-6789-1234-890123456789",
            "project_id": project_ids["devops"],
            "sprint": "Sprint 24",
            "labels": ["devops", "kubernetes", "containers"],
            "due_date": datetime(2025, 2, 15),
            "story_points": 13,
            "comments_count": 2,
            "attachments_count": 0
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Security Scanning Integration",
            "description": "Integrate security scanning into CI/CD pipeline",
            "status": "todo",
            "priority": "medium",
            "assignee_id": "i9j0k1l2-3456-789a-2345-90123456789a",
            "project_id": project_ids["devops"],
            "sprint": "Sprint 24",
            "labels": ["devops", "security", "scanning"],
            "due_date": datetime(2025, 2, 25),
            "story_points": 8,
            "comments_count": 1,
            "attachments_count": 0
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Performance Testing Automation",
            "description": "Automate performance testing in deployment pipeline",
            "status": "backlog",
            "priority": "low",
            "assignee_id": "j0k1l2m3-4567-89ab-3456-0123456789ab",
            "project_id": project_ids["devops"],
            "sprint": "Sprint 25",
            "labels": ["devops", "performance", "testing"],
            "due_date": datetime(2025, 3, 10),
            "story_points": 5,
            "comments_count": 0,
            "attachments_count": 0
        },

        # Legacy System Migration Project (5 tasks)
        {
            "id": str(uuid.uuid4()),
            "title": "System Architecture Analysis",
            "description": "Analyze existing legacy system architecture and dependencies",
            "status": "completed",
            "priority": "critical",
            "assignee_id": "i9j0k1l2-3456-789a-2345-90123456789a",
            "project_id": project_ids["legacy_migration"],
            "sprint": "Sprint 21",
            "labels": ["migration", "analysis", "architecture"],
            "due_date": datetime(2025, 1, 10),
            "story_points": 8,
            "comments_count": 7,
            "attachments_count": 4
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Database Schema Migration",
            "description": "Migrate database schema to new system format",
            "status": "in-progress",
            "priority": "high",
            "assignee_id": "j0k1l2m3-4567-89ab-3456-0123456789ab",
            "project_id": project_ids["legacy_migration"],
            "sprint": "Sprint 23",
            "labels": ["migration", "database", "schema"],
            "due_date": datetime(2025, 2, 8),
            "story_points": 21,
            "comments_count": 5,
            "attachments_count": 2
        },
        {
            "id": str(uuid.uuid4()),
            "title": "API Endpoint Migration",
            "description": "Migrate and update API endpoints to new standards",
            "status": "todo",
            "priority": "high",
            "assignee_id": "k1l2m3n4-5678-9abc-4567-123456789abc",
            "project_id": project_ids["legacy_migration"],
            "sprint": "Sprint 24",
            "labels": ["migration", "api", "endpoints"],
            "due_date": datetime(2025, 2, 20),
            "story_points": 13,
            "comments_count": 3,
            "attachments_count": 1
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Data Migration Scripts",
            "description": "Create scripts for migrating legacy data to new system",
            "status": "todo",
            "priority": "medium",
            "assignee_id": "l2m3n4o5-6789-abcd-5678-23456789abcd",
            "project_id": project_ids["legacy_migration"],
            "sprint": "Sprint 25",
            "labels": ["migration", "data", "scripts"],
            "due_date": datetime(2025, 3, 5),
            "story_points": 13,
            "comments_count": 1,
            "attachments_count": 0
        },
        {
            "id": str(uuid.uuid4()),
            "title": "User Training Documentation",
            "description": "Create comprehensive user training materials",
            "status": "backlog",
            "priority": "low",
            "assignee_id": "m3n4o5p6-789a-bcde-6789-3456789abcde",
            "project_id": project_ids["legacy_migration"],
            "sprint": "Sprint 26",
            "labels": ["migration", "documentation", "training"],
            "due_date": datetime(2025, 3, 15),
            "story_points": 5,
            "comments_count": 0,
            "attachments_count": 0
        },

        # Support Ticket Management Project (5 tasks)
        {
            "id": str(uuid.uuid4()),
            "title": "Kanban Board Implementation",
            "description": "Build interactive Kanban board for ticket management",
            "status": "completed",
            "priority": "high",
            "assignee_id": "l2m3n4o5-6789-abcd-5678-23456789abcd",
            "project_id": project_ids["support_kanban"],
            "sprint": "Sprint 22",
            "labels": ["kanban", "ui", "tickets"],
            "due_date": datetime(2025, 1, 25),
            "story_points": 13,
            "comments_count": 6,
            "attachments_count": 2
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Ticket Priority System",
            "description": "Implement automatic ticket prioritization based on criteria",
            "status": "in-progress",
            "priority": "medium",
            "assignee_id": "m3n4o5p6-789a-bcde-6789-3456789abcde",
            "project_id": project_ids["support_kanban"],
            "sprint": "Sprint 23",
            "labels": ["kanban", "priority", "automation"],
            "due_date": datetime(2025, 2, 5),
            "story_points": 8,
            "comments_count": 3,
            "attachments_count": 1
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Customer Notification System",
            "description": "Send automated updates to customers about ticket status",
            "status": "todo",
            "priority": "medium",
            "assignee_id": "n4o5p6q7-89ab-cdef-789a-456789abcdef",
            "project_id": project_ids["support_kanban"],
            "sprint": "Sprint 24",
            "labels": ["kanban", "notifications", "customer"],
            "due_date": datetime(2025, 2, 12),
            "story_points": 5,
            "comments_count": 2,
            "attachments_count": 0
        },
        {
            "id": str(uuid.uuid4()),
            "title": "SLA Tracking & Reporting",
            "description": "Track and report on service level agreement compliance",
            "status": "todo",
            "priority": "low",
            "assignee_id": "o5p6q7r8-9abc-def0-89ab-56789abcdef0",
            "project_id": project_ids["support_kanban"],
            "sprint": "Sprint 24",
            "labels": ["kanban", "sla", "reporting"],
            "due_date": datetime(2025, 2, 20),
            "story_points": 8,
            "comments_count": 1,
            "attachments_count": 0
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Knowledge Base Integration",
            "description": "Integrate knowledge base for self-service support",
            "status": "backlog",
            "priority": "low",
            "assignee_id": "p6q7r8s9-abcd-ef01-9abc-6789abcdef01",
            "project_id": project_ids["support_kanban"],
            "sprint": "Sprint 25",
            "labels": ["kanban", "knowledge-base", "self-service"],
            "due_date": datetime(2025, 3, 1),
            "story_points": 8,
            "comments_count": 0,
            "attachments_count": 0
        },

        # Process Optimization Initiative Project (5 tasks)
        {
            "id": str(uuid.uuid4()),
            "title": "Current Process Documentation",
            "description": "Document all current business processes and workflows",
            "status": "completed",
            "priority": "medium",
            "assignee_id": "o5p6q7r8-9abc-def0-89ab-56789abcdef0",
            "project_id": project_ids["process_optimization"],
            "sprint": "Sprint 22",
            "labels": ["lean", "documentation", "process"],
            "due_date": datetime(2025, 1, 30),
            "story_points": 8,
            "comments_count": 4,
            "attachments_count": 5
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Waste Identification Analysis",
            "description": "Identify waste and inefficiencies in current processes",
            "status": "in-progress",
            "priority": "medium",
            "assignee_id": "p6q7r8s9-abcd-ef01-9abc-6789abcdef01",
            "project_id": project_ids["process_optimization"],
            "sprint": "Sprint 23",
            "labels": ["lean", "analysis", "waste"],
            "due_date": datetime(2025, 2, 10),
            "story_points": 5,
            "comments_count": 3,
            "attachments_count": 1
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Workflow Automation Tools",
            "description": "Implement tools to automate repetitive workflow tasks",
            "status": "todo",
            "priority": "medium",
            "assignee_id": "q7r8s9t0-bcde-f012-abcd-789abcdef012",
            "project_id": project_ids["process_optimization"],
            "sprint": "Sprint 24",
            "labels": ["lean", "automation", "tools"],
            "due_date": datetime(2025, 2, 25),
            "story_points": 13,
            "comments_count": 2,
            "attachments_count": 0
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Performance Metrics Dashboard",
            "description": "Create dashboard to track process improvement metrics",
            "status": "todo",
            "priority": "low",
            "assignee_id": "r8s9t0u1-cdef-0123-bcde-89abcdef0123",
            "project_id": project_ids["process_optimization"],
            "sprint": "Sprint 25",
            "labels": ["lean", "metrics", "dashboard"],
            "due_date": datetime(2025, 3, 10),
            "story_points": 8,
            "comments_count": 1,
            "attachments_count": 0
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Team Training Program",
            "description": "Develop lean methodology training program for teams",
            "status": "backlog",
            "priority": "low",
            "assignee_id": "s9t0u1v2-def0-1234-cdef-9abcdef01234",
            "project_id": project_ids["process_optimization"],
            "sprint": "Sprint 26",
            "labels": ["lean", "training", "methodology"],
            "due_date": datetime(2025, 3, 20),
            "story_points": 5,
            "comments_count": 0,
            "attachments_count": 0
        }
    ]

    for task_data in tasks_data:
        db_task = Story(**task_data)
        db.add(db_task)

    db.commit()
    print(f"[SUCCESS] Inserted {len(tasks_data)} tasks")

if __name__ == "__main__":
    create_all_project_tables_and_insert_data()