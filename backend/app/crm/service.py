import uuid
import re
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from .models import Customer
from .schemas import CustomerCreate, CustomerUpdate

class CustomerNotFoundError(Exception):
    pass

class DuplicateCustomerError(Exception):
    pass

def _generate_customer_id() -> str:
    return f"CUST-{uuid.uuid4().hex[:8].upper()}"

def normalize_customer_name(value: str) -> str:
    if not value:
        return ""
    # Trim, collapse whitespace, lowercase
    return re.sub(r'\s+', ' ', str(value).strip()).lower()

def normalize_search_text(value: str) -> str:
    if not value:
        return ""
    val = str(value).lower()
    # Replace punctuation with spaces to tolerate variations
    val = re.sub(r'[.,-]', ' ', val)
    return re.sub(r'\s+', ' ', val).strip()

def get_customer_by_customer_id(db: Session, customer_id: str) -> Customer:
    customer = db.scalars(select(Customer).where(Customer.customer_id == customer_id)).first()
    if not customer:
        raise CustomerNotFoundError()
    return customer

def get_customers(db: Session, page: int = 1, page_size: int = 20) -> Tuple[List[Customer], int]:
    offset = (page - 1) * page_size
    query = select(Customer)
    total = db.scalar(select(func.count()).select_from(Customer))
    customers = db.scalars(query.offset(offset).limit(page_size)).all()
    return list(customers), total or 0

def search_customers(db: Session, search_query: str = "", company: str = None, designation: str = None) -> List[Customer]:
    query = select(Customer)
    
    # Helper to clean up DB values for matching
    def _db_clean(col):
        return func.replace(func.replace(func.replace(func.lower(col), '.', ' '), ',', ' '), '-', ' ')

    if search_query:
        norm_query = normalize_search_text(search_query)
        if norm_query:
            search_term = f"%{norm_query.replace(' ', '%')}%"
            query = query.where(
                (_db_clean(func.concat(Customer.first_name, ' ', Customer.last_name)).like(search_term)) |
                (_db_clean(Customer.email).like(search_term))
            )
            
    if company:
        norm_company = normalize_search_text(company)
        if norm_company:
            query = query.where(_db_clean(Customer.company).like(f"%{norm_company.replace(' ', '%')}%"))
            
    if designation:
        norm_designation = normalize_search_text(designation)
        if norm_designation:
            query = query.where(_db_clean(Customer.designation).like(f"%{norm_designation.replace(' ', '%')}%"))

    if not search_query and not company and not designation:
        return []
        
    query = query.limit(50)
    customers = db.scalars(query).all()
    return list(customers)

def create_customer(db: Session, customer_in: CustomerCreate) -> Customer:
    customer_id = _generate_customer_id()
    db_customer = Customer(
        customer_id=customer_id,
        **customer_in.model_dump()
    )
    db.add(db_customer)
    try:
        db.commit()
        db.refresh(db_customer)
        return db_customer
    except IntegrityError:
        db.rollback()
        raise DuplicateCustomerError()

def update_customer(db: Session, customer_id: str, customer_in: CustomerUpdate) -> Customer:
    db_customer = get_customer_by_customer_id(db, customer_id)
    update_data = customer_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_customer, field, value)
    
    try:
        db.commit()
        db.refresh(db_customer)
        return db_customer
    except IntegrityError:
        db.rollback()
        raise DuplicateCustomerError()

def delete_customer(db: Session, customer_id: str) -> None:
    db_customer = get_customer_by_customer_id(db, customer_id)
    db.delete(db_customer)
    db.commit()
