from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from moy_sklad_api.enums import EntityType, ProductType


class MetaModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    href: str
    type: str
    media_type: str | None = Field(
        default=None,
        validation_alias="mediaType",
        serialization_alias="mediaType",
    )
    metadata_href: str | None = Field(
        default=None,
        validation_alias="metadataHref",
        serialization_alias="metadataHref",
    )

    @classmethod
    def for_entity(
        cls,
        entity_id: UUID,
        entity_type: EntityType | ProductType,
    ) -> "MetaModel":

        base_url = "https://api.moysklad.ru/api/remap/1.2/entity"
        return cls(
            href=f"{base_url}/{entity_type}/{entity_id}",
            metadata_href=f"{base_url}/{entity_type}/metadata",
            type=str(entity_type),
            media_type="application/json",
        )

    def to_api_dict(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True)
