# MS API Client

Клиент для работы с API МойСклад (api.moysklad.ru).

## Установка

```bash
pip install -e .
```

Или для установки в режиме разработки:

```bash
pip install -e ".[dev]"
```

## Использование

### Базовый пример

```python
import asyncio
from datetime import datetime
from uuid import UUID
from ms_api import MoySkladAPIClient

async def main():
    # Создаем клиент
    client = MoySkladAPIClient(access_token="your_access_token")
    
    # Получаем список товаров
    products = await client.get_products()
    print(f"Найдено товаров: {len(products.items)}")
    
    # Получаем склад по ID
    warehouse_id = UUID("cc244c2d-55a8-11ed-0a80-023100027dcb")
    warehouse = await client.get_warehouse_by_id(warehouse_id)
    print(f"Склад: {warehouse.name}")
    
    # Получаем остатки на складе
    stocks = await client.get_warehouse_stocks(warehouse_id)
    print(f"Найдено позиций: {len(stocks.items)}")
    
    # Создаем перемещение
    target_store = UUID("c40606fc-cab9-11f0-0a80-0816000c4e90")
    source_store = UUID("cc244c2d-55a8-11ed-0a80-023100027dcb")
    organization = UUID("1783080e-d9e8-11ed-0a80-0145000af55f")
    
    move_result = await client.create_move(
        target_store_id=target_store,
        positions=[(product_id, 10)],
        source_store_id=source_store,
        moment=datetime.now(),
        organization_id=organization
    )
    print(f"Создано перемещение: {move_result['id']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Работа с датами

```python
from ms_api import MoySkladAPIClient
from ms_api.ms_time import MSTime
from datetime import datetime

client = MoySkladAPIClient(access_token="your_token")

# Получить остатки на определенный момент времени
moment = datetime(2025, 1, 1, 12, 0, 0)
stocks = await client.get_warehouse_stocks_with_moment(warehouse_id, moment)

# Конвертация дат
dt_str = MSTime.datetime_to_str_ms(datetime.now())
dt = MSTime.datetime_from_str_ms("2025-01-01 12:00:00")
```

## API

### MoySkladAPIClient

Основной класс для работы с API.

#### Методы

- `get_warehouse_by_ex_code(code)` - Получить склад по внешнему коду
- `get_warehouse_by_id(warehouse_id)` - Получить склад по ID
- `get_products()` - Получить список товаров
- `get_product_by_id(product_id)` - Получить товар по ID
- `get_warehouse_stocks(store_id)` - Получить текущие остатки на складе
- `get_warehouse_stocks_with_moment(store_id, moment)` - Получить остатки на момент времени
- `get_last_demand(warehouse_id, organization_id)` - Получить последнюю отгрузку
- `create_demand(...)` - Создать документ отгрузки
- `create_move(...)` - Создать документ перемещения

### Модели

Все модели находятся в модуле `ms_api.models`:

- `ProductMSModel` - Модель товара
- `ProductsMSCollection` - Коллекция товаров
- `StoreModel` - Модель склада
- `StoresCollection` - Коллекция складов
- `ProductStocksMSModel` - Модель остатков товара
- `ProductStocksMSCollection` - Коллекция остатков
- `ProductExpandStocksMSModel` - Модель остатков с метаданными
- `ProductExpandStocksMSCollection` - Коллекция остатков с метаданными

### Утилиты

- `MSTime` - Утилиты для работы с датами в форматах MS API
- `generate_metadata()` - Генерация метаданных для сущностей
- `ProductType` - Типы товаров
- `BundleType` - Типы комплектов
- `EntityType` - Типы сущностей

## Зависимости

- `aiohttp>=3.13.2` - Для асинхронных HTTP запросов
- `pydantic>=2.12.5` - Для валидации данных
- `requests>=2.32.5` - Для синхронных HTTP запросов
- `tzdata>=2025.3` - Для работы с часовыми поясами

## Лицензия

MIT

