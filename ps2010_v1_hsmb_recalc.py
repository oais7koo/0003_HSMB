"""
ps2010 — ps2000 형식으로 HSMB v1 결과 재산출
==============================================
- 입력: data/ps1204_kict_eSFR/ (47개 폴더 × 10 PNG = 470장)
- 알고리즘: ps5010 HSMB v1 (threshold_ratio=0.1, p_beta=2, p_edge_weight=1.5)
- 출력: data/ps2010/01_전체데이터_*.xlsx, 02_그룹별통계_*.xlsx, 03_그룹별평균_*.xlsx
- 동작: ps2000의 기존 xlsx에서 hsmb 컬럼만 v1로 교체. 다른 IQA 지표는 그대로 유지.
"""

import os
import sys
import glob
import time
from datetime import datetime
import numpy as np
import pandas as pd
import cv2
from concurrent.futures import ProcessPoolExecutor, as_completed

# verify_hsmb_d0900.py에서 v1 함수 재사용
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify_hsmb_d0900 import cal_hsmb_ps5010_t01_b2_w15  # t=0.1, β=2, w=1.5


def calc_one(args):
    sub_dir, fnm, img_path = args
    try:
        v = cal_hsmb_ps5010_t01_b2_w15(img_path)
    except Exception as e:
        v = None
    return sub_dir, fnm, v


def main():
    src_root = "data/ps1204_kict_eSFR"
    ps2000_dir = "data/ps2000"
    out_dir = "data/ps2010"
    os.makedirs(out_dir, exist_ok=True)

    # 1) ps2000 기존 데이터 로드
    src_01 = sorted(glob.glob(f"{ps2000_dir}/01_*.xlsx"))[-1]
    src_02 = sorted(glob.glob(f"{ps2000_dir}/02_*.xlsx"))[-1]
    src_03 = sorted(glob.glob(f"{ps2000_dir}/03_*.xlsx"))[-1]
    print(f"[Source] {os.path.basename(src_01)}")

    df01 = pd.read_excel(src_01, sheet_name=0)
    nr_info = pd.read_excel(src_01, sheet_name="NR메트릭정보") if "NR메트릭정보" in pd.ExcelFile(src_01).sheet_names else None
    fr_info = pd.read_excel(src_01, sheet_name="FR메트릭정보") if "FR메트릭정보" in pd.ExcelFile(src_01).sheet_names else None
    print(f"[Loaded] 01_전체데이터: {df01.shape}")

    # 2) v1 HSMB 병렬 계산
    tasks = []
    for _, row in df01.iterrows():
        sub_dir = row["sub_dir"]
        fnm = row["fnm"]
        img_path = f"{src_root}/{sub_dir}/{fnm}"
        if os.path.exists(img_path):
            tasks.append((sub_dir, fnm, img_path))
    print(f"[Tasks] {len(tasks)} images to process")

    t0 = time.time()
    results = {}
    n_workers = max(1, (os.cpu_count() or 4) - 1)
    print(f"[Workers] {n_workers}")
    with ProcessPoolExecutor(max_workers=n_workers) as ex:
        futures = {ex.submit(calc_one, t): t for t in tasks}
        done = 0
        for fut in as_completed(futures):
            sub_dir, fnm, v = fut.result()
            results[(sub_dir, fnm)] = v
            done += 1
            if done % 50 == 0 or done == len(tasks):
                print(f"  progress {done}/{len(tasks)} ({(time.time()-t0):.1f}s elapsed)")
    print(f"[Done] {len(results)} results in {(time.time()-t0):.1f}s")

    # 3) hsmb 컬럼 교체
    df01_new = df01.copy()
    df01_new["hsmb"] = df01_new.apply(
        lambda r: results.get((r["sub_dir"], r["fnm"]), r["hsmb"]), axis=1
    )

    # 4) 그룹별 통계 재계산 (02_그룹별통계.xlsx 형식)
    metric_cols = [c for c in df01_new.columns if c not in ["sub_dir", "fnm", "quality_grade", "fr_grade"]]
    metric_cols = [c for c in metric_cols if pd.api.types.is_numeric_dtype(df01_new[c])]
    grouped = df01_new.groupby("sub_dir")[metric_cols].agg(["mean", "std", "min", "max"])
    grouped = grouped.reset_index()
    print(f"[Grouped 02] {grouped.shape}")

    # 5) 03_그룹별평균.xlsx 형식 (mean only)
    df03 = df01_new.groupby("sub_dir")[metric_cols].mean().reset_index()
    print(f"[Grouped 03] {df03.shape}")

    # 6) 저장
    ts = datetime.now().strftime("%y%m%d%H%M")
    out01 = f"{out_dir}/01_전체데이터_{ts}.xlsx"
    out02 = f"{out_dir}/02_그룹별통계_{ts}.xlsx"
    out03 = f"{out_dir}/03_그룹별평균_{ts}.xlsx"

    with pd.ExcelWriter(out01) as w:
        df01_new.to_excel(w, sheet_name="전체데이터", index=False)
        if nr_info is not None:
            nr_info.to_excel(w, sheet_name="NR메트릭정보", index=False)
        if fr_info is not None:
            fr_info.to_excel(w, sheet_name="FR메트릭정보", index=False)
    grouped.to_excel(out02, sheet_name="그룹별통계")
    df03.to_excel(out03, sheet_name="그룹별평균", index=False)

    print(f"[Saved] {out01}")
    print(f"[Saved] {out02}")
    print(f"[Saved] {out03}")
    print()
    print("=" * 60)
    print("HSMB 컬럼 비교 (sharp case 15000lx_0640_500us_00):")
    sub = df01_new[df01_new["sub_dir"] == "15000lx_0640_500us_00"]
    print(f"  v1 mean = {sub['hsmb'].mean():.4f}")
    print(f"  (참고: ps5010 v1 t=0.1 β=2 w=1.5 / d0900 검증값 0.8893)")


if __name__ == "__main__":
    main()
