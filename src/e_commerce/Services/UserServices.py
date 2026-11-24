
import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from e_commerce.database import model
from e_commerce.schemas.schema import Signup
from e_commerce.Services.AuthServices import get_hash_password

logger = logging.getLogger(__name__)


class UsernameAlreadyExistsError(Exception):
    pass


async def create_user(db: AsyncSession, signup: Signup) -> model.User:
    existing_user = await db.scalar(
        select(model.User).where(model.User.username == signup.username)
    )
    if existing_user is not None:
        raise UsernameAlreadyExistsError(signup.username)

    user_data = signup.model_dump()
    user_data["hash_password"] = get_hash_password(user_data["hash_password"])
    new_user = model.User(**user_data)
    db.add(new_user)

    try:
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except IntegrityError:
        await db.rollback()
        logger.info("Signup conflict for username=%s", signup.username)
        raise UsernameAlreadyExistsError(signup.username) from None
    except Exception:
        await db.rollback()
        logger.exception("Failed to create user")
        raise