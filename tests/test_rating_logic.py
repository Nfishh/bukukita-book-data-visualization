# tests/test_rating_logic.py
# Author    : Muhammad Iqbal 251524114
# Deskripsi : Unit test untuk RatingSystem (book/rating_system.py).
#             Menguji perhitungan rating global (rata-rata, jumlah voter,
#             pembulatan 2 desimal, eksklusi rating 0), penyimpanan rating
#             personal (validasi range 1.0-5.0, normalisasi koma ke titik,
#             create vs update tracker), dan aturan bisnis cek_boleh_rating
#             yang hanya mengizinkan rating untuk status "Selesai Dibaca".
#             Termasuk satu regression test untuk bug substring matching
#             yang ditemukan pada implementasi awal.


# tests/test_rating_logic.py
# ============================================================
# Unit Tests untuk RatingSystem (book/rating_system.py)
# ------------------------------------------------------------
# Cakupan:
#   - hitung_rating_global() — rata-rata + jumlah voter
#   - simpan_rating_personal() — validasi range, normalisasi koma→titik
#   - cek_boleh_rating() — hanya boleh rating jika "Selesai Dibaca"
#
# PERHATIAN — BUG YANG DI-FLAG:
#   Method cek_boleh_rating() saat ini pakai:
#       return "Selesai" in tracker.get('status_baca', '')
#
#   Ini RAWAN: kalau nanti ada status baru yang mengandung kata
#   "Selesai" (misal "Belum Selesai" atau "Selesai Tapi Drop"),
#   bakal salah deteksi. Test `test_cek_boleh_rating_substring_bug`
#   di bawah SENGAJA bakal GAGAL untuk nge-flag bug ini.
#
#   FIX yang disarankan di rating_system.py:
#       return tracker.get('status_baca') == "Selesai Dibaca"
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
from book.rating_system import RatingSystem


