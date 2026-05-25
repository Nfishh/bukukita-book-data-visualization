# tests/test_data_manager.py
# Author    : Muhammad Iqbal 251524114
# Deskripsi : Unit test untuk DataManager (data/data_manager.py).
#             Menguji operasi CRUD users dan tracker, inisialisasi folder/file
#             otomatis, serta ketahanan terhadap kondisi batas seperti file
#             JSON kosong, korup, atau tidak ada. Setiap test berjalan di
#             folder temporary yang dihapus otomatis setelah selesai,
#             sehingga data asli proyek tidak akan tersentuh.


# tests/test_data_manager.py
# ============================================================
# Unit Tests untuk DataManager (data/data_manager.py)
# ------------------------------------------------------------
# Cakupan:
#   - CRUD User (cek_username_ada, simpan_user_baru, cek_kredensial,
#                get_user_data, update_user_data)
#   - CRUD Tracker (simpan_tracker, get_semua_tracker, get_tracker_user,
#                   cek_duplikasi_tracker, update_tracker, hapus_tracker)
#   - Edge cases: file JSON kosong, file JSON korup, file belum ada
#
# Isolasi:
#   Setiap test pakai folder temporary (tempfile.mkdtemp), jadi file
#   data/users.json dan data/tracker.json asli TIDAK akan kesentuh.
# ============================================================

import os
import sys
import json
import shutil
import tempfile
import unittest

# Tambahkan project root ke sys.path supaya bisa import modul aplikasi
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data.data_manager import DataManager


class TestDataManagerSetup(unittest.TestCase):
    """Test isolasi: DataManager harus bikin file/folder yang dibutuhkan."""

    def setUp(self):
        # Bikin temp dir + pindah cwd ke situ, supaya DataManager()
        # bikin folder "data/" dan "output/json/" di temp dir, bukan di proyek asli.
        self.tmp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.tmp_dir)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_init_creates_data_folder(self):
        """DataManager() harus bikin folder data/ kalau belum ada."""
        DataManager()
        self.assertTrue(os.path.exists("data"), "Folder data/ harusnya dibuat otomatis")

    def test_init_creates_empty_users_json(self):
        """File users.json harus dibuat dengan isi list kosong."""
        dm = DataManager()
        self.assertTrue(os.path.exists(dm.path_users))
        with open(dm.path_users, 'r', encoding='utf-8') as f:
            self.assertEqual(json.load(f), [])

    def test_init_creates_empty_tracker_json(self):
        """File tracker.json harus dibuat dengan isi list kosong."""
        dm = DataManager()
        self.assertTrue(os.path.exists(dm.path_tracker))
        with open(dm.path_tracker, 'r', encoding='utf-8') as f:
            self.assertEqual(json.load(f), [])


