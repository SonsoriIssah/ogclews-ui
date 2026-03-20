# main.py
import sys
import os

# Must be set before ANY Qt imports
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-web-security --allow-file-access-from-files"
os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui     import QPalette, QColor
from PyQt5.QtCore    import Qt
from app.window      import MainWindow

BG      = "#0f1117"
SURFACE = "#1a1d27"
TEXT    = "#e8eaf0"
ACCENT  = "#00e5ff"


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    pal = QPalette()
    pal.setColor(QPalette.Window,          QColor(BG))
    pal.setColor(QPalette.WindowText,      QColor(TEXT))
    pal.setColor(QPalette.Base,            QColor(SURFACE))
    pal.setColor(QPalette.AlternateBase,   QColor(BG))
    pal.setColor(QPalette.Text,            QColor(TEXT))
    pal.setColor(QPalette.Button,          QColor(SURFACE))
    pal.setColor(QPalette.ButtonText,      QColor(TEXT))
    pal.setColor(QPalette.Highlight,       QColor(ACCENT))
    pal.setColor(QPalette.HighlightedText, QColor(BG))
    app.setPalette(pal)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()