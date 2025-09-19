from sqlalchemy import Boolean, Column, String, DateTime, Text, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Sprint(Base):
    __tablename__ = "tbl_project_sprints"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)  # Planning, Active, Completed, Cancelled
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    goal = Column(Text)
    total_points = Column(Integer, default=0)
    completed_points = Column(Integer, default=0)
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    velocity = Column(Float, default=0.0)
    project_id = Column(String, ForeignKey("tbl_projects.id"))
    scrum_master_id = Column(String, ForeignKey("tbl_users.id"))
    team_size = Column(Integer, default=0)
    burndown_trend = Column(String)  # On Track, Behind, Ahead, At Risk
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="sprints")
    scrum_master = relationship("User", back_populates="managed_sprints")
    tasks = relationship("Task", back_populates="sprint_obj", foreign_keys="Task.sprint_id")