from sqlalchemy import Boolean, Column, String, DateTime, Text, Integer, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Task(Base):
    __tablename__ = "tbl_project_tasks"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, nullable=False)  # backlog, todo, in-progress, review, done
    priority = Column(String, nullable=False)  # low, medium, high, critical
    assignee_id = Column(String, ForeignKey("tbl_users.id"))
    project_id = Column(String, ForeignKey("tbl_projects.id"))
    sprint_id = Column(String, ForeignKey("tbl_project_sprints.id"))
    epic_id = Column(String, ForeignKey("tbl_project_epics.id"))
    sprint = Column(String)  # Keep for backward compatibility
    labels = Column(ARRAY(String))
    due_date = Column(DateTime(timezone=True))
    story_points = Column(Integer)
    comments_count = Column(Integer, default=0)
    attachments_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    assignee = relationship("User", back_populates="assigned_tasks")
    project = relationship("Project", back_populates="tasks")
    sprint_obj = relationship("Sprint", back_populates="tasks", foreign_keys=[sprint_id])
    epic_obj = relationship("Epic", back_populates="tasks", foreign_keys=[epic_id])