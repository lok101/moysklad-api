from datetime import datetime, timezone, timedelta
from typing import Any


PROJECT_TIMEZONE = timezone(timedelta(hours=3))


def get_project_timezone() -> timezone:
    """Получить timezone проекта (UTC+3)"""
    return PROJECT_TIMEZONE


def convert_to_project_timezone(dt: datetime) -> datetime:
    """
    Конвертировать datetime в timezone проекта (UTC+3).
    Если datetime naive, предполагается что он уже в UTC.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(PROJECT_TIMEZONE)


def convert_from_project_timezone(dt: datetime) -> datetime:
    """
    Конвертировать datetime из timezone проекта в UTC (для отправки в API).
    Если datetime naive, предполагается что он уже в timezone проекта.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=PROJECT_TIMEZONE)
    return dt.astimezone(timezone.utc)


def parse_api_datetime(value: Any) -> datetime:
    """
    Парсить datetime из API и конвертировать в timezone проекта.
    API возвращает datetime в ISO формате, обычно в UTC.
    """
    if isinstance(value, str):
        normalized = value.replace('Z', '+00:00')
        try:
            dt = datetime.fromisoformat(normalized)
        except ValueError:
            dt = datetime.fromisoformat(normalized.replace(' ', 'T'))
    elif isinstance(value, datetime):
        dt = value
    else:
        raise ValueError(f"Неверный тип для datetime: {type(value)}")
    
    return convert_to_project_timezone(dt)


def extract_id(data: dict):
    """Извлечь ID из метаданных"""
    if not isinstance(data, dict) or "href" not in data:
        raise ValueError("Метаданные должны содержать ключ 'href'")
    href = data["href"]
    entity = href.split("/")[-1]
    entity_without_filter = entity.split("?")[0]
    return entity_without_filter
