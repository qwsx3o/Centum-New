#!/usr/bin/env python3
"""
build_apk.py — Скрипт сборки Centum в APK для Android.

Требования (устанавливаются автоматически при первом запуске):
  - Python 3.9+
  - flet-cli  (pip install flet-cli==0.82.0)
  - Flutter SDK  →  https://flutter.dev/docs/get-started/install
  - Android SDK / NDK (через Android Studio или sdkmanager)
  - Java JDK 17+

Запуск:
  python build_apk.py

Результат:
  build/apk/centum.apk
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# ── Конфигурация ─────────────────────────────────────────────────────────────
APP_NAME        = "Centum"
APP_ORG         = "com.altervolya"
APP_BUNDLE_ID   = "com.altervolya.centum"
APP_VERSION     = "1.0.0"
APP_BUILD_NUM   = "1"
APP_DESCRIPTION = "Личные финансы по правилу Аркада"
SPLASH_COLOR    = "#0D0D0D"       # тёмный фон сплеш-экрана
ICON_FILE       = "assets/icon.png"  # относительно папки проекта

BASE_DIR  = Path(__file__).parent.resolve()
BUILD_DIR = BASE_DIR / "build" / "apk"


def run(cmd: str, cwd=None, check=True):
    """Запускает команду и стримит вывод в консоль."""
    print(f"\n▶  {cmd}\n{'─'*60}")
    result = subprocess.run(
        cmd, shell=True, cwd=cwd or BASE_DIR,
        text=True,
    )
    if check and result.returncode != 0:
        print(f"\n✗ Команда завершилась с кодом {result.returncode}")
        sys.exit(result.returncode)
    return result


def check_tool(name: str, hint: str) -> bool:
    if shutil.which(name):
        print(f"  ✓ {name}")
        return True
    print(f"  ✗ {name} не найден — {hint}")
    return False


def check_requirements():
    print("\n═══ Проверка зависимостей ═══")
    ok = True
    ok &= check_tool("flutter",
        "установите Flutter: https://flutter.dev/docs/get-started/install/windows")
    ok &= check_tool("java",
        "установите JDK 17+: https://adoptium.net/")

    # Android SDK через ANDROID_HOME / ANDROID_SDK_ROOT
    android_home = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if android_home and Path(android_home).exists():
        print(f"  ✓ Android SDK ({android_home})")
    else:
        print("  ✗ ANDROID_HOME не задан — установите Android SDK через Android Studio")
        print("    и добавьте: set ANDROID_HOME=C:\\Users\\<Вас>\\AppData\\Local\\Android\\Sdk")
        ok = False

    # flet-cli
    try:
        import flet_cli  # noqa
        print("  ✓ flet-cli")
    except ImportError:
        print("  ✗ flet-cli не найден — запустите: pip install flet-cli==0.82.0")
        ok = False

    return ok


def check_icon():
    """Проверяет наличие иконки в папке assets/."""
    icon_path = BASE_DIR / ICON_FILE
    textures_icon = BASE_DIR / "textures" / "icon.png"

    if icon_path.exists():
        print(f"  ✓ Иконка: {ICON_FILE}")
        return

    # Если иконка лежит в textures/ — копируем в assets/
    if textures_icon.exists():
        (BASE_DIR / "assets").mkdir(exist_ok=True)
        shutil.copy(textures_icon, icon_path)
        print(f"  ✓ Иконка скопирована: textures/icon.png → {ICON_FILE}")
        return

    print(f"  ⚠ Иконка не найдена ({ICON_FILE})")
    print(f"    Положите icon.png в папку: {BASE_DIR / 'assets'}")
    print(f"    Рекомендуемый размер: 1024×1024 пикселей, формат PNG")


def build_apk():
    print("\n═══ Сборка APK ═══")
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    cmd = (
        f'python -m flet_cli build apk "{BASE_DIR}"'
        f' --project "{APP_NAME}"'
        f' --org "{APP_ORG}"'
        f' --bundle-id "{APP_BUNDLE_ID}"'
        f' --product "{APP_NAME}"'
        f' --description "{APP_DESCRIPTION}"'
        f' --build-version "{APP_VERSION}"'
        f' --build-number "{APP_BUILD_NUM}"'
        f' --splash-color "{SPLASH_COLOR}"'
        f' --splash-dark-color "{SPLASH_COLOR}"'
        f' --android-adaptive-icon-background "{SPLASH_COLOR}"'
        f' --module-name main'
        f' --output "{BUILD_DIR}"'
        f' --no-rich-output'
    )
    run(cmd)


def show_result():
    apk_files = list(BUILD_DIR.glob("*.apk"))
    if not apk_files:
        # flet может положить в подпапку
        apk_files = list(BUILD_DIR.rglob("*.apk"))

    print("\n═══ Результат ═══")
    if apk_files:
        for apk in apk_files:
            size_mb = apk.stat().st_size / 1024 / 1024
            print(f"  ✓ APK готов: {apk}")
            print(f"    Размер: {size_mb:.1f} МБ")
        print()
        print("  Для установки на Android:")
        print("  1. Скопируйте APK на телефон (USB / облако)")
        print("  2. На телефоне: Настройки → Безопасность → Установка из неизвестных источников")
        print("  3. Откройте APK-файл через файловый менеджер")
    else:
        print("  ✗ APK не найден в папке build/apk/")
        print("    Проверьте вывод выше на наличие ошибок Flutter.")


def main():
    print(f"{'═'*60}")
    print(f"  Centum APK Builder  v{APP_VERSION}")
    print(f"  Python {sys.version.split()[0]}  |  {BASE_DIR}")
    print(f"{'═'*60}")

    if not check_requirements():
        print("\n✗ Установите недостающие зависимости и запустите снова.")
        sys.exit(1)

    check_icon()
    build_apk()
    show_result()


if __name__ == "__main__":
    main()
