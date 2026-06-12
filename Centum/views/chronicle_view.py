"""
views/chronicle_view.py — «Хроника»: история и дашборд по месяцам.

Структура экрана:
  ┌──────────────────────────────────┐
  │  ХРОНИКА                         │  ← заголовок
  ├──────────────────────────────────┤
  │  ‹  Март 2026  ›                 │  ← навигатор месяца
  ├────────────┬─────────┬───────────┤
  │  Доход     │ Капитал │  Расходы  │  ← дашборд-чипсы
  ├──────────────────────────────────┤
  │  [карточки транзакций по дням]   │  ← ListView
  └──────────────────────────────────┘

Интеграция в core.py:
  1. from views.chronicle_view import ChronicleView
  2. self._chr = ChronicleView(self._fin, self._set)
  3. self._views = [self._mv, self._hv, self._chr, self._sv]
  4. Добавить NavigationBarDestination с иконкой ft.Icons.CALENDAR_MONTH
"""

from datetime import date
from collections import defaultdict

import flet as ft
from utils.theme import C, FS, SP, R
from models.transaction import (
    get_monthly_summary,
    get_transactions_for_month,
)

# Локализованные названия месяцев (без сторонних зависимостей)
_MONTHS_RU = [
    "", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
]
_MONTHS_GEN = [
    "", "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря",
]


def _month_label(year: int, month: int) -> str:
    return f"{_MONTHS_RU[month]} {year}"


def _day_label(date_str: str) -> str:
    """'2026-03-15' → '15 марта'"""
    try:
        d = date.fromisoformat(date_str)
        return f"{d.day} {_MONTHS_GEN[d.month]}"
    except Exception:
        return date_str


