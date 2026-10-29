from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from e_commerce.database import database_model
from e_commerce.database.database import get_db
from e_commerce.schemas.schema import OrderItemCreate, OrderItemResponse, OrderItemUpdate

router = APIRouter()


@router.get("/{order_item_id}", response_model=OrderItemResponse, status_code=status.HTTP_200_OK)
async def get_order_item(order_item_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(database_model.OrderIteams).where(database_model.OrderIteams.id == order_item_id)
    )
    existing_order_item = result.scalars().first()
    if not existing_order_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order Item Not Found")
    return OrderItemResponse.model_validate(existing_order_item)


@router.post("", response_model=OrderItemResponse, status_code=status.HTTP_201_CREATED)
async def add_order_item(order_item: OrderItemCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    order = await db.get(database_model.Orders, order_item.order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order Not Found")

    product = await db.get(database_model.Product, order_item.product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product Not Found")

    new_order_item = database_model.OrderIteams(
        order_id=order_item.order_id,
        product_id=order_item.product_id,
        quantity=order_item.quantity,
    )
    db.add(new_order_item)
    await db.commit()
    await db.refresh(new_order_item)
    return OrderItemResponse.model_validate(new_order_item)


@router.patch("/patch/{order_item_id}", response_model=OrderItemResponse)
async def update_order_item(
    order_item_id: int,
    update_schema: OrderItemUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(database_model.OrderIteams).where(database_model.OrderIteams.id == order_item_id)
    )
    existing_order_item = result.scalars().first()
    if not existing_order_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order item with id {order_item_id} does not exist",
        )

    updates = update_schema.model_dump(exclude_unset=True, exclude_none=True)
    if "order_id" in updates:
        order = await db.get(database_model.Orders, updates["order_id"])
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order Not Found")
    if "product_id" in updates:
        product = await db.get(database_model.Product, updates["product_id"])
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product Not Found")

    for field, value in updates.items():
        setattr(existing_order_item, field, value)

    await db.commit()
    await db.refresh(existing_order_item)
    return OrderItemResponse.model_validate(existing_order_item)


@router.delete("/delete/{order_item_id}", response_model=OrderItemResponse)
async def delete_order_item(order_item_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(database_model.OrderIteams).where(database_model.OrderIteams.id == order_item_id)
    )
    existing_order_item = result.scalars().first()
    if not existing_order_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order Item Not Found")

    deleted_order_item = OrderItemResponse.model_validate(existing_order_item)
    await db.delete(existing_order_item)
    await db.commit()
    return deleted_order_item
