from fastapi import FastAPI
from e_commerce.database.database import engine 
from e_commerce.database.database_model import Base
from contextlib import asynccontextmanager

from e_commerce.routers import customer, order, order_item, product

@asynccontextmanager
async def lifespan(app_:FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(customer.router,prefix="/api/customer",tags=["Customer"])
app.include_router(order.router,prefix="/api/order",tags=["Order"])
app.include_router(product.router,prefix="/api/product",tags=["Product"])
app.include_router(order_item.router,prefix="/api/order-item",tags=["Order Item"])
