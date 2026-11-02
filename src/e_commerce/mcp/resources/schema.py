from fastmcp import FastMCP


def register_schema_resource(mcp: FastMCP) -> None:
    @mcp.resource("ecommerce://schema")
    async def ecommerce_schema() -> str:
        """Describe the ecommerce entities exposed by this MCP server."""
        return """Ecommerce entities:
- customer: id, name, email, address
- products: id, name, price, description
- orders: id, customer_id, order_date, total_amount
- order_items: id, order_id, product_id, quantity
Relationships: customer has orders; orders have order_items; products can appear in order_items.
"""
