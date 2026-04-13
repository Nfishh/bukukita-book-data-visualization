from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QCheckBox, QAction)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon 
from PyQt5.QtSvg import QSvgWidget

class LoginScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #FFFFFF; font-family: 'Segoe UI', sans-serif;")
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ==========================================
        # BAGIAN KIRI: Area Branding
        # ==========================================
        left_frame = QFrame()
        left_frame.setStyleSheet("background-color: #1A56DB;") 
        
        left_layout = QVBoxLayout(left_frame)
        left_layout.setAlignment(Qt.AlignCenter)
        
        # --- Logo BukuKita ---
        self.logo_svg = QSvgWidget("assets/images/logo.svg")
        self.logo_svg.setFixedSize(320, 140) 
        
        # --- Teks Welcome ---
        welcome_title = QLabel("Selamat Datang!")
        welcome_title.setStyleSheet("font-size: 56px; font-weight: 900; color: #FFFFFF; margin-top: 15px;")
        welcome_title.setAlignment(Qt.AlignCenter)
        
        welcome_subtitle = QLabel("Kelola koleksi bukumu dan lacak progres\nmembacamu dengan lebih elegan dan mudah.")
        welcome_subtitle.setStyleSheet("font-size: 22px; color: #E0E7FF; line-height: 1.5;") 
        welcome_subtitle.setAlignment(Qt.AlignCenter)
        
        left_layout.addWidget(self.logo_svg, alignment=Qt.AlignCenter)
        left_layout.addWidget(welcome_title, alignment=Qt.AlignCenter)
        left_layout.addSpacing(15)
        left_layout.addWidget(welcome_subtitle, alignment=Qt.AlignCenter)
        
        # ==========================================
        # BAGIAN KANAN: Form Login Clean
        # ==========================================
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setAlignment(Qt.AlignCenter)
        
        # Kontainer pembungkus form
        form_container = QWidget()
        form_container.setFixedWidth(600) 
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(25) 
        
        # --- Header Form ---
        title_login = QLabel("Login untuk Melanjutkan")
        title_login.setStyleSheet("font-size: 42px; font-weight: 800; color: #111827;") 
        title_login.setAlignment(Qt.AlignCenter)
        
        subtitle_login = QLabel("Silakan masukkan username dan password kamu")
        subtitle_login.setStyleSheet("font-size: 20px; color: #6B7280; margin-bottom: 25px;") 
        subtitle_login.setAlignment(Qt.AlignCenter)
        
        # --- Input Username ---
        lbl_username = QLabel("Username")
        lbl_username.setStyleSheet("font-size: 22px; font-weight: 600; color: #374151;")
        
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Masukkan username kamu")
        self.input_user.setFixedHeight(60) 
        self.input_user.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #D1D5DB;
                border-radius: 12px;
                padding: 0 20px;
                font-size: 20px;
                color: #111827;
                background-color: #FFFFFF;
            }
            QLineEdit:focus { border: 2px solid #1A56DB; }
        """)
        
        # --- Input Password ---
        lbl_password = QLabel("Password")
        lbl_password.setStyleSheet("font-size: 22px; font-weight: 600; color: #374151; margin-top: 5px;")
        
        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("••••••••")
        self.input_pass.setEchoMode(QLineEdit.Password)
        self.input_pass.setFixedHeight(60) 
        self.input_pass.setStyleSheet(self.input_user.styleSheet())
        
        # FIX MATA: Dipisah cara manggil Icon-nya biar gak kena TypeError
        self.action_eye = QAction(self)
        self.action_eye.setIcon(QIcon("assets/icons/ic_eye_close.svg"))
        self.input_pass.addAction(self.action_eye, QLineEdit.TrailingPosition)
        self.action_eye.triggered.connect(self.toggle_password)
        
        # --- Remember Me & Forgot Password ---
        extra_layout = QHBoxLayout()
        
        self.chk_remember = QCheckBox("Ingatkan saya")
        self.chk_remember.setStyleSheet("""
            QCheckBox { color: #4B5563; font-size: 20px; } 
            QCheckBox::indicator { 
                width: 22px; 
                height: 22px; 
                border-radius: 5px; 
                border: 1.5px solid #D1D5DB; 
            }
            QCheckBox::indicator:checked { 
                background-color: #1A56DB; 
                border: 1.5px solid #1A56DB; 
                image: url('assets/icons/ic_check.svg'); 
            }
        """)
        
        btn_forgot = QPushButton("Lupa password?")
        btn_forgot.setCursor(Qt.PointingHandCursor)
        btn_forgot.setStyleSheet("color: #1A56DB; font-size: 20px; font-weight: 600; border: none; background: transparent;") 
        
        extra_layout.addWidget(self.chk_remember)
        extra_layout.addStretch()
        extra_layout.addWidget(btn_forgot)
        
        # --- Tombol Login ---
        self.btn_login = QPushButton("Masuk") 
        self.btn_login.setFixedHeight(60) 
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #1A56DB;
                color: white;
                font-weight: bold;
                font-size: 20px;
                border-radius: 12px;
                border: none;
                margin-top: 5px; 
            }
            QPushButton:hover { background-color: #1E40AF; }
            QPushButton:pressed { background-color: #1E3A8A; }
        """)
        
        # --- Footer (Contact Admin / Daftar) ---
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(8) 
        footer_layout.setAlignment(Qt.AlignCenter)
        
        lbl_no_account = QLabel("Belum punya akun?")
        lbl_no_account.setStyleSheet("color: #6B7280; font-size: 20px;") 
        
        self.btn_register = QPushButton("Daftar di sini")
        self.btn_register.setCursor(Qt.PointingHandCursor)
        self.btn_register.setStyleSheet("color: #1A56DB; font-size: 20px; font-weight: 600; border: none; background: transparent;") 
        
        footer_layout.addWidget(lbl_no_account)
        footer_layout.addWidget(self.btn_register) 
        
        # --- Susun Semua ke Form Layout ---
        form_layout.addWidget(title_login)
        form_layout.addWidget(subtitle_login)
        
        form_layout.addWidget(lbl_username)
        form_layout.addWidget(self.input_user)
        
        form_layout.addWidget(lbl_password)
        form_layout.addWidget(self.input_pass)
        
        form_layout.addLayout(extra_layout)
        form_layout.addWidget(self.btn_login)
        
        form_layout.addSpacing(15) 
        form_layout.addLayout(footer_layout)
        
        right_layout.addWidget(form_container)
        
        # Proporsi Kiri 45% : Kanan 55%
        main_layout.addWidget(left_frame, 45)
        main_layout.addWidget(right_frame, 55)

    # --- Fungsi untuk ganti mode mata ---
    def toggle_password(self):
        if self.input_pass.echoMode() == QLineEdit.Password:
            self.input_pass.setEchoMode(QLineEdit.Normal)
            self.action_eye.setIcon(QIcon("assets/icons/ic_eye_open.svg"))
        else:
            self.input_pass.setEchoMode(QLineEdit.Password)
            self.action_eye.setIcon(QIcon("assets/icons/ic_eye_close.svg"))