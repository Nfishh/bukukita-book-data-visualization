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

        self.data_manager  = DataManager()
        self.auth_manager  = AuthManager(self.data_manager)
        self.book_manager  = BookManager(self.data_manager)
        self.rating_system = RatingSystem(self.data_manager)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.init_screens()

    def init_screens(self):
        self.login_screen  = LoginScreen()
        self.signup_screen = SignupScreen()
        self.dashboard_screen = DashboardScreen(
            data_manager=self.data_manager,
            book_manager=self.book_manager,
            rating_system=self.rating_system,
        )

        self.stacked_widget.addWidget(self.login_screen)    # 0
        self.stacked_widget.addWidget(self.signup_screen)   # 1
        self.stacked_widget.addWidget(self.dashboard_screen)# 2

        self.login_screen.btn_register.clicked.connect(self.go_to_signup)
        self.signup_screen.btn_login_redirect.clicked.connect(self.go_to_login)
        self.login_screen.btn_login.clicked.connect(self.handle_login)
        self.signup_screen.btn_signup.clicked.connect(self.handle_register)
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
            # Simpan credentials jika remember me dicentang
            self.login_screen.save_credentials_if_remembered()

            # Ambil data lengkap user untuk dashboard
            user_data = self.data_manager.get_user_data(username) or {}
            self.dashboard_screen.set_user(username, user_data)
            self.dashboard_screen.refresh_data()
            self.go_to_dashboard()
        else:
            QMessageBox.warning(self, "Login Gagal", "Username atau password salah.")

    def handle_register(self):
        username = self.signup_screen.input_user.text().strip()
        password = self.signup_screen.input_pass.text().strip()
        confirm  = self.signup_screen.input_confirm.text().strip()
        nama     = self.signup_screen.input_name.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Pendaftaran Gagal", "Username dan password tidak boleh kosong.")
            return
        if password != confirm:
            QMessageBox.warning(self, "Pendaftaran Gagal", "Password dan konfirmasi password tidak cocok.")
            return

        ok, pesan = self.auth_manager.register(username, password, nama_lengkap=nama)
        if ok:
            QMessageBox.information(self, "Berhasil", f"Akun '{username}' berhasil dibuat. Silakan login.")
            self.signup_screen.input_name.clear()
            self.signup_screen.input_user.clear()
            self.signup_screen.input_pass.clear()
            self.signup_screen.input_confirm.clear()
            self.go_to_login()
        else:
            QMessageBox.warning(self, "Pendaftaran Gagal", pesan)

    def handle_logout(self):
        self.auth_manager.logout()
        # Kembalikan form login sesuai status remember me
        self.login_screen.pre_fill_after_logout(self.dashboard_screen.current_user or "")
        self.go_to_login()

    # =====================
    # Navigasi
    # =====================

    def go_to_login(self):
        self.stacked_widget.setCurrentIndex(0)

    def go_to_signup(self):
        self.stacked_widget.setCurrentIndex(1)

    def go_to_dashboard(self):
        self.stacked_widget.setCurrentIndex(2)
        self.showMaximized()