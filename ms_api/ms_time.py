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

    # Форматы строк для MS API
    _MS_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    _MS_DATETIME_FORMAT_WITH_MS = "%Y-%m-%d %H:%M:%S.%f"

    @classmethod
    def set_timezone(cls, tz_name: str) -> None:
        """Установка часового пояса проекта"""
        cls._project_timezone = ZoneInfo(tz_name)

    @classmethod
    def datetime_to_str_ms(cls, dt: datetime, with_ms: bool = False) -> str:
        """
        Конвертация datetime в строку MS API.
        Время форматируется в московском часовом поясе.
        
        Args:
            dt: datetime объект для конвертации
            with_ms: Включить микросекунды
            
        Returns:
            str: Строка в формате MS API (yyyy-mm-dd HH:MM:SS или с микросекундами)
        """
        # Убеждаемся, что datetime в московском часовом поясе
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=cls._project_timezone)
        else:
            dt = dt.astimezone(cls._project_timezone)
        
        fmt = cls._MS_DATETIME_FORMAT_WITH_MS if with_ms else cls._MS_DATETIME_FORMAT
        return dt.strftime(fmt)

    @classmethod
    def datetime_from_str_ms(cls, val: str) -> datetime:
        """
        Парсинг строки MS API в datetime.
        Время интерпретируется как московское.
        
        Args:
            val: Строка в формате MS API (yyyy-mm-dd HH:MM:SS или с микросекундами)
            
        Returns:
            datetime: datetime объект с московским часовым поясом
        """
        # Пробуем оба формата MS (с микросекундами и без)
        try:
            dt = datetime.strptime(val, cls._MS_DATETIME_FORMAT_WITH_MS)
        except ValueError:
            dt = datetime.strptime(val, cls._MS_DATETIME_FORMAT)
        return dt.replace(tzinfo=cls._project_timezone)

