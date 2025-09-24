from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from app.core import deps
from app.core.pagination import PaginatedResponse
from app.features.users.crud import crud_user
from app.features.roles.crud import crud_role
from app.features.projects.crud import crud_project
from app.features.stories.crud import crud_story
from app.features.audit_logs.crud import crud_audit_log
from app.db.database import get_db
from app.features.users.models import User
from app.features.stories.schemas import Story as StorySchema, StoryCreate, StoryUpdate
from app.features.audit_logs.schemas import AuditLogCreate

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[StorySchema])
def read_stories(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(default="created_at", description="Field to sort by"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Sort order"),
    search: Optional[str] = Query(default=None, description="Search in title and description"),
    status: Optional[str] = Query(default=None, description="Filter by story status"),
    priority: Optional[str] = Query(default=None, description="Filter by priority"),
    story_type: Optional[str] = Query(default=None, description="Filter by type (story, task, bug)"),
    assignee_id: Optional[str] = Query(default=None, description="Filter by assignee"),
    project_id: Optional[str] = Query(default=None, description="Filter by project"),
    epic_id: Optional[str] = Query(default=None, description="Filter by epic"),
    label: Optional[str] = Query(default=None, description="Filter by label"),
    current_user: User = Depends(deps.require_permissions(["story:read"]))
) -> Any:
    """
    Get stories with advanced filtering, pagination, and sorting

    **Supported sort fields:** id, title, status, priority, type, story_points, created_at, updated_at

    **Search:** Searches in story title and description fields.

    **Filters:**
    - status: Filter by story status (backlog, todo, in-progress, review, done)
    - priority: Filter by priority (low, medium, high, critical)
    - story_type: Filter by type (story, task, bug)
    - assignee_id: Filter by assignee user ID
    - project_id: Filter by project ID
    - epic_id: Filter by epic ID
    - label: Filter by specific label
    """
    stories, total = crud_story.get_stories_with_filters(
        db=db,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
        status=status,
        priority=priority,
        story_type=story_type,
        assignee_id=assignee_id,
        project_id=project_id,
        epic_id=epic_id,
        label=label
    )

    return PaginatedResponse.create(
        items=stories,
        total=total,
        page=page,
        per_page=per_page
    )

@router.post("/", response_model=StorySchema)
def create_story(
    *,
    request: Request,
    db: Session = Depends(get_db),
    story_in: StoryCreate,
    current_user: User = Depends(deps.require_permissions(["story:write"]))
) -> Any:
    story = crud_story.create(db, obj_in=story_in)

    # Log story creation
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="CREATE",
        resource="Story",
        details=f"Created new {story.story_type}: {story.title}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return story

@router.put("/{story_id}", response_model=StorySchema)
def update_story(
    *,
    request: Request,
    db: Session = Depends(get_db),
    story_id: str,
    story_in: StoryUpdate,
    current_user: User = Depends(deps.require_permissions(["story:write"]))
) -> Any:
    story = crud_story.get(db, id=story_id)
    if not story:
        raise HTTPException(
            status_code=404,
            detail="The story with this id does not exist in the system",
        )

    old_status = story.status
    story = crud_story.update(db, db_obj=story, obj_in=story_in)

    # Log story update with status change details
    details = f"Updated {story.story_type}: {story.title}"
    if story_in.status and old_status != story_in.status:
        details += f" (Status changed from '{old_status}' to '{story_in.status}')"

    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="UPDATE",
        resource="Story",
        details=details,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return story

@router.get("/{story_id}", response_model=StorySchema)
def read_story(
    *,
    db: Session = Depends(get_db),
    story_id: str,
    current_user: User = Depends(deps.require_permissions(["story:read"]))
) -> Any:
    story = crud_story.get(db, id=story_id)
    if not story:
        raise HTTPException(
            status_code=404,
            detail="The story with this id does not exist in the system",
        )
    return story

@router.delete("/{story_id}", response_model=StorySchema)
def delete_story(
    *,
    request: Request,
    db: Session = Depends(get_db),
    story_id: str,
    current_user: User = Depends(deps.require_permissions(["story:delete"]))
) -> Any:
    story = crud_story.get(db, id=story_id)
    if not story:
        raise HTTPException(
            status_code=404,
            detail="The story with this id does not exist in the system",
        )

    story = crud_story.remove(db, id=story_id)

    # Log story deletion
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="DELETE",
        resource="Story",
        details=f"Deleted {story.story_type}: {story.title}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return story

@router.get("/status/{status}", response_model=List[StorySchema])
def read_stories_by_status(
    *,
    db: Session = Depends(get_db),
    status: str,
    current_user: User = Depends(deps.require_permissions(["story:read"]))
) -> Any:
    stories = crud_story.get_by_status(db, status=status)
    return stories

@router.get("/assignee/{assignee_id}", response_model=List[StorySchema])
def read_stories_by_assignee(
    *,
    db: Session = Depends(get_db),
    assignee_id: str,
    current_user: User = Depends(deps.require_permissions(["story:read"]))
) -> Any:
    stories = crud_story.get_by_assignee(db, assignee_id=assignee_id)
    return stories

@router.get("/project/{project_id}", response_model=List[StorySchema])
def read_stories_by_project(
    *,
    db: Session = Depends(get_db),
    project_id: str,
    current_user: User = Depends(deps.require_permissions(["story:read"]))
) -> Any:
    stories = crud_story.get_by_project(db, project_id=project_id)
    return stories

@router.get("/type/{story_type}", response_model=List[StorySchema])
def read_stories_by_type(
    *,
    db: Session = Depends(get_db),
    story_type: str,
    current_user: User = Depends(deps.require_permissions(["story:read"]))
) -> Any:
    stories = crud_story.get_by_type(db, story_type=story_type)
    return stories

@router.get("/board/kanban")
def get_kanban_board(
    db: Session = Depends(get_db),
    project_id: Optional[str] = Query(None, description="Filter by project"),
    story_type: Optional[str] = Query(None, description="Filter by type"),
    current_user: User = Depends(deps.require_permissions(["story:read"]))
) -> Any:
    if project_id:
        all_stories = crud_story.get_by_project(db, project_id=project_id)
    else:
        all_stories = crud_story.get_multi(db, limit=1000)

    # Filter by type if specified
    if story_type:
        all_stories = [story for story in all_stories if story.story_type == story_type]

    board = {
        "backlog": [story for story in all_stories if story.status == "backlog"],
        "todo": [story for story in all_stories if story.status == "todo"],
        "in_progress": [story for story in all_stories if story.status == "in-progress"],
        "review": [story for story in all_stories if story.status == "review"],
        "done": [story for story in all_stories if story.status == "done"]
    }

    return board

@router.get("/stats/overview")
def get_story_stats(
    db: Session = Depends(get_db),
    project_id: Optional[str] = Query(None, description="Filter by project"),
    current_user: User = Depends(deps.require_permissions(["story:read"]))
) -> Any:
    if project_id:
        all_stories = crud_story.get_by_project(db, project_id=project_id)
    else:
        all_stories = crud_story.get_multi(db, limit=1000)

    stats = {
        "total_stories": len(all_stories),
        "by_type": {
            "stories": len([s for s in all_stories if s.story_type == "story"]),
            "tasks": len([s for s in all_stories if s.story_type == "task"]),
            "bugs": len([s for s in all_stories if s.story_type == "bug"])
        },
        "by_status": {
            "backlog": len([s for s in all_stories if s.status == "backlog"]),
            "todo": len([s for s in all_stories if s.status == "todo"]),
            "in_progress": len([s for s in all_stories if s.status == "in-progress"]),
            "review": len([s for s in all_stories if s.status == "review"]),
            "done": len([s for s in all_stories if s.status == "done"])
        },
        "total_story_points": sum([s.story_points or 0 for s in all_stories]),
        "completed_story_points": sum([s.story_points or 0 for s in all_stories if s.status == "done"]),
        "high_priority_items": len([s for s in all_stories if s.priority in ["high", "critical"]])
    }

    return stats

@router.get("/priorities/list")
def get_story_priorities(
    current_user: User = Depends(deps.require_permissions(["story:read"]))
) -> Any:
    return {
        "priorities": ["low", "medium", "high", "critical"]
    }

@router.get("/statuses/list")
def get_story_statuses(
    current_user: User = Depends(deps.require_permissions(["story:read"]))
) -> Any:
    return {
        "statuses": ["backlog", "todo", "in-progress", "review", "done"]
    }

@router.get("/types/list")
def get_story_types(
    current_user: User = Depends(deps.require_permissions(["story:read"]))
) -> Any:
    return {
        "types": ["story", "task", "bug"]
    }