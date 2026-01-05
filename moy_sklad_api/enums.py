"""
Общие константы и типы для MS API
"""

import enum


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
