from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from moy_sklad_api.enums import ProductType


@dataclass(frozen=True, slots=True)
class InventoryPosition:
    product_id: UUID
    quantity: float
    product_type: ProductType
