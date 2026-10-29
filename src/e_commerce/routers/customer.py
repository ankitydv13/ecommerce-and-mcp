from fastapi import APIRouter , HTTPException , status , Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from e_commerce.database.database import get_db
from e_commerce.schemas.schema import( Customer,
                                    CustomerUpdate)
from e_commerce.database import database_model
from sqlalchemy import select
router = APIRouter()


@router.get("/{customer_id}",status_code = 200)
async def get_customer(customer_id:int , db:Annotated[AsyncSession,Depends(get_db)] ):
    result = await db.execute(select(database_model.Customer).where(database_model.Customer.id == customer_id))
    exiting_user = result.scalars().first()
    if not exiting_user:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND , detail = "User Not Found")
    return Customer.model_validate(exiting_user)


@router.post("",status_code=status.HTTP_201_CREATED)
async def add_customer(customer : Customer ,db : Annotated[AsyncSession,Depends(get_db)]):
    new_customer = database_model.Customer( name = customer.name, 
                                        email = customer.email, 
                                        address= customer.address )
    db.add(new_customer)
    await db.commit()

    db.refresh(new_customer)
    return Customer.model_validate(new_customer)

@router.patch("/patch/{customer_id}",response_model=Customer)
async def add_updates(customer_id :int ,update_schema : CustomerUpdate , db : Annotated[AsyncSession,Depends(get_db)]):
    result = await db.execute(select(database_model.Customer).where(database_model.Customer.id == customer_id))
    existing_cus = result.scalars().first()

    if not existing_cus:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,details=f"Customer with id {customer_id} not exits")

    if update_schema.email is not None and update_schema.email != existing_cus.email:
        existing_cus.email = update_schema.email
        print(
            "new email added"
        )
    
    if update_schema.address is not None and update_schema.address != existing_cus.address:
        existing_cus.address = update_schema.address

    await db.commit()
    await db.refresh(existing_cus)

    

    return Customer.model_validate(existing_cus)



@router.delete("/delete/{customer_id}" , response_model=Customer)
async def delete_customer(customer_id:int,db:Annotated[AsyncSession,Depends(get_db)]):
    result = await db.execute(select(database_model.Customer).where(database_model.Customer.id==customer_id))
    existing_cus = result.scalars().first()

    if not existing_cus:
        raise HTTPException(status_code=404 , detail = "No user exits")

    db.delete(existing_cus)
    await db.commit()
    return Customer.model_validate(existing_cus)
