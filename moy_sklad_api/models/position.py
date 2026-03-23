from typing import Any, Annotated
from uuid import UUID

from pydantic import BaseModel, Field, BeforeValidator

from moy_sklad_api.models.variant import VariantModel
from moy_sklad_api.models.product import ProductModel


def _parse_assortment(data: dict[str, Any]) -> ProductModel | VariantModel:
    meta = data.get("meta") or {}
    entity_type = meta.get("type", "") if isinstance(meta, dict) else ""

    if entity_type == "product":
        return ProductModel.model_validate(data)
    if entity_type == "variant":
        return VariantModel.model_validate(data)

    raise ValueError(
        f"Неизвестный тип assortment: '{entity_type}'. Ожидается 'product' или 'variant'."
    )


class PositionModel(BaseModel):
    id: UUID
    quantity: float
    assortment: Annotated[
        ProductModel | VariantModel,
        Field(validation_alias="assortment"),
        BeforeValidator(_parse_assortment),
    ]

    model_config = {"populate_by_name": True}


def parse_positions(value: dict) -> list[PositionModel]:
    if value is None:
        return []

    if isinstance(value, dict):
        rows = value.get("rows", [])

        if isinstance(rows, list):
            positions = [PositionModel.model_validate(item) for item in rows]
            return positions

    return []
