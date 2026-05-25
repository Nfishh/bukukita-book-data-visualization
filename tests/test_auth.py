# tests/test_auth.py
# Author    : Muhammad Iqbal 251524114
# Deskripsi : Unit test untuk AuthManager (auth/auth_manager.py).
#             Mencakup validasi kekuatan password (panjang, huruf besar/kecil,
#             angka, karakter spesial), alur registrasi (sukses, password
#             lemah, username duplikat), alur login (sukses, password salah,
#             user tidak ada, kredensial kosong), serta logout. Test
#             diisolasi penuh menggunakan folder temporary.


# tests/test_auth.py
# ============================================================
# Unit Tests untuk AuthManager (auth/auth_manager.py)
# ------------------------------------------------------------
# Cakupan:
#   - validasi_password() — semua aturan kekuatan password
#   - register() — sukses, password lemah, username duplikat
#   - login() — sukses, gagal (password salah, user tidak ada)
#   - logout, get_user_aktif, set_user_aktif
#
# CATATAN KEAMANAN:
#   Aplikasi BukuKita SAAT INI menyimpan password sebagai plain text
#   di users.json. Test di sini hanya memverifikasi LOGIKA, bukan
#   keamanan penyimpanan. Untuk produksi, password sebaiknya di-hash
#   pakai bcrypt/argon2 — tapi itu di luar scope testing tugas kampus.
# ============================================================

import os
import sys
import shutil
import tempfile
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data.data_manager import DataManager
from auth.auth_manager import AuthManager


class TestValidasiPassword(unittest.TestCase):
    """Test fungsi statik validasi_password — tidak butuh DataManager."""

    def test_password_valid_strong(self):
        """Password yang memenuhi semua syarat harusnya lolos."""
        ok, pesan = AuthManager.validasi_password("Akira123!")
        self.assertTrue(ok)
        self.assertEqual(pesan, "")

    def test_password_too_short(self):
        ok, pesan = AuthManager.validasi_password("Ab1!")
        self.assertFalse(ok)
        self.assertIn("8 karakter", pesan)

    def test_password_no_uppercase(self):
        ok, pesan = AuthManager.validasi_password("akira123!")
        self.assertFalse(ok)
        self.assertIn("huruf besar", pesan)

    def test_password_no_lowercase(self):
        ok, pesan = AuthManager.validasi_password("AKIRA123!")
        self.assertFalse(ok)
        self.assertIn("huruf kecil", pesan)

    def test_password_no_digit(self):
        ok, pesan = AuthManager.validasi_password("AkiraAja!")
        self.assertFalse(ok)
        self.assertIn("angka", pesan)

    def test_password_no_special_char(self):
        ok, pesan = AuthManager.validasi_password("Akira1234")
        self.assertFalse(ok)
        # Pesan bisa "karakter unik" atau "karakter spesial"
        self.assertTrue(
            "karakter" in pesan.lower(),
            f"Pesan error tidak mention 'karakter': {pesan}"
        )

    def test_password_exactly_8_chars_valid(self):
        """Boundary: tepat 8 karakter harus diterima."""
        ok, _ = AuthManager.validasi_password("Akira1!a")
        self.assertTrue(ok)

    def test_password_7_chars_rejected(self):
        """Boundary: 7 karakter harus ditolak."""
        ok, _ = AuthManager.validasi_password("Akira1!")
        self.assertFalse(ok)


class TestAuthRegister(unittest.TestCase):
    """Test alur registrasi pengguna baru."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.tmp_dir)
        self.dm = DataManager()
        self.auth = AuthManager(self.dm)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_register_success(self):
        ok, pesan = self.auth.register("akira", "Akira123!", nama_lengkap="Akira Test")
        self.assertTrue(ok)
        self.assertEqual(pesan, "")

    def test_register_persists_user(self):
        """Setelah register sukses, user harus benar-benar tersimpan."""
        self.auth.register("akira", "Akira123!", nama_lengkap="Akira Test")
        self.assertTrue(self.dm.cek_username_ada("akira"))

    def test_register_saves_nama_lengkap(self):
        self.auth.register("akira", "Akira123!", nama_lengkap="Akira Test")
        data = self.dm.get_user_data("akira")
        self.assertEqual(data["nama_lengkap"], "Akira Test")

    def test_register_weak_password_fails(self):
        ok, pesan = self.auth.register("akira", "lemah", nama_lengkap="X")
        self.assertFalse(ok)
        self.assertNotEqual(pesan, "")

    def test_register_weak_password_does_not_persist(self):
        """Password lemah → user TIDAK boleh tersimpan."""
        self.auth.register("akira", "lemah", nama_lengkap="X")
        self.assertFalse(self.dm.cek_username_ada("akira"))

    def test_register_duplicate_username_fails(self):
        self.auth.register("akira", "Akira123!")
        ok, pesan = self.auth.register("akira", "Akira123!")
        self.assertFalse(ok)
        self.assertIn("sudah", pesan.lower())

    def test_register_default_role_is_user(self):
        self.auth.register("akira", "Akira123!")
        data = self.dm.get_user_data("akira")
        self.assertEqual(data["role"], "user")


class TestAuthLogin(unittest.TestCase):
    """Test alur login."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.tmp_dir)
        self.dm = DataManager()
        self.auth = AuthManager(self.dm)
        # Seed satu user buat dipakai testing
        self.auth.register("akira", "Akira123!", nama_lengkap="Akira")

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_login_success(self):
        self.assertTrue(self.auth.login("akira", "Akira123!"))

    def test_login_sets_user_aktif(self):
        self.auth.login("akira", "Akira123!")
        self.assertEqual(self.auth.get_user_aktif(), "akira")

    def test_login_wrong_password(self):
        self.assertFalse(self.auth.login("akira", "passwordSalah"))

    def test_login_wrong_password_user_aktif_stays_none(self):
        self.auth.login("akira", "passwordSalah")
        self.assertIsNone(self.auth.get_user_aktif())

    def test_login_nonexistent_user(self):
        self.assertFalse(self.auth.login("ghost", "apapun"))

    def test_login_empty_credentials(self):
        """Empty string nggak boleh nge-bypass login."""
        self.assertFalse(self.auth.login("", ""))

    def test_logout_clears_user_aktif(self):
        self.auth.login("akira", "Akira123!")
        self.auth.logout()
        self.assertIsNone(self.auth.get_user_aktif())


if __name__ == "__main__":
    unittest.main(verbosity=2)