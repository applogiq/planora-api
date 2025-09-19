#!/usr/bin/env python3
"""
Create database tables using SQLAlchemy
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from app.db.database import engine, Base

def create_tables():
    """Create all database tables in correct order"""
    print("Creating all database tables...")

    # Import all models to ensure they're registered with Base
    from app.features.users.models import User
    from app.features.roles.models import Role
    from app.features.projects.models import Project
    from app.features.epics.models import Epic
    from app.features.sprints.models import Sprint
    from app.features.stories.models import Story
    from app.features.backlog.models import Backlog
    from app.features.audit_logs.models import AuditLog
    from app.features.masters.models import ProjectMethodology, ProjectType, ProjectStatus, Priority

    # Drop all tables first to ensure clean state
    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)

    # Create all tables
    print("Creating new tables...")
    Base.metadata.create_all(bind=engine)

    print("[SUCCESS] All tables created successfully!")

def create_tables_with_mock_data():
    """Create tables and insert comprehensive mock data"""
    # First create tables
    create_tables()

    # Then import and run the comprehensive mock data script
    print("\nInserting comprehensive mock data...")
    from insert_mock_data import create_tables_and_insert_data
    create_tables_and_insert_data()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--with-mock-data":
        create_tables_with_mock_data()
    else:
        create_tables()