"""
MoySklad API Client Package

Пакет для работы с API МойСклад (api.moysklad.ru)
"""
from dotenv import load_dotenv

from moy_sklad_api.client import Filter, MoySkladAPIClient
from moy_sklad_api.models import (
    ProductsCollection,
    ProductModel,
    ProductStockSCollection,
    ProductStocksModel,
    ProductExpandStocksCollection,
    ProductExpandStocksModel,
    WarehouseCollection,
    WarehouseModel,
    BundlesCollection,
    BundleModel,
    DemandsCollection, DemandModel,
)
from moy_sklad_api.enums import (
    EntityType,
)

load_dotenv()

__version__ = "0.1.0"

__all__ = [
    "Filter",
    "MoySkladAPIClient",
    "ProductsCollection",
    "ProductModel",
    "ProductStockSCollection",
    "ProductStocksModel",
    "ProductExpandStocksCollection",
    "ProductExpandStocksModel",
    "WarehouseCollection",
    "WarehouseModel",
    "BundlesCollection",
    "BundleModel",
    "EntityType",
    "DemandsCollection",
    "DemandModel"
]
