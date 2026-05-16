# run_tests.py
# Author    : Muhammad Iqbal 251524114
# Deskripsi : Master test runner untuk seluruh test suite BukuKita.
#             Menggunakan unittest.TestLoader.discover() untuk menemukan dan
#             menjalankan semua file test_*.py di folder tests/ secara
#             otomatis, lalu mencetak ringkasan jumlah passed/failed/error
#             di akhir. Mendukung flag -v untuk output verbose per-test.
#             Exit code 0 jika semua lulus, 1 jika ada yang gagal.


# run_tests.py
# ============================================================
# Master Test Runner untuk BukuKita
# ------------------------------------------------------------
# Jalanin SEMUA test di folder tests/ secara otomatis.
#
# Cara pakai:
#   python run_tests.py            → output ringkas
#   python run_tests.py -v         → output verbose (per-test)
#
# Exit code:
#   0  = semua test PASSED
#   1  = ada test yang FAILED atau ERROR
# ============================================================

import sys
import os
import unittest

# Pastikan project root ada di sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def main():
    verbosity = 2 if "-v" in sys.argv else 1

    print("=" * 70)
    print("  BukuKita — QA Automated Test Suite")
    print("=" * 70)
    print()

    # Discover semua test di folder tests/
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=os.path.join(PROJECT_ROOT, "tests"),
        pattern="test_*.py",
    )

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    # Ringkasan akhir
    print()
    print("=" * 70)
    print("  Ringkasan Hasil")
    print("=" * 70)
    total   = result.testsRun
    fails   = len(result.failures)
    errors  = len(result.errors)
    skipped = len(result.skipped)
    passed  = total - fails - errors - skipped

    print(f"  Total dijalankan : {total}")
    print(f"  Passed           : {passed}")
    print(f"  Failed           : {fails}")
    print(f"  Errors           : {errors}")
    print(f"  Skipped          : {skipped}")
    print()

    if fails == 0 and errors == 0:
        print("  STATUS: ✅ SEMUA TEST LULUS")
        print("=" * 70)
        sys.exit(0)
    else:
        print("  STATUS: ❌ ADA TEST YANG GAGAL")
        print("  → Cek log di atas untuk detail bug yang di-flag.")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()