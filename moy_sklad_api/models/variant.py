from uuid import UUID

from pydantic import BaseModel, Field

from moy_sklad_api.models.product import ProductModel
from moy_sklad_api.models.metadata import MetaModel


class VariantModel(BaseModel):
    id: UUID
    name: str
    code: int | None = None
    external_code: str | None = Field(default=None, validation_alias="externalCode")
    archived: bool
    product: ProductModel
    meta: MetaModel

    model_config = {"populate_by_name": True, "extra": "ignore"}
