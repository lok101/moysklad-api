"""
Модели остатков товаров MS API
"""

from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, BeforeValidator

from moy_sklad_api.models.base_collection import BaseCollection


class ProductStocksModel(BaseModel):
    """Модель остатков товара из МойСклад"""
    product_id: Annotated[UUID, Field(validation_alias="assortmentId")]
    quantity: Annotated[float, Field(validation_alias="stock")]


class ProductStockSCollection(BaseCollection[ProductStocksModel]):
    """Коллекция остатков товаров из МойСклад"""
    items: Annotated[list[ProductStocksModel], Field(validation_alias="rows")]
