from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from e_commerce.Config.setting import setting


database_url = URL.create(
    drivername="postgresql+asyncpg",
    username=setting.DB_USER,
    password=setting.DB_PASSWORD,
    host=setting.DB_HOST,
    port=setting.DB_PORT,
    database=setting.DB_NAME,
)


engine: AsyncEngine = create_async_engine(
    database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
    pool_timeout=30,
    pool_recycle=1800,
    connect_args={
        "command_timeout": 30,
    },
)