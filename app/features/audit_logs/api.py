from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core import deps
from app.features.users.crud import crud_user
from app.features.roles.crud import crud_role
from app.features.projects.crud import crud_project
from app.features.stories.crud import crud_story
from app.features.audit_logs.crud import crud_audit_log
# from app.crud import crud_audit_log
from app.db.database import get_db
from app.features.users.models import User
from app.features.audit_logs.schemas import AuditLog as AuditLogSchema

router = APIRouter()

@router.get("/", response_model=List[AuditLogSchema])
def read_audit_logs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(deps.require_permissions(["audit:read"]))
) -> Any:
    if user_id:
        logs = crud_audit_log.get_by_user(db, user_id=user_id)
    elif action:
        logs = crud_audit_log.get_by_action(db, action=action)
    elif status:
        logs = crud_audit_log.get_by_status(db, status=status)
    else:
        logs = crud_audit_log.get_multi(db, skip=skip, limit=limit)
    return logs

@router.get("/{log_id}", response_model=AuditLogSchema)
def read_audit_log(
    *,
    db: Session = Depends(get_db),
    log_id: str,
    current_user: User = Depends(deps.require_permissions(["audit:read"]))
) -> Any:
    log = crud_audit_log.get(db, id=log_id)
    if not log:
        raise HTTPException(
            status_code=404,
            detail="The audit log with this id does not exist in the system",
        )
    return log

@router.get("/user/{user_id}", response_model=List[AuditLogSchema])
def read_user_audit_logs(
    *,
    db: Session = Depends(get_db),
    user_id: str,
    current_user: User = Depends(deps.require_permissions(["audit:read"]))
) -> Any:
    logs = crud_audit_log.get_by_user(db, user_id=user_id)
    return logs

@router.get("/actions/list")
def get_available_actions(
    current_user: User = Depends(deps.require_permissions(["audit:read"]))
) -> Any:
    return {
        "actions": [
            "LOGIN", "LOGOUT", "LOGIN_FAILED",
            "CREATE", "UPDATE", "DELETE",
            "READ", "EXPORT", "IMPORT"
        ]
    }

@router.get("/stats/summary")
def get_audit_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_permissions(["audit:read"]))
) -> Any:
    all_logs = crud_audit_log.get_multi(db, limit=1000)

    stats = {
        "total_logs": len(all_logs),
        "success_count": len([log for log in all_logs if log.status == "success"]),
        "failure_count": len([log for log in all_logs if log.status == "failure"]),
        "warning_count": len([log for log in all_logs if log.status == "warning"]),
        "top_actions": {},
        "recent_activity": all_logs[:10]  # Last 10 logs
    }

    # Count actions
    action_counts = {}
    for log in all_logs:
        action_counts[log.action] = action_counts.get(log.action, 0) + 1

    stats["top_actions"] = dict(sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:5])

    return stats