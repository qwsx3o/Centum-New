"""views/main_view.py — Главный экран: кольцевой график + кнопки."""
import math
import flet as ft
import flet.canvas as cv
from utils.theme import C, FS, SP, R, p
from views.components.add_income_dialog import AddIncomeDialog
from views.components.add_expense_dialog import AddExpenseDialog

_S=260; _OR=108; _IR=70; _CX=_CY=_S/2


def _arc(segs: list) -> list:
    paths, gap, deg = [], 1.5, -90.0
    for s in segs:
        sw = s["percent"] / 100 * 360 - gap
        if sw <= 0: continue
        sr, er = math.radians(deg), math.radians(deg + sw)
        la = sw > 180
        def pt(r, a): return _CX + r*math.cos(a), _CY + r*math.sin(a)
        o1=pt(_OR,sr); o2=pt(_OR,er); i1=pt(_IR,er); i2=pt(_IR,sr)
        paths.append(cv.Path(
            elements=[
                cv.Path.MoveTo(*o1),
                cv.Path.ArcTo(x=o2[0],y=o2[1],radius=_OR,large_arc=la,clockwise=True),
                cv.Path.LineTo(*i1),
                cv.Path.ArcTo(x=i2[0],y=i2[1],radius=_IR,large_arc=la,clockwise=False),
                cv.Path.Close(),
            ],
            paint=ft.Paint(color=s["color"], style=ft.PaintingStyle.FILL),
        ))
        deg += sw + gap
    return paths


def _empty_arc() -> list:
    def ring(r, col):
        return cv.Path(
            elements=[cv.Path.MoveTo(_CX, _CY-r),
                      cv.Path.ArcTo(x=_CX+.01, y=_CY-r, radius=r,
                                    large_arc=True, clockwise=True),
                      cv.Path.Close()],
            paint=ft.Paint(color=col, style=ft.PaintingStyle.FILL),
        )
    return [ring(_OR, C.CARD), ring(_IR, C.BG)]


class MainView:
    def __init__(self, fin, svc):
        self._fin = fin; self._svc = svc
        self._dlg_in = AddIncomeDialog(fin, on_success=lambda _: self.refresh())
        self._dlg_ex = AddExpenseDialog(fin, on_success=lambda _: self.refresh())

        # ── График ────────────────────────────────────────────────────────────
        self._canvas = cv.Canvas(shapes=_empty_arc(), width=_S, height=_S)
        self._total_val = ft.Text("0 ₽", color=C.TEXT, size=FS.XXL,
                                   weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
        self._total_lbl = ft.Text("общий доход", color=C.SUBTEXT, size=FS.SM,
                                   text_align=ft.TextAlign.CENTER)

        # ── Статистика ────────────────────────────────────────────────────────
        self._cap = ft.Text("0 ₽", color=C.CAPITAL,   size=FS.MD, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
        self._avl = ft.Text("0 ₽", color=C.AVAILABLE, size=FS.MD, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
        self._exp = ft.Text("0 ₽", color=C.EXPENSE,   size=FS.MD, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)

        # ── Легенда ───────────────────────────────────────────────────────────
        self._legend = ft.Row(controls=[], wrap=True, spacing=SP.SM, run_spacing=SP.XS)

        self.container = ft.Column(
            controls=[
                # Заголовок
                ft.Container(
                    content=ft.Text("CENTUM", color=C.ACCENT, size=FS.LG,
                                    weight=ft.FontWeight.BOLD,
                                    style=ft.TextStyle(letter_spacing=5)),
                    alignment=ft.Alignment(0, 0),
                    padding=p(v=SP.SM),
                ),
                # Кольцевой график
                ft.Container(
                    content=ft.Stack(controls=[
                        ft.Container(content=self._canvas, width=_S, height=_S),
                        ft.Container(
                            content=ft.Column(
                                controls=[self._total_val, self._total_lbl],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=2, tight=True,
                            ),
                            width=_S, height=_S, alignment=ft.Alignment(0, 0),
                        ),
                    ], width=_S, height=_S),
                    alignment=ft.Alignment(0, 0),
                ),
                # Чипсы
                ft.Row(controls=[
                    self._stat_chip(self._cap, "Капитал"),
                    self._stat_chip(self._avl, "Доступно"),
                    self._stat_chip(self._exp, "Расходы"),
                ], spacing=SP.SM),
                # Легенда
                self._legend,
                # Растяжка
                ft.Container(expand=True),
                # Кнопки
                ft.Container(
                    content=ft.Row(controls=[
                        self._fab(ft.Icons.ADD_CIRCLE_OUTLINE, "+ Доход",
                                  C.INCOME, C.BG, self._open_in),
                        self._fab(ft.Icons.REMOVE_CIRCLE_OUTLINE, "− Расход",
                                  C.EXPENSE, C.TEXT, self._open_ex),
                    ], spacing=SP.SM),
                    padding=ft.Padding(left=SP.MD, right=SP.MD, top=SP.SM, bottom=SP.LG),

                ),
            ],
            expand=True,
            spacing=SP.SM,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

    def refresh(self):
        s   = self._fin.get_summary()
        pie = self._fin.get_pie_chart_data()
        cur = self._svc.currency
        self._total_val.value = f"{s['total_income']:,.0f} {cur}"
        self._canvas.shapes   = _arc(pie) if pie else _empty_arc()
        self._cap.value = f"{s['total_capital']:,.0f} {cur}"
        self._avl.value = f"{s['available']:,.0f} {cur}"
        self._exp.value = f"{s['total_expenses']:,.0f} {cur}"
        self._legend.controls = [
            ft.Row([
                ft.Container(width=10, height=10, bgcolor=x["color"], border_radius=R.FULL),
                ft.Text(x["name"], color=C.SUBTEXT, size=FS.XS),
            ], spacing=SP.XS, tight=True)
            for x in pie
        ]
        if self.container.page:
            self.container.page.update()

    def _open_in(self, e): self._dlg_in.open_dialog(e.page)
    def _open_ex(self, e): self._dlg_ex.open_dialog(e.page)

    @staticmethod
    def _stat_chip(ctrl, label):
        return ft.Container(
            content=ft.Column(controls=[ctrl,
                ft.Text(label, color=C.SUBTEXT, size=FS.XS, text_align=ft.TextAlign.CENTER)],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2, tight=True),
            bgcolor=C.SURFACE, border_radius=R.SM,
            padding=p(h=SP.MD, v=SP.SM), expand=True,
        )

    @staticmethod
    def _fab(icon, label, bg, fg, cb):
        """Кнопка действия — FilledButton с явным стилем."""
        return ft.FilledButton(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, color=fg, size=20),
                    ft.Text(label, color=fg, size=FS.MD, weight=ft.FontWeight.W_600),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=SP.SM, tight=True,
            ),
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: bg,
                         ft.ControlState.HOVERED: bg,
                         ft.ControlState.PRESSED: bg},
                color={ft.ControlState.DEFAULT: fg},
                padding=ft.Padding(left=SP.LG, right=SP.LG, top=14, bottom=14),
                shape=ft.RoundedRectangleBorder(radius=R.MD),
                animation_duration=150,
            ),
            on_click=cb,
            expand=True,
            height=54,
        )
