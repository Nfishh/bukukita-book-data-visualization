from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from ui.ui_login import LoginScreen
from ui.ui_signup import SignupScreen
from ui.ui_dashboard import DashboardScreen  # Import Dashboard kita!

class ScreenManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BukuKita - Aplikasi Manajemen Buku")
        self.resize(1280, 800) # Ukuran awal dibesarin dikit buat dashboard
        
        # Bikin tumpukan layar utama
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.init_screens()
        
    def init_screens(self):
        # 1. Inisialisasi Layar
        self.login_screen = LoginScreen()
        self.signup_screen = SignupScreen()
        self.dashboard_screen = DashboardScreen()
        
        # 2. Masukkan ke tumpukan (Urutan: 0=Login, 1=Signup, 2=Dashboard)
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.signup_screen)
        self.stacked_widget.addWidget(self.dashboard_screen)
        
        # 3. Sambungkan Tombol-Tombol
        # Transisi Login <-> Sign Up
        self.login_screen.btn_register.clicked.connect(self.go_to_signup)
        self.signup_screen.btn_login_redirect.clicked.connect(self.go_to_login)
        
        # Transisi ke Dashboard (Klik tombol Masuk)
        self.login_screen.btn_login.clicked.connect(self.go_to_dashboard)
        
        # Transisi Logout dari Dashboard (Balik ke Login)
        self.dashboard_screen.btn_logout.clicked.connect(self.go_to_login)

    def go_to_login(self):
        self.stacked_widget.setCurrentIndex(0)
        
    def go_to_signup(self):
        self.stacked_widget.setCurrentIndex(1)
        
    def go_to_dashboard(self):
        # YAY! Pindah ke Dashboard
        self.stacked_widget.setCurrentIndex(2)
        # Bikin otomatis Fullscreen biar puas lihat grafiknya!
        self.showMaximized()
        
    def register_user(self):
        print("Mencoba mendaftar akun baru...")