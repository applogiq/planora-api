from sqlalchemy import Boolean, Column, String, DateTime, Text, Integer, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Epic(Base):
    __tablename__ = "tbl_project_epics"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    priority = Column(String, nullable=False)  # Low, Medium, High, Critical, Urgent
    status = Column(String, nullable=False)  # To Do, In Progress, Review, Done, Cancelled
    project_id = Column(String, ForeignKey("tbl_projects.id"), nullable=False)
    assignee_id = Column(String, ForeignKey("tbl_users.id"))
    due_date = Column(DateTime(timezone=True))
    total_story_points = Column(Integer, default=0)
    completed_story_points = Column(Integer, default=0)
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    labels = Column(ARRAY(String))
    business_value = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="epics")
    assignee = relationship("User", back_populates="assigned_epics")
    stories = relationship("Story", back_populates="epic", foreign_keys="Story.epic_id")
    backlog_items = relationship("Backlog", back_populates="epic")