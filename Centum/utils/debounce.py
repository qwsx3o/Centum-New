"""
utils/debounce.py
Универсальная реализация паттерна Debounce на asyncio.
Используется в settings_service.py для отложенного сохранения настроек.
"""

import asyncio
from typing import Callable, Any


class Debounce:
    """
    Откладывает вызов функции на `delay` секунд после последнего обращения.
    Если за это время поступает новый вызов — таймер сбрасывается.
    """

    def __init__(self, func: Callable, delay: float = 3.0):
        self._func = func
        self._delay = delay
        self._task: asyncio.Task | None = None

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        if self._task is not None:
            self._task.cancel()
        self._task = asyncio.ensure_future(self._delayed(*args, **kwargs))

    async def _delayed(self, *args: Any, **kwargs: Any) -> None:
        await asyncio.sleep(self._delay)
        self._func(*args, **kwargs)
        self._task = None

    def flush(self) -> None:
        """Немедленно отменяет ожидание и вызывает функцию прямо сейчас."""
        if self._task is not None:
            self._task.cancel()
            self._task = None
        self._func()

    def cancel(self) -> None:
        """Отменяет отложенный вызов без выполнения."""
        if self._task is not None:
            self._task.cancel()
            self._task = None
