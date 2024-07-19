from datetime import datetime
from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.models import Customer, Order
from app.routes.orders import (OrderCreate, OrderUpdate, create_order,
                               delete_order, get_order, get_orders,
                               search_orders_by_date_range, update_order)


@pytest.fixture
def mock_db():
    return Mock(spec=Session)

@pytest.mark.asyncio
async def test_create_order(mock_db):
    order_data = OrderCreate(
        customer_id=1,
        item="Test Item",
        amount=100.0,
        time=datetime.now()
    )
    mock_customer = Customer(id=1, name="Test Customer", code="TEST001", phone_number="1234567890")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_customer

    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    with patch("app.routes.orders.send_sms") as mock_send_sms:
        mock_send_sms.return_value = {"status": "success"}

        result = await create_order(order_data, mock_db)

    assert result["order"].customer_id == order_data.customer_id
    assert result["order"].item == order_data.item
    assert result["order"].amount == order_data.amount
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    mock_send_sms.assert_called_once()

@pytest.mark.asyncio
async def test_create_order_customer_not_found(mock_db):
    order_data = OrderCreate(
        customer_id=999,
        item="Test Item",
        amount=100.0,
        time=datetime.now()
    )
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await create_order(order_data, mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Customer not found"

@pytest.mark.asyncio
async def test_get_orders(mock_db):
    mock_orders = [
        Order(id=1, customer_id=1, item="Item 1", amount=10.0, time=datetime.now()),
        Order(id=2, customer_id=2, item="Item 2", amount=20.0, time=datetime.now())
    ]
    mock_db.query.return_value.offset.return_value.limit.return_value.all.return_value = mock_orders

    result :Any = await get_orders(0, 10, mock_db)

    assert len(result) == 2
    assert result[0].item == "Item 1"
    assert result[1].item == "Item 2"

@pytest.mark.asyncio
async def test_search_orders_by_date_range(mock_db):
    start_date = "2024.01.01"
    end_date = "2024.12.31"
    mock_orders = [
        Order(id=1, customer_id=1, item="Item 1", amount=10.0, time=datetime.now())
    ]
    mock_db.query.return_value.filter.return_value.all.return_value = mock_orders

    result = await search_orders_by_date_range(start_date, end_date, mock_db)

    assert len(result) == 1
    assert result[0].item == "Item 1"

@pytest.mark.asyncio
async def test_search_orders_by_date_range_invalid_date_format(mock_db):
    start_date = "2024-01-01"  # Incorrect format
    end_date = "2024-12-31"  # Incorrect format

    with pytest.raises(HTTPException) as exc_info:
        await search_orders_by_date_range(start_date, end_date, mock_db)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid date format. Use yyyy.mm.dd"

@pytest.mark.asyncio
async def test_search_orders_by_date_range_no_orders(mock_db):
    start_date = "2024.01.01"
    end_date = "2024.12.31"
    mock_db.query.return_value.filter.return_value.all.return_value = []

    with pytest.raises(HTTPException) as exc_info:
        await search_orders_by_date_range(start_date, end_date, mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "No orders found in the specified date range"

@pytest.mark.asyncio
async def test_get_order(mock_db):
    mock_order = Order(id=1, customer_id=1, item="Test Item", amount=100.0, time=datetime.now())
    mock_db.query.return_value.filter.return_value.first.return_value = mock_order

    result :Any = await get_order(1, mock_db)

    assert result.id == 1
    assert result.item == "Test Item"

@pytest.mark.asyncio
async def test_get_order_not_found(mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await get_order(999, mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Order not found"

@pytest.mark.asyncio
async def test_update_order(mock_db):
    mock_order = Order(id=1, customer_id=1, item="Old Item", amount=50.0, time=datetime.now())
    mock_db.query.return_value.filter.return_value.first.return_value = mock_order

    update_data = OrderUpdate(
        item="Updated Item",
        amount=150.0,
        time=datetime.now()
    )

    result:Any = await update_order(1, update_data, mock_db)

    assert result.item == "Updated Item"
    assert result.amount == 150.0
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_update_order_not_found(mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None

    update_data = OrderUpdate(
        item="Updated Item",
        amount=150.0,
        time=datetime.now()
    )

    with pytest.raises(HTTPException) as exc_info:
        await update_order(999, update_data, mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Order not found"

@pytest.mark.asyncio
async def test_delete_order(mock_db):
    mock_order = Order(id=1, customer_id=1, item="Test Item", amount=100.0, time=datetime.now())
    mock_db.query.return_value.filter.return_value.first.return_value = mock_order

    result = await delete_order(1, mock_db)

    assert result == {"message": "Order deleted successfully"}
    mock_db.delete.assert_called_once_with(mock_order)
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_delete_order_not_found(mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await delete_order(999, mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Order not found"
