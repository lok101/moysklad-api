from datetime import datetime, timezone, timedelta
from typing import Any

from moy_sklad_api.exceptions import MoySkladValidationError

PROJECT_TIMEZONE = timezone(timedelta(hours=3))


def get_project_timezone() -> timezone:
    """Получить timezone проекта (UTC+3)"""
    return PROJECT_TIMEZONE


def convert_to_project_timezone(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise MoySkladValidationError("Необходимо указать tz у объекта datetime.")

    return dt.astimezone(PROJECT_TIMEZONE)


def parse_api_datetime(value: Any) -> datetime:
    dt = datetime.fromisoformat(value)
    dt = dt.replace(tzinfo=PROJECT_TIMEZONE)
    return convert_to_project_timezone(dt)


def extract_id(data: dict):
    """Извлечь ID из метаданных"""
    if not isinstance(data, dict) or "href" not in data:
        raise ValueError("Метаданные должны содержать ключ 'href'")
    href = data["href"]
    entity = href.split("/")[-1]
    entity_without_filter = entity.split("?")[0]
    return entity_without_filter
