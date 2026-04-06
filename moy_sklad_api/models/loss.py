from datetime import datetime
from typing import Annotated, Any, Callable
from uuid import UUID

from pydantic import BaseModel, Field, BeforeValidator

from moy_sklad_api.models.position import parse_assortment
from moy_sklad_api.models.variant import VariantModel
from moy_sklad_api.models.product import ProductModel
from moy_sklad_api.utils import parse_api_datetime, parse_rows_as, _parse_meta_entity_id


class LossPosition(BaseModel):
    id: UUID
    assortment: Annotated[
        ProductModel | VariantModel,
        Field(validation_alias="assortment"),
        BeforeValidator(parse_assortment),
    ]
    quantity: float
    price: int
    reason: str | None = None


parse_loss_positions: Callable[[Any], list[LossPosition]] = parse_rows_as(LossPosition)


class LossModel(BaseModel):
    model_config = {"populate_by_name": True, "extra": "ignore"}

    id: UUID
    name: str
    external_code: Annotated[str, Field(validation_alias="externalCode")]
    total_sum: Annotated[int, Field(validation_alias="sum")]
    timestamp: Annotated[datetime, Field(validation_alias="moment"), BeforeValidator(parse_api_datetime)]
    positions: Annotated[list[LossPosition], BeforeValidator(parse_loss_positions)]

    warehouse_id: Annotated[
        UUID,
        Field(validation_alias="store"),
        BeforeValidator(_parse_meta_entity_id),
    ]
