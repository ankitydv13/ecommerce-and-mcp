from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from e_commerce.Config.setting import setting
from e_commerce.database import model
from e_commerce.database.session import get_db

password_hash = PasswordHash.recommended()

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/auth/token")
dummy_password_hash = password_hash.hash("invalid-login-placeholder")

def get_hash_password(password:str):
    return password_hash.hash(password)

def verify_password(plain_password:str,hash_password:str) -> bool:
    return password_hash.verify(plain_password,hash_password)

async def authenticate_user(db:AsyncSession, username:str, password:str):
    user = await get_user_by_username(db, username)
    hashed_password = user.hash_password if user is not None else dummy_password_hash
    password_is_valid = verify_password(password, hashed_password)

    if user is None or not password_is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def create_access_token(user_id: int, expires_minutes: int = 30) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
        "iss": setting.jwt_issuer,
        "aud": setting.jwt_audience,
    }

    return jwt.encode(
        payload,
        setting.jwt_secret_key,
        algorithm=setting.jwt_algorithm,
    )


async def get_current_user(
    token: str = Depends(oauth2_schema),
    db: AsyncSession = Depends(get_db),
) -> int:
    try:
        payload = jwt.decode(
            token,
            setting.jwt_secret_key,
            algorithms=[setting.jwt_algorithm],
            audience=setting.jwt_audience,
            issuer=setting.jwt_issuer,
            options={"require": ["sub", "exp", "iat", "iss", "aud"]},
        )
        user_id = int(payload["sub"])
        if user_id <= 0 or await db.get(model.User, user_id) is None:
            raise jwt.InvalidTokenError("Unknown user")
        return user_id
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_user_by_username(db: AsyncSession, username: str) -> model.User | None:
    result = await db.execute(
        select(model.User).where(model.User.username == username)
    )
    user = result.scalar_one_or_none()
    return user