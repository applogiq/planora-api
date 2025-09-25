import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.features.masters.models import ProjectMethodology, ProjectType, ProjectStatus, Priority, Department, Industry, TaskStatus
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

        # Insert Departments
        print("Inserting departments...")
        insert_departments(db)

        # Insert Industries
        print("Inserting industries...")
        insert_industries(db)

        # Insert Task Statuses
        print("Inserting task statuses...")
        insert_task_statuses(db)

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
            "name": "Scrum",
            "description": "Framework for developing and maintaining complex products with iterative sprints",
            "is_active": True,
            "sort_order": 1
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Kanban",
            "description": "Visual workflow management method for continuous delivery",
            "is_active": True,
            "sort_order": 2
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Waterfall",
            "description": "Linear sequential approach to project management with distinct phases",
            "is_active": True,
            "sort_order": 3
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

def insert_departments(db: Session):
    """Insert department master data"""
    departments_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Engineering",
            "description": "Software development and technical teams",
            "is_active": True,
            "sort_order": 1
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Product Management",
            "description": "Product strategy and roadmap management",
            "is_active": True,
            "sort_order": 2
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Design",
            "description": "User experience and interface design teams",
            "is_active": True,
            "sort_order": 3
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Quality Assurance",
            "description": "Software testing and quality control",
            "is_active": True,
            "sort_order": 4
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Infrastructure",
            "description": "Infrastructure and deployment operations",
            "is_active": True,
            "sort_order": 5
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Marketing",
            "description": "Marketing and promotional activities",
            "is_active": True,
            "sort_order": 6
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Sales",
            "description": "Sales and business development",
            "is_active": True,
            "sort_order": 7
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Operations",
            "description": "Business operations and process management",
            "is_active": True,
            "sort_order": 8
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Finance",
            "description": "Financial planning and accounting",
            "is_active": True,
            "sort_order": 9
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Human Resources",
            "description": "HR and talent management",
            "is_active": True,
            "sort_order": 10
        },
        {
            "id": str(uuid.uuid4()),
            "name": "IT",
            "description": "Information technology and system administration",
            "is_active": True,
            "sort_order": 11
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Management",
            "description": "Executive and senior management",
            "is_active": True,
            "sort_order": 12
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Customer Support",
            "description": "Customer service and technical support",
            "is_active": True,
            "sort_order": 13
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Data Analytics",
            "description": "Data analysis and business intelligence",
            "is_active": True,
            "sort_order": 14
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Security",
            "description": "Information security and compliance",
            "is_active": True,
            "sort_order": 15
        }
    ]

    for department_data in departments_data:
        # Check if department already exists
        existing = db.query(Department).filter(Department.name == department_data["name"]).first()
        if not existing:
            db_department = Department(**department_data)
            db.add(db_department)

    db.commit()
    print(f"[SUCCESS] Inserted {len(departments_data)} departments")

def insert_industries(db: Session):
    """Insert industry master data"""
    industries_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Technology",
            "description": "Technology and software development companies",
            "is_active": True,
            "sort_order": 1
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Healthcare",
            "description": "Healthcare and medical services industry",
            "is_active": True,
            "sort_order": 2
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Finance",
            "description": "Banking, finance, and insurance services",
            "is_active": True,
            "sort_order": 3
        },
        {
            "id": str(uuid.uuid4()),
            "name": "E-commerce",
            "description": "Online retail and e-commerce platforms",
            "is_active": True,
            "sort_order": 4
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Education",
            "description": "Educational institutions and e-learning platforms",
            "is_active": True,
            "sort_order": 5
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Manufacturing",
            "description": "Manufacturing and industrial production",
            "is_active": True,
            "sort_order": 6
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Media & Entertainment",
            "description": "Media, entertainment, and content creation",
            "is_active": True,
            "sort_order": 7
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Real Estate",
            "description": "Real estate and property management",
            "is_active": True,
            "sort_order": 8
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Transportation",
            "description": "Transportation and logistics services",
            "is_active": True,
            "sort_order": 9
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Energy",
            "description": "Energy and utilities sector",
            "is_active": True,
            "sort_order": 10
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Telecommunications",
            "description": "Telecommunications and network services",
            "is_active": True,
            "sort_order": 11
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Agriculture",
            "description": "Agriculture and food production",
            "is_active": True,
            "sort_order": 12
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Consulting",
            "description": "Consulting and professional services",
            "is_active": True,
            "sort_order": 13
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Non-Profit",
            "description": "Non-profit organizations and NGOs",
            "is_active": True,
            "sort_order": 14
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Government",
            "description": "Government and public sector",
            "is_active": True,
            "sort_order": 15
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Retail",
            "description": "Traditional retail and brick-and-mortar stores",
            "is_active": True,
            "sort_order": 16
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Automotive",
            "description": "Automotive industry and vehicle manufacturing",
            "is_active": True,
            "sort_order": 17
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Travel & Tourism",
            "description": "Travel, tourism, and hospitality services",
            "is_active": True,
            "sort_order": 18
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Gaming",
            "description": "Gaming and interactive entertainment",
            "is_active": True,
            "sort_order": 19
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Cryptocurrency",
            "description": "Blockchain and cryptocurrency industry",
            "is_active": True,
            "sort_order": 20
        }
    ]

    for industry_data in industries_data:
        # Check if industry already exists
        existing = db.query(Industry).filter(Industry.name == industry_data["name"]).first()
        if not existing:
            db_industry = Industry(**industry_data)
            db.add(db_industry)

    db.commit()
    print(f"[SUCCESS] Inserted {len(industries_data)} industries")

def insert_task_statuses(db: Session):
    """Insert task status master data"""
    statuses_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Active",
            "description": "Task is Active",
            "color": "#28A745",
            "is_active": True,
            "sort_order": 1
        },
        {
            "id": str(uuid.uuid4()),
            "name": "In Progress",
            "description": "Task is In Progress",
            "color": "#17A2B8",
            "is_active": True,
            "sort_order": 2
        },
        {
            "id": str(uuid.uuid4()),
            "name": "On Hold",
            "description": "Task is temporarily paused",
            "color": "#FFC107",
            "is_active": True,
            "sort_order": 3
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Completed",
            "description": "Task has been completed successfully",
            "color": "#007BFF",
            "is_active": True,
            "sort_order": 4
        }
    ]

    for status_data in statuses_data:
        # Check if task status already exists
        existing = db.query(TaskStatus).filter(TaskStatus.name == status_data["name"]).first()
        if not existing:
            db_status = TaskStatus(**status_data)
            db.add(db_status)

    db.commit()
    print(f"[SUCCESS] Inserted {len(statuses_data)} task statuses")

if __name__ == "__main__":
    insert_master_data()