from sqlalchemy.ext.asyncio import (
        create_async_engine , 
        AsyncSession , 
        async_sessionmaker)
from sqlalchemy.engine import URL

from sqlalchemy.orm import DeclarativeBase
from e_commerce.Config.setting import setting

engine = create_async_engine(
    url=URL.create(
        drivername="postgresql+asyncpg",
        username=setting.DB_USER,
        password=setting.DB_PASSWORD,
        host=setting.DB_HOST,
        port=setting.DB_PORT,
        database=setting.DB_NAME,
    ),
    echo=True
)

session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


async def get_db():
    async with session() as db:
        yield db
