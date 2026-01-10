"""
Модели складов MS API
"""

from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from moy_sklad_api.models.base_collection import BaseCollection


class WarehouseModel(BaseModel):
    """Модель склада из МойСклад"""
    id: UUID
    name: str
    code: int


class WarehouseCollection(BaseCollection[WarehouseModel]):
    """Коллекция складов из МойСклад"""
    items: Annotated[list[WarehouseModel], Field(validation_alias="rows")]
