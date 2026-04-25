"""
Task B — CNN crack detection + HSMB pre-filtering skeleton.

This is a scaffolding. Collaborators plug in the actual ResNet34 inference
and F1 computation based on their label format (pixel-wise or box-wise).

Usage:
    python example_run_crack.py \
        --model /path/to/resnet34.pth \
        --images /path/to/field_images \
        --hsmb_scores task_A_metrics_per_frame.csv \
        --labels /path/to/labels \
        --out task_B_crack_detection_per_image.csv
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pandas as pd


def run_inference(model_path: str, image_path: Path, label_path: Path) -> dict:
    """
    TODO: implement ResNet34 inference and F1 computation.
    Expected return: {"tp": int, "fp": int, "fn": int,
                      "precision": float, "recall": float, "f1": float}
    """
    # Placeholder — replace with real model call
    return {
        "tp": 0,
        "fp": 0,
        "fn": 0,
        "precision": float("nan"),
        "recall": float("nan"),
        "f1": float("nan"),
    }


def complex_blur_flag(iso: int, distance_m: float) -> int:
    return int(iso == 400 and abs(distance_m - 4.5) < 1e-6)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--images", required=True)
    parser.add_argument("--labels", required=True)
    parser.add_argument(
        "--hsmb_scores",
        required=True,
        help="Task A output CSV with per-frame HSMB score",
    )
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    hsmb_df = pd.read_csv(args.hsmb_scores)
    hsmb_df.set_index(["speed_kmh", "iso", "distance_m", "frame"], inplace=True)

    gt_frame_csv = Path(__file__).resolve().parent.parent / "data" / "ground_truth_frame.csv"
    gt = pd.read_csv(gt_frame_csv)
    gt.set_index(["speed_kmh", "iso", "distance_m", "frame"], inplace=True)

    fieldnames = [
        "speed_kmh", "iso", "distance_m", "frame",
        "hsmb", "bew_ref", "mtf50_ref",
        "tp", "fp", "fn",
        "precision", "recall", "f1",
        "complex_blur_flag",
    ]

    with open(args.out, "w", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()

        for key, hsmb_row in hsmb_df.iterrows():
            speed, iso, dist, frame = key
            image_path = Path(args.images) / frame
            if not image_path.exists():
                continue

            label_path = Path(args.labels) / frame  # adapt per label format
            preds = run_inference(args.model, image_path, label_path)

            row = {
                "speed_kmh": speed,
                "iso": iso,
                "distance_m": dist,
                "frame": frame,
                "hsmb": float(hsmb_row.get("hsmb", float("nan"))),
                "bew_ref": float(gt.loc[key, "bew_px"]) if key in gt.index else float("nan"),
                "mtf50_ref": float(gt.loc[key, "mtf50_cy_px"]) if key in gt.index else float("nan"),
                **preds,
                "complex_blur_flag": complex_blur_flag(iso, dist),
            }
            writer.writerow(row)

    print(f"wrote → {args.out}")
    print(
        "TODO next: aggregate by blur bin → task_B_crack_detection_by_blur_bin.csv"
    )
    print("          sweep HSMB threshold → task_B_threshold_sweep.csv")


if __name__ == "__main__":
    main()
