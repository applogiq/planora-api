from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
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
from app.features.audit_logs.schemas import AuditLogCreate
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/")
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    unread_only: bool = False
) -> Any:
    # For this demo, we'll use audit logs as notification source
    # In a real implementation, you'd have a dedicated notifications table

    # Get recent activities that might be relevant to the user
    user_logs = crud_audit_log.get_by_user(db, user_id=current_user.id)

    notifications = []
    for log in user_logs[:20]:  # Last 20 activities
        notifications.append({
            "id": log.id,
            "type": "activity",
            "title": f"{log.action} - {log.resource}",
            "message": log.details,
            "timestamp": log.timestamp,
            "is_read": False,  # In real implementation, track read status
            "priority": "normal",
            "action_url": None
        })

    # Add some system notifications (mock data)
    system_notifications = [
        {
            "id": "sys_001",
            "type": "system",
            "title": "System Maintenance Scheduled",
            "message": "Planned maintenance window on Sunday 2:00 AM - 4:00 AM",
            "timestamp": datetime.now() + timedelta(days=2),
            "is_read": False,
            "priority": "high",
            "action_url": None
        },
        {
            "id": "sys_002",
            "type": "reminder",
            "title": "Weekly Report Due",
            "message": "Your weekly project report is due tomorrow",
            "timestamp": datetime.now() - timedelta(hours=2),
            "is_read": False,
            "priority": "medium",
            "action_url": "/reports"
        }
    ]

    all_notifications = notifications + system_notifications

    if unread_only:
        all_notifications = [n for n in all_notifications if not n["is_read"]]

    return {
        "notifications": all_notifications,
        "unread_count": len([n for n in all_notifications if not n["is_read"]]),
        "total_count": len(all_notifications)
    }

@router.post("/{notification_id}/mark-read")
def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    # In a real implementation, you'd update the notification's read status
    return {"message": f"Notification {notification_id} marked as read"}

@router.post("/mark-all-read")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    # In a real implementation, you'd mark all user's notifications as read
    return {"message": "All notifications marked as read"}

@router.get("/settings")
def get_notification_settings(
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    # Mock notification preferences
    return {
        "email_notifications": True,
        "push_notifications": True,
        "task_assignments": True,
        "project_updates": True,
        "system_alerts": True,
        "weekly_reports": False,
        "digest_frequency": "daily"  # daily, weekly, never
    }

@router.put("/settings")
def update_notification_settings(
    settings: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    # In a real implementation, you'd save these preferences to the database
    return {
        "message": "Notification settings updated successfully",
        "settings": settings
    }