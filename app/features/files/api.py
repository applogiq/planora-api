from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query, File, UploadFile, Form, Path
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core import deps
from app.core.pagination import PaginationParams, PaginatedResponse
from app.features.files.crud import crud_file, crud_file_folder, crud_storage_quota
from app.features.audit_logs.crud import crud_audit_log
from app.db.database import get_db
from app.features.users.models import User
from app.features.files.schemas import (
    File as FileSchema, FileCreate, FileUpdate, FileUploadResponse,
    FileFolder as FileFolderSchema, FileFolderCreate, FileFolderUpdate,
    StorageQuota as StorageQuotaSchema, StorageInfo, FilesListResponse,
    FileSearchResponse
)
from app.features.files.file_utils import (
    save_upload_file, get_file_category, validate_entity_access,
    format_file_size, is_allowed_file
)
from app.features.files.models import File as FileModel
from app.features.audit_logs.schemas import AuditLogCreate
import os
from pathlib import Path as PathLib

router = APIRouter()

# File Upload Endpoints

@router.post("/{entity_type}/{entity_id}/upload", response_model=List[FileUploadResponse])
async def upload_files(
    *,
    request: Request,
    db: Session = Depends(get_db),
    entity_type: str = Path(..., description="Entity type (story, epic, project, sprint, task)"),
    entity_id: str = Path(..., description="Entity ID"),
    files: List[UploadFile] = File(..., description="Files to upload"),
    description: Optional[str] = Form(None, description="File description"),
    tags: Optional[str] = Form(None, description="Comma-separated tags"),
    is_public: bool = Form(False, description="Make files public"),
    current_user: User = Depends(deps.require_permissions(["file:write"]))
) -> Any:
    """
    Upload multiple files to an entity (story, epic, project, sprint, task)

    Supported file types:
    - Images: jpg, jpeg, png, gif, bmp, webp, svg
    - Documents: pdf, doc, docx, txt, rtf, odt, xls, xlsx, ppt, pptx
    - Videos: mp4, avi, mov, wmv, flv, webm, mkv
    - Audio: mp3, wav, flac, aac, ogg, m4a
    - Archives: zip, rar, 7z, tar, gz, bz2
    - Code: py, js, html, css, json, xml, sql, java, cpp, c
    """
    # Validate entity access
    if not validate_entity_access(entity_type, entity_id, current_user.role.permissions if current_user.role else []):
        raise HTTPException(status_code=403, detail="Access denied to this entity")

    uploaded_files = []

    for upload_file in files:
        try:
            # Check quota before upload
            quota_check = crud_file.check_quota_limits(db, entity_type, entity_id, len(await upload_file.read()))
            await upload_file.seek(0)  # Reset file pointer

            if not quota_check["can_upload"]:
                error_msg = "Upload would exceed "
                if quota_check["would_exceed_bytes"]:
                    error_msg += f"storage quota (remaining: {format_file_size(quota_check['remaining_bytes'])})"
                if quota_check["would_exceed_files"]:
                    if quota_check["would_exceed_bytes"]:
                        error_msg += " and "
                    error_msg += f"file count limit (remaining: {quota_check['remaining_files']} files)"

                uploaded_files.append(FileUploadResponse(
                    id="",
                    filename="",
                    original_filename=upload_file.filename or "",
                    file_size=0,
                    content_type="",
                    category="",
                    file_path="",
                    upload_success=False,
                    message=error_msg
                ))
                continue

            # Save file
            file_path, unique_filename, file_size = await save_upload_file(upload_file, entity_type, entity_id)

            # Determine file category
            file_extension = PathLib(upload_file.filename or "").suffix.lower()
            category = get_file_category(file_extension)

            # Create file record
            file_create = FileCreate(
                filename=unique_filename,
                original_filename=upload_file.filename or "",
                file_path=file_path,
                file_size=file_size,
                content_type=upload_file.content_type or "application/octet-stream",
                file_extension=file_extension,
                category=category,
                entity_type=entity_type,
                entity_id=entity_id,
                description=description,
                tags=tags,
                is_public=is_public,
                uploaded_by_id=current_user.id,
                uploaded_by_name=current_user.name
            )

            file_obj = crud_file.create(db, obj_in=file_create)

            # Log upload
            audit_log = AuditLogCreate(
                user_id=current_user.id,
                user_name=current_user.name,
                action="CREATE",
                resource="File",
                details=f"Uploaded file '{upload_file.filename}' to {entity_type}:{entity_id}",
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", ""),
                status="success"
            )
            crud_audit_log.create(db=db, obj_in=audit_log)

            uploaded_files.append(FileUploadResponse(
                id=file_obj.id,
                filename=file_obj.filename,
                original_filename=file_obj.original_filename,
                file_size=file_obj.file_size,
                content_type=file_obj.content_type,
                category=file_obj.category,
                file_path=file_obj.file_path,
                upload_success=True,
                message="File uploaded successfully"
            ))

        except HTTPException as e:
            uploaded_files.append(FileUploadResponse(
                id="",
                filename="",
                original_filename=upload_file.filename or "",
                file_size=0,
                content_type="",
                category="",
                file_path="",
                upload_success=False,
                message=e.detail
            ))
        except Exception as e:
            uploaded_files.append(FileUploadResponse(
                id="",
                filename="",
                original_filename=upload_file.filename or "",
                file_size=0,
                content_type="",
                category="",
                file_path="",
                upload_success=False,
                message=f"Upload failed: {str(e)}"
            ))

    return uploaded_files

