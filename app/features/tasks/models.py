from sqlalchemy import Boolean, Column, String, DateTime, Text, Integer, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, nullable=False)  # backlog, todo, in-progress, review, done
    priority = Column(String, nullable=False)  # low, medium, high, critical
    assignee_id = Column(String, ForeignKey("users.id"))
    project_id = Column(String, ForeignKey("projects.id"))
    sprint = Column(String)
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