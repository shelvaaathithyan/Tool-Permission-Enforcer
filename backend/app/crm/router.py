import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db

from . import schemas, service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("", response_model=schemas.CustomerListResponse)
def list_customers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    try:
        customers, total = service.get_customers(db, page=page, page_size=page_size)
        return schemas.CustomerListResponse(
            items=customers,
            page=page,
            page_size=page_size,
            total=total
        )
    except Exception as e:
        logger.error(f"Error listing customers: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.get("/{customer_id}", response_model=schemas.CustomerResponse)
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    try:
        return service.get_customer_by_customer_id(db, customer_id)
    except service.CustomerNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    except Exception as e:
        logger.error(f"Error getting customer {customer_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.post("", response_model=schemas.CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(customer_in: schemas.CustomerCreate, db: Session = Depends(get_db)):
    try:
        return service.create_customer(db, customer_in)
    except service.DuplicateCustomerError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Customer with this email already exists")
    except Exception as e:
        logger.error(f"Error creating customer: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.patch("/{customer_id}", response_model=schemas.CustomerResponse)
def update_customer(customer_id: str, customer_in: schemas.CustomerUpdate, db: Session = Depends(get_db)):
    try:
        return service.update_customer(db, customer_id, customer_in)
    except service.CustomerNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    except service.DuplicateCustomerError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Customer with this email already exists")
    except Exception as e:
        logger.error(f"Error updating customer {customer_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: str, db: Session = Depends(get_db)):
    try:
        service.delete_customer(db, customer_id)
    except service.CustomerNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    except Exception as e:
        logger.error(f"Error deleting customer {customer_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
