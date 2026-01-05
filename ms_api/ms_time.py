"""
Утилиты для работы с датой и временем в форматах MS API
"""

from datetime import datetime
from zoneinfo import ZoneInfo


class MSTime:
    """
    Класс для работы с датами и временем в форматах МойСклад API
    """

    # Часовой пояс по умолчанию
    _project_timezone = ZoneInfo('Europe/Moscow')

    @classmethod
    def set_timezone(cls, tz_name: str) -> None:
        """Установка часового пояса проекта"""
        cls._project_timezone = ZoneInfo(tz_name)

    @classmethod
    def datetime_to_str_ms(cls, dt: datetime) -> str:
        """
        Конвертация datetime в строку MS API.
        Время форматируется в московском часовом поясе.
        
        Args:
            dt: datetime объект для конвертации

        Returns:
            str: Строка в формате isoformat
        """
        # Убеждаемся, что datetime в московском часовом поясе
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=cls._project_timezone)
        else:
            dt = dt.astimezone(cls._project_timezone)

        return dt.isoformat()

    @classmethod
    def datetime_from_str_ms(cls, val: str) -> datetime:
        """
        Парсинг строки MS API в datetime.
        Время интерпретируется как московское.
        
        Args:
            val: Строка в формате isoformat
            
        Returns:
            datetime: datetime объект с московским часовым поясом
        """
        dt = datetime.fromisoformat(val)
        return dt.replace(tzinfo=cls._project_timezone)
