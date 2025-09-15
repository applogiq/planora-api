#!/usr/bin/env python3
"""
Initialize Planora PostgreSQL database with tables
"""

import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.base import Base
from app.models import *  # Import all models

def main():
    """Initialize database tables"""
    print("Initializing Planora database...")
    print(f"Database URL: {settings.DATABASE_URL}")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"Connected to: {version}")
        
        # Create all tables
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
        
        # Verify tables were created
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result.fetchall()]
            print(f"Created {len(tables)} tables:")
            for table in tables:
                print(f"  - {table}")
                
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    print("\nDatabase initialization completed!")
    print("You can now use the Planora API with PostgreSQL.")
    return True

if __name__ == "__main__":
    main()