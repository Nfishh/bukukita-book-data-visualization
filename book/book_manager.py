# book_manager.py
import uuid

class BookManager:
    def __init__(self, data_manager):
        self.dm = data_manager

    def get_katalog(self):
        """Menyediakan data buku untuk ditampilkan di UI dashboard."""
        return self.dm.get_semua_buku()

    def update_status_baca(self, user_id, book_id, status):
        """Menyusun format pembaruan status bacaan atau menambah koleksi baru."""
        # Cek apakah buku sudah ada di tracker user
        semua_tracker = self.dm._read_json(self.dm.path_tracker)
        tracker_ada = next((t for t in semua_tracker if t.get('user_id') == user_id and t.get('book_id') == book_id), None)

        if tracker_ada:
            # Jika sudah ada, update statusnya
            return self.dm.update_tracker(tracker_ada['id_tracker'], {"status_baca": status})
        else:
            # Jika belum ada, buat entri baru
            data_baru = {
                "id_tracker": str(uuid.uuid4())[:8].upper(),
                "user_id": user_id,
                "book_id": book_id,
                "status_baca": status,
                "rating_personal": 0
            }
            return self.dm.simpan_tracker(data_baru)

    def hapus_dari_koleksi(self, tracker_id):
        """Meneruskan instruksi penghapusan entitas ke lapis data."""
        return self.dm.hapus_tracker(tracker_id)