import flet as ft
from utils.theme import C, FS, SP, R, tf_style
from models.category import create_category

COLORS=["#4CAF50","#EF5350","#42A5F5","#AB47BC",
        "#FF7043","#26C6DA","#FFCA28","#66BB6A","#EC407A","#78909C"]


class CategoryDialog(ft.AlertDialog):
    def __init__(self, on_success=None):
        self._cb=on_success; self._color=COLORS[0]; self._type="expense"
        self._name=ft.TextField(label="Название категории", max_length=40, **tf_style())
        self._seg=ft.SegmentedButton(
            selected=["expense"],
            segments=[
                ft.Segment(value="income",  label=ft.Text("Доход",  color=C.TEXT)),
                ft.Segment(value="expense", label=ft.Text("Расход", color=C.TEXT)),
            ],
            on_change=lambda e: setattr(self, '_type', list(e.control.selected)[0]),
        )
        self._crow = ft.Row(controls=self._chips(), wrap=True, spacing=SP.SM)
        self._err  = ft.Text("", color=C.EXPENSE, size=FS.SM, visible=False)

        super().__init__(
            modal=True, bgcolor=C.CARD,
            shape=ft.RoundedRectangleBorder(radius=R.MD),
            title=ft.Text("Новая категория", color=C.TEXT, size=FS.LG, weight=ft.FontWeight.BOLD),
            content=ft.Column(controls=[
                self._seg, self._name,
                ft.Text("Цвет метки", color=C.SUBTEXT, size=FS.SM),
                self._crow, self._err,
            ], spacing=SP.SM, tight=True, width=300),
            actions=[
                ft.FilledButton(
                    content=ft.Text("Отмена", color=C.SUBTEXT, size=FS.MD),
                    style=ft.ButtonStyle(
                        bgcolor={ft.ControlState.DEFAULT: C.SURFACE},
                        shape=ft.RoundedRectangleBorder(radius=R.SM)),
                    on_click=lambda e: e.page.pop_dialog(),
                ),
                ft.FilledButton(
                    content=ft.Text("Создать", color=C.BG, size=FS.MD, weight=ft.FontWeight.BOLD),
                    style=ft.ButtonStyle(
                        bgcolor={ft.ControlState.DEFAULT: C.ACCENT},
                        color={ft.ControlState.DEFAULT: C.BG},
                        shape=ft.RoundedRectangleBorder(radius=R.SM)),
                    on_click=self._confirm,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def open_dialog(self, page, default_type="expense"):
        self._type=default_type; self._seg.selected=[default_type]
        self._name.value=""; self._err.visible=False
        page.show_dialog(self)

    def _chips(self):
        return [
            ft.GestureDetector(
                content=ft.Container(
                    width=30, height=30, bgcolor=c, border_radius=R.FULL,
                    border=ft.border.all(3, C.TEXT if c==self._color else "transparent"),
                    animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
                ),
                on_tap=lambda e, col=c: self._pick(col),
            ) for c in COLORS
        ]

    def _pick(self, color):
        self._color=color; self._crow.controls=self._chips(); self._crow.update()

    def _confirm(self, e):
        name=(self._name.value or "").strip()
        if len(name)<2:
            self._err.value="Мин. 2 символа"; self._err.visible=True; self.update(); return
        try:
            cat=create_category(name=name, cat_type=self._type, color=self._color)
            e.page.pop_dialog()
            if self._cb: self._cb(cat)
        except Exception as ex:
            self._err.value=f"Ошибка: {ex}"; self._err.visible=True; self.update()
