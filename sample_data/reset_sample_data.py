#!/usr/bin/env python3
"""
Reset all sample data in the Planora API database
WARNING: This will delete ALL data in the database!
"""

import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.base import Base

def reset_database():
    """Reset the database by dropping and recreating all tables"""
    print("⚠️  WARNING: This will DELETE ALL DATA in the database!")
    print(f"Database: {settings.DATABASE_URL}")
    
    # Double confirmation
    response1 = input("\nAre you absolutely sure you want to continue? (yes/no): ").strip().lower()
    if response1 != 'yes':
        print("Reset cancelled.")
        return False
    
    response2 = input("Type 'DELETE ALL DATA' to confirm: ").strip()
    if response2 != 'DELETE ALL DATA':
        print("Reset cancelled.")
        return False
    
    try:
        print("\n🗄️  Connecting to database...")
        engine = create_engine(settings.DATABASE_URL)
        
        # Test connection
        with engine.connect() as connection:
            if "sqlite" in settings.DATABASE_URL:
                result = connection.execute(text("SELECT sqlite_version()"))
                version = f"SQLite {result.fetchone()[0]}"
            else:
                result = connection.execute(text("SELECT version()"))
                version = result.fetchone()[0]
            print(f"Connected to: {version}")
        
        print("\n🧹 Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped successfully")
        
        print("\n🔨 Creating fresh tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")
        
        # Verify tables were created
        with engine.connect() as connection:
            if "sqlite" in settings.DATABASE_URL:
                result = connection.execute(text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                """))
            else:
                result = connection.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """))
            
            tables = [row[0] for row in result.fetchall()]
            print(f"\n📋 Created {len(tables)} tables:")
            for table in tables:
                print(f"   • {table}")
        
        print(f"\n🎉 Database reset completed successfully!")
        print(f"💡 You can now run 'python sample_data/setup_all_data.py' to recreate sample data")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error resetting database: {e}")
        return False

def main():
    """Main function"""
    print("🔄 Planora API Database Reset")
    print("This script will completely reset the database and remove all data.")
    
    if reset_database():
        print("\n✅ Reset completed successfully!")
    else:
        print("\n❌ Reset failed!")

if __name__ == "__main__":
    main()