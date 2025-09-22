import os
import uuid
import shutil
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
from pathlib import Path

# File upload configuration
UPLOAD_DIR = Path("uploads")
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {
    'image': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'},
    'document': {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'},
    'video': {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'},
    'audio': {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'},
    'archive': {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'},
    'code': {'.py', '.js', '.html', '.css', '.json', '.xml', '.sql', '.java', '.cpp', '.c'},
}

def get_file_category(file_extension: str) -> str:
    """Determine file category based on extension"""
    file_extension = file_extension.lower()

    for category, extensions in ALLOWED_EXTENSIONS.items():
        if file_extension in extensions:
            return category

    return 'other'

def is_allowed_file(filename: str) -> bool:
    """Check if file type is allowed"""
    file_extension = Path(filename).suffix.lower()

    # Check if extension is in any allowed category
    for extensions in ALLOWED_EXTENSIONS.values():
        if file_extension in extensions:
            return True

    return False

def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename while preserving extension"""
    file_extension = Path(original_filename).suffix
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{file_extension}"

def get_upload_path(entity_type: str, entity_id: str, filename: str) -> Path:
    """Generate upload path for file"""
    upload_path = UPLOAD_DIR / entity_type / entity_id
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path / filename

def format_file_size(size_bytes: int) -> str:
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"

async def save_upload_file(
    upload_file: UploadFile,
    entity_type: str,
    entity_id: str
) -> Tuple[str, str, int]:
    """
    Save uploaded file and return (file_path, unique_filename, file_size)
    """
    # Validate file
    if not upload_file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    if not is_allowed_file(upload_file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join([ext for exts in ALLOWED_EXTENSIONS.values() for ext in exts])}"
        )

    # Read file content
    content = await upload_file.read()
    file_size = len(content)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {format_file_size(MAX_FILE_SIZE)}"
        )

    # Generate unique filename and path
    unique_filename = generate_unique_filename(upload_file.filename)
    file_path = get_upload_path(entity_type, entity_id, unique_filename)

    try:
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(content)

        return str(file_path), unique_filename, file_size

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

def delete_file(file_path: str) -> bool:
    """Delete file from filesystem"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except Exception:
        return False

def get_file_info(file_path: str) -> Optional[dict]:
    """Get file information"""
    try:
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime
            }
    except Exception:
        pass
    return None

def validate_entity_access(entity_type: str, entity_id: str, user_permissions: list) -> bool:
    """Validate if user has access to entity for file operations"""
    # Define required permissions for each entity type
    permission_map = {
        'story': ['story:read'],
        'epic': ['epic:read'],
        'project': ['project:read'],
        'sprint': ['sprint:read'],
        'task': ['story:read']  # Tasks are part of stories
    }

    required_permissions = permission_map.get(entity_type, [])

    # Check if user has any required permission or is super admin
    if '*' in user_permissions:
        return True

    return any(perm in user_permissions for perm in required_permissions)