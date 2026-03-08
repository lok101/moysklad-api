import json
import os
from collections import defaultdict
from datetime import datetime
from typing import Any, Literal, Mapping
from uuid import UUID

import aiohttp

from moy_sklad_api.exceptions import MoySkladAPIException, MoySkladValidationError
from moy_sklad_api.filter import Filter
from moy_sklad_api.models import (
    ProductModel,
    WarehouseModel,
    ProductStocksModel,
    ProductExpandStocksModel
)
from moy_sklad_api.enums import EntityType, ProductType
from moy_sklad_api.models.metadata import MetaModel
from moy_sklad_api.models.bundle import BundleModel
from moy_sklad_api.models.demand import DemandModel
from moy_sklad_api.utils import convert_to_project_timezone


class MoySkladAPIClient:
    _BASE_URL = "https://api.moysklad.ru/api/remap/1.2"

    def __init__(self, access_token: str | None = None, session: aiohttp.ClientSession | None = None):
        self._base_url = self._BASE_URL

        access_token = access_token or os.getenv("MOY_SKLAD_ACCESS_TOKEN")

        if not access_token:
            raise MoySkladValidationError("Установите токен в виртуальное окружение по ключу MOY_SKLAD_ACCESS_TOKEN.")

        self._headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept-Encoding": "gzip"
        }

        if session is None:
            self._session = aiohttp.ClientSession()
            self._own_session = True

        else:
            self._session = session
            self._own_session = False

    @staticmethod
    async def get_token(login: str, password: str) -> str:
        if not login or not password:
            raise MoySkladValidationError("Логин и пароль обязательны для получения токена.")

        url = f"{MoySkladAPIClient._BASE_URL}/security/token"
        auth = aiohttp.BasicAuth(login, password)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                        url,
                        auth=auth,
                        headers={"Accept-Encoding": "gzip"},
                ) as response:
                    response_data = await response.json()

                    if response.status >= 400:
                        error_info = response_data if isinstance(response_data, dict) else {"error": str(response_data)}
                        raise Exception(f"Ошибка получения токена (HTTP {response.status}): {error_info}")

                    access_token = response_data.get("access_token")
                    if not access_token:
                        raise Exception(f"Токен не найден в ответе API: {response_data}")

                    return access_token

            except aiohttp.ClientError as e:
                raise Exception(f"Ошибка сети при получении токена: {e}")

    async def get_warehouses(
            self, *,
            filters: dict[str, Any] | list[Filter] | None = None,
            order: str | None = None,
            limit: int | None = None,
    ) -> list[WarehouseModel]:

        query_string = self._build_query_string(filters=filters, order=order, limit=limit)
        url = f"{self._base_url}/entity/store{query_string}"

        response = await self._async_get(url)

        return [WarehouseModel.model_validate(item) for item in response["rows"]]

    async def get_warehouse_by_id(self, warehouse_id: str | UUID) -> WarehouseModel | None:

        url = f"{self._base_url}/entity/store/{str(warehouse_id)}"
        response = await self._async_get(url)

        return WarehouseModel.model_validate(response)

    @staticmethod
    def _build_query_string(
            filters: list[Filter] | None = None,
            order: str | None = None,
            limit: int | None = None,
            offset: int | None = None,
            expand: str | None = None,
            **kwargs: Any
    ) -> str:
        query_parts = []

        if filters:
            field_values: dict[str, list[Any]] = defaultdict(list)
            for item in filters:
                field_values[item.field].append(item.value)

            filter_parts = []
            for field, values in field_values.items():
                formatted = ";".join(Filter.format_value(v) for v in values)
                filter_parts.append(f"{field}={formatted}")

            if filter_parts:
                filter_string = "&".join(filter_parts)
                query_parts.append(f"filter={filter_string}")

        if order:
            query_parts.append(f"order={order}")

        if limit is not None:
            query_parts.append(f"limit={limit}")

        if offset is not None:
            query_parts.append(f"offset={offset}")

        if expand:
            query_parts.append(f"expand={expand}")

        for key, value in kwargs.items():
            if value is not None:
                query_parts.append(f"{key}={Filter.format_value}")

        if not query_parts:
            return ""

        return f"?{'&'.join(query_parts)}"

    async def get_products(
            self, *,
            filters: list[Filter] | None = None,
            order: str | None = None,
            limit: int | None = None,
    ) -> list[ProductModel]:

        query_string = self._build_query_string(filters=filters, order=order, limit=limit)
        url = f"{self._base_url}/entity/product{query_string}"

        response = await self._async_get(url)

        return [ProductModel.model_validate(item) for item in response["rows"]]

    async def get_bundles(
            self, *,
            filters: list[Filter] | None = None,
            order: str | None = None,
    ) -> list[BundleModel]:
        all_items: list[Mapping] = []

        entity_per_request: int = 100
        pagination_page = 0

        while True:
            query_string = self._build_query_string(
                filters=filters,
                order=order,
                limit=entity_per_request,
                offset=pagination_page * entity_per_request,
                expand="components.assortment.product"
            )

            url = f"{self._base_url}/entity/bundle{query_string}"

            response = await self._async_get(url)

            items: list[Mapping] = response["rows"]

            all_items.extend(items)
            pagination_page += 1

            if len(items) < entity_per_request:
                break

        return [BundleModel.model_validate(item) for item in all_items]

    async def create_bundle(
            self,
            name: str,
            code: str,
            components: list[tuple[UUID, float, EntityType]],
            path_name: str | None = None,
    ) -> UUID:
        url = f"{self._base_url}/entity/bundle"

        data = {
            "name": name,
            "code": code,
            "components": [
                {
                    "assortment": {
                        "meta": MetaModel.for_entity(product_id, entity_type).to_api_dict()
                    },
                    "quantity": quantity,
                }
                for product_id, quantity, entity_type in components
            ],
        }

        if path_name:
            data["pathName"] = path_name

        response = await self._async_post(url, data)

        return response["id"]

    async def archive_bundle(self, bundle_id: UUID):
        url = f"{self._base_url}/entity/bundle/{bundle_id}"
        data = {
            "archived": True,
        }

        response = await self._async_put(url, data)

        return response["id"]

    async def get_demands(
            self, *,
            filters: list[Filter] | None = None,
            order: str | None = None,
            limit: int | None = None,
    ) -> list[DemandModel]:

        query_string = self._build_query_string(filters=filters, order=order, limit=limit)
        url = f"{self._base_url}/entity/demand{query_string}"

        response = await self._async_get(url)

        return [DemandModel.model_validate(item) for item in response["rows"]]

    async def create_demand(
            self,
            warehouse_id: UUID,
            positions: list[tuple[UUID, int, int]],
            moment: datetime,
            organization_id: UUID,
            agent_id: UUID,
            project_id: UUID,
            sales_channel_id: UUID,
            product_type: ProductType
    ) -> DemandModel:

        url = f"{self._base_url}/entity/demand"

        moment = convert_to_project_timezone(moment)

        store_metadata = {"meta": MetaModel.for_entity(warehouse_id, EntityType.STORE).to_api_dict()}
        organization_metadata = {"meta": MetaModel.for_entity(organization_id, EntityType.ORGANIZATION).to_api_dict()}
        agent_metadata = {"meta": MetaModel.for_entity(agent_id, EntityType.AGENT).to_api_dict()}
        project_metadata = {"meta": MetaModel.for_entity(project_id, EntityType.PROJECT).to_api_dict()}
        sales_channel_metadata = {
            "meta": MetaModel.for_entity(sales_channel_id, EntityType.SALES_CHANNEL).to_api_dict()}

        data = {
            "moment": moment.replace(tzinfo=None, microsecond=0).isoformat(sep=" "),
            "organization": organization_metadata,
            "store": store_metadata,
            "agent": agent_metadata,
            "project": project_metadata,
            "salesChannel": sales_channel_metadata,
            "description": "Создано автоматически.",
            "positions": [
                {
                    "quantity": quantity,
                    "price": price,
                    "assortment": {
                        "meta": MetaModel.for_entity(product_id, product_type).to_api_dict()
                    }
                } for product_id, quantity, price in positions],
        }

        response = await self._async_post(url, data)

        return DemandModel.model_validate(response)

    async def get_product_by_id(self, product_id: UUID | str) -> ProductModel:

        url = f"{self._base_url}/entity/product/{str(product_id)}"

        response = await self._async_get(url)

        return ProductModel.model_validate(response)

    async def get_profit(self, filters: list[Filter] | None = None, ):
        query_string = self._build_query_string(filters=filters)
        url = f"{self._base_url}/report/profit/byproduct{query_string}"

        response = await self._async_get(url)

        return response

    async def create_move(
            self,
            target_store_id: UUID,
            positions: list[tuple[UUID, int]],
            source_store_id: UUID,
            moment: datetime,
            organization_id: UUID,
    ) -> Mapping:

        url = f"{self._base_url}/entity/move"

        moment = convert_to_project_timezone(moment)

        data = {
            "moment": moment.replace(tzinfo=None, microsecond=0).isoformat(sep=" "),
            "comment": "Создано автоматически.",
            "organization": {
                "meta": MetaModel.for_entity(organization_id, EntityType.ORGANIZATION).to_api_dict()
            },
            "sourceStore": {
                "meta": MetaModel.for_entity(source_store_id, EntityType.STORE).to_api_dict()
            },
            "targetStore": {
                "meta": MetaModel.for_entity(target_store_id, EntityType.STORE).to_api_dict()
            },
            "positions": [
                {
                    "quantity": quantity,
                    "assortment": {
                        "meta": MetaModel.for_entity(product_id, EntityType.PRODUCT).to_api_dict()
                    }
                } for product_id, quantity in positions]
        }

        response = await self._async_post(url, data)

        return response

    async def get_warehouse_stocks(self, *, filters: list[Filter] | None = None) -> list[ProductStocksModel]:
        query_string = self._build_query_string(filters=filters)
        url = f"{self._base_url}/report/stock/bystore/current{query_string}"

        response = await self._async_get(url)

        return [ProductStocksModel.model_validate(item) for item in response]

    async def get_warehouse_stocks_with_moment(
            self,
            filters: list[Filter] | None = None,
            expand: str | None = "meta",
    ) -> list[ProductExpandStocksModel]:

        query_string = self._build_query_string(filters=filters, expand=expand)
        url = f"{self._base_url}/report/stock/all{query_string}"

        response = await self._async_get(url)

        return [ProductExpandStocksModel.model_validate(item) for item in response["rows"]]

    async def _async_request(
            self,
            method: Literal["GET", "POST", "PUT"],
            url: str,
            data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        try:
            kwargs: dict[str, Any] = {"headers": self._headers}

            if data is not None:
                kwargs["json"] = data

            async with self._session.request(method, url, **kwargs) as response:
                response_data = await response.json()

                if response.status >= 400:
                    error_info = (
                        response_data
                        if isinstance(response_data, dict)
                        else {"error": str(response_data)}
                    )
                    raise MoySkladAPIException(
                        f"Ошибка HTTP {response.status}: {error_info}"
                    )

                return response_data

        except aiohttp.ClientError as e:
            raise MoySkladAPIException(f"Ошибка при выполнении запроса: {e}")

        except json.JSONDecodeError as e:
            raise MoySkladAPIException(f"API вернул невалидный JSON: {e}")

    async def _async_get(self, url: str) -> dict[str, Any]:
        return await self._async_request("GET", url)

    async def _async_post(self, url: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._async_request("POST", url, data)

    async def _async_put(self, url: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._async_request("PUT", url, data)

    async def close(self):
        if self._own_session and self._session is not None:
            await self._session.close()
            self._session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
