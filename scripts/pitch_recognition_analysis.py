"""
EP-TSP — Pitch Recognition: Timing Bias by Pitch Type
Emerson Performance (EP)

¿El swing de un bateador está calibrado por default a la velocidad de
fastball? Analiza la dirección del error de timing (Early/On Time/Late)
y su magnitud (miss distance) a través de 7 tipos de pitcheo, usando
datos de bat-tracking de la temporada 2026.

Uso:
    python scripts/pitch_recognition_analysis.py
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from ep_chart_style import *

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"

# Finding 1 (early-swing bias) is restricted to the three pitch types that
# actually sustain a real 100-swing-per-batter-pitch-type minimum in 2026.
# Sinker/Cutter/Slider/Sweeper were dropped: at the batter level, too few
# hitters reach 100 swings against a single one of those pitch types in a
# season, so any "league rate" for them would be a small, non-representative
# sample. See README "Correction" section for the full explanation.
MIN100_PITCH_ORDER = ["FF", "CU", "CH"]
# Full 7-type order, still used by Findings 2-4 (min65 dataset; unaffected by
# the Finding 1 correction, but see README Limitations for the same caveat).
PITCH_ORDER = ["SI", "FF", "FC", "ST", "SL", "CH", "CU"]
PITCH_LABELS = {
    "FF": "Fastball", "SI": "Sinker", "FC": "Cutter",
    "SL": "Slider", "CH": "Changeup", "ST": "Sweeper", "CU": "Curveball",
}
PITCH_LABELS_ES = {
    "FF": "Fastball", "SI": "Sinker", "FC": "Cutter",
    "SL": "Slider", "CH": "Cambio", "ST": "Sweeper", "CU": "Curva",
}

MIN_SWINGS = 100


def load_data():
    return pd.read_csv(DATA_DIR / "swing_timing_season.csv")


def load_min100_data():
    df = pd.read_csv(DATA_DIR / "swing_timing_season_min100.csv")
    # Defense in depth: enforce the minimum in code too, don't just trust the export.
    return df[df["n_swings"] >= MIN_SWINGS]


def plot_early_bias(df: pd.DataFrame, lang: str) -> None:
    fig, ax = plt.subplots(figsize=(9, 7.5))
    apply_ep_style(fig, ax)

    labels = PITCH_LABELS if lang == "en" else PITCH_LABELS_ES
    x_labels = [labels[p] for p in MIN100_PITCH_ORDER]
    early_vals = []
    for p in MIN100_PITCH_ORDER:
        sub = df[df["api_pitch_group"] == p]
        weighted = (sub["early_percent"] * sub["n_swings"]).sum() / sub["n_swings"].sum() * 100
        early_vals.append(weighted)

    colors = [EP_COLORS["navy"] if v < 15 else EP_COLORS["gold"] if v < 30 else EP_COLORS["red"]
              for v in early_vals]

    bars = ax.bar(x_labels, early_vals, color=colors, width=0.6, zorder=3,
                   edgecolor=EP_COLORS["navy"], linewidth=1)
    for bar, v in zip(bars, early_vals):
        ax.text(bar.get_x() + bar.get_width()/2, v + 1, f"{v:.1f}%",
                ha="center", fontsize=10.5, fontweight="bold", color=EP_COLORS["navy"],
                fontproperties=FONT_LABEL if FONT_LABEL else None)

    if lang == "en":
        style_axis_label(ax, "y", "SWINGS ARRIVING EARLY (%)")
        add_finding_title(fig, ax, "Swings Are Fastball-Calibrated by Default",
            "League-wide 2026, min. 100 swings/batter-pitch-type — 3 pitch types with sufficient batter-level volume")
        add_source(fig, "Source: Baseball Savant Bat Tracking Swing Timing, 2026")
        fname = OUTPUT_DIR / "early_bias_EN.png"
    else:
        style_axis_label(ax, "y", "SWINGS QUE LLEGAN ADELANTADOS (%)")
        add_finding_title(fig, ax, "El Swing Está Calibrado por Default a Fastball",
            "Liga completa 2026, mín. 100 swings/bateador-pitch-type — 3 tipos con volumen suficiente a nivel bateador")
        add_source(fig, "Fuente: Bat Tracking Swing Timing de Baseball Savant, 2026")
        fname = OUTPUT_DIR / "early_bias_ES.png"

    fig.tight_layout(rect=[0, 0.01, 1, 1])
    plt.savefig(fname, dpi=200, facecolor=EP_COLORS["off_white"])
    plt.close(fig)
    print(f"Guardado: {fname}")


def plot_miss_distance_vs_whiff(df: pd.DataFrame, lang: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 7.5))
    apply_ep_style(fig, ax)

    labels = PITCH_LABELS if lang == "en" else PITCH_LABELS_ES
    rs = []
    for p in PITCH_ORDER:
        sub = df[df["api_pitch_type"] == p]
        if len(sub) > 10:
            r = sub["miss_distance"].corr(sub["whiff_rate"])
            rs.append((labels[p], r))

    rs_sorted = sorted(rs, key=lambda x: x[1])
    names = [x[0] for x in rs_sorted]
    vals = [x[1] for x in rs_sorted]
    colors = [EP_COLORS["navy"] if v < 0.3 else EP_COLORS["red"] for v in vals]

    ax.barh(names, vals, color=colors, height=0.6, zorder=3,
            edgecolor=EP_COLORS["navy"], linewidth=1)
    for i, v in enumerate(vals):
        ax.text(v + 0.01, i, f"r={v:.3f}", va="center", fontsize=10.5, fontweight="bold",
                color=EP_COLORS["navy"], fontproperties=FONT_LABEL if FONT_LABEL else None)

    if lang == "en":
        style_axis_label(ax, "x", "CORRELATION: MISS DISTANCE vs. WHIFF RATE")
        add_finding_title(fig, ax, "Timing Precision Against Off-Speed Predicts Whiffs Best",
            "Changeup and Slider miss distance are the strongest whiff-rate predictors")
        add_source(fig, "Source: Baseball Savant Bat Tracking Swing Timing, 2026")
        fname = OUTPUT_DIR / "miss_distance_whiff_EN.png"
    else:
        style_axis_label(ax, "x", "CORRELACIÓN: MISS DISTANCE vs. WHIFF RATE")
        add_finding_title(fig, ax, "La Precisión de Timing Contra Pitcheos Lentos Predice Mejor los Whiffs",
            "El miss distance de Cambio y Slider son los mejores predictores de whiff rate")
        add_source(fig, "Fuente: Bat Tracking Swing Timing de Baseball Savant, 2026")
        fname = OUTPUT_DIR / "miss_distance_whiff_ES.png"

    fig.tight_layout(rect=[0, 0.01, 1, 1])
    plt.savefig(fname, dpi=200, facecolor=EP_COLORS["off_white"])
    plt.close(fig)
    print(f"Guardado: {fname}")


def plot_zone_breakdown(lang: str) -> None:
    df = pd.read_csv(DATA_DIR / "swing_timing_by_zone.csv")
    zones = ["High", "Middle", "Low"]
    zones_es = {"High": "Alto", "Middle": "Medio", "Low": "Bajo"}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6.8))
    fig.patch.set_facecolor(EP_COLORS["off_white"])

    x_labels = zones if lang == "en" else [zones_es[z] for z in zones]
    early_vals = [df[df["pitchzone_height_code"] == z]["early_percent"].mean() * 100 for z in zones]
    whiff_vals = [df[df["pitchzone_height_code"] == z]["whiff_rate"].mean() * 100 for z in zones]

    for ax, vals, title_en, title_es, color in [
        (ax1, early_vals, "Early Swing %", "% Swing Adelantado", EP_COLORS["gold"]),
        (ax2, whiff_vals, "Whiff %", "% Whiff", EP_COLORS["red"]),
    ]:
        apply_ep_style(fig, ax)
        bars = ax.bar(x_labels, vals, color=color, width=0.55, zorder=3,
                       edgecolor=EP_COLORS["navy"], linewidth=1)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, v + 0.8, f"{v:.1f}%",
                    ha="center", fontsize=11, fontweight="bold", color=EP_COLORS["navy"],
                    fontproperties=FONT_LABEL if FONT_LABEL else None)
        ax.set_title(title_en if lang == "en" else title_es, fontsize=12.5,
                     color=EP_COLORS["subtitle_grey"], pad=8)

    if lang == "en":
        fig.suptitle("High Pitches Fool the Swing Plane, Low Pitches Fool the Timing",
                     fontsize=16, color=EP_COLORS["navy"], y=0.99,
                     fontproperties=FONT_TITLE if FONT_TITLE else None)
        fig.text(0.5, 0.90, "High-zone whiffs happen despite good timing; low-zone whiffs come with both bad timing and bad contact precision",
                  ha="center", fontsize=10, color=EP_COLORS["subtitle_grey"],
                  fontproperties=FONT_SUBTITLE_ITALIC if FONT_SUBTITLE_ITALIC else None)
        add_source(fig, "Source: Baseball Savant Bat Tracking Swing Timing, 2026")
        fname = OUTPUT_DIR / "zone_breakdown_EN.png"
    else:
        fig.suptitle("Pitcheos Altos Engañan el Plano de Swing, Bajos Engañan el Timing",
                     fontsize=15, color=EP_COLORS["navy"], y=0.99,
                     fontproperties=FONT_TITLE if FONT_TITLE else None)
        fig.text(0.5, 0.90, "Whiffs de zona alta ocurren pese a buen timing; whiffs de zona baja vienen con mal timing y mal miss distance",
                  ha="center", fontsize=10, color=EP_COLORS["subtitle_grey"],
                  fontproperties=FONT_SUBTITLE_ITALIC if FONT_SUBTITLE_ITALIC else None)
        add_source(fig, "Fuente: Bat Tracking Swing Timing de Baseball Savant, 2026")
        fname = OUTPUT_DIR / "zone_breakdown_ES.png"

    fig.tight_layout(rect=[0, 0.01, 1, 0.82])
    plt.savefig(fname, dpi=200, facecolor=EP_COLORS["off_white"])
    plt.close(fig)
    print(f"Guardado: {fname}")


def plot_platoon(lang: str) -> None:
    df = pd.read_csv(DATA_DIR / "swing_timing_by_platoon.csv")
    df["same_side"] = df["bat_side"] == df["pitch_hand"]

    fig, ax = plt.subplots(figsize=(9, 7))
    apply_ep_style(fig, ax)

    labels_en = ["Same Side\n(e.g. RHB vs. RHP)", "Opposite Side\n(e.g. RHB vs. LHP)"]
    labels_es = ["Mismo Lado\n(ej. RHB vs. RHP)", "Lado Opuesto\n(ej. RHB vs. LHP)"]
    labels = labels_en if lang == "en" else labels_es
    colors = [EP_COLORS["red"], EP_COLORS["green"]]

    same = df[df["same_side"]]["whiff_rate"].mean() * 100
    opp = df[~df["same_side"]]["whiff_rate"].mean() * 100

    bars = ax.bar(labels, [same, opp], color=colors, width=0.5, zorder=3,
                   edgecolor=EP_COLORS["navy"], linewidth=1.5)
    for bar, v in zip(bars, [same, opp]):
        ax.text(bar.get_x() + bar.get_width()/2, v + 0.5, f"{v:.1f}%",
                ha="center", fontsize=13, fontweight="bold", color=EP_COLORS["navy"],
                fontproperties=FONT_LABEL if FONT_LABEL else None)

    ax.set_ylim(0, 32)

    if lang == "en":
        style_axis_label(ax, "y", "WHIFF RATE (%)")
        add_finding_title(fig, ax, "The Classic Platoon Disadvantage Shows Up in Timing Too",
            "Same-handed matchups produce more whiffs and worse timing than opposite-handed ones")
        add_source(fig, "Source: Baseball Savant Bat Tracking Swing Timing, 2026")
        fname = OUTPUT_DIR / "platoon_EN.png"
    else:
        style_axis_label(ax, "y", "WHIFF RATE (%)")
        add_finding_title(fig, ax, "La Desventaja Clásica de Platoon También Se Ve en el Timing",
            "Matchups del mismo lado producen más whiffs y peor timing que los de lado opuesto")
        add_source(fig, "Fuente: Bat Tracking Swing Timing de Baseball Savant, 2026")
        fname = OUTPUT_DIR / "platoon_ES.png"

    fig.tight_layout(rect=[0, 0.01, 1, 1])
    plt.savefig(fname, dpi=200, facecolor=EP_COLORS["off_white"])
    plt.close(fig)
    print(f"Guardado: {fname}")


if __name__ == "__main__":
    df = load_data()
    df_min100 = load_min100_data()
    print(f"Filas totales (min65, 7 tipos): {len(df)}")
    print(f"Filas min100 (3 tipos): {len(df_min100)}")
    print()
    print("=== Early% por tipo de pitcheo (min 100, weighted by n_swings) ===")
    for p in MIN100_PITCH_ORDER:
        sub = df_min100[df_min100["api_pitch_group"] == p]
        weighted = (sub["early_percent"] * sub["n_swings"]).sum() / sub["n_swings"].sum() * 100
        print(f"  {p}: Early={weighted:.1f}%, n_players={len(sub)}, min_swings={sub['n_swings'].min():.0f}")

    print()
    print("=== Correlación miss_distance vs whiff_rate (Findings 2-4 still use min65 dataset) ===")
    for p in ["SI", "FF", "FC", "ST", "SL", "CH", "CU"]:
        sub = df[df["api_pitch_type"] == p]
        if len(sub) > 10:
            r = sub["miss_distance"].corr(sub["whiff_rate"])
            print(f"  {p}: r={r:.3f}")

    OUTPUT_DIR.mkdir(exist_ok=True)
    for lang in ["en", "es"]:
        plot_early_bias(df_min100, lang)
        plot_miss_distance_vs_whiff(df, lang)
        plot_zone_breakdown(lang)
        plot_platoon(lang)
