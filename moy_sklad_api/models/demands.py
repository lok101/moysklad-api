from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, BeforeValidator

from moy_sklad_api.ms_time import MSTime


class DemandModel(BaseModel):
    timestamp: Annotated[datetime, Field(validation_alias="moment"), BeforeValidator(MSTime.datetime_from_str_ms)]


class DemandsCollection(BaseModel):
    items: Annotated[list[DemandModel], Field(validation_alias="rows")]

    def get_first(self) -> DemandModel | None:
        if self.items:
            return self.items[0]

        return None
