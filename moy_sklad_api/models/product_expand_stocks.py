from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, BeforeValidator

from moy_sklad_api.models.base_collection import BaseCollection
from moy_sklad_api.utils import extract_id


class ProductExpandStocksModel(BaseModel):
    """Модель остатков товара с расширенными метаданными"""
    product_id: Annotated[UUID, Field(validation_alias="meta"), BeforeValidator(extract_id)]
    quantity: Annotated[float, Field(validation_alias="stock")]


class ProductExpandStocksCollection(BaseCollection[ProductExpandStocksModel]):
    """Коллекция остатков товаров с расширенными метаданными"""
    items: Annotated[list[ProductExpandStocksModel], Field(validation_alias="rows")]
