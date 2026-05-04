# main/main.py
import sys
import os

os.environ["QT_LOGGING_RULES"] = "qt.gui.icc=false"

# --- Setup sys.path agar semua modul (ui, auth, book, data) bisa diimport ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# Tambahkan project_root ke path (agar import ui.xxx, auth.xxx dll bisa berjalan)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Ubah working directory ke project_root agar path relatif (assets/, output/) bisa berjalan
os.chdir(project_root)

from PyQt5.QtWidgets import QApplication
from screen_manager import ScreenManager


def main():
    app = QApplication(sys.argv)

    # Set font modern bawaan sistem
    font = app.font()
    font.setFamily("Segoe UI")
    app.setFont(font)

    # Panggil Screen Manager
    window = ScreenManager()
    window.showMaximized()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
