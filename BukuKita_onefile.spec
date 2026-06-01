# -*- mode: python ; coding: utf-8 -*-
# =====================================================================
# BukuKita_onefile.spec
# Konfigurasi build PyInstaller mode --onefile (SATU FILE .exe TUNGGAL)
# =====================================================================
# Hasil akhir: dist/BukuKita.exe  <-- satu file, itu saja yang di-share.
#
# Cara pakai (jalankan dari ROOT proyek):
#     pyinstaller BukuKita_onefile.spec
#
# CATATAN PENTING:
#   buku.json, assets/  -> dibundel KE DALAM .exe (read-only, aman).
#   users.json, tracker.json -> TIDAK dibundel. Dibuat otomatis oleh
#   aplikasi di folder "data/" di samping file .exe saat pertama
#   dijalankan, sehingga data registrasi & koleksi tetap PERSISTEN.
# =====================================================================

block_cipher = None


a = Analysis(
    ['main/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('output/json/buku.json', 'output/json'),
    ],
    hiddenimports=[
        'PyQt5.QtSvg',
        'PyQt5.QtPrintSupport',
        'matplotlib.backends.backend_qt5agg',
        'matplotlib.backends.backend_qtagg',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# --- Perbedaan utama dengan mode --onedir ---
# Semua komponen (a.binaries, a.zipfiles, a.datas) dimasukkan LANGSUNG
# ke dalam EXE, dan TIDAK ADA blok COLLECT. Inilah yang membuat
# hasilnya berupa satu file tunggal.
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BukuKita',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                    # True saat debugging agar error terlihat
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/images/logo.ico',    # hapus baris ini jika belum punya .ico
)
