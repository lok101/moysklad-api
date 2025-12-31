"""
MoySklad API Client Package

Пакет для работы с API МойСклад (api.moysklad.ru)
"""

from ms_api.client import MoySkladAPIClient
from ms_api.models import (
    ProductsMSCollection,
    ProductMSModel,
    ProductStocksMSCollection,
    ProductStocksMSModel,
    ProductExpandStocksMSCollection,
    ProductExpandStocksMSModel,
    StoresCollection,
    StoreModel,
)
from ms_api.common import (
    MSProductType,
    EntityType,
    BASE_URL,
)

__version__ = "0.1.0"

__all__ = [
    "MoySkladAPIClient",
    "ProductsMSCollection",
    "ProductMSModel",
    "ProductStocksMSCollection",
    "ProductStocksMSModel",
    "ProductExpandStocksMSCollection",
    "ProductExpandStocksMSModel",
    "StoresCollection",
    "StoreModel",
    "MSProductType",
    "EntityType",
    "BASE_URL",
]

