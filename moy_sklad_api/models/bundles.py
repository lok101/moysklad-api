from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, BeforeValidator

from moy_sklad_api.exceptions import MoySkladAPIException
from moy_sklad_api.models.base_collection import BaseCollection


def _parse_bundle_components(data: dict) -> list[BundleComponentModel]:
    components_data = data.get("rows")

    if components_data is None:
        raise MoySkladAPIException(f"Не найдены компоненты колмплекта. Объект: {data}")

    return [BundleComponentModel.model_validate(item) for item in components_data]


class BundleComponentModel(BaseModel):
    id: UUID
    quantity: float


class BundleModel(BaseModel):
    """Модель комплекта из МойСклад"""
    id: UUID
    name: str
    code: int
    components: Annotated[list[BundleComponentModel], BeforeValidator(_parse_bundel_componens)]
    type: str = Field(validation_alias="pathName")


class BundlesCollection(BaseCollection[BundleModel]):
    """Коллекция комплектов из МойСклад"""
    items: Annotated[list[BundleModel], Field(validation_alias="rows")]
