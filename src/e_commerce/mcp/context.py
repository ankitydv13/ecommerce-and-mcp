from __future__ import annotations

from decimal import Decimal
from typing import Any

def model_dict(entity: Any) -> dict[str, Any]:
    values = {column.name: getattr(entity, column.name) for column in entity.__table__.columns}
    return {
        key: value.isoformat() if hasattr(value, "isoformat") else str(value) if isinstance(value, Decimal) else value
        for key, value in values.items()
    }
