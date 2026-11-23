from typing import Annotated
from fastapi.security import OAuth2PasswordBearer , OAuth2PasswordRequestForm
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pwdlib import PasswordHash
from e_commerce.database import model
from fastapi import HTTPException , status
from datetime import datetime , UTC , timedelta
import jwt

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()

oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")

def get_hash_password(password:str):
    return password_hash.hash(password)

def verify_password(plain_password:str,hash_password:str) -> bool:
    return password_hash.verify(plain_password,hash_password)

async def authenticate_user(db:AsyncSession, username:str, password:str):
    user = await get_user_by_username(db,username)
    hashed_password = user.hash_password
    plain_password = password

    verify = verify_password(plain_password,hashed_password)

    if not verify:
        raise HTTPException(status_code=404,detail="username or password is wrong")
    return user


async def create_access_token(data:dict):
    access_expire_time =  datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()

    to_encode.update({'exp':access_expire_time})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

    return encoded_jwt

async def get_user_by_username(db,username:str):
    result = await db.execute(select(model.User).where(model.User.username==username))
    user = result.scalar_one_or_none()
    # user = await db.get(entity=model.User,ident=username)
    if user is None:
        raise HTTPException(status_code=404,detail="username or password is wrong ")
    return user