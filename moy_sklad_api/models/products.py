"""
Модели товаров MS API
"""

from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from moy_sklad_api.models.base_collection import BaseCollection


class ProductModel(BaseModel):
    """Модель товара из МойСклад"""
    id: UUID
    name: str
    code: int
    capacity: int = Field(validation_alias="volume")
    type: str = Field(validation_alias="pathName")


class ProductsCollection(BaseCollection[ProductModel]):
    """Коллекция товаров из МойСклад"""
    items: Annotated[list[ProductModel], Field(validation_alias="rows")]
