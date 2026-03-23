from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID

from pydantic import BaseModel, Field, BeforeValidator

from moy_sklad_api.models.position import PositionModel, parse_positions


class BundleModel(BaseModel):
    id: UUID
    name: str
    code: str | None = None
    volume: int
    components: Annotated[
        list[PositionModel],
        BeforeValidator(parse_positions),
    ] = Field(default_factory=list)

    model_config = {"populate_by_name": True, "extra": "ignore"}
