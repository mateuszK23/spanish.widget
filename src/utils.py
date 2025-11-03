import sys, os
from PySide6 import QtWidgets


def format_seconds(seconds: int) -> str:
    # human readable
    hrs, rem = divmod(seconds, 3600)
    mins, secs = divmod(rem, 60)
    parts = []
    if hrs:
        parts.append(f"{hrs}h")
    if mins:
        parts.append(f"{mins}m")
    if secs or not parts:
        parts.append(f"{secs}s")
    return " ".join(parts)


def center_on_screen(widget):
    """Centers a widget on the primary screen."""
    screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
    size = widget.frameGeometry()
    x = screen.center().x() - size.width() // 2
    y = screen.center().y() - size.height() // 2
    widget.move(x, y)

def resource_path(path):
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller bundled resource
        return os.path.join(sys._MEIPASS, path)
    return os.path.abspath(path)
