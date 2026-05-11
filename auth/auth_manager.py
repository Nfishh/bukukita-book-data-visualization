# auth_manager.py
# Developer: Muhammad Ziddan 
# Deskripsi: Mengelola autentikasi pengguna BukuKita 

class AuthManager:
    def __init__(self, data_manager):
        """
        Menginisialisasi AuthManager dengan dependensi DataManager.
        """
        self.data_manager = data_manager
        self.user_aktif = None

    def login(self, u, p):
        """
        Memvalidasi kredensial pengguna secara langsung.
        """
        # Langsung mengirim u dan p apa adanya ke  (DataManager)
        user = self.data_manager.cek_kredensial(u, p)
        
        if user:
            self.user_aktif = user.get('id', u)
            return True
        return False


    @staticmethod
    def validasi_password(p):
        """
        Cek kekuatan password. Return (True, "") jika valid,
        atau (False, pesan_error) jika tidak memenuhi syarat.
        """
        import re
        if len(p) < 8:
            return False, "Password minimal 8 karakter."
        if not re.search(r"[A-Z]", p):
            return False, "Password harus mengandung minimal 1 huruf besar."
        if not re.search(r"[a-z]", p):
            return False, "Password harus mengandung minimal 1 huruf kecil."
        if not re.search(r"[0-9]", p):
            return False, "Password harus mengandung minimal 1 angka."
        if not re.search(r"[^A-Za-z0-9]", p):
            return False, "Password harus mengandung minimal 1 karakter unik (!@#$% dll)."
        return True, ""

    def register(self, u, p, nama_lengkap=""):
        """
        Mendaftarkan akun baru. nama_lengkap disimpan sekalian dalam satu operasi.
        """
        valid, pesan = self.validasi_password(p)
        if not valid:
            print(f"Pendaftaran gagal: {pesan}")
            return False, pesan

        if self.data_manager.cek_username_ada(u):
            print(f"Pendaftaran gagal: Username '{u}' sudah ada.")
            return False, "Username sudah digunakan."

        data_user_baru = {
            "username"     : u,
            "password"     : p,
            "role"         : "user",
            "nama_lengkap" : nama_lengkap,
        }
        ok = self.data_manager.simpan_user_baru(data_user_baru)
        return (True, "") if ok else (False, "Gagal menyimpan data.")

    def set_user_aktif(self, user_id):
        self.user_aktif = user_id

    def get_user_aktif(self):
        return self.user_aktif

    def logout(self):
        self.user_aktif = None
        return True