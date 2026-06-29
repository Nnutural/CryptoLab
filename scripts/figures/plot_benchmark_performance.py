from __future__ import annotations

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from figure_style import DATA_DIR, PALETTE, panel_label, save_svg_png, set_nature_style


RAW_CSV = DATA_DIR / "fig4_benchmark_raw.csv"
SUMMARY_CSV = DATA_DIR / "fig4_benchmark_summary.csv"


def bar_with_points(ax, raw: pd.DataFrame, summary: pd.DataFrame, labels: list[str], metric: str, ylabel: str, title: str, color: str) -> None:
    xs = np.arange(len(labels))
    means = [summary.loc[summary["label"] == label, "mean"].iloc[0] for label in labels]
    mins = [summary.loc[summary["label"] == label, "min"].iloc[0] for label in labels]
    maxs = [summary.loc[summary["label"] == label, "max"].iloc[0] for label in labels]
    yerr = np.array([[m - lo for m, lo in zip(means, mins)], [hi - m for m, hi in zip(means, maxs)]])
    ax.bar(xs, means, yerr=yerr, color=color, edgecolor="#222222", linewidth=0.5, capsize=2.5, width=0.64, alpha=0.88)
    for i, label in enumerate(labels):
        vals = raw.loc[raw["label"] == label, metric].astype(float).to_numpy()
        offsets = np.linspace(-0.16, 0.16, len(vals)) if len(vals) > 1 else np.array([0])
        ax.scatter(np.full_like(vals, xs[i], dtype=float) + offsets, vals, s=12, color="#222222", alpha=0.72, linewidths=0, zorder=5)
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", fontsize=8, fontweight="bold")
    ax.grid(axis="y", color="#E9E9E9", linewidth=0.5)


def plot() -> None:
    if not RAW_CSV.exists() or not SUMMARY_CSV.exists():
        raise FileNotFoundError("Run scripts/figures/run_benchmarks.py first")
    raw = pd.read_csv(RAW_CSV)
    summary = pd.read_csv(SUMMARY_CSV)
    set_nature_style()
    fig = plt.figure(figsize=(7.2, 5.1))
    gs = fig.add_gridspec(2, 2, hspace=0.56, wspace=0.38)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    bar_with_points(
        ax_a,
        raw,
        summary,
        ["AES ECB", "AES GCM", "SM4 ECB", "RC6 ECB"],
        "throughput_mb_per_s",
        "throughput (MiB/s)",
        "Symmetric encryption throughput",
        PALETTE["blue"],
    )
    panel_label(ax_a, "a")

    bar_with_points(
        ax_b,
        raw,
        summary,
        ["SHA1", "SHA256", "SHA512", "SHA3-256", "RIPEMD160"],
        "throughput_mb_per_s",
        "throughput (MiB/s)",
        "Hash throughput",
        PALETTE["teal"],
    )
    panel_label(ax_b, "b")

    pk_labels = ["RSA encrypt", "RSA decrypt", "RSA sign", "RSA verify", "ECDSA sign", "ECDSA verify"]
    pk = summary[summary["label"].isin(pk_labels)].copy()
    xs = np.arange(len(pk_labels))
    for i, label in enumerate(pk_labels):
        vals = raw.loc[raw["label"] == label, "ms_per_op"].astype(float).to_numpy()
        offsets = np.linspace(-0.13, 0.13, len(vals))
        ax_c.scatter(np.full_like(vals, xs[i], dtype=float) + offsets, vals, s=18, color=PALETTE["purple"], alpha=0.75, linewidths=0)
        median = pk.loc[pk["label"] == label, "median"].iloc[0]
        ax_c.hlines(median, i - 0.24, i + 0.24, color="#222222", linewidth=1.1)
    ax_c.set_yscale("log")
    ax_c.set_xticks(xs)
    ax_c.set_xticklabels(pk_labels, rotation=35, ha="right")
    ax_c.set_ylabel("time (ms/op, log scale)")
    ax_c.set_title("Public-key operation latency", loc="left", fontsize=8, fontweight="bold")
    ax_c.grid(axis="y", color="#E9E9E9", linewidth=0.5, which="both")
    panel_label(ax_c, "c")

    bar_with_points(
        ax_d,
        raw,
        summary,
        ["HMAC-SHA256", "PBKDF2-HMAC-SHA256"],
        "ms_per_op",
        "time (ms/op)",
        "MAC and KDF cost",
        PALETTE["gold"],
    )
    ax_d.set_yscale("log")
    panel_label(ax_d, "d")

    fig.suptitle("Benchmark performance from repeated in-process measurements", x=0.02, y=0.995, ha="left", fontsize=9, fontweight="bold")
    save_svg_png(fig, "fig4_benchmark_performance")


if __name__ == "__main__":
    plot()

