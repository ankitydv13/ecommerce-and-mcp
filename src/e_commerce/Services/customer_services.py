from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from e_commerce.database import model
from e_commerce.schemas.schema import Customer, CustomerUpdate

logger = logging.getLogger(__name__)


class CustomerNotFoundError(Exception):
    """Raised when a requested customer does not exist."""


class CustomerHasOrdersError(Exception):
    """Raised when a customer with orders is requested for deletion."""


async def get_customer_by_id(customer_id: int, db: AsyncSession) -> model.Customer | None:
    result = await db.execute(
        select(model.Customer)
        .options(selectinload(model.Customer.orders))
        .where(model.Customer.id == customer_id)
    )
    return result.scalar_one_or_none()


async def get_customer_or_raise(customer_id: int, db: AsyncSession) -> model.Customer:
    customer = await get_customer_by_id(customer_id, db)
    if customer is None:
        raise CustomerNotFoundError(customer_id)
    return customer


async def create_customer(customer_data: Customer, db: AsyncSession) -> model.Customer:
    customer = model.Customer(**customer_data.model_dump())
    db.add(customer)

    try:
        await db.commit()
        await db.refresh(customer)
    except Exception:
        await db.rollback()
        logger.exception("Failed to create customer")
        raise

    return customer


async def update_customer(
    customer: model.Customer,
    update_data: CustomerUpdate,
    db: AsyncSession,
) -> model.Customer:
    changes = update_data.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in changes.items():
        setattr(customer, field, value)

    try:
        await db.commit()
        await db.refresh(customer)
    except Exception:
        await db.rollback()
        logger.exception("Failed to update customer id=%s", customer.id)
        raise

    return customer


async def delete_customer(customer: model.Customer, db: AsyncSession) -> model.Customer:
    if customer.orders:
        raise CustomerHasOrdersError(customer.id)

    try:
        await db.delete(customer)
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("Failed to delete customer id=%s", customer.id)
        raise

    return customer
