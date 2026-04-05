from __future__ import annotations

from typing import Any


class MoySkladValidationError(Exception):
    pass


class MoySkladAPIException(Exception):
    pass


class MoySkladRequestError(MoySkladAPIException):
    """Ответ API со структурой ошибок МойСклад (ключ ``errors``).

    Наследует ``MoySkladAPIException``, чтобы существующие ``except MoySkladAPIException``
    по-прежнему перехватывали такие случаи; для ветвления по коду используйте
    ``except MoySkladRequestError`` или атрибуты ``codes`` / ``code``.
    """

    def __init__(self, status: int, payload: dict[str, Any]) -> None:
        self.status = status
        self.payload = payload
        self.codes = _extract_error_codes(payload)
        super().__init__(f"Ошибка HTTP {status}: {payload}")

    @property
    def code(self) -> int | None:
        return self.codes[0] if self.codes else None


def _extract_error_codes(payload: dict[str, Any]) -> list[int]:
    errors = payload.get("errors")
    if not isinstance(errors, list):
        return []
    out: list[int] = []
    for item in errors:
        if isinstance(item, dict):
            c = item.get("code")
            if isinstance(c, int):
                out.append(c)
    return out


class MoySkladConnectionError(Exception):
    pass
