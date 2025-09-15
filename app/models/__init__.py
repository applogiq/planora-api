# Import all models to ensure they are registered with SQLAlchemy
from app.models.user import User, UserProfile
from app.models.auth import (
    Role, Permission, RolePermission, UserRole,
    AuditLog, APIToken, AuthProvider
)
from app.models.project import Project, ProjectMember
from app.models.task import (
    Board, BoardColumn, Sprint, Task, TaskLink,
    Comment, Attachment, Label, TaskLabel,
    CustomField, TaskCustomField, TaskHistory, TaskWatcher
)

__all__ = [
    # Core
    "User", "UserProfile",

    # Auth
    "Role", "Permission", "RolePermission", "UserRole",
    "AuditLog", "APIToken", "AuthProvider",

    # Projects
    "Project", "ProjectMember",

    # Tasks
    "Board", "BoardColumn", "Sprint", "Task", "TaskLink",
    "Comment", "Attachment", "Label", "TaskLabel",
    "CustomField", "TaskCustomField", "TaskHistory", "TaskWatcher"
]