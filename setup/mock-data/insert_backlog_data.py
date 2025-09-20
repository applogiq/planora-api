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
            },
            {
                "id": "STORY-006",
                "title": "Mobile App Push Notifications",
                "description": "As a user, I want to receive push notifications on my mobile device so that I stay updated on important events",
                "type": "User Story",
                "priority": "High",
                "status": "Ready",
                "epic_id": "EPIC-011",
                "epic_title": "Mobile App Enhancements",
                "project_id": "aa1bb2cc-dd33-4ee5-5ff6-678901234567",
                "project_name": "Mobile App Development",
                "assignee_id": "u1v2w3x4-f012-3456-0123-0123456789ab",
                "assignee_name": "Carlos Rodriguez",
                "reporter_id": "v2w3x4y5-0123-4567-1234-123456789abc",
                "reporter_name": "Michelle Parker",
                "story_points": 13,
                "business_value": "High",
                "effort": "Medium",
                "labels": ["Mobile", "Notifications", "Push"],
                "acceptance_criteria": [
                    "Users receive notifications for important events",
                    "Notifications can be enabled/disabled in settings",
                    "Rich notifications with actions are supported",
                    "Notification preferences are saved per user"
                ]
            },
            {
                "id": "BUG-003",
                "title": "Database Connection Pool Exhaustion",
                "description": "High traffic causes database connection pool exhaustion leading to application timeouts",
                "type": "Bug",
                "priority": "Critical",
                "status": "In Progress",
                "epic_id": "EPIC-012",
                "epic_title": "Performance & Scalability",
                "project_id": "bb2cc3dd-ee44-5ff6-6778-789012345678",
                "project_name": "Backend API Optimization",
                "assignee_id": "w3x4y5z6-1234-5678-2345-23456789abcd",
                "assignee_name": "Alexander Kim",
                "reporter_id": "x4y5z6a7-2345-6789-3456-3456789abcde",
                "reporter_name": "Victoria Lee",
                "story_points": 8,
                "business_value": "Critical",
                "effort": "Medium",
                "labels": ["Bug", "Database", "Performance", "Scalability"],
                "acceptance_criteria": [
                    "Connection pool size is optimized for load",
                    "Connection timeouts are handled gracefully",
                    "Monitoring alerts are set up for pool usage",
                    "Load testing validates the fix"
                ]
            },
            {
                "id": "FEATURE-002",
                "title": "Advanced Data Export Options",
                "description": "Implement multiple data export formats (CSV, Excel, JSON, PDF) with custom filtering",
                "type": "Feature",
                "priority": "Medium",
                "status": "Review",
                "epic_id": "EPIC-013",
                "epic_title": "Data Management & Export",
                "project_id": "cc3dd4ee-ff55-6667-7889-890123456789",
                "project_name": "Analytics Platform",
                "assignee_id": "y5z6a7b8-3456-789a-4567-456789abcdef",
                "assignee_name": "Isabella Chen",
                "reporter_id": "z6a7b8c9-4567-89ab-5678-56789abcdef0",
                "reporter_name": "Thomas Wilson",
                "story_points": 21,
                "business_value": "Medium",
                "effort": "High",
                "labels": ["Feature", "Export", "Data", "Formats"],
                "acceptance_criteria": [
                    "Support for CSV, Excel, JSON, and PDF exports",
                    "Custom date range filtering for exports",
                    "Large dataset exports are handled efficiently",
                    "Export progress indicator is shown to users"
                ]
            },
            {
                "id": "ENHANCEMENT-002",
                "title": "Two-Factor Authentication Enhancement",
                "description": "Enhance existing 2FA with support for hardware tokens and backup codes",
                "type": "Enhancement",
                "priority": "High",
                "status": "Ready",
                "epic_id": "EPIC-001",
                "epic_title": "User Management System",
                "project_id": "aa1bb2cc-dd33-4ee5-5ff6-678901234567",
                "project_name": "Security Enhancement",
                "assignee_id": "a7b8c9d0-5678-9abc-6789-6789abcdef01",
                "assignee_name": "Sebastian Torres",
                "reporter_id": "b8c9d0e1-6789-abcd-789a-789abcdef012",
                "reporter_name": "Grace Martinez",
                "story_points": 13,
                "business_value": "High",
                "effort": "Medium",
                "labels": ["Enhancement", "Security", "2FA", "Authentication"],
                "acceptance_criteria": [
                    "Support for FIDO2/WebAuthn hardware tokens",
                    "Backup recovery codes are generated",
                    "Multiple 2FA methods can be configured",
                    "Admin can enforce 2FA for specific roles"
                ]
            },
            {
                "id": "SPIKE-002",
                "title": "Microservices Architecture Research",
                "description": "Research the feasibility of migrating to microservices architecture and evaluate tools",
                "type": "Spike",
                "priority": "Medium",
                "status": "Ready",
                "epic_id": "EPIC-014",
                "epic_title": "Architecture Modernization",
                "project_id": "dd4ee5ff-6789-01ab-2cd3-ef4567890abc",
                "project_name": "Architecture Refactoring",
                "assignee_id": "c9d0e1f2-789a-bcde-89ab-89abcdef0123",
                "assignee_name": "Lucas Johnson",
                "reporter_id": "d0e1f2g3-89ab-cdef-9abc-9abcdef01234",
                "reporter_name": "Sophia Adams",
                "story_points": 8,
                "business_value": "Medium",
                "effort": "Medium",
                "labels": ["Research", "Architecture", "Microservices"],
                "acceptance_criteria": [
                    "Evaluate at least 3 microservices frameworks",
                    "Assess migration complexity and timeline",
                    "Analyze performance and scalability benefits",
                    "Provide detailed recommendation report"
                ]
            },
            {
                "id": "STORY-007",
                "title": "Real-time Chat Integration",
                "description": "As a user, I want to communicate with team members in real-time so that we can collaborate effectively",
                "type": "User Story",
                "priority": "Medium",
                "status": "In Progress",
                "epic_id": "EPIC-015",
                "epic_title": "Team Collaboration Tools",
                "project_id": "ee5ff678-9012-ab34-cd56-ef789012345a",
                "project_name": "Collaboration Platform",
                "assignee_id": "e1f2g3h4-9abc-def0-abcd-abcdef012345",
                "assignee_name": "Maya Patel",
                "reporter_id": "f2g3h4i5-abcd-ef01-bcde-bcdef0123456",
                "reporter_name": "Jacob Miller",
                "story_points": 21,
                "business_value": "Medium",
                "effort": "High",
                "labels": ["Chat", "Real-time", "Collaboration"],
                "acceptance_criteria": [
                    "Users can send and receive messages instantly",
                    "Support for file sharing in chat",
                    "Group chat functionality with channels",
                    "Message history and search capabilities"
                ]
            },
            {
                "id": "BUG-004",
                "title": "Memory Leak in Image Processing",
                "description": "Memory usage continuously increases during batch image processing operations",
                "type": "Bug",
                "priority": "High",
                "status": "Review",
                "epic_id": "EPIC-016",
                "epic_title": "Media Processing Engine",
                "project_id": "ff67890a-bc12-def3-4567-890123456789",
                "project_name": "Media Processing Service",
                "assignee_id": "g3h4i5j6-bcde-f012-cdef-cdef01234567",
                "assignee_name": "Ethan Brown",
                "reporter_id": "h4i5j6k7-cdef-0123-def0-def012345678",
                "reporter_name": "Ava Wilson",
                "story_points": 13,
                "business_value": "High",
                "effort": "Medium",
                "labels": ["Bug", "Memory", "Performance", "Images"],
                "acceptance_criteria": [
                    "Memory usage remains stable during processing",
                    "All image objects are properly disposed",
                    "Batch processing completes without errors",
                    "Memory monitoring shows no leaks"
                ]
            },
            {
                "id": "TASK-003",
                "title": "API Rate Limiting Implementation",
                "description": "Implement rate limiting for public APIs to prevent abuse and ensure fair usage",
                "type": "Task",
                "priority": "High",
                "status": "Ready",
                "epic_id": "EPIC-017",
                "epic_title": "API Security & Management",
                "project_id": "aa1bb2cc-dd33-4ee5-5ff6-678901234567",
                "project_name": "API Gateway Enhancement",
                "assignee_id": "i5j6k7l8-def0-1234-f012-f01234567890",
                "assignee_name": "Noah Davis",
                "reporter_id": "j6k7l8m9-f012-3456-0123-012345678901",
                "reporter_name": "Emma Thompson",
                "story_points": 8,
                "business_value": "High",
                "effort": "Medium",
                "labels": ["API", "Security", "Rate Limiting"],
                "acceptance_criteria": [
                    "Rate limits are configurable per endpoint",
                    "Different limits for authenticated vs anonymous users",
                    "Clear error messages when limits are exceeded",
                    "Rate limit headers are included in responses"
                ]
            },
            {
                "id": "FEATURE-003",
                "title": "Advanced Search with AI",
                "description": "Implement AI-powered search with natural language processing and semantic understanding",
                "type": "Feature",
                "priority": "Medium",
                "status": "Ready",
                "epic_id": "EPIC-018",
                "epic_title": "AI-Powered Features",
                "project_id": "bb2cc3dd-ee44-5ff6-6778-789012345678",
                "project_name": "AI Search Engine",
                "assignee_id": "k7l8m9n0-0123-4567-2345-234567890123",
                "assignee_name": "Zoe Garcia",
                "reporter_id": "l8m9n0o1-1234-5678-3456-345678901234",
                "reporter_name": "Connor Lee",
                "story_points": 34,
                "business_value": "Medium",
                "effort": "High",
                "labels": ["AI", "Search", "NLP", "Machine Learning"],
                "acceptance_criteria": [
                    "Natural language queries are understood",
                    "Semantic search returns relevant results",
                    "Search suggestions are AI-powered",
                    "Performance is optimized for real-time use"
                ]
            },
            {
                "id": "ENHANCEMENT-003",
                "title": "Dark Mode Theme Implementation",
                "description": "Implement comprehensive dark mode theme across all application interfaces",
                "type": "Enhancement",
                "priority": "Low",
                "status": "Ready",
                "epic_id": "EPIC-019",
                "epic_title": "User Experience Improvements",
                "project_id": "cc3dd4ee-ff55-6667-7889-890123456789",
                "project_name": "UI/UX Enhancement",
                "assignee_id": "m9n0o1p2-2345-6789-4567-456789012345",
                "assignee_name": "Lily Wang",
                "reporter_id": "n0o1p2q3-3456-789a-5678-567890123456",
                "reporter_name": "Hunter Martinez",
                "story_points": 13,
                "business_value": "Low",
                "effort": "Medium",
                "labels": ["UI", "Theme", "Dark Mode", "Accessibility"],
                "acceptance_criteria": [
                    "All components support dark mode",
                    "Theme can be toggled by user preference",
                    "Color contrast meets accessibility standards",
                    "Theme preference is saved per user"
                ]
            },
            {
                "id": "STORY-008",
                "title": "Automated Testing Framework",
                "description": "As a developer, I want an automated testing framework so that we can ensure code quality and catch regressions",
                "type": "User Story",
                "priority": "High",
                "status": "In Progress",
                "epic_id": "EPIC-020",
                "epic_title": "Development Process Automation",
                "project_id": "dd4ee5ff-6789-01ab-2cd3-ef4567890abc",
                "project_name": "DevOps Pipeline",
                "assignee_id": "o1p2q3r4-4567-89ab-6789-678901234567",
                "assignee_name": "Aaron Clark",
                "reporter_id": "p2q3r4s5-5678-9abc-789a-789012345678",
                "reporter_name": "Chloe Rodriguez",
                "story_points": 21,
                "business_value": "High",
                "effort": "High",
                "labels": ["Testing", "Automation", "CI/CD", "Quality"],
                "acceptance_criteria": [
                    "Unit tests run automatically on commits",
                    "Integration tests validate API endpoints",
                    "Test coverage reports are generated",
                    "Failed tests block deployment pipeline"
                ]
            },
            {
                "id": "BUG-005",
                "title": "File Upload Size Limit Issue",
                "description": "Large file uploads fail silently without proper error messages or progress indication",
                "type": "Bug",
                "priority": "Medium",
                "status": "Ready",
                "epic_id": "EPIC-021",
                "epic_title": "File Management System",
                "project_id": "aa1bb2cc-dd33-4ee5-5ff6-678901234567",
                "project_name": "Document Management",
                "assignee_id": "q3r4s5t6-6789-abcd-89ab-89abcdef0123",
                "assignee_name": "Sophie Turner",
                "reporter_id": "r4s5t6u7-789a-bcde-9abc-9abcdef01234",
                "reporter_name": "Oliver Johnson",
                "story_points": 5,
                "business_value": "Medium",
                "effort": "Low",
                "labels": ["Bug", "File Upload", "User Experience"],
                "acceptance_criteria": [
                    "Clear error messages for oversized files",
                    "Progress bar shows upload status",
                    "File size limits are clearly displayed",
                    "Chunked upload for large files"
                ]
            },
            {
                "id": "STORY-009",
                "title": "Advanced User Permissions",
                "description": "As an admin, I want to set granular permissions for users so that I can control access to specific features",
                "type": "User Story",
                "priority": "High",
                "status": "Ready",
                "epic_id": "EPIC-022",
                "epic_title": "Advanced Access Control",
                "project_id": "bb2cc3dd-ee44-5ff6-6778-789012345678",
                "project_name": "Security Management",
                "assignee_id": "s5t6u7v8-89ab-cdef-abcd-abcdef012345",
                "assignee_name": "Marcus Williams",
                "reporter_id": "t6u7v8w9-9abc-def0-bcde-bcdef0123456",
                "reporter_name": "Elena Garcia",
                "story_points": 21,
                "business_value": "High",
                "effort": "High",
                "labels": ["Security", "Permissions", "Admin", "Access Control"],
                "acceptance_criteria": [
                    "Granular permissions can be assigned per feature",
                    "Role-based permission templates are available",
                    "Permission changes take effect immediately",
                    "Audit log tracks permission modifications"
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
        print("   • 25 Backlog items across different projects")
        print("   • 8 User Stories")
        print("   • 4 Bugs")
        print("   • 3 Tasks")
        print("   • 3 Enhancements")
        print("   • 3 Features")
        print("   • 2 Spikes")
        print("   • 2 Additional specialized items")
        print("\n📊 Status Distribution:")
        print("   • 10 Ready items")
        print("   • 8 In Progress items")
        print("   • 5 Review items")
        print("   • 2 Done items")
        print("\n⚡ Priority Distribution:")
        print("   • 4 Critical priority")
        print("   • 12 High priority")
        print("   • 8 Medium priority")
        print("   • 1 Low priority")

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