from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
import uuid

class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    designation: Optional[str] = None
    date_of_birth: Optional[date] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    designation: Optional[str] = None
    date_of_birth: Optional[date] = None
    session_status: Optional[str] = Field(None, pattern="^(ACTIVE|INACTIVE)$")

class CustomerResponse(CustomerBase):
    id: uuid.UUID
    customer_id: str
    session_status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CustomerListResponse(BaseModel):
    items: List[CustomerResponse]
    page: int
    page_size: int
    total: int