class RatingSystemTestBase(unittest.TestCase):
    """Base class — bikin DataManager isolated + RatingSystem siap dipakai."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.tmp_dir)
        self.dm = DataManager()
        self.rs = RatingSystem(self.dm)
        # Bikin buku.json minimal di output/json supaya update_rating_bukukita gak crash
        os.makedirs(self.dm.output_dir, exist_ok=True)
        with open(self.dm.path_buku, 'w', encoding='utf-8') as f:
            import json
            json.dump([
                {"id_buku": "GR_1572_001", "judul": "Buku A"},
                {"id_buku": "GR_1572_002", "judul": "Buku B"},
            ], f)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _seed_tracker(self, user_id, book_id, status, rating, id_tracker=None):
        """Helper: bikin tracker entry langsung lewat DataManager."""
        import uuid
        self.dm.simpan_tracker({
            "id_tracker": id_tracker or str(uuid.uuid4())[:8].upper(),
            "user_id": user_id,
            "book_id": book_id,
            "status_baca": status,
            "rating_personal": rating,
            "catatan": "",
            "tgl_mulai": "2026-05-16",
            "tgl_selesai": "",
        })


class TestHitungRatingGlobal(RatingSystemTestBase):
    """Test agregasi rating dari semua user."""

    def test_no_ratings_returns_zero(self):
        """Kalau belum ada user yang rating, return (0.0, 0)."""
        avg, total = self.rs.hitung_rating_global("GR_1572_001")
        self.assertEqual(avg, 0.0)
        self.assertEqual(total, 0)

    def test_single_rating(self):
        self._seed_tracker("akira", "GR_1572_001", "Selesai Dibaca", 4.0)
        avg, total = self.rs.hitung_rating_global("GR_1572_001")
        self.assertEqual(avg, 4.0)
        self.assertEqual(total, 1)

    def test_multiple_ratings_averaged(self):
        self._seed_tracker("akira",  "GR_1572_001", "Selesai Dibaca", 5.0)
        self._seed_tracker("bagas",  "GR_1572_001", "Selesai Dibaca", 3.0)
        self._seed_tracker("citra",  "GR_1572_001", "Selesai Dibaca", 4.0)
        avg, total = self.rs.hitung_rating_global("GR_1572_001")
        self.assertEqual(avg, 4.0)  # (5+3+4)/3
        self.assertEqual(total, 3)

    def test_rating_zero_excluded(self):
        """Rating 0 (belum rating) HARUS di-exclude dari rata-rata."""
        self._seed_tracker("akira", "GR_1572_001", "Selesai Dibaca", 4.0)
        self._seed_tracker("bagas", "GR_1572_001", "Belum Dibaca",   0)
        avg, total = self.rs.hitung_rating_global("GR_1572_001")
        self.assertEqual(avg, 4.0)
        self.assertEqual(total, 1)  # bagas nggak dihitung

    def test_different_book_isolated(self):
        """Rating untuk buku A nggak boleh keitung di buku B."""
        self._seed_tracker("akira", "GR_1572_001", "Selesai Dibaca", 5.0)
        self._seed_tracker("akira", "GR_1572_002", "Selesai Dibaca", 1.0)
        avg_a, _ = self.rs.hitung_rating_global("GR_1572_001")
        avg_b, _ = self.rs.hitung_rating_global("GR_1572_002")
        self.assertEqual(avg_a, 5.0)
        self.assertEqual(avg_b, 1.0)

    def test_decimal_rating_rounded_to_2_places(self):
        """Rata-rata harus dibulatkan 2 desimal."""
        self._seed_tracker("a", "GR_1572_001", "Selesai Dibaca", 4.0)
        self._seed_tracker("b", "GR_1572_001", "Selesai Dibaca", 4.0)
        self._seed_tracker("c", "GR_1572_001", "Selesai Dibaca", 5.0)
        avg, _ = self.rs.hitung_rating_global("GR_1572_001")
        # (4+4+5)/3 = 4.333... → 4.33
        self.assertEqual(avg, 4.33)


class TestSimpanRatingPersonal(RatingSystemTestBase):
    """Test penyimpanan rating personal user."""

    def test_simpan_rating_valid(self):
        ok = self.rs.simpan_rating_personal("akira", "GR_1572_001", 4.5)
        self.assertTrue(ok)

    def test_simpan_rating_below_range_rejected(self):
        """Rating < 1.0 harus ditolak."""
        ok = self.rs.simpan_rating_personal("akira", "GR_1572_001", 0.5)
        self.assertFalse(ok)

    def test_simpan_rating_above_range_rejected(self):
        """Rating > 5.0 harus ditolak."""
        ok = self.rs.simpan_rating_personal("akira", "GR_1572_001", 5.5)
        self.assertFalse(ok)

    def test_simpan_rating_boundary_1_accepted(self):
        """Boundary minimum: tepat 1.0 harus diterima."""
        ok = self.rs.simpan_rating_personal("akira", "GR_1572_001", 1.0)
        self.assertTrue(ok)

    def test_simpan_rating_boundary_5_accepted(self):
        """Boundary maximum: tepat 5.0 harus diterima."""
        ok = self.rs.simpan_rating_personal("akira", "GR_1572_001", 5.0)
        self.assertTrue(ok)

    def test_simpan_rating_with_comma_normalized(self):
        """User input '4,5' (format Indonesia) harus dikonversi ke 4.5."""
        ok = self.rs.simpan_rating_personal("akira", "GR_1572_001", "4,5")
        self.assertTrue(ok)
        # Verifikasi tersimpan sebagai float, bukan string
        tracker = self.dm.get_semua_tracker()[0]
        self.assertEqual(tracker["rating_personal"], 4.5)

    def test_simpan_rating_invalid_string_rejected(self):
        """String non-numeric harus ditolak, nggak boleh crash."""
        ok = self.rs.simpan_rating_personal("akira", "GR_1572_001", "abc")
        self.assertFalse(ok)

    def test_simpan_rating_creates_new_tracker_if_absent(self):
        """Kalau user belum punya tracker untuk buku itu, dibuat baru."""
        self.assertEqual(len(self.dm.get_semua_tracker()), 0)
        self.rs.simpan_rating_personal("akira", "GR_1572_001", 4.0)
        self.assertEqual(len(self.dm.get_semua_tracker()), 1)

    def test_simpan_rating_updates_existing_tracker(self):
        """Kalau tracker udah ada, di-update — bukan duplikat."""
        self._seed_tracker("akira", "GR_1572_001", "Selesai Dibaca", 3.0, id_tracker="EXIST")
        self.rs.simpan_rating_personal("akira", "GR_1572_001", 5.0)
        trackers = self.dm.get_semua_tracker()
        self.assertEqual(len(trackers), 1)  # Tetap 1, bukan 2
        self.assertEqual(trackers[0]["rating_personal"], 5.0)

    def test_simpan_rating_updates_buku_json_aggregate(self):
        """Setelah simpan rating, buku.json harus ke-update juga."""
        self.rs.simpan_rating_personal("akira", "GR_1572_001", 4.0)
        buku = self.dm.get_detail_buku("GR_1572_001")
        self.assertEqual(buku["rating_bukukita"], 4.0)
        self.assertEqual(buku["total_voter_bukukita"], 1)


class TestCekBolehRating(RatingSystemTestBase):
    """Test gate apakah user boleh memberi rating.
    Aturan bisnis: hanya boleh rating jika status_baca = 'Selesai Dibaca'.
    """

    def test_boleh_rating_jika_selesai(self):
        self._seed_tracker("akira", "GR_1572_001", "Selesai Dibaca", 0)
        self.assertTrue(self.rs.cek_boleh_rating("akira", "GR_1572_001"))

    def test_tidak_boleh_rating_jika_belum_dibaca(self):
        self._seed_tracker("akira", "GR_1572_001", "Belum Dibaca", 0)
        self.assertFalse(self.rs.cek_boleh_rating("akira", "GR_1572_001"))

    def test_tidak_boleh_rating_jika_sedang_membaca(self):
        self._seed_tracker("akira", "GR_1572_001", "Sedang Membaca", 0)
        self.assertFalse(self.rs.cek_boleh_rating("akira", "GR_1572_001"))

    def test_tidak_boleh_rating_jika_drop(self):
        """Buku yang di-drop nggak boleh dirating
        (sesuai aturan bisnis: hanya 'Selesai Dibaca' yang boleh)."""
        self._seed_tracker("akira", "GR_1572_001", "Drop", 0)
        self.assertFalse(self.rs.cek_boleh_rating("akira", "GR_1572_001"))

    def test_tidak_boleh_rating_jika_tracker_tidak_ada(self):
        """User yang belum nambahin buku ke tracker nggak boleh rating."""
        self.assertFalse(self.rs.cek_boleh_rating("akira", "GR_1572_001"))

    def test_cek_boleh_rating_substring_bug(self):
        """
        BUG FLAG — TEST INI SENGAJA GAGAL DENGAN IMPLEMENTASI SAAT INI.

        Implementasi sekarang:
            return "Selesai" in tracker.get('status_baca', '')

        Masalah: substring matching kena false-positive untuk status
        hipotetis yang mengandung "Selesai" tapi BUKAN "Selesai Dibaca".
        Contoh: "Selesai Tapi Drop", "Belum Selesai".

        Test ini bikin status fiktif "Belum Selesai" dan ngecek bahwa
        sistem TIDAK boleh ngizinin rating. Kalau test ini fail, artinya
        bug substring masih ada dan harus diganti jadi equality check:
            return tracker.get('status_baca') == "Selesai Dibaca"
        """
        self._seed_tracker("akira", "GR_1572_001", "Belum Selesai", 0)
        self.assertFalse(
            self.rs.cek_boleh_rating("akira", "GR_1572_001"),
            "BUG: status 'Belum Selesai' tidak boleh diizinkan rating, "
            "tapi substring 'Selesai' di status_baca lolos cek. "
            "Fix: ganti `\"Selesai\" in ...` jadi `... == \"Selesai Dibaca\"`."
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)