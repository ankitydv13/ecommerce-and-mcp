from fastapi import APIRouter , Depends 
from sqlalchemy.ext.asyncio import AsyncSession
from e_commerce.database.session import get_db
from typing import Annotated
from src.e_commerce.Services.chat_services  import new_session , get_chat_content
import e_commerce.database.model as model
from src.e_commerce.app import logger

router = APIRouter(tags=["Chat"])


router.post("/chat/{chat_session_id}")
async def new_or_chat(chat_session_id:str,db : Annotated[AsyncSession,Depends(get_db)]):
    #TODO : Validate User
    user_id = 1
    if chat_session_id is None:
        chat_session_id = new_session(user_id,db)
        logger.info(f"New chat session created with id: {chat_session_id}")
        return {"chat_session_id":chat_session_id}

    # Getting all results
    result = get_chat_content(chat_session_id,db)
    if result is None:
        return {"error":"Chat session not found"}
    return result


    

    



