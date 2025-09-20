from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from app.core import deps
from app.core.pagination import PaginationParams, PaginatedResponse
from app.core.file_upload import process_profile_picture, delete_profile_image
from app.features.users.crud import crud_user
from app.features.audit_logs.crud import crud_audit_log
from app.db.database import get_db
from app.features.users.models import User
from app.features.users.schemas import User as UserSchema, UserCreate, UserUpdate
from app.features.users.user_summary import UserSummary
from app.features.audit_logs.schemas import AuditLogCreate

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[UserSchema])
def read_users(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(default="created_at", description="Field to sort by"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Sort order"),
    search: Optional[str] = Query(default=None, description="Search in name and email"),
    role_name: Optional[str] = Query(default=None, description="Filter by role name"),
    role_id: Optional[str] = Query(default=None, description="Filter by role ID"),
    is_active: Optional[bool] = Query(default=None, description="Filter by active status"),
    department: Optional[str] = Query(default=None, description="Filter by department"),
    current_user: User = Depends(deps.require_permissions(["user:read"]))
) -> Any:
    """
    Get users with advanced filtering, pagination, and sorting

    **Supported sort fields:** id, name, email, created_at, updated_at, department, is_active

    **Search:** Searches in user name and email fields. Supports partial matches and split name search.

    **Filters:**
    - role_name: Filter by role name (case-insensitive)
    - role_id: Filter by specific role ID
    - is_active: Filter by active status (true/false)
    - department: Filter by department (case-insensitive, partial match)
    """
    users, total = crud_user.get_users_with_filters(
        db=db,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
        role_name=role_name,
        role_id=role_id,
        is_active=is_active,
        department=department
    )

    return PaginatedResponse.create(
        items=users,
        total=total,
        page=page,
        per_page=per_page
    )

@router.post("/{user_id}/upload-avatar", response_model=UserSchema)
async def upload_user_avatar(
    *,
    request: Request,
    db: Session = Depends(get_db),
    user_id: str,
    avatar_file: Optional[UploadFile] = File(None),
    avatar_url: Optional[str] = Form(None),
    current_user: User = Depends(deps.require_permissions(["user:write"]))
) -> Any:
    """
    Upload or update user profile picture

    You can provide a profile picture in two ways:
    1. Upload a file (avatar_file): PNG/JPEG only, max 2MB
    2. Provide an external URL (avatar_url): Must be a valid image URL

    Cannot provide both file and URL - choose one option.
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    # Remove old avatar if it's a local file
    if user.avatar and user.avatar.startswith('/public/user-profile/'):
        delete_profile_image(user.avatar)

    # Process new profile picture (uses default if none provided)
    avatar_path = await process_profile_picture(
        file=avatar_file,
        external_url=avatar_url,
        use_default=True
    )

    # Update user with new avatar
    user = crud_user.update(db, db_obj=user, obj_in={"avatar": avatar_path})

    # Log avatar update
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="UPDATE",
        resource="User Avatar",
        details=f"Updated profile picture for user: {user.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return user

@router.delete("/{user_id}/avatar", response_model=UserSchema)
def remove_user_avatar(
    *,
    request: Request,
    db: Session = Depends(get_db),
    user_id: str,
    current_user: User = Depends(deps.require_permissions(["user:write"]))
) -> Any:
    """Remove user profile picture"""
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    # Remove avatar file if it's a local file (but not if it's the default)
    if user.avatar and user.avatar.startswith('/public/user-profile/') and user.avatar != '/public/user-profile/default.png':
        delete_profile_image(user.avatar)

    # Update user to use default avatar
    user = crud_user.update(db, db_obj=user, obj_in={"avatar": "/public/user-profile/default.png"})

    # Log avatar removal
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="DELETE",
        resource="User Avatar",
        details=f"Removed profile picture for user: {user.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return user

@router.get("/summary", response_model=UserSummary)
def get_user_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_permissions(["user:read"]))
) -> Any:
    """
    Get user summary statistics including:
    - Total users count
    - Active/inactive users count
    - Total roles count
    - Count of users by role (Admin, Project Manager, Developer, Client, etc.)
    """
    summary_data = crud_user.get_user_summary(db)
    return UserSummary(**summary_data)

@router.post("/", response_model=UserSchema)
async def create_user(
    *,
    request: Request,
    db: Session = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    role_id: str = Form(...),
    is_active: bool = Form(True),
    department: Optional[str] = Form(None),
    skills: Optional[str] = Form(None),  # JSON string of array
    phone: Optional[str] = Form(None),
    timezone: Optional[str] = Form(None),
    avatar_file: Optional[UploadFile] = File(None),
    avatar_url: Optional[str] = Form(None),
    current_user: User = Depends(deps.require_permissions(["user:write"]))
) -> Any:
    """
    Create new user with optional profile picture

    You can provide a profile picture in two ways:
    1. Upload a file (avatar_file): PNG/JPEG only, max 2MB
    2. Provide an external URL (avatar_url): Must be a valid image URL

    Cannot provide both file and URL - choose one option.
    """
    # Check if user already exists
    user = crud_user.get_by_email(db, email=email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    # Process profile picture (automatically uses default if none provided)
    avatar_path = await process_profile_picture(
        file=avatar_file,
        external_url=avatar_url,
        use_default=True
    )

    # Parse skills if provided
    skills_list = None
    if skills:
        try:
            import json
            skills_list = json.loads(skills)
        except json.JSONDecodeError:
            # Fallback: split by comma
            skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()]

    # Create user data
    user_create = UserCreate(
        email=email,
        password=password,
        name=name,
        role_id=role_id,
        avatar=avatar_path,
        is_active=is_active,
        department=department,
        skills=skills_list,
        phone=phone,
        timezone=timezone
    )

    user = crud_user.create(db, obj_in=user_create)

    # Log user creation
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="CREATE",
        resource="User",
        details=f"Created new user: {user.email}" + (f" with profile picture" if avatar_path else ""),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return user

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    *,
    request: Request,
    db: Session = Depends(get_db),
    user_id: str,
    email: Optional[str] = Form(None),
    name: Optional[str] = Form(None),
    role_id: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    department: Optional[str] = Form(None),
    skills: Optional[str] = Form(None),  # JSON string of array
    phone: Optional[str] = Form(None),
    timezone: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    avatar_file: Optional[UploadFile] = File(None),
    avatar_url: Optional[str] = Form(None),
    remove_avatar: bool = Form(False),
    current_user: User = Depends(deps.require_permissions(["user:write"]))
) -> Any:
    """
    Update user with optional profile picture update

    Profile picture options:
    1. Upload new file (avatar_file): PNG/JPEG only, max 2MB
    2. Set external URL (avatar_url): Must be a valid image URL
    3. Remove current avatar (remove_avatar=true)

    Cannot provide both file and URL - choose one option.
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    # Handle avatar updates
    avatar_path = None
    if remove_avatar:
        # Remove current avatar
        if user.avatar and user.avatar.startswith('/public/user-profile/'):
            delete_profile_image(user.avatar)
        avatar_path = None
    elif avatar_file or avatar_url:
        # Update avatar
        if user.avatar and user.avatar.startswith('/public/user-profile/'):
            delete_profile_image(user.avatar)
        avatar_path = await process_profile_picture(
            file=avatar_file,
            external_url=avatar_url
        )
    else:
        # Keep existing avatar
        avatar_path = user.avatar

    # Parse skills if provided
    skills_list = None
    if skills is not None:
        if skills:  # Not empty string
            try:
                import json
                skills_list = json.loads(skills)
            except json.JSONDecodeError:
                # Fallback: split by comma
                skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
        else:
            skills_list = []  # Empty array for empty string

    # Create update data
    update_data = {}
    if email is not None:
        update_data["email"] = email
    if name is not None:
        update_data["name"] = name
    if role_id is not None:
        update_data["role_id"] = role_id
    if is_active is not None:
        update_data["is_active"] = is_active
    if department is not None:
        update_data["department"] = department
    if skills_list is not None:
        update_data["skills"] = skills_list
    if phone is not None:
        update_data["phone"] = phone
    if timezone is not None:
        update_data["timezone"] = timezone
    if password is not None:
        update_data["password"] = password

    # Always update avatar (could be None, new path, or existing path)
    update_data["avatar"] = avatar_path

    user = crud_user.update(db, db_obj=user, obj_in=update_data)

    # Log user update
    details = f"Updated user: {user.email}"
    if avatar_file or avatar_url:
        details += " with new profile picture"
    elif remove_avatar:
        details += " and removed profile picture"

    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="UPDATE",
        resource="User",
        details=details,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return user

@router.get("/{user_id}", response_model=UserSchema)
def read_user(
    *,
    db: Session = Depends(get_db),
    user_id: str,
    current_user: User = Depends(deps.require_permissions(["user:read"]))
) -> Any:
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    return user

@router.delete("/{user_id}", response_model=UserSchema)
def delete_user(
    *,
    request: Request,
    db: Session = Depends(get_db),
    user_id: str,
    current_user: User = Depends(deps.require_permissions(["user:delete"]))
) -> Any:
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Users cannot delete themselves",
        )

    user = crud_user.remove(db, id=user_id)

    # Log user deletion
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="DELETE",
        resource="User",
        details=f"Deleted user: {user.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return user

