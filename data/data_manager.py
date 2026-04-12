import json
import os

class DataManager:
    def __init__(self):
        """
        Menginisialisasi direktori data dan berkas JSON.
        Fokus pada folder 'data' untuk aktivitas dan 'output/json' untuk master buku.
        """
        self.data_dir = "data"
        self.output_dir = os.path.join("output", "json")
        
        # Definisi Path sesuai struktur repositori 
        self.path_buku = os.path.join(self.output_dir, "buku.json")
        self.path_users = os.path.join(self.data_dir, "users.json")
        self.path_tracker = os.path.join(self.data_dir, "tracker.json")
        
        self._init_files()

    def _init_files(self):
        """Memastikan direktori 'data' ada dan file JSON inisial tersedia."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        # Inisialisasi file users dan tracker jika belum ada
        for path in [self.path_users, self.path_tracker]:
            if not os.path.exists(path):
                self._write_json(path, [])

    # --- Utilitas Privat (Metode Internal) ---
    def _read_json(self, path):
        """Membaca berkas JSON dari path yang ditentukan."""
        try:
            if not os.path.exists(path):
                return []
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _write_json(self, path, data):
        """Menulis data ke berkas JSON di path yang ditentukan."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    # --- Modul Master Buku (Data dari Scraper) ---
    def get_semua_buku(self):
        """Mengambil seluruh data master buku dari output/json/buku.json."""
        return self._read_json(self.path_buku)

    def get_detail_buku(self, book_id):
        """Mencari data detail satu buku berdasarkan ID."""
        semua_buku = self.get_semua_buku()
        return next((b for b in semua_buku if b.get('id_buku') == book_id), None)

    # --- Modul Autentikasi (Untuk AuthManager) ---
    def cek_username_ada(self, username):
        """Validasi username untuk mencegah duplikasi pendaftaran."""
        users = self._read_json(self.path_users)
        return any(u.get('username') == username for u in users)

    def simpan_user_baru(self, data_user):
        """Menyimpan data akun baru ke users.json."""
        users = self._read_json(self.path_users)
        users.append(data_user)
        return self._write_json(self.path_users, users)

    def cek_kredensial(self, username, password):
        """Validasi login pengguna."""
        users = self._read_json(self.path_users)
        return next((u for u in users if u.get('username') == username and u.get('password') == password), None)

    # --- Modul Tracker (Untuk BookManager & DataViz) ---
    def get_tracker_user(self, user_id):
        """Mengambil riwayat koleksi milik satu pengguna."""
        tracker = self._read_json(self.path_tracker)
        return [t for t in tracker if t.get('user_id') == user_id]

    def cek_duplikasi_tracker(self, user_id, book_id):
        """Memeriksa apakah buku sudah ada di koleksi pengguna."""
        tracker = self._read_json(self.path_tracker)
        return any(t.get('user_id') == user_id and t.get('book_id') == book_id for t in tracker)

    def simpan_tracker(self, data_tracker):
        """Menyimpan entri koleksi baru ke tracker.json."""
        all_tracker = self._read_json(self.path_tracker)
        all_tracker.append(data_tracker)
        return self._write_json(self.path_tracker, all_tracker)

    def update_tracker(self, tracker_id, data_baru):
        """Memperbarui status atau rating pada koleksi yang ada."""
        all_tracker = self._read_json(self.path_tracker)
        for t in all_tracker:
            if t.get('id_tracker') == tracker_id:
                t.update(data_baru)
                break
        return self._write_json(self.path_tracker, all_tracker)

    def hapus_tracker(self, tracker_id):
        """Menghapus entri spesifik dari riwayat bacaan."""
        all_tracker = self._read_json(self.path_tracker)
        filtered_tracker = [t for t in all_tracker if t.get('id_tracker') != tracker_id]
        return self._write_json(self.path_tracker, filtered_tracker)