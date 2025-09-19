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
    avatar = Column(String)
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
    assigned_backlog_items = relationship("Backlog", foreign_keys="Backlog.assignee_id", back_populates="assignee")
    reported_backlog_items = relationship("Backlog", foreign_keys="Backlog.reporter_id", back_populates="reporter")