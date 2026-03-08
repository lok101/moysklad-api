from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, BeforeValidator

from moy_sklad_api.utils import extract_id


class ProductExpandStocksModel(BaseModel):
    product_id: Annotated[UUID, Field(validation_alias="meta"), BeforeValidator(extract_id)]
    quantity: Annotated[float, Field(validation_alias="stock")]
