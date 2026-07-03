import os
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase, QIcon

from storage import load_settings, app_path
from win_utils import set_app_id
from overlay import Overlay
from config_window import ConfigWindow

APP_ID = "Satheus.DbDCrosshair"


def _carregar_fontes():
    pasta = app_path("fonts")
    if not os.path.isdir(pasta):
        return
    for nome in os.listdir(pasta):
        if nome.lower().endswith((".ttf", ".otf")):
            QFontDatabase.addApplicationFont(os.path.join(pasta, nome))


def main():
    app = QApplication(sys.argv)

    set_app_id(APP_ID)
    icone = QIcon(app_path("icon.ico"))
    if not icone.isNull():
        app.setWindowIcon(icone)

    _carregar_fontes()

    settings = load_settings()

    overlay = Overlay(settings)
    overlay.show()

    config = ConfigWindow(settings, overlay)
    config.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
