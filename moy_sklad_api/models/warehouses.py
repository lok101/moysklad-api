from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class WarehouseModel(BaseModel):
    """Модель склада из МойСклад"""
    id: UUID
    name: str
    code: str | None = None
    path_name: Annotated[str, Field(validation_alias="pathName")]
