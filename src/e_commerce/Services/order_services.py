from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from e_commerce.database import model
from e_commerce.schemas.schema import OrderCreate, OrderUpdate

logger = logging.getLogger(__name__)


class OrderNotFoundError(Exception):
    pass


class CustomerNotFoundForOrderError(Exception):
    pass


class OrderHasItemsError(Exception):
    pass


async def get_order_or_raise(order_id: int, db: AsyncSession) -> model.Orders:
    result = await db.execute(select(model.Orders).where(model.Orders.id == order_id))
    order = result.scalar_one_or_none()
    if order is None:
        raise OrderNotFoundError(order_id)
    return order


async def create_order(data: OrderCreate, db: AsyncSession) -> model.Orders:
    if await db.get(model.Customer, data.customer_id) is None:
        raise CustomerNotFoundForOrderError(data.customer_id)
    order = model.Orders(**data.model_dump())
    db.add(order)
    try:
        await db.commit()
        await db.refresh(order)
    except Exception:
        await db.rollback()
        logger.exception("Failed to create order")
        raise
    return order


async def update_order(order: model.Orders, data: OrderUpdate, db: AsyncSession) -> model.Orders:
    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    if "customer_id" in changes and await db.get(model.Customer, changes["customer_id"]) is None:
        raise CustomerNotFoundForOrderError(changes["customer_id"])
    for field, value in changes.items():
        setattr(order, field, value)
    try:
        await db.commit()
        await db.refresh(order)
    except Exception:
        await db.rollback()
        logger.exception("Failed to update order id=%s", order.id)
        raise
    return order


async def delete_order(order: model.Orders, db: AsyncSession) -> model.Orders:
    result = await db.execute(
        select(model.OrderItems.id).where(model.OrderItems.order_id == order.id).limit(1)
    )
    if result.scalar_one_or_none() is not None:
        raise OrderHasItemsError(order.id)
    try:
        await db.delete(order)
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("Failed to delete order id=%s", order.id)
        raise
    return order
