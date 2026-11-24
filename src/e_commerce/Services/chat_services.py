import uuid
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from e_commerce.database import model


async def new_session(user_id: int, db) -> str:
    chat_session_id = uuid.uuid4()
    
    #TODO: Generate the title of the chat on first query of the user 
    title = "new_chat"
    chat_session = model.ChatSession(
        user_id = user_id,
        title  =title,
        session_id = chat_session_id
    )
    db.add(chat_session)
    await db.commit()
    await db.refresh(chat_session)

    return str(chat_session_id)


async def get_chat_content(session_id: str, db, user_id: int):
    result = await db.execute(
        select(model.ChatSession)
        .options(selectinload(model.ChatSession.messages))
        .where(
            model.ChatSession.user_id == user_id,
            model.ChatSession.session_id == uuid.UUID(session_id),
        )
    )
    chat_session = result.scalar_one_or_none()

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

async def get_all_session(user_id:int, db):
    result = await db.execute(
        select(model.ChatSession)
        .where(model.ChatSession.user_id == user_id)
    )
    chat_sessions = result.scalars().all()
    return [
        {
            "session_id": session.session_id,
            "title": session.title,
            "created_at": session.created_at
        }
        for session in chat_sessions
    ]