class TestDataManagerUserCRUD(unittest.TestCase):
    """CRUD operations untuk users."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.tmp_dir)
        self.dm = DataManager()

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_simpan_user_baru_returns_true(self):
        ok = self.dm.simpan_user_baru({
            "username": "akira", "password": "Test1234!", "role": "user"
        })
        self.assertTrue(ok)

    def test_simpan_user_baru_persisted(self):
        """Setelah save, data harus benar-benar ada di file."""
        self.dm.simpan_user_baru({
            "username": "akira", "password": "Test1234!", "role": "user"
        })
        with open(self.dm.path_users, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["username"], "akira")

    def test_cek_username_ada_returns_true_when_exists(self):
        self.dm.simpan_user_baru({"username": "akira", "password": "x", "role": "user"})
        self.assertTrue(self.dm.cek_username_ada("akira"))

    def test_cek_username_ada_returns_false_when_not_exists(self):
        self.assertFalse(self.dm.cek_username_ada("ghost_user"))

    def test_cek_kredensial_correct(self):
        self.dm.simpan_user_baru({"username": "akira", "password": "Test1234!", "role": "user"})
        user = self.dm.cek_kredensial("akira", "Test1234!")
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "akira")

    def test_cek_kredensial_wrong_password(self):
        self.dm.simpan_user_baru({"username": "akira", "password": "Test1234!", "role": "user"})
        self.assertIsNone(self.dm.cek_kredensial("akira", "salah"))

    def test_cek_kredensial_nonexistent_user(self):
        self.assertIsNone(self.dm.cek_kredensial("ghost", "apapun"))

    def test_get_user_data_returns_full_dict(self):
        self.dm.simpan_user_baru({
            "username": "akira", "password": "x", "role": "user", "nama_lengkap": "Akira X"
        })
        data = self.dm.get_user_data("akira")
        self.assertEqual(data["nama_lengkap"], "Akira X")

    def test_get_user_data_returns_none_when_missing(self):
        self.assertIsNone(self.dm.get_user_data("ghost"))

    def test_update_user_data_modifies_correctly(self):
        self.dm.simpan_user_baru({"username": "akira", "password": "x", "role": "user"})
        ok = self.dm.update_user_data("akira", {"nama_lengkap": "Akira Baru"})
        self.assertTrue(ok)
        data = self.dm.get_user_data("akira")
        self.assertEqual(data["nama_lengkap"], "Akira Baru")

    def test_update_user_data_preserves_other_fields(self):
        """Update sebagian field nggak boleh ngehapus field lain."""
        self.dm.simpan_user_baru({"username": "akira", "password": "Pass1234!", "role": "user"})
        self.dm.update_user_data("akira", {"nama_lengkap": "Akira Baru"})
        data = self.dm.get_user_data("akira")
        self.assertEqual(data["password"], "Pass1234!")
        self.assertEqual(data["role"], "user")


class TestDataManagerTrackerCRUD(unittest.TestCase):
    """CRUD operations untuk tracker buku.
    Memakai skema BARU: tgl_mulai + tgl_selesai (sesuai keputusan).
    """

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.tmp_dir)
        self.dm = DataManager()

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _make_tracker(self, **overrides):
        """Helper bikin tracker default dengan skema baru."""
        base = {
            "id_tracker": "TEST0001",
            "user_id": "akira",
            "book_id": "GR_1572_001",
            "status_baca": "Sedang Membaca",
            "rating_personal": 0,
            "catatan": "",
            "tgl_mulai": "2026-05-16",
            "tgl_selesai": "",
        }
        base.update(overrides)
        return base

    def test_simpan_tracker_basic(self):
        ok = self.dm.simpan_tracker(self._make_tracker())
        self.assertTrue(ok)
        self.assertEqual(len(self.dm.get_semua_tracker()), 1)

    def test_get_semua_tracker_empty_initially(self):
        self.assertEqual(self.dm.get_semua_tracker(), [])

    def test_get_tracker_user_filters_by_user_id(self):
        self.dm.simpan_tracker(self._make_tracker(id_tracker="A1", user_id="akira"))
        self.dm.simpan_tracker(self._make_tracker(id_tracker="A2", user_id="akira"))
        self.dm.simpan_tracker(self._make_tracker(id_tracker="B1", user_id="lain"))

        hasil = self.dm.get_tracker_user("akira")
        self.assertEqual(len(hasil), 2)
        self.assertTrue(all(t["user_id"] == "akira" for t in hasil))

    def test_get_tracker_user_returns_empty_for_no_match(self):
        self.dm.simpan_tracker(self._make_tracker(user_id="akira"))
        self.assertEqual(self.dm.get_tracker_user("ghost"), [])

    def test_cek_duplikasi_tracker_true_when_exists(self):
        self.dm.simpan_tracker(self._make_tracker(user_id="akira", book_id="GR_1572_001"))
        self.assertTrue(self.dm.cek_duplikasi_tracker("akira", "GR_1572_001"))

    def test_cek_duplikasi_tracker_false_when_different_book(self):
        self.dm.simpan_tracker(self._make_tracker(user_id="akira", book_id="GR_1572_001"))
        self.assertFalse(self.dm.cek_duplikasi_tracker("akira", "GR_1572_999"))

    def test_update_tracker_modifies_status(self):
        self.dm.simpan_tracker(self._make_tracker(id_tracker="X1", status_baca="Belum Dibaca"))
        ok = self.dm.update_tracker("X1", {"status_baca": "Selesai Dibaca"})
        self.assertTrue(ok)

        hasil = self.dm.get_semua_tracker()
        self.assertEqual(hasil[0]["status_baca"], "Selesai Dibaca")

    def test_update_tracker_modifies_rating(self):
        self.dm.simpan_tracker(self._make_tracker(id_tracker="X1", rating_personal=0))
        self.dm.update_tracker("X1", {"rating_personal": 4.5})
        hasil = self.dm.get_semua_tracker()
        self.assertEqual(hasil[0]["rating_personal"], 4.5)

    def test_hapus_tracker_removes_entry(self):
        self.dm.simpan_tracker(self._make_tracker(id_tracker="A1"))
        self.dm.simpan_tracker(self._make_tracker(id_tracker="A2"))

        ok = self.dm.hapus_tracker("A1")
        self.assertTrue(ok)

        hasil = self.dm.get_semua_tracker()
        self.assertEqual(len(hasil), 1)
        self.assertEqual(hasil[0]["id_tracker"], "A2")

    def test_hapus_tracker_nonexistent_does_not_error(self):
        """Hapus tracker yg gak ada nggak boleh ngecrash, cuma noop."""
        self.dm.simpan_tracker(self._make_tracker(id_tracker="A1"))
        ok = self.dm.hapus_tracker("GHOST_ID")
        # Tetep return True karena write berhasil; data nggak berubah
        self.assertTrue(ok)
        self.assertEqual(len(self.dm.get_semua_tracker()), 1)


class TestDataManagerEdgeCases(unittest.TestCase):
    """Boundary conditions: JSON kosong, JSON korup, file hilang."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.tmp_dir)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_read_corrupted_json_returns_empty_list(self):
        """JSON korup nggak boleh ngecrash aplikasi — harus return []."""
        dm = DataManager()
        # Tulis isi yang BUKAN JSON valid
        with open(dm.path_users, 'w', encoding='utf-8') as f:
            f.write("{ ini bukan JSON valid ][[}")

        hasil = dm._read_json(dm.path_users)
        self.assertEqual(hasil, [])

    def test_read_empty_file_returns_empty_list(self):
        """File kosong total juga nggak boleh ngecrash."""
        dm = DataManager()
        with open(dm.path_users, 'w', encoding='utf-8') as f:
            f.write("")

        hasil = dm._read_json(dm.path_users)
        self.assertEqual(hasil, [])

    def test_read_nonexistent_file_returns_empty_list(self):
        dm = DataManager()
        hasil = dm._read_json("/path/yang/gak/ada/file.json")
        self.assertEqual(hasil, [])

    def test_simpan_user_baru_to_corrupted_file_still_works(self):
        """Kalau users.json korup, simpan_user_baru harusnya overwrite,
        bukan crash. (Karena _read_json balikin [] saat error.)"""
        dm = DataManager()
        with open(dm.path_users, 'w', encoding='utf-8') as f:
            f.write("CORRUPTED DATA")

        ok = dm.simpan_user_baru({"username": "akira", "password": "x", "role": "user"})
        self.assertTrue(ok)
        self.assertTrue(dm.cek_username_ada("akira"))


if __name__ == "__main__":
    unittest.main(verbosity=2)