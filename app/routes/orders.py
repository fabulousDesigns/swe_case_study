from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.utils.sms_sender import send_sms
from app.utils.utils import VerifyToken

from ..models.models import Customer, Order

router = APIRouter()
verify_token = VerifyToken()

class OrderCreate(BaseModel):
    customer_id: int
    item: str
    amount: float
    time: datetime

class OrderUpdate(BaseModel):
    item: str
    amount: float
    time: datetime

class OrderResponse(BaseModel):
    id: int
    customer_id: int
    item: str
    amount: float
    time: datetime
    formatted_time: str

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            customer_id=obj.customer_id,
            item=obj.item,
            amount=obj.amount,
            time=obj.time,
            formatted_time=obj.time.strftime("%Y-%m-%d %H:%M:%S")
        )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def create_order(order: OrderCreate, db: Session):
    db_customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    db_order = Order(
        customer_id=order.customer_id,
        item=order.item,
        amount=order.amount,
        time=order.time
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    message = f"New order placed: {order.item} for ${order.amount:.2f}"
    sms_response = send_sms(str(db_customer.phone_number), message)  # Convert to string

    return {"order": db_order, "sms_response": sms_response}

async def get_orders(skip: int, limit: int, db: Session):
    return db.query(Order).offset(skip).limit(limit).all()

async def search_orders_by_date_range(start_date: str, end_date: str, db: Session):
    try:
        start_datetime = datetime.strptime(start_date, "%Y.%m.%d")
        end_datetime = datetime.strptime(end_date, "%Y.%m.%d").replace(hour=23, minute=59, second=59)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use yyyy.mm.dd")

    orders = db.query(Order).filter(
        and_(
            Order.time >= start_datetime,
            Order.time <= end_datetime
        )
    ).all()

    if not orders:
        raise HTTPException(status_code=404, detail="No orders found in the specified date range")

    return [OrderResponse.from_orm(order) for order in orders]

async def get_order(order_id: int, db: Session):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

async def update_order(order_id: int, order: OrderUpdate, db: Session):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    for key, value in order.dict().items():
        setattr(db_order, key, value)

    db.commit()
    db.refresh(db_order)
    return db_order

async def delete_order(order_id: int, db: Session):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(db_order)
    db.commit()
    return {"message": "Order deleted successfully"}

@router.post("/orders", dependencies=[Depends(verify_token.verify)], tags=["orders"])
async def create_order_route(order: OrderCreate, db: Session = Depends(get_db)):
    return await create_order(order, db)

@router.get("/orders", dependencies=[Depends(verify_token.verify)], tags=["orders"])
async def get_orders_route(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return await get_orders(skip, limit, db)

@router.get("/orders/date_range", response_model=List[OrderResponse], dependencies=[Depends(verify_token.verify)], tags=["orders"])
async def search_orders_by_date_range_route(
    start_date: str = Query(..., description="Start date for the search range (format: yyyy.mm.dd)", example="2024.01.01"),
    end_date: str = Query(..., description="End date for the search range (format: yyyy.mm.dd)", example="2024.12.31"),
    db: Session = Depends(get_db)
):
    return await search_orders_by_date_range(start_date, end_date, db)

@router.get("/orders/{order_id}", dependencies=[Depends(verify_token.verify)], tags=["orders"])
async def get_order_route(order_id: int, db: Session = Depends(get_db)):
    return await get_order(order_id, db)

@router.put("/orders/{order_id}", dependencies=[Depends(verify_token.verify)], tags=["orders"])
async def update_order_route(order_id: int, order: OrderUpdate, db: Session = Depends(get_db)):
    return await update_order(order_id, order, db)

@router.delete("/orders/{order_id}", dependencies=[Depends(verify_token.verify)], tags=["orders"])
async def delete_order_route(order_id: int, db: Session = Depends(get_db)):
    return await delete_order(order_id, db)
