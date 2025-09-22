from sqlalchemy import Boolean, Column, String, DateTime, ForeignKey, Text, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class User(Base):
    __tablename__ = "tbl_users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role_id = Column(String, ForeignKey("tbl_roles.id"), nullable=False)
    user_profile = Column(String)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    department = Column(String)
    skills = Column(ARRAY(String))
    phone = Column(String)
    timezone = Column(String)

    # Relationships
    role = relationship("Role", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")
    assigned_stories = relationship("Story", back_populates="assignee", foreign_keys="Story.assignee_id")
    reported_stories = relationship("Story", back_populates="reporter", foreign_keys="Story.reporter_id")
    managed_projects = relationship("Project", back_populates="team_lead")
    managed_sprints = relationship("Sprint", back_populates="scrum_master")
    assigned_epics = relationship("Epic", back_populates="assignee")

    # File relationships
    uploaded_files = relationship("File", back_populates="uploaded_by", foreign_keys="File.uploaded_by_id")
    deleted_files = relationship("File", back_populates="deleted_by", foreign_keys="File.deleted_by_id")
    created_folders = relationship("FileFolder", back_populates="created_by", foreign_keys="FileFolder.created_by_id")
    deleted_folders = relationship("FileFolder", back_populates="deleted_by", foreign_keys="FileFolder.deleted_by_id")
