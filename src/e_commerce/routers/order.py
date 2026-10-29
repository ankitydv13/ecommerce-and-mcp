from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from e_commerce.database import database_model
from e_commerce.database.database import get_db
from e_commerce.schemas.schema import OrderCreate, OrderResponse, OrderUpdate

router = APIRouter()


@router.get("/{order_id}", response_model=OrderResponse, status_code=status.HTTP_200_OK)
async def get_order(order_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(database_model.Orders).where(database_model.Orders.id == order_id))
    existing_order = result.scalars().first()
    if not existing_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order Not Found")
    return OrderResponse.model_validate(existing_order)


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def add_order(order: OrderCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    customer = await db.get(database_model.Customer, order.customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer Not Found")

    new_order = database_model.Orders(
        customer_id=order.customer_id,
        total_amount=order.total_amount,
    )
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    return OrderResponse.model_validate(new_order)


@router.patch("/patch/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    update_schema: OrderUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(database_model.Orders).where(database_model.Orders.id == order_id))
    existing_order = result.scalars().first()
    if not existing_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} does not exist",
        )

    updates = update_schema.model_dump(exclude_unset=True, exclude_none=True)
    if "customer_id" in updates:
        customer = await db.get(database_model.Customer, updates["customer_id"])
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer Not Found")

    for field, value in updates.items():
        setattr(existing_order, field, value)

    await db.commit()
    await db.refresh(existing_order)
    return OrderResponse.model_validate(existing_order)


@router.delete("/delete/{order_id}", response_model=OrderResponse)
async def delete_order(order_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(database_model.Orders).where(database_model.Orders.id == order_id))
    existing_order = result.scalars().first()
    if not existing_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order Not Found")

    order_items = await db.execute(
        select(database_model.OrderIteams.id).where(database_model.OrderIteams.order_id == order_id)
    )
    if order_items.scalars().first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete an order that contains order items",
        )

    deleted_order = OrderResponse.model_validate(existing_order)
    await db.delete(existing_order)
    await db.commit()
    return deleted_order
