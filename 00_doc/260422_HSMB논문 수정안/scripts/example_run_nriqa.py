"""
Task A — NR-IQA metric computation skeleton.

Fills in the HSMB computation using `hsmb_metric.py`. Other NR-IQA metrics
(CPBD, NIQE, PIQE, BRISQUE, DBCNN, ARNIQA) are left as TODO placeholders —
collaborators plug in their preferred libraries/implementations.

Expected filename pattern:
    cam1_v{60|80}_iso{100|200|400|800|1600}_d{25|35|45|55|65}_frame_{XXXXXX}.png
or existing tunnelscanning directory layout (condition folder → frame files).

Usage:
    python example_run_nriqa.py --images /path/to/images --out task_A_metrics_per_frame.csv
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import time
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hsmb_metric import compute_hsmb

FNAME_RE = re.compile(
    r"cam1_v(?P<speed>\d+)_iso(?P<iso>\d+)_d(?P<d10>\d+)"
    r"(?:_frame_(?P<frame>\d+))?\.(?:png|tif|jpg|jpeg)$",
    re.IGNORECASE,
)

HSMB_KWARGS = {"edge_weight": 1.5, "jnb": 3, "beta": 2.0}


def parse_condition(path: Path) -> dict | None:
    m = FNAME_RE.search(path.name)
    if m:
        return {
            "speed_kmh": int(m.group("speed")),
            "iso": int(m.group("iso")),
            "distance_m": int(m.group("d10")) / 10.0,
            "frame": path.name,
        }
    # Fallback: parse from parent directory
    parent = path.parent.name
    m = FNAME_RE.match(parent + ".png")
    if m:
        return {
            "speed_kmh": int(m.group("speed")),
            "iso": int(m.group("iso")),
            "distance_m": int(m.group("d10")) / 10.0,
            "frame": path.name,
        }
    return None


def compute_all_metrics(image: np.ndarray) -> dict:
    """Compute HSMB plus placeholders for other NR-IQA metrics."""
    out = {}

    t0 = time.perf_counter()
    out["hsmb"] = float(compute_hsmb(image, **HSMB_KWARGS))
    out["_hsmb_ms"] = (time.perf_counter() - t0) * 1000.0

    # TODO — replace with real library calls
    out["cpbd"] = np.nan      # from `cpbd` package
    out["niqe"] = np.nan      # from skimage or MATLAB
    out["piqe"] = np.nan      # MATLAB built-in
    out["brisque"] = np.nan   # pybrisque
    out["dbcnn"] = np.nan     # DBCNN pretrained
    out["arniqa"] = np.nan    # ARNIQA pretrained

    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", required=True, help="root dir of field images")
    parser.add_argument("--out", required=True, help="output CSV path")
    parser.add_argument(
        "--pattern",
        default="**/*.png",
        help="glob pattern relative to --images",
    )
    args = parser.parse_args()

    root = Path(args.images)
    files = sorted(root.glob(args.pattern))
    print(f"Found {len(files)} images under {root}")

    fieldnames = [
        "speed_kmh",
        "iso",
        "distance_m",
        "frame",
        "hsmb",
        "cpbd",
        "niqe",
        "piqe",
        "brisque",
        "dbcnn",
        "arniqa",
    ]

    runtime_samples: list[float] = []

    with open(args.out, "w", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()

        for i, path in enumerate(files, 1):
            cond = parse_condition(path)
            if cond is None:
                print(f"[WARN] cannot parse condition from {path.name}, skipping")
                continue

            img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
            if img is None:
                print(f"[WARN] failed to read {path}")
                continue

            metrics = compute_all_metrics(img)
            if "_hsmb_ms" in metrics:
                runtime_samples.append(metrics.pop("_hsmb_ms"))

            row = {**cond, **metrics}
            writer.writerow(row)

            if i % 100 == 0:
                print(f"  processed {i}/{len(files)}")

    if runtime_samples:
        print(
            f"HSMB runtime: mean {np.mean(runtime_samples):.2f} ms / image "
            f"(N={len(runtime_samples)})"
        )
    print(f"wrote → {args.out}")


if __name__ == "__main__":
    main()
