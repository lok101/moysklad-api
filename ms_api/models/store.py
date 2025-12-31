"""
Модели складов MS API
"""

from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class StoreModel(BaseModel):
    """Модель склада из МойСклад"""
    id: UUID
    name: str
    code: int


class StoresCollection(BaseModel):
    """Коллекция складов из МойСклад"""
    items: Annotated[list[StoreModel], Field(validation_alias="rows")]

