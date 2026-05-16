# ui/data_viz.py
# Developer : Muhammad Iqbal 252524114
# Deskripsi : Modul visualisasi data BukuKita. Menghasilkan chart dan
#             grafik statistik bacaan user (distribusi status baca,
#             rating rata-rata, progres membaca dari waktu ke waktu)
#             untuk ditampilkan di dashboard. Mendukung mode animasi
#             yang bisa diaktifkan/dimatikan per user via preferensi.


import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import matplotlib.patches

# ── Performance: matikan rcParams yang berat ──────────────────────────
matplotlib.rcParams.update({
    'path.simplify'           : True,
    'path.simplify_threshold' : 0.5,
    'agg.path.chunksize'      : 10000,
    'figure.max_open_warning' : 0,
})

_PALETTE = [
    '#1A56DB', '#059669', '#D97706', '#7C3AED',
    '#DB2777', '#0891B2', '#65A30D', '#EA580C',
]

def _card_color(key):
    MAP = {
        'Selesai Dibaca': '#059669', 'Selesai': '#059669',
        'Sedang Membaca': '#D97706', 'Sedang' : '#D97706',
        'Belum Dibaca'  : '#1A56DB', 'Belum'  : '#1A56DB',
        'Drop'          : '#94A3B8',
    }
    return MAP.get(key, '#1A56DB')


