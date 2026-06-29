from __future__ import annotations

import csv
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

from figure_style import DATA_DIR, PALETTE, panel_label, save_svg_png, set_nature_style


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs" / "progress_evidence"
OUT_CSV = DATA_DIR / "fig1_validation_overview.csv"


def read(name: str) -> str:
    return (EVIDENCE / name).read_text(encoding="utf-8", errors="replace")


def parse_cargo(text: str) -> dict[str, int]:
    match = re.search(r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored", text)
    if not match:
        raise ValueError("Could not parse cargo test summary")
    passed, failed, ignored = map(int, match.groups())
    return {"passed": passed, "failed": failed, "ignored": ignored}


def parse_pytest(text: str) -> dict[str, int]:
    match = re.search(r"(\d+) passed(?:, (\d+) deselected)?", text)
    if not match:
        raise ValueError("Could not parse pytest summary")
    passed = int(match.group(1))
    deselected = int(match.group(2) or 0)
    failed_match = re.search(r"(\d+) failed", text)
    failed = int(failed_match.group(1)) if failed_match else 0
    return {"passed": passed, "failed": failed, "deselected": deselected}


def status_from_tail(text: str, success_markers: list[str], failure_markers: list[str]) -> str:
    lowered = text.lower()
    if any(marker.lower() in lowered for marker in failure_markers):
        return "blocked"
    if any(marker.lower() in lowered for marker in success_markers):
        return "passed"
    return "partial"


def write_data() -> tuple[dict[str, int], dict[str, int], list[dict[str, str]]]:
    cargo = parse_cargo(read("20_cargo_test_tail.txt"))
    pytest = parse_pytest(read("21_pytest_tail.txt"))
    npm_test = read("22_frontend_npm_test_tail.txt")
    npm_build = read("23_frontend_build_tail.txt")
    docker = read("24_docker_build_tail.txt")

    statuses = [
        {
            "layer": "Rust core",
            "check": "cargo test",
            "status": "passed" if cargo["failed"] == 0 else "failed",
            "evidence": f'{cargo["passed"]} passed; {cargo["failed"]} failed; {cargo["ignored"]} ignored',
        },
        {
            "layer": "API",
            "check": "pytest",
            "status": "passed" if pytest["failed"] == 0 else "failed",
            "evidence": f'{pytest["passed"]} passed; {pytest["failed"]} failed; {pytest["deselected"]} deselected',
        },
        {
            "layer": "Frontend",
            "check": "npm run build",
            "status": status_from_tail(npm_build, ["built in", "✓ built"], ["error", "failed"]),
            "evidence": "build succeeded with Vite chunk warning",
        },
        {
            "layer": "Docker",
            "check": "docker compose build",
            "status": status_from_tail(docker, ["successfully built"], ["daemon is not running", "error during connect"]),
            "evidence": "blocked by Docker daemon availability",
        },
        {
            "layer": "Frontend",
            "check": "npm test",
            "status": status_from_tail(npm_test, ["tsc -b", "passed"], ["missing script", "error"]),
            "evidence": "TypeScript test script state from archived output",
        },
    ]

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["figure_panel", "metric", "category", "value", "status", "evidence"])
        writer.writeheader()
        for row in statuses:
            writer.writerow(
                {
                    "figure_panel": "A" if row["check"] != "npm test" else "D",
                    "metric": row["check"],
                    "category": row["layer"],
                    "value": "",
                    "status": row["status"],
                    "evidence": row["evidence"],
                }
            )
        for key, value in cargo.items():
            writer.writerow(
                {
                    "figure_panel": "B",
                    "metric": "cargo test",
                    "category": key,
                    "value": value,
                    "status": "",
                    "evidence": "docs/progress_evidence/20_cargo_test_tail.txt",
                }
            )
        for key, value in pytest.items():
            writer.writerow(
                {
                    "figure_panel": "C",
                    "metric": "pytest",
                    "category": key,
                    "value": value,
                    "status": "",
                    "evidence": "docs/progress_evidence/21_pytest_tail.txt",
                }
            )
    return cargo, pytest, statuses


