from fastapi import APIRouter , Depends 
from sqlalchemy.ext.asyncio import AsyncSession
from e_commerce.database.session import get_db
from typing import Annotated
from uuid import uuid4

router = APIRouter(tags=["Chat"])


router.post("/chat/{chat_session_id}")
async def new_or_chat(chat_session_id:str,db : Annotated[AsyncSession,Depends(get_db)]):
    #TODO : Validate User

    if chat_session_id is None:
        chat_session_id = str(uuid4())
    

    



