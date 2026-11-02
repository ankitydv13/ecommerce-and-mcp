from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from e_commerce.Services.customer_services import (
    CustomerHasOrdersError,
    CustomerNotFoundError,
    create_customer,
    delete_customer,
    get_customer_or_raise,
    update_customer,
)
from e_commerce.database.session import get_db
from e_commerce.schemas.schema import Customer, CustomerUpdate

router = APIRouter()
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


def customer_not_found(customer_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Customer with id {customer_id} does not exist",
    )


@router.get("/{customer_id}", response_model=Customer)
async def get_customer(customer_id: int, db: DatabaseSession):
    try:
        customer = await get_customer_or_raise(customer_id, db)
    except CustomerNotFoundError:
        raise customer_not_found(customer_id) from None
    return Customer.model_validate(customer)


@router.post("", response_model=Customer, status_code=status.HTTP_201_CREATED)
async def add_customer(customer: Customer, db: DatabaseSession):
    try:
        created_customer = await create_customer(customer, db)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A customer with this email already exists",
        ) from None
    return Customer.model_validate(created_customer)


@router.patch("/patch/{customer_id}", response_model=Customer)
async def update_customer_route(
    customer_id: int,
    update_schema: CustomerUpdate,
    db: DatabaseSession,
):
    try:
        customer = await get_customer_or_raise(customer_id, db)
        updated_customer = await update_customer(customer, update_schema, db)
    except CustomerNotFoundError:
        raise customer_not_found(customer_id) from None
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A customer with this email already exists",
        ) from None
    return Customer.model_validate(updated_customer)


@router.delete("/delete/{customer_id}", response_model=Customer)
async def delete_customer_route(customer_id: int, db: DatabaseSession):
    try:
        customer = await get_customer_or_raise(customer_id, db)
        deleted_customer = await delete_customer(customer, db)
    except CustomerNotFoundError:
        raise customer_not_found(customer_id) from None
    except CustomerHasOrdersError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a customer that has orders",
        ) from None
    return Customer.model_validate(deleted_customer)
