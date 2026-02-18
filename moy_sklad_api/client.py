import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping
from urllib.parse import quote
from uuid import UUID

import aiohttp

from moy_sklad_api.exceptions import MoySkladValidationError
from moy_sklad_api.models import (
    ProductStockSCollection,
    ProductExpandStocksCollection,
    ProductsCollection,
    ProductModel,
    WarehouseCollection,
    WarehouseModel,
    BundlesCollection,
    DemandsCollection
)
from moy_sklad_api.enums import EntityType, ProductType
from moy_sklad_api.data_templates import generate_metadata
from moy_sklad_api.models.demands import DemandModel
from moy_sklad_api.utils import convert_to_project_timezone


@dataclass
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
        """Получение нового токена доступа по логину и паролю.

        При генерации нового токена все ранее сгенерированные токены пользователя
        будут отозваны.

        Args:
            login: Логин пользователя МойСклад.
            password: Пароль пользователя МойСклад.

        Returns:
            Токен доступа (access_token).

        Raises:
            MoySkladValidationError: Если логин или пароль не указаны.
            Exception: При ошибке сети или неверных учётных данных.
        """
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

    async def _get_sales_channels(self) -> Mapping:
        url = f"{self._base_url}/entity/saleschannel"

        return await self._async_get(url)

    async def get_warehouses(
            self, *,
            filters: dict[str, Any] | list[Filter | tuple[str, Any]] | None = None,
            order: str | None = None,
            limit: int | None = None,
    ) -> WarehouseCollection:

        query_string = self._build_query_string(filters=filters, order=order, limit=limit)
        url = f"{self._base_url}/entity/store{query_string}"

        response = await self._async_get(url)
        if response is None:
            raise Exception("Не удалось получить склады из API")

        return WarehouseCollection.model_validate(response)

    async def get_warehouse_by_id(self, warehouse_id: str | UUID) -> WarehouseModel | None:

        url = f"{self._base_url}/entity/store/{str(warehouse_id)}"
        response = await self._async_get(url)

        if response is None:
            return None

        store_model = WarehouseModel.model_validate(response)

        return store_model

    @staticmethod
    def _build_query_string(
            filters: list[Filter] | None = None,
            order: str | None = None,
            limit: int | None = None,
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
    ) -> ProductsCollection:
        query_string = self._build_query_string(filters=filters, order=order, limit=limit)
        url = f"{self._base_url}/entity/product{query_string}"

        response = await self._async_get(url)
        if response is None:
            raise Exception("Не удалось получить продукты из API")

        return ProductsCollection.model_validate(response)

    async def get_bundles(
            self, *,
            filters: list[Filter] | None = None,
            order: str | None = None,
            limit: int | None = None,
    ) -> BundlesCollection:
        query_string = self._build_query_string(filters=filters, order=order, limit=limit)
        url = f"{self._base_url}/entity/bundle{query_string}"

        response = await self._async_get(url)
        if response is None:
            raise Exception("Не удалось получить комплекты из API")

        return BundlesCollection.model_validate(response)

    async def get_demands(
            self, *,
            filters: list[Filter] | None = None,
            order: str | None = None,
            limit: int | None = None,
    ) -> DemandsCollection:

        query_string = self._build_query_string(filters=filters, order=order, limit=limit)
        url = f"{self._base_url}/entity/demand{query_string}"

        response = await self._async_get(url)
        if response is None:
            raise Exception("Не удалось получить отгрузки из API")

        return DemandsCollection.model_validate(response)

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

        store_metadata = {"meta": generate_metadata(warehouse_id, EntityType.STORE)}
        organization_metadata = {"meta": generate_metadata(organization_id, EntityType.ORGANIZATION)}
        agent_metadata = {"meta": generate_metadata(agent_id, EntityType.AGENT)}
        project_metadata = {"meta": generate_metadata(project_id, EntityType.PROJECT)}
        sales_channel_metadata = {"meta": generate_metadata(sales_channel_id, EntityType.SALES_CHANNEL)}

        data = {
            "moment": moment.replace(tzinfo=None, microsecond=0).isoformat(sep=" "),
            "organization": organization_metadata,
            "store": store_metadata,
            "agent": agent_metadata,
            "project": project_metadata,
            "salesChannel": sales_channel_metadata,
            "comment": "Создано автоматически.",
            "positions": [
                {
                    "quantity": quantity,
                    "price": price,
                    "assortment": {
                        "meta": generate_metadata(product_id, product_type)
                    }
                } for product_id, quantity, price in positions],
        }

        response = await self._async_post(url, data)

        return DemandModel.model_validate(response)

    async def get_product_by_id(self, product_id: UUID | str) -> ProductModel:

        url = f"{self._base_url}/entity/product/{str(product_id)}"

        response = await self._async_get(url)
        if response is None:
            raise Exception(f"Не удалось получить продукт {product_id} из API")

        product_model = ProductModel.model_validate(response)

        return product_model

    async def get_profit(self, filters: list[Filter] | None = None, ):
        query_string = self._build_query_string(filters=filters)
        url = f"{self._base_url}/report/profit/byproduct{query_string}"

        response = await self._async_get(url)

        if response is None:
            raise Exception("Не удалось получить прибыльность из API")

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
                "meta": generate_metadata(organization_id, EntityType.ORGANIZATION)
            },
            "sourceStore": {
                "meta": generate_metadata(source_store_id, EntityType.STORE)
            },
            "targetStore": {
                "meta": generate_metadata(target_store_id, EntityType.STORE)
            },
            "positions": [
                {
                    "quantity": quantity,
                    "assortment": {
                        "meta": generate_metadata(product_id, EntityType.PRODUCT)
                    }
                } for product_id, quantity in positions]
        }

        response = await self._async_post(url, data)

        return response

    async def get_warehouse_stocks(
            self, *,
            filters: list[Filter] | None = None,
    ) -> ProductStockSCollection:
        query_string = self._build_query_string(filters=filters)
        url = f"{self._base_url}/report/stock/bystore/current{query_string}"

        response = await self._async_get(url)
        if response is None:
            raise Exception("Не удалось получить остатки из API")

        if isinstance(response, list):
            response_data = {"rows": response}
        elif isinstance(response, dict) and "rows" in response:
            response_data = response
        else:
            response_data = {"rows": response}

        return ProductStockSCollection.model_validate(response_data)

    async def get_warehouse_stocks_with_moment(
            self,
            filters: list[Filter] | None = None,
            expand: str | None = "meta",
    ) -> ProductExpandStocksCollection:

        query_string = self._build_query_string(filters=filters, expand=expand)
        url = f"{self._base_url}/report/stock/all{query_string}"

        response = await self._async_get(url)
        if response is None:
            raise Exception("Не удалось получить остатки из API")

        return ProductExpandStocksCollection.model_validate(response)

    async def _async_get(self, url: str):
        try:
            async with self._session.get(url, headers=self._headers) as response:
                response.raise_for_status()
                return await response.json()

        except aiohttp.ClientError as e:
            raise Exception(f"Ошибка сети: {e}")

    async def _async_post(self, url: str, data: dict[str, Any]):
        try:
            async with self._session.post(url, headers=self._headers, json=data) as response:
                response_data = await response.json()
                if response.status >= 400:
                    error_info = response_data if isinstance(response_data, dict) else {"error": str(response_data)}
                    raise Exception(f"Ошибка HTTP {response.status}: {error_info}")
                return response_data
        except Exception as e:
            if "Ошибка HTTP" in str(e):
                raise
            raise Exception(f"Ошибка при выполнении запроса: {e}")

    async def close(self):
        if self._own_session and self._session is not None:
            await self._session.close()
            self._session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
