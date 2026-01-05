from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from moy_sklad_api.common import BundleType


class BundleModel(BaseModel):
    """Модель комплекта из МойСклад"""
    id: UUID
    name: str
    code: int
    type: BundleType = Field(validation_alias="pathName")


class BundlesCollection(BaseModel):
    """Коллекция комплектов из МойСклад"""
    items: Annotated[list[BundleModel], Field(validation_alias="rows")]
