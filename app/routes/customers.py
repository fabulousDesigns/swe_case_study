from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.utils.utils import VerifyToken

from ..models.models import Customer

router = APIRouter()
verify_token = VerifyToken()

class CustomerBase(BaseModel):
    name: str
    code: str
    phone_number: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    phone_number: Optional[str] = None

class CustomerResponse(CustomerBase):
    id: int

    class Config:
        from_attributes = True

async def create_customer(customer: CustomerCreate, db: Session):
    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

async def get_all_customers(skip: int, limit: int, db: Session):
    customers = db.query(Customer).offset(skip).limit(limit).all()
    return customers

async def get_customer(customer_id: int, db: Session):
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

async def update_customer(customer_id: int, customer: CustomerUpdate, db: Session):
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    update_data = customer.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_customer, key, value)

    db.commit()
    db.refresh(db_customer)
    return db_customer

async def delete_customer(customer_id: int, db: Session):
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(db_customer)
    db.commit()
    return {"message": "Customer deleted successfully"}

@router.post("/customers", response_model=CustomerResponse, dependencies=[Depends(verify_token.verify)], tags=["customers"])
async def create_customer_route(customer: CustomerCreate, db: Session = Depends(get_db)):
    return await create_customer(customer, db)

@router.get("/customers", response_model=List[CustomerResponse], dependencies=[Depends(verify_token.verify)], tags=["customers"])
async def get_all_customers_route(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return await get_all_customers(skip, limit, db)

@router.get("/customers/{customer_id}", response_model=CustomerResponse, dependencies=[Depends(verify_token.verify)], tags=["customers"])
async def get_customer_route(customer_id: int, db: Session = Depends(get_db)):
    return await get_customer(customer_id, db)

@router.put("/customers/{customer_id}", response_model=CustomerResponse, dependencies=[Depends(verify_token.verify)], tags=["customers"])
async def update_customer_route(customer_id: int, customer: CustomerUpdate, db: Session = Depends(get_db)):
    return await update_customer(customer_id, customer, db)

@router.delete("/customers/{customer_id}", dependencies=[Depends(verify_token.verify)], tags=["customers"])
async def delete_customer_route(customer_id: int, db: Session = Depends(get_db)):
    return await delete_customer(customer_id, db)