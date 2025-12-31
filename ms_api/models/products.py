"""
Модели товаров MS API
"""

from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from ms_api.common import MSProductType


class ProductMSModel(BaseModel):
    """Модель товара из МойСклад"""
    id: UUID
    name: str
    code: int
    capacity: int = Field(validation_alias="volume")
    type: MSProductType = Field(validation_alias="pathName")


class ProductsMSCollection(BaseModel):
    """Коллекция товаров из МойСклад"""
    items: Annotated[list[ProductMSModel], Field(validation_alias="rows")]

