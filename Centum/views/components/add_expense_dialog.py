"""
views/components/add_expense_dialog.py

Диалог добавления расхода с двумя психологическими WOW-механиками:

  МЕХАНИКА 1 — «Трансмутация»
    Срабатывает для категорий: Образование, Здоровье, Навыки и похожих.
    Карточка анимируется в золотой цвет, появляется вдохновляющий SnackBar.

  МЕХАНИКА 2 — «Пауза Патриция»
    Срабатывает для категорий: Развлечения, Спонтанные желания и похожих.
    3-секундная блокировка через asyncio.sleep, два выбора после паузы.

Все on_click — async для неблокирующего UI.
"""

import asyncio
import flet as ft
from utils.theme import C, FS, SP, R, tf_style
from models.category import get_categories_by_type, get_category_by_id

# ── Константы механик ─────────────────────────────────────────────────────────

# Ключевые слова для МЕХАНИКИ 1 — Трансмутация (инвестиции в себя)
TRANSMUTATION_KW = ("образование", "здоровье", "навык", "развитие", "обучение", "курс")

# Ключевые слова для МЕХАНИКИ 2 — Пауза Патриция (защита от транжирства)
PAUSE_KW = ("развлечен", "спонтан", "желани", "удовольстви", "хобби", "игр", "ресторан", "кафе")

# Золотые цвета
GOLD      = "#C9A84C"
GOLD_WARM = "#1A1500"   # тёплый тёмный фон во время анимации
GOLD_GLOW = "#FFD700"


def _classify(category_name: str) -> str:
    """
    Определяет тип механики по названию категории.
    Возвращает: 'transmutation' | 'pause' | 'normal'
    """
    n = category_name.lower()
    if any(kw in n for kw in TRANSMUTATION_KW):
        return "transmutation"
    if any(kw in n for kw in PAUSE_KW):
        return "pause"
    return "normal"


