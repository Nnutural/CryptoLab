from __future__ import annotations

import csv
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = ROOT / "docs" / "report_assets" / "figures"
DATA_DIR = ROOT / "docs" / "report_assets" / "data"
QA_MD = ROOT / "docs" / "report_assets" / "FIGURE_QA.md"
R_STATUS = DATA_DIR / "r_figures_status.txt"

FIGURES = [
    ("Fig. 1", "fig1_validation_overview", ["fig1_validation_overview.csv"]),
    ("Fig. 2", "fig2_algorithm_coverage_matrix", ["fig2_algorithm_coverage_matrix.csv"]),
    ("Fig. 3", "fig3_cross_validation_evidence", ["fig3_cross_validation_evidence.csv"]),
    ("Fig. 4", "fig4_benchmark_performance", ["fig4_benchmark_raw.csv", "fig4_benchmark_summary.csv"]),
    ("Fig. 5", "fig5_aes_verbose_trace", ["fig5_aes_verbose_trace.csv"]),
    ("Fig. 6", "fig6_security_demos", ["fig6_ecb_leak_metrics.csv", "fig6_pbkdf2_iterations.csv"]),
]


def csv_rows(path: Path) -> int:
    if not path.exists():
        return -1
    with path.open("r", newline="", encoding="utf-8") as f:
        return max(sum(1 for _ in csv.reader(f)) - 1, 0)


def check_svg(path: Path) -> tuple[bool, str]:
    if not path.exists() or path.stat().st_size == 0:
        return False, "missing or empty"
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return False, f"parse error: {exc}"
    if not root.tag.lower().endswith("svg"):
        return False, f"root tag is {root.tag}"
    return True, "readable SVG"


def check_png(path: Path) -> tuple[bool, str, int, int]:
    if not path.exists() or path.stat().st_size == 0:
        return False, "missing or empty", 0, 0
    with Image.open(path) as img:
        width, height = img.size
    if width < 1800:
        return False, f"width {width}px < 1800px", width, height
    return True, f"{width}x{height}px", width, height


def main() -> None:
    r_missing = R_STATUS.exists() and "Rscript missing" in R_STATUS.read_text(encoding="utf-8", errors="replace")
    lines = [
        "# Figure QA Report",
        "",
        "检查项：文件存在且非空、SVG 可解析、PNG 宽度至少 1800 px、CSV 有数据行。文字重叠、图例遮挡和数值一致性通过脚本设计约束与人工复核说明记录。",
        "",
        "| Figure | SVG | PNG | CSV rows | Status | Notes |",
        "|---|---:|---:|---:|---|---|",
    ]
    all_ok = True
    for fig_id, stem, csv_names in FIGURES:
        svg_ok, svg_note = check_svg(FIG_DIR / f"{stem}.svg")
        png_ok, png_note, _width, _height = check_png(FIG_DIR / f"{stem}.png")
        row_counts = {name: csv_rows(DATA_DIR / name) for name in csv_names}
        csv_ok = all(count > 0 for count in row_counts.values())
        r_not_run = fig_id in {"Fig. 2", "Fig. 3"} and r_missing
        ok = svg_ok and png_ok and csv_ok
        all_ok = all_ok and ok
        csv_summary = "; ".join(f"{name}={count}" for name, count in row_counts.items())
        status = "PASS" if ok else ("NOT RUN" if r_not_run else "FAIL")
        notes = "R runtime/package missing; Python fallback intentionally not used" if r_not_run else "backend-specific script output"
        lines.append(
            f"| {fig_id} | {svg_note} | {png_note} | {csv_summary} | {status} | {notes} |"
        )

    lines.extend(
        [
            "",
            "## Visual QA Notes",
            "",
            "- 所有 Python 图显式设置 sans-serif 字体、`svg.fonttype=none`、线宽和克制配色。",
            "- R 图由 R 脚本使用 ggplot2/patchwork/svglite/ragg 输出；未用 Python 替代渲染。",
            "- 所有坐标轴包含单位或明确计数含义。",
            "- 未使用彩虹色板；红绿不作为唯一编码，状态图同时使用文字标签。",
            "- PNG 作为报告预览图，SVG 作为可编辑主图。",
            f"- Overall status: {'PASS' if all_ok else 'FAIL'}",
        ]
    )
    if r_missing:
        lines.extend(
            [
                "",
                "## Missing Runtime",
                "",
                f"- R figures not executed: `{R_STATUS.relative_to(ROOT)}` records `Rscript missing`; this follows the backend exclusivity rule.",
            ]
        )
    QA_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(QA_MD)
    if not all_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
