from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from pydantic import BaseModel, Field, BeforeValidator

from moy_sklad_api.models.position import PositionModel, parse_positions
from moy_sklad_api.utils import extract_id, parse_api_datetime


def _parse_store_id(value: Any) -> str:
    if not isinstance(value, dict):
        raise TypeError("store must be an object")

    meta = value.get("meta")

    if not isinstance(meta, dict):
        raise TypeError("store.meta must be an object")

    return extract_id(meta)


# def _parse_positions(value: Any) -> dict[str, int | float]:
#     if value is None:
#         return {}
#
#     if isinstance(value, dict):
#         value = value.get("rows", [])
#
#     if not isinstance(value, list):
#         raise TypeError("positions must be a list (or object with 'rows')")
#
#     result: dict[str, int | float] = {}
#
#     for item in value:
#         if not isinstance(item, dict):
#             continue
#
#         quantity = item.get("quantity")
#
#         if quantity is None:
#             continue
#
#         assortment = item.get("assortment") or {}
#         meta = assortment.get("meta") if isinstance(assortment, dict) else None
#
#         if not isinstance(meta, dict):
#             continue
#
#         product_id = extract_id(meta)
#         result[product_id] = quantity
#
#     return result
#

class MoveModel(BaseModel):
    model_config = {"populate_by_name": True, "extra": "ignore"}

    id: UUID

    source_warehouse_id: Annotated[
        UUID,
        Field(validation_alias="sourceStore"),
        BeforeValidator(_parse_store_id),
    ]
    target_warehouse_id: Annotated[
        UUID,
        Field(validation_alias="targetStore"),
        BeforeValidator(_parse_store_id),
    ]

    timestamp: Annotated[datetime, Field(validation_alias="moment"), BeforeValidator(parse_api_datetime)]

    positions: Annotated[
        list[PositionModel],
        BeforeValidator(parse_positions),
    ] = Field(default_factory=list)
