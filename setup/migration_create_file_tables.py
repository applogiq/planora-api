"""
Migration script to create file management tables

This script creates the necessary tables for file management:
- tbl_files: Store file metadata and associations
- tbl_file_folders: Store folder structure
- tbl_storage_quotas: Track storage usage and limits

Usage:
    python setup/migration_create_file_tables.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings

def create_file_tables():
    """Create file management tables"""

    engine = create_engine(settings.DATABASE_URL)

    # SQL statements to create tables
    sql_statements = [
        # Create tbl_files table
        """
        CREATE TABLE IF NOT EXISTS tbl_files (
            id VARCHAR PRIMARY KEY,
            filename VARCHAR NOT NULL,
            original_filename VARCHAR NOT NULL,
            file_path VARCHAR NOT NULL,
            file_size BIGINT NOT NULL,
            content_type VARCHAR NOT NULL,
            file_extension VARCHAR NOT NULL,
            category VARCHAR NOT NULL,
            entity_type VARCHAR NOT NULL,
            entity_id VARCHAR NOT NULL,
            entity_title VARCHAR,
            description TEXT,
            tags VARCHAR,
            is_public BOOLEAN DEFAULT FALSE,
            uploaded_by_id VARCHAR NOT NULL,
            uploaded_by_name VARCHAR NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE,
            is_deleted BOOLEAN DEFAULT FALSE,
            deleted_at TIMESTAMP WITH TIME ZONE,
            deleted_by_id VARCHAR,
            FOREIGN KEY (uploaded_by_id) REFERENCES tbl_users(id),
            FOREIGN KEY (deleted_by_id) REFERENCES tbl_users(id)
        )
        """,

        # Create tbl_file_folders table
        """
        CREATE TABLE IF NOT EXISTS tbl_file_folders (
            id VARCHAR PRIMARY KEY,
            name VARCHAR NOT NULL,
            description TEXT,
            entity_type VARCHAR NOT NULL,
            entity_id VARCHAR NOT NULL,
            parent_folder_id VARCHAR,
            created_by_id VARCHAR NOT NULL,
            created_by_name VARCHAR NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE,
            is_deleted BOOLEAN DEFAULT FALSE,
            deleted_at TIMESTAMP WITH TIME ZONE,
            deleted_by_id VARCHAR,
            FOREIGN KEY (parent_folder_id) REFERENCES tbl_file_folders(id),
            FOREIGN KEY (created_by_id) REFERENCES tbl_users(id),
            FOREIGN KEY (deleted_by_id) REFERENCES tbl_users(id)
        )
        """,

        # Create tbl_storage_quotas table
        """
        CREATE TABLE IF NOT EXISTS tbl_storage_quotas (
            id VARCHAR PRIMARY KEY,
            entity_type VARCHAR NOT NULL,
            entity_id VARCHAR NOT NULL,
            total_quota_bytes BIGINT NOT NULL DEFAULT 10737418240,
            used_bytes BIGINT DEFAULT 0,
            max_files INTEGER DEFAULT 1000,
            current_files INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE,
            UNIQUE(entity_type, entity_id)
        )
        """,

        # Create indexes for better performance
        """
        CREATE INDEX IF NOT EXISTS idx_files_entity ON tbl_files(entity_type, entity_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_files_category ON tbl_files(category);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_files_uploaded_by ON tbl_files(uploaded_by_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_files_created_at ON tbl_files(created_at);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_files_is_deleted ON tbl_files(is_deleted);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_file_folders_entity ON tbl_file_folders(entity_type, entity_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_file_folders_parent ON tbl_file_folders(parent_folder_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_storage_quotas_entity ON tbl_storage_quotas(entity_type, entity_id);
        """
    ]

    try:
        with engine.connect() as connection:
            for sql in sql_statements:
                print(f"Executing: {sql.strip()[:50]}...")
                connection.execute(text(sql))
                connection.commit()

        print("✅ File management tables created successfully!")
        print("\nCreated tables:")
        print("- tbl_files: File metadata and associations")
        print("- tbl_file_folders: Folder structure")
        print("- tbl_storage_quotas: Storage usage tracking")
        print("\nCreated indexes for optimal performance")

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

    return True

def create_default_storage_quotas():
    """Create default storage quotas for existing entities"""

    engine = create_engine(settings.DATABASE_URL)

    try:
        with engine.connect() as connection:
            # Create default quotas for existing projects
            projects_sql = """
            INSERT INTO tbl_storage_quotas (id, entity_type, entity_id, total_quota_bytes, max_files)
            SELECT
                'quota_' || p.id,
                'project',
                p.id,
                10737418240,  -- 10GB
                1000
            FROM tbl_projects p
            WHERE NOT EXISTS (
                SELECT 1 FROM tbl_storage_quotas sq
                WHERE sq.entity_type = 'project' AND sq.entity_id = p.id
            )
            """

            connection.execute(text(projects_sql))
            connection.commit()

        print("✅ Default storage quotas created for existing projects!")

    except Exception as e:
        print(f"❌ Error creating default quotas: {e}")
        return False

    return True

if __name__ == "__main__":
    print("🚀 Creating file management tables...")

    if create_file_tables():
        create_default_storage_quotas()
        print("\n🎉 File management system setup complete!")
        print("\nYou can now use the file management API endpoints:")
        print("- POST /api/v1/files/{entity_type}/{entity_id}/upload")
        print("- GET /api/v1/files/{entity_type}/{entity_id}/list")
        print("- GET /api/v1/files/search")
        print("- GET /api/v1/files/{file_id}/download")
        print("- PUT /api/v1/files/{file_id}")
        print("- DELETE /api/v1/files/{file_id}")
    else:
        print("❌ Setup failed!")
        sys.exit(1)