#!/usr/bin/env python3
"""
Database Setup Script for Planora API

This script sets up the database with all tables and optional mock data.
Run this script to initialize your database for development or testing.

Usage:
    python setup_database.py           # Create tables only
    python setup_database.py --mock    # Create tables with mock data
"""

import sys
import os
import argparse

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine
from app.models import user, role, project, task, audit_log
from app.db.database import Base
from app.db.database import SessionLocal
from app.db.init_db import init_db

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

    # Initialize with default data
    db = SessionLocal()
    try:
        init_db(db)
        print("✅ Database initialized with default data!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
    finally:
        db.close()

def create_tables_with_mock_data():
    """Create tables and insert comprehensive mock data"""
    try:
        # Import the comprehensive mock data script
        from insert_mock_data import create_tables_and_insert_data
        create_tables_and_insert_data()
        print("🎉 Database setup completed with mock data!")
    except Exception as e:
        print(f"❌ Error setting up database with mock data: {e}")
        print("You can try running run_mock_data.py separately if Unicode issues persist.")

def main():
    """Main function to handle command line arguments and execute setup"""
    parser = argparse.ArgumentParser(
        description="Setup Planora API Database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python setup_database.py           # Basic setup with default data
    python setup_database.py --mock    # Setup with comprehensive mock data
    python setup_database.py -m        # Short form for mock data
        """
    )

    parser.add_argument(
        '--mock', '-m',
        action='store_true',
        help='Include comprehensive mock data for testing and development'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("🚀 Planora API Database Setup")
    print("=" * 60)

    if args.mock:
        print("📦 Setting up database with mock data...")
        create_tables_with_mock_data()
    else:
        print("🔧 Setting up basic database...")
        create_tables()

    print("=" * 60)
    print("✅ Database setup completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()