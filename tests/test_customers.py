from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.models import Customer
from app.routes.customers import (CustomerCreate, CustomerUpdate,
                                  create_customer, delete_customer,
                                  get_all_customers, get_customer,
                                  update_customer)


@pytest.fixture
def mock_db():
    return Mock(spec=Session)

@pytest.mark.asyncio
async def test_create_customer(mock_db):
    customer_data = CustomerCreate(
        name="Test Customer",
        code="TEST001",
        phone_number="1234567890"
    )
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    result: Any = await create_customer(customer_data, mock_db)

    assert result.name == customer_data.name
    assert result.code == customer_data.code
    assert result.phone_number == customer_data.phone_number
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_get_all_customers(mock_db):
    mock_customers = [
        Customer(id=1, name="Customer 1", code="C001", phone_number="1111111111"),
        Customer(id=2, name="Customer 2", code="C002", phone_number="2222222222")
    ]
    mock_db.query.return_value.offset.return_value.limit.return_value.all.return_value = mock_customers

    result: Any = await get_all_customers(0, 100, mock_db)

    assert len(result) == 2
    assert result[0].name == "Customer 1"
    assert result[1].name == "Customer 2"

@pytest.mark.asyncio
async def test_get_customer(mock_db):
    mock_customer = Customer(id=1, name="Test Customer", code="TEST001", phone_number="1234567890")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_customer

    result: Any = await get_customer(1, mock_db)

    assert result.id == 1
    assert result.name == "Test Customer"
    assert result.code == "TEST001"

@pytest.mark.asyncio
async def test_get_customer_not_found(mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await get_customer(1, mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Customer not found"

@pytest.mark.asyncio
async def test_update_customer(mock_db):
    mock_customer = Customer(id=1, name="Old Name", code="OLD001", phone_number="0000000000")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_customer

    update_data = CustomerUpdate(
        name="New Name",
        code="NEW001",
        phone_number="1111111111"
    )

    result: Any = await update_customer(1, update_data, mock_db)

    assert result.name == "New Name"
    assert result.code == "NEW001"
    assert result.phone_number == "1111111111"
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_delete_customer(mock_db):
    mock_customer = Customer(id=1, name="Test Customer", code="TEST001", phone_number="1234567890")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_customer

    result = await delete_customer(1, mock_db)

    assert result == {"message": "Customer deleted successfully"}
    mock_db.delete.assert_called_once_with(mock_customer)
    mock_db.commit.assert_called_once()