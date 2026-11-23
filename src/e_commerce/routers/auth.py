from fastapi import APIRouter , Depends , HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from e_commerce.schemas.schema import Token , Signup
from e_commerce.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from e_commerce.Services.AuthServices import authenticate_user , create_access_token
from datetime import UTC , datetime , timedelta
from e_commerce.Services.UserServices import create_user

router = APIRouter()
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]

@router.post("/token")
async def login_for_access_token(db:DatabaseSession,form_data : Annotated[OAuth2PasswordRequestForm,Depends()])->Token:
    user = await authenticate_user(db,form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect user named or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = await create_access_token(data= {"sub":user.username})
    return Token(access_token=access_token,token_type="bearer")

@router.post("/signup")
async def signup(db: DatabaseSession ,signup:Signup):
    new_username = await create_user(db,signup)
    access_token = await create_access_token(data= {"sub":new_username})
    return Token(access_token=access_token,token_type="bearer")

    
