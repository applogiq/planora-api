from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import math

from app.db.database import get_db
from . import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.CustomerResponse, summary="Create Customer")
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    """
    Create a new customer.

    - **name**: Customer name (required)
    - **industry**: Industry type
    - **contact**: Contact information including name, email, phone, title
    - **website**: Company website
    - **address**: Business address
    - **status**: Customer status (Active, Inactive, Prospect)
    - **priority**: Priority level (Low, Medium, High, Critical)
    - **notes**: Additional notes
    """
    try:
        # Check if customer with same name already exists
        existing_customer = crud.get_customer_by_name(db, customer.name)
        if existing_customer:
            raise HTTPException(status_code=400, detail="Customer with this name already exists")

        db_customer = crud.create_customer(db, customer)
        return schemas.CustomerResponse.from_orm(db_customer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating customer: {str(e)}")

@router.get("/", response_model=schemas.CustomerListResponse, summary="Get Customers")
def get_customers(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    name: Optional[str] = Query(None, description="Filter by customer name"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    min_revenue: Optional[float] = Query(None, description="Minimum revenue filter"),
    max_revenue: Optional[float] = Query(None, description="Maximum revenue filter"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    db: Session = Depends(get_db)
):
    """
    Get customers with filtering and pagination.

    - **page**: Page number (starts from 1)
    - **size**: Number of items per page (max 100)
    - **name**: Filter customers by name (partial match)
    - **industry**: Filter by industry
    - **status**: Filter by status (Active, Inactive, Prospect)
    - **priority**: Filter by priority (Low, Medium, High, Critical)
    - **min_revenue**: Minimum total revenue
    - **max_revenue**: Maximum total revenue
    - **project_id**: Filter customers associated with specific project
    """
    try:
        skip = (page - 1) * size

        filters = schemas.CustomerFilter(
            name=name,
            industry=industry,
            status=status,
            priority=priority,
            min_revenue=min_revenue,
            max_revenue=max_revenue,
            project_id=project_id
        )

        customers, total = crud.get_customers(db, skip=skip, limit=size, filters=filters)

        total_pages = math.ceil(total / size)
        has_next = page < total_pages
        has_prev = page > 1

        return schemas.CustomerListResponse(
            customers=[schemas.CustomerResponse.from_orm(customer) for customer in customers],
            total=total,
            page=page,
            size=size,
            has_next=has_next,
            has_prev=has_prev
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching customers: {str(e)}")

@router.get("/{customer_id}", response_model=schemas.CustomerResponse, summary="Get Customer Details")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific customer.

    - **customer_id**: Unique customer identifier
    """
    db_customer = crud.get_customer(db, customer_id)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return schemas.CustomerResponse.from_orm(db_customer)

@router.put("/{customer_id}", response_model=schemas.CustomerResponse, summary="Update Customer")
def update_customer(
    customer_id: str,
    customer_update: schemas.CustomerUpdate,
    db: Session = Depends(get_db)
):
    """
    Update customer information.

    - **customer_id**: Unique customer identifier
    - **customer_update**: Fields to update (only provided fields will be updated)
    """
    try:
        # Check if customer exists
        existing_customer = crud.get_customer(db, customer_id)
        if not existing_customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        # If updating name, check if new name conflicts with existing customer
        if customer_update.name and customer_update.name != existing_customer.name:
            name_conflict = crud.get_customer_by_name(db, customer_update.name)
            if name_conflict:
                raise HTTPException(status_code=400, detail="Customer with this name already exists")

        updated_customer = crud.update_customer(db, customer_id, customer_update)
        if not updated_customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        return schemas.CustomerResponse.from_orm(updated_customer)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating customer: {str(e)}")

@router.delete("/{customer_id}", summary="Delete Customer")
def delete_customer(customer_id: str, db: Session = Depends(get_db)):
    """
    Soft delete a customer (marks as inactive).

    - **customer_id**: Unique customer identifier
    """
    success = crud.delete_customer(db, customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")

    return {"message": "Customer deleted successfully"}

@router.get("/search/", response_model=List[schemas.CustomerResponse], summary="Search Customers")
def search_customers(
    q: str = Query(..., min_length=2, description="Search term"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """
    Search customers by name, industry, or contact email.

    - **q**: Search term (minimum 2 characters)
    - **limit**: Maximum number of results (max 50)
    """
    try:
        customers = crud.search_customers(db, q, limit)
        return [schemas.CustomerResponse.from_orm(customer) for customer in customers]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching customers: {str(e)}")

@router.get("/by-industry/{industry}", response_model=List[schemas.CustomerResponse], summary="Get Customers by Industry")
def get_customers_by_industry(industry: str, db: Session = Depends(get_db)):
    """
    Get all customers in a specific industry.

    - **industry**: Industry name
    """
    try:
        customers = crud.get_customers_by_industry(db, industry)
        return [schemas.CustomerResponse.from_orm(customer) for customer in customers]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching customers by industry: {str(e)}")

@router.get("/by-status/{status}", response_model=List[schemas.CustomerResponse], summary="Get Customers by Status")
def get_customers_by_status(status: str, db: Session = Depends(get_db)):
    """
    Get all customers with a specific status.

    - **status**: Customer status (Active, Inactive, Prospect)
    """
    try:
        customers = crud.get_customers_by_status(db, status)
        return [schemas.CustomerResponse.from_orm(customer) for customer in customers]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching customers by status: {str(e)}")