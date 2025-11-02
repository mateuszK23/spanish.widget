from PySide6 import QtGui, QtWidgets
from logger import logger
from paths import TRAY_ICON


class TrayController(QtWidgets.QSystemTrayIcon):
    def __init__(self, app):
        icon = QtGui.QIcon(TRAY_ICON)
        super().__init__(icon, app)
        self.app = app

        menu = QtWidgets.QMenu()
        menu.addAction("Refresh Now", self.refresh_now)
        menu.addAction("Settings", self.open_settings)
        menu.addSeparator()
        menu.addAction("Quit", self.quit_app)

        self.setContextMenu(menu)

    def start(self):
        self.show()

    def refresh_now(self):
        logger.info("Manual refresh triggered from tray")
        self.app.regenerate_data_for_today()

    def open_settings(self):
        self.app.open_settings()

    def quit_app(self):
        logger.info("Quitting the app")
        self.hide()
        self.app.quit()
