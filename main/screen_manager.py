# main/screen_manager.py
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QMessageBox

from data.data_manager import DataManager
from auth.auth_manager import AuthManager
from book.book_manager import BookManager
from book.rating_system import RatingSystem

from ui.ui_login import LoginScreen
from ui.ui_signup import SignupScreen
from ui.ui_dashboard import DashboardScreen


class ScreenManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BukuKita - Aplikasi Manajemen Buku")
        self.resize(1280, 800)

        # ===================================================
        # Inisialisasi layer data & logika (dependency chain)
        # ===================================================
        self.data_manager = DataManager()
        self.auth_manager = AuthManager(self.data_manager)
        self.book_manager = BookManager(self.data_manager)
        self.rating_system = RatingSystem(self.data_manager)

        # Tumpukan layar utama
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.init_screens()

    def init_screens(self):
        # 1. Inisialisasi layar dengan dependensi yang tepat
        self.login_screen = LoginScreen()
        self.signup_screen = SignupScreen()
        self.dashboard_screen = DashboardScreen(
            data_manager=self.data_manager,
            book_manager=self.book_manager,
            rating_system=self.rating_system,
        )

        # 2. Masukkan ke tumpukan (0=Login, 1=Signup, 2=Dashboard)
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.signup_screen)
        self.stacked_widget.addWidget(self.dashboard_screen)

        # 3. Sambungkan navigasi antar layar
        self.login_screen.btn_register.clicked.connect(self.go_to_signup)
        self.signup_screen.btn_login_redirect.clicked.connect(self.go_to_login)

        # Tombol Masuk -> validasi login terlebih dahulu
        self.login_screen.btn_login.clicked.connect(self.handle_login)

        # Tombol Daftar -> proses registrasi
        self.signup_screen.btn_signup.clicked.connect(self.handle_register)

        # Logout dari dashboard
        self.dashboard_screen.btn_logout.clicked.connect(self.handle_logout)

    # =====================
    # Handler Autentikasi
    # =====================

    def handle_login(self):
        username = self.login_screen.input_user.text().strip()
        password = self.login_screen.input_pass.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Login Gagal", "Username dan password tidak boleh kosong.")
            return

        if self.auth_manager.login(username, password):
            # Login berhasil → refresh dashboard lalu tampilkan
            self.dashboard_screen.set_user(username)
            self.dashboard_screen.refresh_data()
            self.go_to_dashboard()
            # Bersihkan input password setelah login
            self.login_screen.input_pass.clear()
        else:
            QMessageBox.warning(self, "Login Gagal", "Username atau password salah.")

    def handle_register(self):
        username = self.signup_screen.input_user.text().strip()
        password = self.signup_screen.input_pass.text().strip()
        confirm  = self.signup_screen.input_confirm.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Pendaftaran Gagal", "Username dan password tidak boleh kosong.")
            return

        if password != confirm:
            QMessageBox.warning(self, "Pendaftaran Gagal", "Password dan konfirmasi password tidak cocok.")
            return

        if self.auth_manager.register(username, password):
            QMessageBox.information(self, "Pendaftaran Berhasil", f"Akun '{username}' berhasil dibuat. Silakan login.")
            # Bersihkan form signup
            self.signup_screen.input_name.clear()
            self.signup_screen.input_user.clear()
            self.signup_screen.input_pass.clear()
            self.signup_screen.input_confirm.clear()
            self.go_to_login()
        else:
            QMessageBox.warning(self, "Pendaftaran Gagal", f"Username '{username}' sudah digunakan.")

    def handle_logout(self):
        self.auth_manager.logout()
        self.go_to_login()

    # =====================
    # Navigasi Layar
    # =====================

    def go_to_login(self):
        self.stacked_widget.setCurrentIndex(0)
        self.showNormal()
        self.resize(1280, 800)

    def go_to_signup(self):
        self.stacked_widget.setCurrentIndex(1)

    def go_to_dashboard(self):
        self.stacked_widget.setCurrentIndex(2)
        self.showMaximized()
