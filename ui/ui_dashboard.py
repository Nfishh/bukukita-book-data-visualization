from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFrame, QTableWidget,
                             QTableWidgetItem, QHeaderView, QSpacerItem, QSizePolicy,
                             QStackedWidget, QButtonGroup, QComboBox, QMenu, QAction,
                             QMessageBox, QScrollArea, QDialog, QGridLayout)
from PyQt5.QtCore import Qt, QSize, QDate, QPoint, QTimer
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor
from PyQt5.QtSvg import QSvgWidget

# FIX: Import path disesuaikan dengan struktur folder ui/
from ui.ui_detail import BookDetailDialog
from ui.data_viz import DataVisualizer

# ==========================================
# Custom Modern Calendar Popup
# ==========================================
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
        
        btn_user = QPushButton()
        btn_user.setIcon(QIcon("assets/icons/ic_user.svg"))
        btn_user.setIconSize(QSize(30, 30))
        btn_user.setFixedSize(50, 50)
        btn_user.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E3E8EE; border-radius: 25px;")
        btn_user.setCursor(Qt.PointingHandCursor)
        
        header_layout.addLayout(title_vbox)
        header_layout.addStretch()
        header_layout.addWidget(btn_user)
        
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.card_total    = StatCard("Total Koleksi",   "0 Buku", "#1A56DB", self.btn_menu_col.click)
        self.card_reading  = StatCard("Sedang Dibaca",   "0 Buku", "#059669", self.btn_menu_col.click)
        self.card_finished = StatCard("Selesai Dibaca",  "0 Buku", "#D97706", self.btn_menu_col.click)
        
        stats_layout.addWidget(self.card_total)
        stats_layout.addWidget(self.card_reading)
        stats_layout.addWidget(self.card_finished)
        
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
        
        self.combo_status = QComboBox()
        self.combo_status.addItems(["Sedang Membaca", "Selesai Dibaca", "Belum Dibaca"])
        self.combo_status.setFixedHeight(45)
        self.combo_status.setFixedWidth(200)
        
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
        self.input_col_date.setPlaceholderText("yyyy-MM-dd")
        self.input_col_date.setReadOnly(True)
        self.input_col_date.setStyleSheet("""
            QLineEdit {
                border: none; background: transparent;
                font-size: 15px; color: #374151; font-weight: 600;
            }
        """)

        self._btn_cal = QPushButton("📅")
        self._btn_cal.setFixedSize(30, 30)
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

        self.input_col_rating = QLineEdit()
        self.input_col_rating.setPlaceholderText("Rating (1-5)")
        self.input_col_rating.setFixedHeight(45)
        self.input_col_rating.setFixedWidth(150)
        
        row1_layout.addWidget(self.input_col_title)
        row1_layout.addWidget(self.combo_status)
        row1_layout.addWidget(date_container)
        row1_layout.addWidget(self.input_col_rating)
        
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
        
        self.table_col = QTableWidget(0, 5) 
        self.table_col.setHorizontalHeaderLabels(["Judul Buku", "Status", "Rating Pribadi", "Anotasi / Catatan", "Tgl Mulai"])
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

        # FIX: Context menu klik kanan
        self.table_col.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_col.customContextMenuRequested.connect(self._show_col_context_menu)
        # FIX: Sambungkan seleksi baris ke form CRUD
        self.table_col.itemSelectionChanged.connect(self._on_collection_selected)
        
        table_layout.addWidget(self.table_col)
        
        layout.addLayout(header_layout)
        layout.addWidget(crud_card)
        layout.addWidget(table_container, 1)
        
        return page

    def build_analytics_page(self):
        """Build analytics page — chart akan diisi data nyata saat pertama kali dibuka."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()
        lbl_title = QLabel("Analytics")
        lbl_title.setStyleSheet("font-size: 38px; font-weight: 800; color: #1A1F36;")
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()

        top_charts_layout = QHBoxLayout()
        top_charts_layout.setSpacing(20)

        # --- Pie Chart Card ---
        pie_card = QFrame()
        pie_card.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E3E8EE;")
        pie_layout = QVBoxLayout(pie_card)
        pie_layout.setContentsMargins(25, 25, 25, 25)
        lbl_pie_title = QLabel("Status Bacaan")
        lbl_pie_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1A1F36; border: none;")
        # FIX: Simpan referensi layout agar bisa diupdate chart-nya
        self._pie_chart_layout = pie_layout
        pie_layout.addWidget(lbl_pie_title)
        pie_layout.addSpacing(15)
        # Placeholder label sebelum data tersedia
        self._pie_placeholder = QLabel("Data akan muncul setelah login")
        self._pie_placeholder.setAlignment(Qt.AlignCenter)
        self._pie_placeholder.setStyleSheet("color: #9CA3AF; font-size: 16px;")
        pie_layout.addWidget(self._pie_placeholder)
        pie_layout.addStretch()

        # --- Bar Chart Card ---
        bar_card = QFrame()
        bar_card.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E3E8EE;")
        bar_layout = QVBoxLayout(bar_card)
        bar_layout.setContentsMargins(25, 25, 25, 25)
        lbl_bar_title = QLabel("Komposisi Kategori Buku")
        lbl_bar_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1A1F36; border: none;")
        self._bar_chart_layout = bar_layout
        bar_layout.addWidget(lbl_bar_title)
        bar_layout.addSpacing(15)
        self._bar_placeholder = QLabel("Data akan muncul setelah login")
        self._bar_placeholder.setAlignment(Qt.AlignCenter)
        self._bar_placeholder.setStyleSheet("color: #9CA3AF; font-size: 16px;")
        bar_layout.addWidget(self._bar_placeholder)
        bar_layout.addStretch()

        top_charts_layout.addWidget(pie_card)
        top_charts_layout.addWidget(bar_card)

        # --- Histogram Rating ---
        bottom_card = QFrame()
        bottom_card.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E3E8EE;")
        bottom_layout = QVBoxLayout(bottom_card)
        bottom_layout.setContentsMargins(25, 25, 25, 25)
        lbl_bottom_title = QLabel("Persebaran Rating Pribadi")
        lbl_bottom_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1A1F36; border: none;")
        self._hist_chart_layout = bottom_layout
        bottom_layout.addWidget(lbl_bottom_title)
        bottom_layout.addSpacing(15)
        self._hist_placeholder = QLabel("Data akan muncul setelah login")
        self._hist_placeholder.setAlignment(Qt.AlignCenter)
        self._hist_placeholder.setStyleSheet("color: #9CA3AF; font-size: 16px;")
        bottom_layout.addWidget(self._hist_placeholder)
        bottom_layout.addStretch()

        layout.addLayout(header_layout)
        layout.addLayout(top_charts_layout, 1)
        layout.addWidget(bottom_card, 1)

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

    def set_user(self, username: str):
        """Simpan username user yang sedang login dan tampilkan greeting."""
        self.current_user = username
        if hasattr(self, "lbl_welcome"):
            self.lbl_welcome.setText(f"Selamat datang kembali, {username}! 👋")

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
        self.btn_prev_page.setEnabled(self.current_page > 1)
        self.btn_next_page.setEnabled(self.current_page < max_page)

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
            rating  = str(tracker.get("rating_personal", 0))
            catatan = tracker.get("catatan", tracker.get("anotasi", ""))
            tgl     = tracker.get("tgl_mulai", tracker.get("tanggal_mulai", "-"))

            # Pakai cover cache — tidak baca disk ulang
            icon_buku = self._get_cover_icon(buku.get("local_cover_path", ""))

            for col, (text, centered) in enumerate([
                ("   " + judul, False), (status, True),
                (rating, True), (catatan, False), (tgl, True)
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

        self.input_col_rating.setText(str(tracker_data.get("rating_personal", "")))
        catatan = tracker_data.get("catatan", tracker_data.get("anotasi", ""))
        self.input_col_notes.setText(catatan)

        self._selected_tracker = tracker_data

    def _open_calendar(self):
        """Buka ModernCalendarPopup dan update input_col_date."""
        current_str = self.input_col_date.text().strip()
        current_qdate = QDate.fromString(current_str, "yyyy-MM-dd")
        if not current_qdate.isValid():
            current_qdate = QDate.currentDate()
        result = ModernCalendarPopup.get_date(current_qdate, self._date_container, self)
        if result:
            self.input_col_date.setText(result.toString("yyyy-MM-dd"))

    def _save_collection_edit(self):
        """Simpan perubahan status/rating/catatan ke tracker.json."""
        if not hasattr(self, "_selected_tracker") or not self._selected_tracker:
            QMessageBox.information(self, "Info", "Pilih baris koleksi terlebih dahulu.")
            return

        tracker_id = self._selected_tracker.get("id_tracker")
        status     = self.combo_status.currentText()
        catatan    = self.input_col_notes.text().strip()

        tgl_mulai  = self.input_col_date.text().strip() or "-"

        rating_text = self.input_col_rating.text().strip()
        try:
            rating = int(rating_text) if rating_text else 0
            if rating and not (1 <= rating <= 5):
                QMessageBox.warning(self, "Rating Tidak Valid", "Rating harus antara 1–5.")
                return
        except ValueError:
            QMessageBox.warning(self, "Rating Tidak Valid", "Masukkan angka untuk rating.")
            return

        self.data_manager.update_tracker(tracker_id, {
            "status_baca"    : status,
            "rating_personal": rating,
            "catatan"        : catatan,
            "tgl_mulai"      : tgl_mulai,
        })

        QMessageBox.information(self, "Berhasil", "Koleksi berhasil diperbarui.")
        self._selected_tracker = None
        self._load_collections_data()
        self._load_overview_data()

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

        for card, val in [
            (self.card_total,    f"{total} Buku"),
            (self.card_reading,  f"{membaca} Buku"),
            (self.card_finished, f"{selesai} Buku"),
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

    def _rebuild_analytics_charts(self):
        """Rebuild chart analytics dengan data nyata dari tracker user."""
        if not self.current_user or not self.data_manager:
            return

        tracker_list = self.data_manager.get_tracker_user(self.current_user)
        buku_dict    = {b.get("id_buku"): b for b in self._all_books_cache}

        # Hitung status
        status_count = {"Selesai": 0, "Sedang": 0, "Belum": 0}
        for t in tracker_list:
            s = t.get("status_baca", "")
            if "Selesai" in s:
                status_count["Selesai"] += 1
            elif "Sedang" in s:
                status_count["Sedang"] += 1
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
            ph = getattr(self, placeholder_attr, None)
            if ph:
                layout.removeWidget(ph)
                ph.deleteLater()
                setattr(self, placeholder_attr, None)
            # Hapus widget canvas lama jika ada (index 2 setelah title+spacing)
            while layout.count() > 2:
                item = layout.takeAt(layout.count() - 1)
                if item.widget():
                    item.widget().deleteLater()
            layout.addWidget(new_widget, 1)

        data_status_display = status_count if any(v > 0 for v in status_count.values()) else None
        pie_widget = visualizer.create_pie_chart_status(data_status_display)
        _replace_chart(self._pie_chart_layout, "_pie_placeholder", pie_widget)

        data_kat_display = kategori_count if kategori_count else None
        bar_widget = visualizer.create_bar_chart_kategori(data_kat_display)
        _replace_chart(self._bar_chart_layout, "_bar_placeholder", bar_widget)

        data_rating_display = rating_count if any(v > 0 for v in rating_count.values()) else None
        hist_widget = visualizer.create_histogram_rating(data_rating_display)
        _replace_chart(self._hist_chart_layout, "_hist_placeholder", hist_widget)

    # Alias lama agar kompatibel dengan kode yang sudah ada
    def _refresh_analytics(self):
        pass  # chart dirender saat tab analytics dibuka, bukan di awal

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
                "sinopsis" : book_data.get("sinopsis", book_data.get("description", "Sinopsis tidak tersedia.")),
                # Simpan id_buku untuk fitur bookmark dari dialog
                "id_buku"  : book_data.get("id_buku", ""),
            }
            dialog = BookDetailDialog(mapped)
        else:
            dialog = BookDetailDialog()

        # FIX: Hubungkan tombol Bookmark di dialog ke fungsi _add_to_collection
        if book_data:
            dialog.btn_bookmark.clicked.connect(
                lambda: self._add_to_collection(book_data)
            )

        dialog.exec_()