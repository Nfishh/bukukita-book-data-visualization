from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class BookDetailDialog(QDialog):
    def __init__(self, book_data=None):
        super().__init__()
        self.setWindowTitle("Detail Buku")
        self.setFixedSize(600, 650)
        self.setStyleSheet("background-color: #FFFFFF; font-family: 'Segoe UI', sans-serif;")
        
        # Menerima data dummy untuk ditampilkan (Nanti dari file JSON)
        self.book = book_data if book_data else {
            "judul": "Judul Buku", "penulis": "Penulis", "tahun": "Tahun", 
            "kategori": "Kategori", "rating": "⭐ 0.0", "halaman": "0 Halaman", 
            "isbn": "000-0000000000",
            "sinopsis": "Sinopsis buku akan ditampilkan di area ini. Menjelaskan secara singkat mengenai plot dan tema utama yang diangkat oleh penulis di dalam karyanya."
        }
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # --- Judul & Penulis ---
        lbl_judul = QLabel(self.book["judul"])
        lbl_judul.setStyleSheet("font-size: 32px; font-weight: 900; color: #1A1F36;")
        lbl_judul.setWordWrap(True)
        
        lbl_penulis = QLabel(f"Oleh: {self.book['penulis']}  |  Terbit: {self.book['tahun']}")
        lbl_penulis.setStyleSheet("font-size: 18px; font-weight: 600; color: #1A56DB;")
        
        # --- Kartu Detail Info ---
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #F7F9FC; border-radius: 12px; border: 1px solid #E3E8EE;")
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(20, 20, 20, 20)
        
        # Info Kiri
        left_info = QVBoxLayout()
        left_info.addWidget(self.create_info_item("Kategori", self.book["kategori"]))
        left_info.addWidget(self.create_info_item("Halaman", self.book["halaman"]))
        
        # Info Kanan
        right_info = QVBoxLayout()
        right_info.addWidget(self.create_info_item("Rating Goodreads", self.book["rating"]))
        right_info.addWidget(self.create_info_item("ISBN", self.book["isbn"]))
        
        info_layout.addLayout(left_info)
        info_layout.addLayout(right_info)
        
        # --- Sinopsis ---
        lbl_sinopsis_title = QLabel("Sinopsis")
        lbl_sinopsis_title.setStyleSheet("font-size: 20px; font-weight: 800; color: #1A1F36; margin-top: 10px;")
        
        lbl_sinopsis = QLabel(self.book["sinopsis"])
        lbl_sinopsis.setStyleSheet("font-size: 16px; color: #4F566B; line-height: 1.6;")
        lbl_sinopsis.setWordWrap(True)
        lbl_sinopsis.setAlignment(Qt.AlignTop)
        
        # --- Tombol Tambah Koleksi ---
        self.btn_add_collection = QPushButton("🔖 Tambahkan ke My Collections")
        self.btn_add_collection.setFixedHeight(55)
        self.btn_add_collection.setCursor(Qt.PointingHandCursor)
        self.btn_add_collection.setStyleSheet("""
            QPushButton {
                background-color: #1A56DB;
                color: white;
                font-weight: bold;
                font-size: 18px;
                border-radius: 12px;
                border: none;
                margin-top: 20px;
            }
            QPushButton:hover { background-color: #1E40AF; }
        """)
        
        # --- Susun Layout ---
        layout.addWidget(lbl_judul)
        layout.addWidget(lbl_penulis)
        layout.addWidget(info_frame)
        layout.addWidget(lbl_sinopsis_title)
        layout.addWidget(lbl_sinopsis, 1) # Melar isi sisa ruang
        layout.addWidget(self.btn_add_collection)
        
    def create_info_item(self, label, value):
        container = QWidget()
        l = QVBoxLayout(container)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(2)
        
        lbl1 = QLabel(label)
        lbl1.setStyleSheet("font-size: 14px; color: #6B7280; font-weight: bold;")
        lbl2 = QLabel(value)
        lbl2.setStyleSheet("font-size: 18px; color: #1A1F36; font-weight: bold;")
        
        l.addWidget(lbl1)
        l.addWidget(lbl2)
        return container