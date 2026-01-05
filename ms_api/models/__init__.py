"""
Модели данных для MS API
"""
from ms_api.models.bundles import (
    BundleModel,
    BundlesCollection
)
from ms_api.models.products import (
    ProductsMSCollection,
    ProductMSModel,
)
from ms_api.models.product_stocks import (
    ProductStocksMSCollection,
    ProductStocksMSModel,
    ProductExpandStocksMSCollection,
    ProductExpandStocksMSModel,
)
from ms_api.models.warehouses import (
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
    "ProductStocksMSCollection",
    "ProductStocksMSModel",
    "ProductExpandStocksMSCollection",
    "ProductExpandStocksMSModel",
    # Stores
    "WarehouseCollection",
    "WarehouseModel",
]
