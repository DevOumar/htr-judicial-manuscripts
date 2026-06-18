import argparse
import json
import sys
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List

import matplotlib.pyplot as plt

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))


def _center(line: Dict[str, Any]) -> tuple[float, float]:
    bbox = line.get("bbox")
    if bbox:
        return (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
    points = line.get("polygon", [])
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return mean(xs), mean(ys)


def analyze_page(page_dir: Path, output_dir: Path) -> Dict[str, Any]:
    lines = json.load((page_dir / "transcriptions.json").open("r", encoding="utf-8"))
    rows = []
    backward_y_jumps = 0
    large_x_jumps = 0
    previous_y = None
    previous_x = None

    for line in sorted(lines, key=lambda item: item.get("order", 0)):
        x, y = _center(line)
        rows.append({"order": line.get("order"), "x": x, "y": y, "prediction": line.get("prediction", "")})
        if previous_y is not None and y + 20 < previous_y:
            backward_y_jumps += 1
        if previous_x is not None and abs(x - previous_x) > 500:
            large_x_jumps += 1
        previous_x, previous_y = x, y

    fig, axis = plt.subplots(figsize=(8, 10))
    axis.scatter([row["x"] for row in rows], [row["y"] for row in rows], s=20)
    for row in rows:
        axis.text(row["x"], row["y"], str(row["order"]), fontsize=7)
    axis.invert_yaxis()
    axis.set_title(page_dir.name)
    axis.set_xlabel("x center")
    axis.set_ylabel("y center")
    figure_path = output_dir / f"{page_dir.name}_reading_order.png"
    fig.tight_layout()
    fig.savefig(figure_path, dpi=150)
    plt.close(fig)

    return {
        "page": page_dir.name,
        "num_lines": len(rows),
        "backward_y_jumps": backward_y_jumps,
        "large_x_jumps": large_x_jumps,
        "likely_multicolumn": large_x_jumps >= 2,
        "figure": str(figure_path),
        "lines": rows,
    }


def analyze_directory(input_dir: str = "outputs/judicial_demo", output_dir: str = "outputs/reading_order") -> Dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    page_dirs = sorted(Path(input_dir).glob("page_*_canvas_*"))
    pages = [analyze_page(page_dir, output) for page_dir in page_dirs if (page_dir / "transcriptions.json").exists()]
    report = {
        "input_dir": input_dir,
        "num_pages": len(pages),
        "total_lines": sum(page["num_lines"] for page in pages),
        "pages_with_backward_y_jumps": sum(1 for page in pages if page["backward_y_jumps"]),
        "pages_likely_multicolumn": sum(1 for page in pages if page["likely_multicolumn"]),
        "pages": pages,
    }
    with (output / "reading_order_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
    with (output / "reading_order_report.md").open("w", encoding="utf-8") as handle:
        handle.write("# Reading order validation\n\n")
        handle.write(f"- Pages: {report['num_pages']}\n")
        handle.write(f"- Lines: {report['total_lines']}\n")
        handle.write(f"- Pages with backward y jumps: {report['pages_with_backward_y_jumps']}\n")
        handle.write(f"- Pages likely multicolumn: {report['pages_likely_multicolumn']}\n\n")
        for page in pages:
            handle.write(f"## {page['page']}\n\n")
            handle.write(f"- Lines: {page['num_lines']}\n")
            handle.write(f"- Backward y jumps: {page['backward_y_jumps']}\n")
            handle.write(f"- Large x jumps: {page['large_x_jumps']}\n")
            handle.write(f"- Figure: `{page['figure']}`\n\n")
    print(json.dumps({k: v for k, v in report.items() if k != "pages"}, indent=2))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze reading order from judicial demo line polygons.")
    parser.add_argument("--input-dir", default="outputs/judicial_demo")
    parser.add_argument("--output-dir", default="outputs/reading_order")
    args = parser.parse_args()
    analyze_directory(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
