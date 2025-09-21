from sqlalchemy import Boolean, Column, String, DateTime, Text, Integer, Float, JSON
from sqlalchemy.sql import func
from app.db.database import Base

class Customer(Base):
    __tablename__ = "tbl_customers"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    industry = Column(String)

    # Contact information stored as JSON
    contact = Column(JSON)

    website = Column(String)

    # Address information stored as JSON
    address = Column(JSON)

    status = Column(String, default="Active")
    join_date = Column(DateTime(timezone=True))
    last_activity = Column(DateTime(timezone=True))
    total_revenue = Column(Float, default=0.0)

    # Project IDs stored as JSON array
    project_ids = Column(JSON, default=list)

    priority = Column(String, default="Medium")
    notes = Column(Text)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())