from typing import Optional, List, Any
from pydantic import BaseModel, Field
from datetime import datetime

class FileBase(BaseModel):
    filename: str
    original_filename: str
    file_size: int
    content_type: str
    file_extension: str
    category: str
    entity_type: str
    entity_id: str
    entity_title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    is_public: bool = False

class FileCreate(FileBase):
    file_path: str
    uploaded_by_id: str
    uploaded_by_name: str

class FileUpdate(BaseModel):
    filename: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    is_public: Optional[bool] = None
    category: Optional[str] = None

class File(FileBase):
    id: str
    file_path: str
    uploaded_by_id: str
    uploaded_by_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by_id: Optional[str] = None

    class Config:
        from_attributes = True

class FileFolderBase(BaseModel):
    name: str
    description: Optional[str] = None
    entity_type: str
    entity_id: str
    parent_folder_id: Optional[str] = None

class FileFolderCreate(FileFolderBase):
    created_by_id: str
    created_by_name: str

class FileFolderUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_folder_id: Optional[str] = None

class FileFolder(FileFolderBase):
    id: str
    created_by_id: str
    created_by_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by_id: Optional[str] = None

    class Config:
        from_attributes = True

class StorageQuotaBase(BaseModel):
    entity_type: str
    entity_id: str
    total_quota_bytes: int = 10737418240  # 10GB
    max_files: int = 1000

class StorageQuotaCreate(StorageQuotaBase):
    pass

class StorageQuotaUpdate(BaseModel):
    total_quota_bytes: Optional[int] = None
    max_files: Optional[int] = None

class StorageQuota(StorageQuotaBase):
    id: str
    used_bytes: int = 0
    current_files: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class StorageInfo(BaseModel):
    used_bytes: int
    available_bytes: int
    total_bytes: int
    used_percentage: float
    current_files: int
    max_files: int
    files_percentage: float

class FileUploadResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    file_size: int
    content_type: str
    category: str
    file_path: str
    upload_success: bool
    message: str

class FilesListResponse(BaseModel):
    files: List[File]
    folders: List[FileFolder]
    storage_info: StorageInfo
    total_files: int
    total_folders: int

class FileSearchResponse(BaseModel):
    files: List[File]
    total: int
    page: int
    per_page: int
    total_pages: int