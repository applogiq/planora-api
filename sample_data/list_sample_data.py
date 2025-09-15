#!/usr/bin/env python3
"""
List existing sample data in the Planora API database
Shows a summary of what data currently exists
"""

import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import (
    Tenant, User, UserProfile, Role, 
    Project, Task, Sprint, Board,
    TimeEntry, Timesheet,
    IntegrationProvider, AutomationRule, Webhook,
    Report, Dashboard
)

def list_sample_data():
    """List all sample data in the database"""
    print("Planora API Sample Data Summary")
    print(f"Database: {settings.DATABASE_URL}")
    print("="*60)
    
    try:
        # Create engine and session
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        # Core entities
        print("\nCORE ENTITIES")
        print("-" * 30)
        
        tenants = session.query(Tenant).all()
        print(f"Tenants: {len(tenants)}")
        for tenant in tenants:
            print(f"  • {tenant.name}")
        
        users = session.query(User).all()
        print(f"\nUsers: {len(users)}")
        for user in users:
            profile = session.query(UserProfile).filter(UserProfile.user_id == user.id).first()
            name = f"{profile.first_name} {profile.last_name}" if profile else "No Profile"
            print(f"  • {user.email} - {name}")
        
        roles = session.query(Role).all()
        print(f"\nRoles: {len(roles)}")
        for role in roles:
            print(f"  • {role.name}")
        
        # Project Management
        print("\nPROJECT MANAGEMENT")
        print("-" * 30)
        
        projects = session.query(Project).all()
        print(f"Projects: {len(projects)}")
        for project in projects:
            print(f"  • {project.key}: {project.name} ({project.status})")
        
        tasks = session.query(Task).all()
        print(f"\nTasks: {len(tasks)}")
        task_by_status = {}
        task_by_type = {}
        for task in tasks:
            task_by_status[task.status] = task_by_status.get(task.status, 0) + 1
            task_by_type[task.type] = task_by_type.get(task.type, 0) + 1
        
        print("  By Status:")
        for status, count in task_by_status.items():
            print(f"    - {status}: {count}")
        print("  By Type:")
        for task_type, count in task_by_type.items():
            print(f"    - {task_type}: {count}")
        
        sprints = session.query(Sprint).all()
        print(f"\nSprints: {len(sprints)}")
        for sprint in sprints:
            print(f"  • {sprint.name} ({sprint.state})")
        
        boards = session.query(Board).all()
        print(f"\nBoards: {len(boards)}")
        for board in boards:
            print(f"  • {board.name}")
        
        # Time & Resources
        print("\nTIME & RESOURCES")
        print("-" * 30)
        
        time_entries = session.query(TimeEntry).all()
        print(f"Time Entries: {len(time_entries)}")
        total_hours = sum(entry.minutes for entry in time_entries) / 60
        print(f"  • Total Hours Logged: {total_hours:.1f}")
        
        timesheets = session.query(Timesheet).all()
        print(f"\nTimesheets: {len(timesheets)}")
        timesheet_by_status = {}
        for timesheet in timesheets:
            timesheet_by_status[timesheet.status] = timesheet_by_status.get(timesheet.status, 0) + 1
        for status, count in timesheet_by_status.items():
            print(f"  • {status}: {count}")
        
        # Integrations & Automation
        print("\nINTEGRATIONS & AUTOMATION")
        print("-" * 30)
        
        providers = session.query(IntegrationProvider).all()
        print(f"Integration Providers: {len(providers)}")
        for provider in providers:
            print(f"  • {provider.display_name}")
        
        rules = session.query(AutomationRule).all()
        print(f"\nAutomation Rules: {len(rules)}")
        for rule in rules:
            print(f"  • {rule.name} ({'enabled' if rule.is_enabled else 'disabled'})")
        
        webhooks = session.query(Webhook).all()
        print(f"\nWebhooks: {len(webhooks)}")
        for webhook in webhooks:
            print(f"  • {webhook.name} ({'active' if webhook.is_active else 'inactive'})")
        
        # Reports & Analytics
        print("\nREPORTS & ANALYTICS")
        print("-" * 30)
        
        reports = session.query(Report).all()
        print(f"Reports: {len(reports)}")
        for report in reports:
            print(f"  • {report.name} ({report.report_type})")
        
        dashboards = session.query(Dashboard).all()
        print(f"\nDashboards: {len(dashboards)}")
        for dashboard in dashboards:
            print(f"  • {dashboard.name}")
        
        session.close()
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        
        if len(users) > 0:
            print("[OK] Sample data exists in the database")
            print(f"   - {len(users)} users across {len(tenants)} tenant(s)")
            print(f"   - {len(projects)} projects with {len(tasks)} tasks")
            print(f"   - {len(time_entries)} time entries totaling {total_hours:.1f} hours")
            print(f"   - {len(providers)} integrations and {len(rules)} automation rules")
            print(f"   - {len(reports)} reports and {len(dashboards)} dashboard(s)")
        else:
            print("[EMPTY] No sample data found in the database")
            print("TIP: Run 'python sample_data/setup_all_data.py' to create sample data")
        
    except Exception as e:
        print(f"[ERROR] Error accessing database: {e}")
        print("TIP: Make sure the database is running and accessible")

def main():
    """Main function"""
    list_sample_data()

if __name__ == "__main__":
    main()