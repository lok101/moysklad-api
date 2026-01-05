"""
Модели остатков товаров MS API
"""

from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, BeforeValidator


def extract_id(data: dict):
    """Извлечь ID из метаданных"""
    if not isinstance(data, dict) or "href" not in data:
        raise ValueError("Метаданные должны содержать ключ 'href'")
    href = data["href"]
    entity = href.split("/")[-1]
    entity_without_filter = entity.split("?")[0]
    return entity_without_filter


class ProductStocksMSModel(BaseModel):
    """Модель остатков товара из МойСклад"""
    product_id: Annotated[UUID, Field(validation_alias="assortmentId")]
    quantity: Annotated[float, Field(validation_alias="stock")]


class ProductStocksMSCollection(BaseModel):
    """Коллекция остатков товаров из МойСклад"""
    items: Annotated[list[ProductStocksMSModel], Field(validation_alias="rows")]


class ProductExpandStocksMSModel(BaseModel):
    """Модель остатков товара с расширенными метаданными"""
    product_id: Annotated[UUID, Field(validation_alias="meta"), BeforeValidator(extract_id)]
    quantity: Annotated[float, Field(validation_alias="stock")]


class ProductExpandStocksMSCollection(BaseModel):
    """Коллекция остатков товаров с расширенными метаданными"""
    items: Annotated[list[ProductExpandStocksMSModel], Field(validation_alias="rows")]

