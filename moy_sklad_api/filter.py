from dataclasses import dataclass
from datetime import datetime
from typing import Any
from urllib.parse import quote
from uuid import UUID

from moy_sklad_api.utils import convert_to_project_timezone


@dataclass(frozen=True, slots=True)
class Filter:
    field: str
    value: Any

    def to_string(self) -> str:
        return f"{self.field}={self.format_value(self.value)}"

    @staticmethod
    def format_value(value: Any) -> str:
        if isinstance(value, bool):
            return str(value).lower()

        elif isinstance(value, UUID):
            return str(value)

        elif isinstance(value, str):
            if value.startswith("http://") or value.startswith("https://"):
                return quote(value, safe='/:')

            return value

        elif isinstance(value, datetime):
            moment = convert_to_project_timezone(value)
            return moment.replace(tzinfo=None, microsecond=0).isoformat(sep=" ")

        else:
            return str(value)
