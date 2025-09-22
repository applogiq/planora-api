from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from app.core.security import get_password_hash, verify_password
from app.core.pagination import paginate_query
from app.shared.crud import CRUDBase
from app.features.users.models import User
from app.features.roles.models import Role
from app.features.users.schemas import UserCreate, UserUpdate
import uuid

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            id=str(uuid.uuid4()),
            email=obj_in.email,
            password=get_password_hash(obj_in.password),
            name=obj_in.name,
            role_id=obj_in.role_id,
            user_profile=obj_in.user_profile,
            is_active=obj_in.is_active,
            department=obj_in.department,
            skills=obj_in.skills,
            phone=obj_in.phone,
            timezone=obj_in.timezone,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Load the role relationship to ensure permissions are accessible for new users
        db_obj = db.query(User).options(joinedload(User.role)).filter(User.id == db_obj.id).first()
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        # Handle password hashing
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["password"] = hashed_password

        # Check if role is being updated
        role_changed = False
        old_role_id = db_obj.role_id
        new_role_id = update_data.get("role_id")

        if new_role_id and new_role_id != old_role_id:
            role_changed = True

        # Update the user
        updated_user = super().update(db, db_obj=db_obj, obj_in=update_data)

        # Always refresh the user to get updated role permissions (especially important for role changes)
        db.refresh(updated_user)
        # Load the role relationship to ensure permissions are accessible
        updated_user = db.query(User).options(joinedload(User.role)).filter(User.id == updated_user.id).first()

        # If role changed, ensure the session is properly committed and role is loaded
        if role_changed:
            db.commit()
            # Force a fresh query to ensure we get the latest role data
            updated_user = db.query(User).options(joinedload(User.role)).filter(User.id == updated_user.id).first()

        return updated_user

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def get(self, db: Session, id: Any) -> Optional[User]:
        return db.query(User).options(joinedload(User.role)).filter(User.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[User]:
        return db.query(User).options(joinedload(User.role)).offset(skip).limit(limit).all()

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).options(joinedload(User.role)).filter(User.email == email).first()

    def get_users_with_filters(
        self,
        db: Session,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        search: Optional[str] = None,
        role_name: Optional[str] = None,
        role_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        department: Optional[str] = None
    ) -> tuple[List[User], int]:
        """
        Get users with advanced filtering, pagination, and sorting

        Args:
            db: Database session
            page: Page number (starts from 1)
            per_page: Items per page
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            search: Search term for name and email
            role_name: Filter by role name
            role_id: Filter by role ID
            is_active: Filter by active status
            department: Filter by department

        Returns:
            Tuple of (users_list, total_count)
        """
        query = db.query(User).options(joinedload(User.role))

        # Apply filters
        filters = []

        # Search filter (name and email)
        if search:
            search_term = f"%{search.lower()}%"
            search_filters = [
                func.lower(User.name).contains(search_term),
                func.lower(User.email).contains(search_term)
            ]
            # Split search term to handle first name, last name search
            search_parts = search.lower().split()
            if len(search_parts) > 1:
                # Search for "first last" in name field
                for part in search_parts:
                    search_filters.append(func.lower(User.name).contains(f"%{part}%"))

            filters.append(or_(*search_filters))

        # Role filters
        if role_name:
            query = query.join(Role, User.role_id == Role.id)
            filters.append(func.lower(Role.name) == role_name.lower())

        if role_id:
            filters.append(User.role_id == role_id)

        # Status filter
        if is_active is not None:
            filters.append(User.is_active == is_active)

        # Department filter
        if department:
            filters.append(func.lower(User.department).contains(department.lower()))

        # Apply all filters
        if filters:
            query = query.filter(and_(*filters))

        # Apply pagination and sorting
        return paginate_query(
            query=query,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            model_class=User
        )

    def get_users_by_role(
        self,
        db: Session,
        role_name: str,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[User], int]:
        """Get users by role name with pagination"""
        return self.get_users_with_filters(
            db=db,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            role_name=role_name
        )

    def get_active_users(
        self,
        db: Session,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[User], int]:
        """Get active users with pagination"""
        return self.get_users_with_filters(
            db=db,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            is_active=True
        )

    def get_user_summary(self, db: Session) -> Dict[str, Any]:
        """Get user summary statistics"""
        # Total users count
        total_users = db.query(func.count(User.id)).scalar()

        # Active and inactive users count
        active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
        inactive_users = total_users - active_users

        # Total roles count
        total_roles = db.query(func.count(Role.id)).scalar()

        # Role-wise user counts
        role_counts = (
            db.query(Role.name, func.count(User.id).label('count'))
            .outerjoin(User, User.role_id == Role.id)
            .group_by(Role.id, Role.name)
            .all()
        )

        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "total_roles": total_roles,
            "role_counts": [{"role_name": role.name, "count": role.count} for role in role_counts]
        }

    def get_users_by_multiple_roles(
        self,
        db: Session,
        role_ids: List[str],
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        is_active: Optional[bool] = True
    ) -> tuple[List[User], int]:
        """Get users by multiple role IDs with pagination"""
        query = db.query(User).options(joinedload(User.role))

        # Filter by multiple role IDs
        query = query.filter(User.role_id.in_(role_ids))

        # Filter by active status if specified
        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        # Apply pagination and sorting
        return paginate_query(
            query=query,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            model_class=User
        )

    def get_users_by_roles(self, db: Session, roles: List[str]) -> List[User]:
        """Get users by role IDs without pagination"""
        return db.query(User).options(joinedload(User.role)).filter(
            User.role_id.in_(roles),
            User.is_active == True
        ).all()

    def get_active_users(self, db: Session) -> List[User]:
        """Get all active users without pagination"""
        return db.query(User).options(joinedload(User.role)).filter(
            User.is_active == True
        ).all()

    def refresh_user_permissions(self, db: Session, user_id: str) -> Optional[User]:
        """Force refresh user with latest role and permissions"""
        return db.query(User).options(joinedload(User.role)).filter(User.id == user_id).first()

    def get_team_members(
        self,
        db: Session,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        search: Optional[str] = None,
        is_active: Optional[bool] = True,
        department: Optional[str] = None
    ) -> tuple[List[User], int]:
        """
        Get team members (excludes admin, super admin, and project manager roles)

        Team members are users who are not in management or admin roles.
        Excludes: role_admin, role_super_admin, role_project_manager
        """
        # Roles to exclude from team members
        excluded_role_ids = ["role_admin", "role_super_admin", "role_project_manager"]

        query = db.query(User).options(joinedload(User.role))

        # Exclude management and admin roles
        query = query.filter(~User.role_id.in_(excluded_role_ids))

        # Apply filters
        filters = []

        # Search filter (name and email)
        if search:
            search_term = f"%{search.lower()}%"
            search_filters = [
                func.lower(User.name).contains(search_term),
                func.lower(User.email).contains(search_term)
            ]
            # Split search term to handle first name, last name search
            search_parts = search.lower().split()
            if len(search_parts) > 1:
                # Search for "first last" in name field
                for part in search_parts:
                    search_filters.append(func.lower(User.name).contains(f"%{part}%"))

            filters.append(or_(*search_filters))

        # Status filter
        if is_active is not None:
            filters.append(User.is_active == is_active)

        # Department filter
        if department:
            filters.append(func.lower(User.department).contains(department.lower()))

        # Apply all filters
        if filters:
            query = query.filter(and_(*filters))

        # Apply pagination and sorting
        return paginate_query(
            query=query,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            model_class=User
        )

crud_user = CRUDUser(User)

# Export for backward compatibility
__all__ = ["crud_user", "CRUDUser"]