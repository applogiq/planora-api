#!/usr/bin/env python3
"""
Mockup data for project tables (projects, epics, sprints, tasks, backlog)
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
from datetime import datetime, timedelta
import uuid

def insert_project_data():
    """Insert mock data for project tables"""

    db = SessionLocal()

    try:
        print("🔄 Inserting project data (projects, epics, sprints, tasks, backlog)...")

        # Insert data in dependency order
        insert_projects(db)
        insert_epics(db)
        insert_sprints(db)
        insert_tasks(db)
        insert_backlog(db)

        db.commit()
        print("✅ Project data inserted successfully!")

    except Exception as e:
        print(f"❌ Error inserting project data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def insert_projects(db: Session):
    """Insert project mock data"""

    # Clear existing data
    db.execute(text("DELETE FROM tbl_projects"))

    projects = [
        (
            "aa1bb2cc-dd33-4ee5-5ff6-678901234567",
            "Web App Redesign",
            "Complete redesign of the main web application with new UI/UX and improved performance",
            "Active", 75, datetime(2024, 10, 1), datetime(2025, 2, 28),
            150000.0, 112500.0, "Acme Corporation", "CUST-001", "High",
            "c3d4e5f6-7890-1234-cdef-345678901234",
            ["e5f6g7h8-9012-3456-ef01-567890123456", "f6g7h8i9-0123-4567-f012-678901234567"],
            ["frontend", "design", "react", "ui/ux"], "#28A745", "Agile", "Web Development"
        ),
        (
            "bb2cc3dd-ee44-5ff6-6778-789012345678",
            "Mobile Banking App",
            "Secure mobile banking application with biometric authentication and real-time transactions",
            "Active", 60, datetime(2024, 11, 15), datetime(2025, 4, 15),
            200000.0, 120000.0, "Global Bank Corp", "CUST-002", "Critical",
            "b2c3d4e5-6f78-9012-bcde-f23456789012",
            ["c3d4e5f6-7890-1234-cdef-345678901234", "e5f6g7h8-9012-3456-ef01-567890123456"],
            ["mobile", "security", "fintech", "banking"], "#17A2B8", "Scrum", "Mobile Development"
        ),
        (
            "cc3dd4ee-ff55-6667-7889-890123456789",
            "E-commerce Platform",
            "Full-featured e-commerce solution with inventory management and payment processing",
            "Active", 45, datetime(2024, 12, 1), datetime(2025, 6, 30),
            300000.0, 135000.0, "Retail Solutions Inc", "CUST-003", "High",
            "f6g7h8i9-0123-4567-f012-678901234567",
            ["e5f6g7h8-9012-3456-ef01-567890123456", "g7h8i9j0-1234-5678-0123-789012345678"],
            ["e-commerce", "inventory", "payments", "retail"], "#FFC107", "Agile", "Software Development"
        ),
        (
            "dd4ee5ff-6677-8899-aabb-ccddee112233",
            "AI Recommendation Engine",
            "Machine learning powered recommendation system for personalized user experiences",
            "Planning", 10, datetime(2025, 1, 15), datetime(2025, 8, 15),
            250000.0, 25000.0, "Tech Innovations Ltd", "CUST-004", "Medium",
            "g7h8i9j0-1234-5678-0123-789012345678",
            ["h8i9j0k1-2345-6789-1234-890123456789", "j0k1l2m3-4567-89ab-3456-0123456789ab"],
            ["ai", "ml", "recommendation", "personalization"], "#6F42C1", "Agile", "AI/ML Development"
        ),
        (
            "ee5ff6gg-7788-99aa-bbcc-ddeeff334455",
            "Customer Portal Upgrade",
            "Modernize customer portal with self-service capabilities and improved user experience",
            "On Hold", 30, datetime(2024, 9, 1), datetime(2025, 3, 31),
            120000.0, 36000.0, "Service Corp", "CUST-005", "Low",
            "i9j0k1l2-3456-789a-2345-90123456789a",
            ["j0k1l2m3-4567-89ab-3456-0123456789ab"],
            ["portal", "self-service", "upgrade", "customer"], "#FD7E14", "Waterfall", "Web Development"
        ),
        (
            "ff6gg7hh-8899-aabb-ccdd-eeff11223344",
            "IoT Device Management",
            "Comprehensive IoT device management platform with real-time monitoring",
            "Active", 20, datetime(2024, 11, 1), datetime(2025, 5, 30),
            180000.0, 36000.0, "IoT Systems Inc", "CUST-006", "Medium",
            "d4e5f6g7-8901-2345-def0-456789012345",
            ["f6g7h8i9-0123-4567-f012-678901234567", "g7h8i9j0-1234-5678-0123-789012345678"],
            ["iot", "monitoring", "devices", "real-time"], "#20C997", "Kanban", "IoT Development"
        )
    ]

    for project in projects:
        db.execute("""
            INSERT INTO tbl_projects (
                id, name, description, status, progress, start_date, end_date,
                budget, spent, customer, customer_id, priority, team_lead_id,
                team_members, tags, color, methodology, project_type, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, project)

    print(f"   ✓ Inserted {len(projects)} projects")

