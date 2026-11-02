from fastmcp import FastMCP

from e_commerce.Services.order_item_services import OrderItemNotFoundError, OrderNotFoundForItemError, ProductNotFoundForItemError, create_order_item, delete_order_item, get_order_item_or_raise, update_order_item
from e_commerce.database.session import session_factory
from e_commerce.mcp.context import model_dict
from e_commerce.schemas.schema import OrderItemCreate, OrderItemUpdate


def register_order_item_tools(mcp: FastMCP) -> None:
    @mcp.tool
    async def get_order_item(order_item_id: int) -> dict:
        """Get one order item by ID."""
        async with session_factory() as db:
            try:
                return model_dict(await get_order_item_or_raise(order_item_id, db))
            except OrderItemNotFoundError:
                return {"success": False, "error": "ORDER_ITEM_NOT_FOUND"}

    @mcp.tool
    async def create_order_item_tool(order_id: int, product_id: int, quantity: int = 1) -> dict:
        """Create an order item after validating its references."""
        async with session_factory() as db:
            try:
                return model_dict(await create_order_item(OrderItemCreate(order_id=order_id, product_id=product_id, quantity=quantity), db))
            except OrderNotFoundForItemError:
                return {"success": False, "error": "ORDER_NOT_FOUND"}
            except ProductNotFoundForItemError:
                return {"success": False, "error": "PRODUCT_NOT_FOUND"}

    @mcp.tool
    async def update_order_item_tool(order_item_id: int, order_id: int | None = None, product_id: int | None = None, quantity: int | None = None) -> dict:
        """Update an order item after validating its references."""
        async with session_factory() as db:
            try:
                item = await get_order_item_or_raise(order_item_id, db)
                return model_dict(await update_order_item(item, OrderItemUpdate(order_id=order_id, product_id=product_id, quantity=quantity), db))
            except OrderItemNotFoundError:
                return {"success": False, "error": "ORDER_ITEM_NOT_FOUND"}
            except OrderNotFoundForItemError:
                return {"success": False, "error": "ORDER_NOT_FOUND"}
            except ProductNotFoundForItemError:
                return {"success": False, "error": "PRODUCT_NOT_FOUND"}

    @mcp.tool
    async def delete_order_item_tool(order_item_id: int, confirmed: bool) -> dict:
        """Delete an order item; pass confirmed=true to confirm."""
        if not confirmed:
            return {"success": False, "error": "OPERATION_NOT_CONFIRMED"}
        async with session_factory() as db:
            try:
                item = await get_order_item_or_raise(order_item_id, db)
                return model_dict(await delete_order_item(item, db))
            except OrderItemNotFoundError:
                return {"success": False, "error": "ORDER_ITEM_NOT_FOUND"}
