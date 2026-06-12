"""
models/database.py
Инициализация SQLite-соединения с PRAGMA WAL, создание схемы таблиц.
Единственное место, где происходит прямое взаимодействие с файлом centum.db.
"""

import sqlite3
import os
from pathlib import Path


# Путь к базе данных относительно корня проекта
DB_PATH = Path(__file__).parent.parent / "data" / "centum.db"


def get_connection() -> sqlite3.Connection:
    """
    Возвращает соединение с БД с включённым WAL-режимом.
    Row factory позволяет обращаться к полям по имени колонки.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    # Критично: WAL снижает износ накопителя и улучшает конкурентность
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def initialize_schema() -> None:
    """
    Создаёт все таблицы при первом запуске (если не существуют).
    Безопасно вызывать при каждом старте приложения.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # ── Категории ─────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            type        TEXT    NOT NULL CHECK(type IN ('income', 'expense', 'system')),
            is_system   INTEGER NOT NULL DEFAULT 0,   -- 1 = системная, нельзя удалить
            color       TEXT    DEFAULT NULL,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
        );
    """)

    # ── Транзакции ────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            type        TEXT    NOT NULL CHECK(type IN ('income', 'expense', 'capital')),
            amount      REAL    NOT NULL CHECK(amount > 0),
            category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
            note        TEXT    DEFAULT '',
            created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
        );
    """)

    # ── Индексы для быстрой выборки истории ──────────────────────────────────
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_transactions_created_at
        ON transactions(created_at DESC);
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_transactions_type
        ON transactions(type);
    """)

    conn.commit()

    # ── Системные категории (вставляем при отсутствии) ────────────────────────
    _seed_system_categories(cursor, conn)

    conn.close()


def _seed_system_categories(cursor: sqlite3.Cursor, conn: sqlite3.Connection) -> None:
    """
    Вставляет системные категории, если их ещё нет.
    Системные категории нельзя редактировать или удалять из UI.
    """
    system_cats = [
        # (name, type, color)
        ("Капитал (Моё богатство)", "system", "#C9A84C"),  # 10% — правило Аркада
        ("Основной доход",          "income",  "#4CAF50"),
    ]

    for name, cat_type, color in system_cats:
        cursor.execute("""
            INSERT OR IGNORE INTO categories (name, type, is_system, color)
            VALUES (?, ?, 1, ?);
        """, (name, cat_type, color))

    conn.commit()
