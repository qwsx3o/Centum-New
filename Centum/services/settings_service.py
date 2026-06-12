"""
services/settings_service.py
Чтение и запись пользовательских настроек в settings.json.
Запись реализована через паттерн Debounce (3 секунды задержки).
"""

import json
from pathlib import Path
from utils.debounce import Debounce


SETTINGS_PATH = Path(__file__).parent.parent / "config" / "settings.json"

DEFAULT_SETTINGS = {
    "profile": {
        "family_members": 1,       # Количество членов семьи (источников дохода)
    },
    "app": {
        "currency": "₽",
        "dark_mode": True,
    },
}


class SettingsService:
    """
    Управляет пользовательскими настройками.
    _data хранится в памяти; на диск пишем через Debounce.
    """

    def __init__(self):
        self._data: dict = {}
        self._debounced_save = Debounce(self._write_to_disk, delay=3.0)
        self._load()

    # ─── Публичный API ───────────────────────────────────────────────────────

    def get(self, *keys: str, default=None):
        """
        Читает вложенное значение по цепочке ключей.
        Пример: settings.get("profile", "family_members") → 1
        """
        node = self._data
        for key in keys:
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return node

    def set(self, *keys_and_value) -> None:
        """
        Устанавливает вложенное значение. Последний аргумент — значение.
        Пример: settings.set("profile", "family_members", 3)
        Запись на диск откладывается на 3 секунды.
        """
        if len(keys_and_value) < 2:
            raise ValueError("Нужно передать хотя бы один ключ и значение")

        *keys, value = keys_and_value
        node = self._data
        for key in keys[:-1]:
            node = node.setdefault(key, {})
        node[keys[-1]] = value

        # Откладываем запись — не сразу
        self._debounced_save()

    def save_now(self) -> None:
        """Немедленно сохраняет настройки, игнорируя задержку Debounce."""
        self._debounced_save.flush()

    def get_all(self) -> dict:
        """Возвращает копию всех настроек."""
        return dict(self._data)

    # Удобные свойства ────────────────────────────────────────────────────────

    @property
    def family_members(self) -> int:
        return self.get("profile", "family_members", default=1)

    @family_members.setter
    def family_members(self, value: int) -> None:
        self.set("profile", "family_members", max(1, int(value)))

    @property
    def currency(self) -> str:
        return self.get("app", "currency", default="₽")

    # ─── Внутренние методы ───────────────────────────────────────────────────

    def _load(self) -> None:
        """Загружает настройки с диска или создаёт файл с дефолтами."""
        SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

        if SETTINGS_PATH.exists():
            try:
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                # Мержим с дефолтами, чтобы новые ключи появились автоматически
                self._data = self._deep_merge(DEFAULT_SETTINGS, loaded)
            except (json.JSONDecodeError, OSError):
                self._data = dict(DEFAULT_SETTINGS)
                self._write_to_disk()
        else:
            self._data = dict(DEFAULT_SETTINGS)
            self._write_to_disk()

    def _write_to_disk(self) -> None:
        """Пишет текущее состояние _data на диск."""
        try:
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"[SettingsService] Ошибка записи настроек: {e}")

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        """Рекурсивно мержит override поверх base, сохраняя новые ключи из base."""
        result = dict(base)
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = SettingsService._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