# ─────────────────────────────────────────────────────────────────────────────
class ChronicleView:
    """
    Экран «Хроника» — финансовая история с навигацией по месяцам.
    Совместим с паттерном .container / .refresh() всего приложения.
    """

    def __init__(self, fin, svc):
        self._fin = fin
        self._svc = svc

        # Текущий отображаемый месяц
        today = date.today()
        self._year  = today.year
        self._month = today.month

        # ── Навигатор месяца ──────────────────────────────────────────────────
        self._month_label = ft.Text(
            _month_label(self._year, self._month),
            color=C.TEXT, size=FS.LG, weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
            expand=True,
        )
        self._btn_prev = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            icon_color=C.ACCENT, icon_size=28,
            on_click=self._prev_month,
            style=ft.ButtonStyle(
                overlay_color={ft.ControlState.HOVERED: "#22C9A84C"},
            ),
        )
        self._btn_next = ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT,
            icon_color=C.ACCENT, icon_size=28,
            on_click=self._next_month,
            style=ft.ButtonStyle(
                overlay_color={ft.ControlState.HOVERED: "#22C9A84C"},
            ),
        )

        # ── Дашборд ───────────────────────────────────────────────────────────
        self._d_income  = ft.Text("0 ₽", color=C.INCOME,   size=FS.MD, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
        self._d_capital = ft.Text("0 ₽", color=C.CAPITAL,  size=FS.MD, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
        self._d_expense = ft.Text("0 ₽", color=C.EXPENSE,  size=FS.MD, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)

        # ── Список транзакций ─────────────────────────────────────────────────
        self._list = ft.ListView(
            controls=[], expand=True, spacing=SP.XS,
            padding=ft.Padding(left=SP.MD, right=SP.MD, top=SP.XS, bottom=SP.LG),
        )
        self._empty = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.CALENDAR_MONTH, color=C.MUTED, size=52),
                ft.Text("В этом месяце операций нет", color=C.MUTED, size=FS.MD),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=SP.SM),
            alignment=ft.Alignment(0, 0), expand=True,
        )

        # ── Сборка layout ─────────────────────────────────────────────────────
        self.container = ft.Column(
            controls=[
                # Заголовок
                ft.Container(
                    content=ft.Text(
                        "ХРОНИКА", color=C.ACCENT, size=FS.LG,
                        weight=ft.FontWeight.BOLD,
                        style=ft.TextStyle(letter_spacing=4),
                    ),
                    alignment=ft.Alignment(0, 0),
                    padding=ft.Padding(left=0, right=0, top=SP.MD, bottom=SP.XS),
                ),

                # Навигатор месяца
                ft.Container(
                    content=ft.Row(
                        controls=[self._btn_prev, self._month_label, self._btn_next],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    bgcolor=C.SURFACE,
                    border_radius=R.MD,
                    margin=ft.Margin(left=SP.MD, right=SP.MD, top=0, bottom=0),
                ),

                # Дашборд-чипсы
                ft.Container(
                    content=ft.Row(controls=[
                        self._chip(self._d_income,  "Доход"),
                        self._chip(self._d_capital, "Капитал"),
                        self._chip(self._d_expense, "Расходы"),
                    ], spacing=SP.SM),
                    padding=ft.Padding(left=SP.MD, right=SP.MD, top=SP.SM, bottom=0),
                ),

                # Разделитель
                ft.Container(
                    height=1, bgcolor=C.DIVIDER,
                    margin=ft.Margin(left=SP.MD, right=SP.MD, top=SP.SM, bottom=0),
                ),

                # Список / заглушка
                self._empty,
                self._list,
            ],
            expand=True,
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Публичный метод — вызывается AppController при переходе на вкладку
    # ─────────────────────────────────────────────────────────────────────────

    def refresh(self):
        self._reload()
        if self.container.page:
            self.container.page.update()

    # ─────────────────────────────────────────────────────────────────────────
    # Навигация по месяцам
    # ─────────────────────────────────────────────────────────────────────────

    def _prev_month(self, e):
        if self._month == 1:
            self._month = 12
            self._year -= 1
        else:
            self._month -= 1
        self._reload()
        e.page.update()

    def _next_month(self, e):
        # Запрещаем переход в будущее
        today = date.today()
        if self._year >= today.year and self._month >= today.month:
            return
        if self._month == 12:
            self._month = 1
            self._year += 1
        else:
            self._month += 1
        self._reload()
        e.page.update()

    # ─────────────────────────────────────────────────────────────────────────
    # Загрузка данных
    # ─────────────────────────────────────────────────────────────────────────

    def _reload(self):
        cur = self._svc.currency

        # Обновляем лейбл месяца
        self._month_label.value = _month_label(self._year, self._month)

        # Затемняем кнопку «вперёд» если уже текущий месяц
        today = date.today()
        at_present = (self._year >= today.year and self._month >= today.month)
        self._btn_next.icon_color = C.MUTED if at_present else C.ACCENT

        # Дашборд
        summary = get_monthly_summary(self._year, self._month)
        self._d_income.value  = f"{summary['total_income']:,.0f} {cur}"
        self._d_capital.value = f"{summary['total_capital']:,.0f} {cur}"
        self._d_expense.value = f"{summary['total_expenses']:,.0f} {cur}"

        # Список транзакций
        txs = get_transactions_for_month(self._year, self._month)

        if not txs:
            self._empty.visible = True
            self._list.visible  = False
            return

        self._empty.visible = False
        self._list.visible  = True

        # Группируем по дню
        groups: dict[str, list] = defaultdict(list)
        for tx in txs:
            day_key = tx.created_at[:10]   # 'YYYY-MM-DD'
            groups[day_key].append(tx)

        controls = []
        for day_key in sorted(groups.keys(), reverse=True):
            # Заголовок дня
            controls.append(self._day_header(day_key, groups[day_key], cur))
            # Карточки транзакций
            for tx in groups[day_key]:
                controls.append(self._tx_card(tx, cur))

        self._list.controls = controls

    # ─────────────────────────────────────────────────────────────────────────
    # UI-компоненты
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _chip(val_ctrl, label: str) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    val_ctrl,
                    ft.Text(label, color=C.SUBTEXT, size=FS.XS,
                            text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2, tight=True,
            ),
            bgcolor=C.SURFACE, border_radius=R.SM,
            padding=ft.Padding(left=SP.SM, right=SP.SM, top=SP.SM, bottom=SP.SM),
            expand=True,
        )

    def _day_header(self, day_key: str, txs: list, cur: str) -> ft.Container:
        """Заголовок группы дня: дата слева, нетто-итог справа."""
        net = sum(
            tx.amount if tx.type == "income"
            else -tx.amount if tx.type == "expense"
            else 0
            for tx in txs
        )
        net_color = C.INCOME if net >= 0 else C.EXPENSE
        net_sign  = "+" if net >= 0 else ""

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(_day_label(day_key), color=C.SUBTEXT,
                            size=FS.SM, weight=ft.FontWeight.W_500),
                    ft.Text(f"{net_sign}{net:,.0f} {cur}",
                            color=net_color, size=FS.SM,
                            weight=ft.FontWeight.W_500),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.Padding(left=SP.XS, right=SP.XS, top=SP.SM, bottom=SP.XS),
        )

    def _tx_card(self, tx, cur: str) -> ft.Container:
        """Карточка одной транзакции."""
        type_map = {
            "income":  (C.INCOME,  ft.Icons.ARROW_DOWNWARD, "+"),
            "expense": (C.EXPENSE, ft.Icons.ARROW_UPWARD,   "−"),
            "capital": (C.CAPITAL, ft.Icons.SAVINGS,        "→"),
        }
        color, icon, sign = type_map.get(tx.type, (C.SUBTEXT, ft.Icons.CIRCLE, ""))
        time_str = tx.created_at[11:16] if len(tx.created_at) >= 16 else ""

        return ft.Container(
            content=ft.Row(
                controls=[
                    # Иконка типа
                    ft.Container(
                        content=ft.Icon(icon, color=color, size=16),
                        bgcolor=C.BG, border_radius=R.FULL,
                        width=34, height=34,
                        alignment=ft.Alignment(0, 0),
                    ),
                    # Описание
                    ft.Column(
                        controls=[
                            ft.Text(tx.category_name, color=C.TEXT,
                                    size=FS.SM, weight=ft.FontWeight.W_500),
                            ft.Text(
                                f"{tx.note}  ·  {time_str}" if tx.note else time_str,
                                color=C.MUTED, size=FS.XS,
                            ),
                        ],
                        expand=True, spacing=2, tight=True,
                    ),
                    # Сумма
                    ft.Text(
                        f"{sign}{tx.amount:,.2f} {cur}",
                        color=color, size=FS.SM,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=SP.SM,
            ),
            bgcolor=C.SURFACE,
            border_radius=R.SM,
            padding=ft.Padding(left=SP.SM, right=SP.SM, top=SP.XS, bottom=SP.XS),
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN),
        )
