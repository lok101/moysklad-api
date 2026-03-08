from uuid import UUID

from pydantic import BaseModel


class WarehouseModel(BaseModel):
    """Модель склада из МойСклад"""
    id: UUID
    name: str
    code: int | None = None
