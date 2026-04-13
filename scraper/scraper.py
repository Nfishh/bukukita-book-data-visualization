"""
scraper.py
==========
web scraper untuk mengambil 250 buku teratas dari daftar Goodreads:
  https://www.goodreads.com/list/show/1572.Buku_Indonesia_Sepanjang_Masa

Arsitektur 3 Fase:
  Fase 1 — List Crawling  : Ambil data dasar + URL detail dari halaman 1-3.
  Fase 2 — Deep Crawling  : Buka URL detail tiap buku untuk sinopsis, genre, dsb.
  Fase 3 — Image Download : Unduh cover buku ke assets/covers/.

Output: buku.json
"""

import json
import os
import re
import time
import random
import cloudscraper

from dataclasses import dataclass, field, asdict
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Konstanta
# ---------------------------------------------------------------------------

BASE_URL = "https://www.goodreads.com"
LIST_URL = "https://www.goodreads.com/list/show/1572.Buku_Indonesia_Sepanjang_Masa"
LIST_ID  = "1572"

COVER_DIR   = os.path.join("assets", "covers")
OUTPUT_FILE = "buku.json"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"
]

PAGES_TO_CRAWL  = 6      
TARGET_BOOKS    = 500
SLEEP_DETAIL    = 4.0    # Jeda anti-blokir Cloudflare
SLEEP_LIST      = 2.0    
REQUEST_TIMEOUT = 20     

# ---------------------------------------------------------------------------
# Data class
# ---------------------------------------------------------------------------

@dataclass
class BookData:
    """Representasi satu buku dalam skema JSON yang diminta."""

    id_buku:         str            = ""
    judul:           str            = ""
    penulis:         str            = ""
    avg_rating_gr:   float          = 0.0
    total_ratings:   int            = 0
    score:           int            = 0
    people_voted:    int            = 0
    sinopsis:        str            = ""
    genre:           list           = field(default_factory=list)
    pages:           int            = 0
    first_published: str            = ""
    isbn:            str            = ""
    cover_url:       str            = ""
    local_cover_path: str           = ""


# ---------------------------------------------------------------------------
# Helper: Pembersih data (Data Cleaning)
# ---------------------------------------------------------------------------

def _clean_int(text: str) -> int:
    """Ambil angka integer dari teks acak, e.g. '25,143 ratings' → 25143."""
    if not text:
        return 0
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else 0


def _clean_float(text: str) -> float:
    """Ambil float dari teks acak, e.g. '4.35 avg rating' → 4.35."""
    if not text:
        return 0.0
    match = re.search(r"[\d]+\.?[\d]*", text)
    return float(match.group()) if match else 0.0


def _clean_pages(text: str) -> int:
    """Ambil jumlah halaman, e.g. '535 pages' → 535."""
    return _clean_int(text)


def _clean_year(text: str) -> str:
    """Ekstrak tahun 4-digit dari teks publikasi."""
    if not text:
        return ""
    match = re.search(r"\b(1[0-9]{3}|20[0-2][0-9])\b", text)
    return match.group() if match else text.strip()


