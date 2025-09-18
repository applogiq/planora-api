from fastapi import APIRouter

def get_api_router() -> APIRouter:
    """Lazy load API router to avoid circular imports"""
    from app.features.users.api import router as users_router
    from app.features.roles.api import router as roles_router
    from app.features.projects.api import router as projects_router
    from app.features.tasks.api import router as tasks_router
    from app.features.auth.api import router as auth_router
    from app.features.audit_logs.api import router as audit_logs_router
    from app.features.notifications.api import router as notifications_router
    from app.features.dashboard.api import router as dashboard_router
    from app.features.reports.api import router as reports_router
    from app.features.masters.api import router as masters_router

    api_router = APIRouter()

    # Include all feature routers
    api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
    api_router.include_router(users_router, prefix="/users", tags=["users"])
    api_router.include_router(roles_router, prefix="/roles", tags=["roles"])
    api_router.include_router(projects_router, prefix="/projects", tags=["projects"])
    api_router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
    api_router.include_router(audit_logs_router, prefix="/audit-logs", tags=["audit-logs"])
    api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
    api_router.include_router(reports_router, prefix="/reports", tags=["reports"])
    api_router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
    api_router.include_router(masters_router, prefix="/masters", tags=["masters"])

    return api_router

api_router = get_api_router()