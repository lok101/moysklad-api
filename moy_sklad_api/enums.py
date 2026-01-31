"""
Общие константы и типы для MS API
"""

import enum


class EntityType(enum.StrEnum):
    """Типы сущностей в МойСклад"""
    PROJECT = 'project'
    STORE = 'store'
    ORGANIZATION = 'organization'
    AGENT = 'counterparty'
    MOVE = 'move'
    DEMAND = 'demand'
    SALES_CHANNEL = 'saleschannel'
    ATTRIBUTE = 'attributemetadata'


class ProductType:
    SINGLE_PRODUCT = 'product'
    COMPOSITE_PRODUCT = 'bundle'
