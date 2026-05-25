# ui/ui_dashboard.py
# Developer : Muhammad Iqbal 251524114
# Deskripsi : Halaman utama (dashboard) BukuKita setelah user login.
#             Menampilkan katalog buku, statistik bacaan personal
#             (status_count untuk Belum Dibaca, Sedang Membaca, Selesai
#             Dibaca, Drop), filter berdasarkan status, serta navigasi ke
#             halaman detail buku dan profil user. Memuat data secara
#             lazy/debounced untuk performa optimal pada koleksi besar.


import os
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFrame, QTableWidget,
                             QTableWidgetItem, QHeaderView, QSpacerItem, QSizePolicy,
                             QStackedWidget, QButtonGroup, QComboBox, QMenu, QAction,
                             QMessageBox, QScrollArea, QDialog, QGridLayout)
from PyQt5.QtCore import Qt, QSize, QDate, QPoint, QTimer, pyqtSignal, QRect
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor, QPainter, QFontMetrics
from PyQt5.QtSvg import QSvgWidget

# FIX: Import path disesuaikan dengan struktur folder ui/
from ui.ui_detail import BookDetailDialog
from ui.data_viz import DataVisualizer
from ui.ui_profile import ProfileDialog, HelpDialog, SettingsDialog

class StarRatingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 24)
        self.value = 0.0
    
    def set_value(self, val):
        self.value = val
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        font = QFont("Segoe UI", 16)
        painter.setFont(font)
        
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance("★★★★★")
        text_rect = QRect(0, 0, text_width, self.height())
        
        painter.setPen(QColor("#D1D5DB"))
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, "★★★★★")
        
        clip_width = int((self.value / 5.0) * text_width)
        painter.setClipRect(0, 0, clip_width, self.height())
        painter.setPen(QColor("#F59E0B"))
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, "★★★★★")

# ==========================================
# Custom Modern Calendar Popup
# ==========================================
def _make_round_pixmap(path, size):
    """Fungsi helper khusus Dashboard untuk memotong gambar jadi bulat"""
    from PyQt5.QtGui import QPixmap, QPainter, QPainterPath
    from PyQt5.QtCore import Qt
    
    src = QPixmap(path)
    if src.isNull():
        return QPixmap()
    src = src.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    x = (src.width() - size) // 2
    y = (src.height() - size) // 2
    src = src.copy(x, y, size, size)

    result = QPixmap(size, size)
    result.fill(Qt.transparent)
    painter = QPainter(result)
    painter.setRenderHint(QPainter.Antialiasing)
    path_clip = QPainterPath()
    path_clip.addEllipse(0, 0, size, size)
    painter.setClipPath(path_clip)
    painter.drawPixmap(0, 0, src)
    painter.end()
    return result

