from datetime import datetime, timezone, timedelta
from typing import Any, TypeVar, Callable
from uuid import UUID

from pydantic import BaseModel

from moy_sklad_api.exceptions import MoySkladValidationError

PROJECT_TIMEZONE = timezone(timedelta(hours=3))

T = TypeVar("T", bound=BaseModel)


def get_project_timezone() -> timezone:
    return PROJECT_TIMEZONE


def convert_to_project_timezone(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise MoySkladValidationError("Необходимо указать tz у объекта datetime.")

    return dt.astimezone(PROJECT_TIMEZONE)


def parse_api_datetime(value: Any) -> datetime:
    dt = datetime.fromisoformat(value)
    dt = dt.replace(tzinfo=PROJECT_TIMEZONE)
    return convert_to_project_timezone(dt)


def _parse_meta_entity_id(value: Any) -> UUID:
    if not isinstance(value, dict):
        raise TypeError("reference must be an object")

    meta = value.get("meta")

    if not isinstance(meta, dict):
        raise TypeError("reference.meta must be an object")

    return UUID(extract_id(meta))


def extract_id(data: dict):
    """Извлечь ID из метаданных"""
    if not isinstance(data, dict) or "href" not in data:
        raise ValueError("Метаданные должны содержать ключ 'href'")
    href = data["href"]
    entity = href.split("/")[-1]
    entity_without_filter = entity.split("?")[0]
    return entity_without_filter


def parse_rows_as(model: type[T]) -> Callable[[Any], list[T]]:
    def _parse(value: Any) -> list[T]:
        if value is None:
            return []
        if isinstance(value, dict):
            rows = value.get("rows", [])
            if isinstance(rows, list):
                return [model.model_validate(item) for item in rows]
        return []

    return _parse
