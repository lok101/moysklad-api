from __future__ import annotations

import asyncio
import inspect
import logging
import os
from datetime import datetime, timezone, timedelta
from functools import wraps
from typing import Any, Callable, TypeVar
from uuid import UUID

from pydantic import BaseModel

from moy_sklad_api.exceptions import MoySkladValidationError, MoySkladConnectionError, MoySkladAPIException

PROJECT_TIMEZONE = timezone(timedelta(hours=3))

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)


def get_required_env(var_name: str) -> str:
    value: str | None = os.getenv(var_name)

    if value is None or not value.strip():
        raise MoySkladAPIException(f"Env-переменная '{var_name}' не задана или пустая.")

    return value.strip()


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


def tries(times: int = 5, timeout: int = 10) -> Callable[[type], type]:
    """Повтор запросов при сетевых сбоях для всех вызовов HTTP через класс клиента."""

    def _retry_async_method(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(1, times + 1):
                try:
                    return await func(*args, **kwargs)

                except MoySkladConnectionError as ex:
                    logger.warning(
                        "Неуспешная попытка обращения к API. "
                        "Номер попытки: %s. "
                        "Таймаут: %s секунд",
                        attempt,
                        timeout,
                    )

                    if attempt == times:
                        raise MoySkladAPIException() from ex

                    await asyncio.sleep(timeout)

            raise RuntimeError("unreachable")  # for type checkers

        return wrapper

    def class_decorator(cls: type) -> type:
        body = cls.__dict__
        target = body.get("_async_request")
        if target is not None and inspect.iscoroutinefunction(target):
            setattr(cls, "_async_request", _retry_async_method(target))
            return cls

        skip = frozenset({"close"})
        for name, attr in body.items():
            if name.startswith("__") or name in skip:
                continue
            if isinstance(attr, (staticmethod, classmethod, property)):
                continue
            if inspect.iscoroutinefunction(attr):
                setattr(cls, name, _retry_async_method(attr))

        return cls

    return class_decorator
