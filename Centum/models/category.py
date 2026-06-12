"""
models/category.py
ORM-модель категории. Только CRUD-запросы — никакой бизнес-логики.
"""

from dataclasses import dataclass
from typing import Optional
from .database import get_connection


@dataclass
class Category:
    id: int
    name: str
    type: str          # 'income' | 'expense' | 'system'
    is_system: bool
    color: Optional[str]
    created_at: str


# ─── Чтение ──────────────────────────────────────────────────────────────────

def get_all_categories() -> list[Category]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM categories ORDER BY is_system DESC, name ASC"
    ).fetchall()
    conn.close()
    return [_row_to_category(r) for r in rows]


def get_categories_by_type(cat_type: str) -> list[Category]:
    """cat_type: 'income' | 'expense' | 'system'"""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM categories WHERE type = ? ORDER BY is_system DESC, name ASC",
        (cat_type,)
    ).fetchall()
    conn.close()
    return [_row_to_category(r) for r in rows]


def get_category_by_id(category_id: int) -> Optional[Category]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM categories WHERE id = ?", (category_id,)
    ).fetchone()
    conn.close()
    return _row_to_category(row) if row else None


def get_category_by_name(name: str) -> Optional[Category]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM categories WHERE name = ?", (name,)
    ).fetchone()
    conn.close()
    return _row_to_category(row) if row else None


# ─── Запись ──────────────────────────────────────────────────────────────────

def create_category(name: str, cat_type: str, color: Optional[str] = None) -> Category:
    """Создаёт пользовательскую категорию. is_system=0 всегда."""
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO categories (name, type, is_system, color) VALUES (?, ?, 0, ?)",
        (name.strip(), cat_type, color)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return get_category_by_id(new_id)


def delete_category(category_id: int) -> bool:
    """
    Удаляет категорию. Возвращает False если категория системная
    или к ней привязаны транзакции.
    """
    cat = get_category_by_id(category_id)
    if not cat or cat.is_system:
        return False

    conn = get_connection()
    # Проверяем наличие транзакций
    count = conn.execute(
        "SELECT COUNT(*) FROM transactions WHERE category_id = ?", (category_id,)
    ).fetchone()[0]

    if count > 0:
        conn.close()
        return False  # Нельзя удалить — есть история транзакций

    conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    conn.commit()
    conn.close()
    return True


# ─── Вспомогательные ─────────────────────────────────────────────────────────

def _row_to_category(row) -> Category:
    return Category(
        id=row["id"],
        name=row["name"],
        type=row["type"],
        is_system=bool(row["is_system"]),
        color=row["color"],
        created_at=row["created_at"],
    )
