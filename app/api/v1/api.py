from fastapi import APIRouter

def get_api_router() -> APIRouter:
    """Lazy load API router to avoid circular imports"""
    from app.features.users.api import router as users_router
    from app.features.roles.api import router as roles_router
    from app.features.projects.api import router as projects_router
    from app.features.stories.api import router as stories_router
    from app.features.sprints.api import router as sprints_router
    from app.features.epics.api import router as epics_router
    from app.features.auth.api import router as auth_router
    from app.features.audit_logs.api import router as audit_logs_router
    from app.features.notifications.api import router as notifications_router
    from app.features.dashboard.api import router as dashboard_router
    from app.features.reports.api import router as reports_router
    from app.features.masters.api import router as masters_router
    from app.features.customers.api import router as customers_router
    from app.features.files.api import router as files_router

    api_router = APIRouter()

    # Include all feature routers
    api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
    api_router.include_router(users_router, prefix="/users", tags=["Users"])
    api_router.include_router(roles_router, prefix="/roles", tags=["Roles"])
    api_router.include_router(projects_router, prefix="/projects", tags=["Projects"])
    api_router.include_router(stories_router, prefix="/stories", tags=["Stories"])
    api_router.include_router(sprints_router, prefix="/sprints", tags=["Sprints"])
    api_router.include_router(epics_router, prefix="/epics", tags=["Epics"])
    api_router.include_router(audit_logs_router, prefix="/audit-logs", tags=["Audit-logs"])
    api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
    api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
    api_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
    api_router.include_router(masters_router, prefix="/masters", tags=["Masters"])
    api_router.include_router(customers_router, prefix="/customers", tags=["Customers"])
    api_router.include_router(files_router, prefix="/files", tags=["Files"])

    return api_router

api_router = get_api_router()