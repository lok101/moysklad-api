"""
Общие константы и типы для MS API
"""

import enum
from uuid import UUID

BASE_URL = "https://api.moysklad.ru/api/remap/1.2"


class EntityType(enum.StrEnum):
    """Типы сущностей в МойСклад"""
    PROJECT = 'project'
    STORE = 'store'
    PRODUCT = 'product'
    ORGANIZATION = 'organization'
    AGENT = 'counterparty'
    MOVE = 'move'
    DEMAND = 'demand'
    SALES_CHANNEL = 'saleschannel'
    ATTRIBUTE = 'attributemetadata'


class MSProductType(enum.StrEnum):
    """Типы товаров в МойСклад"""
    SNACK = 'Основной склад Остатки/МОИ Снэки'
    FOOD = 'Основной склад Остатки/МОИ Снэки/Сэндвичи, салаты'

