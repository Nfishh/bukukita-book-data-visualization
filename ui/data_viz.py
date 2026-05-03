import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import numpy as np

class DataVisualizer:
    def __init__(self):
        self.colors = {
            'primary': '#1A56DB',       # Biru BukuKita
            'success': '#059669',       # Hijau Selesai
            'warning': '#D97706',       # Oranye Sedang/Rating
            'text': '#1A1F36',
            'text_light': '#6B7280',
            'bg': '#F8FAFC',
            'hover_primary': '#1E40AF',
            'hover_warning': '#B45309'
        }

    def _setup_figure(self, figsize=(5, 4)):
        fig = Figure(figsize=figsize, dpi=100)
        fig.patch.set_alpha(0.0)
        return fig

    def _clean_axes(self, ax):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False) # Sembunyikan garis kiri biar lebih clean
        ax.spines['bottom'].set_color('#E2E8F0')
        ax.tick_params(axis='x', colors=self.colors['text_light'], length=0, labelsize=11)
        ax.tick_params(axis='y', colors=self.colors['text_light'], length=0, labelsize=10)

    # =========================================================
    # PIE CHART (Dibuat jadi Donut Chart Interaktif)
    # =========================================================
    def create_pie_chart_status(self, data_status=None):
        if not data_status:
            data_status = {'Selesai': 45, 'Sedang': 12, 'Belum': 20}

        fig = self._setup_figure(figsize=(6, 6))
        ax = fig.add_subplot(111)

        labels = list(data_status.keys())
        sizes  = list(data_status.values())
        
        # Mapping warna biar konsisten sama StatCard Dashboard
        color_map = {'Selesai': self.colors['success'], 'Sedang': self.colors['warning'], 'Belum': self.colors['primary']}
        warna = [color_map.get(k, self.colors['primary']) for k in labels]
        
        total_frames = 45

        # FIX: Hapus autopct, kita taruh teksnya di tengah donut!
        wedges, _ = ax.pie(
            sizes, labels=None, colors=warna,
            startangle=90, radius=1.0, 
            wedgeprops=dict(width=0.45, edgecolor='white', linewidth=3)
        )

        # Teks di tengah Donut
        center_text = ax.text(0, 0, "Arahkan Mouse\nke Grafik", ha='center', va='center', 
                              fontsize=14, fontweight='bold', color=self.colors['text_light'])

        theta1_finals = [w.theta1 for w in wedges]
        theta2_finals = [w.theta2 for w in wedges]

        for w in wedges:
            w.set_theta2(w.theta1)

        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background-color: transparent;")
        canvas.hovered_pie_idx = -1

        def animate_pie(frame):
            t = frame / total_frames
            progress = 1 - (1 - t) ** 2  

            for i, w in enumerate(wedges):
                t1 = theta1_finals[i]
                t2_final = theta2_finals[i]
                w.set_theta2(t1 + (t2_final - t1) * progress)

            canvas.draw_idle()

            if frame >= total_frames:
                anim_pie.event_source.stop()
                canvas.mpl_connect("motion_notify_event", on_hover_pie)

        def on_hover_pie(event):
            if event.inaxes != ax:
                if canvas.hovered_pie_idx != -1:
                    for i, w in enumerate(wedges):
                        w.set_alpha(1.0)
                    center_text.set_text("Arahkan Mouse\nke Grafik")
                    center_text.set_color(self.colors['text_light'])
                    canvas.hovered_pie_idx = -1
                    canvas.draw_idle()
                return

            found_idx = -1
            for i, w in enumerate(wedges):
                if w.contains(event)[0]:
                    found_idx = i
                    break

            if found_idx != canvas.hovered_pie_idx:
                canvas.hovered_pie_idx = found_idx
                for i, w in enumerate(wedges):
                    if i == found_idx:
                        w.set_alpha(0.85)
                        # FIX: Update teks di tengah saat di-hover
                        percentage = (sizes[i] / sum(sizes)) * 100
                        center_text.set_text(f"{labels[i]}\n{sizes[i]} Buku\n({percentage:.1f}%)")
                        center_text.set_color(self.colors['text'])
                    else:
                        w.set_alpha(1.0)
                canvas.draw_idle()

        anim_pie = FuncAnimation(
            fig, animate_pie,
            frames=total_frames + 1,
            interval=30,
            repeat=False
        )
        canvas._anim_pie = anim_pie
        return canvas

    # =========================================================
    # BAR CHART KATEGORI (Balok Bersih Tanpa Bug Patch)
    # =========================================================
    def create_bar_chart_kategori(self, data_kategori=None):
        if not data_kategori:
            data_kategori = {'Fiksi': 120, 'Non-Fiksi': 85}

        fig = self._setup_figure(figsize=(5, 4))
        ax = fig.add_subplot(111)

        kategori = list(data_kategori.keys())
        jumlah   = list(data_kategori.values())
        total_frames = 30

        # Tambah garis bantu (grid) horizontal biar estetik
        ax.grid(axis='y', linestyle='--', alpha=0.5, color='#CBD5E1', zorder=0)

        # FIX: Pakai bar standar, no more FancyBboxPatch yg bikin aneh!
        bars = ax.bar(kategori, jumlah, color=self.colors['primary'], width=0.5, zorder=3)

        max_val = max(jumlah) if jumlah else 10
        ax.set_ylim(0, max_val * 1.25)
        self._clean_axes(ax)

        value_texts = []
        for bar in bars:
            txt = ax.text(
                bar.get_x() + bar.get_width() / 2, 0,
                f'{int(bar.get_height())}',
                ha='center', va='bottom',
                color=self.colors['text'], fontweight='bold', fontsize=12
            )
            txt.set_visible(False) 
            value_texts.append(txt)

        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background-color: transparent;")
        canvas.hovered_bar_idx = -1

        def animate_bar(frame):
            t = frame / total_frames
            progress = 1 - (1 - t) ** 3  

            for i, bar in enumerate(bars):
                h = jumlah[i] * progress
                bar.set_height(h)
                # Teks ngikutin tinggi bar
                value_texts[i].set_position((bar.get_x() + bar.get_width() / 2, h + (max_val * 0.02)))

            canvas.draw_idle()
            if frame >= total_frames:
                anim_bar.event_source.stop()

        def on_hover_bar(event):
            if event.inaxes != ax:
                if canvas.hovered_bar_idx != -1:
                    for i, b in enumerate(bars):
                        b.set_facecolor(self.colors['primary'])
                        value_texts[i].set_visible(False) 
                    canvas.hovered_bar_idx = -1
                    canvas.draw_idle()
                return

            found_idx = -1
            for i, b in enumerate(bars):
                if b.contains(event)[0]:
                    found_idx = i
                    break

            if found_idx != canvas.hovered_bar_idx:
                canvas.hovered_bar_idx = found_idx
                for i, b in enumerate(bars):
                    if i == found_idx:
                        b.set_facecolor(self.colors['hover_primary'])
                        value_texts[i].set_visible(True) 
                    else:
                        b.set_facecolor(self.colors['primary'])
                        value_texts[i].set_visible(False) 
                canvas.draw_idle()

        anim_bar = FuncAnimation(
            fig, animate_bar,
            frames=total_frames + 1,
            interval=30,
            repeat=False
        )
        canvas.mpl_connect("motion_notify_event", on_hover_bar)
        canvas._anim_bar = anim_bar
        return canvas

    # =========================================================
    # HISTOGRAM RATING (Balok Bersih)
    # =========================================================
    def create_histogram_rating(self, data_rating=None):
        if not data_rating:
            data_rating = {'★ 1': 0, '★ 2': 0, '★ 3': 0, '★ 4': 0, '★ 5': 0}

        fig = self._setup_figure(figsize=(8, 4))
        ax = fig.add_subplot(111)

        bintang = list(data_rating.keys())
        jumlah  = list(data_rating.values())
        n       = len(jumlah)
        total_frames = 30
        stagger = 4

        ax.grid(axis='y', linestyle='--', alpha=0.5, color='#CBD5E1', zorder=0)

        # FIX: Pakai bar standar
        bars = ax.bar(bintang, jumlah, color=self.colors['warning'], width=0.55, zorder=3)

        max_val = max(jumlah) if max(jumlah) > 0 else 5
        ax.set_ylim(0, max_val * 1.25)
        self._clean_axes(ax)

        value_texts = []
        for bar in bars:
            txt = ax.text(
                bar.get_x() + bar.get_width() / 2, 0,
                f'{int(bar.get_height())}',
                ha='center', va='bottom',
                color=self.colors['text'], fontweight='bold', fontsize=12
            )
            txt.set_visible(False) 
            value_texts.append(txt)

        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background-color: transparent;")
        canvas.hovered_hist_idx = -1

        total_anim_frames = total_frames + (n - 1) * stagger

        def animate_hist(frame):
            for i, bar in enumerate(bars):
                effective = max(0, frame - i * stagger)
                t = min(effective / total_frames, 1.0)
                progress = 1 - (1 - t) ** 3

                h = jumlah[i] * progress
                bar.set_height(h)
                value_texts[i].set_position((bar.get_x() + bar.get_width() / 2, h + (max_val * 0.02)))

            canvas.draw_idle()
            if frame >= total_anim_frames:
                anim_hist.event_source.stop()

        def on_hover_hist(event):
            if event.inaxes != ax:
                if canvas.hovered_hist_idx != -1:
                    for i, b in enumerate(bars):
                        b.set_facecolor(self.colors['warning'])
                        value_texts[i].set_visible(False) 
                    canvas.hovered_hist_idx = -1
                    canvas.draw_idle()
                return

            found_idx = -1
            for i, b in enumerate(bars):
                if b.contains(event)[0]:
                    found_idx = i
                    break

            if found_idx != canvas.hovered_hist_idx:
                canvas.hovered_hist_idx = found_idx
                for i, b in enumerate(bars):
                    if i == found_idx:
                        b.set_facecolor(self.colors['hover_warning'])
                        value_texts[i].set_visible(True) 
                    else:
                        b.set_facecolor(self.colors['warning'])
                        value_texts[i].set_visible(False)
                canvas.draw_idle()

        anim_hist = FuncAnimation(
            fig, animate_hist,
            frames=total_anim_frames + 1,
            interval=30,
            repeat=False
        )
        canvas.mpl_connect("motion_notify_event", on_hover_hist)
        canvas._anim_hist = anim_hist
        return canvas