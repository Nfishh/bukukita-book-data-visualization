# data/data_manager.py
# Developer : Fidella Rafida Ariani 251524100
# Deskripsi : Lapisan data access (data layer) BukuKita. Mengelola semua
#             operasi baca-tulis file JSON untuk tiga entitas utama:
#             master buku (output/json/buku.json), data pengguna
#             (data/users.json), dan tracker bacaan personal
#             (data/tracker.json). Menyediakan API CRUD lengkap serta
#             penanganan error untuk file korup, kosong, atau belum ada
#             agar aplikasi tidak crash. Inisialisasi otomatis membuat
#             folder dan file kosong jika belum tersedia.


# data/data_manager.py
# Developer : Fidella Rafida Ariani 251524100
# Deskripsi : Lapisan data access (data layer) BukuKita. Mengelola semua
#             operasi baca-tulis file JSON untuk tiga entitas utama:
#             master buku (output/json/buku.json), data pengguna
#             (data/users.json), dan tracker bacaan personal
#             (data/tracker.json). Menyediakan API CRUD lengkap serta
#             penanganan error untuk file korup, kosong, atau belum ada
#             agar aplikasi tidak crash. Inisialisasi otomatis membuat
#             folder dan file kosong jika belum tersedia.
#
#             [UPDATE] Mendukung PyInstaller: buku.json (read-only) dibaca
#             dari folder aset, sedangkan users.json & tracker.json
#             (read-write) disimpan di folder persisten di samping .exe
#             sehingga registrasi user & koleksi tidak hilang antar sesi.


import json
import os

class DataManager:
    def __init__(self):
        # ------------------------------------------------------------
        # Penentuan lokasi file.
        #
        # WRITABLE_ROOT  : folder untuk data yang berubah (users, tracker).
        #                  Diisi oleh main.py lewat environment variable.
        #                  Fallback ke "." (cwd) jika dijalankan tanpa main.py
        #                  (mis. saat unit test) -- perilaku lama tetap aman.
        # ASSET_ROOT     : folder kerja saat ini (cwd). main.py sudah
        #                  meng-chdir ke folder aset, jadi buku.json tetap
        #                  bisa diakses lewat path relatif seperti semula.
        # ------------------------------------------------------------
        writable_root = os.environ.get("BUKUKITA_WRITABLE_ROOT", "")

        self.data_dir   = os.path.join(writable_root, "data") if writable_root else "data"
        self.output_dir = os.path.join("output", "json")

        self.path_buku    = os.path.join(self.output_dir, "buku.json")
        self.path_users   = os.path.join(self.data_dir, "users.json")
        self.path_tracker = os.path.join(self.data_dir, "tracker.json")
        self._init_files()

    def _init_files(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        for path in [self.path_users, self.path_tracker]:
            if not os.path.exists(path):
                self._write_json(path, [])

    def _read_json(self, path):
        try:
            if not os.path.exists(path):
                return []
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _write_json(self, path, data):
        try:
            # Pastikan folder tujuan ada sebelum menulis
            folder = os.path.dirname(path)
            if folder and not os.path.exists(folder):
                os.makedirs(folder)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    # --- Modul Master Buku ---
    def get_semua_buku(self):
        return self._read_json(self.path_buku)

    def get_detail_buku(self, book_id):
        semua_buku = self.get_semua_buku()
        return next((b for b in semua_buku if b.get('id_buku') == book_id), None)

    def update_rating_bukukita(self, book_id: str, rating_baru: float, jumlah_voter: int):
        """
        Simpan rating akumulasi BukuKita ke buku.json.
        Field yang ditulis: rating_bukukita, total_voter_bukukita.
        """
        semua_buku = self._read_json(self.path_buku)
        for buku in semua_buku:
            if buku.get('id_buku') == book_id:
                buku['rating_bukukita']       = rating_baru
                buku['total_voter_bukukita']  = jumlah_voter
                break
        return self._write_json(self.path_buku, semua_buku)

    # --- Modul Autentikasi ---
    def cek_username_ada(self, username):
        users = self._read_json(self.path_users)
        return any(u.get('username') == username for u in users)

    def simpan_user_baru(self, data_user):
        users = self._read_json(self.path_users)
        users.append(data_user)
        return self._write_json(self.path_users, users)

    def cek_kredensial(self, username, password):
        users = self._read_json(self.path_users)
        return next(
            (u for u in users
             if u.get('username') == username and u.get('password') == password),
            None
        )

    def get_user_data(self, username):
        users = self._read_json(self.path_users)
        return next((u for u in users if u.get('username') == username), None)

    def update_user_data(self, username, data_baru: dict):
        users = self._read_json(self.path_users)
        for u in users:
            if u.get('username') == username:
                u.update(data_baru)
                break
        return self._write_json(self.path_users, users)

    # --- Modul Tracker ---
    def get_tracker_user(self, user_id):
        tracker = self._read_json(self.path_tracker)
        return [t for t in tracker if t.get('user_id') == user_id]

    def get_semua_tracker(self):
        return self._read_json(self.path_tracker)

    def cek_duplikasi_tracker(self, user_id, book_id):
        tracker = self._read_json(self.path_tracker)
        return any(
            t.get('user_id') == user_id and t.get('book_id') == book_id
            for t in tracker
        )

    def simpan_tracker(self, data_tracker):
        all_tracker = self._read_json(self.path_tracker)
        all_tracker.append(data_tracker)
        return self._write_json(self.path_tracker, all_tracker)

    def update_tracker(self, tracker_id, data_baru):
        all_tracker = self._read_json(self.path_tracker)
        for t in all_tracker:
            if t.get('id_tracker') == tracker_id:
                t.update(data_baru)
                break
        return self._write_json(self.path_tracker, all_tracker)

    def hapus_tracker(self, tracker_id):
        all_tracker = self._read_json(self.path_tracker)
        filtered = [t for t in all_tracker if t.get('id_tracker') != tracker_id]
        return self._write_json(self.path_tracker, filtered)