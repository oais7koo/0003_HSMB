# TODO / 디버깅 이슈 — 0003_HSMB

## 진행 중

- [TODO] 필수 플러그인 설치 — Claude Code에서 수동 실행 필요: `/plugin marketplace add forrestchang/andrej-karpathy-skills` → `/plugin install andrej-karpathy-skills@forrestchang-andrej-karpathy-skills`
- [TODO] d0100 §4 Task A에서 현장 area-scan 파일 부분 확인 필요 — 1,500장 협업자 전달 자산 vs 실측 데이터(ps1010_chungsong_MTF frame 507장) 매칭/부족 분석 (2026-05-13 추가)
- [TODO] 본 연구 최종 목표 확인 필요 — 결국 HSMB가 BEW와의 상관성(PLCC/SROCC)을 높이도록 개선하는 것이 핵심 목표인지 PRD §1.2/§2 재검토 및 확정 (2026-05-13 추가)
- [TODO] `data/02_260422_HSMB논문 수정안/` 폴더 데이터 이철희 박사에게 다시 수령 필요 — 폴더 내 파일이 섞여있어 원본 패키지 재전달 요청 (2026-05-13 추가)
- [TODO] [medium] CPBD 정식 알고리즘으로 교체 — `src/ps2000_통합IQA.py:233-236 calculate_cpbd` 현재 Canny edge 픽셀 비율만 계산(간이판). PyPI `cpbd`(Narvekar & Karam 2011) 또는 pyiqa 도입 검토 (2026-05-15 추가)
- [TODO] [medium] NIQE/PIQE/BRISQUE 정식 메트릭으로 교체 — `src/ps2000_통합IQA.py:316-345` 세 메트릭 모두 간이 구현(NSS·SVR·블록통계 미적용). `pyiqa.create_metric("niqe"|"brisque")` 도입, PIQE는 MATLAB 또는 대체 라이브러리 조사 필요 (2026-05-15 추가)
- [TODO] [medium] 출력 CSV 컬럼명 d0100 §6.1 표준 헤더 매핑 — 현재 `niqe_simple`/`piqe_simple`/`dl_dbcnn`/`dl_arniqa` → 표준 `niqe`/`piqe`/`dbcnn`/`arniqa`로 통일. F002-1 산출물 호환성 확보 (2026-05-15 추가)
- [TODO] [low] F002-1 산출 CSV 7종 선별 — v04는 23개 NR 메트릭 계산 중. `task_A_metrics_per_frame.csv`/`task_A_metrics_per_condition.csv` 산출 시 d0100 §6.1 헤더(hsmb,cpbd,niqe,piqe,brisque,dbcnn,arniqa) 7종만 추출하는 필터/리포터 구현 (2026-05-15 추가)

---

## 완료 (→ d0010_history.md)

- [DONE] ps0010_new_iqa_lib.py HSMBCalculator 교체 및 검증 완료 — 기존 v2 계통(Scharr+CLAHE+Lap+FFT 융합) → ps5010 v1 정식 구현(Sobel+mean임계+순수 Weibull CDF)으로 교체. 15000lx-500us-00 이미지 01.png 기준 ps0010=0.8888, ps2010=0.8888 (Δ=0.0000). d0900 target(0.8893) Δ=0.0005. uv sync + ps5101 GPU 테스트 정상 확인 (2026-05-15 완료)
- [DONE] ps0010 7종 IQA 동작 검증 완료 — compute_all_from_path() 9컬럼 산출: hsmb✅ niqe✅ niqe_matlab✅ piqe✅ brisque✅ brisque_matlab✅ dbcnn✅ arniqa✅ cpbd✅(patch 적용 후). cpbd의 scipy.ndimage.imread 제거 이슈는 `scripts/patch_cpbd.py`로 해결 — `.venv/.../cpbd/compute.py` import를 cv2 fallback으로 교체. 절차: PRD §7.1 참조 (2026-05-15 완료)
- [DONE] ps2000_통합IQA.py HSMB 파라미터 PRD 사양으로 수정 완료 — `src/ps2000_통합IQA.py` 수정 내역: ① CONFIG threshold_ratio 0.3→0.1, beta 1.8→2.0, edge_weight 0.8→1.5 (line 99-101) ② JNB 하드코딩 2.5→3.0 (line 514) ③ p_jnb cumsum[45]→cumsum[63] (line 521). 근거: d1600 분석 — ps5010 v1(ew=1.5/β=2.0/JNB=3/cdf[63])이 PRD §4.1 사양과 완전 일치하며 PLCC -0.9532로 최고 성능. 참조: d1600_hsmb_기존값비교.md, d0900_hsmb_적합버전찾기.md (2026-05-15 완료)
- [DONE] pyproject.toml `[dependency-groups]` dev 그룹 검증 — 이미 정의됨(pytest/pylint/mypy/black/isort), `uv sync --group dev` 정상 동작 확인 (2026-05-13)
- [DONE] qmd 컬렉션 등록 — `oais` (C:\Users\oaiskoo\doom\1_oais, 13,907 files) + `code` (C:\Users\oaiskoo\doom\3_code, 1,693 files) (2026-05-13)
- [DONE] task-master-ai npm 글로벌 설치 — 0.43.1 (2026-05-13)
- [DONE] ooenv 스크립트 SP 경로 하드코딩 버그 수정 — flat 구조(OAIS_NO_SP=1 또는 sp00/ 부재) 자동 감지 로직 추가, ENV_REPORT_PATH 동적 결정 (2026-04-26)
- [DONE] ps2000_통합IQA.py v04 — DL-IQA (DBCNN + ARNIQA) 통합 (2026-04-23)
- [DONE] pyproject.toml — cu128 explicit index + [tool.uv.sources] 설정 (2026-04-23)
- [DONE] CUDA torch 2.11.0+cu128 동작 확인 — RTX 3070, CUDA available=True (2026-04-23)
- [DONE] ps2000_통합IQA.py GPU 전체 실행 — 940장, DL-IQA 포함, 결과 3파일 생성 (2026-04-23)

---

## 환경 메모

| 항목 | 내용 |
|------|------|
| GPU | RTX 3070 8GB |
| Driver | 581.57 |
| CUDA | 13.0 (12.x 하위호환) |
| 목표 torch | 2.11.0+cu128 |
| pip 명령 | `.venv/Scripts/pip install --force-reinstall --no-deps torch==2.11.0+cu128 torchvision==0.26.0+cu128 --index-url https://download.pytorch.org/whl/cu128` |
| cpbd 패치 | `uv sync`/`uv add` 후 **반드시** `uv run python scripts/patch_cpbd.py` 재실행 (cpbd compute.py의 scipy.ndimage.imread 제거 대응, 멱등). 절차: PRD §7.1 |
