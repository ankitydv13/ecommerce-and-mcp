
from e_commerce.schemas.schema import Signup
from e_commerce.database import model
from e_commerce.Services.AuthServices import get_hash_password , get_user_by_username
async def create_user(db,signup:Signup):

    await get_user_by_username(db,signup.username)

    hashed_password = get_hash_password(signup.hash_password)
    signup.hash_password = hashed_password
    
    new_user = model.User(**signup.model_dump())
    db.add(new_user)

    try:
        await db.commit()
        await db.refresh(new_user)
        return new_user.username
    except Exception:
        await db.rollback()
        print(Exception)
        raise
    