def insert_epics(db: Session):
    """Insert epic mock data"""

    # Clear existing data
    db.execute(text("DELETE FROM tbl_project_epics"))

    epics = [
        (
            "EPIC-001", "User Management System",
            "Complete user authentication, authorization, and profile management system with advanced security features",
            "High", "In Progress", "aa1bb2cc-dd33-4ee5-5ff6-678901234567",
            "b2c3d4e5-6f78-9012-bcde-f23456789012", datetime(2025, 2, 15, 17, 0, 0),
            89, 45, 24, 12, ["Authentication", "Security", "Core Feature"],
            "High - Foundation for all user interactions"
        ),
        (
            "EPIC-002", "Payment Processing Integration",
            "Secure payment gateway integration with multiple providers, fraud detection, and transaction management",
            "Critical", "To Do", "bb2cc3dd-ee44-5ff6-6778-789012345678",
            "g7h8i9j0-1234-5678-0123-789012345678", datetime(2025, 3, 30, 17, 0, 0),
            72, 0, 18, 0, ["Payment", "Security", "Integration"],
            "Critical - Core business functionality for revenue generation"
        ),
        (
            "EPIC-003", "Product Catalog Management",
            "Comprehensive product catalog with categories, search, filtering, and inventory tracking",
            "High", "Planning", "cc3dd4ee-ff55-6667-7889-890123456789",
            "f6g7h8i9-0123-4567-f012-678901234567", datetime(2025, 4, 20, 17, 0, 0),
            65, 15, 22, 3, ["Catalog", "Search", "Inventory"],
            "High - Essential for e-commerce functionality"
        ),
        (
            "EPIC-004", "Mobile App Core Features",
            "Essential mobile app features including account management, transaction history, and push notifications",
            "Critical", "In Progress", "bb2cc3dd-ee44-5ff6-6778-789012345678",
            "c3d4e5f6-7890-1234-cdef-345678901234", datetime(2025, 3, 15, 17, 0, 0),
            95, 60, 28, 18, ["Mobile", "Core Features", "Banking"],
            "Critical - Core mobile banking functionality"
        ),
        (
            "EPIC-005", "AI Recommendation Engine",
            "Machine learning algorithms for personalized product recommendations and user behavior analysis",
            "Medium", "Planning", "dd4ee5ff-6677-8899-aabb-ccddee112233",
            "g7h8i9j0-1234-5678-0123-789012345678", datetime(2025, 6, 30, 17, 0, 0),
            120, 0, 35, 0, ["AI", "ML", "Recommendations", "Analytics"],
            "Medium - Enhanced user experience through personalization"
        )
    ]

    for epic in epics:
        db.execute("""
            INSERT INTO tbl_project_epics (
                id, title, description, priority, status, project_id, assignee_id, due_date,
                total_story_points, completed_story_points, total_tasks, completed_tasks,
                labels, business_value, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, epic)

    print(f"   ✓ Inserted {len(epics)} epics")

def insert_sprints(db: Session):
    """Insert sprint mock data"""

    # Clear existing data
    db.execute(text("DELETE FROM tbl_project_sprints"))

    sprints = [
        (
            "SPRINT-001", "Sprint 23 - User Authentication",
            "Active", datetime(2025, 1, 8), datetime(2025, 1, 22),
            "Complete user authentication system with OAuth integration and security enhancements",
            55, 32, 18, 11, 42.0, "aa1bb2cc-dd33-4ee5-5ff6-678901234567",
            "b2c3d4e5-6f78-9012-bcde-f23456789012", 6, "On Track"
        ),
        (
            "SPRINT-002", "Sprint 24 - Payment Integration",
            "Planning", datetime(2025, 1, 23), datetime(2025, 2, 6),
            "Integrate payment gateway and implement secure transaction processing",
            0, 0, 0, 0, 0.0, "bb2cc3dd-ee44-5ff6-6778-789012345678",
            "g7h8i9j0-1234-5678-0123-789012345678", 5, "Planning"
        ),
        (
            "SPRINT-003", "Sprint 25 - Mobile Core Features",
            "Active", datetime(2025, 1, 15), datetime(2025, 1, 29),
            "Implement core mobile banking features and user interface components",
            40, 25, 15, 9, 38.0, "bb2cc3dd-ee44-5ff6-6778-789012345678",
            "c3d4e5f6-7890-1234-cdef-345678901234", 4, "Slightly Behind"
        ),
        (
            "SPRINT-004", "Sprint 26 - E-commerce Catalog",
            "Planning", datetime(2025, 2, 1), datetime(2025, 2, 15),
            "Build product catalog system with search and filtering capabilities",
            0, 0, 0, 0, 0.0, "cc3dd4ee-ff55-6667-7889-890123456789",
            "f6g7h8i9-0123-4567-f012-678901234567", 6, "Planning"
        ),
        (
            "SPRINT-005", "Sprint 22 - UI Redesign",
            "Completed", datetime(2024, 12, 11), datetime(2024, 12, 25),
            "Complete UI redesign with new design system and responsive layouts",
            45, 45, 20, 20, 45.0, "aa1bb2cc-dd33-4ee5-5ff6-678901234567",
            "c3d4e5f6-7890-1234-cdef-345678901234", 5, "Completed Successfully"
        ),
        (
            "SPRINT-006", "Sprint 27 - IoT Device Setup",
            "Active", datetime(2025, 1, 10), datetime(2025, 1, 24),
            "Initial IoT device registration and monitoring dashboard setup",
            30, 12, 12, 5, 28.0, "ff6gg7hh-8899-aabb-ccdd-eeff11223344",
            "d4e5f6g7-8901-2345-def0-456789012345", 4, "On Track"
        )
    ]

    for sprint in sprints:
        db.execute("""
            INSERT INTO tbl_project_sprints (
                id, name, status, start_date, end_date, goal, total_points, completed_points,
                total_tasks, completed_tasks, velocity, project_id, scrum_master_id,
                team_size, burndown_trend, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, sprint)

    print(f"   ✓ Inserted {len(sprints)} sprints")

def insert_tasks(db: Session):
    """Insert task mock data"""

    # Clear existing data
    db.execute(text("DELETE FROM tbl_project_tasks"))

    tasks = [
        (
            "TASK-001", "Implement OAuth2 Social Login",
            "Add Google, Facebook, and GitHub authentication options with secure token management",
            "backlog", "high", "e5f6g7h8-9012-3456-ef01-567890123456",
            "aa1bb2cc-dd33-4ee5-5ff6-678901234567", "SPRINT-001", "EPIC-001",
            "Sprint 23", ["backend", "security", "oauth"], datetime(2025, 2, 15),
            8, 3, 2
        ),
        (
            "TASK-002", "JWT Token Management",
            "Implement secure JWT refresh token mechanism with automatic renewal",
            "in-progress", "critical", "c3d4e5f6-7890-1234-cdef-345678901234",
            "bb2cc3dd-ee44-5ff6-6778-789012345678", "SPRINT-002", "EPIC-002",
            "Sprint 24", ["backend", "security", "jwt"], datetime(2025, 1, 27),
            5, 5, 1
        ),
        (
            "TASK-003", "User Profile Dashboard",
            "Create comprehensive user profile management page with avatar upload",
            "todo", "high", "e5f6g7h8-9012-3456-ef01-567890123456",
            "aa1bb2cc-dd33-4ee5-5ff6-678901234567", "SPRINT-001", "EPIC-001",
            "Sprint 23", ["frontend", "profile", "dashboard"], datetime(2025, 1, 30),
            8, 2, 1
        ),
        (
            "TASK-004", "Payment Gateway Integration",
            "Integrate Stripe payment gateway with webhook support for transaction updates",
            "todo", "critical", "g7h8i9j0-1234-5678-0123-789012345678",
            "bb2cc3dd-ee44-5ff6-6778-789012345678", None, "EPIC-002",
            "Backlog", ["payment", "stripe", "webhook"], datetime(2025, 3, 15),
            13, 0, 0
        ),
        (
            "TASK-005", "Mobile App Authentication",
            "Implement biometric authentication for mobile banking app",
            "in-progress", "critical", "c3d4e5f6-7890-1234-cdef-345678901234",
            "bb2cc3dd-ee44-5ff6-6778-789012345678", "SPRINT-003", "EPIC-004",
            "Sprint 25", ["mobile", "biometric", "security"], datetime(2025, 2, 5),
            8, 4, 1
        ),
        (
            "TASK-006", "Product Search Functionality",
            "Build advanced product search with filters, sorting, and pagination",
            "todo", "medium", "f6g7h8i9-0123-4567-f012-678901234567",
            "cc3dd4ee-ff55-6667-7889-890123456789", None, "EPIC-003",
            "Backlog", ["search", "filters", "pagination"], datetime(2025, 4, 10),
            8, 1, 0
        ),
        (
            "TASK-007", "Transaction History API",
            "Create RESTful API for transaction history with filtering and export",
            "review", "high", "e5f6g7h8-9012-3456-ef01-567890123456",
            "bb2cc3dd-ee44-5ff6-6778-789012345678", "SPRINT-003", "EPIC-004",
            "Sprint 25", ["api", "transactions", "export"], datetime(2025, 1, 25),
            5, 6, 2
        ),
        (
            "TASK-008", "Responsive Design Implementation",
            "Implement responsive design for all major components and pages",
            "done", "medium", "f6g7h8i9-0123-4567-f012-678901234567",
            "aa1bb2cc-dd33-4ee5-5ff6-678901234567", "SPRINT-005", "EPIC-001",
            "Sprint 22", ["frontend", "responsive", "css"], datetime(2024, 12, 20),
            5, 3, 1
        ),
        (
            "TASK-009", "IoT Device Registration",
            "Create device registration flow with QR code scanning",
            "in-progress", "medium", "g7h8i9j0-1234-5678-0123-789012345678",
            "ff6gg7hh-8899-aabb-ccdd-eeff11223344", "SPRINT-006", None,
            "Sprint 27", ["iot", "registration", "qr-code"], datetime(2025, 1, 20),
            5, 2, 1
        ),
        (
            "TASK-010", "Real-time Monitoring Dashboard",
            "Build real-time dashboard for IoT device monitoring with live data",
            "todo", "high", "d4e5f6g7-8901-2345-def0-456789012345",
            "ff6gg7hh-8899-aabb-ccdd-eeff11223344", "SPRINT-006", None,
            "Sprint 27", ["dashboard", "real-time", "monitoring"], datetime(2025, 1, 22),
            8, 0, 0
        )
    ]

    for task in tasks:
        db.execute("""
            INSERT INTO tbl_project_tasks (
                id, title, description, status, priority, assignee_id, project_id,
                sprint_id, epic_id, sprint, labels, due_date, story_points,
                comments_count, attachments_count, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, task)

    print(f"   ✓ Inserted {len(tasks)} tasks")

def insert_backlog(db: Session):
    """Insert backlog mock data"""

    # Clear existing data
    db.execute(text("DELETE FROM tbl_project_backlog"))

    backlog_items = [
        (
            "STORY-001", "User Registration with Email Verification",
            "As a new user, I want to register with my email address and receive a verification link so that I can securely create an account",
            "User Story", "High", "Ready", "EPIC-001", "User Management System",
            "aa1bb2cc-dd33-4ee5-5ff6-678901234567", "Web App Redesign",
            "c3d4e5f6-7890-1234-cdef-345678901234", "Jane Smith",
            "g7h8i9j0-1234-5678-0123-789012345678", "Diana Miller",
            8, "High", "Medium", ["Authentication", "Email", "Security"],
            ["User can enter email and password on registration form", "System sends verification email to provided address", "User can click verification link to activate account", "Account remains inactive until email is verified"]
        ),
        (
            "STORY-002", "User Login with Social Media Integration",
            "As a returning user, I want to login using my social media accounts so that I can access the application quickly",
            "User Story", "Medium", "In Progress", "EPIC-001", "User Management System",
            "aa1bb2cc-dd33-4ee5-5ff6-678901234567", "Web App Redesign",
            "b2c3d4e5-6f78-9012-bcde-f23456789012", "John Doe",
            "d4e5f6g7-8901-2345-def0-456789012345", "Bob Wilson",
            13, "Medium", "High", ["Authentication", "Social Media", "OAuth"],
            ["User can login with Google account", "User can login with Facebook account", "User profile is populated with social media data", "Existing users can link social accounts to their profile"]
        ),
        (
            "BUG-001", "Password Reset Email Not Received",
            "Users report not receiving password reset emails when requested through the forgot password feature",
            "Bug", "Critical", "Review", "EPIC-001", "User Management System",
            "aa1bb2cc-dd33-4ee5-5ff6-678901234567", "Web App Redesign",
            "e5f6g7h8-9012-3456-ef01-567890123456", "Alice Brown",
            "h8i9j0k1-2345-6789-1234-890123456789", "Erik Johnson",
            5, "High", "Low", ["Bug", "Email", "Password Reset"],
            ["Password reset emails are delivered within 5 minutes", "Email delivery is logged for troubleshooting", "Users receive confirmation that email was sent", "Fallback mechanism exists for email delivery failures"]
        ),
        (
            "STORY-003", "Mobile Transaction History",
            "As a mobile banking user, I want to view my transaction history with filtering options so that I can track my spending",
            "User Story", "High", "Ready", "EPIC-004", "Mobile App Core Features",
            "bb2cc3dd-ee44-5ff6-6778-789012345678", "Mobile Banking App",
            "c3d4e5f6-7890-1234-cdef-345678901234", "Jane Smith",
            "e5f6g7h8-9012-3456-ef01-567890123456", "Alice Brown",
            8, "High", "Medium", ["Mobile", "Transactions", "History"],
            ["User can view last 30 days of transactions by default", "User can filter transactions by date range", "User can filter by transaction type and amount", "User can export transaction history as PDF"]
        ),
        (
            "STORY-004", "Biometric Authentication Setup",
            "As a mobile user, I want to set up biometric authentication so that I can access my account securely and quickly",
            "User Story", "Critical", "In Progress", "EPIC-004", "Mobile App Core Features",
            "bb2cc3dd-ee44-5ff6-6778-789012345678", "Mobile Banking App",
            "g7h8i9j0-1234-5678-0123-789012345678", "Diana Miller",
            "c3d4e5f6-7890-1234-cdef-345678901234", "Jane Smith",
            13, "Critical", "High", ["Biometric", "Security", "Authentication"],
            ["User can enable fingerprint authentication", "User can enable face recognition authentication", "Fallback to PIN if biometric fails", "User can disable biometric authentication"]
        ),
        (
            "FEATURE-001", "IoT Device Auto-Discovery",
            "Implement automatic discovery of IoT devices on the network for easier onboarding",
            "Feature", "Medium", "Ready", "EPIC-008", "IoT Device Management",
            "ff6gg7hh-8899-aabb-ccdd-eeff11223344", "IoT Device Management",
            "d4e5f6g7-8901-2345-def0-456789012345", "Bob Wilson",
            "f6g7h8i9-0123-4567-f012-678901234567", "Charlie Davis",
            8, "Medium", "Medium", ["IoT", "Discovery", "Network"],
            ["System scans network for IoT devices", "Discovered devices are listed with basic info", "Users can select devices to add to platform", "Auto-discovery can be scheduled or manual"]
        ),
        (
            "STORY-005", "Social Media Post Scheduling",
            "As a marketing manager, I want to schedule social media posts in advance so that I can maintain consistent content delivery",
            "User Story", "Medium", "Review", "EPIC-007", "Social Media Integration",
            "cc3dd4ee-ff55-6667-7889-890123456789", "E-commerce Platform",
            "f6g7h8i9-0123-4567-f012-678901234567", "Charlie Davis",
            "g7h8i9j0-1234-5678-0123-789012345678", "Diana Miller",
            8, "Medium", "Medium", ["Social Media", "Scheduling", "Content"],
            ["Users can create posts and set future publish time", "Posts are published automatically at scheduled time", "Users can edit or cancel scheduled posts", "Support for multiple social platforms"]
        ),
        (
            "TASK-011", "Cloud Infrastructure Security Audit",
            "Conduct comprehensive security audit of cloud infrastructure before migration",
            "Task", "Critical", "Ready", "EPIC-006", "Cloud Infrastructure Migration",
            "bb2cc3dd-ee44-5ff6-6778-789012345678", "Mobile Banking App",
            "d4e5f6g7-8901-2345-def0-456789012345", "Bob Wilson",
            "h8i9j0k1-2345-6789-1234-890123456789", "Erik Johnson",
            21, "Critical", "High", ["Security", "Audit", "Cloud"],
            ["All security policies are reviewed and documented", "Penetration testing is completed", "Compliance requirements are verified", "Security recommendations are provided"]
        )
    ]

    for item in backlog_items:
        db.execute("""
            INSERT INTO tbl_project_backlog (
                id, title, description, type, priority, status, epic_id, epic_title,
                project_id, project_name, assignee_id, assignee_name, reporter_id, reporter_name,
                story_points, business_value, effort, labels, acceptance_criteria, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, item)

    print(f"   ✓ Inserted {len(backlog_items)} backlog items")

if __name__ == "__main__":
    insert_project_data()