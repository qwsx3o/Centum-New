import flet as ft
from pathlib import Path
from core import AppController

BASE_DIR = Path(__file__).parent


def main():
    ft.app(
        target=AppController(),
        assets_dir=str(BASE_DIR / "assets"),
    )


if __name__ == "__main__":
    main()
