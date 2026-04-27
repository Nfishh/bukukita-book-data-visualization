from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QSpacerItem, QSizePolicy,
                             QStackedWidget, QButtonGroup, QComboBox, QMenu, QAction) 
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor
from PyQt5.QtSvg import QSvgWidget

from ui.ui_detail import BookDetailDialog
from ui.data_viz import DataVisualizer


# ==========================================
# FIX: Class Khusus Kartu Statistik Animasi
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
    def __init__(self):
        super().__init__()
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
        
        self.page_overview = self.build_overview_page()
        self.page_library = self.build_library_page()
        self.page_collections = self.build_collections_page()
        self.page_analytics = self.build_analytics_page() 
        
        self.content_stack.addWidget(self.page_overview)    
        self.content_stack.addWidget(self.page_library)     
        self.content_stack.addWidget(self.page_collections) 
        self.content_stack.addWidget(self.page_analytics)   
        
        self.btn_menu_dash.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))
        self.btn_menu_lib.clicked.connect(lambda: self.content_stack.setCurrentIndex(1))
        self.btn_menu_col.clicked.connect(lambda: self.content_stack.setCurrentIndex(2))
        self.btn_menu_analytics.clicked.connect(lambda: self.content_stack.setCurrentIndex(3)) 
        
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
        
        self.search_bar_dash = QLineEdit()
        self.search_bar_dash.setPlaceholderText("Cari di dashboard...")
        self.search_bar_dash.setFixedWidth(350)
        self.search_bar_dash.setFixedHeight(50)
        self.search_bar_dash.setStyleSheet("""
            QLineEdit { background-color: #FFFFFF; border: 1px solid #E3E8EE; border-radius: 25px; padding: 0 20px; font-size: 18px; color: #1A1F36; }
            QLineEdit:focus { border: 2px solid #1A56DB; }
        """)
        
        btn_user = QPushButton()
        btn_user.setIcon(QIcon("assets/icons/ic_user.svg"))
        btn_user.setIconSize(QSize(30, 30))
        btn_user.setFixedSize(50, 50)
        btn_user.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E3E8EE; border-radius: 25px;")
        btn_user.setCursor(Qt.PointingHandCursor)
        
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(self.search_bar_dash)
        header_layout.addSpacing(15)
        header_layout.addWidget(btn_user)
        
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        card_total = StatCard("Total Koleksi", "124 Buku", "#1A56DB", self.btn_menu_col.click)
        card_reading = StatCard("Sedang Dibaca", "3 Buku", "#059669", self.btn_menu_col.click)
        card_finished = StatCard("Selesai Dibaca", "45 Buku", "#D97706", self.btn_menu_col.click)
        
        stats_layout.addWidget(card_total)
        stats_layout.addWidget(card_reading)
        stats_layout.addWidget(card_finished)
        
        table_container = QFrame()
        table_container.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E3E8EE;")
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(25, 25, 25, 25)
        
        lbl_table_title = QLabel("Koleksi Terbaru")
        lbl_table_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1A1F36; border: none;") 
        
        self.table_dash = QTableWidget(5, 5) 
        self.table_dash.setHorizontalHeaderLabels(["Judul Buku", "Penulis", "Tahun", "Rating", "Status"])
        self.table_dash.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_dash.setEditTriggers(QTableWidget.NoEditTriggers) 
        self.table_dash.setFocusPolicy(Qt.NoFocus)
        self.table_dash.setShowGrid(False)
        self.table_dash.horizontalHeader().setSectionsClickable(False)
        self.table_dash.setStyleSheet("""
            QTableWidget { background-color: #FFFFFF; border: none; font-size: 18px; color: #4F566B; }
            QHeaderView { background-color: transparent; }
            QHeaderView::section { 
                background-color: #F8FAFC;
                padding: 12px 15px; 
                font-size: 16px; 
                font-weight: 800; 
                color: #475569; 
                border: none; 
                border-top: 1px solid #E2E8F0;
                border-bottom: 2px solid #E2E8F0; 
            }
            QHeaderView::section:first {
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
                border-left: 1px solid #E2E8F0;
            }
            QHeaderView::section:last {
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
                border-right: 1px solid #E2E8F0;
            }
            QTableWidget::item { padding: 15px; border-bottom: 1px solid #F1F5F9; }
        """)
        
        dummy_data = [
            ("Bumi Manusia", "Pramoedya Ananta Toer", "1980", "⭐ 4.8", "Selesai"),
            ("Laskar Pelangi", "Andrea Hirata", "2005", "⭐ 4.7", "Selesai"),
            ("Laut Bercerita", "Leila S. Chudori", "2017", "⭐ 4.9", "Membaca")
        ]
        
        for row, data in enumerate(dummy_data):
            for col, item in enumerate(data):
                cell = QTableWidgetItem(item)
                if col >= 2: cell.setTextAlignment(Qt.AlignCenter)
                self.table_dash.setItem(row, col, cell)
                
        self.table_dash.verticalHeader().setDefaultSectionSize(60)
        self.table_dash.verticalHeader().setVisible(False) 
        
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
        layout.setSpacing(25)
        
        header_layout = QHBoxLayout()
        title_layout = QVBoxLayout()
        lbl_title = QLabel("Library Database")
        lbl_title.setStyleSheet("font-size: 38px; font-weight: 800; color: #1A1F36;")
        lbl_desc = QLabel("Jelajahi 500 koleksi buku eksklusif yang siap kamu tambahkan ke My Collections.")
        lbl_desc.setStyleSheet("font-size: 18px; color: #6B7280; margin-top: 5px;")
        title_layout.addWidget(lbl_title)
        title_layout.addWidget(lbl_desc)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Toolbar: Search & Dropdown
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(15)
        
        self.search_bar_lib = QLineEdit()
        self.search_bar_lib.setPlaceholderText("Cari judul buku, penulis, atau ISBN...")
        self.search_bar_lib.setFixedHeight(45)
        self.search_bar_lib.setFixedWidth(400)
        
        self.action_search = QAction(self)
        self.action_search.setIcon(QIcon("assets/icons/ic_search.svg"))
        self.search_bar_lib.addAction(self.action_search, QLineEdit.LeadingPosition)
        
        self.search_bar_lib.setStyleSheet("""
            QLineEdit { 
                background-color: #FFFFFF; 
                border: 1.5px solid #E3E8EE; 
                border-radius: 22px;
                padding: 0 15px 0 5px; 
                font-size: 16px; 
                color: #1A1F36; 
            }
            QLineEdit:focus { border: 2px solid #1A56DB; }
        """)
        
        self.combo_filter_lib = QComboBox()
        self.combo_filter_lib.addItems(["Semua Kategori", "Fiksi", "Non-Fiksi"])
        self.combo_filter_lib.setFixedHeight(45)
        self.combo_filter_lib.setFixedWidth(220)
        self.combo_filter_lib.setCursor(Qt.PointingHandCursor)
        self.combo_filter_lib.setStyleSheet("""
            QComboBox { 
                background-color: #FFFFFF; 
                border: 1.5px solid #E3E8EE; 
                border-radius: 22px; 
                padding: 0 20px; 
                font-size: 16px; 
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
            QComboBox QAbstractItemView::item {
                min-height: 45px; 
                padding: 10px;
            }
        """)
        
        toolbar_layout.addWidget(self.search_bar_lib)
        toolbar_layout.addWidget(self.combo_filter_lib)
        toolbar_layout.addStretch()
        
        table_container = QFrame()
        table_container.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E3E8EE;")
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(25, 25, 25, 25)
        
        self.table_lib = QTableWidget(6, 6) 
        self.table_lib.setHorizontalHeaderLabels(["Judul Buku", "Penulis", "Tahun", "Kategori", "Rating", "Aksi"])
        self.table_lib.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_lib.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table_lib.setEditTriggers(QTableWidget.NoEditTriggers) 
        self.table_lib.setFocusPolicy(Qt.NoFocus)
        self.table_lib.setShowGrid(False)
        self.table_lib.horizontalHeader().setSectionsClickable(False)

        # FIX (dari Doc 1): Cover art placeholder — icon & row size
        self.table_lib.setIconSize(QSize(35, 50))
        self.table_lib.verticalHeader().setDefaultSectionSize(75)
        self.table_lib.verticalHeader().setVisible(False)

        self.table_lib.setStyleSheet("""
            QTableWidget { background-color: #FFFFFF; border: none; font-size: 18px; color: #4F566B; }
            QHeaderView { background-color: transparent; }
            QHeaderView::section { 
                background-color: #F8FAFC; 
                padding: 12px 15px; 
                font-size: 16px; 
                font-weight: 800; 
                color: #475569; 
                border: none; 
                border-top: 1px solid #E2E8F0;
                border-bottom: 2px solid #E2E8F0; 
            }
            QHeaderView::section:first {
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
                border-left: 1px solid #E2E8F0;
            }
            QHeaderView::section:last {
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
                border-right: 1px solid #E2E8F0;
            }
            QTableWidget::item { padding: 15px; border-bottom: 1px solid #F1F5F9; }
        """)
        
        dummy_lib_data = [
            ("Filosofi Teras", "Henry Manampiring", "2018", "Non-Fiksi", "⭐ 4.8"),
            ("Sapiens", "Yuval Noah Harari", "2011", "Non-Fiksi", "⭐ 4.9"),
            ("Bumi Manusia", "Pramoedya Ananta Toer", "1980", "Fiksi", "⭐ 4.8"),
            ("Laut Bercerita", "Leila S. Chudori", "2017", "Fiksi", "⭐ 4.9"),
            ("Atomic Habits", "James Clear", "2018", "Non-Fiksi", "⭐ 4.8"),
            ("Gadis Kretek", "Eka Kurniawan", "2012", "Fiksi", "⭐ 4.6")
        ]
        
        # FIX (dari Doc 1): Buat placeholder cover abu-abu
        placeholder_cover = QPixmap(35, 50)
        placeholder_cover.fill(QColor("#CBD5E1"))
        cover_icon = QIcon(placeholder_cover)

        for row, data in enumerate(dummy_lib_data):
            for col, item in enumerate(data):
                # FIX (dari Doc 1): Tambah spasi di depan teks judul biar rapi di samping icon
                cell = QTableWidgetItem("   " + item if col == 0 else item)
                
                # FIX (dari Doc 1): Pasang icon cover hanya di kolom Judul
                if col == 0:
                    cell.setIcon(cover_icon)
                    
                if col >= 2:
                    cell.setTextAlignment(Qt.AlignCenter)
                self.table_lib.setItem(row, col, cell)
                
            btn_action = QPushButton()
            btn_action.setIcon(QIcon("assets/icons/ic_more_vert.svg")) 
            btn_action.setIconSize(QSize(24, 24))
            btn_action.setCursor(Qt.PointingHandCursor)
            btn_action.setStyleSheet("""
                QPushButton { background: transparent; border: none; }
                QPushButton::menu-indicator { image: none; width: 0px; } 
            """)
            
            menu = QMenu()
            menu.setStyleSheet("""
                QMenu { background-color: #FFFFFF; border: 1px solid #E3E8EE; border-radius: 8px; padding: 5px; }
                QMenu::item { padding: 10px 20px; font-size: 16px; font-weight: bold; color: #1A1F36; border-radius: 6px; }
                QMenu::item:selected { background-color: #F7F9FC; color: #1A56DB; }
            """)
            
            action_detail = QAction(QIcon("assets/icons/ic_detail.svg"), "Detail", self)
            action_detail.triggered.connect(self.show_book_detail) 
            menu.addAction(action_detail)
            
            action_bookmark = QAction(QIcon("assets/icons/ic_bookmark.svg"), "Bookmark", self)
            menu.addAction(action_bookmark)
            
            btn_action.setMenu(menu)
            self.table_lib.setCellWidget(row, 5, btn_action)
        
        table_layout.addWidget(self.table_lib)
        
        layout.addLayout(header_layout)
        layout.addLayout(toolbar_layout)
        layout.addWidget(table_container, 1) 
        
        return page

    def show_book_detail(self):
        dialog = BookDetailDialog()
        dialog.exec_()

    def _show_col_context_menu(self, position):
        """Context menu klik kanan di tabel My Collections"""
        # Pastikan klik mengenai baris yang valid, bukan area kosong
        index = self.table_col.indexAt(position)
        if not index.isValid():
            return

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #E3E8EE;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 10px 20px 10px 8px;
                font-size: 16px;
                font-weight: bold;
                color: #1A1F36;
                border-radius: 6px;
            }
            QMenu::item:selected {
                background-color: #EFF6FF;
                color: #1A56DB;
            }
            QMenu::icon {
                padding-left: 6px;
            }
        """)

        action_detail = QAction(QIcon("assets/icons/ic_detail.svg"), "Detail Buku", self)
        action_detail.triggered.connect(self.show_book_detail)
        menu.addAction(action_detail)

        # Munculkan menu tepat di posisi kursor
        menu.exec_(self.table_col.viewport().mapToGlobal(position))

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
        
        self.input_col_rating = QLineEdit()
        self.input_col_rating.setPlaceholderText("Rating (1-5)")
        self.input_col_rating.setFixedHeight(45)
        self.input_col_rating.setFixedWidth(150)
        
        row1_layout.addWidget(self.input_col_title)
        row1_layout.addWidget(self.combo_status)
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
        
        self.btn_col_delete = QPushButton("Hapus")
        self.btn_col_delete.setFixedHeight(45)
        self.btn_col_delete.setCursor(Qt.PointingHandCursor)
        self.btn_col_delete.setStyleSheet(btn_style + "QPushButton { background-color: #DC2626; } QPushButton:hover { background-color: #B91C1C; }")
        
        row2_layout.addWidget(self.input_col_notes)
        row2_layout.addWidget(self.btn_col_save)
        row2_layout.addWidget(self.btn_col_delete)
        
        for widget in [self.combo_status, self.input_col_rating, self.input_col_notes]:
            widget.setStyleSheet("""
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
                QComboBox QAbstractItemView::item {
                    min-height: 45px; 
                    padding: 10px;
                }
            """)
            
        crud_layout.addWidget(lbl_crud_title)
        crud_layout.addLayout(row1_layout)
        crud_layout.addLayout(row2_layout)
        
        table_container = QFrame()
        table_container.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E3E8EE;")
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(25, 25, 25, 25)
        
        self.table_col = QTableWidget(5, 5) 
        self.table_col.setHorizontalHeaderLabels(["Judul Buku", "Status", "Rating Pribadi", "Anotasi / Catatan", "Tgl Mulai"])
        self.table_col.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_col.setEditTriggers(QTableWidget.NoEditTriggers) 
        self.table_col.setFocusPolicy(Qt.NoFocus)
        self.table_col.setSelectionBehavior(QTableWidget.SelectRows) 
        self.table_col.setShowGrid(False)

        # Cover placeholder — sama seperti tabel Library
        self.table_col.setIconSize(QSize(35, 50))
        self.table_col.verticalHeader().setDefaultSectionSize(75)

        self.table_col.setStyleSheet("""
            QTableWidget { background-color: #FFFFFF; border: none; font-size: 18px; color: #4F566B; }
            QHeaderView { background-color: transparent; }
            QHeaderView::section { 
                background-color: #F8FAFC; 
                padding: 12px 15px; 
                font-size: 16px; 
                font-weight: 800; 
                color: #475569; 
                border: none; 
                border-top: 1px solid #E2E8F0;
                border-bottom: 2px solid #E2E8F0; 
            }
            QHeaderView::section:first {
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
                border-left: 1px solid #E2E8F0;
            }
            QHeaderView::section:last {
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
                border-right: 1px solid #E2E8F0;
            }
            QTableWidget::item { padding: 15px; border-bottom: 1px solid #F1F5F9; }
            QTableWidget::item:selected { background-color: #EFF6FF; color: #1A56DB; } 
        """)
        
        dummy_col_data = [
            ("Bumi Manusia", "Selesai Dibaca", "5", "Karya epik Pramoedya! Sangat menginspirasi.", "12 Okt 2025"),
            ("Laut Bercerita", "Sedang Membaca", "4", "Sedih banget ceritanya, belum kuat lanjutin.", "20 Okt 2025"),
            ("Atomic Habits", "Selesai Dibaca", "5", "Buku wajib buat self-improvement.", "01 Sep 2025")
        ]

        # Cover placeholder abu-abu — sama seperti tabel Library
        col_placeholder = QPixmap(35, 50)
        col_placeholder.fill(QColor("#CBD5E1"))
        col_cover_icon = QIcon(col_placeholder)

        for row, data in enumerate(dummy_col_data):
            for col, item in enumerate(data):
                # Tambah spasi di depan teks judul biar rapi di samping icon
                cell = QTableWidgetItem("   " + item if col == 0 else item)
                if col == 0:
                    cell.setIcon(col_cover_icon)
                if col in [1, 2, 4]: cell.setTextAlignment(Qt.AlignCenter)
                self.table_col.setItem(row, col, cell)

        self.table_col.verticalHeader().setVisible(False)

        # --- Fitur klik kanan: context menu "Detail Buku" ---
        self.table_col.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_col.customContextMenuRequested.connect(self._show_col_context_menu) 
        
        table_layout.addWidget(self.table_col)
        
        layout.addLayout(header_layout)
        layout.addWidget(crud_card)
        layout.addWidget(table_container, 1) 
        
        return page

    def build_analytics_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        
        visualizer = DataVisualizer()
        
        header_layout = QHBoxLayout()
        title_layout = QVBoxLayout()
        lbl_title = QLabel("Analytics & Insight")
        lbl_title.setStyleSheet("font-size: 38px; font-weight: 800; color: #1A1F36;")
        lbl_desc = QLabel("Visualisasi data koleksimu berdasarkan kategori, rating, dan status baca.")
        lbl_desc.setStyleSheet("font-size: 18px; color: #6B7280; margin-top: 5px;")
        title_layout.addWidget(lbl_title)
        title_layout.addWidget(lbl_desc)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        top_charts_layout = QHBoxLayout()
        top_charts_layout.setSpacing(25)
        
        # [A] Pie Chart (Status Bacaan)
        pie_card = QFrame()
        pie_card.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E3E8EE;")
        pie_layout = QVBoxLayout(pie_card)
        pie_layout.setContentsMargins(25, 25, 25, 25)
        
        lbl_pie_title = QLabel("Distribusi Status Bacaan")
        lbl_pie_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1A1F36; border: none;")
        
        pie_chart_widget = visualizer.create_pie_chart_status()
        
        pie_layout.addWidget(lbl_pie_title)
        pie_layout.addSpacing(15)
        pie_layout.addWidget(pie_chart_widget, 1)
        
        # [B] Bar Chart (Kategori)
        bar_card = QFrame()
        bar_card.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E3E8EE;")
        bar_layout = QVBoxLayout(bar_card)
        bar_layout.setContentsMargins(25, 25, 25, 25)
        
        lbl_bar_title = QLabel("Komposisi Kategori Buku")
        lbl_bar_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1A1F36; border: none;")
        
        bar_chart_widget = visualizer.create_bar_chart_kategori()
        
        bar_layout.addWidget(lbl_bar_title)
        bar_layout.addSpacing(15)
        bar_layout.addWidget(bar_chart_widget, 1)
        
        top_charts_layout.addWidget(pie_card)
        top_charts_layout.addWidget(bar_card)
        
        # Bottom Chart (Histogram Rating)
        bottom_card = QFrame()
        bottom_card.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E3E8EE;")
        bottom_layout = QVBoxLayout(bottom_card)
        bottom_layout.setContentsMargins(25, 25, 25, 25)
        
        lbl_bottom_title = QLabel("Persebaran Rating Pribadi")
        lbl_bottom_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1A1F36; border: none;")
        
        rating_chart_widget = visualizer.create_histogram_rating()
        
        bottom_layout.addWidget(lbl_bottom_title)
        bottom_layout.addSpacing(15)
        bottom_layout.addWidget(rating_chart_widget, 1)
        
        layout.addLayout(header_layout)
        layout.addLayout(top_charts_layout, 1) 
        layout.addWidget(bottom_card, 1)       
        
        return page