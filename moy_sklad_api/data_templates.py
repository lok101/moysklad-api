"""
Шаблоны данных для MS API
"""

from uuid import UUID

from moy_sklad_api.enums import EntityType, ProductType


def generate_metadata(entity_id: UUID, entity_type: EntityType | ProductType) -> dict:
    """
    Генерировать метаданные для сущности МойСклад
    
    Args:
        entity_id: ID сущности
        entity_type: Тип сущности
        
    Returns:
        dict: Метаданные в формате MS API
    """
    return {
        "href": f"https://api.moysklad.ru/api/remap/1.2/entity/{entity_type}/{str(entity_id)}",
        "metadataHref": f"https://api.moysklad.ru/api/remap/1.2/entity/{entity_type}/metadata",
        "type": f"{entity_type}",
        "mediaType": "application/json"
    }
