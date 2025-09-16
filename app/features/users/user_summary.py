from pydantic import BaseModel


class RoleCount(BaseModel):
    role_name: str
    count: int


class UserSummary(BaseModel):
    total_users: int
    active_users: int
    inactive_users: int
    total_roles: int
    role_counts: list[RoleCount]

    class Config:
        from_attributes = True