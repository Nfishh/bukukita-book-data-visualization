import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch
from matplotlib.animation import FuncAnimation
import numpy as np

class DataVisualizer:
    def __init__(self):
        self.colors = {
            'primary': '#1E3A8A',
            'success': '#065F46',
            'warning': '#9A3412',
            'text': '#374151',
            'bg': '#F8FAFC',
            'hover': '#3B82F6',
            'hover_warning': '#F59E0B'
        }

    def _setup_figure(self, figsize=(5, 4)):
        fig = Figure(figsize=figsize, dpi=100)
        fig.patch.set_alpha(0.0)
        return fig

    def _clean_axes(self, ax):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#E2E8F0')
        ax.spines['bottom'].set_color('#E2E8F0')
        ax.tick_params(colors=self.colors['text'])

    # =========================================================
    # PIE CHART — animasi theta per-wedge tanpa ax.clear()
    # =========================================================
    def create_pie_chart_status(self, data_status=None):
        if not data_status:
            data_status = {'Selesai': 45, 'Sedang': 12, 'Belum': 20}

        fig = self._setup_figure(figsize=(6, 6))
        ax = fig.add_subplot(111)

        labels = list(data_status.keys())
        sizes  = list(data_status.values())
        warna  = [self.colors['warning'], self.colors['success'], self.colors['primary']]
        total_frames = 45

        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, colors=warna, autopct='%1.1f%%',
            startangle=90, radius=1.3,
            pctdistance=1.15,
            labeldistance=1.35,
            wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2)
        )

        for autotext in autotexts:
            autotext.set_visible(False)
            autotext.set_color(self.colors['text'])
            autotext.set_fontsize(13)
            autotext.set_fontweight('bold')

        for text in texts:
            text.set_color(self.colors['text'])
            text.set_fontsize(12)
            text.set_fontweight('bold')
            text.set_alpha(0)  

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

            for text in texts:
                text.set_alpha(progress)

            canvas.draw_idle()

            if frame >= total_frames:
                anim_pie.event_source.stop()
                canvas.mpl_connect("motion_notify_event", on_hover_pie)

        def on_hover_pie(event):
            if event.inaxes != ax:
                if canvas.hovered_pie_idx != -1:
                    for i, w in enumerate(wedges):
                        w.set_alpha(1.0)
                        autotexts[i].set_visible(False)
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
                        w.set_alpha(0.80)
                        autotexts[i].set_visible(True)
                    else:
                        w.set_alpha(1.0)
                        autotexts[i].set_visible(False)
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
    # BAR CHART — animasi pop-up + hover highlight & angka
    # =========================================================
    def create_bar_chart_kategori(self, data_kategori=None):
        if not data_kategori:
            data_kategori = {'Fiksi': 120, 'Non-Fiksi': 85}

        fig = self._setup_figure(figsize=(5, 4))
        ax = fig.add_subplot(111)

        kategori = list(data_kategori.keys())
        jumlah   = list(data_kategori.values())
        total_frames = 30

        bars = ax.bar(kategori, jumlah, color='white', alpha=0)

        new_patches = []
        for bar in bars:
            patch = FancyBboxPatch(
                (bar.get_x() + 0.15, 0),
                bar.get_width() - 0.3, 0,
                boxstyle="Round,pad=0,rounding_size=0.2",
                facecolor=self.colors['primary'], edgecolor="none"
            )
            ax.add_patch(patch)
            new_patches.append(patch)

        ax.set_ylim(0, max(jumlah) * 1.2)
        self._clean_axes(ax)

        value_texts = []
        for bar in bars:
            txt = ax.text(
                bar.get_x() + bar.get_width() / 2, 3,
                f'{int(bar.get_height())}',
                ha='center', va='bottom',
                color=self.colors['text'], fontweight='bold', fontsize=11,
                alpha=0 
            )
            txt.set_visible(False) # FIX: Sembunyikan awal
            value_texts.append(txt)

        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background-color: transparent;")
        canvas.hovered_bar_idx = -1

        def animate_bar(frame):
            t = frame / total_frames
            progress = 1 - (1 - t) ** 3  

            for i, (patch, bar) in enumerate(zip(new_patches, bars)):
                h = jumlah[i] * progress
                patch.set_height(h)
                value_texts[i].set_position((
                    bar.get_x() + bar.get_width() / 2, h + 3
                ))
                # HAPUS BARIS INI: value_texts[i].set_alpha(progress) (Biar gak nongol pas animasi awal)

            canvas.draw_idle()
            if frame >= total_frames:
                anim_bar.event_source.stop()

        def on_hover_bar(event):
            if event.inaxes != ax:
                if canvas.hovered_bar_idx != -1:
                    for i, p in enumerate(new_patches):
                        p.set_facecolor(self.colors['primary'])
                        value_texts[i].set_visible(False) # FIX: Sembunyikan angka kalau keluar
                    canvas.hovered_bar_idx = -1
                    canvas.draw_idle()
                return

            found_idx = -1
            for i, p in enumerate(new_patches):
                if p.contains(event)[0]:
                    found_idx = i
                    break

            if found_idx != canvas.hovered_bar_idx:
                canvas.hovered_bar_idx = found_idx
                for i, p in enumerate(new_patches):
                    if i == found_idx:
                        p.set_facecolor(self.colors['hover'])
                        value_texts[i].set_visible(True) # FIX: Munculkan angka HANYA yg dihover
                        value_texts[i].set_alpha(1.0)
                    else:
                        p.set_facecolor(self.colors['primary'])
                        value_texts[i].set_visible(False) # Sembunyikan sisanya
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
    # HISTOGRAM RATING — animasi stagger pop-up + hover highlight & angka
    # =========================================================
    def create_histogram_rating(self, data_rating=None):
        if not data_rating:
            data_rating = {'★ 1': 10, '★ 2': 20, '★ 3': 40, '★ 4': 80, '★ 5': 50}

        fig = self._setup_figure(figsize=(8, 4))
        ax = fig.add_subplot(111)

        bintang = list(data_rating.keys())
        jumlah  = list(data_rating.values())
        n       = len(jumlah)
        total_frames = 30
        stagger = 4

        bars = ax.bar(bintang, jumlah, color='white', alpha=0)

        new_patches = []
        for bar in bars:
            patch = FancyBboxPatch(
                (bar.get_x() + 0.1, 0),
                bar.get_width() - 0.2, 0,
                boxstyle="Round,pad=0,rounding_size=0.25",
                facecolor=self.colors['warning'], edgecolor="none"
            )
            ax.add_patch(patch)
            new_patches.append(patch)

        ax.set_ylim(0, max(jumlah) * 1.2)
        self._clean_axes(ax)

        value_texts = []
        for bar in bars:
            txt = ax.text(
                bar.get_x() + bar.get_width() / 2, 2,
                f'{int(bar.get_height())}',
                ha='center', va='bottom',
                color=self.colors['text'], fontweight='bold',
                alpha=0
            )
            txt.set_visible(False) # FIX: Sembunyikan awal
            value_texts.append(txt)

        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background-color: transparent;")
        canvas.hovered_hist_idx = -1

        total_anim_frames = total_frames + (n - 1) * stagger

        def animate_hist(frame):
            for i, (patch, bar) in enumerate(zip(new_patches, bars)):
                effective = max(0, frame - i * stagger)
                t = min(effective / total_frames, 1.0)
                progress = 1 - (1 - t) ** 3

                h = jumlah[i] * progress
                patch.set_height(h)
                value_texts[i].set_position((
                    bar.get_x() + bar.get_width() / 2, h + 2
                ))
                # HAPUS BARIS INI: value_texts[i].set_alpha(progress) (Biar gak nongol pas animasi awal)

            canvas.draw_idle()
            if frame >= total_anim_frames:
                anim_hist.event_source.stop()

        def on_hover_hist(event):
            if event.inaxes != ax:
                if canvas.hovered_hist_idx != -1:
                    for i, p in enumerate(new_patches):
                        p.set_facecolor(self.colors['warning'])
                        value_texts[i].set_visible(False) # FIX: Sembunyikan angka kalau keluar
                    canvas.hovered_hist_idx = -1
                    canvas.draw_idle()
                return

            found_idx = -1
            for i, p in enumerate(new_patches):
                if p.contains(event)[0]:
                    found_idx = i
                    break

            if found_idx != canvas.hovered_hist_idx:
                canvas.hovered_hist_idx = found_idx
                for i, p in enumerate(new_patches):
                    if i == found_idx:
                        p.set_facecolor(self.colors['hover_warning'])
                        value_texts[i].set_visible(True) # FIX: Munculkan angka HANYA yg dihover
                        value_texts[i].set_alpha(1.0)
                    else:
                        p.set_facecolor(self.colors['warning'])
                        value_texts[i].set_visible(False) # Sembunyikan sisanya
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