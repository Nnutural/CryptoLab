from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIGURE_DIR = PROJECT_ROOT / "docs" / "report_assets" / "figures"
DATA_DIR = PROJECT_ROOT / "docs" / "report_assets" / "data"

PALETTE = {
    "blue": "#2F5D8C",
    "blue_light": "#8FB3D9",
    "teal": "#3C8D8F",
    "green": "#5C9E6E",
    "gold": "#D6A64A",
    "orange": "#C8754A",
    "red": "#B85C5C",
    "purple": "#7A6DAA",
    "gray_dark": "#333333",
    "gray": "#7A7A7A",
    "gray_light": "#D8D8D8",
    "gray_faint": "#F2F2F2",
}


def set_nature_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 7.0,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.7,
            "axes.edgecolor": "#333333",
            "axes.labelcolor": "#333333",
            "xtick.color": "#333333",
            "ytick.color": "#333333",
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "legend.frameon": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )


def panel_label(ax: mpl.axes.Axes, label: str, x: float = -0.12, y: float = 1.05) -> None:
    ax.text(
        x,
        y,
        label,
        transform=ax.transAxes,
        fontsize=8.5,
        fontweight="bold",
        va="top",
        ha="left",
        color="#111111",
    )


def save_svg_png(fig: mpl.figure.Figure, stem: str, width_px_min: int = 1800) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    svg_path = FIGURE_DIR / f"{stem}.svg"
    png_path = FIGURE_DIR / f"{stem}.png"
    fig.savefig(svg_path, bbox_inches="tight")
    width_in = fig.get_size_inches()[0]
    dpi = max(300, int(width_px_min / max(width_in, 1)))
    fig.savefig(png_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)

