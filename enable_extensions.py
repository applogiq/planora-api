#!/usr/bin/env python3
"""
Enable required PostgreSQL extensions for Planora
"""

import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.core.config import settings

def main():
    """Enable PostgreSQL extensions"""
    print("Enabling PostgreSQL extensions...")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as connection:
            # Enable extensions
            print("Enabling uuid-ossp extension...")
            connection.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
            
            print("Enabling citext extension...")
            connection.execute(text('CREATE EXTENSION IF NOT EXISTS "citext"'))
            
            connection.commit()
            
            # Verify extensions
            result = connection.execute(text("""
                SELECT extname FROM pg_extension 
                WHERE extname IN ('uuid-ossp', 'citext')
                ORDER BY extname
            """))
            
            extensions = [row[0] for row in result.fetchall()]
            print(f"Enabled extensions: {', '.join(extensions)}")
            
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    print("Extensions enabled successfully!")
    return True

if __name__ == "__main__":
    main()