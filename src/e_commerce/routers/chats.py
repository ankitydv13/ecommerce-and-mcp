import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from e_commerce.database.session import get_db
from e_commerce.Services.chat_services import get_chat_content, new_session , get_all_session
from e_commerce.Services.AuthServices import get_current_user


router = APIRouter()
logger = logging.getLogger(__name__)


DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_chat(
    db: DatabaseSession,
    user_id: int = Depends(get_current_user),
):
    chat_session_id = await new_session(user_id, db)
    logger.info("New chat session created for user id=%s", user_id)
    return {"chat_session_id": chat_session_id}


@router.post("/{chat_session_id}")
async def get_chat(
    chat_session_id: UUID,
    db: DatabaseSession,
    user_id: int = Depends(get_current_user),
):
    result = await get_chat_content(str(chat_session_id), db, user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return result

@router.get("",status_code=202)
async def get_all_session(
    db : DatabaseSession,
    user_id : int = Depends(get_current_user)
):
    result = await get_all_session(user_id, db)
    return result

