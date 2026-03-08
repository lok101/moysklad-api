from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID

from pydantic import BaseModel, Field, BeforeValidator

from moy_sklad_api.models.product import ProductModel
from moy_sklad_api.models.variant import VariantModel


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


class BundleComponentModel(BaseModel):
    id: UUID
    quantity: float
    assortment: Annotated[
        ProductModel | VariantModel,
        Field(validation_alias="assortment"),
        BeforeValidator(_parse_assortment),
    ]

    model_config = {"populate_by_name": True}


def _parse_components(value: dict) -> list[BundleComponentModel]:
    """Парсит components: поддерживает список или объект с полем rows."""
    if value is None:
        return []

    if isinstance(value, dict):
        rows = value.get("rows", [])

        if isinstance(rows, list):
            return [BundleComponentModel.model_validate(item) for item in rows]

    return []


class BundleModel(BaseModel):
    id: UUID
    name: str
    code: str = ""
    components: Annotated[
        list[BundleComponentModel],
        BeforeValidator(_parse_components),
    ] = Field(default_factory=list)

    model_config = {"populate_by_name": True, "extra": "ignore"}