class AddExpenseDialog(ft.AlertDialog):

    def __init__(self, finance_service, on_success=None):
        self._svc = finance_service
        self._cb  = on_success

        # ── Поля ввода ────────────────────────────────────────────────────────
        self._avl    = ft.Text("", color=C.AVAILABLE, size=FS.SM,
                                weight=ft.FontWeight.W_500)
        self._amount = ft.TextField(label="Сумма",
                                    keyboard_type=ft.KeyboardType.NUMBER,
                                    prefix=ft.Text("₽  ", color=C.SUBTEXT),
                                    **tf_style())
        self._note   = ft.TextField(label="Примечание (необязательно)",
                                    max_length=100, **tf_style())
        self._cat_dd = ft.Dropdown(
            label="Категория", bgcolor=C.CARD,
            border_color=C.DIVIDER, focused_border_color=C.ACCENT,
            border_radius=R.SM,
            label_style=ft.TextStyle(color=C.SUBTEXT),
            text_style=ft.TextStyle(color=C.TEXT),
        )
        self._err = ft.Text("", color=C.EXPENSE, size=FS.SM, visible=False)

        # ── Блок Паузы Патриция (скрыт изначально) ───────────────────────────
        self._progress    = ft.ProgressRing(color=GOLD, bgcolor=C.DIVIDER,
                                             stroke_width=3, width=28,
                                             height=28, visible=False)
        self._timer_lbl   = ft.Text("", color=C.SUBTEXT, size=FS.XS,
                                    text_align=ft.TextAlign.CENTER)
        self._pause_quote = ft.Text("", color=GOLD, size=FS.SM, italic=True,
                                    text_align=ft.TextAlign.CENTER)
        self._pause_block = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(controls=[self._progress, self._timer_lbl],
                           alignment=ft.MainAxisAlignment.CENTER,
                           spacing=SP.SM),
                    self._pause_quote,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=SP.SM, tight=True,
            ),
            bgcolor=C.BG, border_radius=R.SM,
            padding=ft.Padding(left=SP.MD, right=SP.MD, top=SP.SM, bottom=SP.SM),
            visible=False,
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_IN),
        )

        # ── Кнопки ───────────────────────────────────────────────────────────
        self._btn_cancel = ft.FilledButton(
            content=ft.Text("Отмена", color=C.SUBTEXT, size=FS.MD),
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: C.SURFACE},
                shape=ft.RoundedRectangleBorder(radius=R.SM),
            ),
            on_click=lambda e: e.page.pop_dialog(),
        )
        # Главная кнопка добавления
        self._btn_add = ft.FilledButton(
            content=ft.Text("Добавить", color=C.TEXT, size=FS.MD,
                            weight=ft.FontWeight.BOLD),
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: C.EXPENSE},
                color={ft.ControlState.DEFAULT: C.TEXT},
                shape=ft.RoundedRectangleBorder(radius=R.SM),
            ),
            on_click=self._on_add_click,
        )
        # Кнопка "всё-таки потратить" после паузы
        self._btn_spend = ft.FilledButton(
            content=ft.Text("Я осознаю. Потратить.", color=C.SUBTEXT,
                            size=FS.SM),
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: C.CARD},
                shape=ft.RoundedRectangleBorder(radius=R.SM),
            ),
            visible=False,
            on_click=self._on_spend_anyway,
        )
        # Золотая кнопка "сберечь"
        self._btn_capital = ft.FilledButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.SHIELD, color=C.BG, size=16),
                    ft.Text("Оставить в Капитале", color=C.BG,
                            size=FS.SM, weight=ft.FontWeight.BOLD),
                ],
                spacing=SP.XS, tight=True,
            ),
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: GOLD,
                         ft.ControlState.HOVERED: GOLD_GLOW},
                color={ft.ControlState.DEFAULT: C.BG},
                shape=ft.RoundedRectangleBorder(radius=R.SM),
                animation_duration=200,
            ),
            visible=False,
            on_click=self._on_keep_capital,
        )

        super().__init__(
            modal=True, bgcolor=C.CARD,
            shape=ft.RoundedRectangleBorder(radius=R.MD),
            title=ft.Text("Добавить расход", color=C.TEXT,
                          size=FS.LG, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                controls=[
                    ft.Row([ft.Text("Доступно:", color=C.SUBTEXT, size=FS.SM),
                            self._avl], spacing=SP.XS),
                    self._amount, self._cat_dd, self._note,
                    self._pause_block,
                    self._err,
                ],
                spacing=SP.SM, tight=True, width=300,
            ),
            actions=[
                self._btn_cancel,
                self._btn_spend,
                self._btn_capital,
                self._btn_add,
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Внутреннее состояние
        self._pending_amt:   float | None = None
        self._pending_catid: int   | None = None
        self._pending_note:  str          = ""
        self._pause_active:  bool         = False

    # ── Открытие ─────────────────────────────────────────────────────────────

    def open_dialog(self, page: ft.Page):
        cats = get_categories_by_type("expense")
        self._cat_dd.options = [
            ft.dropdown.Option(key=str(c.id), text=c.name) for c in cats
        ]
        self._cat_dd.value = str(cats[0].id) if cats else None
        s   = self._svc.get_summary()
        avl = s.get("available", 0)
        self._avl.value = f"{avl:,.2f} ₽"
        self._avl.color = C.AVAILABLE if avl > 0 else C.EXPENSE
        self._reset_ui()
        page.show_dialog(self)

    # ── Главный обработчик ────────────────────────────────────────────────────

    async def _on_add_click(self, e: ft.ControlEvent):
        """Валидирует ввод и запускает нужный флоу."""
        self._err.visible = False

        # Валидация суммы
        try:
            amt = float((self._amount.value or "").replace(",", ".").strip())
            assert amt > 0
        except Exception:
            self._err.value = "Введите корректную сумму"
            self._err.visible = True
            self.update()
            return

        # Валидация категории
        if not self._cat_dd.value:
            self._err.value = "Выберите категорию"
            self._err.visible = True
            self.update()
            return

        cat_id   = int(self._cat_dd.value)
        cat      = get_category_by_id(cat_id)
        mechanic = _classify(cat.name) if cat else "normal"

        self._pending_amt   = amt
        self._pending_catid = cat_id
        self._pending_note  = self._note.value or ""

        if mechanic == "transmutation":
            await self._flow_transmutation(e, amt, cat_id)
        elif mechanic == "pause":
            await self._flow_pause(e, amt)
        else:
            self._commit(e, amt, cat_id, self._pending_note)

    # ── МЕХАНИКА 1: Трансмутация ──────────────────────────────────────────────

    async def _flow_transmutation(self, e, amt: float, cat_id: int):
        """
        Проводит транзакцию, анимирует заголовок красный → золотой,
        показывает вдохновляющий SnackBar.
        """
        try:
            tx = self._svc.add_expense(
                amount=amt, category_id=cat_id, note=self._pending_note
            )
        except ValueError as ex:
            self._err.value = str(ex)
            self._err.visible = True
            self.update()
            return

        # Шаг 1: вспышка красного (обычный расход)
        self.title.color = C.EXPENSE
        self.update()
        await asyncio.sleep(0.1)

        # Шаг 2: плавный переход в золотой (трансмутация)
        self.title.color = GOLD
        self.title.value = "✦ Трансмутация"
        self.bgcolor     = GOLD_WARM
        self.update()
        await asyncio.sleep(0.9)

        e.page.pop_dialog()

        # SnackBar с цитатой
        e.page.show_dialog(ft.SnackBar(
            content=ft.Text(
                "Вы не потратили эти монеты. Вы конвертировали их в самый "
                "дорогой актив — в себя. Знания не обложит налогом "
                "ни один правитель.",
                color=C.BG, size=FS.SM,
            ),
            bgcolor=GOLD, duration=6000,
            show_close_icon=True, close_icon_color=C.BG,
        ))

        if self._cb:
            self._cb(tx)

    # ── МЕХАНИКА 2: Пауза Патриция ────────────────────────────────────────────

    async def _flow_pause(self, e, amt: float):
        """
        Блокирует ввод и запускает 3-секундный философский таймер.
        После паузы показывает два выбора.
        """
        self._pause_active    = True
        future_val            = round(amt * 15, 2)

        # Блокируем ввод и кнопку «Добавить»
        self._btn_add.visible  = False
        self._amount.disabled  = True
        self._cat_dd.disabled  = True
        self._note.disabled    = True

        # Показываем блок паузы
        self._progress.visible   = True
        self._pause_block.visible = True
        self._pause_quote.value  = (
            f"Истинное богатство — умение владеть желаниями.\n"
            f"Эти {amt:,.0f} ₽ через 10 лет превратятся "
            f"в {future_val:,.0f} ₽.\n"
            f"Ваше решение, Правитель."
        )
        self.update()

        # Отсчёт 3 секунды (asyncio.sleep — UI не зависает)
        for remaining in range(3, 0, -1):
            self._timer_lbl.value = f"Подождите {remaining} сек..."
            self.update()
            await asyncio.sleep(1)

        # Таймер завершён
        self._progress.visible   = False
        self._timer_lbl.value    = "Осознанность — путь Патриция."
        self._btn_spend.visible  = True
        self._btn_capital.visible = True
        self.update()

    async def _on_spend_anyway(self, e: ft.ControlEvent):
        """Пользователь осознанно решил потратить."""
        self._commit(e, self._pending_amt, self._pending_catid,
                     self._pending_note)

    async def _on_keep_capital(self, e: ft.ControlEvent):
        """
        Пользователь отказался от траты.
        Вспышка золотого + SnackBar с похвалой.
        """
        # Тройная вспышка золотого
        for _ in range(3):
            self.bgcolor = GOLD_WARM
            self.update()
            await asyncio.sleep(0.1)
            self.bgcolor = C.CARD
            self.update()
            await asyncio.sleep(0.07)

        self.title.value = "✦ Воля Патриция"
        self.title.color = GOLD
        self.bgcolor     = GOLD_WARM
        self.update()
        await asyncio.sleep(0.4)

        e.page.pop_dialog()

        # SnackBar с похвалой и щитом
        e.page.show_dialog(ft.SnackBar(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.SHIELD, color=C.BG, size=20),
                    ft.Text(
                        "Аркад гордится твоей волей! Капитал сохранён.",
                        color=C.BG, size=FS.SM, weight=ft.FontWeight.BOLD,
                        expand=True,
                    ),
                ],
                spacing=SP.SM,
            ),
            bgcolor=GOLD, duration=5000,
            show_close_icon=True, close_icon_color=C.BG,
        ))
        # Колбэк НЕ вызываем — транзакция отменена

    # ── Внутренние ───────────────────────────────────────────────────────────

    def _commit(self, e, amt: float, cat_id: int, note: str):
        """Проводит транзакцию и закрывает диалог."""
        try:
            tx = self._svc.add_expense(
                amount=amt, category_id=cat_id, note=note
            )
            e.page.pop_dialog()
            if self._cb:
                self._cb(tx)
        except ValueError as ex:
            self._err.value   = str(ex)
            self._err.visible = True
            self.update()

    def _reset_ui(self):
        """Полный сброс диалога к начальному состоянию."""
        self._pause_active          = False
        self._pending_amt           = None
        self._pending_catid         = None
        self._pending_note          = ""

        self._amount.value          = ""
        self._amount.disabled       = False
        self._note.value            = ""
        self._note.disabled         = False
        self._cat_dd.disabled       = False
        self._err.visible           = False

        self._pause_block.visible   = False
        self._progress.visible      = False
        self._timer_lbl.value       = ""
        self._pause_quote.value     = ""

        self._btn_add.visible       = True
        self._btn_spend.visible     = False
        self._btn_capital.visible   = False

        self.bgcolor                = C.CARD
        self.title.value            = "Добавить расход"
        self.title.color            = C.TEXT
