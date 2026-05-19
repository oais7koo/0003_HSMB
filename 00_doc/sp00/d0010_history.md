# 변경 이력 — 0003_HSMB

## v06 — 2026-05-19

### IQA 분석 및 상관성 검증 (E3 실험군)

**변경 내용**:
- ps3011 SFR↔IQA 상관 속도별 재분석 — 속도 그룹별(all/60km/80km) 분리 산출, 결과 차이 미미함 확인.
- ps3100 E1-1 터널표준영상(ps1204) IQA 분석 완료 — 47조건 470장, hsmb 평균=0.8316.
- ps3020/ps3030 center crop 50% 적용 — 대용량 대응을 위한 가로/세로 중앙 영역 추출 로직 추가.
- ps3040 E3-4 ps1010+ps1301 통합 풀 IQA 완료 — 1,257행 통합 데이터셋 구축.
- ps3010 E3-1 ps1010 IQA 분석 완료 — 50조건 520장 산출.
- E3 스크립트(ps3010~3040) 재부팅 복구성 강화 — 이미지 단위 체크포인트 및 `--resume` 기능 구현.
- d0004 환경 메모 GPU 정보 현행화 — 실제 장착된 GTX 750 Ti(CC 5.0) 사양으로 문서 수정.

---

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
