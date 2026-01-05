"""
Клиент для работы с API МойСклад
"""
import os
from datetime import datetime
from typing import Any, Mapping
from uuid import UUID

import aiohttp
import requests

from ms_api.exceptions import MoySkladValidationError
from ms_api.models import (
    ProductStocksMSCollection,
    ProductExpandStocksMSCollection,
    ProductsMSCollection,
    ProductMSModel,
    WarehouseCollection,
    WarehouseModel,
    BundlesCollection,
)
from ms_api.common import ProductType, EntityType, BundleType
from ms_api.data_templates import generate_metadata
from ms_api.ms_time import MSTime


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
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json"
        }
        
        if session is None:
            self._session = aiohttp.ClientSession()
            self._own_session = True
        else:
            self._session = session
            self._own_session = False

    async def get_warehouse_by_ex_code(self, code: int) -> WarehouseModel | None:
        """
        Получить склад по внешнему коду
        
        Args:
            code: Внешний код склада
            
        Returns:
            StoreModel или None, если склад не найден
        """
        url = f"{self._base_url}/entity/store?filter=code={code}"
        response = await self._async_get(url)

        if response is None:
            return None

        store_model = WarehouseCollection.model_validate(response)

        if store_model.items:
            return store_model.items[0]
        return None

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

    async def get_products(self) -> ProductsMSCollection:
        """
        Получить список товаров (снэки и еда)
        
        Returns:
            ProductsMSCollection: Коллекция товаров
        """
        request_filter = (
            f"?filter=pathName={ProductType.SNACK}"
            f";pathName={ProductType.FOOD}"
        )
        url = f"{self._base_url}/entity/product{request_filter}"

        response = await self._async_get(url)
        if response is None:
            raise Exception("Не удалось получить продукты из API")

        products_collection = ProductsMSCollection.model_validate(response)

        return products_collection

    async def get_bundles(self) -> BundlesCollection:
        request_filter = (
            f"?filter=pathName={BundleType.COFFEE}"
        )
        url = f"{self._base_url}/entity/bundle{request_filter}"

        response = await self._async_get(url)
        if response is None:
            raise Exception("Не удалось получить продукты из API")

        bundles_collection = BundlesCollection.model_validate(response)

        return bundles_collection

    async def get_last_demand(self, warehouse_id: UUID, organization_id: UUID) -> Mapping | None:
        """
        Получить последнюю отгрузку для склада
        
        Args:
            warehouse_id: ID склада
            organization_id: ID организации
            
        Returns:
            Mapping с данными отгрузки или None
        """
        url = (
            f"{self._base_url}/entity/demand"
            f"?filter=organization=https://api.moysklad.ru/api/remap/1.2/entity/organization/{str(organization_id)}"
            f";store=https://api.moysklad.ru/api/remap/1.2/entity/store/{str(warehouse_id)}"
            f"&order=moment,desc"
            f"&limit=100"
        )

        response = await self._async_get(url)
        if response is None:
            return None

        if isinstance(response, dict) and response.get("rows"):
            rows = response["rows"]
            if rows:
                return rows[0]
        return None

    async def create_demand(
            self,
            warehouse_id: UUID,
            positions: list[tuple[UUID, int, int]],
            moment: str,
            organization_id: UUID,
            agent_id: UUID,
            project_id: UUID,
            sales_channel_id: UUID,
    ) -> Mapping:
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
            "moment": moment,
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

        return response

    async def get_product_by_id(self, product_id: UUID | str) -> ProductMSModel:
        """
        Получить товар по ID
        
        Args:
            product_id: ID товара
            
        Returns:
            ProductMSModel: Модель товара
        """
        url = f"{self._base_url}/entity/product/{str(product_id)}"

        response = await self._async_get(url)
        if response is None:
            raise Exception(f"Не удалось получить продукт {product_id} из API")

        product_model = ProductMSModel.model_validate(response)

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
            "moment": MSTime.datetime_to_str_ms(moment),
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

    async def get_warehouse_stocks(self, store_id: UUID) -> ProductStocksMSCollection:
        """
        Получить текущие остатки на складе
        
        Args:
            store_id: ID склада
            
        Returns:
            ProductStocksMSCollection: Коллекция остатков
        """
        request_filter = f"filter=storeId={str(store_id)}"

        url = f"{self._base_url}/report/stock/bystore/current?{request_filter}"

        response = await self._async_get(url)
        if response is None:
            raise Exception(f"Не удалось получить остатки склада {store_id} из API")

        # API возвращает массив напрямую, оборачиваем в структуру с rows
        if isinstance(response, list):
            response_data = {"rows": response}
        elif isinstance(response, dict) and "rows" in response:
            response_data = response
        else:
            response_data = {"rows": response}

        stocks_collection = ProductStocksMSCollection.model_validate(response_data)

        return stocks_collection

    async def get_warehouse_stocks_with_moment(
            self,
            store_id: UUID,
            moment: datetime
    ) -> ProductExpandStocksMSCollection:
        """
        Получить остатки на складе на определенный момент времени
        
        Args:
            store_id: ID склада
            moment: Момент времени
            
        Returns:
            ProductExpandStocksMSCollection: Коллекция остатков
        """
        st_api_format = MSTime.datetime_to_str_ms(moment)

        request_filter = (
            f"filter=moment={st_api_format}"
            f";store=https://api.moysklad.ru/api/remap/1.2/entity/store/{str(store_id)}"
        )
        url = f"{self._base_url}/report/stock/all?{request_filter}&expand=meta"

        response = await self._async_get(url)
        if response is None:
            raise Exception(f"Не удалось получить остатки склада {store_id} на момент {moment} из API")

        stocks_collection = ProductExpandStocksMSCollection.model_validate(response)

        return stocks_collection

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
                response.raise_for_status()
                return await response.json()

        except aiohttp.ClientError as e:
            raise Exception(f"Ошибка сети: {e}")
    
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
