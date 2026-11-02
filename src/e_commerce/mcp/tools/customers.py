from fastmcp import FastMCP , Context

from e_commerce.Services.customer_services import CustomerHasOrdersError, CustomerNotFoundError, create_customer, delete_customer, get_customer_or_raise, update_customer
from e_commerce.database.session import session_factory
from e_commerce.mcp.context import model_dict
from e_commerce.schemas.schema import Customer, CustomerUpdate
from e_commerce.app import logger
from e_commerce.mcp.server import ask_user 

def register_customer_tools(mcp: FastMCP) -> None:
    @mcp.tool
    async def get_customer(customer_id: int) -> dict:
        """Get one customer by ID."""
        async with session_factory() as db:
            try:
                return model_dict(await get_customer_or_raise(customer_id, db))
            except CustomerNotFoundError:
                return {"success": False, "error": "CUSTOMER_NOT_FOUND"}

    @mcp.tool
    async def create_customer_tool(name: str, email: str, address: str) -> dict:
        """Create a customer."""
        async with session_factory() as db:
            return model_dict(await create_customer(Customer(name=name, email=email, address=address), db))

    @mcp.tool
    async def update_customer_tool(customer_id: int, name: str | None = None, email: str | None = None, address: str | None = None) -> dict:
        """Update an existing customer."""
        async with session_factory() as db:
            try:
                customer = await get_customer_or_raise(customer_id, db)
                return model_dict(await update_customer(customer, CustomerUpdate(name=name, email=email, address=address), db))
            except CustomerNotFoundError:
                return {"success": False, "error": "CUSTOMER_NOT_FOUND"}

    @mcp.tool
    async def delete_customer_tool(customer_id: int, ctx: Context):
        """Delete a customer; pass confirmed=true to confirm. Customers with orders cannot be deleted."""
        logger.info("select_query called")
        responses = ctx.input_responses

        if responses is None or "confirm_query" not in responses:
            return ask_user(customer_id, "Do you want to delete the customer with id  ?")

        response = responses["confirm_query"]
        if response.action != "accept":
            return "Query is Cancel by User"

        content = response.content or {}
        if content.get("confirmed", False) is not True:
            logger.info("User Does not confirmed query")
            return "Query Cancel the query"
        async with session_factory() as db:
            try:
                customer = await get_customer_or_raise(customer_id, db)
                return model_dict(await delete_customer(customer, db))
            except CustomerNotFoundError:
                return {"success": False, "error": "CUSTOMER_NOT_FOUND"}
            except CustomerHasOrdersError:
                return {"success": False, "error": "CUSTOMER_HAS_ORDERS"}
