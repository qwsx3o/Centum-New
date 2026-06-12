"""
services/backup_service.py
Локальное резервное копирование: centum.db + settings.json.
Никакой облачной синхронизации — только локальный файл архива.
"""

import shutil
import zipfile
from pathlib import Path
from datetime import datetime


DB_PATH       = Path(__file__).parent.parent / "data" / "centum.db"
SETTINGS_PATH = Path(__file__).parent.parent / "config" / "settings.json"
BACKUP_DIR    = Path(__file__).parent.parent / "data" / "backups"


class BackupService:

    def create_backup(self, destination_dir: str | None = None) -> Path:
        """
        Создаёт ZIP-архив с centum.db и settings.json.
        Если destination_dir не указан — сохраняет в data/backups/.
        Возвращает путь к созданному архиву.
        """
        target_dir = Path(destination_dir) if destination_dir else BACKUP_DIR
        target_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = target_dir / f"centum_backup_{timestamp}.zip"

        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
            if DB_PATH.exists():
                zf.write(DB_PATH, arcname="centum.db")
            if SETTINGS_PATH.exists():
                zf.write(SETTINGS_PATH, arcname="settings.json")

        return archive_path

    def restore_backup(self, archive_path: str) -> bool:
        """
        Восстанавливает данные из ZIP-архива.
        Перезаписывает текущие centum.db и settings.json.
        Возвращает True при успехе.
        """
        archive = Path(archive_path)
        if not archive.exists() or not zipfile.is_zipfile(archive):
            return False

        try:
            with zipfile.ZipFile(archive, "r") as zf:
                names = zf.namelist()
                if "centum.db" in names:
                    zf.extract("centum.db", DB_PATH.parent)
                if "settings.json" in names:
                    zf.extract("settings.json", SETTINGS_PATH.parent)
            return True
        except Exception as e:
            print(f"[BackupService] Ошибка восстановления: {e}")
            return False

    def list_backups(self) -> list[dict]:
        """Возвращает список доступных бэкапов с метаданными."""
        if not BACKUP_DIR.exists():
            return []

        result = []
        for f in sorted(BACKUP_DIR.glob("centum_backup_*.zip"), reverse=True):
            stat = f.stat()
            result.append({
                "path":     str(f),
                "name":     f.name,
                "size_kb":  round(stat.st_size / 1024, 1),
                "created":  datetime.fromtimestamp(stat.st_mtime).strftime("%d.%m.%Y %H:%M"),
            })
        return result
    def clear_all_data(self) -> Path:
        """
        Сначала создаёт резервную копию,
        затем очищает все транзакции и несистемные категории из БД,
        а также сбрасывает settings.json.
        Возвращает путь к созданному бэкапу.
        """
        import json
        from models.database import get_connection

        # 1. Бэкап ПЕРЕД очисткой
        backup_path = self.create_backup()

        # 2. Очищаем транзакции
        conn = get_connection()
        conn.execute("DELETE FROM transactions")
        # Удаляем пользовательские категории (системные не трогаем)
        conn.execute("DELETE FROM categories WHERE is_system = 0")
        conn.commit()
        conn.close()

        # 3. Сбрасываем настройки
        default_settings = {"family_members": 1, "currency": "₽", "theme": "dark"}
        SETTINGS_PATH.write_text(
            json.dumps(default_settings, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        return backup_path

