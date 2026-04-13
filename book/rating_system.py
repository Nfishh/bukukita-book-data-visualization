# rating_system.py

class RatingSystem:
    def __init__(self, data_manager):
        self.dm = data_manager

    def hitung_rating_global(self, book_id):
        """Kalkulasi average rating dari semua user untuk satu buku."""
        # Mengambil semua data tracker dari tracker.json
        semua_tracker = self.dm._read_json(self.dm.path_tracker)
        
        # Filter rating untuk buku tersebut yang tidak bernilai 0
        ratings = [t['rating_personal'] for t in semua_tracker 
                   if t.get('book_id') == book_id and t.get('rating_personal', 0) > 0]
        
        if not ratings:
            return 0.0
            
        return round(sum(ratings) / len(ratings), 2)

    def simpan_rating_personal(self, user_id, book_id, skor):
        """Validasi dan simpan penilaian individu."""
        if not (1 <= skor <= 5):
            return False

        semua_tracker = self.dm._read_json(self.dm.path_tracker)
        tracker_ada = next((t for t in semua_tracker if t.get('user_id') == user_id and t.get('book_id') == book_id), None)

        if tracker_ada:
            # Update rating pada tracker yang sudah ada
            return self.dm.update_tracker(tracker_ada['id_tracker'], {"rating_personal": skor})
        else:
            # Buat tracker baru jika user memberi rating pada buku yang belum masuk koleksinya
            import uuid
            data_baru = {
                "id_tracker": str(uuid.uuid4())[:8].upper(),
                "user_id": user_id,
                "book_id": book_id,
                "status_baca": "Unfinished",
                "rating_personal": skor
            }
            return self.dm.simpan_tracker(data_baru)