"""
Модели данных для MS API
"""

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
from ms_api.models.store import (
    StoresCollection,
    StoreModel,
)

__all__ = [
    # Products
    "ProductsMSCollection",
    "ProductMSModel",
    # Product Stocks
    "ProductStocksMSCollection",
    "ProductStocksMSModel",
    "ProductExpandStocksMSCollection",
    "ProductExpandStocksMSModel",
    # Stores
    "StoresCollection",
    "StoreModel",
]

