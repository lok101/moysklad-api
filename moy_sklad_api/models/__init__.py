"""
Модели данных для MS API
"""
from moy_sklad_api.models.bundles import (
    BundleModel,
    BundlesCollection
)
from moy_sklad_api.models.demands import DemandsCollection
from moy_sklad_api.models.products import (
    ProductsMSCollection,
    ProductMSModel,
)
from moy_sklad_api.models.product_stocks import (
    ProductStockSCollection,
    ProductStocksModel,
    ProductExpandStocksCollection,
    ProductExpandStocksModel,
)
from moy_sklad_api.models.warehouses import (
    WarehouseCollection,
    WarehouseModel,
)

__all__ = [
    # Products
    "ProductsMSCollection",
    "ProductMSModel",
    # Bundles
    "BundleModel",
    "BundlesCollection",
    # Product Stocks
    "ProductStockSCollection",
    "ProductStocksModel",
    "ProductExpandStocksCollection",
    "ProductExpandStocksModel",
    # Stores
    "WarehouseCollection",
    "WarehouseModel",
    # Demands
    "DemandsCollection"
]