# File Management Endpoints

@router.get("/{entity_type}/{entity_id}/list", response_model=FilesListResponse)
def list_files(
    *,
    db: Session = Depends(get_db),
    entity_type: str = Path(..., description="Entity type"),
    entity_id: str = Path(..., description="Entity ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in filenames and descriptions"),
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(deps.require_permissions(["file:read"]))
) -> Any:
    """Get files and folders for an entity with filtering and pagination"""
    # Validate entity access
    if not validate_entity_access(entity_type, entity_id, current_user.role.permissions if current_user.role else []):
        raise HTTPException(status_code=403, detail="Access denied to this entity")

    # Calculate pagination
    skip = (page - 1) * per_page

    # Get files
    files = crud_file.get_by_entity(
        db, entity_type, entity_id,
        skip=skip, limit=per_page,
        category=category, search=search
    )

    # Get folders (root level for now)
    folders = crud_file_folder.get_by_entity(db, entity_type, entity_id)

    # Get storage info
    storage_info = crud_file.get_storage_info(db, entity_type, entity_id)

    # Get totals
    total_files = len(crud_file.get_by_entity(db, entity_type, entity_id, skip=0, limit=10000))
    total_folders = len(folders)

    return FilesListResponse(
        files=files,
        folders=folders,
        storage_info=StorageInfo(**storage_info),
        total_files=total_files,
        total_folders=total_folders
    )

@router.get("/{entity_type}/{entity_id}/categories", response_model=dict)
def get_file_categories(
    *,
    db: Session = Depends(get_db),
    entity_type: str = Path(..., description="Entity type"),
    entity_id: str = Path(..., description="Entity ID"),
    current_user: User = Depends(deps.require_permissions(["file:read"]))
) -> Any:
    """Get file count by category for an entity"""
    # Validate entity access
    if not validate_entity_access(entity_type, entity_id, current_user.role.permissions if current_user.role else []):
        raise HTTPException(status_code=403, detail="Access denied to this entity")

    # Get all files for the entity
    files = crud_file.get_by_entity(db, entity_type, entity_id, skip=0, limit=10000)

    # Count by category
    categories = {}
    for file in files:
        categories[file.category] = categories.get(file.category, 0) + 1

    return {
        "categories": categories,
        "total_files": len(files)
    }

