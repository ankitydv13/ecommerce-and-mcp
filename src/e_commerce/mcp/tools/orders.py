from fastmcp import FastMCP

from e_commerce.Services.order_services import CustomerNotFoundForOrderError, OrderHasItemsError, OrderNotFoundError, create_order, delete_order, get_order_or_raise, update_order
from e_commerce.database.session import session_factory
from e_commerce.mcp.context import model_dict
from e_commerce.schemas.schema import OrderCreate, OrderUpdate


def register_order_tools(mcp: FastMCP) -> None:
    @mcp.tool
    async def get_order(order_id: int) -> dict:
        """Get one order by ID."""
        async with session_factory() as db:
            try:
                return model_dict(await get_order_or_raise(order_id, db))
            except OrderNotFoundError:
                return {"success": False, "error": "ORDER_NOT_FOUND"}

    @mcp.tool
    async def create_order_tool(customer_id: int, total_amount: float) -> dict:
        """Create an order for an existing customer."""
        async with session_factory() as db:
            try:
                return model_dict(await create_order(OrderCreate(customer_id=customer_id, total_amount=total_amount), db))
            except CustomerNotFoundForOrderError:
                return {"success": False, "error": "CUSTOMER_NOT_FOUND"}

    @mcp.tool
    async def update_order_tool(order_id: int, customer_id: int | None = None, total_amount: float | None = None) -> dict:
        """Update an existing order."""
        async with session_factory() as db:
            try:
                order = await get_order_or_raise(order_id, db)
                return model_dict(await update_order(order, OrderUpdate(customer_id=customer_id, total_amount=total_amount), db))
            except OrderNotFoundError:
                return {"success": False, "error": "ORDER_NOT_FOUND"}
            except CustomerNotFoundForOrderError:
                return {"success": False, "error": "CUSTOMER_NOT_FOUND"}

    @mcp.tool
    async def delete_order_tool(order_id: int, confirmed: bool) -> dict:
        """Delete an order; pass confirmed=true to confirm if it has no order items."""
        if not confirmed:
            return {"success": False, "error": "OPERATION_NOT_CONFIRMED"}
        async with session_factory() as db:
            try:
                order = await get_order_or_raise(order_id, db)
                return model_dict(await delete_order(order, db))
            except OrderNotFoundError:
                return {"success": False, "error": "ORDER_NOT_FOUND"}
            except OrderHasItemsError:
                return {"success": False, "error": "ORDER_HAS_ITEMS"}
