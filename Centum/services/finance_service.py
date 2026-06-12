"""
services/finance_service.py
Бизнес-логика финансового ядра.
Правило Аркада: при добавлении дохода 10% автоматически уходят в «Капитал».
Никакого кода Flet здесь нет — только чистый Python.
"""

from models.category import get_category_by_name
from models.transaction import (
    create_transaction,
    get_summary,
    get_expenses_by_category,
    get_all_transactions,
    delete_transaction,
    Transaction,
)


CAPITAL_CATEGORY_NAME = "Капитал (Моё богатство)"
CAPITAL_RATE = 0.10   # 10% — жёстко зафиксировано правилами книги


class FinanceService:
    """
    Единственный сервис, который знает о финансовых правилах приложения.
    Все Views работают только через него, не трогая models напрямую.
    """

    # ─── Доходы ──────────────────────────────────────────────────────────────

    def add_income(
        self,
        amount: float,
        category_id: int,
        note: str = ""
    ) -> dict:
        """
        Добавляет доход и автоматически создаёт две транзакции:
        1. income — полная сумма в выбранную категорию
        2. capital — 10% от суммы в системную категорию «Капитал»

        Возвращает словарь с обеими транзакциями и рассчитанными суммами.
        """
        if amount <= 0:
            raise ValueError("Сумма дохода должна быть больше нуля")

        capital_amount = round(amount * CAPITAL_RATE, 2)
        available_amount = round(amount - capital_amount, 2)

        # Транзакция дохода
        income_tx = create_transaction(
            tx_type="income",
            amount=amount,
            category_id=category_id,
            note=note,
        )

        # Транзакция капитала (автоматическая, системная)
        capital_category = get_category_by_name(CAPITAL_CATEGORY_NAME)
        if not capital_category:
            raise RuntimeError(
                f"Системная категория '{CAPITAL_CATEGORY_NAME}' не найдена. "
                "Пересоздайте базу данных."
            )

        capital_tx = create_transaction(
            tx_type="capital",
            amount=capital_amount,
            category_id=capital_category.id,
            note=f"Авто: 10% от дохода #{income_tx.id}",
        )

        return {
            "income_tx":       income_tx,
            "capital_tx":      capital_tx,
            "income_amount":   amount,
            "capital_amount":  capital_amount,
            "available_amount": available_amount,
        }

    # ─── Расходы ─────────────────────────────────────────────────────────────

    def add_expense(
        self,
        amount: float,
        category_id: int,
        note: str = ""
    ) -> Transaction:
        """
        Добавляет расход. Проверяет, что сумма не превышает «Доступно к распределению».
        Raises ValueError если баланс недостаточен.
        """
        if amount <= 0:
            raise ValueError("Сумма расхода должна быть больше нуля")

        summary = self.get_summary()
        if amount > summary["available"]:
            raise ValueError(
                f"Недостаточно средств. "
                f"Доступно: {summary['available']:.2f}, "
                f"запрошено: {amount:.2f}"
            )

        return create_transaction(
            tx_type="expense",
            amount=amount,
            category_id=category_id,
            note=note,
        )

    # ─── Аналитика ───────────────────────────────────────────────────────────

    def get_summary(self) -> dict:
        """
        Возвращает текущее финансовое состояние для главного экрана.
        Ключи: total_income, total_capital, total_expenses, spendable, available.
        """
        return get_summary()

    def get_pie_chart_data(self) -> list[dict]:
        """
        Данные для PieChart на главном экране.
        Возвращает сегменты: Капитал (10%), расходы по категориям, Доступно.
        """
        summary = self.get_summary()
        if summary["total_income"] == 0:
            return []

        total = summary["total_income"]
        segments = []

        # Капитал — всегда первый
        segments.append({
            "name":    "Капитал",
            "amount":  summary["total_capital"],
            "percent": round(summary["total_capital"] / total * 100, 1),
            "color":   "#C9A84C",
        })

        # Расходы по категориям
        for cat in get_expenses_by_category():
            segments.append({
                "name":    cat["name"],
                "amount":  cat["total"],
                "percent": round(cat["total"] / total * 100, 1),
                "color":   cat["color"] or "#9E9E9E",
            })

        # Доступно к распределению
        if summary["available"] > 0:
            segments.append({
                "name":    "Доступно",
                "amount":  summary["available"],
                "percent": round(summary["available"] / total * 100, 1),
                "color":   "#42A5F5",
            })

        return segments

    def get_history(self, limit: int = 100) -> list[Transaction]:
        return get_all_transactions(limit=limit)

    def delete_transaction(self, tx_id: int) -> bool:
        return delete_transaction(tx_id)