def _clean_str(text: str) -> str:
    """Bersihkan spasi berlebih dan newline dari string."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


# ---------------------------------------------------------------------------
# Kelas Utama
# ---------------------------------------------------------------------------

class GoodreadsScraper:
    """
    Scraper tiga fase untuk daftar buku Goodreads.

    Penggunaan:
        scraper = GoodreadsScraper()
        scraper.run()
    """

    def __init__(self) -> None:
        self.session = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
        self._ensure_dirs()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _ensure_dirs(self) -> None:
        """Buat direktori output cover jika belum ada."""
        os.makedirs(COVER_DIR, exist_ok=True)

    # ------------------------------------------------------------------
    # Utilitas Request
    # ------------------------------------------------------------------

    def _get(self, url: str, params: Optional[dict] = None) -> Optional[BeautifulSoup]:
        """
        Lakukan GET request dengan rotasi User-Agent dan kembalikan objek BeautifulSoup.
        """
        try:
            # Acak identitas browser setiap kali request
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            self.session.headers.update(headers)
            
            resp = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except requests.RequestException as exc:
            print(f"  [ERROR] Request gagal: {exc}")
            return None

    # ------------------------------------------------------------------
    # FASE 1: List Crawling
    # ------------------------------------------------------------------

    def crawl_list_pages(self) -> list[dict]:
        """
        Iterasi halaman 1–PAGES_TO_CRAWL dan kumpulkan data dasar + URL detail.
        Menggunakan internal counter untuk memastikan ID berurut dan tidak tertimpa.
        """
        print("=" * 60)
        print("FASE 1: List Crawling")
        print("=" * 60)

        seen_urls: set[str] = set()   
        raw_books: list[dict] = []
        internal_id_counter = 1  # Penghitung independen agar ID berurut 001-250

        for page_num in range(1, PAGES_TO_CRAWL + 1):
            if len(raw_books) >= TARGET_BOOKS:
                break

            print(f"\n[Halaman {page_num}] Mengambil data list...")
            soup = self._get(LIST_URL, params={"page": page_num})
            if soup is None:
                print(f"  Halaman {page_num} gagal diambil, melewati.")
                continue

            rows = soup.select('tr[itemtype="http://schema.org/Book"]')
            print(f"  Ditemukan {len(rows)} buku di halaman ini.")

            for row in rows:
                if len(raw_books) >= TARGET_BOOKS:
                    break

                book = self._parse_list_row(row, internal_id_counter)
                if not book:
                    continue

                # Deduplication dengan Set
                url = book.get("detail_url", "")
                if url in seen_urls:
                    print(f"  [DUPLIKAT] Dilewati: {book.get('judul', '')}")
                    continue
                
                seen_urls.add(url)
                raw_books.append(book)
                internal_id_counter += 1  # Naikkan angka ID untuk buku berikutnya

            if page_num < PAGES_TO_CRAWL:
                time.sleep(SLEEP_LIST)

        print(f"\n[Fase 1 Selesai] Total buku unik dikumpulkan: {len(raw_books)}")
        return raw_books

    def _parse_list_row(self, row: BeautifulSoup, current_id: int) -> Optional[dict]:
        """Parse satu baris <tr> dari halaman list."""
        try:
            # Nomor urut ranking (untuk informasi saja, tidak untuk ID)
            rank_tag = row.select_one("td.number")
            rank_num = _clean_int(rank_tag.get_text()) if rank_tag else 0

            # Judul & URL detail
            title_tag = row.select_one("a.bookTitle")
            if not title_tag:
                return None
            judul      = _clean_str(title_tag.get_text())
            detail_url = urljoin(BASE_URL, title_tag["href"])

            # Penulis
            author_tag = row.select_one("a.authorName")
            penulis    = _clean_str(author_tag.get_text()) if author_tag else ""

            # Rating
            rating_tag    = row.select_one("span.minirating")
            rating_text   = rating_tag.get_text() if rating_tag else ""
            avg_rating_gr = _clean_float(rating_text)
            total_ratings = _clean_int(rating_text.split("rating")[0].split("—")[-1] if "rating" in rating_text else "")

            # Score & Votes 
            score_tag    = row.select_one("td.scoreContainer")
            score        = 0
            people_voted = 0
            if score_tag:
                sc_text = score_tag.get_text(separator=" ")
                score_match = re.search(r"score:\s*([\d,]+)", sc_text, re.I)
                votes_match = re.search(r"([\d,]+)\s*people voted", sc_text, re.I)
                if score_match:
                    score = _clean_int(score_match.group(1))
                if votes_match:
                    people_voted = _clean_int(votes_match.group(1))

            # Cover URL 
            img_tag   = row.select_one("img")
            cover_url = img_tag["src"] if img_tag and img_tag.get("src") else ""

            # Buat ID buku yang aman dari duplikasi ranking kembar
            id_buku = f"GR_{LIST_ID}_{current_id:03d}"

            return {
                "id_buku":      id_buku,
                "rank":         rank_num,
                "judul":        judul,
                "penulis":      penulis,
                "avg_rating_gr": avg_rating_gr,
                "total_ratings": total_ratings,
                "score":        score,
                "people_voted": people_voted,
                "cover_url":    cover_url,
                "detail_url":   detail_url,
            }

        except Exception as exc:
            print(f"  [WARN] Gagal parse baris: {exc}")
            return None

    # ------------------------------------------------------------------
    # FASE 2: Deep Crawling
    # ------------------------------------------------------------------

    def crawl_book_details(self, raw_books: list[dict]) -> list[BookData]:
        """Buka URL detail tiap buku untuk mengekstrak sinopsis, genre, pages, dsb."""
        print("\n" + "=" * 60)
        print("FASE 2: Deep Crawling")
        print("=" * 60)

        books: list[BookData] = []

        for idx, raw in enumerate(raw_books, start=1):
            detail_url = raw.get("detail_url", "")
            print(f"\n[{idx}/{len(raw_books)}] {raw.get('judul', '')} — {detail_url}")

            book = BookData(
                id_buku        = raw["id_buku"],
                judul          = raw["judul"],
                penulis        = raw["penulis"],
                avg_rating_gr  = raw["avg_rating_gr"],
                total_ratings  = raw["total_ratings"],
                score          = raw["score"],
                people_voted   = raw["people_voted"],
                cover_url      = raw["cover_url"],
            )

            if detail_url:
                soup = self._get(detail_url)
                if soup:
                    self._enrich_book(book, soup)
                else:
                    print("  [WARN] Gagal mengambil halaman detail.")

            books.append(book)

            # Jeda anti-blokir (dengan sedikit elemen acak)
            if idx < len(raw_books):
                waktu_jeda = SLEEP_DETAIL + random.uniform(0.5, 2.0)
                time.sleep(waktu_jeda)

        print(f"\n[Fase 2 Selesai] Detail berhasil diambil: {len(books)} buku.")
        return books

    def _enrich_book(self, book: BookData, soup: BeautifulSoup) -> None:
        """Isi atribut lanjutan BookData dari halaman detail buku."""
        
        # --- Sinopsis ---
        try:
            desc_tag = (
                soup.select_one("div[data-testid='description'] span")
                or soup.select_one("#description span[style]")
                or soup.select_one("#description span")
            )
            book.sinopsis = _clean_str(desc_tag.get_text()) if desc_tag else ""
        except Exception:
            book.sinopsis = ""

        # --- Genre ---
        try:
            # Mencari link yg mengarah ke /genres/ (Cara tangguh)
            genre_tags = soup.select("a[href*='/genres/']")
            if not genre_tags:
                genre_tags = soup.select("span[data-testid='genresList'] a, .left .elementList .actionLinkLite.bookPageGenreLink")
            
            genres = list({_clean_str(g.get_text()) for g in genre_tags if g.get_text().strip()})
            book.genre = genres[:6]  # batasi maksimal 6 genre
        except Exception:
            book.genre = []

        # --- Pages ---
        try:
            pages_tag = (
                soup.select_one("p[data-testid='pagesFormat']")
                or soup.select_one("span[itemprop='numberOfPages']")
            )
            book.pages = _clean_pages(pages_tag.get_text()) if pages_tag else 0
        except Exception:
            book.pages = 0

        # --- First Published ---
        try:
            pub_tag = (
                soup.select_one("p[data-testid='publicationInfo']")
                or soup.select_one(".row:has(> .infoBoxRowTitle:-soup-contains('Published'))")
            )
            if pub_tag:
                book.first_published = _clean_year(pub_tag.get_text())
            else:
                pub_candidates = soup.find_all(string=re.compile(r"Published", re.I))
                for cand in pub_candidates:
                    parent_text = cand.parent.get_text() if cand.parent else ""
                    year = _clean_year(parent_text)
                    if year:
                        book.first_published = year
                        break
        except Exception:
            book.first_published = ""

        # --- ISBN ---
        try:
            # Cari dari script JSON-LD (Paling akurat di Goodreads baru)
            script_tag = soup.find('script', type='application/ld+json')
            if script_tag and script_tag.string:
                data = json.loads(script_tag.string)
                if 'isbn' in data:
                    book.isbn = data['isbn']
                    
            if not book.isbn:
                isbn_tag = soup.select_one("span[itemprop='isbn']")
                book.isbn = _clean_str(isbn_tag.get_text()) if isbn_tag else ""
        except Exception:
            book.isbn = ""

        # --- Cover URL ---
        try:
            cover_img = (
                soup.select_one("img[data-testid='coverImage']")
                or soup.select_one("#coverImage")
                or soup.select_one("img.ResponsiveImage")
            )
            if cover_img and cover_img.get("src"):
                book.cover_url = cover_img["src"]
        except Exception:
            pass 

        # --- Avg Rating & Total Rating ---
        try:
            rating_val = soup.select_one("div.RatingStatistics__rating")
            if rating_val:
                book.avg_rating_gr = _clean_float(rating_val.get_text())

            ratings_count = soup.select_one("span[data-testid='ratingsCount']")
            if ratings_count:
                book.total_ratings = _clean_int(ratings_count.get_text())
        except Exception:
            pass

    # ------------------------------------------------------------------
    # FASE 3: Image Download
    # ------------------------------------------------------------------

    def download_covers(self, books: list[BookData]) -> None:
        """Unduh gambar cover tiap buku ke COVER_DIR."""
        print("\n" + "=" * 60)
        print("FASE 3: Image Download")
        print("=" * 60)

        for idx, book in enumerate(books, start=1):
            if not book.cover_url:
                print(f"  [{idx}] {book.id_buku}: Tidak ada cover URL, dilewati.")
                continue

            local_path = os.path.join(COVER_DIR, f"{book.id_buku}.jpg")

            if os.path.exists(local_path):
                book.local_cover_path = local_path
                print(f"  [{idx}] {book.id_buku}: Cover sudah ada, dilewati.")
                continue

            try:
                print(f"  [{idx}] {book.id_buku}: Mengunduh {book.cover_url[:60]}...")
                resp = self.session.get(book.cover_url, timeout=REQUEST_TIMEOUT, stream=True)
                resp.raise_for_status()

                with open(local_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)

                book.local_cover_path = local_path
                print(f"    → Tersimpan: {local_path}")

            except Exception as exc:
                print(f"    [ERROR] Gagal unduh cover {book.id_buku}: {exc}")
                book.local_cover_path = ""

            time.sleep(0.5) 

        print(f"\n[Fase 3 Selesai] Cover diproses untuk {len(books)} buku.")

    # ------------------------------------------------------------------
    # Export JSON
    # ------------------------------------------------------------------

    def export_json(self, books: list[BookData]) -> None:
        """Ekspor list BookData ke file JSON."""
        output = []
        for book in books:
            d = asdict(book)
            d.pop("rank", None)
            d.pop("detail_url", None)
            output.append(d)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Data berhasil diekspor ke '{OUTPUT_FILE}' ({len(output)} buku).")

    # ------------------------------------------------------------------
    # Entry Point Utama
    # ------------------------------------------------------------------

    def run(self) -> None:
        print("\n🚀 Memulai GoodreadsScraper...")
        print(f"   Target  : {TARGET_BOOKS} buku teratas")
        print(f"   Halaman : 1 – {PAGES_TO_CRAWL}")
        print(f"   Output  : {OUTPUT_FILE}")
        print(f"   Covers  : {COVER_DIR}/\n")

        raw_books = self.crawl_list_pages()
        if not raw_books:
            print("❌ Tidak ada buku yang berhasil dikumpulkan. Berhenti.")
            return

        books = self.crawl_book_details(raw_books)
        self.download_covers(books)
        self.export_json(books)

        print("\n🎉 Scraping selesai!")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    scraper = GoodreadsScraper()
    scraper.run()
