from __future__ import annotations

from typing import Annotated, Any, Callable
from uuid import UUID

from pydantic import BaseModel, Field, BeforeValidator

from moy_sklad_api.models.metadata import MetaModel
from moy_sklad_api.utils import parse_rows_as, extract_id


class TurnoverReportMetricsModel(BaseModel):
    """Показатели onPeriodStart / onPeriodEnd / income / outcome (сумма в копейках, количество)."""

    model_config = {"populate_by_name": True, "extra": "ignore"}

    cost_sum: Annotated[float, Field(validation_alias="sum", serialization_alias="sum")]
    quantity: float


class TurnoverReportAssortmentModel(BaseModel):
    """Краткое представление товара или модификации в отчёте обороты (с детализацией по складам)."""

    model_config = {"populate_by_name": True, "extra": "ignore"}

    id: Annotated[UUID, Field(validation_alias="meta"), BeforeValidator(extract_id)]
    meta: MetaModel
    name: str
    article: str | None = None
    code: str | None = None


class TurnoverReportStoreRefModel(BaseModel):
    """Ссылка на склад в строке детализации."""

    model_config = {"populate_by_name": True, "extra": "ignore"}

    id: Annotated[UUID, Field(validation_alias="meta"), BeforeValidator(extract_id)]
    meta: MetaModel
    name: str | None = None


class TurnoverReportStockByStoreLineModel(BaseModel):
    """Одна строка детализации оборотов по складу."""

    model_config = {"populate_by_name": True, "extra": "ignore"}

    store: TurnoverReportStoreRefModel
    on_period_start: Annotated[
        TurnoverReportMetricsModel,
        Field(validation_alias="onPeriodStart", serialization_alias="onPeriodStart"),
    ]
    on_period_end: Annotated[
        TurnoverReportMetricsModel,
        Field(validation_alias="onPeriodEnd", serialization_alias="onPeriodEnd"),
    ]
    income: TurnoverReportMetricsModel
    outcome: TurnoverReportMetricsModel


def _parse_stock_by_store(value: Any) -> list[TurnoverReportStockByStoreLineModel]:
    if value is None:
        return []
    if isinstance(value, list):
        return [TurnoverReportStockByStoreLineModel.model_validate(item) for item in value]
    if isinstance(value, dict):
        return [TurnoverReportStockByStoreLineModel.model_validate(value)]
    msg = f"stockByStore ожидается list или dict, получено {type(value).__name__}"
    raise TypeError(msg)


class TurnoverReportByStoreRowModel(BaseModel):
    """Строка отчёта «Обороты по товару с детализацией по складам» (/report/turnover/bystore)."""

    model_config = {"populate_by_name": True, "extra": "ignore"}

    assortment: TurnoverReportAssortmentModel
    stock_by_store: Annotated[
        list[TurnoverReportStockByStoreLineModel],
        Field(validation_alias="stockByStore", serialization_alias="stockByStore"),
        BeforeValidator(_parse_stock_by_store),
    ]


parse_turnover_report_by_store_rows: Callable[
    [Any], list[TurnoverReportByStoreRowModel]
] = parse_rows_as(TurnoverReportByStoreRowModel)