def stacked_bar(ax, counts: dict[str, int], order: list[str], colors: dict[str, str], title: str) -> None:
    left = 0
    total = sum(counts.get(k, 0) for k in order)
    for key in order:
        value = counts.get(key, 0)
        if value == 0:
            continue
        ax.barh([0], [value], left=left, color=colors[key], edgecolor="white", linewidth=0.8, height=0.42)
        ax.text(
            left + value / 2,
            0,
            str(value),
            ha="center",
            va="center",
            fontsize=7,
            color="white" if key in {"passed"} else "#222222",
            fontweight="bold" if key == "passed" else "normal",
        )
        left += value
    ax.set_xlim(0, max(total, 1))
    ax.set_yticks([])
    ax.set_xlabel("test cases (count)")
    ax.set_title(title, loc="left", fontsize=8, fontweight="bold")
    ax.grid(axis="x", color="#E6E6E6", linewidth=0.5)
    labels = [f"{key}: {counts.get(key, 0)}" for key in order]
    ax.text(0, -0.55, "  ".join(labels), ha="left", va="center", fontsize=6.4, color=PALETTE["gray_dark"])


def plot() -> None:
    cargo, pytest, statuses = write_data()
    set_nature_style()
    fig = plt.figure(figsize=(7.2, 4.7))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.18, 1], height_ratios=[1.05, 1], wspace=0.35, hspace=0.58)

    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    status_rows = [row for row in statuses if row["check"] != "npm test"]
    color_by_status = {"passed": PALETTE["blue"], "partial": PALETTE["gold"], "blocked": PALETTE["orange"], "failed": PALETTE["red"]}
    label_by_status = {"passed": "PASS", "partial": "PARTIAL", "blocked": "BLOCKED", "failed": "FAIL"}
    ax_a.set_xlim(0, 4)
    ax_a.set_ylim(0, 1)
    for i, row in enumerate(status_rows):
        rect = Rectangle((i + 0.05, 0.18), 0.9, 0.58, facecolor=color_by_status[row["status"]], edgecolor="white", linewidth=1)
        ax_a.add_patch(rect)
        ax_a.text(i + 0.5, 0.51, label_by_status[row["status"]], ha="center", va="center", fontsize=7, color="white", fontweight="bold")
        ax_a.text(i + 0.5, 0.08, row["layer"], ha="center", va="top", fontsize=6.7, color="#222222")
        ax_a.text(i + 0.5, 0.84, row["check"], ha="center", va="bottom", fontsize=5.8, color=PALETTE["gray_dark"])
    ax_a.set_axis_off()
    ax_a.set_title("Validation status by layer", loc="left", fontsize=8, fontweight="bold")
    panel_label(ax_a, "a", x=-0.04)

    stacked_bar(
        ax_b,
        cargo,
        ["passed", "failed", "ignored"],
        {"passed": PALETTE["blue"], "failed": PALETTE["red"], "ignored": PALETTE["gray_light"]},
        "Rust cargo test",
    )
    panel_label(ax_b, "b")

    stacked_bar(
        ax_c,
        pytest,
        ["passed", "failed", "deselected"],
        {"passed": PALETTE["teal"], "failed": PALETTE["red"], "deselected": PALETTE["gray_light"]},
        "API pytest",
    )
    panel_label(ax_c, "c", x=-0.08)

    frontend_rows = [row for row in statuses if row["layer"] == "Frontend"]
    y = np.arange(len(frontend_rows))
    colors = [color_by_status[row["status"]] for row in frontend_rows]
    ax_d.barh(y, [1] * len(frontend_rows), color=colors, edgecolor="white", linewidth=0.8, height=0.46)
    for yi, row in zip(y, frontend_rows):
        ax_d.text(0.5, yi, label_by_status[row["status"]], ha="center", va="center", fontsize=7, color="white", fontweight="bold")
    ax_d.set_yticks(y)
    ax_d.set_yticklabels([row["check"] for row in frontend_rows])
    ax_d.set_xlim(0, 1)
    ax_d.set_xticks([])
    ax_d.set_xlabel("binary command status")
    ax_d.set_title("Frontend command checks", loc="left", fontsize=8, fontweight="bold")
    ax_d.invert_yaxis()
    panel_label(ax_d, "d")

    fig.suptitle("Test and build validation overview", x=0.02, y=0.995, ha="left", fontsize=9, fontweight="bold")
    save_svg_png(fig, "fig1_validation_overview")


if __name__ == "__main__":
    plot()

