from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from . import crud, schemas

router = APIRouter()

@router.get("/project", response_model=schemas.ProjectMastersResponse, summary="Get Project Master Data")
def get_project_masters(db: Session = Depends(get_db)):
    """
    Get all project-related master data including:
    - Project methodologies (Agile, Scrum, Waterfall, etc.)
    - Project types (Software Development, Research, etc.)
    - Project statuses (Active, On Hold, Completed, etc.)
    - Priority levels (Low, Medium, High, Critical)

    Returns a comprehensive object containing all master data for projects.
    """
    try:
        masters_data = crud.get_all_project_masters(db)
        return schemas.ProjectMastersResponse(
            methodologies=[schemas.ProjectMethodologyResponse.from_orm(item) for item in masters_data["methodologies"]],
            types=[schemas.ProjectTypeResponse.from_orm(item) for item in masters_data["types"]],
            statuses=[schemas.ProjectStatusResponse.from_orm(item) for item in masters_data["statuses"]],
            priorities=[schemas.PriorityResponse.from_orm(item) for item in masters_data["priorities"]]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching master data: {str(e)}")

@router.get("/methodology", response_model=List[schemas.ProjectMethodologyResponse], summary="Get Project Methodologies")
def get_project_methodologies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all active project methodologies.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    """
    methodologies = crud.get_project_methodologies(db, skip=skip, limit=limit)
    return [schemas.ProjectMethodologyResponse.from_orm(methodology) for methodology in methodologies]

@router.get("/type", response_model=List[schemas.ProjectTypeResponse], summary="Get Project Types")
def get_project_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all active project types.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    """
    types = crud.get_project_types(db, skip=skip, limit=limit)
    return [schemas.ProjectTypeResponse.from_orm(project_type) for project_type in types]

@router.get("/status", response_model=List[schemas.ProjectStatusResponse], summary="Get Project Statuses")
def get_project_statuses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all active project statuses.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    """
    statuses = crud.get_project_statuses(db, skip=skip, limit=limit)
    return [schemas.ProjectStatusResponse.from_orm(status) for status in statuses]

@router.get("/priority", response_model=List[schemas.PriorityResponse], summary="Get Priority Levels")
def get_priorities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all active priority levels.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    """
    priorities = crud.get_priorities(db, skip=skip, limit=limit)
    return [schemas.PriorityResponse.from_orm(priority) for priority in priorities]