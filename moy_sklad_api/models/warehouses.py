"""
Модели складов MS API
"""

from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class WarehouseModel(BaseModel):
    """Модель склада из МойСклад"""
    id: UUID
    name: str
    code: int


class WarehouseCollection(BaseModel):
    """Коллекция складов из МойСклад"""
    items: Annotated[list[WarehouseModel], Field(validation_alias="rows")]

    def get_all(self) -> list[WarehouseModel]:
        return self.items.copy()
