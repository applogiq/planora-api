from sqlalchemy import Boolean, Column, String, DateTime, Text, Integer, Float, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, nullable=False)  # Active, On Hold, Completed, Planning
    progress = Column(Integer, default=0)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    budget = Column(Float)
    spent = Column(Float, default=0.0)
    customer = Column(String)
    customer_id = Column(String)
    priority = Column(String)  # Low, Medium, High, Critical
    team_lead_id = Column(String, ForeignKey("users.id"))
    team_members = Column(ARRAY(String))
    tags = Column(ARRAY(String))
    color = Column(String)
    methodology = Column(String)  # Agile, Waterfall, Scrum, Kanban, etc.
    project_type = Column(String)  # Software Development, Research, Marketing, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    team_lead = relationship("User", back_populates="managed_projects")
    tasks = relationship("Task", back_populates="project")