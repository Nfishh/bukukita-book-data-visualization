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

    def register(self, u, p):
        """
        Mengelola pendaftaran akun baru dengan menyimpan password teks biasa.
        """
        if self.data_manager.cek_username_ada(u):
            print(f"Pendaftaran gagal: Username '{u}' sudah ada.")
            return False
            
        # Simpan password 
        data_user_baru = {
            "username": u,
            "password": p, 
            "role": "user"
        }
        
        return self.data_manager.simpan_user_baru(data_user_baru)

    def set_user_aktif(self, user_id):
        self.user_aktif = user_id

    def get_user_aktif(self):
        return self.user_aktif

    def logout(self):
        self.user_aktif = None
        return True