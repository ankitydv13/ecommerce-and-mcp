from fastmcp import FastMCP

from e_commerce.Services.product_services import ProductHasOrderItemsError, ProductNotFoundError, create_product, delete_product, get_product_or_raise, update_product
from e_commerce.database.session import session_factory
from e_commerce.mcp.context import model_dict
from e_commerce.schemas.schema import ProductCreate, ProductUpdate


def register_product_tools(mcp: FastMCP) -> None:
    @mcp.tool
    async def get_product(product_id: int) -> dict:
        """Get one product by ID."""
        async with session_factory() as db:
            try:
                return model_dict(await get_product_or_raise(product_id, db))
            except ProductNotFoundError:
                return {"success": False, "error": "PRODUCT_NOT_FOUND"}

    @mcp.tool
    async def create_product_tool(name: str, price: float, description: str) -> dict:
        """Create a product."""
        async with session_factory() as db:
            return model_dict(await create_product(ProductCreate(name=name, price=price, description=description), db))

    @mcp.tool
    async def update_product_tool(product_id: int, name: str | None = None, price: float | None = None, description: str | None = None) -> dict:
        """Update an existing product."""
        async with session_factory() as db:
            try:
                product = await get_product_or_raise(product_id, db)
                return model_dict(await update_product(product, ProductUpdate(name=name, price=price, description=description), db))
            except ProductNotFoundError:
                return {"success": False, "error": "PRODUCT_NOT_FOUND"}

    @mcp.tool
    async def delete_product_tool(product_id: int, confirmed: bool) -> dict:
        """Delete a product; pass confirmed=true to confirm if it has no order items."""
        if not confirmed:
            return {"success": False, "error": "OPERATION_NOT_CONFIRMED"}
        async with session_factory() as db:
            try:
                product = await get_product_or_raise(product_id, db)
                return model_dict(await delete_product(product, db))
            except ProductNotFoundError:
                return {"success": False, "error": "PRODUCT_NOT_FOUND"}
            except ProductHasOrderItemsError:
                return {"success": False, "error": "PRODUCT_HAS_ORDER_ITEMS"}
