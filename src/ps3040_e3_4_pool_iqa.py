# -*- coding: utf-8 -*-
# ################################################################################
# Title: E3-4 ps1010+ps1301 통합 풀 IQA 분석
# Author: oaiskoo
# Date: 2026.05.17
# Version: v01
# Goal: E3-1(ps1010)·E3-2(ps1301) IQA 결과를 통합 풀로 합쳐 분포 분석
# Changes:
#   - v01: 초기 버전 — E3-1·E3-2 결과 concat (IQA 재산출 없음, 이미지 독립성)
# Description:
#   - 입력: data/ps3010/01_전체데이터_*.xlsx (E3-1, 520행)
#           data/ps3020/01_전체데이터_*.xlsx (E3-2, 737행)
#   - 처리: 공통 메타 정규화 + source_ps 부여 → concat → 통합 풀 1,257행
#   - IQA 재산출 없음 — NR-IQA는 이미지별 독립 계산이므로 결과 concat과 동일
# Input: ./data/ps3010/, ./data/ps3020/ (E3-1·E3-2 산출물)
# Output: ./data/ps3040/e3_4_pool_manifest.csv, 01_통합풀데이터_*.xlsx,
#         02_source별통계_*.xlsx, 04_histogram_*.png
# 참조: d3040_상세구현_E3_4_pool_IQA.md, d0001_prd.md §2.7.2
# ################################################################################
# Library
# ################################################################################
import argparse
import datetime
import json
import os
import sys
import time
import warnings
from glob import glob

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_iqa7 as iqa

# ################################################################################
# Setting
# ################################################################################
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

prefix = os.path.splitext(os.path.basename(__file__))[0][:6]
workname = os.path.splitext(os.path.basename(__file__))[0][6:]
dsr = datetime.datetime.now().strftime("%y%m%d%H%M")
print(prefix + "_" + workname + "_" + dsr)

stime = time.time()
warnings.filterwarnings("default")

# ################################################################################
# Parameter
# ################################################################################
CONFIG = {
    "io": {
        "e3_1_dir": "data/ps3010",
        "e3_2_dir": "data/ps3020",
        "output_dir": "data/ps3040",
        "checkpoint_json": "data/ps3040/_checkpoint_stage.json",
        "checkpoint_pool_csv": "data/ps3040/_checkpoint_pool.csv",
    },
    # 통합 풀 공통 메타 컬럼 (E3-1·E3-2 결과의 교집합)
    "meta_cols": [
        "condition", "distance_m", "speed_kmh", "iso", "frame", "is_defocus",
        "run_device", "common_iqa7_version",
    ],
    # 원본 데이터셋 경로 (manifest src_path 재구성용)
    "src_root": {
        "ps1010": "data/ps1010_chungsong_MTF",
        "ps1301": "data/ps1301_real_crack_cam2",
    },
}

parser = argparse.ArgumentParser(description="E3-4 통합 풀 IQA 분석")
parser.add_argument("--e3_1_xlsx", type=str, default=None, help="E3-1 결과 xlsx 직접 지정")
parser.add_argument("--e3_2_xlsx", type=str, default=None, help="E3-2 결과 xlsx 직접 지정")
parser.add_argument("--output_dir", type=str, default=None)
parser.add_argument("--checkpoint_json", type=str, default=None)
parser.add_argument("--checkpoint_pool_csv", type=str, default=None)
parser.add_argument("--resume", action="store_true", help="체크포인트에서 재개")
args = parser.parse_args()

if args.output_dir:
    CONFIG["io"]["output_dir"] = args.output_dir
if args.checkpoint_json:
    CONFIG["io"]["checkpoint_json"] = args.checkpoint_json
if args.checkpoint_pool_csv:
    CONFIG["io"]["checkpoint_pool_csv"] = args.checkpoint_pool_csv

e3_1_dir = os.path.join(project_root, CONFIG["io"]["e3_1_dir"])
e3_2_dir = os.path.join(project_root, CONFIG["io"]["e3_2_dir"])
output_dir = os.path.join(project_root, CONFIG["io"]["output_dir"])
checkpoint_json_path = os.path.join(project_root, CONFIG["io"]["checkpoint_json"])
checkpoint_pool_csv_path = os.path.join(project_root, CONFIG["io"]["checkpoint_pool_csv"])
os.makedirs(output_dir, exist_ok=True)

# ################################################################################
# 한글 차트 설정
# ################################################################################
import platform
os_var = platform.system()
mpl.use("Agg")
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 13
if os_var == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
elif os_var == "Darwin":
    mpl.rc("font", family="AppleGothic")
else:
    plt.rcParams["font.family"] = "NanumGothic"


# ################################################################################
# Function
# ################################################################################

