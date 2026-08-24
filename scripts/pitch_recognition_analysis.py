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

PITCH_ORDER = ["SI", "FF", "FC", "ST", "SL", "CH", "CU"]
PITCH_LABELS = {
    "FF": "Fastball", "SI": "Sinker", "FC": "Cutter",
    "SL": "Slider", "CH": "Changeup", "ST": "Sweeper", "CU": "Curveball",
}
PITCH_LABELS_ES = {
    "FF": "Fastball", "SI": "Sinker", "FC": "Cutter",
    "SL": "Slider", "CH": "Cambio", "ST": "Sweeper", "CU": "Curva",
}


def load_data():
    return pd.read_csv(DATA_DIR / "swing_timing_season.csv")


def plot_early_bias(df: pd.DataFrame, lang: str) -> None:
    fig, ax = plt.subplots(figsize=(11, 7.5))
    apply_ep_style(fig, ax)

    labels = PITCH_LABELS if lang == "en" else PITCH_LABELS_ES
    x_labels = [labels[p] for p in PITCH_ORDER]
    early_vals = [df[df["api_pitch_type"] == p]["early_percent"].mean() * 100 for p in PITCH_ORDER]

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
            "League-wide 2026 — 'Early' swing rate rises sharply as pitch speed/deception increases")
        add_source(fig, "Source: Baseball Savant Bat Tracking Swing Timing, 2026")
        fname = OUTPUT_DIR / "early_bias_EN.png"
    else:
        style_axis_label(ax, "y", "SWINGS QUE LLEGAN ADELANTADOS (%)")
        add_finding_title(fig, ax, "El Swing Está Calibrado por Default a Fastball",
            "Liga completa 2026 — la tasa de swings 'adelantados' sube fuerte con menos velocidad/más quiebre")
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


if __name__ == "__main__":
    df = load_data()
    print(f"Filas totales: {len(df)}")
    print()
    print("=== Early% por tipo de pitcheo ===")
    for p in PITCH_ORDER:
        sub = df[df["api_pitch_type"] == p]
        print(f"  {p}: Early={sub['early_percent'].mean()*100:.1f}%, n={len(sub)}")

    print()
    print("=== Correlación miss_distance vs whiff_rate ===")
    for p in PITCH_ORDER:
        sub = df[df["api_pitch_type"] == p]
        if len(sub) > 10:
            r = sub["miss_distance"].corr(sub["whiff_rate"])
            print(f"  {p}: r={r:.3f}")

    OUTPUT_DIR.mkdir(exist_ok=True)
    for lang in ["en", "es"]:
        plot_early_bias(df, lang)
        plot_miss_distance_vs_whiff(df, lang)
