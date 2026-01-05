"""
Модели товаров MS API
"""

from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from moy_sklad_api.common import ProductType


class ProductMSModel(BaseModel):
    """Модель товара из МойСклад"""
    id: UUID
    name: str
    code: int
    capacity: int = Field(validation_alias="volume")
    type: ProductType = Field(validation_alias="pathName")


class ProductsMSCollection(BaseModel):
    """Коллекция товаров из МойСклад"""
    items: Annotated[list[ProductMSModel], Field(validation_alias="rows")]