class DataVisualizer:
    def __init__(self):
        self.colors = {
            'primary'      : '#1A56DB',
            'success'      : '#059669',
            'warning'      : '#D97706',
            'text'         : '#1A1F36',
            'text_light'   : '#6B7280',
            'hover_primary': '#1E40AF',
            'hover_warning': '#B45309',
        }

    def _fig(self, w=5, h=4):
        fig = Figure(figsize=(w, h), dpi=90)
        fig.patch.set_alpha(0.0)
        return fig

    def _clean(self, ax, show_left=False):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(show_left)
        if show_left:
            ax.spines['left'].set_color('#E2E8F0')
        ax.spines['bottom'].set_color('#E2E8F0')
        ax.tick_params(axis='x', colors=self.colors['text_light'], length=0, labelsize=10)
        ax.tick_params(axis='y', colors=self.colors['text_light'], length=0, labelsize=9)

    def _canvas(self, fig):
        c = FigureCanvas(fig)
        c.setStyleSheet("background-color: transparent;")
        return c

    def _anim(self, fig, func, frames, interval=25):
        return FuncAnimation(fig, func, frames=frames,
                             interval=interval, repeat=False, blit=False)

    # ─────────────────────────────────────────────────────────────────
    # 1. PIE CHART STATUS BACAAN — FULL (bukan donut)
    # ─────────────────────────────────────────────────────────────────
    def create_pie_chart_status(self, data_status=None, use_animations=True):
        if not data_status:
            data_status = {'Selesai': 1, 'Sedang': 1, 'Belum': 1}

        import math
        labels = list(data_status.keys())
        sizes  = list(data_status.values())
        warna  = [_card_color(k) for k in labels]
        total  = sum(sizes)
        FRAMES = 18

        fig = self._fig(5, 4)
        ax  = fig.add_subplot(111)

        wedges, _ = ax.pie(
            sizes, labels=None, colors=warna, startangle=90, radius=1.0,
            wedgeprops=dict(edgecolor='white', linewidth=2.5),
        )
        legend_handles = [
            matplotlib.patches.Patch(color=warna[i], label=f"{labels[i]}  {sizes[i]}")
            for i in range(len(labels))
        ]
        ax.legend(handles=legend_handles, loc='lower left',
                  bbox_to_anchor=(-0.05, -0.12),
                  fontsize=10, framealpha=0, ncol=len(labels))

        theta1_f = [w.theta1 for w in wedges]
        theta2_f = [w.theta2 for w in wedges]
        for w in wedges:
            w.set_theta2(w.theta1)

        canvas = self._canvas(fig)
        canvas.hovered_idx = -1

        def animate(frame):
            t = min(frame / FRAMES, 1.0)
            p = 1 - (1 - t) ** 2
            for i, w in enumerate(wedges):
                w.set_theta2(theta1_f[i] + (theta2_f[i] - theta1_f[i]) * p)
            canvas.draw_idle()
            if frame >= FRAMES:
                if hasattr(canvas, '_anim') and canvas._anim:
                    canvas._anim.event_source.stop()
                for i, w in enumerate(wedges):
                    ang = (w.theta1 + w.theta2) / 2
                    r   = 0.6
                    x   = r * math.cos(math.radians(ang))
                    y   = r * math.sin(math.radians(ang))
                    pct = sizes[i] / total * 100
                    if pct >= 8:
                        ax.text(x, y, f"{pct:.0f}%", ha='center', va='center',
                                fontsize=11, fontweight='bold', color='white')
                canvas.mpl_connect("motion_notify_event", on_hover)
                canvas.draw_idle()

        def on_hover(event):
            if event.inaxes != ax:
                if canvas.hovered_idx != -1:
                    for w in wedges:
                        w.set_alpha(1.0)
                        w.set_radius(1.0)
                    canvas.hovered_idx = -1
                    canvas.draw_idle()
                return
            found = next((i for i, w in enumerate(wedges) if w.contains(event)[0]), -1)
            if found != canvas.hovered_idx:
                canvas.hovered_idx = found
                for i, w in enumerate(wedges):
                    w.set_alpha(0.85 if i == found else 0.95)
                    w.set_radius(1.06 if i == found else 1.0)
                canvas.draw_idle()

        if use_animations:
            a = self._anim(fig, animate, FRAMES + 1)
            canvas._anim = a
        else:
            canvas._anim = None
            animate(FRAMES)
        return canvas

    # ─────────────────────────────────────────────────────────────────
    # 2. PIE CHART KATEGORI KATALOG — FULL
    # ─────────────────────────────────────────────────────────────────
    def create_pie_chart_kategori_global(self, data_kategori=None, use_animations=True):
        if not data_kategori:
            data_kategori = {'Fiksi': 60, 'Non-Fiksi': 40}

        import math
        sorted_kat = sorted(data_kategori.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_kat) > 7:
            top     = sorted_kat[:6]
            lainnya = sum(v for _, v in sorted_kat[6:])
            top.append(("Lainnya", lainnya))
        else:
            top = sorted_kat

        labels = [k for k, _ in top]
        sizes  = [v for _, v in top]
        warna  = [_PALETTE[i % len(_PALETTE)] for i in range(len(labels))]
        total  = sum(sizes)
        FRAMES = 18

        fig = self._fig(5, 4)
        ax  = fig.add_subplot(111)

        wedges, _ = ax.pie(
            sizes, labels=None, colors=warna, startangle=90, radius=1.0,
            wedgeprops=dict(edgecolor='white', linewidth=2.5),
        )
        ncols = min(4, len(labels))
        legend_handles = [
            matplotlib.patches.Patch(color=warna[i], label=labels[i])
            for i in range(len(labels))
        ]
        ax.legend(handles=legend_handles, loc='lower left',
                  bbox_to_anchor=(-0.05, -0.15),
                  fontsize=9, framealpha=0, ncol=ncols)

        theta1_f = [w.theta1 for w in wedges]
        theta2_f = [w.theta2 for w in wedges]
        for w in wedges:
            w.set_theta2(w.theta1)

        canvas = self._canvas(fig)
        canvas.hovered_idx = -1

        def animate(frame):
            t = min(frame / FRAMES, 1.0)
            p = 1 - (1 - t) ** 2
            for i, w in enumerate(wedges):
                w.set_theta2(theta1_f[i] + (theta2_f[i] - theta1_f[i]) * p)
            canvas.draw_idle()
            if frame >= FRAMES:
                if hasattr(canvas, '_anim') and canvas._anim:
                    canvas._anim.event_source.stop()
                for i, w in enumerate(wedges):
                    ang = (w.theta1 + w.theta2) / 2
                    r   = 0.6
                    x   = r * math.cos(math.radians(ang))
                    y   = r * math.sin(math.radians(ang))
                    pct = sizes[i] / total * 100
                    if pct >= 6:
                        ax.text(x, y, f"{pct:.0f}%", ha='center', va='center',
                                fontsize=10, fontweight='bold', color='white')
                canvas.mpl_connect("motion_notify_event", on_hover)
                canvas.draw_idle()

        def on_hover(event):
            if event.inaxes != ax:
                if canvas.hovered_idx != -1:
                    for w in wedges:
                        w.set_alpha(1.0)
                        w.set_radius(1.0)
                    canvas.hovered_idx = -1
                    canvas.draw_idle()
                return
            found = next((i for i, w in enumerate(wedges) if w.contains(event)[0]), -1)
            if found != canvas.hovered_idx:
                canvas.hovered_idx = found
                for i, w in enumerate(wedges):
                    w.set_alpha(0.85 if i == found else 0.95)
                    w.set_radius(1.06 if i == found else 1.0)
                canvas.draw_idle()

        if use_animations:
            a = self._anim(fig, animate, FRAMES + 1)
            canvas._anim = a
        else:
            canvas._anim = None
            animate(FRAMES)
        return canvas

    # ─────────────────────────────────────────────────────────────────
    # 3. BAR CHART KATEGORI — HORIZONTAL, LEBAR PENUH, DINAMIS
    # ─────────────────────────────────────────────────────────────────
    def create_bar_chart_kategori(self, data_kategori=None, use_animations=True):
        if not data_kategori:
            data_kategori = {'Fiksi': 120, 'Non-Fiksi': 85}

        sorted_d = sorted(data_kategori.items(), key=lambda x: x[1], reverse=True)
        kategori = [k for k, _ in sorted_d]
        jumlah   = [v for _, v in sorted_d]
        n        = len(kategori)
        FRAMES   = 15

        fig_h    = max(3.5, min(10, n * 0.52 + 1.5))
        fig      = self._fig(w=12, h=fig_h)
        ax       = fig.add_subplot(111)

        colors_bar = [_PALETTE[i % len(_PALETTE)] for i in range(n)]
        bars       = ax.barh(kategori, [0] * n, color=colors_bar, height=0.55, left=0)
        max_val    = max(jumlah) if jumlah else 10
        ax.set_xlim(0, max_val * 1.18)
        ax.invert_yaxis()

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#E2E8F0')
        ax.tick_params(axis='y', length=0, labelsize=10, colors=self.colors['text'])
        ax.tick_params(axis='x', length=0, labelsize=9,  colors=self.colors['text_light'])
        ax.grid(axis='x', linestyle='--', alpha=0.4, color='#CBD5E1', zorder=0)

        val_texts = [
            ax.text(0, i, '', va='center', ha='left',
                    fontsize=10, fontweight='bold', color=self.colors['text'])
            for i in range(n)
        ]

        canvas = self._canvas(fig)
        canvas.hovered_idx = -1

        def animate(frame):
            t = min(frame / FRAMES, 1.0)
            p = 1 - (1 - t) ** 3
            for i, bar in enumerate(bars):
                w = jumlah[i] * p
                bar.set_width(w)
                val_texts[i].set_x(w + max_val * 0.01)
                val_texts[i].set_text(f"{jumlah[i]}" if p > 0.8 else '')
            canvas.draw_idle()
            if frame >= FRAMES:
                if hasattr(canvas, '_anim') and canvas._anim:
                    canvas._anim.event_source.stop()
                canvas.mpl_connect("motion_notify_event", on_hover)

        def on_hover(event):
            if event.inaxes != ax:
                if canvas.hovered_idx != -1:
                    for i, b in enumerate(bars):
                        b.set_facecolor(colors_bar[i])
                        b.set_alpha(1.0)
                    canvas.hovered_idx = -1
                    canvas.draw_idle()
                return
            found = next((i for i, b in enumerate(bars) if b.contains(event)[0]), -1)
            if found != canvas.hovered_idx:
                canvas.hovered_idx = found
                for i, b in enumerate(bars):
                    b.set_facecolor(colors_bar[i])
                    b.set_alpha(0.65 if (found >= 0 and i != found) else 1.0)
                canvas.draw_idle()

        if use_animations:
            a = self._anim(fig, animate, FRAMES + 1)
            canvas._anim = a
        else:
            canvas._anim = None
            animate(FRAMES)
        return canvas

    # ─────────────────────────────────────────────────────────────────
    # 4. BAR CHART STATUS SEMUA USER — HORIZONTAL, LEBAR PENUH
    # ─────────────────────────────────────────────────────────────────
    def create_bar_status_global(self, data_status_global=None, use_animations=True):
        if not data_status_global:
            data_status_global = {
                'Selesai Dibaca': 30, 'Sedang Membaca': 15,
                'Belum Dibaca'  : 20, 'Drop': 5,
            }

        sorted_d = sorted(data_status_global.items(), key=lambda x: x[1], reverse=True)
        labels   = [k for k, _ in sorted_d]
        values   = [v for _, v in sorted_d]
        colors   = [_card_color(l) for l in labels]
        n        = len(labels)
        FRAMES   = 15

        fig_h = max(3, min(8, n * 0.7 + 1.2))
        fig   = self._fig(w=12, h=fig_h)
        ax    = fig.add_subplot(111)

        bars    = ax.barh(labels, [0] * n, color=colors, height=0.5)
        max_val = max(values) if values else 5
        ax.set_xlim(0, max_val * 1.2)
        ax.invert_yaxis()

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#E2E8F0')
        ax.tick_params(axis='y', length=0, labelsize=10, colors=self.colors['text'])
        ax.tick_params(axis='x', length=0, labelsize=9,  colors=self.colors['text_light'])
        ax.grid(axis='x', linestyle='--', alpha=0.4, color='#CBD5E1', zorder=0)

        val_texts = [
            ax.text(0, i, '', va='center', ha='left',
                    fontsize=10, fontweight='bold', color=self.colors['text'])
            for i in range(n)
        ]

        canvas = self._canvas(fig)
        canvas.hovered_idx = -1

        def animate(frame):
            t = min(frame / FRAMES, 1.0)
            p = 1 - (1 - t) ** 3
            for i, bar in enumerate(bars):
                w = values[i] * p
                bar.set_width(w)
                val_texts[i].set_x(w + max_val * 0.01)
                val_texts[i].set_text(f"{values[i]} tracker" if p > 0.8 else '')
            canvas.draw_idle()
            if frame >= FRAMES:
                if hasattr(canvas, '_anim') and canvas._anim:
                    canvas._anim.event_source.stop()
                canvas.mpl_connect("motion_notify_event", on_hover)

        def on_hover(event):
            if event.inaxes != ax:
                if canvas.hovered_idx != -1:
                    for i, b in enumerate(bars):
                        b.set_facecolor(colors[i])
                        b.set_alpha(1.0)
                    canvas.hovered_idx = -1
                    canvas.draw_idle()
                return
            found = next((i for i, b in enumerate(bars) if b.contains(event)[0]), -1)
            if found != canvas.hovered_idx:
                canvas.hovered_idx = found
                for i, b in enumerate(bars):
                    b.set_facecolor(colors[i])
                    b.set_alpha(0.65 if (found >= 0 and i != found) else 1.0)
                canvas.draw_idle()

        if use_animations:
            a = self._anim(fig, animate, FRAMES + 1)
            canvas._anim = a
        else:
            canvas._anim = None
            animate(FRAMES)
        return canvas

    # ─────────────────────────────────────────────────────────────────
    # 5. HISTOGRAM RATING
    # ─────────────────────────────────────────────────────────────────
    def create_histogram_rating(self, data_rating=None, use_animations=True):
        if not data_rating:
            data_rating = {'★ 1': 0, '★ 2': 0, '★ 3': 0, '★ 4': 0, '★ 5': 0}

        bintang     = list(data_rating.keys())
        jumlah      = list(data_rating.values())
        n           = len(jumlah)
        FRAMES      = 15
        STAGGER     = 2
        star_colors = ['#94A3B8', '#60A5FA', '#34D399', '#FBBF24', '#F59E0B']
        colors_bar  = [star_colors[i] if i < len(star_colors)
                       else self.colors['warning'] for i in range(n)]

        fig     = self._fig(w=7, h=3.5)
        ax      = fig.add_subplot(111)
        ax.grid(axis='y', linestyle='--', alpha=0.4, color='#CBD5E1', zorder=0)
        bars    = ax.bar(bintang, [0] * n, color=colors_bar,
                         width=0.55, zorder=3, edgecolor='white', linewidth=1.5)
        max_val = max(jumlah) if max(jumlah) > 0 else 5
        ax.set_ylim(0, max_val * 1.3)
        self._clean(ax)

        val_texts = [
            ax.text(bar.get_x() + bar.get_width() / 2, 0, '',
                    ha='center', va='bottom', fontsize=10,
                    fontweight='bold', color=self.colors['text'])
            for bar in bars
        ]

        total_frames = FRAMES + (n - 1) * STAGGER
        canvas = self._canvas(fig)
        canvas.hovered_idx = -1

        def animate(frame):
            for i, bar in enumerate(bars):
                eff = max(0, frame - i * STAGGER)
                p   = min(eff / FRAMES, 1.0)
                prg = 1 - (1 - p) ** 3
                h   = jumlah[i] * prg
                bar.set_height(h)
                val_texts[i].set_position(
                    (bar.get_x() + bar.get_width() / 2, h + max_val * 0.02))
                val_texts[i].set_text(str(jumlah[i]) if prg > 0.85 else '')
            canvas.draw_idle()
            if frame >= total_frames:
                if hasattr(canvas, '_anim') and canvas._anim:
                    canvas._anim.event_source.stop()
                canvas.mpl_connect("motion_notify_event", on_hover)

        def on_hover(event):
            if event.inaxes != ax:
                if canvas.hovered_idx != -1:
                    for i, b in enumerate(bars):
                        b.set_facecolor(colors_bar[i])
                        b.set_alpha(1.0)
                    canvas.hovered_idx = -1
                    canvas.draw_idle()
                return
            found = next((i for i, b in enumerate(bars) if b.contains(event)[0]), -1)
            if found != canvas.hovered_idx:
                canvas.hovered_idx = found
                for i, b in enumerate(bars):
                    b.set_facecolor(colors_bar[i])
                    b.set_alpha(0.65 if (found >= 0 and i != found) else 1.0)
                canvas.draw_idle()

        if use_animations:
            a = self._anim(fig, animate, total_frames + 1)
            canvas._anim = a
        else:
            canvas._anim = None
            animate(total_frames)
        return canvas

    # ─────────────────────────────────────────────────────────────────
    # 6. TREND LINE GENRE PER TAHUN — LEBAR PENUH
    # ─────────────────────────────────────────────────────────────────
    def create_trendline_genre_tahun(self, data_trend=None, use_animations=True):
        if not data_trend:
            data_trend = {
                'Fiksi'    : {1990: 5,  2000: 12, 2010: 25, 2020: 18},
                'Non-Fiksi': {1990: 3,  2000: 8,  2010: 15, 2020: 22},
            }

        all_years = sorted({y for d in data_trend.values() for y in d.keys()})
        FRAMES    = 22

        fig = self._fig(w=12, h=4)
        ax  = fig.add_subplot(111)

        line_objs = []
        for idx, (genre, yd) in enumerate(data_trend.items()):
            color = _PALETTE[idx % len(_PALETTE)]
            ys    = [yd.get(y, 0) for y in all_years]
            ln, = ax.plot([], [], color=color, linewidth=2.5,
                          marker='o', markersize=6, label=genre,
                          zorder=3, solid_capstyle='round')
            line_objs.append((ln, all_years, ys))

        max_val = max(v for d in data_trend.values() for v in d.values()) if data_trend else 10
        ax.set_ylim(0, max_val * 1.3)
        ax.set_xlim(min(all_years) - 3, max(all_years) + 3)
        self._clean(ax, show_left=True)
        ax.grid(axis='y', linestyle='--', alpha=0.35, color='#CBD5E1')
        ax.grid(axis='x', linestyle=':', alpha=0.2, color='#CBD5E1')
        ax.legend(fontsize=10, framealpha=0.92, loc='upper left',
                  fancybox=True, edgecolor='#E2E8F0',
                  labelcolor=self.colors['text'])

        canvas = self._canvas(fig)

        def animate(frame):
            t     = min(frame / FRAMES, 1.0)
            p     = 1 - (1 - t) ** 2
            n_pts = max(1, round(p * len(all_years)))
            for ln, xs, ys in line_objs:
                ln.set_data(xs[:n_pts], ys[:n_pts])
            canvas.draw_idle()
            if frame >= FRAMES:
                if hasattr(canvas, '_anim') and canvas._anim:
                    canvas._anim.event_source.stop()

        if use_animations:
            a = self._anim(fig, animate, FRAMES + 1, interval=30)
            canvas._anim = a
        else:
            canvas._anim = None
            animate(FRAMES)
        return canvas