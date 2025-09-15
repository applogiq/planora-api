from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, func, Text
from sqlalchemy.dialects.postgresql import UUID, CITEXT
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=True)  # Made nullable since Tenant model is removed
    email = Column(CITEXT, nullable=False)
    password_hash = Column(String, nullable=True)  # null when SSO-only
    sso_subject = Column(String, nullable=True)  # SSO identifier
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    
    # Project relationships
    owned_projects = relationship("Project", foreign_keys="Project.owner_user_id", back_populates="owner")
    project_memberships = relationship("ProjectMember", back_populates="user", cascade="all, delete-orphan")
    
    # Task relationships
    assigned_tasks = relationship("Task", foreign_keys="Task.assignee_id", back_populates="assignee")
    reported_tasks = relationship("Task", foreign_keys="Task.reporter_id", back_populates="reporter")
    
    # Other relationships
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="uploader", cascade="all, delete-orphan")
    time_entries = relationship("TimeEntry", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    avatar_url = Column(String)
    bio = Column(Text)
    timezone = Column(String(50), default="UTC")
    
    # Relationships
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, name={self.first_name} {self.last_name})>"