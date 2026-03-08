from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, BeforeValidator

from moy_sklad_api.utils import parse_api_datetime


class DemandModel(BaseModel):
    id: UUID
    timestamp: Annotated[datetime, Field(validation_alias="moment"), BeforeValidator(parse_api_datetime)]
