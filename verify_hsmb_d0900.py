"""
d0900 HSMB 버전 매칭 검증 스크립트
==================================
목적: ps1204 입력 데이터에 ps7201 v1.1 / ps7310 v2 알고리즘을 적용해
      data/ps1600_hsmb 기존값비교/ 안의 두 xlsx HSMB 값과 매칭되는지 확인

xlsx 기준값 (15000lx-500us-00km/h):
  - File1: HSMB = 0.8893
  - File2 (_0715): HSMB = 0.6280
"""

import os
import glob
import numpy as np
import cv2
import pandas as pd

# =============================================================
# ps7201 v1.1 함수 (원본 알고리즘) — 그대로 추출
# =============================================================
def v1_grad_mag(gray_block):
    sx = cv2.Sobel(gray_block, cv2.CV_32F, 1, 0, ksize=3)
    sy = cv2.Sobel(gray_block, cv2.CV_32F, 0, 1, ksize=3)
    return cv2.magnitude(sx, sy)

def v1_active_edges(magnitude_block, p_w):
    mean_val = np.mean(magnitude_block) * float(p_w)
    return np.argwhere(magnitude_block > mean_val)

def v1_edge_dir(gray_block, r, c, p_dir):
    h, w = gray_block.shape
    dirs = ([(-1,0),(1,0),(0,-1),(0,1)] if p_dir == "four"
            else [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)])
    cv = float(gray_block[r, c]); md = -1; bd = (0,0)
    for dr, dc in dirs:
        rr, cc = r+dr, c+dc
        if 0 <= rr < h and 0 <= cc < w:
            d = abs(float(gray_block[rr,cc]) - cv)
            if d > md: md = d; bd = (dr, dc)
    return bd

def v1_profile(gray_block, r, c, dr, dc, length=10):
    h, w = gray_block.shape
    p = []
    for i in range(length):
        rr, cc = r+dr*i, c+dc*i
        p.append(float(gray_block[rr,cc]) if (0<=rr<h and 0<=cc<w) else 0.0)
    return np.array(p, dtype=np.float32)

def v1_edge_width(profile, thres):
    cv = profile[0]
    if cv == 0: return None
    tv = abs(cv) * float(thres)
    for i in range(1, len(profile)):
        d = abs(profile[i] - cv)
        if d >= tv:
            dp = abs(profile[i-1] - cv)
            if abs(d - dp) < 1e-9: return float(i)
            t = (tv - dp) / (d - dp)
            return (i - 1) + t
    return None

def v1_precompute(img_path, block_size):
    g = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if g is None: raise FileNotFoundError(img_path)
    g = g.astype(np.float32)
    h, w = g.shape
    nr, nc = h // block_size, w // block_size
    out = []
    for br in range(nr):
        for bc in range(nc):
            r0, c0 = br*block_size, bc*block_size
            blk = g[r0:r0+block_size, c0:c0+block_size]
            out.append((blk, v1_grad_mag(blk)))
    return out

def v1_hsmb_blocks(blocks, thres, beta, pw, pdir):
    hist = np.zeros(101, dtype=np.float32); total = 0
    for blk, mag in blocks:
        edges = v1_active_edges(mag, pw)
        for r, c in edges:
            dr, dc = v1_edge_dir(blk, r, c, pdir)
            if (dr, dc) == (0, 0): continue
            prof = v1_profile(blk, r, c, dr, dc, length=10)
            ew = v1_edge_width(prof, thres)
            if ew is not None:
                pb = 1 - np.exp(-abs(ew/3) ** beta)
                pbs = float(pb.item()) if isinstance(pb, np.ndarray) else float(pb)
                idx = min(int(round(pbs*100)), 100)
                hist[idx] += 1; total += 1
    pdf = hist/total if total > 0 else np.zeros(101)
    cdf = np.cumsum(pdf)
    return round(float(cdf[63]), 4)

def cal_hsmb_v1(img_path, block_size=64, thres=0.4, beta=3.6, pw=1.0, pdir="four"):
    blocks = v1_precompute(img_path, block_size)
    return v1_hsmb_blocks(blocks, thres, beta, pw, pdir)


# ps5010 v1 (원형): thres=0.1, beta=2, w_jnb=3 — 동일 함수 재사용 + 파라미터만 변경
def cal_hsmb_ps5010(img_path):
    return cal_hsmb_v1(img_path, block_size=64, thres=0.1, beta=2, pw=1.0, pdir="four")

