import uuid
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
