from sqlalchemy import (Column, DateTime, Float, ForeignKey, Index, Integer,
                        String)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    code = Column(String, unique=True, index=True)
    phone_number = Column(String, index=True, nullable=True)
    date_created = Column(DateTime, server_default=func.now(), index=True)
    date_updated = Column(DateTime, server_default=func.now(), onupdate=func.now(), index=True)

    orders = relationship("Order", back_populates="customer", lazy="dynamic")

    __table_args__ = (
        Index('ix_customers_name_code', 'name', 'code'),
    )

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), index=True)
    item = Column(String, index=True)
    amount = Column(Float, index=True)
    time = Column(DateTime, index=True)
    date_created = Column(DateTime, server_default=func.now(), index=True)
    date_updated = Column(DateTime, server_default=func.now(), onupdate=func.now(), index=True)

    customer = relationship("Customer", back_populates="orders")

    __table_args__ = (
        Index('ix_orders_customer_id_time', 'customer_id', 'time'),
        Index('ix_orders_time_amount', 'time', 'amount'),
    )