# ps5020 v11: thres=0.4, beta=3.6 (사실상 v1.1과 동일)
def cal_hsmb_ps5020(img_path):
    return cal_hsmb_v1(img_path, block_size=64, thres=0.4, beta=3.6, pw=1.0, pdir="four")


# 파라미터 스윕용 변형 — ps5010 코드에 명시된 4가지 조합
def cal_hsmb_ps5010_t01_b2_w15(img_path):
    return cal_hsmb_v1(img_path, thres=0.1, beta=2, pw=1.5, pdir="four")
def cal_hsmb_ps5010_t02_b2_w10(img_path):
    return cal_hsmb_v1(img_path, thres=0.2, beta=2, pw=1.0, pdir="four")
def cal_hsmb_ps5010_t02_b2_w15(img_path):
    return cal_hsmb_v1(img_path, thres=0.2, beta=2, pw=1.5, pdir="four")

# cdf 인덱스 변형 — ps5010과 동일한 분포에서 다른 위치 (cdf[80], cdf[90], cdf[95])
def _v1_hsmb_blocks_idx(blocks, thres, beta, pw, pdir, cdf_idx):
    hist = np.zeros(101, dtype=np.float32); total = 0
    for blk, mag in blocks:
        edges = v1_active_edges(mag, pw)
        for r, c in edges:
            dr, dc = v1_edge_dir(blk, r, c, pdir)
            if (dr, dc) == (0, 0): continue
            prof = v1_profile(blk, r, c, dr, dc, length=10)
            ew = v1_edge_width(prof, thres)
            if ew is not None:
                pb = 1 - np.exp(-abs(ew/3) ** beta)
                pbs = float(pb.item()) if isinstance(pb, np.ndarray) else float(pb)
                idx = min(int(round(pbs*100)), 100)
                hist[idx] += 1; total += 1
    pdf = hist/total if total > 0 else np.zeros(101)
    cdf = np.cumsum(pdf)
    return round(float(cdf[cdf_idx]), 4)

def cal_hsmb_ps5010_cdf80(img_path):
    blocks = v1_precompute(img_path, 64)
    return _v1_hsmb_blocks_idx(blocks, 0.1, 2, 1.0, "four", 80)

def cal_hsmb_ps5010_cdf90(img_path):
    blocks = v1_precompute(img_path, 64)
    return _v1_hsmb_blocks_idx(blocks, 0.1, 2, 1.0, "four", 90)


# =============================================================
# ps7310 v2 함수 (개선판) — 그대로 추출
# =============================================================
NOISE_THRES = 5.0

def v2_preprocess(gray_img):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enh = clahe.apply(gray_img.astype(np.uint8))
    return cv2.GaussianBlur(enh.astype(np.float32), (3,3), 0.5)

def v2_grad_mag(gray_block):
    sx = cv2.Scharr(gray_block, cv2.CV_32F, 1, 0)
    sy = cv2.Scharr(gray_block, cv2.CV_32F, 0, 1)
    m = cv2.magnitude(sx, sy)
    m[m < NOISE_THRES] = 0
    return m

def v2_active_edges(mag, pw):
    pw = float(pw)
    mv = np.mean(mag); sv = np.std(mag)
    return np.argwhere(mag > (mv + sv*0.5) * pw)

def v2_edge_width(profile, thres):
    cv = profile[0]
    if cv == 0: return None
    tv = abs(cv) * float(thres)
    for i in range(1, len(profile)):
        d = abs(profile[i] - cv)
        if d >= tv:
            dp = abs(profile[i-1] - cv)
            if abs(d - dp) < 1e-9: return float(i)
            t = (tv - dp) / (d - dp)
            return (i - 1) + t
    return float(len(profile))

def v2_lap_var(blk):
    return cv2.Laplacian(blk.astype(np.uint8), cv2.CV_64F).var()

