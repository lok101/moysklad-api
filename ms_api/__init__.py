"""
MoySklad API Client Package

Пакет для работы с API МойСклад (api.moysklad.ru)
"""
from dotenv import load_dotenv

from ms_api.client import MoySkladAPIClient
from ms_api.models import (
    ProductsMSCollection,
    ProductMSModel,
    ProductStocksMSCollection,
    ProductStocksMSModel,
    ProductExpandStocksMSCollection,
    ProductExpandStocksMSModel,
    WarehouseCollection,
    WarehouseModel,
    BundlesCollection,
    BundleModel,
)
from ms_api.common import (
    ProductType,
    EntityType,
)

load_dotenv()

__version__ = "0.1.0"

__all__ = [
    "MoySkladAPIClient",
    "ProductsMSCollection",
    "ProductMSModel",
    "ProductStocksMSCollection",
    "ProductStocksMSModel",
    "ProductExpandStocksMSCollection",
    "ProductExpandStocksMSModel",
    "WarehouseCollection",
    "WarehouseModel",
    "BundlesCollection",
    "BundleModel",
    "ProductType",
    "EntityType",
]