def find_latest_xlsx(base_dir: str) -> str:
    """base_dir에서 가장 최신 01_전체데이터_*.xlsx 경로 반환. 없으면 빈 문자열."""
    cands = sorted(glob(os.path.join(base_dir, "01_전체데이터_*.xlsx")))
    return cands[-1] if cands else ""


def load_e3_result(xlsx_path: str, source_ps: str) -> pd.DataFrame:
    """E3-1/E3-2 결과 xlsx 로드 → 공통 메타 + 9컬럼 정규화 + source_ps 부여."""
    df = pd.read_excel(xlsx_path)
    keep = [c for c in CONFIG["meta_cols"] + iqa.METRIC_COLUMNS if c in df.columns]
    df = df[keep].copy()
    df.insert(0, "source_ps", source_ps)
    return df


def validate_run_compatibility(pool: pd.DataFrame):
    """E3-1/E3-2 산출물이 동일 라이브러리 버전/디바이스인지 검사."""
    version_col = "common_iqa7_version"
    device_col = "run_device"
    if version_col not in pool.columns or device_col not in pool.columns:
        print("[WARNING] run_device/common_iqa7_version 메타데이터가 없어 호환성 검증을 건너뜁니다.")
        print("          ps3010/ps3020을 최신 스크립트로 다시 산출하면 검증할 수 있습니다.")
        return

    grouped = pool.groupby("source_ps")[[version_col, device_col]].agg(
        lambda s: sorted(set(s.dropna().astype(str)))
    )
    print("\n[호환성 점검]")
    for source_ps, row in grouped.iterrows():
        print(f"  {source_ps}: version={row[version_col]} / device={row[device_col]}")

    all_versions = sorted(set(pool[version_col].dropna().astype(str)))
    all_devices = sorted(set(pool[device_col].dropna().astype(str)))
    if len(all_versions) > 1:
        print(f"[WARNING] common_iqa7 버전 불일치 감지: {all_versions}")
    if len(all_devices) > 1:
        print(f"[WARNING] 실행 디바이스 불일치 감지: {all_devices}")
    if len(all_versions) == 1 and len(all_devices) == 1:
        print("[OK] E3-1/E3-2 산출물의 common_iqa7 버전과 실행 디바이스가 일치합니다.")


def build_manifest(pool: pd.DataFrame) -> pd.DataFrame:
    """통합 풀 manifest — source_ps·condition·frame + 원본 경로 재구성."""
    rows = []
    for _, r in pool.iterrows():
        root = CONFIG["src_root"].get(r["source_ps"], "")
        src_path = os.path.join(root, str(r["condition"]), str(r["frame"]))
        rows.append({
            "source_ps": r["source_ps"],
            "condition": r["condition"],
            "frame": r["frame"],
            "src_path": src_path,
        })
    return pd.DataFrame(rows)


def build_source_stats(pool: pd.DataFrame) -> pd.DataFrame:
    """source별(ps1010/ps1301) + 통합(all) 메트릭 통계."""
    frames = []
    for src in ["ps1010", "ps1301"]:
        sub = pool[pool["source_ps"] == src]
        stat = sub[iqa.METRIC_COLUMNS].agg(["mean", "std", "min", "max"]).T
        stat.insert(0, "source_ps", src)
        stat.insert(1, "n", len(sub))
        frames.append(stat.reset_index().rename(columns={"index": "metric"}))
    allstat = pool[iqa.METRIC_COLUMNS].agg(["mean", "std", "min", "max"]).T
    allstat.insert(0, "source_ps", "all")
    allstat.insert(1, "n", len(pool))
    frames.append(allstat.reset_index().rename(columns={"index": "metric"}))
    return pd.concat(frames, ignore_index=True)


