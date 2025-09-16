from app.db.database import engine
from app.models import user, role, project, task, audit_log
from app.db.database import Base
from app.db.database import SessionLocal
from app.db.init_db import init_db

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

    # Initialize with default data
    db = SessionLocal()
    try:
        init_db(db)
        print("Database initialized with default data!")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        db.close()

def create_tables_with_mock_data():
    """Create tables and insert comprehensive mock data"""
    # Import the comprehensive mock data script
    from insert_mock_data import create_tables_and_insert_data
    create_tables_and_insert_data()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--with-mock-data":
        create_tables_with_mock_data()
    else:
        create_tables()