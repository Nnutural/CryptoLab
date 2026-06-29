from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw

from figure_style import DATA_DIR, PALETTE, panel_label, save_svg_png, set_nature_style


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "api_server"))
ECB_CSV = DATA_DIR / "fig6_ecb_leak_metrics.csv"
PBKDF2_CSV = DATA_DIR / "fig6_pbkdf2_iterations.csv"


def synthetic_image(size: int = 192) -> Image.Image:
    img = Image.new("RGB", (size, size), "#F4F4F4")
    draw = ImageDraw.Draw(img)
    block = 16
    for y in range(0, size, block):
        for x in range(0, size, block):
            fill = "#2F5D8C" if (x // block + y // block) % 2 == 0 else "#EDE7D1"
            draw.rectangle([x, y, x + block - 1, y + block - 1], fill=fill)
    draw.rectangle([40, 40, 152, 152], outline="#B85C5C", width=12)
    draw.rectangle([72, 72, 120, 120], fill="#5C9E6E")
    for offset in range(0, size, 32):
        draw.line([0, offset, size, offset], fill="#FFFFFF", width=2)
        draw.line([offset, 0, offset, size], fill="#FFFFFF", width=2)
    return img


def duplicate_block_ratio(data: bytes) -> tuple[int, float]:
    blocks = [data[i : i + 16] for i in range(0, len(data), 16)]
    return len(blocks), (len(blocks) - len(set(blocks))) / max(len(blocks), 1)


def encrypt_images() -> tuple[np.ndarray, np.ndarray, np.ndarray, list[dict[str, object]]]:
    import cryptolab_core

    original = synthetic_image()
    raw = original.tobytes()
    padded = raw + (b"\x00" * ((16 - (len(raw) % 16)) % 16))
    key = bytes.fromhex("00112233445566778899aabbccddeeff")
    ecb = bytes(cryptolab_core.aes_encrypt(padded, key, "ECB", None, None, "None"))
    cbc = bytes(cryptolab_core.aes_encrypt(padded, key, "CBC", b"\x00" * 16, None, "None"))
    ecb_img = Image.frombytes("RGB", original.size, ecb[: len(raw)])
    cbc_img = Image.frombytes("RGB", original.size, cbc[: len(raw)])
    original_padded = raw + (b"\x00" * ((16 - (len(raw) % 16)) % 16))
    rows = []
    for label, data in [("source RGB blocks", original_padded), ("AES-ECB ciphertext", ecb), ("AES-CBC ciphertext", cbc)]:
        count, ratio = duplicate_block_ratio(data)
        rows.append({"image": label, "block_count": count, "duplicate_block_ratio": ratio})
    with ECB_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return np.array(original), np.array(ecb_img), np.array(cbc_img), rows


def measure_pbkdf2() -> list[dict[str, object]]:
    import cryptolab_core

    iterations_list = [1_000, 3_000, 10_000, 30_000, 100_000]
    repeats = 5
    rows: list[dict[str, object]] = []
    password = b"cryptolab-demo-password"
    salt = bytes.fromhex("73616c747361")
    for iterations in iterations_list:
        for repeat in range(1, repeats + 1):
            start = time.perf_counter_ns()
            derived = cryptolab_core.pbkdf2_hmac_sha256(password, salt, iterations, 32)
            duration_ms = (time.perf_counter_ns() - start) / 1_000_000
            rows.append(
                {
                    "iterations": iterations,
                    "repeat": repeat,
                    "duration_ms": duration_ms,
                    "derived_key_prefix": bytes(derived).hex()[:16],
                    "note": "real cryptolab_core.pbkdf2_hmac_sha256 call",
                }
            )
    with PBKDF2_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def plot() -> None:
    source, ecb, cbc, ecb_rows = encrypt_images()
    pbkdf2_rows = measure_pbkdf2()
    set_nature_style()
    fig = plt.figure(figsize=(7.2, 5.1))
    gs = fig.add_gridspec(2, 4, height_ratios=[1.05, 1], width_ratios=[1, 1, 1, 1.08], hspace=0.42, wspace=0.28)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[0, 2])
    ax_d = fig.add_subplot(gs[0, 3])
    ax_e = fig.add_subplot(gs[1, :])

    for ax, image, title, label in [
        (ax_a, source, "Source", "a"),
        (ax_b, ecb, "AES-ECB", "b"),
        (ax_c, cbc, "AES-CBC", "c"),
    ]:
        ax.imshow(image)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(title, fontsize=8, fontweight="bold")
        panel_label(ax, label, x=-0.08, y=1.08)

    labels = [row["image"].replace(" ciphertext", "").replace(" blocks", "") for row in ecb_rows]
    ratios = [float(row["duplicate_block_ratio"]) for row in ecb_rows]
    colors = [PALETTE["gray"], PALETTE["orange"], PALETTE["blue"]]
    ax_d.barh(np.arange(len(labels)), ratios, color=colors, edgecolor="#222222", linewidth=0.45, height=0.5)
    ax_d.set_yticks(np.arange(len(labels)))
    ax_d.set_yticklabels(labels, fontsize=6.2)
    ax_d.set_xlabel("duplicate block ratio")
    ax_d.set_xlim(0, max(ratios) * 1.18 if ratios else 1)
    ax_d.set_title("Block repetition", loc="left", fontsize=8, fontweight="bold")
    ax_d.grid(axis="x", color="#E9E9E9", linewidth=0.5)
    for i, ratio in enumerate(ratios):
        ax_d.text(ratio, i, f" {ratio:.2f}", va="center", ha="left", fontsize=6.2)
    panel_label(ax_d, "d")

    iter_values = sorted({int(row["iterations"]) for row in pbkdf2_rows})
    means = []
    mins = []
    maxs = []
    for iterations in iter_values:
        vals = [float(row["duration_ms"]) for row in pbkdf2_rows if int(row["iterations"]) == iterations]
        means.append(float(np.mean(vals)))
        mins.append(float(np.min(vals)))
        maxs.append(float(np.max(vals)))
        ax_e.scatter([iterations] * len(vals), vals, color=PALETTE["teal"], s=14, alpha=0.62, linewidths=0)
    ax_e.plot(iter_values, means, color=PALETTE["teal"], marker="o", linewidth=1.4, markersize=3.5)
    ax_e.fill_between(iter_values, mins, maxs, color=PALETTE["teal"], alpha=0.16, linewidth=0)
    ax_e.set_xscale("log")
    ax_e.set_yscale("log")
    ax_e.set_xlabel("PBKDF2 iterations (log scale)")
    ax_e.set_ylabel("duration (ms, log scale)")
    ax_e.set_title("PBKDF2 iteration impact", loc="left", fontsize=8, fontweight="bold")
    ax_e.grid(axis="both", color="#E9E9E9", linewidth=0.5, which="both")
    panel_label(ax_e, "e", x=-0.045)

    fig.suptitle("Script-reproducible vulnerability demo results", x=0.02, y=0.995, ha="left", fontsize=9, fontweight="bold")
    save_svg_png(fig, "fig6_security_demos")


if __name__ == "__main__":
    plot()

