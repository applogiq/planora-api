from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogCreate
import uuid

class CRUDAuditLog(CRUDBase[AuditLog, AuditLogCreate, None]):
    def get_by_user(self, db: Session, *, user_id: str) -> List[AuditLog]:
        return db.query(AuditLog).filter(AuditLog.user_id == user_id).all()

    def get_by_action(self, db: Session, *, action: str) -> List[AuditLog]:
        return db.query(AuditLog).filter(AuditLog.action == action).all()

    def get_by_status(self, db: Session, *, status: str) -> List[AuditLog]:
        return db.query(AuditLog).filter(AuditLog.status == status).all()

    def create(self, db: Session, *, obj_in: AuditLogCreate) -> AuditLog:
        db_obj = AuditLog(
            id=str(uuid.uuid4()),
            **obj_in.dict()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

crud_audit_log = CRUDAuditLog(AuditLog)