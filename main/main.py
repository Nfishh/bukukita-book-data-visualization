# main/main.py
import sys
import os

# --- JURUS GPS PYTHON ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from PyQt5.QtWidgets import QApplication

# 🚨 PERBAIKAN DI SINI: Hapus kata "main." di depannya!
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