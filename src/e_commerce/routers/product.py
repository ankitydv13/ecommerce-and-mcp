from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from e_commerce.database.session import get_db
from e_commerce.schemas.schema import ProductCreate, ProductResponse, ProductUpdate
from e_commerce.Services.product_services import (
    ProductHasOrderItemsError, ProductNotFoundError, create_product,
    delete_product, get_product_or_raise, update_product,
)

router = APIRouter()
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


def not_found(product_id: int) -> HTTPException:
    return HTTPException(status_code=404, detail=f"Product with id {product_id} does not exist")


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: DatabaseSession):
    try:
        product = await get_product_or_raise(product_id, db)
    except ProductNotFoundError:
        raise not_found(product_id) from None
    return ProductResponse.model_validate(product)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def add_product(product: ProductCreate, db: DatabaseSession):
    try:
        created = await create_product(product, db)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="A product with this name already exists") from None
    return ProductResponse.model_validate(created)


@router.patch("/patch/{product_id}", response_model=ProductResponse)
async def update_product_route(product_id: int, update_schema: ProductUpdate, db: DatabaseSession):
    try:
        product = await get_product_or_raise(product_id, db)
        updated = await update_product(product, update_schema, db)
    except ProductNotFoundError:
        raise not_found(product_id) from None
    except IntegrityError:
        raise HTTPException(status_code=409, detail="A product with this name already exists") from None
    return ProductResponse.model_validate(updated)


@router.delete("/delete/{product_id}", response_model=ProductResponse)
async def delete_product_route(product_id: int, db: DatabaseSession):
    try:
        product = await get_product_or_raise(product_id, db)
        deleted = await delete_product(product, db)
    except ProductNotFoundError:
        raise not_found(product_id) from None
    except ProductHasOrderItemsError:
        raise HTTPException(status_code=409, detail="Cannot delete a product used by order items") from None
    return ProductResponse.model_validate(deleted)
