"""
models/transaction.py
ORM-модель транзакции. Только CRUD-запросы — никакой бизнес-логики.
"""

from dataclasses import dataclass
from typing import Optional
from .database import get_connection


@dataclass
class Transaction:
    id: int
    type: str          # 'income' | 'expense' | 'capital'
    amount: float
    category_id: int
    category_name: str  # денормализовано для удобства отображения
    note: str
    created_at: str


# ─── Чтение ──────────────────────────────────────────────────────────────────

def get_all_transactions(limit: int = 100, offset: int = 0) -> list[Transaction]:
    conn = get_connection()
    rows = conn.execute("""
        SELECT t.*, c.name AS category_name
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        ORDER BY t.created_at DESC
        LIMIT ? OFFSET ?
    """, (limit, offset)).fetchall()
    conn.close()
    return [_row_to_transaction(r) for r in rows]


def get_transactions_by_type(tx_type: str) -> list[Transaction]:
    conn = get_connection()
    rows = conn.execute("""
        SELECT t.*, c.name AS category_name
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.type = ?
        ORDER BY t.created_at DESC
    """, (tx_type,)).fetchall()
    conn.close()
    return [_row_to_transaction(r) for r in rows]


def get_summary() -> dict:
    """
    Возвращает агрегированные суммы для главного экрана:
    - total_income: сумма всех доходов
    - total_capital: сумма всех капитал-транзакций (10%)
    - total_expenses: сумма всех расходов
    - available: доступно к распределению (90% дохода - расходы)
    """
    conn = get_connection()

    total_income = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type = 'income'"
    ).fetchone()[0]

    total_capital = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type = 'capital'"
    ).fetchone()[0]

    total_expenses = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type = 'expense'"
    ).fetchone()[0]

    conn.close()

    spendable = total_income * 0.9  # 90% от всех доходов
    available = spendable - total_expenses

    return {
        "total_income":   round(total_income, 2),
        "total_capital":  round(total_capital, 2),
        "total_expenses": round(total_expenses, 2),
        "spendable":      round(spendable, 2),
        "available":      round(available, 2),
    }


def get_expenses_by_category() -> list[dict]:
    """Суммы расходов по категориям для PieChart."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT c.name, c.color, SUM(t.amount) AS total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.type = 'expense'
        GROUP BY c.id
        ORDER BY total DESC
    """).fetchall()
    conn.close()
    return [{"name": r["name"], "color": r["color"], "total": r["total"]} for r in rows]


# ─── Запись ──────────────────────────────────────────────────────────────────

def create_transaction(
    tx_type: str,
    amount: float,
    category_id: int,
    note: str = ""
) -> Transaction:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO transactions (type, amount, category_id, note) VALUES (?, ?, ?, ?)",
        (tx_type, round(amount, 2), category_id, note.strip())
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    # Перечитываем с JOIN для получения category_name
    conn = get_connection()
    row = conn.execute("""
        SELECT t.*, c.name AS category_name
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.id = ?
    """, (new_id,)).fetchone()
    conn.close()
    return _row_to_transaction(row)


def delete_transaction(tx_id: int) -> bool:
    conn = get_connection()
    conn.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
    conn.commit()
    conn.close()
    return True


# ─── Вспомогательные ─────────────────────────────────────────────────────────

def _row_to_transaction(row) -> Transaction:
    return Transaction(
        id=row["id"],
        type=row["type"],
        amount=row["amount"],
        category_id=row["category_id"],
        category_name=row["category_name"],
        note=row["note"] or "",
        created_at=row["created_at"],
    )

# ─── Хроника: запросы по месяцу ──────────────────────────────────────────────

def get_monthly_summary(year: int, month: int) -> dict:
    """
    Возвращает агрегаты за конкретный месяц:
      total_income   — сумма доходов
      total_capital  — сумма капитала (10%)
      total_expenses — сумма расходов
    """
    ym = f"{year:04d}-{month:02d}"
    conn = get_connection()

    def _sum(tx_type: str) -> float:
        return conn.execute(
            """SELECT COALESCE(SUM(amount), 0)
               FROM transactions
               WHERE type = ?
                 AND strftime('%Y-%m', created_at) = ?""",
            (tx_type, ym),
        ).fetchone()[0]

    result = {
        "total_income":   round(_sum("income"),  2),
        "total_capital":  round(_sum("capital"), 2),
        "total_expenses": round(_sum("expense"), 2),
    }
    conn.close()
    return result


def get_transactions_for_month(year: int, month: int) -> list["Transaction"]:
    """
    Все транзакции за указанный месяц, отсортированные от новых к старым.
    Используется в ChronicleView для построения сгруппированного списка.
    """
    ym = f"{year:04d}-{month:02d}"
    conn = get_connection()
    rows = conn.execute(
        """SELECT t.*, c.name AS category_name
           FROM transactions t
           JOIN categories c ON t.category_id = c.id
           WHERE strftime('%Y-%m', t.created_at) = ?
           ORDER BY t.created_at DESC""",
        (ym,),
    ).fetchall()
    conn.close()
    return [_row_to_transaction(r) for r in rows]


def get_days_with_transactions(year: int, month: int) -> list[dict]:
    """
    Возвращает список дней с агрегатами за каждый день:
      date  — строка 'YYYY-MM-DD'
      income, capital, expense — суммы по типам
    Используется для «дневного дашборда» в ChroницleView.
    """
    ym = f"{year:04d}-{month:02d}"
    conn = get_connection()
    rows = conn.execute(
        """SELECT
               strftime('%Y-%m-%d', created_at)  AS date,
               SUM(CASE WHEN type='income'  THEN amount ELSE 0 END) AS income,
               SUM(CASE WHEN type='capital' THEN amount ELSE 0 END) AS capital,
               SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) AS expense,
               COUNT(*) AS tx_count
           FROM transactions
           WHERE strftime('%Y-%m', created_at) = ?
           GROUP BY date
           ORDER BY date DESC""",
        (ym,),
    ).fetchall()
    conn.close()
    return [
        {
            "date":     r["date"],
            "income":   round(r["income"],  2),
            "capital":  round(r["capital"], 2),
            "expense":  round(r["expense"], 2),
            "tx_count": r["tx_count"],
        }
        for r in rows
    ]

