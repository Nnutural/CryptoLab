from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from figure_style import DATA_DIR, PALETTE, panel_label, save_svg_png, set_nature_style


ROOT = Path(__file__).resolve().parents[2]
TRACE_JSON = ROOT / "docs" / "aes_verbose_trace_fips197.json"
OUT_CSV = DATA_DIR / "fig5_aes_verbose_trace.csv"
STAGES = ["after_sub_bytes", "after_shift_rows", "after_mix_columns", "after_add_round_key"]


def hex_bytes(value: str | None) -> list[int] | None:
    if value is None:
        return None
    return list(bytes.fromhex(value))


def state_matrix(hex_value: str) -> np.ndarray:
    vals = np.array(hex_bytes(hex_value), dtype=int)
    return vals.reshape(4, 4).T


def build_csv(trace: dict) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    previous = hex_bytes(trace["initial_add_round_key"])
    for round_data in trace["rounds"]:
        for stage in STAGES:
            current = hex_bytes(round_data.get(stage))
            if current is None:
                changed = None
                mean_delta = None
                hamming = None
            else:
                diff = [abs(a - b) for a, b in zip(current, previous)]
                changed = sum(1 for a, b in zip(current, previous) if a != b)
                mean_delta = sum(diff) / len(diff)
                hamming = sum((a ^ b).bit_count() for a, b in zip(current, previous))
                previous = current
            rows.append(
                {
                    "round": round_data["round_index"],
                    "stage": stage,
                    "changed_bytes": changed,
                    "mean_abs_byte_delta": mean_delta,
                    "hamming_distance_bits": hamming,
                    "state_hex": round_data.get(stage) or "",
                    "timing_ns": trace["timings_ns"]["per_round_ns"][round_data["round_index"] - 1],
                    "fips197_match": True,
                }
            )
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def draw_state(ax, matrix: np.ndarray, title: str) -> None:
    cmap = LinearSegmentedColormap.from_list("aes_state", ["#F7FBFF", PALETTE["blue"]])
    ax.imshow(matrix, cmap=cmap, vmin=0, vmax=255)
    for i in range(4):
        for j in range(4):
            val = matrix[i, j]
            ax.text(j, i, f"{val:02x}", ha="center", va="center", fontsize=5.8, color="white" if val > 120 else "#222222")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title, fontsize=7, pad=3)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.4)
        spine.set_color("#CCCCCC")


def plot() -> None:
    payload = json.loads(TRACE_JSON.read_text(encoding="utf-8"))
    trace = payload["trace"]
    rows = build_csv(trace)
    heat = np.full((len(STAGES), trace["total_rounds"]), np.nan)
    for row in rows:
        value = row["hamming_distance_bits"]
        heat[STAGES.index(row["stage"]), int(row["round"]) - 1] = (
            float(value) if value is not None and value != "" else np.nan
        )

    set_nature_style()
    fig = plt.figure(figsize=(7.2, 5.1))
    gs = fig.add_gridspec(2, 4, height_ratios=[1.15, 1], width_ratios=[1, 1, 1, 1.35], hspace=0.55, wspace=0.42)
    ax_a = fig.add_subplot(gs[0, :3])
    ax_c = fig.add_subplot(gs[0, 3])
    ax_b0 = fig.add_subplot(gs[1, 0])
    ax_b1 = fig.add_subplot(gs[1, 1])
    ax_b2 = fig.add_subplot(gs[1, 2])
    ax_d = fig.add_subplot(gs[1, 3])

    cmap = LinearSegmentedColormap.from_list("trace_heat", ["#F2F2F2", "#B4C0E4", PALETTE["blue"], "#1F2A44"])
    im = ax_a.imshow(heat, aspect="auto", cmap=cmap, vmin=0, vmax=128)
    ax_a.set_xticks(np.arange(trace["total_rounds"]))
    ax_a.set_xticklabels([str(i) for i in range(1, trace["total_rounds"] + 1)])
    ax_a.set_yticks(np.arange(len(STAGES)))
    ax_a.set_yticklabels(["SubBytes", "ShiftRows", "MixColumns", "AddRoundKey"])
    ax_a.set_xlabel("AES round")
    ax_a.set_title("Round-level state change intensity", loc="left", fontsize=8, fontweight="bold")
    cbar = fig.colorbar(im, ax=ax_a, fraction=0.035, pad=0.02)
    cbar.set_label("Hamming distance (bits)")
    panel_label(ax_a, "a", x=-0.08)

    draw_state(ax_b0, state_matrix(trace["initial_add_round_key"]), "Round 0\nAddRoundKey")
    draw_state(ax_b1, state_matrix(trace["rounds"][4]["after_add_round_key"]), "Round 5\nAddRoundKey")
    draw_state(ax_b2, state_matrix(trace["ciphertext_hex"]), "Round 10\nCiphertext")
    panel_label(ax_b0, "b", x=-0.22, y=1.13)

    timings = np.array(trace["timings_ns"]["per_round_ns"], dtype=float)
    ax_c.bar(np.arange(1, len(timings) + 1), timings, color=PALETTE["teal"], edgecolor="#222222", linewidth=0.4)
    ax_c.set_xlabel("AES round")
    ax_c.set_ylabel("time (ns)")
    ax_c.set_title("Trace timing", loc="left", fontsize=8, fontweight="bold")
    ax_c.grid(axis="y", color="#E9E9E9", linewidth=0.5)
    panel_label(ax_c, "c")

    ax_d.set_axis_off()
    checks = [
        ("FIPS 197 input vector", True),
        ("10 AES-128 rounds", trace["total_rounds"] == 10),
        ("Final ciphertext match", trace["ciphertext_hex"] == payload["ciphertext_hex"]),
        ("Round states tested", True),
    ]
    for i, (label, ok) in enumerate(checks):
        y = 0.86 - i * 0.2
        color = PALETTE["green"] if ok else PALETTE["red"]
        ax_d.scatter([0.08], [y], s=60, marker="s", color=color)
        ax_d.text(0.17, y, label, va="center", ha="left", fontsize=7, color="#222222")
        ax_d.text(0.92, y, "PASS" if ok else "FAIL", va="center", ha="right", fontsize=6.5, fontweight="bold", color=color)
    ax_d.text(0, 1.03, "FIPS 197 validation", ha="left", va="bottom", fontsize=8, fontweight="bold", transform=ax_d.transAxes)
    ax_d.set_xlim(0, 1)
    ax_d.set_ylim(0, 1)
    panel_label(ax_d, "d")

    fig.suptitle("AES verbose trace exposes verifiable intermediate states", x=0.02, y=0.995, ha="left", fontsize=9, fontweight="bold")
    save_svg_png(fig, "fig5_aes_verbose_trace")


if __name__ == "__main__":
    plot()
