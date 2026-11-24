from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from e_commerce.Config.setting import setting
from e_commerce.database import model


async def get_customer_id_for_user(user_id: int, db: AsyncSession) -> int:
    customer_id = await db.scalar(
        select(model.UserCustomerLink.customer_id).where(
            model.UserCustomerLink.user_id == user_id
        )
    )
    if customer_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found",
        )
    return customer_id


async def ensure_customer_access(
    customer_id: int,
    user_id: int,
    db: AsyncSession,
) -> None:
    linked_customer_id = await get_customer_id_for_user(user_id, db)
    if linked_customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )


async def ensure_order_access(order_id: int, user_id: int, db: AsyncSession) -> None:
    owned_order_id = await db.scalar(
        select(model.Orders.id)
        .join(
            model.UserCustomerLink,
            model.Orders.customer_id == model.UserCustomerLink.customer_id,
        )
        .where(
            model.Orders.id == order_id,
            model.UserCustomerLink.user_id == user_id,
        )
    )
    if owned_order_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )


def ensure_admin(user_id: int) -> None:
    if user_id not in setting.admin_user_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )
