# ui/ui_profile.py
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QLineEdit, QScrollArea,
                             QWidget, QFileDialog, QMessageBox, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QColor, QPainter, QPainterPath, QPen
from PyQt5.QtSvg import QSvgWidget


class _AvatarLabel(QLabel):
    """Label foto profil berbentuk lingkaran sempurna (Fix Anti-Clipping Bug PyQt)."""
    def __init__(self, size=100, border_width=3, parent=None):
        super().__init__(parent)
        self._size = size
        self._border = border_width
        self.setFixedSize(size, size)
        self._clear()

    def _clear(self):
        """Gambar siluet kepala dan pundak ala WhatsApp yang rapi."""
        px = QPixmap(self._size, self._size)
        px.fill(Qt.transparent)
        
        painter = QPainter(px)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        
        inner_size = self._size - 2 * self._border
        
        # 1. Background bulat abu-abu terang
        painter.setBrush(QColor("#E2E8F0"))
        painter.drawEllipse(self._border, self._border, inner_size, inner_size)
        
        # 2. Bikin batasan area biar siluet orangnya nggak keluar dari lingkaran
        path = QPainterPath()
        path.addEllipse(self._border, self._border, inner_size, inner_size)
        painter.setClipPath(path)
        
        # 3. Gambar siluet orang (abu-abu gelap)
        painter.setBrush(QColor("#94A3B8"))
        
        # Kepala
        head_size = inner_size * 0.4
        head_x = self._border + (inner_size - head_size) / 2
        head_y = self._border + inner_size * 0.15
        painter.drawEllipse(int(head_x), int(head_y), int(head_size), int(head_size))
        
        # Pundak/Badan
        body_w = inner_size * 0.85
        body_h = inner_size * 0.6
        body_x = self._border + (inner_size - body_w) / 2
        body_y = self._border + inner_size * 0.6
        painter.drawEllipse(int(body_x), int(body_y), int(body_w), int(body_h))
        
        # 4. Gambar Border putih semi-transparan di atasnya
        painter.setClipping(False)
        pen = QPen(QColor(255, 255, 255, 60)) # Warna border rgba(255,255,255, 0.25)
        pen.setWidth(self._border)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        offset = self._border / 2.0
        painter.drawEllipse(int(offset), int(offset), int(self._size - self._border), int(self._size - self._border))
        
        painter.end()
        self.setPixmap(px)

    def set_image(self, path: str):
        """Pasang foto asli dengan potongan lingkaran yang sempurna."""
        src = QPixmap(path)
        if src.isNull():
            self._clear()
            return
            
        inner_size = self._size - 2 * self._border
        # Resize dan potong gambar asli
        src = src.scaled(inner_size, inner_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        x = (src.width()  - inner_size) // 2
        y = (src.height() - inner_size) // 2
        src = src.copy(x, y, inner_size, inner_size)
        
        px = QPixmap(self._size, self._size)
        px.fill(Qt.transparent)
        
        painter = QPainter(px)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Gambar foto ke dalam batasan lingkaran
        path_clip = QPainterPath()
        path_clip.addEllipse(self._border, self._border, inner_size, inner_size)
        painter.setClipPath(path_clip)
        painter.drawPixmap(self._border, self._border, src)
        
        # Gambar Border
        painter.setClipping(False)
        pen = QPen(QColor(255, 255, 255, 60))
        pen.setWidth(self._border)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        offset = self._border / 2.0
        painter.drawEllipse(int(offset), int(offset), int(self._size - self._border), int(self._size - self._border))
        
        painter.end()
        self.setPixmap(px)


# ============================================================
# DIALOG PROFIL LENGKAP
# ============================================================
class ProfileDialog(QDialog):
    profile_updated = pyqtSignal(dict)

    def __init__(self, username: str, user_data: dict,
                 tracker_list: list, buku_dict: dict,
                 data_manager, parent=None):
        super().__init__(parent)
        self.username     = username
        self.user_data    = dict(user_data)
        self.tracker_list = tracker_list
        self.buku_dict    = buku_dict
        self.data_manager = data_manager

        self.setWindowTitle("Profil Saya")
        self.setFixedSize(680, 780)
        self.setStyleSheet("background-color: #F8FAFC; font-family: 'Segoe UI', sans-serif;")
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setGeometry(0, 0, 680, 780)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical { border:none; background:transparent; width:8px; margin: 0px; }
            QScrollBar::handle:vertical { background:rgba(148,163,184,0.4); border-radius:4px; min-height:40px; }
            QScrollBar::handle:vertical:hover { background:rgba(100,116,139,0.7); }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
        """)

        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        root = QVBoxLayout(content)
        root.setContentsMargins(40, 36, 40, 36)
        root.setSpacing(24)

        # ── Header Abu-abu Elegan dengan Watermark Logo ──
        header = QFrame()
        header.setStyleSheet("""
            QFrame { 
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #475569, stop:1 #1E293B); 
                border-radius: 20px; 
            }
        """)
        
        # FIX: Watermark Logo BukuKita di belakang foto profil
        watermark = QSvgWidget("assets/images/logo.svg", header)
        watermark.setFixedSize(600, 300)
        watermark.setGeometry(-6, -30, 600, 300) # Ditaruh presisi di tengah header
        
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.08) # Transparansi 8% yang kalem
        watermark.setGraphicsEffect(opacity_effect)
        watermark.lower() # Pastikan layernya paling belakang

        hlay = QVBoxLayout(header)
        hlay.setContentsMargins(30, 35, 30, 35)
        hlay.setSpacing(12)
        hlay.setAlignment(Qt.AlignCenter)

        # Foto Profil yang udah Anti-Bug!
        self._avatar = _AvatarLabel(size=104, border_width=4)
        foto_path = self.user_data.get("foto_profile", "")
        if foto_path and os.path.exists(foto_path):
            self._avatar.set_image(foto_path)
        
        # Tombol Aksi Foto
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_ganti_foto = QPushButton("Ganti Foto")
        btn_ganti_foto.setFixedHeight(32)
        btn_ganti_foto.setCursor(Qt.PointingHandCursor)
        btn_ganti_foto.setStyleSheet("""
            QPushButton { background-color: rgba(255,255,255,0.15); color: #FFFFFF;
                border: none; border-radius: 12px; padding: 0 15px;
                font-size: 13px; font-weight: 600; }
            QPushButton:hover { background-color: rgba(255,255,255,0.25); }
        """)
        btn_ganti_foto.clicked.connect(self._pick_photo)

        btn_hapus_foto = QPushButton("Hapus Foto")
        btn_hapus_foto.setFixedHeight(32)
        btn_hapus_foto.setCursor(Qt.PointingHandCursor)
        btn_hapus_foto.setStyleSheet("""
            QPushButton { background-color: transparent; color: #FDA4AF;
                border: 1px solid rgba(251,113,133,0.4); border-radius: 12px; padding: 0 15px;
                font-size: 13px; font-weight: 600; }
            QPushButton:hover { background-color: rgba(251,113,133,0.1); color: #FFE4E6; }
        """)
        btn_hapus_foto.clicked.connect(self._remove_photo)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ganti_foto)
        btn_layout.addWidget(btn_hapus_foto)
        btn_layout.addStretch()

        nama_display = self.user_data.get("nama_lengkap") or self.username
        lbl_nama = QLabel(nama_display)
        lbl_nama.setStyleSheet("font-size: 26px; font-weight: 800; color: #FFFFFF; background: transparent;")
        lbl_nama.setAlignment(Qt.AlignCenter)

        lbl_uname = QLabel(f"@{self.username}")
        lbl_uname.setStyleSheet("font-size: 15px; color: #94A3B8; font-weight: 500; background: transparent;")
        lbl_uname.setAlignment(Qt.AlignCenter)

        hlay.addWidget(self._avatar, alignment=Qt.AlignCenter)
        hlay.addLayout(btn_layout)
        hlay.addSpacing(4)
        hlay.addWidget(lbl_nama)
        hlay.addWidget(lbl_uname)

        # ── Statistik singkat ──
        selesai  = sum(1 for t in self.tracker_list if "Selesai"  in t.get("status_baca",""))
        membaca  = sum(1 for t in self.tracker_list if "Sedang"   in t.get("status_baca",""))
        belum    = sum(1 for t in self.tracker_list if "Belum"    in t.get("status_baca",""))
        drop     = sum(1 for t in self.tracker_list if "Drop"     in t.get("status_baca",""))

        stat_row = QHBoxLayout()
        stat_row.setSpacing(16)
        for label, val, color in [
            ("Selesai Dibaca", selesai, "#10B981"),
            ("Sedang Dibaca",  membaca, "#3B82F6"),
            ("Belum Dibaca",   belum,   "#F59E0B"),
            ("Drop",           drop,    "#DC2626"),
        ]:
            card = self._stat_card(label, val, color)
            stat_row.addWidget(card)

        # ── Form Edit Profil ──
        form_card = QFrame()
        form_card.setStyleSheet("QFrame { background:#FFFFFF; border-radius:16px; border:none; }")
        flay = QVBoxLayout(form_card)
        flay.setContentsMargins(28, 26, 28, 26)
        flay.setSpacing(16)

        lbl_form_title = QLabel("Informasi Akun")
        lbl_form_title.setStyleSheet("font-size:18px; font-weight:800; color:#0F172A; border:none;")
        flay.addWidget(lbl_form_title)
        flay.addSpacing(4)

        def _field(label_text, placeholder, value="", is_pass=False):
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-size:14px; font-weight:600; color:#475569; background:transparent;")
            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setText(value)
            inp.setFixedHeight(46)
            if is_pass:
                inp.setEchoMode(QLineEdit.Password)
            inp.setStyleSheet("""
                QLineEdit { border: 1px solid #E2E8F0; border-radius: 10px;
                    padding: 0 16px; font-size: 15px; color: #0F172A; background: #F8FAFC; }
                QLineEdit:focus { border: 1.5px solid #475569; background: #FFFFFF; }
            """)
            return lbl, inp

        lbl_n, self.inp_nama = _field(
            "Nama Lengkap", "Masukkan nama lengkap",
            self.user_data.get("nama_lengkap", "")
        )
        lbl_u, self.inp_uname = _field("Username", "", self.username)
        self.inp_uname.setReadOnly(True)
        self.inp_uname.setStyleSheet(self.inp_uname.styleSheet() +
            "QLineEdit { background:#F1F5F9; color:#94A3B8; border: 1px solid #F1F5F9; }")

        lbl_p,  self.inp_pass_baru  = _field("Password Baru",    "Kosongkan jika tidak ingin diubah", is_pass=True)
        lbl_cp, self.inp_pass_conf  = _field("Konfirmasi Password", "Ulangi password baru", is_pass=True)

        for w in [lbl_n, self.inp_nama, lbl_u, self.inp_uname,
                  lbl_p, self.inp_pass_baru, lbl_cp, self.inp_pass_conf]:
            flay.addWidget(w)

        btn_save = QPushButton("Simpan Perubahan")
        btn_save.setFixedHeight(48)
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setStyleSheet("""
            QPushButton { background-color:#334155; color:#FFFFFF; font-size:15px;
                font-weight:bold; border-radius:12px; border:none; margin-top:12px; }
            QPushButton:hover { background-color:#1E293B; }
        """)
        btn_save.clicked.connect(self._save_profile)
        flay.addWidget(btn_save)

        # ── Riwayat Bacaan ──
        history_card = QFrame()
        history_card.setStyleSheet("QFrame { background:#FFFFFF; border-radius:16px; border:none; }")
        hislay = QVBoxLayout(history_card)
        hislay.setContentsMargins(28, 26, 28, 26)
        hislay.setSpacing(12)

        lbl_his = QLabel("Aktivitas Terbaru")
        lbl_his.setStyleSheet("font-size:18px; font-weight:800; color:#0F172A; border:none;")
        hislay.addWidget(lbl_his)
        hislay.addSpacing(4)

        for tracker in self.tracker_list:
            buku   = self.buku_dict.get(tracker.get("book_id"), {})
            judul  = buku.get("judul", tracker.get("book_id", "-"))
            status = tracker.get("status_baca", "-")
            rating = tracker.get("rating_personal", 0)

            row = QHBoxLayout()
            lbl_j = QLabel(judul)
            lbl_j.setStyleSheet("font-size:15px; color:#1E293B; font-weight:600; background:transparent;")
            lbl_j.setWordWrap(True)

            status_color = {"Selesai": "#10B981", "Sedang": "#3B82F6", "Belum": "#F59E0B"}
            clr = next((v for k, v in status_color.items() if k in status), "#94A3B8")
            lbl_s = QLabel(status)
            lbl_s.setFixedWidth(130)
            lbl_s.setAlignment(Qt.AlignCenter)
            lbl_s.setStyleSheet(f"""
                font-size:12px; font-weight:bold; color:{clr};
                background-color:{clr}15; border-radius:8px;
                padding:4px 0px; border:none;
            """)

            stars = "★" * int(rating) + "☆" * (5 - int(rating)) if rating else "—"
            lbl_r = QLabel(stars)
            lbl_r.setStyleSheet("font-size:15px; color:#F59E0B; background:transparent;")
            lbl_r.setFixedWidth(70)
            lbl_r.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            row.addWidget(lbl_j, 1)
            row.addWidget(lbl_s)
            row.addWidget(lbl_r)
            hislay.addLayout(row)

            sep = QFrame()
            sep.setFrameShape(QFrame.HLine)
            sep.setStyleSheet("color: #F8FAFC;")
            hislay.addWidget(sep)

        if not self.tracker_list:
            lbl_empty = QLabel("Rak bukumu masih kosong nih, yuk mulai eksplorasi!")
            lbl_empty.setStyleSheet("color:#94A3B8; font-size:14px; background:transparent; font-style: italic;")
            lbl_empty.setAlignment(Qt.AlignCenter)
            hislay.addSpacing(10)
            hislay.addWidget(lbl_empty)
            hislay.addSpacing(10)

        # Susun semua
        root.addWidget(header)
        root.addLayout(stat_row)
        root.addWidget(form_card)
        root.addWidget(history_card)
        root.addStretch()

        scroll.setWidget(content)

    def _stat_card(self, label, value, color):
        card = QFrame()
        card.setStyleSheet("""
            QFrame { background:#FFFFFF; border-radius:16px; border:none; }
        """)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 18, 16, 18)
        lay.setSpacing(4)
        
        lv = QLabel(str(value))
        lv.setStyleSheet(f"font-size:32px; font-weight:900; color:{color}; background:transparent;")
        lv.setAlignment(Qt.AlignCenter)
        
        ll = QLabel(label)
        ll.setStyleSheet("font-size:13px; color:#64748B; font-weight:600; background:transparent;")
        ll.setAlignment(Qt.AlignCenter)
        
        lay.addWidget(lv)
        lay.addWidget(ll)
        return card

    def _pick_photo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Pilih Foto Profil", "",
            "Gambar (*.png *.jpg *.jpeg *.webp)"
        )
        if path:
            self._avatar.set_image(path)
            self.user_data["foto_profile"] = path

    def _remove_photo(self):
        if not self.user_data.get("foto_profile"):
            return 
            
        konfirmasi = QMessageBox.question(
            self, "Hapus Foto", 
            "Yakin nih mau menghapus foto profilmu?", 
            QMessageBox.Yes | QMessageBox.No
        )
        if konfirmasi == QMessageBox.Yes:
            self.user_data["foto_profile"] = ""
            self._avatar._clear() 

    def _save_profile(self):
        nama      = self.inp_nama.text().strip()
        pass_baru = self.inp_pass_baru.text().strip()
        pass_conf = self.inp_pass_conf.text().strip()

        if pass_baru and pass_baru != pass_conf:
            QMessageBox.warning(self, "Gagal", "Konfirmasi password tidak cocok.")
            return

        update = {"nama_lengkap": nama}
        
        update["foto_profile"] = self.user_data.get("foto_profile", "")
            
        if pass_baru:
            update["password"] = pass_baru

        self.data_manager.update_user_data(self.username, update)
        self.user_data.update(update)
        self.profile_updated.emit(self.user_data)
        QMessageBox.information(self, "Berhasil", "Profil berhasil disimpan dengan aman.")


# ============================================================
# DIALOG BANTUAN
# ============================================================
class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pusat Bantuan BukuKita")
        self.setFixedSize(620, 700)
        self.setStyleSheet("background-color: #F8FAFC; font-family: 'Segoe UI', sans-serif;")
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setGeometry(0, 0, 620, 700)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { border:none; background:transparent; width:8px; margin: 0px; }
            QScrollBar::handle:vertical { background:rgba(148,163,184,0.4); border-radius:4px; min-height:40px; }
            QScrollBar::handle:vertical:hover { background:rgba(100,116,139,0.7); }
        """)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        root = QVBoxLayout(content)
        root.setContentsMargins(36, 36, 36, 36)
        root.setSpacing(18)

        # Header
        lbl_title = QLabel("Panduan Cepat BukuKita")
        lbl_title.setStyleSheet("font-size:24px; font-weight:900; color:#0F172A;")
        lbl_sub = QLabel("Ikuti langkah-langkah simpel ini untuk menguasai aplikasinya.")
        lbl_sub.setStyleSheet("font-size:15px; color:#64748B; margin-bottom: 8px;")
        lbl_sub.setWordWrap(True)
        root.addWidget(lbl_title)
        root.addWidget(lbl_sub)

        steps = [
            ("1", "Login & Daftar Akun",
             "Masuk dengan aman atau buat akun baru dalam hitungan detik. Gunakan fitur 'Ingatkan saya' biar nggak repot ngetik ulang."),

            ("2", "Menjelajah Library",
             "Temukan ribuan buku di Library. Pakai filter kategori atau kolom pencarian pintar untuk mencari buku incaranmu."),

            ("3", "Kelola Koleksi Pribadi",
             "Klik tombol titik tiga pada buku untuk menambahkannya ke rak My Collections. Tandai progres bacamu dengan rapi."),

            ("4", "Catatan & Rating Pribadi",
             "Berikan rating bintang dan tulis anotasi atau pesan-kesan pribadi untuk setiap buku yang kamu baca di form koleksi."),

            ("5", "Pantau Visualisasi Data",
             "Masuk ke Analytics untuk melihat grafik keren seputar kebiasaan membacamu. Lihat seberapa banyak buku yang berhasil kamu tamatkan!"),

            ("6", "Sesuaikan Profilmu",
             "Atur nama, password, dan pasang foto profil terbaikmu lewat menu Detail Profil di pojok kanan atas layar."),
        ]

        for num, title, desc in steps:
            card = QFrame()
            card.setStyleSheet("""
                QFrame { background:#FFFFFF; border-radius:16px; border:1px solid #F1F5F9; }
            """)
            cly = QHBoxLayout(card)
            cly.setContentsMargins(20, 20, 20, 20)
            cly.setSpacing(18)

            badge = QLabel(num)
            badge.setFixedSize(40, 40)
            badge.setAlignment(Qt.AlignCenter)
            badge.setStyleSheet("""
                background-color: #EFF6FF; color: #1D4ED8;
                font-size: 16px; font-weight: 900;
                border-radius: 20px; border: none;
            """)

            text_lay = QVBoxLayout()
            text_lay.setSpacing(4)
            lbl_t = QLabel(title)
            lbl_t.setStyleSheet("font-size:16px; font-weight:800; color:#1E293B; background:transparent;")
            lbl_d = QLabel(desc)
            lbl_d.setStyleSheet("font-size:14px; color:#64748B; line-height:1.5; background:transparent;")
            lbl_d.setWordWrap(True)
            text_lay.addWidget(lbl_t)
            text_lay.addWidget(lbl_d)

            cly.addWidget(badge, alignment=Qt.AlignTop)
            cly.addLayout(text_lay, 1)
            root.addWidget(card)

        # Tombol tutup
        btn_close = QPushButton("Saya Mengerti")
        btn_close.setFixedHeight(48)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton { background-color:#334155; color:#FFFFFF; font-size:15px;
                font-weight:bold; border-radius:12px; border:none; margin-top:16px; }
            QPushButton:hover { background-color:#1E293B; }
        """)
        btn_close.clicked.connect(self.accept)
        root.addWidget(btn_close)
        root.addStretch()
        scroll.setWidget(content)