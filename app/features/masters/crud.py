from sqlalchemy.orm import Session
from typing import List
from . import models

def get_project_methodologies(db: Session, skip: int = 0, limit: int = 100) -> List[models.ProjectMethodology]:
    return db.query(models.ProjectMethodology).filter(
        models.ProjectMethodology.is_active == True
    ).order_by(models.ProjectMethodology.sort_order, models.ProjectMethodology.name).offset(skip).limit(limit).all()

def get_project_types(db: Session, skip: int = 0, limit: int = 100) -> List[models.ProjectType]:
    return db.query(models.ProjectType).filter(
        models.ProjectType.is_active == True
    ).order_by(models.ProjectType.sort_order, models.ProjectType.name).offset(skip).limit(limit).all()

def get_project_statuses(db: Session, skip: int = 0, limit: int = 100) -> List[models.ProjectStatus]:
    return db.query(models.ProjectStatus).filter(
        models.ProjectStatus.is_active == True
    ).order_by(models.ProjectStatus.sort_order, models.ProjectStatus.name).offset(skip).limit(limit).all()

def get_priorities(db: Session, skip: int = 0, limit: int = 100) -> List[models.Priority]:
    return db.query(models.Priority).filter(
        models.Priority.is_active == True
    ).order_by(models.Priority.sort_order, models.Priority.level).offset(skip).limit(limit).all()

def get_all_project_masters(db: Session):
    return {
        "methodologies": get_project_methodologies(db),
        "types": get_project_types(db),
        "statuses": get_project_statuses(db),
        "priorities": get_priorities(db)
    }