#!/usr/bin/env python3
"""
Mockup data for master tables (priorities, statuses, types, methodologies)
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
import uuid

def insert_master_data():
    """Insert mock data for all master tables"""

    db = SessionLocal()

    try:
        print("🔄 Inserting master data...")

        # Insert master data using direct SQL to avoid model issues
        insert_priorities(db)
        insert_project_statuses(db)
        insert_project_types(db)
        insert_project_methodologies(db)

        db.commit()
        print("✅ Master data inserted successfully!")

    except Exception as e:
        print(f"❌ Error inserting master data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def insert_priorities(db: Session):
    """Insert priority master data"""

    # Clear existing data
    db.execute(text("DELETE FROM tbl_master_priority"))

    priorities = [
        (str(uuid.uuid4()), "Low", "Low priority tasks or projects", "#6C757D", 1, True, 1),
        (str(uuid.uuid4()), "Medium", "Medium priority tasks or projects", "#FFC107", 2, True, 2),
        (str(uuid.uuid4()), "High", "High priority tasks or projects", "#FD7E14", 3, True, 3),
        (str(uuid.uuid4()), "Critical", "Critical priority tasks or projects", "#DC3545", 4, True, 4),
        (str(uuid.uuid4()), "Urgent", "Urgent priority requiring immediate attention", "#E83E8C", 5, True, 5)
    ]

    for priority in priorities:
        db.execute(text("""
            INSERT INTO tbl_master_priority (id, name, description, color, level, is_active, sort_order, created_at)
            VALUES (:id, :name, :description, :color, :level, :is_active, :sort_order, NOW())
        """), {
            "id": priority[0], "name": priority[1], "description": priority[2],
            "color": priority[3], "level": priority[4], "is_active": priority[5], "sort_order": priority[6]
        })

    print(f"   ✓ Inserted {len(priorities)} priorities")

def insert_project_statuses(db: Session):
    """Insert project status master data"""

    # Clear existing data
    db.execute(text("DELETE FROM tbl_master_project_status"))

    statuses = [
        (str(uuid.uuid4()), "Planning", "Project is in planning phase", "#6C757D", True, 1),
        (str(uuid.uuid4()), "Active", "Project is actively being worked on", "#28A745", True, 2),
        (str(uuid.uuid4()), "On Hold", "Project is temporarily paused", "#FFC107", True, 3),
        (str(uuid.uuid4()), "Completed", "Project has been completed successfully", "#007BFF", True, 4),
        (str(uuid.uuid4()), "Cancelled", "Project has been cancelled", "#DC3545", True, 5),
        (str(uuid.uuid4()), "Archived", "Project has been archived", "#6C757D", True, 6)
    ]

    for status in statuses:
        db.execute(text("""
            INSERT INTO tbl_master_project_status (id, name, description, color, is_active, sort_order, created_at)
            VALUES (:id, :name, :description, :color, :is_active, :sort_order, NOW())
        """), {
            "id": status[0], "name": status[1], "description": status[2],
            "color": status[3], "is_active": status[4], "sort_order": status[5]
        })

    print(f"   ✓ Inserted {len(statuses)} project statuses")

def insert_project_types(db: Session):
    """Insert project type master data"""

    # Clear existing data
    db.execute(text("DELETE FROM tbl_master_project_type"))

    types = [
        (str(uuid.uuid4()), "Software Development", "Development of software applications and systems", True, 1),
        (str(uuid.uuid4()), "Mobile Development", "Development of mobile applications", True, 2),
        (str(uuid.uuid4()), "Web Development", "Development of websites and web applications", True, 3),
        (str(uuid.uuid4()), "Data Analytics", "Projects focused on data analysis and insights", True, 4),
        (str(uuid.uuid4()), "AI/ML Development", "Artificial Intelligence and Machine Learning projects", True, 5),
        (str(uuid.uuid4()), "Infrastructure", "IT infrastructure and system administration projects", True, 6),
        (str(uuid.uuid4()), "Marketing Technology", "Marketing automation and analytics platforms", True, 7),
        (str(uuid.uuid4()), "IoT Development", "Internet of Things and connected device projects", True, 8),
        (str(uuid.uuid4()), "Blockchain Development", "Blockchain and cryptocurrency related projects", True, 9),
        (str(uuid.uuid4()), "Media Technology", "Video, audio, and media processing platforms", True, 10)
    ]

    for project_type in types:
        db.execute(text("""
            INSERT INTO tbl_master_project_type (id, name, description, is_active, sort_order, created_at)
            VALUES (:id, :name, :description, :is_active, :sort_order, NOW())
        """), {
            "id": project_type[0], "name": project_type[1], "description": project_type[2],
            "is_active": project_type[3], "sort_order": project_type[4]
        })

    print(f"   ✓ Inserted {len(types)} project types")

def insert_project_methodologies(db: Session):
    """Insert project methodology master data"""

    # Clear existing data
    db.execute(text("DELETE FROM tbl_master_project_methodology"))

    methodologies = [
        (str(uuid.uuid4()), "Agile", "Iterative and incremental approach to project management", True, 1),
        (str(uuid.uuid4()), "Scrum", "Framework for developing and maintaining complex products", True, 2),
        (str(uuid.uuid4()), "Waterfall", "Linear sequential approach to project management", True, 3),
        (str(uuid.uuid4()), "Kanban", "Visual workflow management method", True, 4),
        (str(uuid.uuid4()), "DevOps", "Combination of development and operations practices", True, 5),
        (str(uuid.uuid4()), "Lean", "Methodology focused on maximizing value and minimizing waste", True, 6)
    ]

    for methodology in methodologies:
        db.execute(text("""
            INSERT INTO tbl_master_project_methodology (id, name, description, is_active, sort_order, created_at)
            VALUES (:id, :name, :description, :is_active, :sort_order, NOW())
        """), {
            "id": methodology[0], "name": methodology[1], "description": methodology[2],
            "is_active": methodology[3], "sort_order": methodology[4]
        })

    print(f"   ✓ Inserted {len(methodologies)} project methodologies")

if __name__ == "__main__":
    insert_master_data()