"""core.py — AppController: DI + NavigationBar."""
import flet as ft
from utils.theme import C, build_theme
from models.database import initialize_schema
from services.finance_service import FinanceService
from services.settings_service import SettingsService
from services.backup_service import BackupService
from views.main_view import MainView
from views.history_view import HistoryView
from views.chronicle_view import ChronicleView
from views.settings_view import SettingsView


class AppController:
    def __init__(self):
        initialize_schema()
        self._set = SettingsService()
        self._fin = FinanceService()
        self._bak = BackupService()
        self._mv  = MainView(self._fin, self._set)
        self._hv  = HistoryView(self._fin, self._set)
        self._chr = ChronicleView(self._fin, self._set)
        self._sv  = SettingsView(self._fin, self._set, self._bak)
        self._views = [self._mv, self._hv, self._chr, self._sv]

    def __call__(self, page: ft.Page):
        self._page = page
        page.title      = "Centum"
        page.theme_mode = ft.ThemeMode.DARK
        page.theme      = build_theme()
        page.bgcolor    = C.BG
        page.padding    = 0

        try:
            page.window.min_width  = 360
            page.window.min_height = 640
        except Exception:
            pass

        self._body = ft.Container(
            content=self._mv.container,
            expand=True,
            bgcolor=C.BG,
        )

        self._nav = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.PIE_CHART_OUTLINE,
                    selected_icon=ft.Icons.PIE_CHART,
                    label="Главная",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.HISTORY,
                    selected_icon=ft.Icons.HISTORY,
                    label="История",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.CALENDAR_MONTH,
                    selected_icon=ft.Icons.CALENDAR_MONTH,
                    label="Хроника",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label="Настройки",
                ),
            ],
            bgcolor=C.SURFACE,
            indicator_color=C.ACCENT,
            shadow_color=C.BG,
            label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
            selected_index=0,
            on_change=self._on_nav,
        )

        page.add(ft.Column(
            controls=[self._body, self._nav],
            expand=True, spacing=0,
        ))

        # Загружаем данные главного экрана
        self._mv.refresh()
        page.update()

    def _on_nav(self, e):
        idx  = e.control.selected_index
        view = self._views[idx]
        self._body.content = view.container
        self._page.update()
        view.refresh()
        self._page.update()
