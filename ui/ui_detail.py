from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QScrollArea, QWidget,
                             QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QColor
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import QByteArray


def build_star_svg(rating: float, star_size: int = 32, gap: int = 4) -> bytes:
    """
    Generate SVG 5 bintang dinamis sesuai nilai rating (0.0 – 5.0).
    - Bintang penuh  → kuning solid #E17726
    - Bintang setengah → separuh kuning, separuh abu
    - Bintang kosong → abu-abu #D1D5DB
    """
    total = 5
    width = total * star_size + (total - 1) * gap
    height = star_size

    # Path bintang 5 titik, dalam kotak 0,0 → 100,100 lalu discale
    # Titik bintang (cx=50, cy=50, outer=48, inner=19, 5 titik)
    import math
    def star_path(cx, cy, outer, inner):
        points = []
        for i in range(10):
            r = outer if i % 2 == 0 else inner
            angle = math.radians(-90 + i * 36)
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            points.append(f"{x:.2f},{y:.2f}")
        return "M " + " L ".join(points) + " Z"

    path_d = star_path(50, 50, 48, 20)
    s = star_size
    g = gap

    defs = ""
    stars_svg = ""

    for i in range(total):
        x_off = i * (s + g)
        fill_ratio = max(0.0, min(1.0, rating - i))  # 0.0, 0.x, atau 1.0

        uid = f"s{i}"

        if fill_ratio >= 0.99:
            # Bintang penuh
            stars_svg += (
                f'<g transform="translate({x_off},0) scale({s/100},{s/100})">'
                f'<path d="{path_d}" fill="#E17726"/>'
                f'</g>\n'
            )
        elif fill_ratio <= 0.01:
            # Bintang kosong
            stars_svg += (
                f'<g transform="translate({x_off},0) scale({s/100},{s/100})">'
                f'<path d="{path_d}" fill="#D1D5DB"/>'
                f'</g>\n'
            )
        else:
            # Bintang sebagian — pakai linearGradient
            pct = f"{fill_ratio*100:.1f}%"
            defs += (
                f'<linearGradient id="g{uid}" x1="0" y1="0" x2="1" y2="0">'
                f'<stop offset="{pct}" stop-color="#E17726"/>'
                f'<stop offset="{pct}" stop-color="#D1D5DB"/>'
                f'</linearGradient>\n'
            )
            stars_svg += (
                f'<g transform="translate({x_off},0) scale({s/100},{s/100})">'
                f'<path d="{path_d}" fill="url(#g{uid})"/>'
                f'</g>\n'
            )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        f'<defs>{defs}</defs>'
        f'{stars_svg}'
        f'</svg>'
    )
    return svg.encode("utf-8")


class StarRatingWidget(QSvgWidget):
    """Widget bintang dinamis berbasis SVG — tidak butuh file icon."""
    def __init__(self, rating: float, star_size: int = 32, parent=None):
        super().__init__(parent)
        self.star_size = star_size
        self.set_rating(rating)

    def set_rating(self, rating: float):
        svg_bytes = build_star_svg(rating, self.star_size)
        self.load(QByteArray(svg_bytes))
        # Hitung ukuran widget dari SVG
        total = 5
        gap = 4
        w = total * self.star_size + (total - 1) * gap
        self.setFixedSize(w, self.star_size)


class BookDetailDialog(QDialog):
    def __init__(self, book_data=None):
        super().__init__()
        self.setWindowTitle("Detail Buku")
        self.setFixedSize(750, 850)
        self.setStyleSheet("background-color: #FFFFFF; font-family: 'Segoe UI', sans-serif;")

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
                "Mengisahkan tentang Minke, seorang pemuda pribumi yang sekolah di HBS."
            )
        }
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(148, 163, 184, 0.5);
                min-height: 40px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(100, 116, 139, 0.9);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px; background: none;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)

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
            self.lbl_cover.setPixmap(
                pixmap.scaled(200, 300, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            )
            self.lbl_cover.setStyleSheet(
                "border-radius: 8px; border: 1px solid #E3E8EE; background-color: #FFFFFF;"
            )
            self.lbl_cover.setScaledContents(True)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 8)
        self.lbl_cover.setGraphicsEffect(shadow)

        # --- Judul, penulis, tahun, rating ---
        title_info_layout = QVBoxLayout()
        title_info_layout.setAlignment(Qt.AlignTop)
        title_info_layout.setSpacing(4)

        lbl_judul = QLabel(self.book.get("judul", "-"))
        lbl_judul.setStyleSheet(
            "font-size: 36px; font-weight: 900; color: #1A1F36; margin-bottom: 0px;"
        )
        lbl_judul.setWordWrap(True)

        lbl_penulis = QLabel(self.book.get("penulis", "-"))
        lbl_penulis.setStyleSheet(
            "font-size: 20px; font-weight: 600; color: #1A56DB; margin-top: 0px;"
        )

        lbl_tahun = QLabel(f"Tahun Terbit: {self.book.get('tahun', '-')}")
        lbl_tahun.setStyleSheet("font-size: 16px; color: #6B7280; margin-top: 0px;")

        # --- Bintang dinamis ---
        try:
            rating_val = float(self.book.get("rating", 0))
        except (ValueError, TypeError):
            rating_val = 0.0
        rating_str = f"{rating_val:.2f}".rstrip("0").rstrip(".")

        rating_row = QHBoxLayout()
        rating_row.setSpacing(10)
        rating_row.setAlignment(Qt.AlignLeft)

        star_widget = StarRatingWidget(rating_val, star_size=30)
        star_widget.setStyleSheet("background: transparent;")

        lbl_angka = QLabel(rating_str)
        lbl_angka.setStyleSheet(
            "font-size: 26px; font-weight: 800; color: #1A1F36; background: transparent;"
        )
        lbl_angka.setAlignment(Qt.AlignVCenter)

        rating_row.addWidget(star_widget)
        rating_row.addWidget(lbl_angka)

        title_info_layout.addWidget(lbl_judul)
        title_info_layout.addWidget(lbl_penulis)
        title_info_layout.addWidget(lbl_tahun)
        title_info_layout.addSpacing(8)
        title_info_layout.addLayout(rating_row)
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
        lbl_sinopsis_title.setStyleSheet(
            "font-size: 22px; font-weight: 800; color: #1A1F36; margin-top: 10px;"
        )

        lbl_sinopsis = QLabel(self.book.get("sinopsis", "Sinopsis tidak tersedia."))
        lbl_sinopsis.setStyleSheet("font-size: 17px; color: #4F566B; line-height: 1.6;")
        lbl_sinopsis.setWordWrap(True)

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
        container = QFrame()
        container.setStyleSheet("""
            QFrame { background-color: rgba(241, 245, 249, 0.6); border-radius: 12px; }
        """)
        l = QVBoxLayout(container)
        l.setContentsMargins(15, 12, 15, 12)
        l.setSpacing(2)
        lbl1 = QLabel(label)
        lbl1.setStyleSheet(
            "font-size: 13px; color: #64748B; font-weight: 600; background: transparent;"
        )
        lbl2 = QLabel(str(value))
        lbl2.setStyleSheet(
            "font-size: 17px; color: #0F172A; font-weight: 800; background: transparent;"
        )
        l.addWidget(lbl1)
        l.addWidget(lbl2)
        return container