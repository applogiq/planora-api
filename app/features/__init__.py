from fastapi import APIRouter

def get_features_router() -> APIRouter:
    """Lazy load feature routers to avoid circular imports"""
    from app.features.users.api import router as users_router
    from app.features.roles.api import router as roles_router
    from app.features.projects.api import router as projects_router
    from app.features.tasks.api import router as tasks_router
    from app.features.auth.api import router as auth_router
    from app.features.audit_logs.api import router as audit_logs_router
    from app.features.notifications.api import router as notifications_router
    from app.features.dashboard.api import router as dashboard_router
    from app.features.reports.api import router as reports_router

    features_router = APIRouter()

    # Include all feature routers
    features_router.include_router(auth_router, prefix="/auth", tags=["auth"])
    features_router.include_router(users_router, prefix="/users", tags=["users"])
    features_router.include_router(roles_router, prefix="/roles", tags=["roles"])
    features_router.include_router(projects_router, prefix="/projects", tags=["projects"])
    features_router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
    features_router.include_router(audit_logs_router, prefix="/audit-logs", tags=["audit-logs"])
    features_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
    features_router.include_router(reports_router, prefix="/reports", tags=["reports"])
    features_router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])

    return features_router

features_router = get_features_router()