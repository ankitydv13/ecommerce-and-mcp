import uuid
from src.e_commerce.database  import model
from typing import Annotated

async def new_session(user_id:int,db):
    chat_session_id = str(uuid.uuid4())
    
    #TODO: Generate the title of the chat on first query of the user 
    title = "new_chat"
    chat_session = model.ChatSession(
        user_id = user_id,
        title  =title,
        session_id = chat_session_id
    )
    await  db.add(chat_session)
    await db.commit()
    await db.refresh()

    return chat_session_id

async def get_chat_content(session_id:str,db):
    chat_session = await db.get(model.ChatSession,session_id)
    if chat_session is None:
        return None
    messages = chat_session.messages
    result = [
        {
            "message_id": message.messages_id,
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at
        }
        for message in messages
    ]
    return result