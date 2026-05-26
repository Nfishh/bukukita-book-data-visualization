# main/main.py
# Developer : Muhammad Nafis Idris 251524115
# Deskripsi : Entry point aplikasi BukuKita. Menginisialisasi
#             QApplication, mengatur sys.path agar semua modul (ui, auth,
#             book, data) dapat di-import dengan benar dari struktur
#             folder proyek, menyesuaikan working directory ke root
#             proyek agar path relatif assets/ dan output/ berfungsi,
#             lalu memunculkan ScreenManager dalam mode maximized.


# main/main.py
# Developer : Muhammad Nafis Idris 251524115
# Deskripsi : Entry point aplikasi BukuKita. Menginisialisasi
#             QApplication, mengatur sys.path agar semua modul (ui, auth,
#             book, data) dapat di-import dengan benar dari struktur
#             folder proyek, menyesuaikan working directory ke root
#             proyek agar path relatif assets/ dan output/ berfungsi,
#             lalu memunculkan ScreenManager dalam mode maximized.
#
#             [UPDATE] Ditambahkan dukungan PyInstaller: saat aplikasi
#             dijalankan sebagai .exe (frozen), aset read-only di-load
#             dari folder ekstraksi sementara (sys._MEIPASS), sementara
#             data yang bisa berubah (users.json, tracker.json) disimpan
#             di samping file .exe agar persisten antar sesi.


import sys
import os

os.environ["QT_LOGGING_RULES"] = "qt.gui.icc=false"


# =====================================================================
# DETEKSI MODE: development (jalan via python) atau frozen (.exe)
# =====================================================================
def is_frozen():
    """True jika aplikasi sedang berjalan sebagai .exe hasil PyInstaller."""
    return getattr(sys, "frozen", False)


def get_asset_root():
    """
    Folder berisi aset read-only (assets/, output/json/buku.json).
    - Mode .exe   : folder ekstraksi sementara PyInstaller (sys._MEIPASS)
    - Mode dev    : root proyek (folder di atas folder main/)
    """
    if is_frozen():
        return sys._MEIPASS  # disediakan PyInstaller saat runtime
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(current_dir)


def get_writable_root():
    """
    Folder untuk data yang BISA BERUBAH (data/users.json, data/tracker.json).
    Tidak boleh di dalam sys._MEIPASS karena folder itu dihapus saat
    aplikasi ditutup -- perubahan akan hilang.
    - Mode .exe   : folder tempat file .exe berada
    - Mode dev    : root proyek
    """
    if is_frozen():
        return os.path.dirname(sys.executable)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(current_dir)


# --- Setup sys.path agar semua modul (ui, auth, book, data) bisa diimport ---
ASSET_ROOT = get_asset_root()
WRITABLE_ROOT = get_writable_root()

# Tambahkan ASSET_ROOT ke path (agar import ui.xxx, auth.xxx dll bisa berjalan)
if ASSET_ROOT not in sys.path:
    sys.path.insert(0, ASSET_ROOT)

# Ubah working directory ke ASSET_ROOT agar path relatif aset
# (assets/images/logo.svg, assets/icons/*.svg, dll) di file UI tetap
# berfungsi TANPA perlu mengubah file UI satu per satu.
os.chdir(ASSET_ROOT)

# Bagikan WRITABLE_ROOT lewat environment variable agar DataManager
# bisa membacanya untuk menentukan lokasi users.json & tracker.json.
os.environ["BUKUKITA_WRITABLE_ROOT"] = WRITABLE_ROOT


from PyQt5.QtWidgets import QApplication
from screen_manager import ScreenManager


def main():
    app = QApplication(sys.argv)

    # Set font modern bawaan sistem
    font = app.font()
    font.setFamily("Segoe UI")
    app.setFont(font)

    # Panggil Screen Manager
    window = ScreenManager()
    window.showMaximized()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()