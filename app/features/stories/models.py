from sqlalchemy import Boolean, Column, String, DateTime, Text, Integer, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Story(Base):
    __tablename__ = "tbl_project_stories"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    type = Column(String, nullable=False)  # story, task, bug
    priority = Column(String, nullable=False)  # low, medium, high, critical
    status = Column(String, nullable=False)  # backlog, todo, in-progress, review, done
    epic_id = Column(String, ForeignKey("tbl_project_epics.id"))
    epic_title = Column(String)
    project_id = Column(String, ForeignKey("tbl_projects.id"))
    project_name = Column(String)
    sprint_id = Column(String, ForeignKey("tbl_project_sprints.id"))
    assignee_id = Column(String, ForeignKey("tbl_users.id"))
    assignee_name = Column(String)
    reporter_id = Column(String, ForeignKey("tbl_users.id"))
    reporter_name = Column(String)
    story_points = Column(Integer)
    business_value = Column(String)
    effort = Column(String)
    labels = Column(ARRAY(String))
    acceptance_criteria = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    assignee = relationship("User", back_populates="assigned_stories", foreign_keys=[assignee_id])
    reporter = relationship("User", back_populates="reported_stories", foreign_keys=[reporter_id])
    project = relationship("Project", back_populates="stories")
    epic = relationship("Epic", back_populates="stories", foreign_keys=[epic_id])
    sprint_obj = relationship("Sprint", back_populates="stories", foreign_keys=[sprint_id])