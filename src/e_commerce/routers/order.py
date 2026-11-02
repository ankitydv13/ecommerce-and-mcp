from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from e_commerce.Services.order_services import (
    CustomerNotFoundForOrderError, OrderHasItemsError, OrderNotFoundError,
    create_order, delete_order, get_order_or_raise, update_order,
)
from e_commerce.database.session import get_db
from e_commerce.schemas.schema import OrderCreate, OrderResponse, OrderUpdate

router = APIRouter()
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


def not_found(order_id: int) -> HTTPException:
    return HTTPException(status_code=404, detail=f"Order with id {order_id} does not exist")


def customer_not_found() -> HTTPException:
    return HTTPException(status_code=404, detail="Customer Not Found")


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: DatabaseSession):
    try:
        order = await get_order_or_raise(order_id, db)
    except OrderNotFoundError:
        raise not_found(order_id) from None
    return OrderResponse.model_validate(order)


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def add_order(order: OrderCreate, db: DatabaseSession):
    try:
        created = await create_order(order, db)
    except CustomerNotFoundForOrderError:
        raise customer_not_found() from None
    return OrderResponse.model_validate(created)


@router.patch("/patch/{order_id}", response_model=OrderResponse)
async def update_order_route(order_id: int, update_schema: OrderUpdate, db: DatabaseSession):
    try:
        order_entity = await get_order_or_raise(order_id, db)
        updated = await update_order(order_entity, update_schema, db)
    except OrderNotFoundError:
        raise not_found(order_id) from None
    except CustomerNotFoundForOrderError:
        raise customer_not_found() from None
    return OrderResponse.model_validate(updated)


@router.delete("/delete/{order_id}", response_model=OrderResponse)
async def delete_order_route(order_id: int, db: DatabaseSession):
    try:
        order = await get_order_or_raise(order_id, db)
        deleted = await delete_order(order, db)
    except OrderNotFoundError:
        raise not_found(order_id) from None
    except OrderHasItemsError:
        raise HTTPException(status_code=409, detail="Cannot delete an order that contains order items") from None
    return OrderResponse.model_validate(deleted)
