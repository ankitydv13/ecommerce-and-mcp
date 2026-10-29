from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from e_commerce.database import database_model
from e_commerce.database.database import get_db
from e_commerce.schemas.schema import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter()


@router.get("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(database_model.Product).where(database_model.Product.id == product_id))
    existing_product = result.scalars().first()
    if not existing_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product Not Found")
    return ProductResponse.model_validate(existing_product)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def add_product(product: ProductCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    new_product = database_model.Product(
        name=product.name,
        price=product.price,
        description=product.description,
    )
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return ProductResponse.model_validate(new_product)


@router.patch("/patch/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    update_schema: ProductUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(database_model.Product).where(database_model.Product.id == product_id))
    existing_product = result.scalars().first()
    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} does not exist",
        )

    for field, value in update_schema.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(existing_product, field, value)

    await db.commit()
    await db.refresh(existing_product)
    return ProductResponse.model_validate(existing_product)


@router.delete("/delete/{product_id}", response_model=ProductResponse)
async def delete_product(product_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(database_model.Product).where(database_model.Product.id == product_id))
    existing_product = result.scalars().first()
    if not existing_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product Not Found")

    order_items = await db.execute(
        select(database_model.OrderIteams.id).where(database_model.OrderIteams.product_id == product_id)
    )
    if order_items.scalars().first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a product that is used by order items",
        )

    deleted_product = ProductResponse.model_validate(existing_product)
    await db.delete(existing_product)
    await db.commit()
    return deleted_product
