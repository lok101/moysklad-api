"""
Модели данных для MS API
"""
from moy_sklad_api.models.bundles import (
    BundleModel,
    BundlesCollection
)
from moy_sklad_api.models.demands import (
    DemandsCollection,
    DemandModel
)
from moy_sklad_api.models.product_expand_stocks import (
    ProductExpandStocksCollection,
    ProductExpandStocksModel
)
from moy_sklad_api.models.products import (
    ProductsCollection,
    ProductModel,
)
from moy_sklad_api.models.product_stocks import (
    ProductStockSCollection,
    ProductStocksModel,
)
from moy_sklad_api.models.warehouses import (
    WarehouseCollection,
    WarehouseModel,
)

__all__ = [
    # Products
    "ProductsCollection",
    "ProductModel",
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
    "DemandsCollection",
    "DemandModel"
]
