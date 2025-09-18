import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.features.masters.models import ProjectMethodology, ProjectType, ProjectStatus, Priority
from app.db.database import Base
import uuid

def insert_master_data():
    """Insert initial master data for project-related lookups"""

    # Get database session
    db = SessionLocal()

    try:
        print("Inserting master data...")

        # Insert Project Methodologies
        print("Inserting project methodologies...")
        insert_project_methodologies(db)

        # Insert Project Types
        print("Inserting project types...")
        insert_project_types(db)

        # Insert Project Statuses
        print("Inserting project statuses...")
        insert_project_statuses(db)

        # Insert Priorities
        print("Inserting priorities...")
        insert_priorities(db)

        print("[SUCCESS] All master data inserted successfully!")

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        db.rollback()
    finally:
        db.close()

def insert_project_methodologies(db: Session):
    """Insert project methodology master data"""
    methodologies_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Agile",
            "description": "Iterative and incremental approach to project management",
            "is_active": True,
            "sort_order": 1
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Scrum",
            "description": "Framework for developing and maintaining complex products",
            "is_active": True,
            "sort_order": 2
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Waterfall",
            "description": "Linear sequential approach to project management",
            "is_active": True,
            "sort_order": 3
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Kanban",
            "description": "Visual workflow management method",
            "is_active": True,
            "sort_order": 4
        },
        {
            "id": str(uuid.uuid4()),
            "name": "DevOps",
            "description": "Combination of development and operations practices",
            "is_active": True,
            "sort_order": 5
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Lean",
            "description": "Methodology focused on maximizing value and minimizing waste",
            "is_active": True,
            "sort_order": 6
        }
    ]

    for methodology_data in methodologies_data:
        # Check if methodology already exists
        existing = db.query(ProjectMethodology).filter(ProjectMethodology.name == methodology_data["name"]).first()
        if not existing:
            db_methodology = ProjectMethodology(**methodology_data)
            db.add(db_methodology)

    db.commit()
    print(f"[SUCCESS] Inserted {len(methodologies_data)} project methodologies")

def insert_project_types(db: Session):
    """Insert project type master data"""
    types_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Software Development",
            "description": "Development of software applications and systems",
            "is_active": True,
            "sort_order": 1
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Mobile Development",
            "description": "Development of mobile applications",
            "is_active": True,
            "sort_order": 2
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Web Development",
            "description": "Development of websites and web applications",
            "is_active": True,
            "sort_order": 3
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Data Analytics",
            "description": "Projects focused on data analysis and insights",
            "is_active": True,
            "sort_order": 4
        },
        {
            "id": str(uuid.uuid4()),
            "name": "AI/ML Development",
            "description": "Artificial Intelligence and Machine Learning projects",
            "is_active": True,
            "sort_order": 5
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Infrastructure",
            "description": "IT infrastructure and system administration projects",
            "is_active": True,
            "sort_order": 6
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Research",
            "description": "Research and development projects",
            "is_active": True,
            "sort_order": 7
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Marketing Technology",
            "description": "Marketing automation and technology projects",
            "is_active": True,
            "sort_order": 8
        },
        {
            "id": str(uuid.uuid4()),
            "name": "IoT Development",
            "description": "Internet of Things development projects",
            "is_active": True,
            "sort_order": 9
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Blockchain Development",
            "description": "Blockchain and cryptocurrency projects",
            "is_active": True,
            "sort_order": 10
        }
    ]

    for type_data in types_data:
        # Check if type already exists
        existing = db.query(ProjectType).filter(ProjectType.name == type_data["name"]).first()
        if not existing:
            db_type = ProjectType(**type_data)
            db.add(db_type)

    db.commit()
    print(f"[SUCCESS] Inserted {len(types_data)} project types")

def insert_project_statuses(db: Session):
    """Insert project status master data"""
    statuses_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Planning",
            "description": "Project is in planning phase",
            "color": "#6C757D",
            "is_active": True,
            "sort_order": 1
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Active",
            "description": "Project is actively being worked on",
            "color": "#28A745",
            "is_active": True,
            "sort_order": 2
        },
        {
            "id": str(uuid.uuid4()),
            "name": "On Hold",
            "description": "Project is temporarily paused",
            "color": "#FFC107",
            "is_active": True,
            "sort_order": 3
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Completed",
            "description": "Project has been completed successfully",
            "color": "#007BFF",
            "is_active": True,
            "sort_order": 4
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Cancelled",
            "description": "Project has been cancelled",
            "color": "#DC3545",
            "is_active": True,
            "sort_order": 5
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Archive",
            "description": "Project has been archived",
            "color": "#6C757D",
            "is_active": True,
            "sort_order": 6
        }
    ]

    for status_data in statuses_data:
        # Check if status already exists
        existing = db.query(ProjectStatus).filter(ProjectStatus.name == status_data["name"]).first()
        if not existing:
            db_status = ProjectStatus(**status_data)
            db.add(db_status)

    db.commit()
    print(f"[SUCCESS] Inserted {len(statuses_data)} project statuses")

def insert_priorities(db: Session):
    """Insert priority master data"""
    priorities_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Low",
            "description": "Low priority tasks or projects",
            "color": "#6C757D",
            "level": 1,
            "is_active": True,
            "sort_order": 1
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Medium",
            "description": "Medium priority tasks or projects",
            "color": "#FFC107",
            "level": 2,
            "is_active": True,
            "sort_order": 2
        },
        {
            "id": str(uuid.uuid4()),
            "name": "High",
            "description": "High priority tasks or projects",
            "color": "#FD7E14",
            "level": 3,
            "is_active": True,
            "sort_order": 3
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Critical",
            "description": "Critical priority tasks or projects",
            "color": "#DC3545",
            "level": 4,
            "is_active": True,
            "sort_order": 4
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Urgent",
            "description": "Urgent priority requiring immediate attention",
            "color": "#E83E8C",
            "level": 5,
            "is_active": True,
            "sort_order": 5
        }
    ]

    for priority_data in priorities_data:
        # Check if priority already exists
        existing = db.query(Priority).filter(Priority.name == priority_data["name"]).first()
        if not existing:
            db_priority = Priority(**priority_data)
            db.add(db_priority)

    db.commit()
    print(f"[SUCCESS] Inserted {len(priorities_data)} priorities")

if __name__ == "__main__":
    insert_master_data()