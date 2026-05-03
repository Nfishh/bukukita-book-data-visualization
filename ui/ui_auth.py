from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QCheckBox, QAction, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon 
from PyQt5.QtSvg import QSvgWidget

# ==========================================
# 1. HALAMAN LOGIN
# ==========================================
class LoginScreen(QWidget):
    login_successful = pyqtSignal() 

    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager
        self.setStyleSheet("background-color: #FFFFFF; font-family: 'Segoe UI', sans-serif;")
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- BAGIAN KIRI: Area Branding ---
        left_frame = QFrame()
        left_frame.setStyleSheet("background-color: #1A56DB;") 
        
        left_layout = QVBoxLayout(left_frame)
        left_layout.setAlignment(Qt.AlignCenter)
        
        self.logo_svg = QSvgWidget("assets/images/logo.svg")
        self.logo_svg.setFixedSize(320, 140) 
        
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
        
        # --- BAGIAN KANAN: Form Login ---
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setAlignment(Qt.AlignCenter)
        
        form_container = QWidget()
        form_container.setFixedWidth(600) 
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(25) 
        
        title_login = QLabel("Login untuk Melanjutkan")
        title_login.setStyleSheet("font-size: 42px; font-weight: 800; color: #111827;") 
        title_login.setAlignment(Qt.AlignCenter)
        
        subtitle_login = QLabel("Silakan masukkan username dan password kamu")
        subtitle_login.setStyleSheet("font-size: 20px; color: #6B7280; margin-bottom: 25px;") 
        subtitle_login.setAlignment(Qt.AlignCenter)
        
        lbl_username = QLabel("Username")
        lbl_username.setStyleSheet("font-size: 22px; font-weight: 600; color: #374151;")
        
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Masukkan username kamu")
        self.input_user.setFixedHeight(60) 
        self.input_user.setStyleSheet("""
            QLineEdit { border: 1.5px solid #D1D5DB; border-radius: 12px; padding: 0 20px; font-size: 20px; color: #111827; background-color: #FFFFFF; }
            QLineEdit:focus { border: 2px solid #1A56DB; }
        """)
        
        lbl_password = QLabel("Password")
        lbl_password.setStyleSheet("font-size: 22px; font-weight: 600; color: #374151; margin-top: 5px;")
        
        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("••••••••")
        self.input_pass.setEchoMode(QLineEdit.Password)
        self.input_pass.setFixedHeight(60) 
        self.input_pass.setStyleSheet(self.input_user.styleSheet())
        
        self.action_eye = QAction(self)
        self.action_eye.setIcon(QIcon("assets/icons/ic_eye_close.svg"))
        self.input_pass.addAction(self.action_eye, QLineEdit.TrailingPosition)
        self.action_eye.triggered.connect(self.toggle_password)
        
        extra_layout = QHBoxLayout()
        self.chk_remember = QCheckBox("Ingatkan saya")
        self.chk_remember.setStyleSheet("""
            QCheckBox { color: #4B5563; font-size: 20px; } 
            QCheckBox::indicator { width: 22px; height: 22px; border-radius: 5px; border: 1.5px solid #D1D5DB; }
            QCheckBox::indicator:checked { background-color: #1A56DB; border: 1.5px solid #1A56DB; image: url('assets/icons/ic_check.svg'); }
        """)
        btn_forgot = QPushButton("Lupa password?")
        btn_forgot.setCursor(Qt.PointingHandCursor)
        btn_forgot.setStyleSheet("color: #1A56DB; font-size: 20px; font-weight: 600; border: none; background: transparent;") 
        extra_layout.addWidget(self.chk_remember)
        extra_layout.addStretch()
        extra_layout.addWidget(btn_forgot)
        
        self.btn_login = QPushButton("Masuk") 
        self.btn_login.setFixedHeight(60) 
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setStyleSheet("""
            QPushButton { background-color: #1A56DB; color: white; font-weight: bold; font-size: 20px; border-radius: 12px; border: none; margin-top: 5px; }
            QPushButton:hover { background-color: #1E40AF; }
            QPushButton:pressed { background-color: #1E3A8A; }
        """)
        self.btn_login.clicked.connect(self.handle_login)
        
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(8) 
        footer_layout.setAlignment(Qt.AlignCenter)
        
        lbl_no_account = QLabel("Belum punya akun?")
        lbl_no_account.setStyleSheet("color: #6B7280; font-size: 20px;") 
        
        self.btn_signup_link = QPushButton("Daftar di sini")
        self.btn_signup_link.setCursor(Qt.PointingHandCursor)
        self.btn_signup_link.setStyleSheet("color: #1A56DB; font-size: 20px; font-weight: 600; border: none; background: transparent;") 
        
        footer_layout.addWidget(lbl_no_account)
        footer_layout.addWidget(self.btn_signup_link) 
        
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
        main_layout.addWidget(left_frame, 45)
        main_layout.addWidget(right_frame, 55)

    # --- FIX: FUNGSI PEMBUAT POP-UP MODERN ---
    def show_custom_popup(self, title, text, type_msg):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        
        if type_msg == "error":
            msg.setIcon(QMessageBox.Critical)
        elif type_msg == "warning":
            msg.setIcon(QMessageBox.Warning)
        elif type_msg == "success":
            msg.setIcon(QMessageBox.Information)

        # Styling CSS super elegan buat Pop-up
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #FFFFFF;
                font-family: 'Segoe UI', sans-serif;
            }
            QMessageBox QLabel {
                color: #111827;
                font-size: 18px;
                font-weight: 500;
                padding: 10px 20px 10px 0px;
            }
            QPushButton {
                background-color: #1A56DB;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
                padding: 8px 24px;
                min-width: 80px;
                margin-top: 10px;
                margin-bottom: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1E40AF;
            }
        """)
        msg.exec_()

    def toggle_password(self):
        if self.input_pass.echoMode() == QLineEdit.Password:
            self.input_pass.setEchoMode(QLineEdit.Normal)
            self.action_eye.setIcon(QIcon("assets/icons/ic_eye_open.svg"))
        else:
            self.input_pass.setEchoMode(QLineEdit.Password)
            self.action_eye.setIcon(QIcon("assets/icons/ic_eye_close.svg"))

    def handle_login(self):
        username = self.input_user.text()
        password = self.input_pass.text()

        if not username or not password:
            self.show_custom_popup("Peringatan", "Username dan Password tidak boleh kosong!", "warning")
            return

        is_success = self.auth_manager.login(username, password)
        
        if is_success:
            self.input_pass.clear()
            self.login_successful.emit() 
        else:
            # FIX: Pakai Custom Pop-up biar cakep!
            self.show_custom_popup("Gagal Login", "Yah, Username atau Password-mu salah!\nSilakan periksa dan coba lagi ya.", "error")


# ==========================================
# 2. HALAMAN SIGN UP
# ==========================================
class SignupScreen(QWidget):
    signup_successful = pyqtSignal()

    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager
        self.setStyleSheet("background-color: #FFFFFF; font-family: 'Segoe UI', sans-serif;")
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        left_frame = QFrame()
        left_frame.setStyleSheet("background-color: #1A56DB;") 
        
        left_layout = QVBoxLayout(left_frame)
        left_layout.setAlignment(Qt.AlignCenter)
        
        self.logo_svg = QSvgWidget("assets/images/logo.svg")
        self.logo_svg.setFixedSize(320, 140) 
        
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
        
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setAlignment(Qt.AlignCenter)
        
        form_container = QWidget()
        form_container.setFixedWidth(600) 
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(15) 
        
        title_signup = QLabel("Daftar Akun Baru")
        title_signup.setStyleSheet("font-size: 42px; font-weight: 800; color: #111827;") 
        title_signup.setAlignment(Qt.AlignCenter)
        
        subtitle_signup = QLabel("Lengkapi data di bawah ini untuk bergabung")
        subtitle_signup.setStyleSheet("font-size: 20px; color: #6B7280; margin-bottom: 20px;") 
        subtitle_signup.setAlignment(Qt.AlignCenter)
        
        input_style = """
            QLineEdit { border: 1.5px solid #D1D5DB; border-radius: 12px; padding: 0 20px; font-size: 20px; color: #111827; background-color: #FFFFFF; }
            QLineEdit:focus { border: 2px solid #1A56DB; }
        """
        label_style = "font-size: 22px; font-weight: 600; color: #374151; margin-top: 5px;"
        
        lbl_name = QLabel("Nama Lengkap")
        lbl_name.setStyleSheet("font-size: 22px; font-weight: 600; color: #374151;")
        
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Masukkan nama lengkap kamu")
        self.input_name.setFixedHeight(60) 
        self.input_name.setStyleSheet(input_style)
        
        lbl_username = QLabel("Username")
        lbl_username.setStyleSheet(label_style)
        
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Buat username baru")
        self.input_user.setFixedHeight(60) 
        self.input_user.setStyleSheet(input_style)
        
        # --- FIX: Input Password dengan Icon Mata ---
        lbl_password = QLabel("Password")
        lbl_password.setStyleSheet(label_style)
        
        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("••••••••")
        self.input_pass.setEchoMode(QLineEdit.Password)
        self.input_pass.setFixedHeight(60) 
        self.input_pass.setStyleSheet(input_style)

        self.action_eye_pass = QAction(self)
        self.action_eye_pass.setIcon(QIcon("assets/icons/ic_eye_close.svg"))
        self.input_pass.addAction(self.action_eye_pass, QLineEdit.TrailingPosition)
        self.action_eye_pass.triggered.connect(self.toggle_password)
        
        # --- FIX: Input Konfirmasi Password dengan Icon Mata ---
        lbl_confirm = QLabel("Konfirmasi Password")
        lbl_confirm.setStyleSheet(label_style)
        
        self.input_confirm = QLineEdit()
        self.input_confirm.setPlaceholderText("••••••••")
        self.input_confirm.setEchoMode(QLineEdit.Password)
        self.input_confirm.setFixedHeight(60) 
        self.input_confirm.setStyleSheet(input_style)

        self.action_eye_confirm = QAction(self)
        self.action_eye_confirm.setIcon(QIcon("assets/icons/ic_eye_close.svg"))
        self.input_confirm.addAction(self.action_eye_confirm, QLineEdit.TrailingPosition)
        self.action_eye_confirm.triggered.connect(self.toggle_confirm_password)
        
        self.btn_signup = QPushButton("Daftar Sekarang") 
        self.btn_signup.setFixedHeight(60) 
        self.btn_signup.setCursor(Qt.PointingHandCursor)
        self.btn_signup.setStyleSheet("""
            QPushButton { background-color: #1A56DB; color: white; font-weight: bold; font-size: 20px; border-radius: 12px; border: none; margin-top: 15px; }
            QPushButton:hover { background-color: #1E40AF; }
            QPushButton:pressed { background-color: #1E3A8A; }
        """)
        self.btn_signup.clicked.connect(self.handle_signup)
        
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(8) 
        
        lbl_has_account = QLabel("Sudah punya akun?")
        lbl_has_account.setStyleSheet("color: #6B7280; font-size: 20px;") 
        
        self.btn_login_link = QPushButton("Masuk di sini")
        self.btn_login_link.setCursor(Qt.PointingHandCursor)
        self.btn_login_link.setStyleSheet("color: #1A56DB; font-size: 20px; font-weight: 600; border: none; background: transparent;") 
        
        footer_layout.addStretch()
        footer_layout.addWidget(lbl_has_account)
        footer_layout.addWidget(self.btn_login_link)
        footer_layout.addStretch()
        
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
        main_layout.addWidget(left_frame, 45)
        main_layout.addWidget(right_frame, 55)

    # --- FIX: FUNGSI PEMBUAT POP-UP MODERN UNTUK SIGN UP ---
    def show_custom_popup(self, title, text, type_msg):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        
        if type_msg == "error":
            msg.setIcon(QMessageBox.Critical)
        elif type_msg == "warning":
            msg.setIcon(QMessageBox.Warning)
        elif type_msg == "success":
            msg.setIcon(QMessageBox.Information)

        msg.setStyleSheet("""
            QMessageBox {
                background-color: #FFFFFF;
                font-family: 'Segoe UI', sans-serif;
            }
            QMessageBox QLabel {
                color: #111827;
                font-size: 18px;
                font-weight: 500;
                padding: 10px 20px 10px 0px;
            }
            QPushButton {
                background-color: #1A56DB;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
                padding: 8px 24px;
                min-width: 80px;
                margin-top: 10px;
                margin-bottom: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1E40AF;
            }
        """)
        msg.exec_()

    # --- FIX: FUNGSI TOGGLE MATA SIGN UP ---
    def toggle_password(self):
        if self.input_pass.echoMode() == QLineEdit.Password:
            self.input_pass.setEchoMode(QLineEdit.Normal)
            self.action_eye_pass.setIcon(QIcon("assets/icons/ic_eye_open.svg"))
        else:
            self.input_pass.setEchoMode(QLineEdit.Password)
            self.action_eye_pass.setIcon(QIcon("assets/icons/ic_eye_close.svg"))

    def toggle_confirm_password(self):
        if self.input_confirm.echoMode() == QLineEdit.Password:
            self.input_confirm.setEchoMode(QLineEdit.Normal)
            self.action_eye_confirm.setIcon(QIcon("assets/icons/ic_eye_open.svg"))
        else:
            self.input_confirm.setEchoMode(QLineEdit.Password)
            self.action_eye_confirm.setIcon(QIcon("assets/icons/ic_eye_close.svg"))

    def handle_signup(self):
        username = self.input_user.text()
        password = self.input_pass.text()
        confirm = self.input_confirm.text()

        if not username or not password or not confirm:
            self.show_custom_popup("Peringatan", "Ups! Semua kolom wajib diisi ya.", "warning")
            return
            
        if password != confirm:
            self.show_custom_popup("Peringatan", "Password dan Konfirmasi Password tidak cocok!", "warning")
            return

        is_success = self.auth_manager.register(username, password)
        
        if is_success:
            self.show_custom_popup("Sukses", "Hore! Akun berhasil dibuat! Silakan login.", "success")
            self.input_user.clear()
            self.input_pass.clear()
            self.input_confirm.clear()
            self.input_name.clear()
            self.signup_successful.emit() 
        else:
            self.show_custom_popup("Gagal", "Username sudah terdaftar! Coba nama yang lain yuk.", "error")