import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

class BukuKitaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BukuKita - Manajemen & Visualisasi Data Buku")
        
        # --- UKURAN BARU YANG LEBIH COMPACT ---
        self.resize(850, 550) 
        
        # --- WIDGET UTAMA & LAYOUT DASAR ---
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- 1. SIDEBAR AREA (Kiri) ---
        sidebar = QFrame()
        sidebar.setFixedWidth(170) # Sidebar dikecilin proporsional
        sidebar.setStyleSheet("background-color: #2c3e50;") 
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 15)
        sidebar_layout.setAlignment(Qt.AlignTop)

        # Label Menu
        menu_label = QLabel("MAIN MENU")
        menu_label.setStyleSheet("color: #95a5a6; font-weight: bold; font-size: 11px;")
        sidebar_layout.addWidget(menu_label)
        sidebar_layout.addSpacing(15)

        # Style untuk tombol (Font dikecilin dikit biar pas)
        btn_style_active = """
            QPushButton {
                background-color: #1abc9c; color: white; border: none; 
                padding: 10px; border-radius: 6px; font-weight: bold; font-size: 12px;
            }
            QPushButton:hover { background-color: #16a085; }
        """
        btn_style_normal = """
            QPushButton {
                background-color: #34495e; color: white; border: none; 
                padding: 10px; border-radius: 6px; font-weight: bold; font-size: 12px;
                text-align: left; padding-left: 10px;
            }
            QPushButton:hover { background-color: #3498db; }
        """

        # Tombol Navigasi
        self.btn_scrape = QPushButton("🕷️ Auto-Scraper")
        self.btn_scrape.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_scrape.setStyleSheet(btn_style_active)
        sidebar_layout.addWidget(self.btn_scrape)
        sidebar_layout.addSpacing(8)

        self.btn_table = QPushButton("📖 Library View")
        self.btn_table.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_table.setStyleSheet(btn_style_normal)
        sidebar_layout.addWidget(self.btn_table)
        sidebar_layout.addSpacing(8)

        self.btn_crud = QPushButton("📝 Reading Tracker")
        self.btn_crud.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_crud.setStyleSheet(btn_style_normal)
        sidebar_layout.addWidget(self.btn_crud)
        sidebar_layout.addSpacing(8)

        self.btn_viz = QPushButton("📊 Analytics")
        self.btn_viz.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_viz.setStyleSheet(btn_style_normal)
        sidebar_layout.addWidget(self.btn_viz)

        # --- 2. KONTEN UTAMA (Kanan) ---
        content_area = QWidget()
        content_area.setStyleSheet("background-color: #ecf0f1;") 
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Header Atas
        header = QFrame()
        header.setFixedHeight(55) # Header dipendekin dikit
        header.setStyleSheet("background-color: #ffffff; border-bottom: 1px solid #bdc3c7;")
        header_layout = QHBoxLayout(header)
        
        title_label = QLabel("📚 BukuKita Dashboard")
        title_label.setStyleSheet("color: #2c3e50; font-weight: bold; font-size: 18px; border: none;")
        header_layout.addWidget(title_label)
        content_layout.addWidget(header)

        # Kanvas Putih 
        canvas_frame = QFrame()
        canvas_frame.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #bdc3c7;")
        canvas_layout = QVBoxLayout(canvas_frame)
        
        welcome_text = (
            "Selamat Datang di BukuKita!\n\n"
            "Area ini adalah ruang kerja utama.\n"
            "Nantinya, Tabel Data (Ziddan) dan Grafik Visualisasi (Fidella)\n"
            "akan di-render secara dinamis di dalam kotak putih ini."
        )
        welcome_label = QLabel(welcome_text)
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("color: #7f8c8d; font-size: 14px; border: none;")
        canvas_layout.addWidget(welcome_label)

        content_layout.addWidget(canvas_frame)
        content_layout.setContentsMargins(20, 20, 20, 20) 

        # Masukkan ke layout utama
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area)

if __name__ == "__main__":
    # --- JURUS PAMUNGKAS ANTI-BLUR PYQT5 ---
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    # ---------------------------------------

    app = QApplication(sys.argv)
    window = BukuKitaApp()
    window.show()
    sys.exit(app.exec_())