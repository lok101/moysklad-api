from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class ProductStocksModel(BaseModel):
    product_id: Annotated[UUID, Field(validation_alias="assortmentId")]
    quantity: Annotated[float, Field(validation_alias="stock")]
