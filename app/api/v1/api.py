from fastapi import APIRouter

from app.api.v1 import (
    auth, projects, tasks, users
)

api_router = APIRouter()

# Core modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])