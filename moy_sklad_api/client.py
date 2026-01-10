"""
Клиент для работы с API МойСклад
"""
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping
from urllib.parse import quote
from uuid import UUID

import aiohttp
import requests

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
from moy_sklad_api.enums import EntityType
from moy_sklad_api.data_templates import generate_metadata
from moy_sklad_api.models.demands import DemandModel


@dataclass
class Filter:
    """Класс для представления одного условия фильтрации"""
    field: str
    value: Any

    def to_string(self) -> str:
        return f"{self.field}={self._format_value(self.value)}"

    @staticmethod
    def _format_value(value: Any) -> str:
        if isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, UUID):
            return str(value)
        elif isinstance(value, str):
            if value.startswith("http://") or value.startswith("https://"):
                return quote(value, safe='/:')
            return quote(value, safe='')
        else:
            return str(value)


class MoySkladAPIClient:
    """
    Клиент для работы с API МойСклад (api.moysklad.ru)
    
    Args:
        access_token: Токен доступа к API
        session: Опциональная сессия aiohttp. Если не передана, будет создана новая.
    """

    def __init__(self, access_token: str | None = None, session: aiohttp.ClientSession | None = None):
        self._base_url = "https://api.moysklad.ru/api/remap/1.2"

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

    async def get_warehouses(
            self, *,
            filters: dict[str, Any] | list[Filter | tuple[str, Any]] | None = None,
            order: str | None = None,
            limit: int | None = None,
    ) -> WarehouseCollection:
        """
        Получить список складов с возможностью фильтрации
        
        Args:
            filters: Словарь или список Filter/кортежей для фильтрации
            order: Параметр сортировки (например, "name,asc")
            limit: Лимит количества записей
        
        Returns:
            WarehouseCollection: Коллекция складов
        """
        query_string = self._build_query_string(filters=filters, order=order, limit=limit)
        url = f"{self._base_url}/entity/store{query_string}"

        response = await self._async_get(url)
        if response is None:
            raise Exception("Не удалось получить склады из API")

        return WarehouseCollection.model_validate(response)

    async def get_warehouse_by_id(self, warehouse_id: str | UUID) -> WarehouseModel | None:
        """
        Получить склад по ID
        
        Args:
            warehouse_id: ID склада
            
        Returns:
            StoreModel или None, если склад не найден
        """
        url = f"{self._base_url}/entity/store/{str(warehouse_id)}"
        response = await self._async_get(url)

        if response is None:
            return None

        store_model = WarehouseModel.model_validate(response)

        return store_model

    def _build_query_string(
            self,
            filters: dict[str, Any] | list[Filter | tuple[str, Any]] | None = None,
            order: str | None = None,
            limit: int | None = None,
            expand: str | None = None,
            **kwargs: Any
    ) -> str:
        """
        Построить строку query параметров для API МойСклад

        Args:
            filters: Словарь или список Filter/кортежей для фильтрации.
                    Словарь: {"поле": значение/список_значений}
                    Список: [Filter(...), ...] или [("поле", значение), ...]
                    Несколько значений одного поля объединяются через OR.
                    Разные поля объединяются через AND.
            order: Параметр сортировки (например, "moment,desc")
            limit: Лимит количества записей
            expand: Параметр расширения (например, "meta")
            **kwargs: Дополнительные query параметры

        Returns:
            str: Строка query параметров вида "?filter=...&order=...&limit=..."
        """
        query_parts = []

        if filters:
            filter_parts = []

            if isinstance(filters, list):
                for item in filters:
                    if isinstance(item, Filter):
                        filter_parts.append(item.to_string())
                    elif isinstance(item, tuple):
                        field, value = item
                        if isinstance(value, (list, tuple)):
                            for v in value:
                                filter_parts.append(f"{field}={self._format_filter_value(v)}")
                        else:
                            filter_parts.append(f"{field}={self._format_filter_value(value)}")
            elif isinstance(filters, dict):
                for field, value in filters.items():
                    if isinstance(value, (list, tuple)):
                        for v in value:
                            filter_parts.append(f"{field}={self._format_filter_value(v)}")
                    else:
                        filter_parts.append(f"{field}={self._format_filter_value(value)}")

            if filter_parts:
                query_parts.append(f"filter={';'.join(filter_parts)}")

        if order:
            query_parts.append(f"order={order}")

        if limit is not None:
            query_parts.append(f"limit={limit}")

        if expand:
            query_parts.append(f"expand={expand}")

        for key, value in kwargs.items():
            if value is not None:
                query_parts.append(f"{key}={self._format_filter_value(value)}")

        if not query_parts:
            return ""

        return f"?{'&'.join(query_parts)}"

    def _format_filter_value(self, value: Any) -> str:
        """
        Форматировать значение для фильтра
        
        Args:
            value: Значение для фильтрации
            
        Returns:
            str: Отформатированное значение
        """
        if isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, UUID):
            return str(value)
        elif isinstance(value, str):
            if value.startswith("http://") or value.startswith("https://"):
                return quote(value, safe='/:')
            return quote(value, safe='')
        else:
            return str(value)

    async def get_products(
            self, *,
            filters: dict[str, Any] | list[Filter | tuple[str, Any]] | None = None,
            order: str | None = None,
            limit: int | None = None,
    ) -> ProductsCollection:
        """
        Получить список товаров с возможностью фильтрации
        
        Args:
            filters: Словарь или список Filter/кортежей для фильтрации.
                    Словарь: {"поле": значение/список_значений}
                    Список: [Filter(...), ...] или [("поле", значение), ...]
                    Несколько значений одного поля объединяются через OR.
                    Разные поля объединяются через AND.
            order: Параметр сортировки (например, "name,asc")
            limit: Лимит количества записей
        
        Returns:
            ProductsCollection: Коллекция товаров
        """
        query_string = self._build_query_string(filters=filters, order=order, limit=limit)
        url = f"{self._base_url}/entity/product{query_string}"

        response = await self._async_get(url)
        if response is None:
            raise Exception("Не удалось получить продукты из API")

        return ProductsCollection.model_validate(response)

    async def get_bundles(
            self, *,
            filters: dict[str, Any] | list[Filter | tuple[str, Any]] | None = None,
            order: str | None = None,
            limit: int | None = None,
    ) -> BundlesCollection:
        """
        Получить список комплектов с возможностью фильтрации
        
        Args:
            filters: Словарь или список Filter/кортежей для фильтрации
            order: Параметр сортировки (например, "name,asc")
            limit: Лимит количества записей
        
        Returns:
            BundlesCollection: Коллекция комплектов
        """
        query_string = self._build_query_string(filters=filters, order=order, limit=limit)
        url = f"{self._base_url}/entity/bundle{query_string}"

        response = await self._async_get(url)
        if response is None:
            raise Exception("Не удалось получить комплекты из API")

        return BundlesCollection.model_validate(response)

    async def get_demands(
            self, *,
            filters: dict[str, Any] | list[Filter | tuple[str, Any]] | None = None,
            order: str | None = None,
            limit: int | None = None,
    ) -> DemandsCollection:
        """
        Получить список отгрузок с возможностью фильтрации
        
        Args:
            filters: Словарь или список Filter/кортежей для фильтрации.
                    Для фильтрации по организации или складу используйте полные URL:
                    {"organization": "https://api.moysklad.ru/api/remap/1.2/entity/organization/{id}"}
            order: Параметр сортировки (например, "moment,desc")
            limit: Лимит количества записей
        
        Returns:
            Mapping с данными отгрузок
        """
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
    ) -> DemandModel:
        """
        Создать документ отгрузки
        
        Args:
            warehouse_id: ID склада
            positions: Список позиций (product_id, quantity, price)
            moment: Момент отгрузки в формате MS API
            organization_id: ID организации
            agent_id: ID контрагента
            project_id: ID проекта
            sales_channel_id: ID канала продаж
            
        Returns:
            Mapping с данными созданного документа
        """
        url = f"{self._base_url}/entity/demand"

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
                        "meta": generate_metadata(product_id, EntityType.PRODUCT)
                    }
                } for product_id, quantity, price in positions],
        }

        response = await self._async_post(url, data)

        return DemandModel.model_validate(response)

    async def get_product_by_id(self, product_id: UUID | str) -> ProductModel:
        """
        Получить товар по ID
        
        Args:
            product_id: ID товара
            
        Returns:
            ProductModel: Модель товара
        """
        url = f"{self._base_url}/entity/product/{str(product_id)}"

        response = await self._async_get(url)
        if response is None:
            raise Exception(f"Не удалось получить продукт {product_id} из API")

        product_model = ProductModel.model_validate(response)

        return product_model

    async def create_move(
            self,
            target_store_id: UUID,
            positions: list[tuple[UUID, int]],
            source_store_id: UUID,
            moment: datetime,
            organization_id: UUID,
    ) -> Mapping:
        """
        Создать документ перемещения
        
        Args:
            target_store_id: ID склада назначения
            positions: Список позиций (product_id, quantity)
            source_store_id: ID склада источника
            moment: Момент перемещения
            organization_id: ID организации
            
        Returns:
            Mapping с данными созданного документа
        """
        url = f"{self._base_url}/entity/move"

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
            filters: dict[str, Any] | list[Filter | tuple[str, Any]] | None = None,
    ) -> ProductStockSCollection:
        """
        Получить текущие остатки на складе с возможностью фильтрации
        
        Args:
            filters: Словарь или список Filter/кортежей для фильтрации.
                    Например: {"storeId": "uuid-склада"}
        
        Returns:
            ProductStockSCollection: Коллекция остатков
        """
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
            filters: dict[str, Any] | list[Filter | tuple[str, Any]] | None = None,
            expand: str | None = "meta",
    ) -> ProductExpandStocksCollection:
        """
        Получить остатки на складе на определенный момент времени с возможностью фильтрации
        
        Args:
            filters: Словарь или список Filter/кортежей для фильтрации.
                    Для фильтрации по моменту времени используйте:
                    {"moment": "2025-01-01T12:00:00"}
                    Для фильтрации по складу используйте полный URL:
                    {"store": "https://api.moysklad.ru/api/remap/1.2/entity/store/{id}"}
            expand: Параметр расширения (по умолчанию "meta")
        
        Returns:
            ProductExpandStocksCollection: Коллекция остатков
        """
        query_string = self._build_query_string(filters=filters, expand=expand)
        url = f"{self._base_url}/report/stock/all{query_string}"

        response = await self._async_get(url)
        if response is None:
            raise Exception("Не удалось получить остатки из API")

        return ProductExpandStocksCollection.model_validate(response)

    async def _async_get(self, url: str):
        """Асинхронный GET запрос"""
        try:
            async with self._session.get(url, headers=self._headers) as response:
                response.raise_for_status()
                return await response.json()

        except aiohttp.ClientError as e:
            raise Exception(f"Ошибка сети: {e}")

    async def _async_post(self, url: str, data: dict[str, Any]):
        """Асинхронный POST запрос"""
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
        """Закрыть сессию, если она была создана клиентом"""
        if self._own_session and self._session is not None:
            await self._session.close()
            self._session = None

    async def __aenter__(self):
        """Поддержка async context manager"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии при выходе из context manager"""
        await self.close()

    def _sync_post(self, url, data: dict[str, Any]):
        """Синхронный POST запрос"""
        response = requests.post(url=url, headers=self._headers, json=data)
        response.raise_for_status()
        return response.json()
