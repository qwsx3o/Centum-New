"""views/history_view.py — История с возможностью удаления записей."""
import flet as ft
from utils.theme import C, FS, SP, R


class HistoryView:
    def __init__(self, fin, svc):
        self._fin = fin
        self._svc = svc

        self._list = ft.ListView(
            controls=[], expand=True, spacing=SP.XS,
            padding=ft.Padding(left=SP.MD, right=SP.MD, top=0, bottom=SP.LG),
        )
        self._empty = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.RECEIPT_LONG, color=C.MUTED, size=56),
                ft.Text("Транзакций пока нет", color=C.MUTED, size=FS.MD),
                ft.Text("Добавьте первый доход на главном экране",
                        color=C.MUTED, size=FS.SM, italic=True),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=SP.SM),
            alignment=ft.Alignment(0, 0), expand=True,
        )

        self.container = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text("История", color=C.TEXT, size=FS.XL,
                                    weight=ft.FontWeight.BOLD),
                    padding=ft.Padding(left=SP.MD, right=SP.MD,
                                       top=SP.MD, bottom=SP.SM),
                ),
                self._empty,
                self._list,
            ],
            expand=True, spacing=0,
        )

    def refresh(self):
        txs = self._fin.get_history(limit=100)
        cur = self._svc.currency
        if not txs:
            self._empty.visible = True
            self._list.visible  = False
        else:
            self._empty.visible = False
            self._list.visible  = True
            self._list.controls = [self._card(tx, cur) for tx in txs]
        if self.container.page:
            self.container.page.update()

    def _card(self, tx, cur: str) -> ft.Container:
        type_map = {
            "income":  (C.INCOME,  ft.Icons.ARROW_DOWNWARD, "+"),
            "expense": (C.EXPENSE, ft.Icons.ARROW_UPWARD,   "−"),
            "capital": (C.CAPITAL, ft.Icons.SAVINGS,        "→"),
        }
        color, icon, sign = type_map.get(tx.type, (C.SUBTEXT, ft.Icons.HISTORY, ""))

        return ft.Container(
            content=ft.Row(
                controls=[
                    # ── Иконка типа ──────────────────────────────────────────
                    ft.Container(
                        content=ft.Icon(icon, color=color, size=18),
                        bgcolor=C.BG, border_radius=R.FULL,
                        width=38, height=38, alignment=ft.Alignment(0, 0),
                    ),
                    # ── Описание ─────────────────────────────────────────────
                    ft.Column(
                        controls=[
                            ft.Text(tx.category_name, color=C.TEXT,
                                    size=FS.MD, weight=ft.FontWeight.W_500),
                            ft.Text(
                                f"{tx.note}  ·  {tx.created_at[:16]}"
                                if tx.note else tx.created_at[:16],
                                color=C.SUBTEXT, size=FS.XS,
                            ),
                        ],
                        expand=True, spacing=2, tight=True,
                    ),
                    # ── Сумма ─────────────────────────────────────────────────
                    ft.Text(
                        f"{sign}{tx.amount:,.2f} {cur}",
                        color=color, size=FS.MD, weight=ft.FontWeight.BOLD,
                    ),
                    # ── Кнопка удаления ───────────────────────────────────────
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=C.MUTED,
                        icon_size=18,
                        tooltip="Удалить запись",
                        on_click=lambda e, tid=tx.id: self._confirm_delete(e, tid),
                        style=ft.ButtonStyle(
                            overlay_color={ft.ControlState.HOVERED: "#33EF5350"},
                        ),
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=SP.XS,
            ),
            bgcolor=C.SURFACE,
            border_radius=R.SM,
            padding=ft.Padding(left=SP.SM, right=SP.XS, top=SP.XS, bottom=SP.XS),
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN),
        )

    def _confirm_delete(self, e, tx_id: int):
        """Показывает диалог подтверждения перед удалением."""
        def do_delete(ev):
            ev.page.pop_dialog()
            self._fin.delete_transaction(tx_id)
            self.refresh()

        e.page.show_dialog(ft.AlertDialog(
            modal=True,
            bgcolor=C.CARD,
            shape=ft.RoundedRectangleBorder(radius=R.MD),
            title=ft.Text("Удалить запись?", color=C.TEXT,
                          size=FS.LG, weight=ft.FontWeight.BOLD),
            content=ft.Text(
                "Запись будет удалена из базы данных.\nЭто действие нельзя отменить.",
                color=C.SUBTEXT, size=FS.SM,
            ),
            actions=[
                ft.FilledButton(
                    content=ft.Text("Отмена", color=C.SUBTEXT, size=FS.MD),
                    style=ft.ButtonStyle(
                        bgcolor={ft.ControlState.DEFAULT: C.SURFACE},
                        shape=ft.RoundedRectangleBorder(radius=R.SM),
                    ),
                    on_click=lambda ev: ev.page.pop_dialog(),
                ),
                ft.FilledButton(
                    content=ft.Text("Удалить", color=C.TEXT, size=FS.MD,
                                    weight=ft.FontWeight.BOLD),
                    style=ft.ButtonStyle(
                        bgcolor={ft.ControlState.DEFAULT: C.EXPENSE},
                        color={ft.ControlState.DEFAULT: C.TEXT},
                        shape=ft.RoundedRectangleBorder(radius=R.SM),
                    ),
                    on_click=do_delete,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        ))
