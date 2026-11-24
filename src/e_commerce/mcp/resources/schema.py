from fastmcp import FastMCP
from pathlib import Path
from fastmcp.resources import FileResource
from e_commerce.database.engine import engine
import json
from sqlalchemy import inspect
from e_commerce.database.model import Base

inspector = inspect(engine)

file_path = Path(r"D:\ecommerce\src\e_commerce\mcp\model.txt").resolve()

def register_schema_resource(mcp: FastMCP) -> None:
    @mcp.resource("ecommerce://schema")
    async def ecommerce_schema() -> str:
        schema_info = []
        for table in inspector.get_table_names(schema="public"):
            schema_info.append({
                "table_name": table,
                "columns": inspector.get_columns(
                    table_name=table,
                    schema="public"
                ),
                "primary_key": inspector.get_pk_constraint(
                    table_name=table,
                    schema="public"
                ),
                "foreign_keys": inspector.get_foreign_keys(
                    table_name=table,
                    schema="public"
                )
            })

        relationships = []
        for mapper in Base.registry.mappers:
            for rel in mapper.relationships:
                relationships.append(
                    {
                        "source_entity": mapper.class_.__name__,
                        "relationship_name": rel.key,
                        "target_entity": rel.mapper.class_.__name__,
                        "direction": str(rel.direction)
                    }
                )


        return json.dumps({
            "tables":schema_info,
            "relationships" :relationships
        }, indent=2, default=str)