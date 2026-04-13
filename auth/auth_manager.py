# auth_manager.py
# Developer: Muhammmad Ziddan (251524117)
# Deskripsi: Mengelola autentikasi pengguna dengan enkripsi SHA-256 untuk keamanan data.

import hashlib

class AuthManager:
    def __init__(self, data_manager):
        """
        Menginisialisasi AuthManager dengan dependensi DataManager.
        """
        self.data_manager = data_manager
        self.user_aktif = None

    def _hash_password(self, password):
        """
        Fungsi privat untuk mengubah teks password menjadi kode unik (hash).
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, u, p):
        """
        Memvalidasi kredensial pengguna dengan membandingkan hash password[cite: 1].
        """
        # Ubah input password menjadi hash sebelum dicek ke DataManager
        hashed_password = self._hash_password(p)
        
        user = self.data_manager.cek_kredensial(u, hashed_password) [cite: 1]
        
        if user:
            self.user_aktif = user.get('id', u) [cite: 1]
            return True
        return False

    def register(self, u, p):
        """
        Mengelola pendaftaran akun baru dengan menyimpan password yang sudah di-hash[cite: 1].
        """
        if self.data_manager.cek_username_ada(u): [cite: 1]
            print(f"Pendaftaran gagal: Username '{u}' sudah ada.")
            return False
            
        # Simpan password dalam bentuk hash, bukan teks asli
        data_user_baru = {
            "username": u,
            "password": self._hash_password(p),
            "role": "user"
        }
        
        return self.data_manager.simpan_user_baru(data_user_baru) [cite: 1]

    def set_user_aktif(self, user_id):
        """Menetapkan ID pengguna yang sedang aktif dalam sesi[cite: 1]."""
        self.user_aktif = user_id [cite: 1]

    def get_user_aktif(self):
        """Mengambil ID pengguna yang sedang aktif[cite: 1]."""
        return self.user_aktif [cite: 1]

    def logout(self):
        """Menghapus data sesi untuk mengakhiri penggunaan aplikasi[cite: 1]."""
        self.user_aktif = None [cite: 1]
        return True