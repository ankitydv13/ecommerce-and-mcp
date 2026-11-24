from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from e_commerce.Services.AuthServices import get_current_user
from e_commerce.Services.authorization_services import ensure_admin, ensure_customer_access
from e_commerce.Services.customer_services import (
    CustomerAlreadyLinkedError,
    CustomerHasOrdersError,
    CustomerNotFoundError,
    LinkedUserNotFoundError,
    create_customer_profile,
    delete_customer,
    get_customer_or_raise,
    link_customer_to_user,
    update_customer,
)
from e_commerce.database.session import get_db
from e_commerce.schemas.schema import Customer, CustomerResponse, CustomerUpdate

router = APIRouter()
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


def customer_not_found(customer_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Customer with id {customer_id} does not exist",
    )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: DatabaseSession,
    user_id: int = Depends(get_current_user),
):
    await ensure_customer_access(customer_id, user_id, db)
    try:
        customer = await get_customer_or_raise(customer_id, db)
    except CustomerNotFoundError:
        raise customer_not_found(customer_id) from None
    return CustomerResponse.model_validate(customer)

@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def add_customer(
    customer: Customer,
    db: DatabaseSession,
    user_id: int = Depends(get_current_user),
):
    try:
        created_customer = await create_customer_profile(customer, user_id, db)
    except CustomerAlreadyLinkedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A customer profile is already linked to this account",
        ) from None
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A customer with this email already exists",
        ) from None
    return CustomerResponse.model_validate(created_customer)

@router.patch("/patch/{customer_id}", response_model=CustomerResponse)
async def update_customer_route(
    customer_id: int,
    update_schema: CustomerUpdate,
    db: DatabaseSession,
    user_id: int = Depends(get_current_user),
):
    await ensure_customer_access(customer_id, user_id, db)
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
    return CustomerResponse.model_validate(updated_customer)

@router.delete("/delete/{customer_id}", response_model=CustomerResponse)
async def delete_customer_route(
    customer_id: int,
    db: DatabaseSession,
    user_id: int = Depends(get_current_user),
):
    await ensure_customer_access(customer_id, user_id, db)
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
    return CustomerResponse.model_validate(deleted_customer)


@router.put("/link/{user_id}/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def link_existing_customer(
    user_id: int,
    customer_id: int,
    db: DatabaseSession,
    admin_user_id: int = Depends(get_current_user),
):
    ensure_admin(admin_user_id)
    try:
        await link_customer_to_user(customer_id, user_id, db)
    except CustomerNotFoundError:
        raise customer_not_found(customer_id) from None
    except LinkedUserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} does not exist",
        ) from None
    except CustomerAlreadyLinkedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user already has a customer profile",
        ) from None
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The customer is already linked to another account",
        ) from None
