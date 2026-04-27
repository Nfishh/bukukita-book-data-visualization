from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QSpacerItem, QSizePolicy, QAction)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon 
from PyQt5.QtSvg import QSvgWidget

class SignupScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #FFFFFF; font-family: 'Segoe UI', sans-serif;")
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ==========================================
        # BAGIAN KIRI: Area Branding (Sama kayak Login)
        # ==========================================
        left_frame = QFrame()
        left_frame.setStyleSheet("background-color: #1A56DB;") 
        
        left_layout = QVBoxLayout(left_frame)
        left_layout.setAlignment(Qt.AlignCenter)
        
        # --- Logo BukuKita ---
        self.logo_svg = QSvgWidget("assets/images/logo.svg")
        self.logo_svg.setFixedSize(320, 140) 
        
        # --- Teks Welcome ---
        welcome_title = QLabel("Mulai Perjalananmu!")
        welcome_title.setStyleSheet("font-size: 56px; font-weight: 900; color: #FFFFFF; margin-top: 15px;")
        welcome_title.setAlignment(Qt.AlignCenter)
        
        welcome_subtitle = QLabel("Bergabunglah untuk mengelola koleksi dan\nmelacak progres membacamu dengan elegan.")
        welcome_subtitle.setStyleSheet("font-size: 22px; color: #E0E7FF; line-height: 1.5;") 
        welcome_subtitle.setAlignment(Qt.AlignCenter)
        
        left_layout.addWidget(self.logo_svg, alignment=Qt.AlignCenter)
        left_layout.addWidget(welcome_title, alignment=Qt.AlignCenter)
        left_layout.addSpacing(15)
        left_layout.addWidget(welcome_subtitle, alignment=Qt.AlignCenter)
        
        # ==========================================
        # BAGIAN KANAN: Form Sign Up Clean
        # ==========================================
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setAlignment(Qt.AlignCenter)
        
        # Kontainer pembungkus form
        form_container = QWidget()
        form_container.setFixedWidth(600) 
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        # FIX: Spacing dikecilin dikit jadi 15 karena formnya lebih panjang dari Login
        form_layout.setSpacing(15) 
        
        # --- Header Form ---
        title_signup = QLabel("Daftar Akun Baru")
        title_signup.setStyleSheet("font-size: 42px; font-weight: 800; color: #111827;") 
        title_signup.setAlignment(Qt.AlignCenter)
        
        subtitle_signup = QLabel("Lengkapi data di bawah ini untuk bergabung")
        subtitle_signup.setStyleSheet("font-size: 20px; color: #6B7280; margin-bottom: 20px;") 
        subtitle_signup.setAlignment(Qt.AlignCenter)
        
        # Gaya CSS Global untuk semua input biar gak repot ngulang
        input_style = """
            QLineEdit {
                border: 1.5px solid #D1D5DB;
                border-radius: 12px;
                padding: 0 20px;
                font-size: 20px;
                color: #111827;
                background-color: #FFFFFF;
            }
            QLineEdit:focus { border: 2px solid #1A56DB; }
        """
        label_style = "font-size: 22px; font-weight: 600; color: #374151; margin-top: 5px;"
        
        # --- Input Nama Lengkap ---
        lbl_name = QLabel("Nama Lengkap")
        lbl_name.setStyleSheet("font-size: 22px; font-weight: 600; color: #374151;") # Margin top gak perlu di elemen pertama
        
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Masukkan nama lengkap kamu")
        self.input_name.setFixedHeight(60) 
        self.input_name.setStyleSheet(input_style)
        
        # --- Input Username ---
        lbl_username = QLabel("Username")
        lbl_username.setStyleSheet(label_style)
        
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Buat username baru")
        self.input_user.setFixedHeight(60) 
        self.input_user.setStyleSheet(input_style)
        
        # --- Input Password ---
        lbl_password = QLabel("Password")
        lbl_password.setStyleSheet(label_style)
        
        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("••••••••")
        self.input_pass.setEchoMode(QLineEdit.Password)
        self.input_pass.setFixedHeight(60) 
        self.input_pass.setStyleSheet(input_style)

        # FIX MATA: Dipisah cara manggil Icon-nya biar gak kena TypeError
        self.action_eye = QAction(self)
        self.action_eye.setIcon(QIcon("assets/icons/ic_eye_close.svg"))
        self.input_pass.addAction(self.action_eye, QLineEdit.TrailingPosition)
        self.action_eye.triggered.connect(self.toggle_password)
        
        # --- Input Konfirmasi Password ---
        lbl_confirm = QLabel("Konfirmasi Password")
        lbl_confirm.setStyleSheet(label_style)

        
        self.input_confirm = QLineEdit()
        self.input_confirm.setPlaceholderText("••••••••")
        self.input_confirm.setEchoMode(QLineEdit.Password)
        self.input_confirm.setFixedHeight(60) 
        self.input_confirm.setStyleSheet(input_style)
        
        # FIX MATA: Dipisah cara manggil Icon-nya biar gak kena TypeError
        self.action_eye_confirm = QAction(self)
        self.action_eye_confirm.setIcon(QIcon("assets/icons/ic_eye_close.svg"))
        self.input_confirm.addAction(self.action_eye_confirm, QLineEdit.TrailingPosition)
        self.action_eye_confirm.triggered.connect(self.toggle_confirm)

        # --- Tombol Sign Up ---
        self.btn_signup = QPushButton("Daftar Sekarang") 
        self.btn_signup.setFixedHeight(60) 
        self.btn_signup.setCursor(Qt.PointingHandCursor)
        self.btn_signup.setStyleSheet("""
            QPushButton {
                background-color: #1A56DB;
                color: white;
                font-weight: bold;
                font-size: 20px;
                border-radius: 12px;
                border: none;
                margin-top: 15px; 
            }
            QPushButton:hover { background-color: #1E40AF; }
            QPushButton:pressed { background-color: #1E3A8A; }
        """)
        
        # --- Footer (Kembali ke Login) ---
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(8) 
        
        lbl_has_account = QLabel("Sudah punya akun?")
        lbl_has_account.setStyleSheet("color: #6B7280; font-size: 20px;") 
        
        self.btn_login_redirect = QPushButton("Masuk di sini")
        self.btn_login_redirect.setCursor(Qt.PointingHandCursor)
        self.btn_login_redirect.setStyleSheet("color: #1A56DB; font-size: 20px; font-weight: 600; border: none; background: transparent;") 
        
        footer_layout.addStretch()
        footer_layout.addWidget(lbl_has_account)
        footer_layout.addWidget(self.btn_login_redirect)
        footer_layout.addStretch()
        
        # --- Susun Semua ke Form Layout ---
        form_layout.addWidget(title_signup)
        form_layout.addWidget(subtitle_signup)
        
        form_layout.addWidget(lbl_name)
        form_layout.addWidget(self.input_name)
        
        form_layout.addWidget(lbl_username)
        form_layout.addWidget(self.input_user)
        
        form_layout.addWidget(lbl_password)
        form_layout.addWidget(self.input_pass)
        
        form_layout.addWidget(lbl_confirm)
        form_layout.addWidget(self.input_confirm)
        
        form_layout.addWidget(self.btn_signup)
        
        form_layout.addSpacing(10) 
        form_layout.addLayout(footer_layout)
        
        right_layout.addWidget(form_container)
        
        # Proporsi Kiri 45% : Kanan 55%
        main_layout.addWidget(left_frame, 45)
        main_layout.addWidget(right_frame, 55)

    def toggle_password(self):
        if self.input_pass.echoMode() == QLineEdit.Password:
            self.input_pass.setEchoMode(QLineEdit.Normal)
            self.action_eye.setIcon(QIcon("assets/icons/ic_eye_open.svg"))
        else:
            self.input_pass.setEchoMode(QLineEdit.Password)
            self.action_eye.setIcon(QIcon("assets/icons/ic_eye_close.svg"))
    
    def toggle_confirm(self):
        if self.input_confirm.echoMode() == QLineEdit.Password:
            self.input_confirm.setEchoMode(QLineEdit.Normal)
            self.action_eye_confirm.setIcon(QIcon("assets/icons/ic_eye_open.svg"))
        else:
            self.input_confirm.setEchoMode(QLineEdit.Password)
            self.action_eye_confirm.setIcon(QIcon("assets/icons/ic_eye_close.svg"))