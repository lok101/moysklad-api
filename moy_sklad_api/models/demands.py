from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, BeforeValidator

from moy_sklad_api.models.base_collection import BaseCollection


class DemandModel(BaseModel):
    id: UUID
    timestamp: Annotated[datetime, Field(validation_alias="moment"), BeforeValidator(datetime.fromisoformat)]


class DemandsCollection(BaseCollection[DemandModel]):
    items: Annotated[list[DemandModel], Field(validation_alias="rows")]
