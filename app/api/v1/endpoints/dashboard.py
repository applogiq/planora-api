from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core import deps
from app.crud import crud_user, crud_project, crud_task, crud_audit_log
from app.db.database import get_db
from app.models.user import User
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/overview")
def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    # Get basic counts
    total_users = len(crud_user.get_multi(db, limit=1000))
    total_projects = len(crud_project.get_multi(db, limit=1000))
    total_tasks = len(crud_task.get_multi(db, limit=1000))

    # Get active items
    active_projects = crud_project.get_active_projects(db)

    # Get user's assigned tasks
    user_tasks = crud_task.get_by_assignee(db, assignee_id=current_user.id)

    # Get recent activity
    recent_logs = crud_audit_log.get_multi(db, limit=10)

    # Task status distribution
    all_tasks = crud_task.get_multi(db, limit=1000)
    task_stats = {
        "backlog": len([t for t in all_tasks if t.status == "backlog"]),
        "todo": len([t for t in all_tasks if t.status == "todo"]),
        "in_progress": len([t for t in all_tasks if t.status == "in-progress"]),
        "review": len([t for t in all_tasks if t.status == "review"]),
        "done": len([t for t in all_tasks if t.status == "done"])
    }

    # Project status distribution
    all_projects = crud_project.get_multi(db, limit=1000)
    project_stats = {
        "active": len([p for p in all_projects if p.status == "Active"]),
        "planning": len([p for p in all_projects if p.status == "Planning"]),
        "on_hold": len([p for p in all_projects if p.status == "On Hold"]),
        "completed": len([p for p in all_projects if p.status == "Completed"])
    }

    return {
        "summary": {
            "total_users": total_users,
            "total_projects": total_projects,
            "total_tasks": total_tasks,
            "active_projects_count": len(active_projects)
        },
        "user_tasks": {
            "total": len(user_tasks),
            "in_progress": len([t for t in user_tasks if t.status == "in-progress"]),
            "pending": len([t for t in user_tasks if t.status in ["backlog", "todo"]])
        },
        "task_distribution": task_stats,
        "project_distribution": project_stats,
        "recent_activity": recent_logs[:5]
    }

@router.get("/user-workload")
def get_user_workload(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    user_tasks = crud_task.get_by_assignee(db, assignee_id=current_user.id)

    workload = {
        "user_id": current_user.id,
        "user_name": current_user.name,
        "total_tasks": len(user_tasks),
        "by_status": {
            "backlog": len([t for t in user_tasks if t.status == "backlog"]),
            "todo": len([t for t in user_tasks if t.status == "todo"]),
            "in_progress": len([t for t in user_tasks if t.status == "in-progress"]),
            "review": len([t for t in user_tasks if t.status == "review"]),
            "done": len([t for t in user_tasks if t.status == "done"])
        },
        "by_priority": {
            "low": len([t for t in user_tasks if t.priority == "low"]),
            "medium": len([t for t in user_tasks if t.priority == "medium"]),
            "high": len([t for t in user_tasks if t.priority == "high"]),
            "critical": len([t for t in user_tasks if t.priority == "critical"])
        },
        "story_points": {
            "total": sum([t.story_points or 0 for t in user_tasks]),
            "completed": sum([t.story_points or 0 for t in user_tasks if t.status == "done"])
        }
    }

    return workload

@router.get("/team-performance")
def get_team_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_permissions(["project:read", "team:read"]))
) -> Any:
    all_users = crud_user.get_multi(db, limit=1000)
    active_users = [user for user in all_users if user.is_active]

    team_performance = []

    for user in active_users:
        user_tasks = crud_task.get_by_assignee(db, assignee_id=user.id)

        performance = {
            "user_id": user.id,
            "user_name": user.name,
            "role": user.role.name if user.role else "No Role",
            "total_tasks": len(user_tasks),
            "completed_tasks": len([t for t in user_tasks if t.status == "done"]),
            "in_progress_tasks": len([t for t in user_tasks if t.status == "in-progress"]),
            "completion_rate": (len([t for t in user_tasks if t.status == "done"]) / len(user_tasks) * 100) if user_tasks else 0,
            "total_story_points": sum([t.story_points or 0 for t in user_tasks]),
            "completed_story_points": sum([t.story_points or 0 for t in user_tasks if t.status == "done"])
        }

        team_performance.append(performance)

    return {
        "team_size": len(active_users),
        "performance": team_performance
    }