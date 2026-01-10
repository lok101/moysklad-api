from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from moy_sklad_api.models.base_collection import BaseCollection


class BundleModel(BaseModel):
    """Модель комплекта из МойСклад"""
    id: UUID
    name: str
    code: int
    type: str = Field(validation_alias="pathName")


class BundlesCollection(BaseCollection[BundleModel]):
    """Коллекция комплектов из МойСклад"""
    items: Annotated[list[BundleModel], Field(validation_alias="rows")]
