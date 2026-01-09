"""
MoySklad API Client Package

Пакет для работы с API МойСклад (api.moysklad.ru)
"""
from dotenv import load_dotenv

from moy_sklad_api.client import Filter, MoySkladAPIClient
from moy_sklad_api.models import (
    ProductsMSCollection,
    ProductMSModel,
    ProductStockSCollection,
    ProductStocksModel,
    ProductExpandStocksCollection,
    ProductExpandStocksModel,
    WarehouseCollection,
    WarehouseModel,
    BundlesCollection,
    BundleModel,
    DemandsCollection,
)
from moy_sklad_api.enums import (
    EntityType,
)

load_dotenv()

__version__ = "0.1.0"

__all__ = [
    "Filter",
    "MoySkladAPIClient",
    "ProductsMSCollection",
    "ProductMSModel",
    "ProductStockSCollection",
    "ProductStocksModel",
    "ProductExpandStocksCollection",
    "ProductExpandStocksModel",
    "WarehouseCollection",
    "WarehouseModel",
    "BundlesCollection",
    "BundleModel",
    "EntityType",
    "DemandsCollection"
]