def v2_fft_energy(blk):
    f = np.fft.fftshift(np.fft.fft2(blk)); ms = np.abs(f)
    h, w = blk.shape; ch, cw = h//2, w//2
    mask = np.zeros((h,w))
    mask[0:ch//2,:] = 1; mask[ch+ch//2:,:] = 1
    mask[:,0:cw//2] = 1; mask[:,cw+cw//2:] = 1
    return np.sum(ms*mask)

def v2_precompute(img_path, block_size):
    g = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if g is None: raise FileNotFoundError(img_path)
    g = v2_preprocess(g)
    h, w = g.shape; nr, nc = h//block_size, w//block_size
    out = []
    for br in range(nr):
        for bc in range(nc):
            r0, c0 = br*block_size, bc*block_size
            blk = g[r0:r0+block_size, c0:c0+block_size]
            out.append((blk, v2_grad_mag(blk), v2_lap_var(blk), v2_fft_energy(blk)))
    return out

def v2_hsmb_blocks(blocks, thres, beta, pw, pdir):
    hist = np.zeros(101, dtype=np.float32); total = 0
    tlap = 0; tfft = 0
    for blk, mag, lv, fe in blocks:
        tlap += lv; tfft += fe
        edges = v2_active_edges(mag, pw)
        for r, c in edges:
            dr, dc = v1_edge_dir(blk, r, c, pdir)  # 동일 함수 재사용
            if (dr, dc) == (0, 0): continue
            prof = v1_profile(blk, r, c, dr, dc, length=10)
            ew = v2_edge_width(prof, thres)
            if ew is not None:
                pb = 1 - np.exp(-abs(ew/2.5) ** beta)
                pbs = float(pb.item()) if isinstance(pb, np.ndarray) else float(pb)
                idx = min(int(round(pbs*100)), 100)
                hist[idx] += 1; total += 1
    pdf = hist/total if total > 0 else np.zeros(101)
    cdf = np.cumsum(pdf)
    base_hsmb = float(cdf[45])
    nb = len(blocks)
    avg_lap = tlap/nb if nb > 0 else 0
    avg_fft = tfft/nb if nb > 0 else 0
    lap_score = min(1.0, avg_lap/800.0)
    fft_score = min(1.0, avg_fft/1200000.0)
    hsmb_sharp = 1 - base_hsmb
    base_sharp = lap_score
    hsmb_adj = (hsmb_sharp - 0.5) * 0.1
    fft_adj = (fft_score - 0.5) * 0.05
    score = base_sharp + hsmb_adj + fft_adj
    score = np.clip(score, 0.0, 1.0)
    score = score ** 0.25
    score = 0.1 + score * 0.85
    return round(float(np.clip(score, 0.0, 1.0)), 4)

def cal_hsmb_v2(img_path, block_size=64, thres=0.3, beta=1.8, pw=0.8, pdir="four"):
    blocks = v2_precompute(img_path, block_size)
    return v2_hsmb_blocks(blocks, thres, beta, pw, pdir)


# =============================================================
# 검증 실행
# =============================================================
if __name__ == "__main__":
    folder = "data/ps1204_kict_eSFR/15000lx_0640_500us_00"  # sharpest test case
    target_xlsx_file1 = 0.8893  # MTF(15000)-IQA 지표.xlsx
    target_xlsx_file2 = 0.6280  # MTF(15000)-IQA 지표_0715.xlsx

    imgs = sorted(glob.glob(f"{folder}/*.png"))
    print(f"Folder: {folder}")
    print(f"Image count: {len(imgs)}")
    print()

    candidates = [
        ("v1.1 (t.4 b3.6)", cal_hsmb_v1),
        ("v2 (enhanced)", cal_hsmb_v2),
        ("ps5010 (t.1 b2 w1.0)", cal_hsmb_ps5010),
        ("ps5010 (t.1 b2 w1.5)", cal_hsmb_ps5010_t01_b2_w15),
        ("ps5010 (t.2 b2 w1.0)", cal_hsmb_ps5010_t02_b2_w10),
        ("ps5010 (t.2 b2 w1.5)", cal_hsmb_ps5010_t02_b2_w15),
        ("ps5010 cdf[80]", cal_hsmb_ps5010_cdf80),
        ("ps5010 cdf[90]", cal_hsmb_ps5010_cdf90),
    ]
    results = {name: [] for name, _ in candidates}
    for p in imgs:
        line = f"  {os.path.basename(p):<8} "
        for name, fn in candidates:
            v = fn(p)
            results[name].append(v)
            line += f"{name[:14]}={v:.4f} "
        print(line)

    print()
    print("=" * 70)
    print(f"Test Case: 15000lx-500us-00km/h (sharpest, BEW=3.23)")
    print(f"  Target file1 = {target_xlsx_file1}, file2 = {target_xlsx_file2}")
    print()
    for name, vals in results.items():
        m = np.mean(vals)
        d1 = abs(m - target_xlsx_file1)
        d2 = abs(m - target_xlsx_file2)
        print(f"  {name:<14} mean={m:.4f}  Δfile1={d1:.4f}  Δfile2={d2:.4f}")
