from __future__ import annotations

from decimal import Decimal
from typing import Any

from fastmcp import Context

from mcp.types import ElicitRequest, ElicitRequestFormParams, InputRequiredResult


def model_dict(entity: Any) -> dict[str, Any]:
    values = {column.name: getattr(entity, column.name) for column in entity.__table__.columns}
    return {
        key: value.isoformat() if hasattr(value, "isoformat") else str(value) if isinstance(value, Decimal) else value
        for key, value in values.items()
    }


def ask_user(query: str, message: str) -> InputRequiredResult:
    params = ElicitRequestFormParams(
        message=f"{message}\n\n{query}",
        requested_schema={
            "type": "object",
            "properties": {
                "confirmed": {
                    "type": "boolean",
                    "title": "Confirm execution",
                }
            },
            "required": ["confirmed"],
        },
    )
    elicitation = ElicitRequest(
        method="elicitation/create",
        params=params,
    )
    return InputRequiredResult(
        result_type="input_required",
        input_requests={"confirm_query": elicitation},
    )


def confirmation_result(
    ctx: Context,
    query: str,
    message: str,
) -> bool | str | InputRequiredResult:
    responses = ctx.input_responses
    if responses is None or "confirm_query" not in responses:
        return ask_user(query, message)

    response = responses["confirm_query"]
    if response.action != "accept":
        return "Query is Cancel by User"

    content = response.content or {}
    if content.get("confirmed", False) is not True:
        return "Query Cancel the query"

    return True
