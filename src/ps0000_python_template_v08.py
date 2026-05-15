# -*- coding: utf-8 -*-
# ################################################################################
# Title:
# Author: oaiskoo
# Date: 2025.01.17
# Version: v01
# Goal:
# Changes:
#   - v01: 초기 버전
# Description:
#   -
# Input: ./data/
# Output: ./data/{prefix}/
# ################################################################################
# Library
# ################################################################################
import os
import sys
import time
import glob
import argparse
import platform
import datetime
import warnings

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from tqdm import tqdm

# 프로젝트 루트를 sys.path에 추가 (oais 패키지 접근용)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

import oais

# ################################################################################
# Setting
# ################################################################################
# 1. Basic Information
prefix = os.path.splitext(os.path.basename(__file__))[0][:6]
workname = os.path.splitext(os.path.basename(__file__))[0][6:]
dsr = datetime.datetime.now().strftime("%y%m%d%H%M")
print(prefix + "_" + workname + "_" + dsr)

# 2. Output Directory
output_dir = oais.make_output_dir(
    os.path.join(project_root, "data"), prefix, rmfolder="n"
)

# 3. System & Environment
stime = time.time()
mpl.use("Agg")
warnings.filterwarnings("default")

# ################################################################################
# Parameter
# ################################################################################
# =============================================================================
# 파라미터 설정 (수정 가능)
# =============================================================================
CONFIG = {
    # 입출력 설정
    "io": {
        "input_dir": "data/sample",  # 입력 디렉토리 (project_root 기준)
        "extensions": ["bmp", "png", "jpg", "jpeg", "tif", "tiff"],
    },
    # 처리 설정
    "processing": {
        "enabled": True,
    },
    # 출력 설정
    "output": {
        "save_results": True,
    },
}
# =============================================================================

# argparse (CONFIG 값을 덮어쓸 수 있음)
parser = argparse.ArgumentParser(description="스크립트 설명")
parser.add_argument("--reset", type=str, default="y", help="출력 폴더 초기화 여부")
parser.add_argument(
    "--input_dir", type=str, default=None, help="입력 디렉토리 (CONFIG 덮어쓰기)"
)
args = parser.parse_args()

# argparse로 CONFIG 덮어쓰기
if args.input_dir:
    CONFIG["io"]["input_dir"] = args.input_dir

# 한글 차트 설정
os_var = platform.system()
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 15

if os_var == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
elif os_var == "Darwin":
    mpl.rc("font", family="AppleGothic")
else:
    plt.rcParams["font.family"] = "NanumGothic"

# 설정 출력
print(f"\n{'='*60}")
print("설정 정보")
print(f"{'='*60}")
print(f"입력 디렉토리: {CONFIG['io']['input_dir']}")
print(f"출력 디렉토리: {output_dir}")
print(f"{'='*60}")

# ################################################################################
# IO
# ################################################################################
input_dir = os.path.join(project_root, CONFIG["io"]["input_dir"])
EXTENSIONS = CONFIG["io"]["extensions"]

# 파일 목록 수집
file_list = []
for ext in EXTENSIONS:
    file_list.extend(glob.glob(os.path.join(input_dir, f"**/*.{ext}"), recursive=True))
file_list = sorted(file_list)
print(f"총 파일 수: {len(file_list)}")


# ################################################################################
# Function
# ################################################################################
def process_single_file(file_path):
    """단일 파일 처리 함수"""
    # TODO: 처리 로직 구현
    result = {
        "file_path": file_path,
        "filename": os.path.basename(file_path),
    }
    return result


# ################################################################################
# Main
# ################################################################################
def main():
    print(f"\n{'='*60}")
    print("처리 시작")
    print(f"{'='*60}")

    # 파일 처리
    results = []
    for file_path in tqdm(file_list, desc="처리 중"):
        result = process_single_file(file_path)
        results.append(result)

    print(f"처리 완료: {len(results)}개")

    # ############################################################################
    # Save
    # ############################################################################
    if CONFIG["output"]["save_results"]:
        # 결과 저장
        output_pth = os.path.join(output_dir, "results.xlsx")
        df = pd.DataFrame(results)
        df.to_excel(output_pth, index=False)
        print(f"결과 저장: {output_pth}")

    # ############################################################################
    # Finish
    # ############################################################################
    etime = time.time()
    print(f"\n{prefix}_{workname} finished in {etime-stime:.2f} seconds")


if __name__ == "__main__":
    main()
