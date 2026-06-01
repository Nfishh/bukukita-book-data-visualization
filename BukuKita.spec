# -*- mode: python ; coding: utf-8 -*-
# =====================================================================
# BukuKita.spec  --  Konfigurasi build PyInstaller untuk aplikasi BukuKita
# =====================================================================
# Cara pakai (jalankan dari ROOT proyek, folder yang berisi main/, ui/,
# auth/, book/, data/, output/, assets/):
#
#     pyinstaller BukuKita.spec
#
# Hasil akhir ada di folder:  dist/BukuKita/BukuKita.exe
# =====================================================================

block_cipher = None


a = Analysis(
    ['main/main.py'],                 # entry point aplikasi
    pathex=['.'],                     # root proyek -- agar import ui.*, auth.* dll terdeteksi
    binaries=[],
    datas=[
        # (sumber, tujuan_di_dalam_bundle)
        ('assets', 'assets'),                 # logo, ikon SVG, cover buku
        ('output/json/buku.json',             # master data buku (read-only)
         'output/json'),
        # CATATAN: data/ (users.json, tracker.json) SENGAJA tidak dibundel.
        # File itu read-write dan akan dibuat otomatis oleh DataManager
        # di samping file .exe saat aplikasi pertama dijalankan.
    ],
    hiddenimports=[
        # PyQt5 -- modul yang kadang tidak terdeteksi otomatis
        'PyQt5.QtSvg',
        'PyQt5.QtPrintSupport',
        # Matplotlib -- backend Qt5 dipakai data_viz.py
        'matplotlib.backends.backend_qt5agg',
        'matplotlib.backends.backend_qtagg',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Kecilkan ukuran .exe -- buang modul yang tidak dipakai
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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BukuKita',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                         # kompres -- opsional, set False jadi True jika UPX tidak terpasang
    console=False,                    # False = tanpa jendela CMD hitam.
                                      # Saat debugging awal, set True agar
                                      # pesan error terlihat bila .exe crash.
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/images/logo.ico',    # opsional -- hapus baris ini jika
                                      # belum punya file .ico
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BukuKita',                  # nama folder hasil di dist/
)