def save_histogram(pool: pd.DataFrame, out_dir: str):
    """9개 메트릭 히스토그램 — source별(ps1010/ps1301) 오버레이."""
    fig, axes = plt.subplots(3, 3, figsize=(15, 12))
    for ax, col in zip(axes.flatten(), iqa.METRIC_COLUMNS):
        for src, color in (("ps1010", "steelblue"), ("ps1301", "indianred")):
            vals = pool.loc[pool["source_ps"] == src, col].dropna()
            ax.hist(vals, bins=30, alpha=0.55, label=src, color=color, edgecolor="white")
        ax.set_title(f"{col}\n({iqa.METRIC_DIRECTION[col]})")
        ax.set_xlabel("Score")
        ax.set_ylabel("Count")
        ax.legend(fontsize=9)
    plt.tight_layout()
    out_path = os.path.join(out_dir, f"04_histogram_{dsr}.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"히스토그램 저장: {out_path}")


def save_stage_checkpoint(stage: str, extra: dict | None = None):
    """단계 체크포인트 저장."""
    payload = {"stage": stage}
    if extra:
        payload.update(extra)
    tmp_path = f"{checkpoint_json_path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, checkpoint_json_path)


def load_stage_checkpoint() -> dict:
    """단계 체크포인트 로드."""
    if not args.resume or not os.path.exists(checkpoint_json_path):
        return {}
    with open(checkpoint_json_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ################################################################################
# Main
# ################################################################################
def main():
    stage_ckpt = load_stage_checkpoint()
    if stage_ckpt:
        print(f"[RESUME] stage={stage_ckpt.get('stage')}")

    # E3-1·E3-2 결과 경로 결정
    e3_1_path = args.e3_1_xlsx or find_latest_xlsx(e3_1_dir)
    e3_2_path = args.e3_2_xlsx or find_latest_xlsx(e3_2_dir)

    print(f"\n{'='*60}")
    print("입력 확인")
    print(f"{'='*60}")
    print(f"E3-1 (ps1010): {e3_1_path or '[없음]'}")
    print(f"E3-2 (ps1301): {e3_2_path or '[없음]'}")

    if not e3_1_path or not os.path.exists(e3_1_path):
        print("[ERROR] E3-1 결과 없음 — ps3010 먼저 실행 필요")
        sys.exit(1)
    if not e3_2_path or not os.path.exists(e3_2_path):
        print("[ERROR] E3-2 결과 없음 — ps3020 먼저 실행 필요")
        sys.exit(1)

    df1 = None
    df2 = None
    if stage_ckpt.get("stage") in {"merged", "saved"} and os.path.exists(checkpoint_pool_csv_path):
        pool = pd.read_csv(checkpoint_pool_csv_path)
        print(f"\n[RESUME] 통합 풀 체크포인트 로드: {len(pool)}행")
    else:
        # 로드 + source_ps 부여
        df1 = load_e3_result(e3_1_path, "ps1010")
        df2 = load_e3_result(e3_2_path, "ps1301")
        print(f"\nE3-1 로드: {len(df1)}행 / E3-2 로드: {len(df2)}행")
        # 통합 풀
        pool = pd.concat([df1, df2], ignore_index=True)
        print(f"통합 풀: {len(pool)}행 (ps1010 {len(df1)} + ps1301 {len(df2)})")
        pool.to_csv(checkpoint_pool_csv_path, index=False, encoding="utf-8-sig")
        save_stage_checkpoint("merged", {"rows": int(len(pool))})

    validate_run_compatibility(pool)

    # ############################################################################
    # 저장
    # ############################################################################
    print(f"\n{'='*60}")
    print("결과 저장")
    print(f"{'='*60}")

    manifest = build_manifest(pool)
    manifest_path = os.path.join(output_dir, "e3_4_pool_manifest.csv")
    manifest.to_csv(manifest_path, index=False, encoding="utf-8-sig")
    print(f"manifest: {manifest_path}")

    out_all = os.path.join(output_dir, f"01_통합풀데이터_{dsr}.xlsx")
    with pd.ExcelWriter(out_all, engine="openpyxl") as w:
        pool.to_excel(w, sheet_name="통합풀데이터", index=False)
    print(f"통합 풀: {out_all}")

    stats = build_source_stats(pool)
    out_stats = os.path.join(output_dir, f"02_source별통계_{dsr}.xlsx")
    with pd.ExcelWriter(out_stats, engine="openpyxl") as w:
        stats.to_excel(w, sheet_name="source별통계", index=False)
    print(f"source별 통계: {out_stats}")

    save_histogram(pool, output_dir)
    save_stage_checkpoint("saved", {"rows": int(len(pool))})

    # 요약
    print(f"\n{'='*60}")
    print("결과 요약")
    print(f"{'='*60}")
    if df1 is None or df2 is None:
        df1_count = int((pool["source_ps"] == "ps1010").sum())
        df2_count = int((pool["source_ps"] == "ps1301").sum())
    else:
        df1_count = len(df1)
        df2_count = len(df2)
    print(f"통합 풀: {len(pool)}행 (ps1010 {df1_count} + ps1301 {df2_count})")
    print("\nsource별 메트릭 평균:")
    for col in iqa.METRIC_COLUMNS:
        m1 = pool.loc[pool["source_ps"] == "ps1010", col].dropna().mean()
        m2 = pool.loc[pool["source_ps"] == "ps1301", col].dropna().mean()
        mall = pool[col].dropna().mean()
        print(f"  {col:<16} ps1010={m1:8.4f}  ps1301={m2:8.4f}  통합={mall:8.4f}")

    # ############################################################################
    # Finish
    # ############################################################################
    etime = time.time()
    print(f"\n{prefix}_{workname} finished in {etime-stime:.2f} seconds")


if __name__ == "__main__":
    main()
