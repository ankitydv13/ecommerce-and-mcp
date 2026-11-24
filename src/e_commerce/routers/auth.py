from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from e_commerce.database.session import get_db
from e_commerce.schemas.schema import Signup, Token
from e_commerce.Services.AuthServices import authenticate_user, create_access_token
from e_commerce.Services.UserServices import (
    UsernameAlreadyExistsError,
    create_user,
)

router = APIRouter()
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]

@router.post("/token")
async def login_for_access_token(
    db: DatabaseSession,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await authenticate_user(db,form_data.username, form_data.password)
    access_token = create_access_token(user_id=user.id)
    return Token(access_token=access_token, token_type="bearer")

@router.post("/signup")
async def signup(db: DatabaseSession, signup: Signup) -> Token:
    try:
        new_user = await create_user(db, signup)
    except UsernameAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        ) from None

    access_token = create_access_token(user_id=new_user.id)
    return Token(access_token=access_token, token_type="bearer")

    
