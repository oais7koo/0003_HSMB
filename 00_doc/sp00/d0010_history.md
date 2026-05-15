# 변경 이력 — 0003_HSMB

## v05 — 2026-04-25

### d0001_prd.md v05 (터널표준영상 정의 + E1 실험 구조화)

**변경 내용**:
- §2.5 터널표준영상 정의 신규 추가 — `data/ps1204_kict_eSFR/` (47조건, eSFR 차트, 폴더명: `{조도}lx_{ISO}_{셔터속도}us_{속도kmh}`)
- 신규 실험 E1 → E1-1단계/E1-2단계로 분리
  - E1-1단계: 터널표준영상 → NR-IQA 7종 스코어 산출
  - E1-2단계: 터널표준영상 → BEW-H/BEW-V 측정 → NR-IQA 상관성 분석 (PLCC/SROCC)
- §3 RQ7: "MTF 이미지" → 터널표준영상 기반 E1-1단계/E1-2단계로 업데이트
- §5 F14 → F14a(NR-IQA 측정) / F14b(상관성 분석)으로 분리
- §6 Phase 1.5: E1 워크플로우 상세 흐름 추가
- §8 프로젝트 구조: `data/ps1204_kict_eSFR/` 추가
- §10.2 테스트 데이터: 터널표준영상(47조건) 항목 추가

---

## v04 — 2026-04-23

### ps2000_통합IQA.py v04 (DL-IQA 통합)

**변경 내용**:
- NR-IQA + DL-IQA + FR-IQA 통합 분석 구조 완성
- `DeepLearningIQA` 클래스 추가 — DBCNN + ARNIQA (pyiqa 기반)
- CUDA 자동 감지 (`_DL_AVAILABLE` 플래그 — torch/pyiqa 미설치 시 비활성화)
- `CONFIG["dl_iqa"]` 섹션 추가 (`enabled`, `device`)
- `--no_dl` argparse 인자 추가
- `_make_nr_desc_df()`에 dl_dbcnn, dl_arniqa 메트릭 행 추가
- 출력 요약: `NR: N개 | DL: 2개 | FR: N개` 형식

**pyproject.toml**:
- `[[tool.uv.index]]` cu128 explicit 설정
- `[tool.uv.sources]` torch/torchvision → pytorch-cu128 바인딩
- torch 버전 요건: `>=2.6.0` (cu128 인덱스 제공 범위)

---

## v03 (이전 세션)

- ps2000_통합IQA.py v03 기반 코드 존재 (DL-IQA 통합 전)
- NR-IQA (hsmb, cpbd, brisque, weighted_score) + FR-IQA (psnr, ssim) 구조
