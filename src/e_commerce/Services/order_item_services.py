from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from e_commerce.database import model
from e_commerce.schemas.schema import OrderItemCreate, OrderItemUpdate

logger = logging.getLogger(__name__)


class OrderItemNotFoundError(Exception):
    pass


class OrderNotFoundForItemError(Exception):
    pass


class ProductNotFoundForItemError(Exception):
    pass


async def get_order_item_or_raise(order_item_id: int, db: AsyncSession) -> model.OrderItems:
    result = await db.execute(
        select(model.OrderItems).where(model.OrderItems.id == order_item_id)
    )
    item = result.scalar_one_or_none()
    if item is None:
        raise OrderItemNotFoundError(order_item_id)
    return item


async def validate_references(order_id: int, product_id: int, db: AsyncSession) -> None:
    if await db.get(model.Orders, order_id) is None:
        raise OrderNotFoundForItemError(order_id)
    if await db.get(model.Product, product_id) is None:
        raise ProductNotFoundForItemError(product_id)


async def create_order_item(data: OrderItemCreate, db: AsyncSession) -> model.OrderItems:
    await validate_references(data.order_id, data.product_id, db)
    item = model.OrderItems(**data.model_dump())
    db.add(item)
    try:
        await db.commit()
        await db.refresh(item)
    except Exception:
        await db.rollback()
        logger.exception("Failed to create order item")
        raise
    return item


async def update_order_item(
    item: model.OrderItems,
    data: OrderItemUpdate,
    db: AsyncSession,
) -> model.OrderItems:
    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    await validate_references(
        changes.get("order_id", item.order_id),
        changes.get("product_id", item.product_id),
        db,
    )
    for field, value in changes.items():
        setattr(item, field, value)
    try:
        await db.commit()
        await db.refresh(item)
    except Exception:
        await db.rollback()
        logger.exception("Failed to update order item id=%s", item.id)
        raise
    return item


async def delete_order_item(item: model.OrderItems, db: AsyncSession) -> model.OrderItems:
    try:
        await db.delete(item)
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("Failed to delete order item id=%s", item.id)
        raise
    return item
