from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QScrollArea, QWidget,
                             QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QColor

class BookDetailDialog(QDialog):
    def __init__(self, book_data=None):
        super().__init__()
        self.setWindowTitle("Detail Buku")
        self.setFixedSize(750, 850) 
        self.setStyleSheet("background-color: #FFFFFF; font-family: 'Segoe UI', sans-serif;")
        
        # FIX: Gunakan data nyata yang dikirim dari dashboard, fallback ke dummy jika None
        self.book = book_data if book_data else {
            "judul"    : "Bumi Manusia", 
            "penulis"  : "Pramoedya Ananta Toer", 
            "tahun"    : "1980", 
            "kategori" : "Fiksi", 
            "rating"   : "4.8",
            "halaman"  : "535 Halaman", 
            "isbn"     : "978-979-97312-3-5",
            "cover"    : "assets/covers/bumi_manusia.jpg", 
            "sinopsis" : (
                "Bumi Manusia merupakan buku pertama dari Tetralogi Buru. "
                "Mengisahkan tentang Minke, seorang pemuda pribumi yang sekolah di HBS, "
                "sekolah untuk orang Eropa dan kaum bangsawan."
            )
        }
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        
        # ==========================================
        # 1. HEADER SECTION (Cover + Judul)
        # ==========================================
        header_layout = QHBoxLayout()
        header_layout.setSpacing(30)
        
        self.lbl_cover = QLabel()
        self.lbl_cover.setFixedSize(200, 300)
        self.lbl_cover.setObjectName("coverImage")
        
        pixmap = QPixmap(self.book.get("cover", ""))
        if pixmap.isNull():
            self.lbl_cover.setText("No Cover\nAvailable")
            self.lbl_cover.setAlignment(Qt.AlignCenter)
            self.lbl_cover.setStyleSheet("""
                #coverImage {
                    background-color: #E5E7EB; color: #9CA3AF; font-weight: bold;
                    border-radius: 8px; border: 2px dashed #D1D5DB;
                }
            """)
        else:
            self.lbl_cover.setPixmap(pixmap.scaled(200, 300, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            self.lbl_cover.setStyleSheet("border-radius: 8px; border: 1px solid #E3E8EE; background-color: #FFFFFF;")
            self.lbl_cover.setScaledContents(True)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 8)
        self.lbl_cover.setGraphicsEffect(shadow)

        title_info_layout = QVBoxLayout()
        title_info_layout.setAlignment(Qt.AlignTop)
        title_info_layout.setSpacing(2)
        
        lbl_judul = QLabel(self.book.get("judul", "-"))
        lbl_judul.setStyleSheet("font-size: 36px; font-weight: 900; color: #1A1F36; margin-bottom: 0px;")
        lbl_judul.setWordWrap(True)
        
        lbl_penulis = QLabel(self.book.get("penulis", "-"))
        lbl_penulis.setStyleSheet("font-size: 20px; font-weight: 600; color: #1A56DB; margin-top: 0px;")
        
        lbl_tahun = QLabel(f"Tahun Terbit: {self.book.get('tahun', '-')}")
        lbl_tahun.setStyleSheet("font-size: 16px; color: #6B7280; margin-top: 0px;")
        
        # FIX: Rating bisa berupa float/string, tangani keduanya
        try:
            rating_val = float(self.book.get("rating", 0))
            rating_str = f"{rating_val:.1f}"
        except (ValueError, TypeError):
            rating_str = str(self.book.get("rating", "-"))

        bintang_html = "<span style='color: #E17726; font-size: 32px;'>★★★★½</span>"
        angka_html   = f"<span style='font-size: 28px; font-weight: 800; color: #1A1F36;'>  {rating_str}</span>"
        
        lbl_rating_gr = QLabel(bintang_html + angka_html)
        lbl_rating_gr.setStyleSheet("margin-top: 10px; background: transparent;")
        
        title_info_layout.addWidget(lbl_judul)
        title_info_layout.addWidget(lbl_penulis)
        title_info_layout.addWidget(lbl_tahun)
        title_info_layout.addWidget(lbl_rating_gr)
        title_info_layout.addStretch()
        
        header_layout.addWidget(self.lbl_cover)
        header_layout.addLayout(title_info_layout, 1)
        
        # ==========================================
        # 2. DETAIL METADATA
        # ==========================================
        info_layout = QHBoxLayout()
        info_layout.setSpacing(15)
        
        left_info = QVBoxLayout()
        left_info.setSpacing(12)
        left_info.addWidget(self.create_info_item("Kategori", self.book.get("kategori", "-")))
        left_info.addWidget(self.create_info_item("Jumlah Halaman", self.book.get("halaman", "-")))
        
        right_info = QVBoxLayout()
        right_info.setSpacing(12)
        right_info.addWidget(self.create_info_item("ISBN", self.book.get("isbn", "-")))
        right_info.addWidget(self.create_info_item("ID Referensi", self.book.get("id_buku", "-")))
        
        info_layout.addLayout(left_info)
        info_layout.addLayout(right_info)
        
        # ==========================================
        # 3. SINOPSIS & ACTION
        # ==========================================
        lbl_sinopsis_title = QLabel("Sinopsis")
        lbl_sinopsis_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #1A1F36; margin-top: 10px;")
        
        lbl_sinopsis = QLabel(self.book.get("sinopsis", "Sinopsis tidak tersedia."))
        lbl_sinopsis.setStyleSheet("font-size: 17px; color: #4F566B; line-height: 1.6;")
        lbl_sinopsis.setWordWrap(True)
        
        # FIX: btn_bookmark tersedia sebagai public attribute agar bisa
        # disambungkan ke _add_to_collection dari DashboardScreen
        self.btn_bookmark = QPushButton("Bookmark ke My Collections")
        self.btn_bookmark.setFixedHeight(60)
        self.btn_bookmark.setCursor(Qt.PointingHandCursor)
        self.btn_bookmark.setStyleSheet("""
            QPushButton {
                background-color: #1A56DB; color: white; font-weight: bold;
                font-size: 18px; border-radius: 12px; border: none; margin-top: 10px;
            }
            QPushButton:hover { background-color: #1E40AF; }
        """)
        
        layout.addLayout(header_layout)
        layout.addLayout(info_layout)
        layout.addWidget(lbl_sinopsis_title)
        layout.addWidget(lbl_sinopsis)
        layout.addWidget(self.btn_bookmark)
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
    def create_info_item(self, label, value):
        """Membuat kotak info terpisah yang melingkar & transparan."""
        container = QFrame()
        container.setStyleSheet("""
            QFrame { background-color: rgba(241, 245, 249, 0.6); border-radius: 12px; }
        """)
        
        l = QVBoxLayout(container)
        l.setContentsMargins(15, 12, 15, 12)
        l.setSpacing(2)
        
        lbl1 = QLabel(label)
        lbl1.setStyleSheet("font-size: 13px; color: #64748B; font-weight: 600; background: transparent;")
        lbl2 = QLabel(str(value))
        lbl2.setStyleSheet("font-size: 17px; color: #0F172A; font-weight: 800; background: transparent;")
        
        l.addWidget(lbl1)
        l.addWidget(lbl2)
        return container
