import sys
from PySide6 import QtWidgets, QtCore
from app import SpanishWidget


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = SpanishWidget()

    # Position top-right of screen
    screen = app.primaryScreen().availableGeometry()
    x = screen.right() - window.width()
    y = screen.top()
    window.move(x, y)

    # Frameless and transparent like before
    window.setWindowFlags(
        QtCore.Qt.Tool  # prevents taskbar icon
        | QtCore.Qt.FramelessWindowHint  # frameless like before
    )
    window.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
