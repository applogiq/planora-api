from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from . import models, schemas
import uuid

def create_customer(db: Session, customer: schemas.CustomerCreate) -> models.Customer:
    """Create a new customer"""
    customer_id = f"CUST-{str(uuid.uuid4())[:8].upper()}"

    # Convert contact and address to dict for JSON storage
    contact_dict = customer.contact.dict() if customer.contact else None
    address_dict = customer.address.dict() if customer.address else None

    db_customer = models.Customer(
        id=customer_id,
        name=customer.name,
        industry=customer.industry,
        contact=contact_dict,
        website=customer.website,
        address=address_dict,
        status=customer.status,
        join_date=customer.join_date,
        last_activity=customer.last_activity,
        total_revenue=customer.total_revenue,
        project_ids=customer.project_ids,
        priority=customer.priority,
        notes=customer.notes
    )

    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def get_customer(db: Session, customer_id: str) -> Optional[models.Customer]:
    """Get a customer by ID"""
    return db.query(models.Customer).filter(
        models.Customer.id == customer_id,
        models.Customer.is_active == True
    ).first()

def update_customer(db: Session, customer_id: str, customer_update: schemas.CustomerUpdate) -> Optional[models.Customer]:
    """Update a customer"""
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return None

    update_data = customer_update.dict(exclude_unset=True)

    # Handle contact and address updates
    if "contact" in update_data and update_data["contact"]:
        update_data["contact"] = update_data["contact"].dict()
    if "address" in update_data and update_data["address"]:
        update_data["address"] = update_data["address"].dict()

    for field, value in update_data.items():
        setattr(db_customer, field, value)

    db.commit()
    db.refresh(db_customer)
    return db_customer

def delete_customer(db: Session, customer_id: str) -> bool:
    """Soft delete a customer"""
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return False

    db_customer.is_active = False
    db.commit()
    return True

def get_customers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[schemas.CustomerFilter] = None
) -> tuple[List[models.Customer], int]:
    """Get customers with filtering and pagination"""
    query = db.query(models.Customer).filter(models.Customer.is_active == True)

    if filters:
        if filters.name:
            query = query.filter(models.Customer.name.ilike(f"%{filters.name}%"))

        if filters.industry:
            query = query.filter(models.Customer.industry.ilike(f"%{filters.industry}%"))

        if filters.status:
            query = query.filter(models.Customer.status == filters.status)

        if filters.priority:
            query = query.filter(models.Customer.priority == filters.priority)

        if filters.min_revenue is not None:
            query = query.filter(models.Customer.total_revenue >= filters.min_revenue)

        if filters.max_revenue is not None:
            query = query.filter(models.Customer.total_revenue <= filters.max_revenue)

        if filters.project_id:
            query = query.filter(models.Customer.project_ids.contains([filters.project_id]))

    total = query.count()
    customers = query.order_by(models.Customer.created_at.desc()).offset(skip).limit(limit).all()

    return customers, total

def get_customer_by_name(db: Session, name: str) -> Optional[models.Customer]:
    """Get customer by name"""
    return db.query(models.Customer).filter(
        models.Customer.name == name,
        models.Customer.is_active == True
    ).first()

def search_customers(db: Session, search_term: str, limit: int = 10) -> List[models.Customer]:
    """Search customers by name, industry, or contact email"""
    return db.query(models.Customer).filter(
        and_(
            models.Customer.is_active == True,
            or_(
                models.Customer.name.ilike(f"%{search_term}%"),
                models.Customer.industry.ilike(f"%{search_term}%"),
                models.Customer.contact['email'].astext.ilike(f"%{search_term}%")
            )
        )
    ).limit(limit).all()

def get_customers_by_industry(db: Session, industry: str) -> List[models.Customer]:
    """Get all customers in a specific industry"""
    return db.query(models.Customer).filter(
        models.Customer.industry == industry,
        models.Customer.is_active == True
    ).all()

def get_customers_by_status(db: Session, status: str) -> List[models.Customer]:
    """Get all customers with a specific status"""
    return db.query(models.Customer).filter(
        models.Customer.status == status,
        models.Customer.is_active == True
    ).all()