from typing import Any, Dict, Optional, Union, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from app.shared.crud import CRUDBase
from app.features.files.models import File, FileFolder, StorageQuota
from app.features.files.schemas import FileCreate, FileUpdate, FileFolderCreate, FileFolderUpdate, StorageQuotaCreate, StorageQuotaUpdate
from app.features.files.file_utils import delete_file, format_file_size
import uuid
from datetime import datetime

class CRUDFile(CRUDBase[File, FileCreate, FileUpdate]):
    def create(self, db: Session, *, obj_in: FileCreate) -> File:
        db_obj = File(
            id=str(uuid.uuid4()),
            **obj_in.dict()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Update storage quota
        self._update_storage_usage(db, obj_in.entity_type, obj_in.entity_id, obj_in.file_size, 1)

        return db_obj

    def get_by_entity(
        self,
        db: Session,
        entity_type: str,
        entity_id: str,
        *,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[File]:
        """Get files for a specific entity"""
        query = db.query(File).filter(
            and_(
                File.entity_type == entity_type,
                File.entity_id == entity_id,
                File.is_deleted == False
            )
        )

        if category:
            query = query.filter(File.category == category)

        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(File.filename).contains(search_term),
                    func.lower(File.original_filename).contains(search_term),
                    func.lower(File.description).contains(search_term),
                    func.lower(File.tags).contains(search_term)
                )
            )

        return query.order_by(desc(File.created_at)).offset(skip).limit(limit).all()

    def search_files(
        self,
        db: Session,
        *,
        search: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        category: Optional[str] = None,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[File], int]:
        """Search files with filters"""
        query = db.query(File).filter(File.is_deleted == False)

        # Search in multiple fields
        search_term = f"%{search.lower()}%"
        search_filters = [
            func.lower(File.filename).contains(search_term),
            func.lower(File.original_filename).contains(search_term),
            func.lower(File.description).contains(search_term),
            func.lower(File.tags).contains(search_term),
            func.lower(File.entity_title).contains(search_term)
        ]
        query = query.filter(or_(*search_filters))

        # Apply filters
        if entity_type:
            query = query.filter(File.entity_type == entity_type)

        if entity_id:
            query = query.filter(File.entity_id == entity_id)

        if category:
            query = query.filter(File.category == category)

        if user_id:
            query = query.filter(File.uploaded_by_id == user_id)

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        files = query.order_by(desc(File.created_at)).offset(skip).limit(limit).all()

        return files, total

    def get_files_by_category(
        self,
        db: Session,
        entity_type: str,
        entity_id: str,
        category: str,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[File]:
        """Get files by category for an entity"""
        return db.query(File).filter(
            and_(
                File.entity_type == entity_type,
                File.entity_id == entity_id,
                File.category == category,
                File.is_deleted == False
            )
        ).order_by(desc(File.created_at)).offset(skip).limit(limit).all()

    def soft_delete(self, db: Session, *, file_id: str, deleted_by_id: str) -> Optional[File]:
        """Soft delete a file"""
        file_obj = self.get(db, id=file_id)
        if file_obj and not file_obj.is_deleted:
            file_obj.is_deleted = True
            file_obj.deleted_at = datetime.utcnow()
            file_obj.deleted_by_id = deleted_by_id
            db.commit()
            db.refresh(file_obj)

            # Update storage quota
            self._update_storage_usage(db, file_obj.entity_type, file_obj.entity_id, -file_obj.file_size, -1)

            # Delete physical file
            delete_file(file_obj.file_path)

            return file_obj
        return None

    def restore(self, db: Session, *, file_id: str) -> Optional[File]:
        """Restore a soft-deleted file"""
        file_obj = self.get(db, id=file_id)
        if file_obj and file_obj.is_deleted:
            file_obj.is_deleted = False
            file_obj.deleted_at = None
            file_obj.deleted_by_id = None
            db.commit()
            db.refresh(file_obj)

            # Update storage quota
            self._update_storage_usage(db, file_obj.entity_type, file_obj.entity_id, file_obj.file_size, 1)

            return file_obj
        return None

    def get_storage_info(self, db: Session, entity_type: str, entity_id: str) -> Dict[str, Any]:
        """Get storage information for an entity"""
        quota = self._get_or_create_quota(db, entity_type, entity_id)

        # Calculate actual usage from files
        actual_usage = db.query(func.sum(File.file_size)).filter(
            and_(
                File.entity_type == entity_type,
                File.entity_id == entity_id,
                File.is_deleted == False
            )
        ).scalar() or 0

        actual_count = db.query(func.count(File.id)).filter(
            and_(
                File.entity_type == entity_type,
                File.entity_id == entity_id,
                File.is_deleted == False
            )
        ).scalar() or 0

        # Update quota if needed
        if quota.used_bytes != actual_usage or quota.current_files != actual_count:
            quota.used_bytes = actual_usage
            quota.current_files = actual_count
            db.commit()

        available_bytes = max(0, quota.total_quota_bytes - quota.used_bytes)
        used_percentage = (quota.used_bytes / quota.total_quota_bytes * 100) if quota.total_quota_bytes > 0 else 0
        files_percentage = (quota.current_files / quota.max_files * 100) if quota.max_files > 0 else 0

        return {
            "used_bytes": quota.used_bytes,
            "available_bytes": available_bytes,
            "total_bytes": quota.total_quota_bytes,
            "used_percentage": round(used_percentage, 1),
            "current_files": quota.current_files,
            "max_files": quota.max_files,
            "files_percentage": round(files_percentage, 1),
            "used_formatted": format_file_size(quota.used_bytes),
            "available_formatted": format_file_size(available_bytes),
            "total_formatted": format_file_size(quota.total_quota_bytes)
        }

    def check_quota_limits(self, db: Session, entity_type: str, entity_id: str, file_size: int) -> Dict[str, Any]:
        """Check if file upload would exceed quota limits"""
        quota = self._get_or_create_quota(db, entity_type, entity_id)

        would_exceed_bytes = (quota.used_bytes + file_size) > quota.total_quota_bytes
        would_exceed_files = (quota.current_files + 1) > quota.max_files

        return {
            "can_upload": not (would_exceed_bytes or would_exceed_files),
            "would_exceed_bytes": would_exceed_bytes,
            "would_exceed_files": would_exceed_files,
            "remaining_bytes": max(0, quota.total_quota_bytes - quota.used_bytes),
            "remaining_files": max(0, quota.max_files - quota.current_files)
        }

    def _get_or_create_quota(self, db: Session, entity_type: str, entity_id: str) -> StorageQuota:
        """Get or create storage quota for entity"""
        quota = db.query(StorageQuota).filter(
            and_(
                StorageQuota.entity_type == entity_type,
                StorageQuota.entity_id == entity_id
            )
        ).first()

        if not quota:
            quota = StorageQuota(
                id=str(uuid.uuid4()),
                entity_type=entity_type,
                entity_id=entity_id
            )
            db.add(quota)
            db.commit()
            db.refresh(quota)

        return quota

    def _update_storage_usage(self, db: Session, entity_type: str, entity_id: str, size_delta: int, count_delta: int):
        """Update storage usage for entity"""
        quota = self._get_or_create_quota(db, entity_type, entity_id)
        quota.used_bytes = max(0, quota.used_bytes + size_delta)
        quota.current_files = max(0, quota.current_files + count_delta)
        db.commit()

class CRUDFileFolder(CRUDBase[FileFolder, FileFolderCreate, FileFolderUpdate]):
    def create(self, db: Session, *, obj_in: FileFolderCreate) -> FileFolder:
        db_obj = FileFolder(
            id=str(uuid.uuid4()),
            **obj_in.dict()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_entity(
        self,
        db: Session,
        entity_type: str,
        entity_id: str,
        parent_folder_id: Optional[str] = None
    ) -> List[FileFolder]:
        """Get folders for a specific entity and parent"""
        return db.query(FileFolder).filter(
            and_(
                FileFolder.entity_type == entity_type,
                FileFolder.entity_id == entity_id,
                FileFolder.parent_folder_id == parent_folder_id,
                FileFolder.is_deleted == False
            )
        ).order_by(FileFolder.name).all()

    def soft_delete(self, db: Session, *, folder_id: str, deleted_by_id: str) -> Optional[FileFolder]:
        """Soft delete a folder and its contents"""
        folder_obj = self.get(db, id=folder_id)
        if folder_obj and not folder_obj.is_deleted:
            folder_obj.is_deleted = True
            folder_obj.deleted_at = datetime.utcnow()
            folder_obj.deleted_by_id = deleted_by_id
            db.commit()
            db.refresh(folder_obj)
            return folder_obj
        return None

class CRUDStorageQuota(CRUDBase[StorageQuota, StorageQuotaCreate, StorageQuotaUpdate]):
    def create(self, db: Session, *, obj_in: StorageQuotaCreate) -> StorageQuota:
        db_obj = StorageQuota(
            id=str(uuid.uuid4()),
            **obj_in.dict()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_entity(self, db: Session, entity_type: str, entity_id: str) -> Optional[StorageQuota]:
        """Get storage quota for entity"""
        return db.query(StorageQuota).filter(
            and_(
                StorageQuota.entity_type == entity_type,
                StorageQuota.entity_id == entity_id
            )
        ).first()

crud_file = CRUDFile(File)
crud_file_folder = CRUDFileFolder(FileFolder)
crud_storage_quota = CRUDStorageQuota(StorageQuota)