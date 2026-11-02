from fastmcp import Context, FastMCP

from e_commerce.Services.order_services import CustomerNotFoundForOrderError, OrderHasItemsError, OrderNotFoundError, create_order, delete_order, get_order_or_raise, update_order
from e_commerce.database.session import session_factory
from e_commerce.mcp.context import confirmation_result, model_dict
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
    async def delete_order_tool(order_id: int, ctx: Context):
        """Ask for confirmation before deleting an order."""
        confirmation = confirmation_result(
            ctx,
            f"order_id: {order_id}",
            "Do you want to delete this order?",
        )
        if confirmation is not True:
            return confirmation

        async with session_factory() as db:
            try:
                order = await get_order_or_raise(order_id, db)
                return model_dict(await delete_order(order, db))
            except OrderNotFoundError:
                return {"success": False, "error": "ORDER_NOT_FOUND"}
            except OrderHasItemsError:
                return {"success": False, "error": "ORDER_HAS_ITEMS"}
