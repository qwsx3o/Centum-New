import flet as ft
from utils.theme import C, FS, SP, R, tf_style
from models.category import get_categories_by_type


class AddIncomeDialog(ft.AlertDialog):
    def __init__(self, finance_service, on_success=None):
        self._svc=finance_service; self._cb=on_success
        self._amount = ft.TextField(label="Сумма", keyboard_type=ft.KeyboardType.NUMBER,
                                    prefix=ft.Text("₽  ", color=C.SUBTEXT), **tf_style())
        self._note   = ft.TextField(label="Примечание (необязательно)", max_length=100, **tf_style())
        self._cat_dd = ft.Dropdown(label="Категория", bgcolor=C.CARD,
                                    border_color=C.DIVIDER, focused_border_color=C.ACCENT,
                                    border_radius=R.SM,
                                    label_style=ft.TextStyle(color=C.SUBTEXT),
                                    text_style=ft.TextStyle(color=C.TEXT))
        self._err = ft.Text("", color=C.EXPENSE, size=FS.SM, visible=False)

        super().__init__(
            modal=True, bgcolor=C.CARD,
            shape=ft.RoundedRectangleBorder(radius=R.MD),
            title=ft.Text("Добавить доход", color=C.TEXT, size=FS.LG, weight=ft.FontWeight.BOLD),
            content=ft.Column(controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.INFO_OUTLINE, color=C.ACCENT, size=14),
                        ft.Text("10% автоматически → «Капитал»",
                                color=C.ACCENT, size=FS.SM, italic=True),
                    ], spacing=SP.XS),
                    bgcolor=C.BG, border_radius=R.SM,
                    padding=ft.Padding(left=SP.MD, right=SP.MD, top=SP.SM, bottom=SP.SM),
                ),
                self._amount, self._cat_dd, self._note, self._err,
            ], spacing=SP.SM, tight=True, width=300),
            actions=[
                ft.FilledButton(
                    content=ft.Text("Отмена", color=C.SUBTEXT, size=FS.MD),
                    style=ft.ButtonStyle(
                        bgcolor={ft.ControlState.DEFAULT: C.SURFACE},
                        color={ft.ControlState.DEFAULT: C.SUBTEXT},
                        shape=ft.RoundedRectangleBorder(radius=R.SM),
                    ),
                    on_click=lambda e: e.page.pop_dialog(),
                ),
                ft.FilledButton(
                    content=ft.Text("Добавить", color=C.BG, size=FS.MD,
                                    weight=ft.FontWeight.BOLD),
                    style=ft.ButtonStyle(
                        bgcolor={ft.ControlState.DEFAULT: C.INCOME},
                        color={ft.ControlState.DEFAULT: C.BG},
                        shape=ft.RoundedRectangleBorder(radius=R.SM),
                    ),
                    on_click=self._confirm,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def open_dialog(self, page):
        cats = get_categories_by_type("income")
        self._cat_dd.options = [ft.dropdown.Option(key=str(c.id), text=c.name) for c in cats]
        self._cat_dd.value   = str(cats[0].id) if cats else None
        self._amount.value=self._note.value=""; self._err.visible=False
        page.show_dialog(self)

    def _confirm(self, e):
        self._err.visible=False
        try:
            amt=float((self._amount.value or "").replace(",",".").strip()); assert amt>0
        except:
            self._err.value="Введите корректную сумму"; self._err.visible=True
            self.update(); return
        if not self._cat_dd.value:
            self._err.value="Выберите категорию"; self._err.visible=True
            self.update(); return
        try:
            res=self._svc.add_income(amount=amt,
                                     category_id=int(self._cat_dd.value),
                                     note=self._note.value or "")
            e.page.pop_dialog()
            if self._cb: self._cb(res)
        except Exception as ex:
            self._err.value=str(ex); self._err.visible=True; self.update()
