from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from e_commerce.database import model
from e_commerce.schemas.schema import ProductCreate, ProductUpdate

logger = logging.getLogger(__name__)


class ProductNotFoundError(Exception):
    pass


class ProductHasOrderItemsError(Exception):
    pass


async def get_product_or_raise(product_id: int, db: AsyncSession) -> model.Product:
    result = await db.execute(select(model.Product).where(model.Product.id == product_id))
    product = result.scalar_one_or_none()
    if product is None:
        raise ProductNotFoundError(product_id)
    return product


async def create_product(data: ProductCreate, db: AsyncSession) -> model.Product:
    product = model.Product(**data.model_dump())
    db.add(product)
    try:
        await db.commit()
        await db.refresh(product)
    except Exception:
        await db.rollback()
        logger.exception("Failed to create product")
        raise
    return product


async def update_product(product: model.Product, data: ProductUpdate, db: AsyncSession) -> model.Product:
    for field, value in data.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(product, field, value)
    try:
        await db.commit()
        await db.refresh(product)
    except Exception:
        await db.rollback()
        logger.exception("Failed to update product id=%s", product.id)
        raise
    return product


async def delete_product(product: model.Product, db: AsyncSession) -> model.Product:
    result = await db.execute(
        select(model.OrderItems.id).where(model.OrderItems.product_id == product.id).limit(1)
    )
    if result.scalar_one_or_none() is not None:
        raise ProductHasOrderItemsError(product.id)
    try:
        await db.delete(product)
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("Failed to delete product id=%s", product.id)
        raise
    return product
