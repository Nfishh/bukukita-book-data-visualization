# rating_system.py

class RatingSystem:
    def __init__(self, data_manager):
        self.dm = data_manager

    def hitung_rating_global(self, book_id: str) -> tuple:
        """
        Hitung rata-rata rating dari semua user BukuKita untuk satu buku.
        Return: (rata_rata: float, jumlah_voter: int)
        """
        semua_tracker = self.dm.get_semua_tracker()
        ratings = [
            t['rating_personal']
            for t in semua_tracker
            if t.get('book_id') == book_id and t.get('rating_personal', 0) > 0
        ]
        if not ratings:
            return 0.0, 0
        avg = round(sum(ratings) / len(ratings), 2)
        return avg, len(ratings)

    def simpan_rating_personal(self, user_id: str, book_id: str, skor: float) -> bool:
        """
        Validasi, simpan rating personal (float 1.0–5.0),
        lalu hitung ulang & simpan akumulasi rating BukuKita ke buku.json.
        """
        # Normalisasi: ganti koma → titik, lalu parse float
        if isinstance(skor, str):
            skor = skor.replace(',', '.')
            try:
                skor = float(skor)
            except ValueError:
                return False

        skor = round(skor, 2)
        if not (1.0 <= skor <= 5.0):
            return False

        # Simpan ke tracker
        semua_tracker = self.dm.get_semua_tracker()
        tracker_ada = next(
            (t for t in semua_tracker
             if t.get('user_id') == user_id and t.get('book_id') == book_id),
            None
        )

        if tracker_ada:
            ok = self.dm.update_tracker(tracker_ada['id_tracker'], {"rating_personal": skor})
        else:
            import uuid
            data_baru = {
                "id_tracker"     : str(uuid.uuid4())[:8].upper(),
                "user_id"        : user_id,
                "book_id"        : book_id,
                "status_baca"    : "Selesai Dibaca",
                "rating_personal": skor,
            }
            ok = self.dm.simpan_tracker(data_baru)

        if ok:
            # Hitung ulang rata-rata semua user → simpan ke buku.json
            avg, total = self.hitung_rating_global(book_id)
            self.dm.update_rating_bukukita(book_id, avg, total)

        return ok

    def cek_boleh_rating(self, user_id: str, book_id: str) -> bool:
        """
        User hanya boleh memberi rating jika status baca = 'Selesai Dibaca'.
        """
        semua_tracker = self.dm.get_semua_tracker()
        tracker = next(
            (t for t in semua_tracker
             if t.get('user_id') == user_id and t.get('book_id') == book_id),
            None
        )
        if not tracker:
            return False
        return "Selesai" in tracker.get('status_baca', '')
