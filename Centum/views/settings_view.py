import flet as ft
from utils.theme import C, FS, SP, R, p, tf_style
from models.category import get_categories_by_type, delete_category
from views.components.category_dialog import CategoryDialog


class SettingsView:
    def __init__(self, finance_service, settings_service, backup_service):
        self._fin=finance_service; self._set=settings_service; self._bak=backup_service
        self._cat_dlg = CategoryDialog(on_success=self._on_cat)

        self._fam = ft.Text(str(self._set.family_members), color=C.ACCENT,
                             size=FS.XXL, weight=ft.FontWeight.BOLD)
        self._inc_col  = ft.Column(spacing=SP.XS)
        self._exp_col  = ft.Column(spacing=SP.XS)
        self._bak_lbl  = ft.Text("", color=C.SUBTEXT, size=FS.SM)

        scroll = ft.Column(controls=[
            self._profile_card(),
            ft.Divider(height=1, color=C.DIVIDER),
            self._cats_card(),
            ft.Divider(height=1, color=C.DIVIDER),
            self._backup_card(),
            ft.Divider(height=1, color=C.DIVIDER),
            self._danger_card(),
            ft.Container(height=SP.LG),
        ], spacing=SP.MD, scroll=ft.ScrollMode.AUTO, expand=True)

        self.container = ft.Column(controls=[
            ft.Container(
                content=ft.Text("Настройки", color=C.TEXT, size=FS.XL, weight=ft.FontWeight.BOLD),
                padding=ft.Padding(left=SP.MD, top=SP.MD, right=SP.MD, bottom=SP.SM),
            ),
            ft.Container(content=scroll, expand=True,
                         padding=ft.Padding(left=SP.MD, right=SP.MD, top=0, bottom=0)),
        ], expand=True, spacing=0)

    def refresh(self):
        self._fam.value = str(self._set.family_members)
        self._reload()
        if self.container.page: self.container.page.update()

    def _profile_card(self):
        return ft.Container(
            content=ft.Column([
                ft.Text("Профиль семьи", color=C.TEXT, size=FS.LG, weight=ft.FontWeight.W_600),
                ft.Text("Количество источников дохода", color=C.SUBTEXT, size=FS.SM),
                ft.Row([
                    ft.IconButton(icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                                  icon_color=C.ACCENT, on_click=self._dec),
                    self._fam,
                    ft.IconButton(icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                                  icon_color=C.ACCENT, on_click=self._inc),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=SP.MD),
            ], spacing=SP.SM),
            bgcolor=C.SURFACE, border_radius=R.MD, padding=SP.MD,
        )

    def _cats_card(self):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Категории", color=C.TEXT, size=FS.LG,
                            weight=ft.FontWeight.W_600, expand=True),
                    ft.IconButton(icon=ft.Icons.ADD_CIRCLE_OUTLINE, icon_color=C.ACCENT,
                                  tooltip="Добавить", on_click=self._add_cat),
                ]),
                ft.Text("Доходы", color=C.INCOME, size=FS.SM, weight=ft.FontWeight.W_500),
                self._inc_col,
                ft.Container(height=SP.XS),
                ft.Text("Расходы", color=C.EXPENSE, size=FS.SM, weight=ft.FontWeight.W_500),
                self._exp_col,
            ], spacing=SP.SM),
            bgcolor=C.SURFACE, border_radius=R.MD, padding=SP.MD,
        )

    def _backup_card(self):
        return ft.Container(
            content=ft.Column([
                ft.Text("Резервная копия", color=C.TEXT, size=FS.LG, weight=ft.FontWeight.W_600),
                ft.Text("Экспорт centum.db + settings.json в ZIP", color=C.SUBTEXT, size=FS.SM),
                ft.FilledButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SAVE_ALT, color=C.TEXT, size=18),
                        ft.Text("Создать бэкап", color=C.TEXT, size=FS.MD),
                    ], spacing=SP.SM, tight=True),
                    style=ft.ButtonStyle(
                        bgcolor={ft.ControlState.DEFAULT: C.CARD},
                        color={ft.ControlState.DEFAULT: C.TEXT},
                        shape=ft.RoundedRectangleBorder(radius=R.SM),
                    ),
                    on_click=self._do_backup,
                ),
                self._bak_lbl,
            ], spacing=SP.SM),
            bgcolor=C.SURFACE, border_radius=R.MD, padding=SP.MD,
        )

    def _reload(self):
        self._inc_col.controls = [self._cat_row(c) for c in get_categories_by_type("income")]
        self._exp_col.controls = [self._cat_row(c) for c in get_categories_by_type("expense")]

    def _cat_row(self, cat):
        return ft.Row([
            ft.Container(width=12, height=12, bgcolor=cat.color or C.SUBTEXT,
                         border_radius=R.FULL),
            ft.Text(cat.name,
                    color=C.TEXT if not cat.is_system else C.SUBTEXT,
                    size=FS.MD, expand=True, italic=cat.is_system),
            *([] if cat.is_system else [
                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=C.EXPENSE,
                              icon_size=18,
                              on_click=lambda e, cid=cat.id: self._del(e, cid)),
            ]),
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=SP.SM)

    def _inc(self, e):
        self._set.family_members += 1
        self._fam.value = str(self._set.family_members); e.page.update()

    def _dec(self, e):
        if self._set.family_members > 1:
            self._set.family_members -= 1
            self._fam.value = str(self._set.family_members); e.page.update()

    def _add_cat(self, e): self._cat_dlg.open_dialog(e.page)

    def _on_cat(self, _):
        self._reload()
        if self.container.page: self.container.page.update()

    def _del(self, e, cid):
        if delete_category(cid):
            self._reload(); e.page.update()
        else:
            e.page.snack_bar = ft.SnackBar(
                content=ft.Text("Нельзя удалить: есть транзакции", color=C.TEXT),
                bgcolor=C.CARD)
            e.page.snack_bar.open = True; e.page.update()

    def _danger_card(self):
        return ft.Container(
            content=ft.Column([
                ft.Text("Опасная зона", color=C.EXPENSE, size=FS.LG,
                        weight=ft.FontWeight.W_600),
                ft.Text(
                    "Перед очисткой автоматически создаётся резервная копия.",
                    color=C.SUBTEXT, size=FS.SM,
                ),
                ft.FilledButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DELETE_FOREVER, color=C.TEXT, size=18),
                        ft.Text("Очистить все данные", color=C.TEXT, size=FS.MD),
                    ], spacing=SP.SM, tight=True),
                    style=ft.ButtonStyle(
                        bgcolor={ft.ControlState.DEFAULT: "#7A1515"},
                        color={ft.ControlState.DEFAULT: C.TEXT},
                        shape=ft.RoundedRectangleBorder(radius=R.SM),
                    ),
                    on_click=self._confirm_clear,
                ),
            ], spacing=SP.SM),
            bgcolor=C.SURFACE,
            border_radius=R.MD,
            padding=SP.MD,
            border=ft.border.all(1, "#7A1515"),
        )

    def _confirm_clear(self, e):
        def do_clear(ev):
            ev.page.pop_dialog()
            try:
                backup_path = self._bak.clear_all_data()
                # Сбрасываем settings_service в памяти
                self._set.family_members = 1
                self._fam.value = "1"
                self._reload()
                self._bak_lbl.value = f"✓ Бэкап сохранён: {backup_path.name}"
                self._bak_lbl.color = C.INCOME
                ev.page.update()
            except Exception as ex:
                self._bak_lbl.value = f"Ошибка: {ex}"
                self._bak_lbl.color = C.EXPENSE
                ev.page.update()

        e.page.show_dialog(ft.AlertDialog(
            modal=True,
            bgcolor=C.CARD,
            shape=ft.RoundedRectangleBorder(radius=R.MD),
            title=ft.Text("Очистить все данные?", color=C.EXPENSE,
                          size=FS.LG, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text(
                    "Будут удалены ВСЕ транзакции и пользовательские категории.",
                    color=C.TEXT, size=FS.MD,
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SAVE_ALT, color=C.INCOME, size=14),
                        ft.Text("Резервная копия будет создана автоматически.",
                                color=C.INCOME, size=FS.SM, italic=True),
                    ], spacing=SP.XS),
                    bgcolor=C.BG, border_radius=R.SM,
                    padding=ft.Padding(left=SP.SM, right=SP.SM, top=SP.XS, bottom=SP.XS),
                ),
                ft.Text("Это действие нельзя отменить без бэкапа.",
                        color=C.SUBTEXT, size=FS.SM),
            ], spacing=SP.SM, tight=True, width=280),
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
                    content=ft.Text("Очистить", color=C.TEXT, size=FS.MD,
                                    weight=ft.FontWeight.BOLD),
                    style=ft.ButtonStyle(
                        bgcolor={ft.ControlState.DEFAULT: "#7A1515"},
                        color={ft.ControlState.DEFAULT: C.TEXT},
                        shape=ft.RoundedRectangleBorder(radius=R.SM),
                    ),
                    on_click=do_clear,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        ))

    def _do_backup(self, e):
        try:
            self._set.save_now()
            path = self._bak.create_backup()
            self._bak_lbl.value = f"✓ {path.name}"; self._bak_lbl.color = C.INCOME
        except Exception as ex:
            self._bak_lbl.value = f"Ошибка: {ex}"; self._bak_lbl.color = C.EXPENSE
        e.page.update()
