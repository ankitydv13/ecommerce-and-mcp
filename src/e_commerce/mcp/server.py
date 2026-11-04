import logging

from fastmcp import FastMCP

from e_commerce.mcp.resources.schema import register_schema_resource
from e_commerce.mcp.tools.customers import register_customer_tools
from e_commerce.mcp.tools.order_items import register_order_item_tools
from e_commerce.mcp.tools.orders import register_order_tools
from e_commerce.mcp.tools.products import register_product_tools

from fastmcp.resources import FileResource
from pathlib import Path

file_path = Path(r"D:\ecommerce\src\e_commerce\mcp\model.txt").resolve()


mcp = FastMCP(
    "ecommerce-mcp",
    instructions="Use the ecommerce tools to manage customers, products, orders, and order items.",
)

register_customer_tools(mcp)
register_product_tools(mcp)
register_order_tools(mcp)
register_order_item_tools(mcp)
register_schema_resource(mcp)

if file_path.exists:
            model_resource= FileResource(
                uri=f"file://{file_path.as_posix()}",
                path = file_path,
                name = "Model File",
                description = "This file tell the database model",
                mime_type = "text",
                tag = {"model document"}
            )
        mcp.add_resource(model_resource)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    mcp.run(transport="http", host="127.0.0.1", port=8001)


if __name__ == "__main__":
    main()
