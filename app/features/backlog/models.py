from sqlalchemy import Boolean, Column, String, DateTime, Text, Integer, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Backlog(Base):
    __tablename__ = "tbl_project_backlog"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    type = Column(String, nullable=False)  # User Story, Bug, Epic, Task, etc.
    priority = Column(String, nullable=False)  # Low, Medium, High, Critical
    status = Column(String, nullable=False)  # Ready, In Progress, Review, Done, etc.
    epic_id = Column(String, ForeignKey("tbl_project_epics.id"))
    epic_title = Column(String)
    project_id = Column(String, ForeignKey("tbl_projects.id"))
    project_name = Column(String)
    assignee_id = Column(String, ForeignKey("tbl_users.id"))
    assignee_name = Column(String)
    reporter_id = Column(String, ForeignKey("tbl_users.id"))
    reporter_name = Column(String)
    story_points = Column(Integer)
    business_value = Column(String)  # High, Medium, Low
    effort = Column(String)  # High, Medium, Low
    labels = Column(ARRAY(String))
    acceptance_criteria = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    epic = relationship("Epic", back_populates="backlog_items")
    project = relationship("Project", back_populates="backlog_items")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_backlog_items")
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="reported_backlog_items")