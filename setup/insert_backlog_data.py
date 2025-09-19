#!/usr/bin/env python3
"""
Add Backlog table and insert mock data
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.features.backlog.models import Backlog
from app.db.database import Base
from datetime import datetime, timedelta
import uuid

def create_backlog_tables_and_insert_data():
    """Create backlog table and insert mock data"""

    # Create backlog table
    print("Creating backlog table...")
    Base.metadata.create_all(bind=engine)
    print("[SUCCESS] Backlog table created successfully!")

    # Get database session
    db = SessionLocal()

    try:
        # Insert sample backlog data
        print("Inserting backlog mock data...")

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
                "id": "STORY-002",
                "title": "User Login with Social Media Integration",
                "description": "As a returning user, I want to login using my social media accounts so that I can access the application quickly",
                "type": "User Story",
                "priority": "Medium",
                "status": "In Progress",
                "epic_id": "EPIC-001",
                "epic_title": "User Management System",
                "project_id": "aa1bb2cc-dd33-4ee5-5ff6-678901234567",
                "project_name": "Web App Redesign",
                "assignee_id": "b2c3d4e5-6f78-9012-bcde-f23456789012",
                "assignee_name": "John Doe",
                "reporter_id": "d4e5f6g7-8901-2345-ef01-890123456789",
                "reporter_name": "Michael Johnson",
                "story_points": 13,
                "business_value": "Medium",
                "effort": "High",
                "labels": ["Authentication", "Social Media", "OAuth"],
                "acceptance_criteria": [
                    "User can login with Google account",
                    "User can login with Facebook account",
                    "User profile is populated with social media data",
                    "Existing users can link social accounts to their profile"
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
                "assignee_id": "e5f6g7h8-9012-3456-f012-901234567890",
                "assignee_name": "Alex Chen",
                "reporter_id": "h8i9j0k1-2345-6789-0234-123456789012",
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
            },
            {
                "id": "STORY-003",
                "title": "Product Search with Advanced Filters",
                "description": "As a customer, I want to search for products using advanced filters so that I can find exactly what I'm looking for",
                "type": "User Story",
                "priority": "High",
                "status": "Done",
                "epic_id": "EPIC-003",
                "epic_title": "Product Catalog & Search",
                "project_id": "cc3dd4ee-ff55-6667-7889-890123456789",
                "project_name": "E-commerce Platform",
                "assignee_id": "k1l2m3n4-5678-9abc-4567-123456789abc",
                "assignee_name": "Emma Rodriguez",
                "reporter_id": "i9j0k1l2-3456-789a-1234-234567890123",
                "reporter_name": "Robert Wilson",
                "story_points": 21,
                "business_value": "High",
                "effort": "High",
                "labels": ["E-commerce", "Search", "Filters"],
                "acceptance_criteria": [
                    "Users can filter by price range",
                    "Users can filter by category",
                    "Users can filter by brand",
                    "Users can sort results by relevance, price, rating",
                    "Filter combinations work correctly"
                ]
            },
            {
                "id": "TASK-001",
                "title": "Set up Payment Gateway API Documentation",
                "description": "Create comprehensive API documentation for payment gateway integration including examples and error codes",
                "type": "Task",
                "priority": "Medium",
                "status": "Ready",
                "epic_id": "EPIC-002",
                "epic_title": "Payment Processing Integration",
                "project_id": "bb2cc3dd-ee44-5ff6-6778-789012345678",
                "project_name": "Mobile Banking App",
                "assignee_id": "f6g7h8i9-0123-4567-0123-012345678901",
                "assignee_name": "James Garcia",
                "reporter_id": "g7h8i9j0-1234-5678-0123-789012345678",
                "reporter_name": "Diana Miller",
                "story_points": 3,
                "business_value": "Medium",
                "effort": "Low",
                "labels": ["Documentation", "API", "Payment"],
                "acceptance_criteria": [
                    "All API endpoints are documented",
                    "Request/response examples are provided",
                    "Error codes and messages are listed",
                    "Authentication methods are explained"
                ]
            },
            {
                "id": "ENHANCEMENT-001",
                "title": "Real-time Dashboard Performance Optimization",
                "description": "Optimize dashboard loading times and implement real-time data updates without page refresh",
                "type": "Enhancement",
                "priority": "High",
                "status": "In Progress",
                "epic_id": "EPIC-004",
                "epic_title": "Real-time Analytics Dashboard",
                "project_id": "PROJ-004",
                "project_name": "Analytics Dashboard",
                "assignee_id": "o5p6q7r8-9abc-def0-89ab-56789abcdef0",
                "assignee_name": "Sarah Taylor",
                "reporter_id": "j0k1l2m3-4567-89ab-2345-345678901234",
                "reporter_name": "Christopher Brown",
                "story_points": 13,
                "business_value": "High",
                "effort": "Medium",
                "labels": ["Performance", "Real-time", "Dashboard"],
                "acceptance_criteria": [
                    "Dashboard loads in under 3 seconds",
                    "Data updates in real-time via WebSocket",
                    "Charts render smoothly without lag",
                    "Memory usage is optimized for long sessions"
                ]
            },
            {
                "id": "SPIKE-001",
                "title": "Research AI Chatbot NLP Libraries",
                "description": "Research and evaluate different NLP libraries for implementing the AI chatbot functionality",
                "type": "Spike",
                "priority": "Medium",
                "status": "Done",
                "epic_id": "EPIC-005",
                "epic_title": "AI Chatbot & Customer Support",
                "project_id": "aa1bb2cc-3dd4-5ee6-ff78-90ab12cd34ef",
                "project_name": "AI Chatbot Integration",
                "assignee_id": "s9t0u1v2-def0-1234-cdef-9abcdef01234",
                "assignee_name": "Natalie Clark",
                "reporter_id": "k1l2m3n4-5678-9abc-4567-567890123456",
                "reporter_name": "Amanda Martinez",
                "story_points": 8,
                "business_value": "Medium",
                "effort": "Medium",
                "labels": ["Research", "AI", "NLP"],
                "acceptance_criteria": [
                    "Evaluate at least 3 NLP libraries",
                    "Compare performance benchmarks",
                    "Assess integration complexity",
                    "Provide recommendation with pros/cons"
                ]
            },
            {
                "id": "STORY-004",
                "title": "Multi-signature Wallet Implementation",
                "description": "As a security-conscious user, I want to set up multi-signature wallet protection so that my funds require multiple approvals",
                "type": "User Story",
                "priority": "Critical",
                "status": "Ready",
                "epic_id": "EPIC-009",
                "epic_title": "Blockchain Wallet Security",
                "project_id": "ee5ff678-9012-ab34-cd56-ef789012345a",
                "project_name": "Blockchain Wallet",
                "assignee_id": "m3n4o5p6-789a-bcde-6789-3456789abcde",
                "assignee_name": "Olivia White",
                "reporter_id": "l2m3n4o5-6789-abcd-5678-678901234567",
                "reporter_name": "Kevin Thompson",
                "story_points": 34,
                "business_value": "Critical",
                "effort": "High",
                "labels": ["Blockchain", "Security", "Multi-sig"],
                "acceptance_criteria": [
                    "User can configure multi-signature requirements",
                    "Transactions require specified number of signatures",
                    "Co-signers receive notification for pending transactions",
                    "Time-based expiration for pending signatures"
                ]
            },
            {
                "id": "BUG-002",
                "title": "Video Streaming Buffering Issues",
                "description": "Users experience frequent buffering and poor video quality on mobile devices during peak hours",
                "type": "Bug",
                "priority": "High",
                "status": "In Progress",
                "epic_id": "EPIC-010",
                "epic_title": "Video Streaming Engine",
                "project_id": "ff67890a-bc12-def3-4567-890123456789",
                "project_name": "Video Streaming Platform",
                "assignee_id": "n4o5p6q7-89ab-cdef-789a-456789abcdef",
                "assignee_name": "Ryan Martinez",
                "reporter_id": "m3n4o5p6-789a-bcde-6789-789012345678",
                "reporter_name": "Jennifer Davis",
                "story_points": 21,
                "business_value": "High",
                "effort": "High",
                "labels": ["Bug", "Video", "Performance", "Mobile"],
                "acceptance_criteria": [
                    "Video starts playing within 2 seconds",
                    "Buffering occurs less than 5% of playback time",
                    "Adaptive bitrate adjusts to network conditions",
                    "Mobile performance matches desktop quality"
                ]
            },
            {
                "id": "FEATURE-001",
                "title": "IoT Device Auto-Discovery",
                "description": "Implement automatic discovery of IoT devices on the network for easier onboarding",
                "type": "Feature",
                "priority": "Medium",
                "status": "Ready",
                "epic_id": "EPIC-008",
                "epic_title": "IoT Device Management Platform",
                "project_id": "dd4ee5ff-6789-01ab-2cd3-ef4567890abc",
                "project_name": "IoT Device Management",
                "assignee_id": "l2m3n4o5-6789-abcd-5678-23456789abcd",
                "assignee_name": "David Thompson",
                "reporter_id": "n4o5p6q7-89ab-cdef-789a-890123456789",
                "reporter_name": "Stephanie Wilson",
                "story_points": 13,
                "business_value": "Medium",
                "effort": "Medium",
                "labels": ["IoT", "Discovery", "Automation"],
                "acceptance_criteria": [
                    "System scans network for IoT devices",
                    "Discovered devices are listed with basic info",
                    "Users can select devices to add to platform",
                    "Auto-discovery can be scheduled or manual"
                ]
            },
            {
                "id": "STORY-005",
                "title": "Social Media Post Scheduling",
                "description": "As a marketing manager, I want to schedule social media posts in advance so that I can maintain consistent content delivery",
                "type": "User Story",
                "priority": "Medium",
                "status": "Review",
                "epic_id": "EPIC-007",
                "epic_title": "Social Media Integration",
                "project_id": "cc3dd4ee-5ff6-7890-1ab2-cd34ef56789a",
                "project_name": "Social Media Dashboard",
                "assignee_id": "k1l2m3n4-5678-9abc-4567-123456789abc",
                "assignee_name": "Emma Rodriguez",
                "reporter_id": "o5p6q7r8-9abc-def0-89ab-901234567890",
                "reporter_name": "Mark Anderson",
                "story_points": 8,
                "business_value": "Medium",
                "effort": "Medium",
                "labels": ["Social Media", "Scheduling", "Content"],
                "acceptance_criteria": [
                    "Users can create posts and set future publish time",
                    "Posts are published automatically at scheduled time",
                    "Users can edit or cancel scheduled posts",
                    "Support for multiple social platforms"
                ]
            },
            {
                "id": "TASK-002",
                "title": "Cloud Infrastructure Security Audit",
                "description": "Conduct comprehensive security audit of cloud infrastructure before migration",
                "type": "Task",
                "priority": "Critical",
                "status": "Ready",
                "epic_id": "EPIC-006",
                "epic_title": "Cloud Infrastructure Migration",
                "project_id": "bb2cc3dd-4ee5-6ff7-8901-ab23cd45ef67",
                "project_name": "Cloud Migration",
                "assignee_id": "t0u1v2w3-ef01-2345-def0-abcdef012345",
                "assignee_name": "Daniel Lewis",
                "reporter_id": "p6q7r8s9-abcd-ef01-90ab-abc1234567890",
                "reporter_name": "Rachel Thompson",
                "story_points": 21,
                "business_value": "Critical",
                "effort": "High",
                "labels": ["Security", "Audit", "Cloud"],
                "acceptance_criteria": [
                    "All security policies are reviewed and documented",
                    "Penetration testing is completed",
                    "Compliance requirements are verified",
                    "Security recommendations are provided"
                ]
            }
        ]

        for item_data in backlog_data:
            db_item = Backlog(**item_data)
            db.add(db_item)

        db.commit()
        print(f"[SUCCESS] Inserted {len(backlog_data)} backlog items")

        print("\n" + "=" * 60)
        print("🎉 Backlog setup completed successfully!")
        print("\n📋 Backlog Data Summary:")
        print("   • 13 Backlog items across different projects")
        print("   • 5 User Stories")
        print("   • 2 Bugs")
        print("   • 2 Tasks")
        print("   • 1 Enhancement")
        print("   • 1 Feature")
        print("   • 1 Spike")
        print("   • 1 User Story (Multi-sig)")
        print("\n📊 Status Distribution:")
        print("   • 5 Ready items")
        print("   • 4 In Progress items")
        print("   • 3 Review items")
        print("   • 2 Done items")
        print("\n⚡ Priority Distribution:")
        print("   • 3 Critical priority")
        print("   • 6 High priority")
        print("   • 4 Medium priority")

        print("\n🚀 Backlog APIs available at:")
        print("   • GET /api/v1/backlog/ - List all backlog items")
        print("   • POST /api/v1/backlog/ - Create new backlog item")
        print("   • GET /api/v1/backlog/{id} - Get backlog item details")
        print("   • PUT /api/v1/backlog/{id} - Update backlog item")
        print("   • GET /api/v1/backlog/board/kanban - Kanban board view")
        print("   • GET /api/v1/backlog/stats/overview - Backlog statistics")
        print("   • GET /api/v1/backlog/status/{status} - Filter by status")
        print("   • GET /api/v1/backlog/type/{type} - Filter by type")
        print("   • GET /api/v1/backlog/priority/{priority} - Filter by priority")

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_backlog_tables_and_insert_data()