from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from e_commerce.Services.order_item_services import (
    OrderItemNotFoundError, OrderNotFoundForItemError, ProductNotFoundForItemError,
    create_order_item, delete_order_item, get_order_item_or_raise, update_order_item,
)
from e_commerce.database.session import get_db
from e_commerce.schemas.schema import OrderItemCreate, OrderItemResponse, OrderItemUpdate

router = APIRouter()
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


def not_found(order_item_id: int) -> HTTPException:
    return HTTPException(status_code=404, detail=f"Order item with id {order_item_id} does not exist")


def reference_not_found(error: Exception) -> HTTPException:
    if isinstance(error, OrderNotFoundForItemError):
        return HTTPException(status_code=404, detail="Order Not Found")
    return HTTPException(status_code=404, detail="Product Not Found")


@router.get("/{order_item_id}", response_model=OrderItemResponse)
async def get_order_item(order_item_id: int, db: DatabaseSession):
    try:
        item = await get_order_item_or_raise(order_item_id, db)
    except OrderItemNotFoundError:
        raise not_found(order_item_id) from None
    return OrderItemResponse.model_validate(item)


@router.post("", response_model=OrderItemResponse, status_code=status.HTTP_201_CREATED)
async def add_order_item(order_item: OrderItemCreate, db: DatabaseSession):
    try:
        created = await create_order_item(order_item, db)
    except (OrderNotFoundForItemError, ProductNotFoundForItemError) as error:
        raise reference_not_found(error) from None
    return OrderItemResponse.model_validate(created)


@router.patch("/patch/{order_item_id}", response_model=OrderItemResponse)
async def update_order_item_route(
    order_item_id: int,
    update_schema: OrderItemUpdate,
    db: DatabaseSession,
):
    try:
        item = await get_order_item_or_raise(order_item_id, db)
        updated = await update_order_item(item, update_schema, db)
    except OrderItemNotFoundError:
        raise not_found(order_item_id) from None
    except (OrderNotFoundForItemError, ProductNotFoundForItemError) as error:
        raise reference_not_found(error) from None
    return OrderItemResponse.model_validate(updated)


@router.delete("/delete/{order_item_id}", response_model=OrderItemResponse)
async def delete_order_item_route(order_item_id: int, db: DatabaseSession):
    try:
        item = await get_order_item_or_raise(order_item_id, db)
        deleted = await delete_order_item(item, db)
    except OrderItemNotFoundError:
        raise not_found(order_item_id) from None
    return OrderItemResponse.model_validate(deleted)