class ModernCalendarPopup(QDialog):
    """Popup kalender modern pengganti QCalendarWidget bawaan Qt yang jadul."""

    def __init__(self, current_date: QDate = None, parent=None):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.selected_date = current_date or QDate.currentDate()
        self._view_year  = self.selected_date.year()
        self._view_month = self.selected_date.month()
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)
        outer.setSpacing(0)

        self._card = QFrame()
        self._card.setObjectName("calCard")
        self._card.setStyleSheet("""
            QFrame#calCard {
                background-color: #FFFFFF;
                border-radius: 16px;
                border: 1px solid #E2E8F0;
            }
        """)
        from PyQt5.QtWidgets import QGraphicsDropShadowEffect
        from PyQt5.QtGui import QColor as _QColor
        sh = QGraphicsDropShadowEffect()
        sh.setBlurRadius(24)
        sh.setColor(_QColor(0, 0, 0, 35))
        sh.setOffset(0, 6)
        self._card.setGraphicsEffect(sh)

        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(12)

        # --- Header ---
        header = QHBoxLayout()
        header.setSpacing(6)
        self._btn_prev = self._nav_btn("\u2039")
        self._btn_prev.clicked.connect(self._prev_month)
        self._lbl_month = QLabel()
        self._lbl_month.setAlignment(Qt.AlignCenter)
        self._lbl_month.setStyleSheet(
            "font-size: 17px; font-weight: 800; color: #1A1F36; background: transparent;"
        )
        self._btn_next = self._nav_btn("\u203a")
        self._btn_next.clicked.connect(self._next_month)
        self._btn_today = QPushButton("Hari ini")
        self._btn_today.setCursor(Qt.PointingHandCursor)
        self._btn_today.setFixedHeight(32)
        self._btn_today.setStyleSheet("""
            QPushButton {
                background-color: #EFF6FF; color: #1A56DB;
                border: 1.5px solid #BFDBFE; border-radius: 8px;
                font-size: 13px; font-weight: 700; padding: 0 12px;
            }
            QPushButton:hover { background-color: #DBEAFE; }
        """)
        self._btn_today.clicked.connect(self._go_today)
        header.addWidget(self._btn_prev)
        header.addWidget(self._lbl_month, 1)
        header.addWidget(self._btn_next)
        header.addSpacing(8)
        header.addWidget(self._btn_today)
        card_layout.addLayout(header)

        # --- Nama hari ---
        day_names = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
        day_row = QHBoxLayout()
        day_row.setSpacing(0)
        for d in day_names:
            lbl = QLabel(d)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedWidth(44)
            lbl.setStyleSheet(
                "font-size: 12px; font-weight: 700; background: transparent; padding: 4px 0;"
                + ("color: #EF4444;" if d in ("Sab", "Min") else "color: #94A3B8;")
            )
            day_row.addWidget(lbl)
        card_layout.addLayout(day_row)

        # --- Grid tanggal ---
        self._grid_widget = QWidget()
        self._grid_widget.setStyleSheet("background: transparent;")
        self._grid = QGridLayout(self._grid_widget)
        self._grid.setSpacing(4)
        self._grid.setContentsMargins(0, 0, 0, 0)
        card_layout.addWidget(self._grid_widget)

        outer.addWidget(self._card)
        self._refresh_grid()

    def _prev_month(self):
        self._view_month -= 1
        if self._view_month < 1:
            self._view_month = 12
            self._view_year -= 1
        self._refresh_grid()

    def _next_month(self):
        self._view_month += 1
        if self._view_month > 12:
            self._view_month = 1
            self._view_year += 1
        self._refresh_grid()

    def _go_today(self):
        today = QDate.currentDate()
        self._view_year  = today.year()
        self._view_month = today.month()
        self._pick_date(today)

    def _refresh_grid(self):
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        bulan = ["","Januari","Februari","Maret","April","Mei","Juni",
                 "Juli","Agustus","September","Oktober","November","Desember"]
        self._lbl_month.setText(f"{bulan[self._view_month]}  {self._view_year}")

        first_day = QDate(self._view_year, self._view_month, 1)
        start_col = first_day.dayOfWeek() - 1  # 0=Sen
        days_in_month = first_day.daysInMonth()
        today = QDate.currentDate()

        for d in range(1, days_in_month + 1):
            date     = QDate(self._view_year, self._view_month, d)
            cell_idx = d - 1 + start_col
            row      = cell_idx // 7
            col      = cell_idx % 7
            is_sel   = (date == self.selected_date)
            is_today = (date == today)
            is_wknd  = col >= 5

            btn = QPushButton(str(d))
            btn.setFixedSize(40, 36)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFlat(True)

            if is_sel:
                style = ("QPushButton { background-color: #1A56DB; color: #FFFFFF;"
                         "border-radius: 10px; font-size: 14px; font-weight: 800; border: none; }")
            elif is_today:
                style = ("QPushButton { background-color: #EFF6FF; color: #1A56DB;"
                         "border-radius: 10px; font-size: 14px; font-weight: 700;"
                         "border: 1.5px solid #93C5FD; }"
                         "QPushButton:hover { background-color: #DBEAFE; }")
            elif is_wknd:
                style = ("QPushButton { background: transparent; color: #EF4444;"
                         "border-radius: 10px; font-size: 14px; border: none; }"
                         "QPushButton:hover { background-color: #FEF2F2; }")
            else:
                style = ("QPushButton { background: transparent; color: #374151;"
                         "border-radius: 10px; font-size: 14px; border: none; }"
                         "QPushButton:hover { background-color: #F1F5F9; }")

            btn.setStyleSheet(style)
            btn.clicked.connect(lambda _, dt=date: self._pick_date(dt))
            self._grid.addWidget(btn, row, col)

    def _pick_date(self, date: QDate):
        self.selected_date = date
        self.accept()

    def _nav_btn(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedSize(34, 34)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton { font-size: 20px; font-weight: 700; color: #64748B;
                background: transparent; border: none; border-radius: 8px; }
            QPushButton:hover { background-color: #F1F5F9; color: #1A1F36; }
        """)
        return btn

    @classmethod
    def get_date(cls, current_date: QDate, anchor_widget, parent=None):
        popup = cls(current_date, parent)
        popup.setFixedWidth(340)
        # Center popup horizontal terhadap anchor, muncul tepat di bawahnya
        popup_w = 340
        anchor_global = anchor_widget.mapToGlobal(QPoint(0, 0))
        x = anchor_global.x() + anchor_widget.width() // 2 - popup_w // 2
        y = anchor_global.y() + anchor_widget.height() + 4
        popup.move(QPoint(x, y))
        if popup.exec_() == QDialog.Accepted:
            return popup.selected_date
        return None




# ==========================================
# Class Khusus Kartu Statistik Animasi
# ==========================================
class StatCard(QFrame):
    """Custom Widget QFrame yang punya interaksi layaknya tombol melayang"""
    def __init__(self, title, value, color_code, click_callback):
        super().__init__()
        self.color_code = color_code
        self.click_callback = click_callback
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 20px; color: #4F566B; font-weight: 600; border: none; background: transparent;") 
        
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet("font-size: 34px; font-weight: 900; color: #1A1F36; border: none; background: transparent;") 
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        
        self.setStyleSheet(self.default_style())
        
    def default_style(self):
        return f"""
            QFrame {{
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E3E8EE;
                border-left: 6px solid {self.color_code};
                margin-top: 6px;
                margin-bottom: 0px;
            }}
        """

    def hover_style(self):
        return f"""
            QFrame {{
                background-color: #F0F4F8;
                border-radius: 12px;
                border: 1px solid #94A3B8;
                border-left: 6px solid {self.color_code};
                margin-top: 0px;   
                margin-bottom: 6px; 
            }}
        """

    def enterEvent(self, event):
        self.setStyleSheet(self.hover_style())
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self.default_style())
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: #E2E8F0;
                    border-radius: 12px;
                    border: 1px solid #94A3B8;
                    border-left: 6px solid {self.color_code};
                    margin-top: 8px;
                    margin-bottom: -2px;
                }}
            """)
            self.click_callback()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.underMouse():
            self.setStyleSheet(self.hover_style())
        else:
            self.setStyleSheet(self.default_style())
        super().mouseReleaseEvent(event)


# ==========================================
# KELAS UTAMA DASHBOARD
# ==========================================
class DashboardScreen(QWidget):
    def __init__(self, data_manager=None, book_manager=None, rating_system=None):
        super().__init__()
        self.data_manager = data_manager
        self.book_manager = book_manager
        self.rating_system = rating_system
        self.current_user = None

        # Cache data buku untuk filtering tanpa baca ulang JSON
        self._all_books_cache = []
        # Data profil user aktif
        self._user_data: dict = {}
        # --- FIX: VARIABEL PAGINASI ---
        self._filtered_books_cache = [] 
        self.current_page = 1
        self.items_per_page = 50
        # Cache icon cover agar tidak dibaca ulang dari disk tiap filter
        self._cover_icon_cache: dict = {}
        self._default_icon = None
        # Debounce timer — tunda filter 300ms setelah user berhenti mengetik
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._do_filter_library)

        self.setStyleSheet("""
            QWidget {
                background-color: #F7F9FC; 
                font-family: 'Segoe UI', sans-serif;
            }
            QScrollBar:vertical {
                border: none; 
                background: transparent; 
                width: 14px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(148, 163, 184, 0.4);
                min-height: 40px; 
                border-radius: 7px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(100, 116, 139, 0.8);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px; background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ==========================================
        # 1. SIDEBAR (KIRI)
        # ==========================================
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(360)
        sidebar.setStyleSheet("#sidebar { background-color: transparent; border: none; }")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 10, 20, 30)
        sidebar_layout.setSpacing(10)
        
        logo_layout = QVBoxLayout() 
        logo_layout.setAlignment(Qt.AlignCenter)
        logo_layout.setSpacing(0) 
        logo_layout.setContentsMargins(0, -40, 0, 0)
        
        self.logo_svg = QSvgWidget("assets/images/logo_blue.svg")
        self.logo_svg.setFixedSize(320, 140) 
        self.logo_svg.setStyleSheet("background-color: transparent;")
        
        lbl_brand = QLabel("BukuKita")
        lbl_brand.setStyleSheet("background-color: transparent; font-size: 30px; font-weight: 900; color: #1A1F36;") 
        lbl_brand.setAlignment(Qt.AlignCenter)
        
        logo_layout.addWidget(self.logo_svg, alignment=Qt.AlignCenter)
        logo_layout.addWidget(lbl_brand, alignment=Qt.AlignCenter)
        
        sidebar_layout.addLayout(logo_layout)
        sidebar_layout.addSpacing(30)
        
        menu_style = """
            QPushButton {
                text-align: left; padding: 15px 20px; font-size: 22px; font-weight: 600;
                color: #4F566B; background-color: transparent; border-radius: 10px; border: none;
            }
            QPushButton:hover { background-color: #E3E8EE; color: #1A1F36; }
            QPushButton:checked { background-color: #FFFFFF; color: #1A56DB; border: 1px solid #E3E8EE; }
        """
        
        self.menu_group = QButtonGroup(self)
        self.menu_group.setExclusive(True)
        
        self.btn_menu_dash = QPushButton("  Dashboard") 
        self.btn_menu_dash.setIcon(QIcon("assets/icons/ic_dashboard.svg"))
        self.btn_menu_dash.setIconSize(QSize(28, 28)) 
        self.btn_menu_dash.setStyleSheet(menu_style)
        self.btn_menu_dash.setCheckable(True)
        self.btn_menu_dash.setChecked(True) 
        self.btn_menu_dash.setCursor(Qt.PointingHandCursor)
        
        self.btn_menu_lib = QPushButton("  Library") 
        self.btn_menu_lib.setIcon(QIcon("assets/icons/ic_library.svg"))
        self.btn_menu_lib.setIconSize(QSize(28, 28)) 
        self.btn_menu_lib.setStyleSheet(menu_style)
        self.btn_menu_lib.setCheckable(True)
        self.btn_menu_lib.setCursor(Qt.PointingHandCursor)
        
        self.btn_menu_col = QPushButton("  My Collections") 
        self.btn_menu_col.setIcon(QIcon("assets/icons/ic_collections.svg"))
        self.btn_menu_col.setIconSize(QSize(28, 28)) 
        self.btn_menu_col.setStyleSheet(menu_style)
        self.btn_menu_col.setCheckable(True)
        self.btn_menu_col.setCursor(Qt.PointingHandCursor)
        
        self.btn_menu_analytics = QPushButton("  Analytics") 
        self.btn_menu_analytics.setIcon(QIcon("assets/icons/ic_analytics.svg"))
        self.btn_menu_analytics.setIconSize(QSize(28, 28)) 
        self.btn_menu_analytics.setStyleSheet(menu_style)
        self.btn_menu_analytics.setCheckable(True)
        self.btn_menu_analytics.setCursor(Qt.PointingHandCursor)
        
        self.menu_group.addButton(self.btn_menu_dash)
        self.menu_group.addButton(self.btn_menu_lib)
        self.menu_group.addButton(self.btn_menu_col)
        self.menu_group.addButton(self.btn_menu_analytics) 
        
        sidebar_layout.addWidget(self.btn_menu_dash)
        sidebar_layout.addWidget(self.btn_menu_lib)
        sidebar_layout.addWidget(self.btn_menu_col)
        sidebar_layout.addWidget(self.btn_menu_analytics) 
        
        sidebar_layout.addStretch()
        
        self.btn_logout = QPushButton("  Keluar")
        self.btn_logout.setIcon(QIcon("assets/icons/ic_logout.svg"))
        self.btn_logout.setIconSize(QSize(28, 28)) 
        self.btn_logout.setStyleSheet("""
            QPushButton { text-align: left; padding: 15px 20px; font-size: 22px; font-weight: 600; color: #DC2626; background-color: transparent; border-radius: 10px; border: none; }
            QPushButton:hover { background-color: #FEF2F2; }
        """)
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        sidebar_layout.addWidget(self.btn_logout)
        
        # ==========================================
        # 2. MAIN CONTENT
        # ==========================================
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: transparent;")
        
        self.page_overview     = self.build_overview_page()
        self.page_library      = self.build_library_page()
        self.page_collections  = self.build_collections_page()
        self.page_analytics    = self.build_analytics_page()
        
        self.content_stack.addWidget(self.page_overview)    # index 0
        self.content_stack.addWidget(self.page_library)     # index 1
        self.content_stack.addWidget(self.page_collections) # index 2
        self.content_stack.addWidget(self.page_analytics)   # index 3
        
        self.btn_menu_dash.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))
        self.btn_menu_lib.clicked.connect(lambda: self.content_stack.setCurrentIndex(1))
        self.btn_menu_col.clicked.connect(lambda: self.content_stack.setCurrentIndex(2))
        self.btn_menu_analytics.clicked.connect(lambda: (
            self.content_stack.setCurrentIndex(3),
            self._rebuild_analytics_charts()
        ))
        
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_stack, 1) 
        
    # ==========================================
    # PAGES
    # ==========================================
    def build_overview_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        header_layout = QHBoxLayout()
        lbl_title = QLabel("Dashboard") 
        lbl_title.setStyleSheet("font-size: 38px; font-weight: 800; color: #1A1F36;") 
        
        self.lbl_welcome = QLabel("Selamat datang!")
        self.lbl_welcome.setStyleSheet("font-size: 20px; color: #6B7280; margin-top: 4px;")

        title_vbox = QVBoxLayout()
        title_vbox.addWidget(lbl_title)
        title_vbox.addWidget(self.lbl_welcome)
        
        user_container = QWidget()
        user_layout = QHBoxLayout(user_container)
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setSpacing(12)
        
        self.lbl_top_user_name = QLabel()
        self.lbl_top_user_name.setStyleSheet("font-size: 16px; font-weight: 700; color: #1A1F36;")
        self.lbl_top_user_name.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.btn_user = QPushButton()
        self.btn_user.setIcon(QIcon("assets/icons/ic_user.svg"))
        self.btn_user.setIconSize(QSize(30, 30))
        self.btn_user.setFixedSize(50, 50)
        self.btn_user.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E3E8EE; border-radius: 25px;")
        self.btn_user.setCursor(Qt.PointingHandCursor)
        self.btn_user.clicked.connect(self._show_user_popup)
        
        user_layout.addWidget(self.lbl_top_user_name)
        user_layout.addWidget(self.btn_user)

        header_layout.addLayout(title_vbox)
        header_layout.addStretch()
        header_layout.addWidget(user_container)
        
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.card_total    = StatCard("Total Koleksi",   "0 Buku", "#1A56DB", self.btn_menu_col.click)
        self.card_reading  = StatCard("Sedang Dibaca",   "0 Buku", "#059669", self.btn_menu_col.click)
        self.card_finished = StatCard("Selesai Dibaca",  "0 Buku", "#D97706", self.btn_menu_col.click)
        self.card_drop     = StatCard("Drop",            "0 Buku", "#6B7280", self.btn_menu_col.click)
        
        stats_layout.addWidget(self.card_total)
        stats_layout.addWidget(self.card_reading)
        stats_layout.addWidget(self.card_finished)
        stats_layout.addWidget(self.card_drop)
        
        table_container = QFrame()
        table_container.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E3E8EE;")
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(25, 25, 25, 25)
        
        lbl_table_title = QLabel("Koleksi Terbaru")
        lbl_table_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1A1F36; border: none;") 
        
        self.table_dash = QTableWidget(0, 5) 
        self.table_dash.setHorizontalHeaderLabels(["Judul Buku", "Penulis", "Tahun", "Rating", "Status"])
        self.table_dash.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_dash.setEditTriggers(QTableWidget.NoEditTriggers) 
        self.table_dash.setFocusPolicy(Qt.NoFocus)
        self.table_dash.setShowGrid(False)
        self.table_dash.horizontalHeader().setSectionsClickable(False)
        self.table_dash.verticalHeader().setDefaultSectionSize(60)
        self.table_dash.verticalHeader().setVisible(False) 
        self.table_dash.setStyleSheet(self._table_stylesheet())
        
        table_layout.addWidget(lbl_table_title)
        table_layout.addSpacing(15)
        table_layout.addWidget(self.table_dash)
        
        layout.addLayout(header_layout)
        layout.addLayout(stats_layout)
        layout.addWidget(table_container)
        
        return page

    def build_library_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        header_layout = QHBoxLayout()
        lbl_title = QLabel("Library")
        lbl_title.setStyleSheet("font-size: 38px; font-weight: 800; color: #1A1F36;")
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(15)
        
        self.search_bar_lib = QLineEdit()
        self.search_bar_lib.setPlaceholderText("Cari judul atau penulis...")
        self.search_bar_lib.setFixedHeight(50)
        self.search_bar_lib.setFixedWidth(350)
        self.search_bar_lib.setStyleSheet("""
            QLineEdit { background-color: #FFFFFF; border: 1px solid #E3E8EE; border-radius: 25px; padding: 0 20px; font-size: 18px; color: #1A1F36; }
            QLineEdit:focus { border: 2px solid #1A56DB; }
        """)
        # Debounce: tunda filter 300ms setelah user berhenti ketik
        self.search_bar_lib.textChanged.connect(
            lambda: self._search_timer.start(300)
        )
        
        self.combo_filter_lib = QComboBox()
        self.combo_filter_lib.addItems(["Semua Kategori", "Fiksi", "Non-Fiksi", "Romance", "Mystery", "Science Fiction", "Fantasy", "Biography", "History"])
        self.combo_filter_lib.setFixedHeight(50)
        self.combo_filter_lib.setFixedWidth(220)
        self.combo_filter_lib.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                border: 1.5px solid #E3E8EE;
                border-radius: 25px;
                padding: 0 20px;
                font-size: 18px;
                font-weight: bold;
                color: #4F566B; 
            }
            QComboBox:hover { border: 1.5px solid #1A56DB; color: #1A56DB; }
            QComboBox::drop-down { border: none; width: 40px; }
            QComboBox::down-arrow { image: url('assets/icons/ic_chevron_down.svg'); width: 20px; height: 20px; }
            QComboBox QAbstractItemView {
                border: 1px solid #E3E8EE;
                border-radius: 8px;
                background-color: #FFFFFF;
                selection-background-color: #EFF6FF;
                selection-color: #1A56DB;
                outline: none;
            }
            QComboBox QAbstractItemView::item { min-height: 45px; padding: 10px; }
        """)
        # Combo langsung filter (tidak perlu debounce, user harus klik)
        self.combo_filter_lib.currentTextChanged.connect(self._filter_library)
        
        toolbar_layout.addWidget(self.search_bar_lib)
        toolbar_layout.addWidget(self.combo_filter_lib)
        toolbar_layout.addStretch()
        
        table_container = QFrame()
        table_container.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E3E8EE;")
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(25, 25, 25, 25)
        
        self.table_lib = QTableWidget(0, 6) 
        self.table_lib.setHorizontalHeaderLabels(["Judul Buku", "Penulis", "Tahun", "Kategori", "Rating", "Aksi"])
        self.table_lib.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_lib.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table_lib.setEditTriggers(QTableWidget.NoEditTriggers) 
        self.table_lib.setFocusPolicy(Qt.NoFocus)
        self.table_lib.setShowGrid(False)
        self.table_lib.horizontalHeader().setSectionsClickable(False)
        self.table_lib.setIconSize(QSize(35, 50))
        self.table_lib.verticalHeader().setDefaultSectionSize(75)
        self.table_lib.verticalHeader().setVisible(False)
        self.table_lib.setStyleSheet(self._table_stylesheet())
        # Klik sel judul (col 0) → buka detail buku
        self.table_lib.cellClicked.connect(self._on_lib_cell_clicked)
        
        table_layout.addWidget(self.table_lib)
        
        self.pagination_layout = QHBoxLayout()
        self.btn_prev_page = QPushButton("« Sebelumnya")
        self.btn_prev_page.setCursor(Qt.PointingHandCursor)
        self.btn_prev_page.setStyleSheet("QPushButton { background-color: #E3E8EE; color: #1A1F36; border-radius: 6px; padding: 8px 15px; font-weight: bold; border: none; } QPushButton:hover { background-color: #CBD5E1; }")
        self.btn_prev_page.clicked.connect(self._prev_page)

        self.lbl_page_info = QLabel("Halaman 1 dari 1")
        self.lbl_page_info.setAlignment(Qt.AlignCenter)
        self.lbl_page_info.setStyleSheet("font-weight: 800; font-size: 16px; color: #4F566B;")

        self.btn_next_page = QPushButton("Selanjutnya »")
        self.btn_next_page.setCursor(Qt.PointingHandCursor)
        self.btn_next_page.setStyleSheet(self.btn_prev_page.styleSheet())
        self.btn_next_page.clicked.connect(self._next_page)

        self.pagination_layout.addWidget(self.btn_prev_page)
        self.pagination_layout.addStretch()
        self.pagination_layout.addWidget(self.lbl_page_info)
        self.pagination_layout.addStretch()
        self.pagination_layout.addWidget(self.btn_next_page)

        table_layout.addLayout(self.pagination_layout)

        layout.addLayout(header_layout)
        layout.addLayout(toolbar_layout)
        layout.addWidget(table_container, 1) 
        
        return page

    def build_collections_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        
        header_layout = QHBoxLayout()
        title_layout = QVBoxLayout()
        lbl_title = QLabel("My Collections")
        lbl_title.setStyleSheet("font-size: 38px; font-weight: 800; color: #1A1F36;")
        lbl_desc = QLabel("Kelola rak bukumu, berikan rating, dan catat sentimen/ulasan pribadimu di sini.")
        lbl_desc.setStyleSheet("font-size: 18px; color: #6B7280; margin-top: 5px;")
        title_layout.addWidget(lbl_title)
        title_layout.addWidget(lbl_desc)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        crud_card = QFrame()
        crud_card.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E3E8EE; border-left: 6px solid #D97706;") 
        crud_layout = QVBoxLayout(crud_card)
        crud_layout.setContentsMargins(25, 25, 25, 25)
        crud_layout.setSpacing(15)
        
        lbl_crud_title = QLabel("Detail My Collections")
        lbl_crud_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1A1F36; border: none;")
        
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(15)
        
        self.input_col_title = QLineEdit()
        self.input_col_title.setPlaceholderText("Klik area tabel untuk memilih judul")
        self.input_col_title.setReadOnly(True) 
        self.input_col_title.setFixedHeight(45)
        self.input_col_title.setStyleSheet("""
            QLineEdit { 
                border: none; 
                background-color: transparent; 
                font-size: 24px; 
                font-weight: 800; 
                color: #1A1F36; 
            }
        """)
        
        def _wrap(title, w):
            lay = QVBoxLayout()
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setSpacing(6)
            lbl = QLabel(title)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #1E293B; border: none; background: transparent;")
            lay.addWidget(lbl)
            lay.addWidget(w)
            wrapper = QWidget()
            wrapper.setStyleSheet("background: transparent; border: none;")
            wrapper.setLayout(lay)
            return wrapper

        self.combo_status = QComboBox()
        self.combo_status.addItems(["Sedang Membaca", "Selesai Dibaca", "Belum Dibaca", "Drop"])
        self.combo_status.setFixedHeight(45)
        self.combo_status.setFixedWidth(200)
        self.combo_status.currentTextChanged.connect(self._on_status_changed)
        status_wrap = _wrap("Status", self.combo_status)
        
        # Custom date picker: QLineEdit + tombol kalender modern
        self._date_container = QFrame()
        date_container = self._date_container
        date_container.setFixedHeight(45)
        date_container.setFixedWidth(180)
        date_container.setStyleSheet("""
            QFrame {
                border: 1.5px solid #E3E8EE;
                border-radius: 8px;
                background-color: rgba(247, 249, 252, 0.7);
            }
            QFrame:focus-within {
                border: 2px solid #1A56DB;
                background-color: #FFFFFF;
            }
        """)
        date_inner = QHBoxLayout(date_container)
        date_inner.setContentsMargins(10, 0, 4, 0)
        date_inner.setSpacing(4)

        self.input_col_date = QLineEdit()
        self.input_col_date.setPlaceholderText("Tanggal Mulai")
        self.input_col_date.setReadOnly(True)
        self.input_col_date.setStyleSheet("""
            QLineEdit {
                border: none; background: transparent;
                font-size: 15px; color: #374151; font-weight: 600;
            }
        """)

        self._btn_cal = QPushButton()
        self._btn_cal.setIcon(QIcon("assets/icons/ic_calendar.svg"))
        self._btn_cal.setIconSize(QSize(25, 25))
        self._btn_cal.setFixedSize(35, 35)
        self._btn_cal.setCursor(Qt.PointingHandCursor)
        self._btn_cal.setStyleSheet("""
            QPushButton {
                background: transparent; border: none;
                font-size: 16px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #EFF6FF; }
        """)
        self._btn_cal.clicked.connect(self._open_calendar)

        date_inner.addWidget(self.input_col_date)
        date_inner.addWidget(self._btn_cal)

        # Date selesai — struktur identik dengan date_container
        self._date_end_container = QFrame()
        date_end_container = self._date_end_container
        date_end_container.setFixedHeight(45)
        date_end_container.setFixedWidth(180)
        date_end_container.setStyleSheet("""
            QFrame {
                border: 1.5px solid #E3E8EE;
                border-radius: 8px;
                background-color: rgba(247, 249, 252, 0.7);
            }
            QFrame:focus-within {
                border: 2px solid #1A56DB;
                background-color: #FFFFFF;
            }
        """)
        date_end_inner = QHBoxLayout(date_end_container)
        date_end_inner.setContentsMargins(10, 0, 4, 0)
        date_end_inner.setSpacing(4)

        self.input_col_date_end = QLineEdit()
        self.input_col_date_end.setPlaceholderText("Tanggal Selesai")
        self.input_col_date_end.setReadOnly(True)
        self.input_col_date_end.setStyleSheet("""
            QLineEdit {
                border: none; background: transparent;
                font-size: 15px; color: #374151; font-weight: 600;
            }
        """)

        self._btn_cal_end = QPushButton()
        self._btn_cal_end.setIcon(QIcon("assets/icons/ic_calendar.svg"))
        self._btn_cal_end.setIconSize(QSize(25, 25))
        self._btn_cal_end.setFixedSize(35, 35)
        self._btn_cal_end.setCursor(Qt.PointingHandCursor)
        self._btn_cal_end.setStyleSheet("""
            QPushButton { background: transparent; border: none; border-radius: 6px; }
            QPushButton:hover { background-color: #EFF6FF; }
        """)
        self._btn_cal_end.clicked.connect(self._open_calendar_end)

        date_end_inner.addWidget(self.input_col_date_end)
        date_end_inner.addWidget(self._btn_cal_end)

        self.input_col_rating = QLineEdit()
        self.input_col_rating.setPlaceholderText("1.0 – 5.0 (Selesai dulu)")
        self.input_col_rating.setFixedHeight(45)
        self.input_col_rating.setFixedWidth(150)
        
        rating_widget_inner = QWidget()
        rating_widget_inner.setStyleSheet("background: transparent; border: none;")
        inner_lay = QVBoxLayout(rating_widget_inner)
        inner_lay.setContentsMargins(0, 0, 0, 0)
        inner_lay.setSpacing(4)
        
        self.star_widget = StarRatingWidget()
        inner_lay.addWidget(self.star_widget, alignment=Qt.AlignCenter)
        inner_lay.addWidget(self.input_col_rating)
        
        rating_wrap = _wrap("Rating", rating_widget_inner)
        
        self.input_col_rating.textChanged.connect(self._on_rating_text_changed)
        
        row1_layout.addWidget(self.input_col_title, 1, alignment=Qt.AlignBottom)
        row1_layout.addWidget(status_wrap, alignment=Qt.AlignBottom)
        row1_layout.addWidget(_wrap("Tanggal Mulai", date_container), alignment=Qt.AlignBottom)
        row1_layout.addWidget(_wrap("Tanggal Selesai", date_end_container), alignment=Qt.AlignBottom)
        row1_layout.addWidget(rating_wrap, alignment=Qt.AlignBottom)
        
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(15)
        
        self.input_col_notes = QLineEdit()
        self.input_col_notes.setPlaceholderText("Tulis anotasi, kesan, atau ulasan pribadimu tentang buku ini...")
        self.input_col_notes.setFixedHeight(45)
        
        btn_style = "QPushButton { color: white; font-weight: bold; font-size: 16px; border-radius: 8px; padding: 0 20px; border: none;}"
        
        self.btn_col_save = QPushButton("Simpan")
        self.btn_col_save.setFixedHeight(45)
        self.btn_col_save.setCursor(Qt.PointingHandCursor)
        self.btn_col_save.setStyleSheet(btn_style + "QPushButton { background-color: #1A56DB; } QPushButton:hover { background-color: #1E40AF; }")
        self.btn_col_save.clicked.connect(self._save_collection_edit)
        
        self.btn_col_delete = QPushButton("Hapus")
        self.btn_col_delete.setFixedHeight(45)
        self.btn_col_delete.setCursor(Qt.PointingHandCursor)
        self.btn_col_delete.setStyleSheet(btn_style + "QPushButton { background-color: #DC2626; } QPushButton:hover { background-color: #B91C1C; }")
        self.btn_col_delete.clicked.connect(self._delete_collection_entry)
        
        row2_layout.addWidget(self.input_col_notes)
        row2_layout.addWidget(self.btn_col_save)
        row2_layout.addWidget(self.btn_col_delete)
        
        input_widget_style = """
            QLineEdit, QComboBox { 
                border: 1.5px solid #E3E8EE; 
                border-radius: 8px; 
                padding: 0 15px; 
                font-size: 16px; 
                color: #4F566B; 
                background-color: rgba(247, 249, 252, 0.7); 
            }
            QLineEdit:focus, QComboBox:focus { 
                border: 2px solid #1A56DB; 
                background-color: #FFFFFF; 
            }
            /* Styling panah Dropdown biar seragam */
            QComboBox::drop-down { border: none; width: 35px; }
            QComboBox::down-arrow { image: url('assets/icons/ic_chevron_down.svg'); width: 20px; height: 20px; }
            
            QComboBox QAbstractItemView {
                border: 1px solid #E3E8EE;
                border-radius: 8px;
                background-color: #FFFFFF;
                selection-background-color: #EFF6FF;
                selection-color: #1A56DB;
                outline: none;
            }
            QComboBox QAbstractItemView::item { min-height: 45px; padding: 10px; }
        """
        
        for widget in [self.combo_status, self.input_col_rating, self.input_col_notes]:
            widget.setStyleSheet(input_widget_style)
            
        crud_layout.addWidget(lbl_crud_title)
        crud_layout.addLayout(row1_layout)
        crud_layout.addLayout(row2_layout)
        
        table_container = QFrame()
        table_container.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E3E8EE;")
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(25, 25, 25, 25)
        
        self.table_col = QTableWidget(0, 6) 
        self.table_col.setHorizontalHeaderLabels(["Judul Buku", "Status", "Rating", "Anotasi / Catatan", "Mulai", "Selesai"])
        self.table_col.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_col.setEditTriggers(QTableWidget.NoEditTriggers) 
        self.table_col.setFocusPolicy(Qt.NoFocus)
        self.table_col.setSelectionBehavior(QTableWidget.SelectRows) 
        self.table_col.setShowGrid(False)
        self.table_col.setIconSize(QSize(35, 50))
        self.table_col.verticalHeader().setDefaultSectionSize(75)
        self.table_col.verticalHeader().setVisible(False)
        self.table_col.setStyleSheet(self._table_stylesheet() + """
            QTableWidget::item:selected { background-color: #EFF6FF; color: #1A56DB; }
        """)

        # Double-click baris → buka popup edit
        self.table_col.doubleClicked.connect(self._on_collection_double_click)
        # Context menu klik kanan
        self.table_col.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_col.customContextMenuRequested.connect(self._show_col_context_menu)
        # Seleksi baris → isi form CRUD
        self.table_col.itemSelectionChanged.connect(self._on_collection_selected)
        
        table_layout.addWidget(self.table_col)
        
        layout.addLayout(header_layout)
        layout.addWidget(crud_card)
        layout.addWidget(table_container, 1)
        
        return page

    def _on_rating_text_changed(self, text):
        try:
            val = float(text.replace(',', '.'))
            val = max(0.0, min(5.0, val))
            self.star_widget.set_value(val)
        except ValueError:
            self.star_widget.set_value(0.0)

    def build_analytics_page(self):
        """Analytics page — scrollable, semua chart full-width."""
        page = QWidget()
        page.setStyleSheet("background-color: #F7F9FC;")
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        # ── Scroll Area ──────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                border: none; background: transparent; width: 6px; margin: 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(148,163,184,0.45); min-height: 50px; border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover { background: rgba(71,85,105,0.75); }
            QScrollBar::handle:vertical:pressed { background: rgba(30,64,175,0.8); }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0; width: 0; border: none; background: none;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                width: 0; height: 0; background: none; image: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # ── Header ───────────────────────────────────────────────────
        lbl_title = QLabel("Analytics")
        lbl_title.setStyleSheet("font-size: 38px; font-weight: 800; color: #1A1F36;")
        layout.addWidget(lbl_title)

        # Helper buat card container
        def _card(title, layout_ref_attr, placeholder_attr):
            card = QFrame()
            card.setStyleSheet(
                "background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E3E8EE;"
            )
            cl = QVBoxLayout(card)
            cl.setContentsMargins(25, 20, 25, 20)
            cl.setSpacing(10)
            lbl = QLabel(title)
            lbl.setStyleSheet(
                "font-size: 18px; font-weight: 800; color: #1A1F36; border: none;"
            )
            cl.addWidget(lbl)
            ph = QLabel("Data akan muncul setelah login")
            ph.setAlignment(Qt.AlignCenter)
            ph.setStyleSheet("color: #9CA3AF; font-size: 15px;")
            cl.addWidget(ph)
            cl.addStretch()
            setattr(self, layout_ref_attr, cl)
            setattr(self, placeholder_attr, ph)
            return card

        # ── Baris 1: Pie Status + Pie Genre (50:50) ──────────────────
        row1 = QHBoxLayout()
        row1.setSpacing(20)
        row1.addWidget(_card("Status Bacaan (Kamu)",
                             "_pie_chart_layout", "_pie_placeholder"))
        row1.addWidget(_card("Komposisi Genre Katalog",
                             "_pie_kat_layout", "_pie_kat_placeholder"))
        layout.addLayout(row1)

        # ── Bar Chart Kategori — LEBAR PENUH ─────────────────────────
        layout.addWidget(_card("Komposisi Kategori Buku — Semua Koleksimu",
                               "_bar_chart_layout", "_bar_placeholder"))

        # ── Histogram Rating ─────────────────────────────────────────
        layout.addWidget(_card("Persebaran Rating Pribadi",
                               "_hist_chart_layout", "_hist_placeholder"))

        # ── Bar Status Semua User — LEBAR PENUH ──────────────────────
        layout.addWidget(_card("Status Bacaan — Semua Pengguna",
                               "_global_chart_layout", "_global_placeholder"))

        # ── Trend Line Genre per Tahun — LEBAR PENUH ─────────────────
        layout.addWidget(_card("Tren Genre Berdasarkan Tahun Terbit",
                               "_trend_chart_layout", "_trend_placeholder"))

        layout.addStretch()
        scroll.setWidget(content)
        page_layout.addWidget(scroll)
        return page


    # =========================================================
    # HELPER
    # =========================================================
    def _table_stylesheet(self):
        return """
            QTableWidget { background-color: #FFFFFF; border: none; font-size: 18px; color: #4F566B; }
            QHeaderView { background-color: transparent; }
            QHeaderView::section { 
                background-color: #F8FAFC; padding: 12px 15px; font-size: 16px; 
                font-weight: 800; color: #475569; border: none; 
                border-top: 1px solid #E2E8F0; border-bottom: 2px solid #E2E8F0; 
            }
            QHeaderView::section:first {
                border-top-left-radius: 10px; border-bottom-left-radius: 10px; border-left: 1px solid #E2E8F0;
            }
            QHeaderView::section:last {
                border-top-right-radius: 10px; border-bottom-right-radius: 10px; border-right: 1px solid #E2E8F0;
            }
            QTableWidget::item { padding: 15px; border-bottom: 1px solid #F1F5F9; }
        """

    def _make_action_btn(self, buku: dict):
        """Buat tombol aksi (⋮) — QMenu dibuat LAZY saat diklik, bukan saat render."""
        btn = QPushButton()
        btn.setIcon(QIcon("assets/icons/ic_more_vert.svg"))
        btn.setIconSize(QSize(24, 24))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; }"
            "QPushButton::menu-indicator { image: none; width: 0px; }"
        )

        def _show_menu():
            menu = QMenu(btn)
            menu.setStyleSheet("""
                QMenu { background-color: #FFFFFF; border: 1px solid #E3E8EE; border-radius: 8px; padding: 5px; }
                QMenu::item { padding: 10px 20px; font-size: 16px; font-weight: bold; color: #1A1F36; border-radius: 6px; }
                QMenu::item:selected { background-color: #F7F9FC; color: #1A56DB; }
            """)
            action_detail = QAction(QIcon("assets/icons/ic_detail.svg"), "Detail", btn)
            action_detail.triggered.connect(lambda: self.show_book_detail(buku))
            menu.addAction(action_detail)
            action_bookmark = QAction(QIcon("assets/icons/ic_bookmark.svg"), "Tambah ke Koleksi", btn)
            action_bookmark.triggered.connect(lambda: self._add_to_collection(buku))
            menu.addAction(action_bookmark)
            menu.exec_(btn.mapToGlobal(btn.rect().bottomLeft()))

        btn.clicked.connect(_show_menu)
        return btn

    # =========================================================
    # INTEGRASI DATA — dipanggil oleh ScreenManager
    # =========================================================

    def set_user(self, username: str, user_data: dict = None):
        """Simpan username & data profil user yang sedang login."""
        self.current_user = username
        self._user_data   = dict(user_data) if user_data else {}
        if hasattr(self, "lbl_welcome"):
            nama = self._user_data.get("nama_lengkap") or username
            self.lbl_welcome.setText(f"Selamat datang kembali, {nama}! 👋")
            if hasattr(self, "lbl_top_user_name"):
                self.lbl_top_user_name.setText(nama)
        self._update_user_avatar()

    def refresh_data(self):
        """Muat ulang semua data dari DataManager ke seluruh halaman."""
        if not self.data_manager:
            return
        self._all_books_cache = self.data_manager.get_semua_buku()
        self._filtered_books_cache = self._all_books_cache.copy() # Reset filter
        self.current_page = 1 # Kembali ke halaman 1
        
        self._load_library_data()
        self._load_collections_data()
        self._load_overview_data()
        # Analytics di-rebuild saat tab dibuka agar tidak berat di awal

    def _get_default_icon(self) -> QIcon:
        """Buat default icon placeholder sekali, simpan di cache."""
        if self._default_icon is None:
            px = QPixmap(35, 50)
            px.fill(QColor("#CBD5E1"))
            self._default_icon = QIcon(px)
        return self._default_icon

    def _get_cover_icon(self, cover_path: str) -> QIcon:
        """Ambil icon cover dari cache. Baca disk hanya sekali per path."""
        if not cover_path:
            return self._get_default_icon()
        if cover_path not in self._cover_icon_cache:
            px = QPixmap(cover_path)
            if px.isNull():
                self._cover_icon_cache[cover_path] = self._get_default_icon()
            else:
                self._cover_icon_cache[cover_path] = QIcon(
                    px.scaled(35, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
        return self._cover_icon_cache[cover_path]

    def _load_library_data(self):
        """Isi tabel Library berdasarkan halaman saat ini."""
        total_items = len(self._filtered_books_cache)
        max_page = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        # Potong data sesuai halaman (Slicing Array)
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)
        buku_page_ini = self._filtered_books_cache[start_idx:end_idx]

        # Update teks info halaman
        self.lbl_page_info.setText(f"Halaman {self.current_page} dari {max_page}  (Total: {total_items} Buku)")
        # Sembunyikan tombol di halaman ujung
        self.btn_prev_page.setVisible(self.current_page > 1)
        self.btn_next_page.setVisible(self.current_page < max_page)

        self.table_lib.setUpdatesEnabled(False)
        self.table_lib.setRowCount(len(buku_page_ini))

        for row, buku in enumerate(buku_page_ini):
            judul    = str(buku.get("judul", "-"))
            penulis  = str(buku.get("penulis", "-"))
            tahun    = str(buku.get("first_published", buku.get("tahun_terbit", "-")))
            rating   = str(buku.get("avg_rating_gr", buku.get("rating", "0.0")))
            genres   = buku.get("genre", buku.get("kategori", []))
            kategori = ", ".join(genres[:2]) if isinstance(genres, list) else str(genres)

            icon_buku = self._get_cover_icon(buku.get("local_cover_path", ""))

            col_data = [
                ("   " + judul, False), (penulis, False),
                (tahun, True), (kategori, True), (f"⭐ {rating}", True)
            ]

            for col, (text, centered) in enumerate(col_data):
                cell = QTableWidgetItem(text)
                if col == 0:
                    cell.setIcon(icon_buku)
                if centered:
                    cell.setTextAlignment(Qt.AlignCenter)
                self.table_lib.setItem(row, col, cell)

            self.table_lib.setCellWidget(row, 5, self._make_action_btn(buku))

        self.table_lib.setUpdatesEnabled(True)


    def _on_lib_cell_clicked(self, row, col):
        """Klik kolom judul/cover (col 0) di Library → buka detail buku."""
        if col != 0:
            return
        # Ambil data buku dari filtered list berdasarkan baris yang diklik
        visible_books = self._get_current_page_books()
        if row < len(visible_books):
            self.show_book_detail(visible_books[row])

    def _get_current_page_books(self):
        """Return list buku yang sedang ditampilkan di halaman saat ini."""
        keyword  = self.search_bar_lib.text().strip().lower()
        kategori = self.combo_filter_lib.currentText()
        filtered = []
        for buku in self._all_books_cache:
            judul     = str(buku.get("judul", "")).lower()
            penulis   = str(buku.get("penulis", "")).lower()
            genres    = buku.get("genre", buku.get("kategori", []))
            genre_str = ", ".join(genres).lower() if isinstance(genres, list) else str(genres).lower()
            if ((not keyword) or keyword in judul or keyword in penulis) and                (kategori == "Semua Kategori" or kategori.lower() in genre_str):
                filtered.append(buku)
        page_size = getattr(self, 'items_per_page', 20)
        cur_page  = getattr(self, 'current_page', 1)
        start = (cur_page - 1) * page_size
        return filtered[start:start + page_size]

    def _filter_library(self):
        """Trigger debounce — dipanggil langsung saat combo berubah."""
        self._search_timer.stop()
        self._do_filter_library()

    def _do_filter_library(self):
        """Filter tabel Library — dipanggil setelah debounce 300ms."""
        keyword  = self.search_bar_lib.text().strip().lower()
        kategori = self.combo_filter_lib.currentText()

        filtered = []
        for buku in self._all_books_cache:
            judul   = str(buku.get("judul", "")).lower()
            penulis = str(buku.get("penulis", "")).lower()
            genres  = buku.get("genre", buku.get("kategori", []))
            genre_str = ", ".join(genres).lower() if isinstance(genres, list) else str(genres).lower()

            cocok_keyword  = (not keyword) or (keyword in judul) or (keyword in penulis)
            cocok_kategori = (kategori == "Semua Kategori") or (kategori.lower() in genre_str)

            if cocok_keyword and cocok_kategori:
                filtered.append(buku)

        self._filtered_books_cache = filtered
        self.current_page = 1 # Habis filter, selalu balik ke halaman 1
        self._load_library_data()

    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._load_library_data()

    def _next_page(self):
        max_page = (len(self._filtered_books_cache) + self.items_per_page - 1) // self.items_per_page
        if self.current_page < max_page:
            self.current_page += 1
            self._load_library_data()

    def _load_collections_data(self):
        """Isi tabel My Collections dengan data tracker user yang login."""
        if not self.current_user:
            return

        tracker_list = self.data_manager.get_tracker_user(self.current_user)
        buku_dict    = {b.get("id_buku"): b for b in self._all_books_cache}

        self.table_col.setUpdatesEnabled(False)
        self.table_col.setRowCount(len(tracker_list))

        for row, tracker in enumerate(tracker_list):
            buku    = buku_dict.get(tracker.get("book_id"), {})
            judul   = buku.get("judul", tracker.get("book_id", "-"))
            status  = tracker.get("status_baca", "-")
            _r = tracker.get("rating_personal", 0) or 0
            rating  = f"{_r:g}" if _r else "—"
            catatan = tracker.get("catatan", tracker.get("anotasi", ""))
            tgl     = tracker.get("tgl_mulai", tracker.get("tanggal_mulai", "-"))

            # Pakai cover cache — tidak baca disk ulang
            icon_buku = self._get_cover_icon(buku.get("local_cover_path", ""))

            tgl_selesai_val = tracker.get("tgl_selesai", "")
            tgl_selesai_display = tgl_selesai_val if tgl_selesai_val not in ("", None) else "-"

            for col, (text, centered) in enumerate([
                ("   " + judul, False), (status, True),
                (rating, True), (catatan, False), (tgl, True), (tgl_selesai_display, True)
            ]):
                cell = QTableWidgetItem(text)
                if col == 0:
                    # FIX: Gunakan icon_buku yang udah dicek, bukan col_cover_icon
                    cell.setIcon(icon_buku)
                    cell.setData(Qt.UserRole, tracker) 
                if centered:
                    cell.setTextAlignment(Qt.AlignCenter)
                self.table_col.setItem(row, col, cell)

        self.table_col.setUpdatesEnabled(True)


    def _on_collection_double_click(self, index):
        """Double-click baris koleksi → buka popup dialog edit."""
        row = index.row()
        item = self.table_col.item(row, 0)
        if not item:
            return
        tracker_data = item.data(Qt.UserRole)
        if not tracker_data:
            return

        buku_dict = {b.get("id_buku"): b for b in self._all_books_cache}
        buku = buku_dict.get(tracker_data.get("book_id"), {})
        judul = buku.get("judul", tracker_data.get("book_id", "-"))

        # --- Buat dialog popup ---
        dialog = QDialog(self, Qt.Dialog)
        dialog.setWindowTitle("Edit Koleksi")
        dialog.setFixedWidth(480)
        dialog.setStyleSheet("background-color: #FFFFFF; font-family: 'Segoe UI';")

        outer = QVBoxLayout(dialog)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(16)

        # Judul buku
        lbl_judul = QLabel(f"Judul: {judul}")
        lbl_judul.setStyleSheet("font-size: 20px; font-weight: 800; color: #1A1F36;")
        lbl_judul.setWordWrap(True)
        outer.addWidget(lbl_judul)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #E2E8F0;")
        outer.addWidget(sep)

        field_style = """
            QComboBox, QLineEdit {
                border: 1.5px solid #E3E8EE; border-radius: 8px;
                padding: 0 12px; font-size: 15px; color: #374151;
                background-color: #F8FAFC; min-height: 38px;
            }
            QComboBox:focus, QLineEdit:focus { border: 2px solid #1A56DB; background: #FFF; }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox::down-arrow { image: url('assets/icons/ic_chevron_down.svg'); width: 16px; height: 16px; }
            QComboBox QAbstractItemView {
                background: #FFF; border: 1px solid #E3E8EE;
                selection-background-color: #EFF6FF; selection-color: #1A56DB;
            }
            QComboBox QAbstractItemView::item { min-height: 36px; padding: 6px; }
        """

        def _row(label_text, widget):
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFixedWidth(130)
            lbl.setStyleSheet("font-size: 14px; font-weight: 600; color: #6B7280;")
            row.addWidget(lbl)
            row.addWidget(widget)
            outer.addLayout(row)

        # Status
        combo_status = QComboBox()
        combo_status.addItems(["Sedang Membaca", "Selesai Dibaca", "Belum Dibaca", "Drop"])
        cur_status = tracker_data.get("status_baca", "Belum Dibaca")
        idx = combo_status.findText(cur_status)
        if idx >= 0: combo_status.setCurrentIndex(idx)
        combo_status.setStyleSheet(field_style)
        _row("Status", combo_status)

        # Rating
        input_rating = QLineEdit()
        input_rating.setPlaceholderText("1 – 5")
        cur_rating = tracker_data.get("rating_personal", 0)
        if cur_rating: input_rating.setText(str(cur_rating))
        input_rating.setStyleSheet(field_style)
        _row("Rating ⭐", input_rating)

        # Anotasi
        input_anotasi = QLineEdit()
        input_anotasi.setPlaceholderText("Tulis kesan atau ulasan...")
        input_anotasi.setText(tracker_data.get("catatan", tracker_data.get("anotasi", "")))
        input_anotasi.setStyleSheet(field_style)
        _row("Anotasi", input_anotasi)

        # Tanggal Mulai
        input_tgl_mulai = QLineEdit()
        input_tgl_mulai.setPlaceholderText("yyyy-MM-dd")
        input_tgl_mulai.setReadOnly(True)
        tgl_mulai = tracker_data.get("tgl_mulai", tracker_data.get("tanggal_mulai", ""))
        if tgl_mulai and tgl_mulai != "-": input_tgl_mulai.setText(tgl_mulai)
        input_tgl_mulai.setStyleSheet(field_style)

        btn_cal_mulai = QPushButton("📅")
        btn_cal_mulai.setFixedSize(34, 34)
        btn_cal_mulai.setCursor(Qt.PointingHandCursor)
        btn_cal_mulai.setStyleSheet("QPushButton{background:transparent;border:none;font-size:16px;border-radius:6px;}QPushButton:hover{background:#EFF6FF;}")

        tgl_mulai_row = QHBoxLayout()
        lbl_tm = QLabel("Tgl Mulai")
        lbl_tm.setFixedWidth(130)
        lbl_tm.setStyleSheet("font-size: 14px; font-weight: 600; color: #6B7280;")
        tgl_mulai_row.addWidget(lbl_tm)
        tgl_mulai_row.addWidget(input_tgl_mulai)
        tgl_mulai_row.addWidget(btn_cal_mulai)
        outer.addLayout(tgl_mulai_row)

        # Tanggal Selesai
        input_tgl_selesai = QLineEdit()
        input_tgl_selesai.setPlaceholderText("yyyy-MM-dd")
        input_tgl_selesai.setReadOnly(True)
        tgl_selesai = tracker_data.get("tgl_selesai", "")
        if tgl_selesai and tgl_selesai != "-": input_tgl_selesai.setText(tgl_selesai)
        input_tgl_selesai.setStyleSheet(field_style)

        btn_cal_selesai = QPushButton("📅")
        btn_cal_selesai.setFixedSize(34, 34)
        btn_cal_selesai.setCursor(Qt.PointingHandCursor)
        btn_cal_selesai.setStyleSheet(btn_cal_mulai.styleSheet())

        tgl_selesai_row = QHBoxLayout()
        lbl_ts = QLabel("Tgl Selesai")
        lbl_ts.setFixedWidth(130)
        lbl_ts.setStyleSheet("font-size: 14px; font-weight: 600; color: #6B7280;")
        tgl_selesai_row.addWidget(lbl_ts)
        tgl_selesai_row.addWidget(input_tgl_selesai)
        tgl_selesai_row.addWidget(btn_cal_selesai)
        outer.addLayout(tgl_selesai_row)

        # Sambungkan tombol kalender popup
        def open_cal(field, btn):
            from screen_manager import ScreenManager  # hindari circular
            cur = QDate.fromString(field.text(), "yyyy-MM-dd")
            if not cur.isValid(): cur = QDate.currentDate()
            result = ModernCalendarPopup.get_date(cur, btn, dialog)
            if result: field.setText(result.toString("yyyy-MM-dd"))

        btn_cal_mulai.clicked.connect(lambda: open_cal(input_tgl_mulai, btn_cal_mulai))
        btn_cal_selesai.clicked.connect(lambda: open_cal(input_tgl_selesai, btn_cal_selesai))

        # Tombol aksi
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        btn_hapus = QPushButton("Hapus dari Koleksi")
        btn_hapus.setFixedHeight(42)
        btn_hapus.setCursor(Qt.PointingHandCursor)
        btn_hapus.setStyleSheet("QPushButton{background:#FEF2F2;color:#DC2626;border:1.5px solid #FECACA;border-radius:8px;font-weight:700;font-size:14px;padding: 0 20px;}QPushButton:hover{background:#FEE2E2;}")

        btn_simpan = QPushButton("Simpan")
        btn_simpan.setFixedHeight(42)
        btn_simpan.setCursor(Qt.PointingHandCursor)
        btn_simpan.setStyleSheet("QPushButton{background:#1A56DB;color:white;border:none;border-radius:8px;font-weight:700;font-size:14px;padding: 0 24px;}QPushButton:hover{background:#1E40AF;}")

        btn_row.addWidget(btn_hapus)
        btn_row.addStretch()
        btn_row.addWidget(btn_simpan)
        outer.addLayout(btn_row)

        def do_save():
            rating_text = input_rating.text().strip().replace(',', '.')
            try:
                rating = float(rating_text) if rating_text else 0.0
                if rating and not (1.0 <= rating <= 5.0):
                    QMessageBox.warning(dialog, "Rating Tidak Valid", "Rating harus antara 1.0–5.0.")
                    return
            except ValueError:
                QMessageBox.warning(dialog, "Rating Tidak Valid", "Masukkan angka untuk rating.")
                return
            self.data_manager.update_tracker(tracker_data["id_tracker"], {
                "status_baca"    : combo_status.currentText(),
                "rating_personal": rating,
                "catatan"        : input_anotasi.text().strip(),
                "tgl_mulai"      : input_tgl_mulai.text().strip() or "-",
                "tgl_selesai"    : input_tgl_selesai.text().strip() or "-",
            })
            dialog.accept()
            self._load_collections_data()
            self._load_overview_data()

        def do_hapus():
            k = QMessageBox.question(dialog, "Konfirmasi", "Hapus buku ini dari koleksi?",
                                     QMessageBox.Yes | QMessageBox.No)
            if k == QMessageBox.Yes:
                self.data_manager.hapus_tracker(tracker_data["id_tracker"])
                dialog.accept()
                self._load_collections_data()
                self._load_overview_data()

        btn_simpan.clicked.connect(do_save)
        btn_hapus.clicked.connect(do_hapus)
        dialog.exec_()

    def _on_collection_selected(self):
        """Isi form CRUD saat user memilih baris di tabel Collections."""
        selected = self.table_col.selectedItems()
        if not selected:
            return

        row = self.table_col.currentRow()
        item = self.table_col.item(row, 0)
        if not item:
            return
        tracker_data = item.data(Qt.UserRole)
        if not tracker_data:
            return

        self.input_col_title.setText(self.table_col.item(row, 0).text().strip())

        status = tracker_data.get("status_baca", "Belum Dibaca")
        idx = self.combo_status.findText(status)
        if idx >= 0:
            self.combo_status.setCurrentIndex(idx)

        tgl_str = tracker_data.get("tgl_mulai", tracker_data.get("tanggal_mulai", ""))
        self.input_col_date.setText(tgl_str if tgl_str not in ("-", "", None) else "")
        tgl_end_str = tracker_data.get("tgl_selesai", "")
        if hasattr(self, "input_col_date_end"):
            self.input_col_date_end.setText(tgl_end_str if tgl_end_str not in ("-", "", None) else "")

        # Tampilkan float dengan bersih: 3.0 → "3", 3.5 → "3.5"
        r = tracker_data.get("rating_personal", 0)
        self.input_col_rating.setText(
            f"{r:g}" if r else ""
        )
        self.star_widget.set_value(float(r))
        # Aktif/disable field rating berdasarkan status
        self._on_status_changed(self.combo_status.currentText())
        catatan = tracker_data.get("catatan", tracker_data.get("anotasi", ""))
        self.input_col_notes.setText(catatan)

        self._selected_tracker = tracker_data

    def _open_calendar_end(self):
        """Buka kalender untuk tanggal selesai baca."""
        current_str = self.input_col_date_end.text().strip()
        current_qdate = QDate.fromString(current_str, "yyyy-MM-dd")
        if not current_qdate.isValid():
            current_qdate = QDate.currentDate()
        result = ModernCalendarPopup.get_date(current_qdate, self._btn_cal_end, self)
        if result:
            self.input_col_date_end.setText(result.toString("yyyy-MM-dd"))

    def _open_calendar(self):
        """Buka ModernCalendarPopup dan update input_col_date."""
        current_str = self.input_col_date.text().strip()
        current_qdate = QDate.fromString(current_str, "yyyy-MM-dd")
        if not current_qdate.isValid():
            current_qdate = QDate.currentDate()
        result = ModernCalendarPopup.get_date(current_qdate, self._date_container, self)
        if result:
            self.input_col_date.setText(result.toString("yyyy-MM-dd"))

    def _on_status_changed(self, status: str):
        """Atur enable/disable field rating & tanggal selesai sesuai status."""
        is_selesai = (status == "Selesai Dibaca")
        is_drop    = (status == "Drop")

        # Rating: hanya boleh saat Selesai atau Drop
        self.input_col_rating.setEnabled(is_selesai or is_drop)
        if is_selesai or is_drop:
            self.input_col_rating.setPlaceholderText("1.0 – 5.0")
        else:
            self.input_col_rating.clear()
            self.input_col_rating.setPlaceholderText("Selesaikan buku dulu")

        # Tanggal selesai: aktif saat Selesai atau Drop
        if hasattr(self, "_date_end_container"):
            self._date_end_container.setEnabled(is_selesai or is_drop)
            opacity = "1.0" if (is_selesai or is_drop) else "0.4"
            self._date_end_container.setStyleSheet(f"""
                QFrame {{
                    border: 1.5px solid #E3E8EE; border-radius: 8px;
                    background-color: rgba(247, 249, 252, 0.7);
                    opacity: {opacity};
                }}
            """)
            if not (is_selesai or is_drop):
                self.input_col_date_end.clear()

    def _save_collection_edit(self):
        """Simpan perubahan status/rating/catatan ke tracker.json."""
        if not hasattr(self, "_selected_tracker") or not self._selected_tracker:
            QMessageBox.information(self, "Info", "Pilih baris koleksi terlebih dahulu.")
            return

        tracker_id = self._selected_tracker.get("id_tracker")
        status     = self.combo_status.currentText()
        catatan    = self.input_col_notes.text().strip()

        tgl_mulai  = self.input_col_date.text().strip() or "-"

        # Parse rating — support titik DAN koma sebagai desimal
        rating_text = self.input_col_rating.text().strip().replace(',', '.')
        rating = 0.0
        if rating_text:
            if status not in ["Selesai Dibaca", "Drop"]:
                QMessageBox.warning(self, "Rating Tidak Bisa Diisi",
                    "Rating hanya bisa diberikan jika status Selesai Dibaca atau Drop.")
                return
            try:
                rating = float(rating_text)
            except ValueError:
                QMessageBox.warning(self, "Rating Tidak Valid",
                    "Masukkan angka. Contoh: 4 atau 4.5 atau 4,5")
                return
            if not (1.0 <= rating <= 5.0):
                QMessageBox.warning(self, "Rating Tidak Valid",
                    "Rating harus antara 1.0 sampai 5.0.")
                return
            rating = round(rating, 2)

        tgl_selesai = ""
        if hasattr(self, "input_col_date_end"):
            tgl_selesai = self.input_col_date_end.text().strip() or ""

        self.data_manager.update_tracker(tracker_id, {
            "status_baca"    : status,
            "rating_personal": rating,
            "catatan"        : catatan,
            "tgl_mulai"      : tgl_mulai,
            "tgl_selesai"    : tgl_selesai,
        })

        # Akumulasi rating ke buku.json via rating_system
        if rating and status == "Selesai Dibaca" and self.rating_system:
            book_id = self._selected_tracker.get("book_id", "")
            self.rating_system.simpan_rating_personal(
                self.current_user, book_id, rating
            )
            # Refresh cache buku agar detail dialog tampilkan rating terbaru
            self._all_books_cache = self.data_manager.get_semua_buku()

        QMessageBox.information(self, "Berhasil", "Koleksi berhasil diperbarui.")
        
        # Simpan tracker_id yang baru saja diedit
        edited_tracker_id = self._selected_tracker.get("id_tracker")
        self._selected_tracker = None
        
        self._load_collections_data()
        self._load_overview_data()
        
        # Kembalikan seleksi (garis biru) ke baris yang baru saja diedit
        for row in range(self.table_col.rowCount()):
            item = self.table_col.item(row, 0)
            if item:
                tracker_data = item.data(Qt.UserRole)
                if tracker_data and tracker_data.get("id_tracker") == edited_tracker_id:
                    self.table_col.selectRow(row)
                    self._on_collection_selected()  # Paksa update state dan form
                    break

    def _delete_collection_entry(self):
        """Hapus entri koleksi dari tracker.json."""
        if not hasattr(self, "_selected_tracker") or not self._selected_tracker:
            QMessageBox.information(self, "Info", "Pilih baris koleksi terlebih dahulu.")
            return

        konfirmasi = QMessageBox.question(
            self, "Konfirmasi Hapus",
            "Hapus buku ini dari koleksi?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if konfirmasi == QMessageBox.Yes:
            self.data_manager.hapus_tracker(self._selected_tracker["id_tracker"])
            self._selected_tracker = None
            self._load_collections_data()
            self._load_overview_data()

    def _add_to_collection(self, buku: dict):
        """Tambahkan buku ke koleksi user (dari tombol Bookmark di Library)."""
        if not self.current_user:
            QMessageBox.warning(self, "Belum Login", "Silakan login terlebih dahulu.")
            return

        book_id = buku.get("id_buku")
        if self.data_manager.cek_duplikasi_tracker(self.current_user, book_id):
            QMessageBox.information(self, "Sudah Ada", "Buku ini sudah ada di koleksimu.")
            return

        import uuid
        data_baru = {
            "id_tracker"      : str(uuid.uuid4())[:8].upper(),
            "user_id"         : self.current_user,
            "book_id"         : book_id,
            "status_baca"     : "Belum Dibaca",
            "rating_personal" : 0,
            "catatan"         : "",
            "tgl_mulai"       : "-",
        }
        self.data_manager.simpan_tracker(data_baru)
        QMessageBox.information(self, "Berhasil", f"'{buku.get('judul')}' ditambahkan ke koleksimu.")
        self._load_collections_data()
        self._load_overview_data()

    def _show_col_context_menu(self, position):
        """Context menu klik kanan di tabel My Collections."""
        index = self.table_col.indexAt(position)
        if not index.isValid():
            return

        row = index.row()
        item = self.table_col.item(row, 0)
        tracker_data = item.data(Qt.UserRole) if item else None

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #FFFFFF; border: 1px solid #E3E8EE; border-radius: 8px; padding: 5px; }
            QMenu::item { padding: 10px 20px 10px 8px; font-size: 16px; font-weight: bold; color: #1A1F36; border-radius: 6px; }
            QMenu::item:selected { background-color: #EFF6FF; color: #1A56DB; }
            QMenu::icon { padding-left: 6px; }
        """)

        if tracker_data:
            buku_dict = {b.get("id_buku"): b for b in self._all_books_cache}
            buku = buku_dict.get(tracker_data.get("book_id"), {})

            action_detail = QAction(QIcon("assets/icons/ic_detail.svg"), "Detail Buku", self)
            action_detail.triggered.connect(lambda: self.show_book_detail(buku))
            menu.addAction(action_detail)

        menu.exec_(self.table_col.viewport().mapToGlobal(position))

    def _load_overview_data(self):
        """Update stat cards dan tabel ringkasan di halaman Overview."""
        if not self.current_user:
            return

        tracker_list = self.data_manager.get_tracker_user(self.current_user)
        total    = len(tracker_list)
        membaca  = sum(1 for t in tracker_list if t.get("status_baca") == "Sedang Membaca")
        selesai  = sum(1 for t in tracker_list if t.get("status_baca") == "Selesai Dibaca")
        drop     = sum(1 for t in tracker_list if t.get("status_baca") == "Drop")

        for card, val in [
            (self.card_total,    f"{total} Buku"),
            (self.card_reading,  f"{membaca} Buku"),
            (self.card_finished, f"{selesai} Buku"),
            (self.card_drop,     f"{drop} Buku"),
        ]:
            lbl_val = card.layout().itemAt(1).widget()
            if lbl_val:
                lbl_val.setText(val)

        buku_dict = {b.get("id_buku"): b for b in self._all_books_cache}
        recent = tracker_list[-5:]
        self.table_dash.setRowCount(len(recent))

        for row, tracker in enumerate(recent):
            buku   = buku_dict.get(tracker.get("book_id"), {})
            judul  = buku.get("judul", "-")
            penuls = buku.get("penulis", "-")
            tahun  = str(buku.get("first_published", buku.get("tahun_terbit", "-")))
            rating = str(buku.get("avg_rating_gr", buku.get("rating", "-")))
            status = tracker.get("status_baca", "-")

            for col, (text, centered) in enumerate([
                (judul, False), (penuls, False),
                (tahun, True), (f"⭐ {rating}", True), (status, True)
            ]):
                if isinstance(text, list):
                    safe_text = ", ".join([str(i) for i in text])
                else:
                    safe_text = str(text)

                cell = QTableWidgetItem(safe_text)
                if centered:
                    cell.setTextAlignment(Qt.AlignCenter)
                self.table_dash.setItem(row, col, cell)

    def _render_all_charts(self):
        if hasattr(self, "_pie_chart_layout"):
            self._rebuild_analytics_charts()

    def _rebuild_analytics_charts(self):
        """Rebuild chart analytics dengan data nyata dari tracker user."""
        if not self.current_user or not self.data_manager:
            return

        tracker_list = self.data_manager.get_tracker_user(self.current_user)
        buku_dict    = {b.get("id_buku"): b for b in self._all_books_cache}

        # Hitung status
        status_count = {"Selesai": 0, "Sedang": 0, "Belum": 0, "Drop": 0}
        for t in tracker_list:
            s = t.get("status_baca", "")
            if "Selesai" in s:
                status_count["Selesai"] += 1
            elif "Sedang" in s:
                status_count["Sedang"] += 1
            elif "Drop" in s:
                status_count["Drop"] += 1
            else:
                status_count["Belum"] += 1

        # Hitung kategori
        kategori_count: dict = {}
        for t in tracker_list:
            buku = buku_dict.get(t.get("book_id"), {})
            kat_raw = buku.get("kategori", buku.get("genre", "Lainnya"))
            if isinstance(kat_raw, list):
                kat = str(kat_raw[0]) if kat_raw else "Lainnya"
            else:
                kat = str(kat_raw)
            kategori_count[kat] = kategori_count.get(kat, 0) + 1

        # Hitung distribusi rating
        ratings_raw = [t.get("rating_personal", 0) for t in tracker_list if t.get("rating_personal", 0) > 0]
        rating_count = {f"★ {i}": ratings_raw.count(i) for i in range(1, 6)}

        visualizer = DataVisualizer()

        # FIX: Hapus widget lama dan pasang yang baru dengan data nyata
        def _replace_chart(layout, placeholder_attr, new_widget):
            # Hapus semua item kecuali label judul (index 0)
            while layout.count() > 1:
                item = layout.takeAt(layout.count() - 1)
                if item.widget():
                    item.widget().deleteLater()
                elif item.spacerItem():
                    pass  # spacer cukup di-takeAt
            setattr(self, placeholder_attr, None)
            layout.addWidget(new_widget)
            # Tinggi canvas menyesuaikan konten
            new_widget.setMinimumHeight(int(new_widget.figure.get_figheight() * new_widget.figure.get_dpi()))

        use_anim = self._user_data.get("animate_charts", True)

        data_status_display = status_count if any(v > 0 for v in status_count.values()) else None
        pie_widget = visualizer.create_pie_chart_status(data_status_display, use_animations=use_anim)
        _replace_chart(self._pie_chart_layout, "_pie_placeholder", pie_widget)

        data_kat_display = kategori_count if kategori_count else None
        bar_widget = visualizer.create_bar_chart_kategori(data_kat_display, use_animations=use_anim)
        _replace_chart(self._bar_chart_layout, "_bar_placeholder", bar_widget)

        data_rating_display = rating_count if any(v > 0 for v in rating_count.values()) else None
        hist_widget = visualizer.create_histogram_rating(data_rating_display, use_animations=use_anim)
        _replace_chart(self._hist_chart_layout, "_hist_placeholder", hist_widget)

        # === DATA GLOBAL (semua user dari tracker.json) ===
        all_tracker = self.data_manager._read_json(self.data_manager.path_tracker)

        # Bar chart status semua user
        status_global = {}
        for t in all_tracker:
            s = t.get('status_baca', 'Belum Dibaca')
            status_global[s] = status_global.get(s, 0) + 1
        global_widget = visualizer.create_bar_status_global(status_global or None, use_animations=use_anim)
        _replace_chart(self._global_chart_layout, "_global_placeholder", global_widget)

        # Pie chart komposisi genre dari SELURUH buku di katalog
        kat_global = {}
        for b in self._all_books_cache:
            genres = b.get('genre', [])
            if isinstance(genres, list):
                for g in genres[:1]:  # ambil genre utama
                    kat_global[g] = kat_global.get(g, 0) + 1
            elif genres:
                kat_global[str(genres)] = kat_global.get(str(genres), 0) + 1
        pie_kat_widget = visualizer.create_pie_chart_kategori_global(kat_global or None, use_animations=use_anim)
        _replace_chart(self._pie_kat_layout, "_pie_kat_placeholder", pie_kat_widget)

        # Trend line genre per dekade dari buku.json
        top_genres = sorted(kat_global, key=kat_global.get, reverse=True)[:5]
        trend_data = {g: {} for g in top_genres}
        for b in self._all_books_cache:
            tahun = b.get('first_published', 0)
            try: tahun = int(tahun)
            except: continue
            if tahun < 1950 or tahun > 2024: continue
            dekade = (tahun // 10) * 10
            genres = b.get('genre', [])
            g0 = genres[0] if isinstance(genres, list) and genres else str(genres)
            if g0 in trend_data:
                trend_data[g0][dekade] = trend_data[g0].get(dekade, 0) + 1
        trend_data = {g: d for g, d in trend_data.items() if d}
        trend_widget = visualizer.create_trendline_genre_tahun(trend_data or None, use_animations=use_anim)
        _replace_chart(self._trend_chart_layout, "_trend_placeholder", trend_widget)

    # Alias lama agar kompatibel dengan kode yang sudah ada
    def _refresh_analytics(self):
        pass  # chart dirender saat tab analytics dibuka, bukan di awal

    def _update_user_avatar(self):
        """Update tombol profil: tampilkan foto jika ada, fallback ke icon."""
        foto = self._user_data.get("foto_profile", "")
        if foto and os.path.exists(foto):
            px = _make_round_pixmap(foto, 50)
            if not px.isNull():
                self.btn_user.setIcon(QIcon(px))
                self.btn_user.setIconSize(QSize(50, 50))
                return
        self.btn_user.setIcon(QIcon("assets/icons/ic_user.svg"))
        self.btn_user.setIconSize(QSize(30, 30))

    def _show_user_popup(self):
        """Tampilkan popup mini profil di bawah tombol avatar."""
        popup = QDialog(self, Qt.Popup | Qt.FramelessWindowHint)
        popup.setAttribute(Qt.WA_TranslucentBackground)
        popup.setFixedWidth(280)

        outer = QVBoxLayout(popup)
        outer.setContentsMargins(8, 8, 8, 8)

        card = QFrame()
        card.setObjectName("popCard")
        card.setStyleSheet("""
            QFrame#popCard {
                background-color: #FFFFFF;
                border-radius: 14px;
                border: 1px solid #E2E8F0;
            }
        """)
        from PyQt5.QtWidgets import QGraphicsDropShadowEffect
        sh = QGraphicsDropShadowEffect()
        sh.setBlurRadius(20)
        sh.setColor(QColor(0, 0, 0, 30))
        sh.setOffset(0, 6)
        card.setGraphicsEffect(sh)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 18, 18, 14)
        lay.setSpacing(0)

        # Avatar kecil + nama + username
        top = QHBoxLayout()
        top.setSpacing(12)
        from ui.ui_profile import _AvatarLabel
        av = _AvatarLabel(size=44)
        foto = self._user_data.get("foto_profile", "")
        if foto and os.path.exists(foto):
            av.set_image(foto)
        av.setStyleSheet("border-radius:22px;")

        info = QVBoxLayout()
        info.setSpacing(1)
        nama  = self._user_data.get("nama_lengkap") or self.current_user or "—"
        lbl_n = QLabel(nama)
        lbl_n.setStyleSheet("font-size:14px; font-weight:800; color:#1A1F36; background:transparent;")
        lbl_u = QLabel(f"@{self.current_user or ''}")
        lbl_u.setStyleSheet("font-size:12px; color:#94A3B8; background:transparent;")
        info.addWidget(lbl_n)
        info.addWidget(lbl_u)
        top.addWidget(av)
        top.addLayout(info)
        lay.addLayout(top)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("color:#F1F5F9; margin-top:12px; margin-bottom:4px;")
        lay.addWidget(div)

        # Menu item style
        menu_item_style = """
            QPushButton { text-align:left; padding:10px 6px; font-size:14px; font-weight:600;
                color:#374151; background:transparent; border:none; border-radius:8px; }
            QPushButton:hover { background-color:#F7F9FC; color:#1A56DB; }
        """

        btn_profile = QPushButton("  Detail Profil")
        btn_profile.setIcon(QIcon("assets/icons/ic_detailAccount.svg"))
        btn_profile.setStyleSheet(menu_item_style)
        btn_profile.setCursor(Qt.PointingHandCursor)
        btn_profile.clicked.connect(lambda: (popup.accept(), self._open_profile_dialog()))

        btn_help = QPushButton("  Bantuan & Panduan")
        btn_help.setIcon(QIcon("assets/icons/ic_help.svg"))
        btn_help.setStyleSheet(menu_item_style)
        btn_help.setCursor(Qt.PointingHandCursor)
        btn_help.clicked.connect(lambda: (popup.accept(), HelpDialog(self).exec_()))
        
        btn_settings = QPushButton("  Settings")
        btn_settings.setIcon(QIcon("assets/icons/ic_settings.svg"))
        btn_settings.setStyleSheet(menu_item_style)
        btn_settings.setCursor(Qt.PointingHandCursor)
        btn_settings.clicked.connect(lambda: (popup.accept(), self._open_settings_dialog()))

        lay.addWidget(btn_profile)
        lay.addWidget(btn_help)
        lay.addWidget(btn_settings)
        outer.addWidget(card)

        # Posisi popup di bawah btn_user
        gp = self.btn_user.mapToGlobal(QPoint(0, self.btn_user.height() + 6))
        gp.setX(gp.x() - 280 + self.btn_user.width())
        popup.move(gp)
        popup.exec_()

    def _on_settings_updated(self, updated_data):
        self._user_data.update(updated_data)
        self._render_all_charts()

    def _open_settings_dialog(self):
        if not self.current_user: return
        dlg = SettingsDialog(
            username=self.current_user,
            user_data=self._user_data,
            data_manager=self.data_manager,
            parent=self
        )
        dlg.settings_updated.connect(self._on_settings_updated)
        dlg.exec_()

    def _open_profile_dialog(self):
        """Buka dialog profil lengkap."""
        if not self.current_user:
            return
        tracker_list = self.data_manager.get_tracker_user(self.current_user)
        buku_dict    = {b.get("id_buku"): b for b in self._all_books_cache}
        dlg = ProfileDialog(
            username=self.current_user,
            user_data=self._user_data,
            tracker_list=tracker_list,
            buku_dict=buku_dict,
            data_manager=self.data_manager,
            parent=self
        )
        dlg.profile_updated.connect(self._on_profile_updated)
        dlg.exec_()

    def _on_profile_updated(self, new_data: dict):
        """Sinkronisasi dashboard setelah profil disimpan."""
        self._user_data = new_data
        nama = new_data.get("nama_lengkap") or self.current_user
        if hasattr(self, "lbl_welcome"):
            self.lbl_welcome.setText(f"Selamat datang kembali, {nama}! 👋")
        if hasattr(self, "lbl_top_user_name"):
            self.lbl_top_user_name.setText(nama)
        self._update_user_avatar()

    def show_book_detail(self, book_data=None):
        """Tampilkan dialog detail buku. book_data bisa None (dummy) atau dict buku nyata."""
        if book_data:
            # FIX: Mapping key JSON buku.json ke key yang dipakai BookDetailDialog
            mapped = {
                "judul"    : book_data.get("judul", "-"),
                "penulis"  : book_data.get("penulis", "-"),
                "tahun"    : str(book_data.get("first_published", book_data.get("tahun_terbit", "-"))),
                "kategori" : (", ".join(book_data["genre"][:2])
                              if isinstance(book_data.get("genre"), list)
                              else str(book_data.get("genre", book_data.get("kategori", "-")))),
                "rating"   : str(book_data.get("avg_rating_gr", book_data.get("rating", "-"))),
                "halaman"  : str(book_data.get("pages", book_data.get("num_pages", book_data.get("halaman", "-")))) + " Halaman",
                "isbn"     : str(book_data.get("isbn", book_data.get("isbn13", "-"))),
                "cover"    : book_data.get("local_cover_path", book_data.get("cover", "")),
                "sinopsis"              : book_data.get("sinopsis", book_data.get("description", "Sinopsis tidak tersedia.")),
                # Rating akumulasi BukuKita
                "rating_bukukita"       : book_data.get("rating_bukukita", 0),
                "total_voter_bukukita"  : book_data.get("total_voter_bukukita", 0),
                # Simpan id_buku untuk fitur bookmark dari dialog
                "id_buku"               : book_data.get("id_buku", ""),
            }
            dialog = BookDetailDialog(mapped)
        else:
            dialog = BookDetailDialog()

        # Hubungkan tombol Bookmark
        if book_data:
            dialog.btn_bookmark.clicked.connect(
                lambda: (self._add_to_collection(book_data), dialog.accept())
            )

        # Tampilkan aktivitas user jika buku ada di koleksi
        if book_data and self.current_user:
            book_id = book_data.get("id_buku", "")
            semua_tracker = self.data_manager.get_semua_tracker()
            tracker_user  = next(
                (t for t in semua_tracker
                 if t.get("user_id") == self.current_user
                 and t.get("book_id") == book_id),
                None
            )
            if tracker_user:
                dialog.set_aktivitas(tracker_user)

        dialog.exec_()