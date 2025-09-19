from typing import Any, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core import deps
from app.features.users.crud import crud_user
from app.features.roles.crud import crud_role
from app.features.projects.crud import crud_project
from app.features.stories.crud import crud_story
from app.features.audit_logs.crud import crud_audit_log
# from app.crud import crud_project, crud_story, crud_user, crud_audit_log
from app.db.database import get_db
from app.features.users.models import User
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/project-progress")
def get_project_progress_report(
    db: Session = Depends(get_db),
    project_id: Optional[str] = Query(None, description="Specific project ID"),
    current_user: User = Depends(deps.require_permissions(["report:read"]))
) -> Any:
    if project_id:
        projects = [crud_project.get(db, id=project_id)]
        projects = [p for p in projects if p is not None]
    else:
        projects = crud_project.get_multi(db, limit=1000)

    report = []

    for project in projects:
        project_tasks = crud_story.get_by_project(db, project_id=project.id)

        project_report = {
            "project_id": project.id,
            "project_name": project.name,
            "status": project.status,
            "progress": project.progress,
            "budget": project.budget,
            "spent": project.spent,
            "budget_utilization": (project.spent / project.budget * 100) if project.budget else 0,
            "task_summary": {
                "total_tasks": len(project_tasks),
                "completed_tasks": len([t for t in project_tasks if t.status == "done"]),
                "in_progress_tasks": len([t for t in project_tasks if t.status == "in-progress"]),
                "pending_tasks": len([t for t in project_tasks if t.status in ["backlog", "todo"]])
            },
            "timeline": {
                "start_date": project.start_date,
                "end_date": project.end_date,
                "is_overdue": project.end_date < datetime.now() if project.end_date else False
            }
        }

        report.append(project_report)

    return {
        "generated_at": datetime.now(),
        "total_projects": len(report),
        "projects": report
    }

@router.get("/time-tracking")
def get_time_tracking_report(
    db: Session = Depends(get_db),
    user_id: Optional[str] = Query(None, description="Specific user ID"),
    project_id: Optional[str] = Query(None, description="Specific project ID"),
    current_user: User = Depends(deps.require_permissions(["report:read"]))
) -> Any:
    # Get tasks based on filters
    if user_id:
        tasks = crud_story.get_by_assignee(db, assignee_id=user_id)
    elif project_id:
        tasks = crud_story.get_by_project(db, project_id=project_id)
    else:
        tasks = crud_story.get_multi(db, limit=1000)

    # Group by user
    user_time_data = {}

    for task in tasks:
        if task.assignee_id:
            if task.assignee_id not in user_time_data:
                user = crud_user.get(db, id=task.assignee_id)
                user_time_data[task.assignee_id] = {
                    "user_id": task.assignee_id,
                    "user_name": user.name if user else "Unknown",
                    "total_story_points": 0,
                    "completed_story_points": 0,
                    "tasks_count": 0,
                    "completed_tasks": 0
                }

            user_time_data[task.assignee_id]["total_story_points"] += task.story_points or 0
            user_time_data[task.assignee_id]["tasks_count"] += 1

            if task.status == "done":
                user_time_data[task.assignee_id]["completed_story_points"] += task.story_points or 0
                user_time_data[task.assignee_id]["completed_tasks"] += 1

    return {
        "generated_at": datetime.now(),
        "time_tracking": list(user_time_data.values())
    }

@router.get("/productivity")
def get_productivity_report(
    db: Session = Depends(get_db),
    days: int = Query(30, description="Number of days to analyze"),
    current_user: User = Depends(deps.require_permissions(["report:read"]))
) -> Any:
    # Get recent audit logs for activity analysis
    all_logs = crud_audit_log.get_multi(db, limit=1000)

    # Filter logs by date range
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_logs = [log for log in all_logs if log.timestamp >= cutoff_date]

    # Activity by action type
    action_counts = {}
    for log in recent_logs:
        action_counts[log.action] = action_counts.get(log.action, 0) + 1

    # Daily activity
    daily_activity = {}
    for log in recent_logs:
        date_key = log.timestamp.date().isoformat()
        if date_key not in daily_activity:
            daily_activity[date_key] = 0
        daily_activity[date_key] += 1

    # User activity
    user_activity = {}
    for log in recent_logs:
        if log.user_id:
            if log.user_id not in user_activity:
                user_activity[log.user_id] = {
                    "user_id": log.user_id,
                    "user_name": log.user_name,
                    "activity_count": 0
                }
            user_activity[log.user_id]["activity_count"] += 1

    return {
        "generated_at": datetime.now(),
        "analysis_period": f"{days} days",
        "total_activities": len(recent_logs),
        "action_breakdown": action_counts,
        "daily_activity": daily_activity,
        "user_activity": list(user_activity.values())
    }

@router.get("/task-completion")
def get_task_completion_report(
    db: Session = Depends(get_db),
    project_id: Optional[str] = Query(None, description="Specific project ID"),
    current_user: User = Depends(deps.require_permissions(["report:read"]))
) -> Any:
    if project_id:
        tasks = crud_story.get_by_project(db, project_id=project_id)
    else:
        tasks = crud_story.get_multi(db, limit=1000)

    # Overall completion stats
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == "done"])
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # Completion by priority
    priority_stats = {}
    for priority in ["low", "medium", "high", "critical"]:
        priority_tasks = [t for t in tasks if t.priority == priority]
        priority_completed = [t for t in priority_tasks if t.status == "done"]
        priority_stats[priority] = {
            "total": len(priority_tasks),
            "completed": len(priority_completed),
            "completion_rate": (len(priority_completed) / len(priority_tasks) * 100) if priority_tasks else 0
        }

    # Completion by assignee
    assignee_stats = {}
    for task in tasks:
        if task.assignee_id:
            if task.assignee_id not in assignee_stats:
                user = crud_user.get(db, id=task.assignee_id)
                assignee_stats[task.assignee_id] = {
                    "user_id": task.assignee_id,
                    "user_name": user.name if user else "Unknown",
                    "total": 0,
                    "completed": 0
                }

            assignee_stats[task.assignee_id]["total"] += 1
            if task.status == "done":
                assignee_stats[task.assignee_id]["completed"] += 1

    # Calculate completion rates for assignees
    for stats in assignee_stats.values():
        stats["completion_rate"] = (stats["completed"] / stats["total"] * 100) if stats["total"] > 0 else 0

    return {
        "generated_at": datetime.now(),
        "overall": {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": completion_rate
        },
        "by_priority": priority_stats,
        "by_assignee": list(assignee_stats.values())
    }