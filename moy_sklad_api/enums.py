import enum


class EntityType(enum.StrEnum):
    PROJECT = 'project'
    PRODUCT = "product"
    BUNDLE = 'bundle'
    STORE = 'store'
    ORGANIZATION = 'organization'
    AGENT = 'counterparty'
    MOVE = 'move'
    DEMAND = 'demand'
    SALES_CHANNEL = 'saleschannel'
    ATTRIBUTE = 'attributemetadata'
    MODIFICATION = 'variant'


class ProductType(enum.StrEnum):
    SINGLE_PRODUCT = 'product'
    COMPOSITE_PRODUCT = 'bundle'
