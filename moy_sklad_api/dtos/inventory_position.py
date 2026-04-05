from dataclasses import dataclass
from uuid import UUID

from beartype import beartype
from moy_sklad_api import ProductType


@beartype
@dataclass(frozen=True, slots=True, kw_only=True)
class InventoryPositionDTO:
    product_id: UUID
    product_type: ProductType
    quantity: float
