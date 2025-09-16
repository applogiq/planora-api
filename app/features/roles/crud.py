from typing import List, Optional
from sqlalchemy.orm import Session
from app.shared.crud import CRUDBase
from app.features.roles.models import Role
from app.features.roles.schemas import RoleCreate, RoleUpdate
import uuid

class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Role]:
        return db.query(Role).filter(Role.name == name).first()

    def get_active_roles(self, db: Session) -> List[Role]:
        return db.query(Role).filter(Role.is_active == True).all()

    def create(self, db: Session, *, obj_in: RoleCreate) -> Role:
        db_obj = Role(
            id=str(uuid.uuid4()),
            name=obj_in.name,
            description=obj_in.description,
            permissions=obj_in.permissions,
            is_active=obj_in.is_active,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

crud_role = CRUDRole(Role)

# Export for backward compatibility
__all__ = ["crud_role", "CRUDRole"]