from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, BigInteger, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class File(Base):
    __tablename__ = "tbl_files"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    content_type = Column(String, nullable=False)
    file_extension = Column(String, nullable=False)
    category = Column(String, nullable=False)  # document, image, video, audio, archive, other

    # Association with entities
    entity_type = Column(String, nullable=False)  # story, epic, project, sprint, task
    entity_id = Column(String, nullable=False)
    entity_title = Column(String)  # Cache entity title for quick display

    # File metadata
    description = Column(Text)
    tags = Column(String)  # Comma-separated tags
    is_public = Column(Boolean, default=False)

    # Audit fields
    uploaded_by_id = Column(String, ForeignKey("tbl_users.id"), nullable=False)
    uploaded_by_name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True))
    deleted_by_id = Column(String, ForeignKey("tbl_users.id"))

    # Relationships - temporarily disabled due to import issues
    # uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])
    # deleted_by = relationship("User", foreign_keys=[deleted_by_id])

class FileFolder(Base):
    __tablename__ = "tbl_file_folders"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)

    # Association with entities
    entity_type = Column(String, nullable=False)  # story, epic, project, sprint, task
    entity_id = Column(String, nullable=False)

    # Folder hierarchy
    parent_folder_id = Column(String, ForeignKey("tbl_file_folders.id"))

    # Audit fields
    created_by_id = Column(String, ForeignKey("tbl_users.id"), nullable=False)
    created_by_name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True))
    deleted_by_id = Column(String, ForeignKey("tbl_users.id"))

    # Relationships - temporarily disabled due to import issues
    # created_by = relationship("User", foreign_keys=[created_by_id])
    # deleted_by = relationship("User", foreign_keys=[deleted_by_id])
    # parent_folder = relationship("FileFolder", remote_side=[id])

class StorageQuota(Base):
    __tablename__ = "tbl_storage_quotas"

    id = Column(String, primary_key=True, index=True)
    entity_type = Column(String, nullable=False)  # project, user, global
    entity_id = Column(String, nullable=False)

    # Quota settings
    total_quota_bytes = Column(BigInteger, nullable=False, default=10737418240)  # 10GB default
    used_bytes = Column(BigInteger, default=0)

    # File count limits
    max_files = Column(Integer, default=1000)
    current_files = Column(Integer, default=0)

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())