@router.get("/search", response_model=FileSearchResponse)
def search_files(
    *,
    db: Session = Depends(get_db),
    q: str = Query(..., min_length=1, description="Search query"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    user_id: Optional[str] = Query(None, description="Filter by uploader"),
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(deps.require_permissions(["file:read"]))
) -> Any:
    """Search files across entities"""
    skip = (page - 1) * per_page

    files, total = crud_file.search_files(
        db,
        search=q,
        entity_type=entity_type,
        entity_id=entity_id,
        category=category,
        user_id=user_id,
        skip=skip,
        limit=per_page
    )

    total_pages = (total + per_page - 1) // per_page

    return FileSearchResponse(
        files=files,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

@router.get("/{file_id}/download")
async def download_file(
    *,
    db: Session = Depends(get_db),
    file_id: str = Path(..., description="File ID"),
    current_user: User = Depends(deps.require_permissions(["file:read"]))
) -> Any:
    """Download a file"""
    file_obj = crud_file.get(db, id=file_id)
    if not file_obj or file_obj.is_deleted:
        raise HTTPException(status_code=404, detail="File not found")

    # Check access to entity
    if not validate_entity_access(file_obj.entity_type, file_obj.entity_id, current_user.role.permissions if current_user.role else []):
        if not file_obj.is_public:
            raise HTTPException(status_code=403, detail="Access denied")

    # Check if file exists
    if not os.path.exists(file_obj.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=file_obj.file_path,
        filename=file_obj.original_filename,
        media_type=file_obj.content_type
    )

@router.get("/{file_id}/info", response_model=FileSchema)
def get_file_info(
    *,
    db: Session = Depends(get_db),
    file_id: str = Path(..., description="File ID"),
    current_user: User = Depends(deps.require_permissions(["file:read"]))
) -> Any:
    """Get file information"""
    file_obj = crud_file.get(db, id=file_id)
    if not file_obj or file_obj.is_deleted:
        raise HTTPException(status_code=404, detail="File not found")

    # Check access to entity
    if not validate_entity_access(file_obj.entity_type, file_obj.entity_id, current_user.role.permissions if current_user.role else []):
        if not file_obj.is_public:
            raise HTTPException(status_code=403, detail="Access denied")

    return file_obj

@router.put("/{file_id}", response_model=FileSchema)
def update_file(
    *,
    request: Request,
    db: Session = Depends(get_db),
    file_id: str = Path(..., description="File ID"),
    file_update: FileUpdate,
    current_user: User = Depends(deps.require_permissions(["file:write"]))
) -> Any:
    """Update file metadata"""
    file_obj = crud_file.get(db, id=file_id)
    if not file_obj or file_obj.is_deleted:
        raise HTTPException(status_code=404, detail="File not found")

    # Check access to entity
    if not validate_entity_access(file_obj.entity_type, file_obj.entity_id, current_user.role.permissions if current_user.role else []):
        raise HTTPException(status_code=403, detail="Access denied")

    updated_file = crud_file.update(db, db_obj=file_obj, obj_in=file_update)

    # Log update
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="UPDATE",
        resource="File",
        details=f"Updated file '{updated_file.original_filename}' metadata",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return updated_file

@router.delete("/{file_id}", response_model=FileSchema)
def delete_file(
    *,
    request: Request,
    db: Session = Depends(get_db),
    file_id: str = Path(..., description="File ID"),
    current_user: User = Depends(deps.require_permissions(["file:delete"]))
) -> Any:
    """Delete a file (soft delete)"""
    file_obj = crud_file.get(db, id=file_id)
    if not file_obj or file_obj.is_deleted:
        raise HTTPException(status_code=404, detail="File not found")

    # Check access to entity
    if not validate_entity_access(file_obj.entity_type, file_obj.entity_id, current_user.role.permissions if current_user.role else []):
        raise HTTPException(status_code=403, detail="Access denied")

    deleted_file = crud_file.soft_delete(db, file_id=file_id, deleted_by_id=current_user.id)

    # Log deletion
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="DELETE",
        resource="File",
        details=f"Deleted file '{deleted_file.original_filename}' from {deleted_file.entity_type}:{deleted_file.entity_id}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return deleted_file

# Storage Management Endpoints

@router.get("/{entity_type}/{entity_id}/storage", response_model=StorageInfo)
def get_storage_info(
    *,
    db: Session = Depends(get_db),
    entity_type: str = Path(..., description="Entity type"),
    entity_id: str = Path(..., description="Entity ID"),
    current_user: User = Depends(deps.require_permissions(["file:read"]))
) -> Any:
    """Get storage information for an entity"""
    # Validate entity access
    if not validate_entity_access(entity_type, entity_id, current_user.role.permissions if current_user.role else []):
        raise HTTPException(status_code=403, detail="Access denied to this entity")

    storage_info = crud_file.get_storage_info(db, entity_type, entity_id)
    return StorageInfo(**storage_info)

# Folder Management Endpoints

@router.post("/{entity_type}/{entity_id}/folders", response_model=FileFolderSchema)
def create_folder(
    *,
    request: Request,
    db: Session = Depends(get_db),
    entity_type: str = Path(..., description="Entity type"),
    entity_id: str = Path(..., description="Entity ID"),
    folder_create: FileFolderCreate,
    current_user: User = Depends(deps.require_permissions(["file:write"]))
) -> Any:
    """Create a new folder"""
    # Validate entity access
    if not validate_entity_access(entity_type, entity_id, current_user.role.permissions if current_user.role else []):
        raise HTTPException(status_code=403, detail="Access denied to this entity")

    # Ensure entity matches path
    folder_create.entity_type = entity_type
    folder_create.entity_id = entity_id
    folder_create.created_by_id = current_user.id
    folder_create.created_by_name = current_user.name

    folder = crud_file_folder.create(db, obj_in=folder_create)

    # Log creation
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="CREATE",
        resource="Folder",
        details=f"Created folder '{folder.name}' in {entity_type}:{entity_id}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return folder