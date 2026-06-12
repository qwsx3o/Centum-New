"""utils/theme.py — тема Centum для Flet 0.82"""
import flet as ft


class C:
    BG        = "#0D0D0D"
    SURFACE   = "#1A1A1A"
    CARD      = "#242424"
    ACCENT    = "#C9A84C"
    INCOME    = "#4CAF50"
    EXPENSE   = "#EF5350"
    CAPITAL   = "#C9A84C"
    AVAILABLE = "#42A5F5"
    TEXT      = "#F5F5F5"
    SUBTEXT   = "#9E9E9E"
    MUTED     = "#555555"
    DIVIDER   = "#2C2C2C"


class FS:
    XS=10; SM=12; MD=14; LG=16; XL=20; XXL=28; HERO=36


class SP:
    XS=4; SM=8; MD=16; LG=24; XL=32


class R:
    SM=8; MD=12; LG=20; FULL=100


def p(h=0, v=0, l=0, t=0, r=0, b=0) -> ft.Padding:
    """Хелпер padding без deprecated вызовов."""
    if h or v:
        return ft.Padding(left=h, right=h, top=v, bottom=v)
    return ft.Padding(left=l, top=t, right=r, bottom=b)


def build_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme_seed=C.ACCENT,
        color_scheme=ft.ColorScheme(
            primary=C.ACCENT,
            on_primary=C.BG,
            surface=C.SURFACE,
            on_surface=C.TEXT,
        ),
    )


def tf_style() -> dict:
    return dict(
        bgcolor=C.CARD,
        border_color=C.DIVIDER,
        focused_border_color=C.ACCENT,
        cursor_color=C.ACCENT,
        label_style=ft.TextStyle(color=C.SUBTEXT, size=FS.SM),
        text_style=ft.TextStyle(color=C.TEXT, size=FS.MD),
        border_radius=R.SM,
    )