@router.get("/role/{role_name}", response_model=PaginatedResponse[UserSchema])
def read_users_by_role(
    *,
    db: Session = Depends(get_db),
    role_name: str,
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(default="created_at", description="Field to sort by"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(deps.require_permissions(["user:read"]))
) -> Any:
    """Get users by role name with pagination and sorting"""
    users, total = crud_user.get_users_by_role(
        db=db,
        role_name=role_name,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return PaginatedResponse.create(
        items=users,
        total=total,
        page=page,
        per_page=per_page
    )

@router.post("/{user_id}/upload-avatar", response_model=UserSchema)
async def upload_user_avatar(
    *,
    request: Request,
    db: Session = Depends(get_db),
    user_id: str,
    avatar_file: Optional[UploadFile] = File(None),
    avatar_url: Optional[str] = Form(None),
    current_user: User = Depends(deps.require_permissions(["user:write"]))
) -> Any:
    """
    Upload or update user profile picture

    You can provide a profile picture in two ways:
    1. Upload a file (avatar_file): PNG/JPEG only, max 2MB
    2. Provide an external URL (avatar_url): Must be a valid image URL

    Cannot provide both file and URL - choose one option.
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    # Remove old avatar if it's a local file
    if user.avatar and user.avatar.startswith('/public/user-profile/'):
        delete_profile_image(user.avatar)

    # Process new profile picture (uses default if none provided)
    avatar_path = await process_profile_picture(
        file=avatar_file,
        external_url=avatar_url,
        use_default=True
    )

    # Update user with new avatar
    user = crud_user.update(db, db_obj=user, obj_in={"avatar": avatar_path})

    # Log avatar update
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="UPDATE",
        resource="User Avatar",
        details=f"Updated profile picture for user: {user.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return user

@router.delete("/{user_id}/avatar", response_model=UserSchema)
def remove_user_avatar(
    *,
    request: Request,
    db: Session = Depends(get_db),
    user_id: str,
    current_user: User = Depends(deps.require_permissions(["user:write"]))
) -> Any:
    """Remove user profile picture"""
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    # Remove avatar file if it's a local file (but not if it's the default)
    if user.avatar and user.avatar.startswith('/public/user-profile/') and user.avatar != '/public/user-profile/default.png':
        delete_profile_image(user.avatar)

    # Update user to use default avatar
    user = crud_user.update(db, db_obj=user, obj_in={"avatar": "/public/user-profile/default.png"})

    # Log avatar removal
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="DELETE",
        resource="User Avatar",
        details=f"Removed profile picture for user: {user.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return user

@router.get("/summary", response_model=UserSummary)
def get_user_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_permissions(["user:read"]))
) -> Any:
    """
    Get user summary statistics including:
    - Total users count
    - Active/inactive users count
    - Total roles count
    - Count of users by role (Admin, Project Manager, Developer, Client, etc.)
    """
    summary_data = crud_user.get_user_summary(db)
    return UserSummary(**summary_data)

@router.get("/active/list", response_model=PaginatedResponse[UserSchema])
def read_active_users(
    *,
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(default="created_at", description="Field to sort by"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(deps.require_permissions(["user:read"]))
) -> Any:
    """Get active users with pagination and sorting"""
    users, total = crud_user.get_active_users(
        db=db,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return PaginatedResponse.create(
        items=users,
        total=total,
        page=page,
        per_page=per_page
    )

@router.post("/{user_id}/upload-avatar", response_model=UserSchema)
async def upload_user_avatar(
    *,
    request: Request,
    db: Session = Depends(get_db),
    user_id: str,
    avatar_file: Optional[UploadFile] = File(None),
    avatar_url: Optional[str] = Form(None),
    current_user: User = Depends(deps.require_permissions(["user:write"]))
) -> Any:
    """
    Upload or update user profile picture

    You can provide a profile picture in two ways:
    1. Upload a file (avatar_file): PNG/JPEG only, max 2MB
    2. Provide an external URL (avatar_url): Must be a valid image URL

    Cannot provide both file and URL - choose one option.
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    # Remove old avatar if it's a local file
    if user.avatar and user.avatar.startswith('/public/user-profile/'):
        delete_profile_image(user.avatar)

    # Process new profile picture (uses default if none provided)
    avatar_path = await process_profile_picture(
        file=avatar_file,
        external_url=avatar_url,
        use_default=True
    )

    # Update user with new avatar
    user = crud_user.update(db, db_obj=user, obj_in={"avatar": avatar_path})

    # Log avatar update
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="UPDATE",
        resource="User Avatar",
        details=f"Updated profile picture for user: {user.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return user

@router.delete("/{user_id}/avatar", response_model=UserSchema)
def remove_user_avatar(
    *,
    request: Request,
    db: Session = Depends(get_db),
    user_id: str,
    current_user: User = Depends(deps.require_permissions(["user:write"]))
) -> Any:
    """Remove user profile picture"""
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    # Remove avatar file if it's a local file (but not if it's the default)
    if user.avatar and user.avatar.startswith('/public/user-profile/') and user.avatar != '/public/user-profile/default.png':
        delete_profile_image(user.avatar)

    # Update user to use default avatar
    user = crud_user.update(db, db_obj=user, obj_in={"avatar": "/public/user-profile/default.png"})

    # Log avatar removal
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="DELETE",
        resource="User Avatar",
        details=f"Removed profile picture for user: {user.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return user

@router.get("/project-owner/", response_model=PaginatedResponse[UserSchema])
def read_project_owners(
    *,
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(default="created_at", description="Field to sort by"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Sort order"),
    is_active: Optional[bool] = Query(default=True, description="Filter by active status"),
    current_user: User = Depends(deps.require_permissions(["user:read"]))
) -> Any:
    """
    Get project owners (users with Project Manager role)

    Project owners are users who can manage and lead projects.
    Currently includes users with role_project_manager.
    """
    # Project owner roles: project manager
    project_owner_role_ids = ["role_project_manager"]

    users, total = crud_user.get_users_by_multiple_roles(
        db=db,
        role_ids=project_owner_role_ids,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        is_active=is_active
    )

    return PaginatedResponse.create(
        items=users,
        total=total,
        page=page,
        per_page=per_page
    )

@router.post("/{user_id}/upload-avatar", response_model=UserSchema)
async def upload_user_avatar(
    *,
    request: Request,
    db: Session = Depends(get_db),
    user_id: str,
    avatar_file: Optional[UploadFile] = File(None),
    avatar_url: Optional[str] = Form(None),
    current_user: User = Depends(deps.require_permissions(["user:write"]))
) -> Any:
    """
    Upload or update user profile picture

    You can provide a profile picture in two ways:
    1. Upload a file (avatar_file): PNG/JPEG only, max 2MB
    2. Provide an external URL (avatar_url): Must be a valid image URL

    Cannot provide both file and URL - choose one option.
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    # Remove old avatar if it's a local file
    if user.avatar and user.avatar.startswith('/public/user-profile/'):
        delete_profile_image(user.avatar)

    # Process new profile picture (uses default if none provided)
    avatar_path = await process_profile_picture(
        file=avatar_file,
        external_url=avatar_url,
        use_default=True
    )

    # Update user with new avatar
    user = crud_user.update(db, db_obj=user, obj_in={"avatar": avatar_path})

    # Log avatar update
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="UPDATE",
        resource="User Avatar",
        details=f"Updated profile picture for user: {user.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return user

@router.delete("/{user_id}/avatar", response_model=UserSchema)
def remove_user_avatar(
    *,
    request: Request,
    db: Session = Depends(get_db),
    user_id: str,
    current_user: User = Depends(deps.require_permissions(["user:write"]))
) -> Any:
    """Remove user profile picture"""
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    # Remove avatar file if it's a local file (but not if it's the default)
    if user.avatar and user.avatar.startswith('/public/user-profile/') and user.avatar != '/public/user-profile/default.png':
        delete_profile_image(user.avatar)

    # Update user to use default avatar
    user = crud_user.update(db, db_obj=user, obj_in={"avatar": "/public/user-profile/default.png"})

    # Log avatar removal
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="DELETE",
        resource="User Avatar",
        details=f"Removed profile picture for user: {user.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return user

@router.get("/project-member/", response_model=PaginatedResponse[UserSchema])
def read_project_members(
    *,
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(default="created_at", description="Field to sort by"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Sort order"),
    is_active: Optional[bool] = Query(default=True, description="Filter by active status"),
    current_user: User = Depends(deps.require_permissions(["user:read"]))
) -> Any:
    """
    Get project members (users with Developer and Tester roles)

    Project members are users who work on projects as contributors.
    Includes users with role_developer and role_tester.
    """
    # Project member roles: developer and tester
    project_member_role_ids = ["role_developer", "role_tester"]

    users, total = crud_user.get_users_by_multiple_roles(
        db=db,
        role_ids=project_member_role_ids,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        is_active=is_active
    )

    return PaginatedResponse.create(
        items=users,
        total=total,
        page=page,
        per_page=per_page
    )

@router.post("/{user_id}/upload-avatar", response_model=UserSchema)
async def upload_user_avatar(
    *,
    request: Request,
    db: Session = Depends(get_db),
    user_id: str,
    avatar_file: Optional[UploadFile] = File(None),
    avatar_url: Optional[str] = Form(None),
    current_user: User = Depends(deps.require_permissions(["user:write"]))
) -> Any:
    """
    Upload or update user profile picture

    You can provide a profile picture in two ways:
    1. Upload a file (avatar_file): PNG/JPEG only, max 2MB
    2. Provide an external URL (avatar_url): Must be a valid image URL

    Cannot provide both file and URL - choose one option.
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    # Remove old avatar if it's a local file
    if user.avatar and user.avatar.startswith('/public/user-profile/'):
        delete_profile_image(user.avatar)

    # Process new profile picture (uses default if none provided)
    avatar_path = await process_profile_picture(
        file=avatar_file,
        external_url=avatar_url,
        use_default=True
    )

    # Update user with new avatar
    user = crud_user.update(db, db_obj=user, obj_in={"avatar": avatar_path})

    # Log avatar update
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="UPDATE",
        resource="User Avatar",
        details=f"Updated profile picture for user: {user.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return user

@router.delete("/{user_id}/avatar", response_model=UserSchema)
def remove_user_avatar(
    *,
    request: Request,
    db: Session = Depends(get_db),
    user_id: str,
    current_user: User = Depends(deps.require_permissions(["user:write"]))
) -> Any:
    """Remove user profile picture"""
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    # Remove avatar file if it's a local file (but not if it's the default)
    if user.avatar and user.avatar.startswith('/public/user-profile/') and user.avatar != '/public/user-profile/default.png':
        delete_profile_image(user.avatar)

    # Update user to use default avatar
    user = crud_user.update(db, db_obj=user, obj_in={"avatar": "/public/user-profile/default.png"})

    # Log avatar removal
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="DELETE",
        resource="User Avatar",
        details=f"Removed profile picture for user: {user.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return user