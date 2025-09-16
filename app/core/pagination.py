from typing import Generic, TypeVar, List, Optional, Any
from pydantic import BaseModel, Field
from sqlalchemy.orm import Query
from sqlalchemy import desc, asc
from math import ceil

T = TypeVar('T')

class PaginationParams(BaseModel):
    """Pagination parameters for API endpoints"""
    page: int = Field(default=1, ge=1, description="Page number (starts from 1)")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: str = Field(default="asc", pattern="^(asc|desc)$", description="Sort order: asc or desc")

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model"""
    items: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        per_page: int
    ) -> "PaginatedResponse[T]":
        """Create a paginated response from items and metadata"""
        total_pages = ceil(total / per_page) if per_page > 0 else 0

        return cls(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )

def paginate_query(
    query: Query,
    page: int = 1,
    per_page: int = 20,
    sort_by: Optional[str] = None,
    sort_order: str = "asc",
    model_class: Any = None
) -> tuple[List[Any], int]:
    """
    Apply pagination and sorting to a SQLAlchemy query

    Args:
        query: SQLAlchemy query object
        page: Page number (starts from 1)
        per_page: Items per page
        sort_by: Field name to sort by
        sort_order: Sort order ('asc' or 'desc')
        model_class: Model class for sorting validation

    Returns:
        Tuple of (items, total_count)
    """
    # Get total count before applying pagination
    total = query.count()

    # Apply sorting if specified
    if sort_by and model_class:
        if hasattr(model_class, sort_by):
            sort_column = getattr(model_class, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

    # Apply pagination
    offset = (page - 1) * per_page
    items = query.offset(offset).limit(per_page).all()

    return items, total