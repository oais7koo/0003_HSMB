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
- [TODO] [low] d3010 §9 결과 해석 및 d0043 리포트 작성 — ps3011 상관분석 완료. HSMB↔MTF50_H PLCC=-0.44 (방향 불일치 해석 필요), arniqa↔R1090_H PLCC=-0.69 가장 강함. IQA 51조건 중 SFR 50조건 매칭(1개 불일치 확인 필요). 산출: `e3_1_sfr_metrics.csv`/`e3_1_correlation.csv`/scatter 2종 (2026-05-17 추가)
- [TODO] [low] [검토] DBCNN·ARNIQA 커스텀 IQA 모델(파인튜닝) 가능성 검토 — 현재 `common_iqa7.py`는 pyiqa pretrained(DBCNN=KonIQ10k, ARNIQA) 그대로 사용. 원 모델 backbone 다운로드 → 터널 모션블러 도메인 데이터로 파인튜닝 → 커스텀 IQA 모델로 지표 측정 가능 여부 검토. 검토 항목: ① MOS/품질 라벨 데이터 확보 방안 ② pyiqa 파인튜닝·재학습 지원 여부 ③ 논문 재투고 시 표준 pretrained 대비 커스텀 모델의 정당성·재현성 (2026-05-17 추가, 검토)

## 완료 (→ d0010_history.md)

- [DONE] ps3040 E3-4 ps1010+ps1301 통합 풀 IQA 완료 — E3-1(520행)+E3-2(737행) concat → 1,257행. 산출물: `data/ps3040/01_통합풀데이터_2605180538.xlsx`, `02_source별통계_*.xlsx`, `04_histogram_*.png`. 실행시간 1.44초 (IQA 재산출 없음) (2026-05-18 완료)
- [DONE] ps3020 E3-2 ps1301 실제크랙 IQA 분석 완료 — 737장/50조건 7종 NR-IQA 산출(center_crop=True). hsmb 평균=0.6132, defocus(ISO=400) 148프레임. 산출물: `data/ps3020/01~04_*_2605171829.{xlsx,png}`. 실행시간 4.9시간 (2026-05-17 완료)
- [DONE] ps3030 E3-3 ps1302 인쇄크랙 IQA 분석 완료 — 50장 7종 NR-IQA 산출(center_crop=True). 산출물: `data/ps3030/01_전체데이터_2605171728.xlsx`, `04_histogram_2605171728.png`. d3030 F002-6 ✅ (2026-05-17 완료)
- [DONE] ps3011 E3-1 SFR↔IQA 상관분석 스크립트 구현 및 실행 완료 — `src/ps3011_e3_1_sfr_correlation.py` 신규 작성. 50조건 SFR_cypx.csv 파싱(R1090/MTF50 H·V 평균) → IQA 9컬럼 조인 → PLCC/SROCC/KRCC 산출. 산출물: `e3_1_sfr_metrics.csv`, `e3_1_correlation.csv`, scatter 2종. 명세: d3010 §9 (2026-05-17 완료)
- [DONE] ps3010 E3-1 ps1010 IQA 분석 완료 — 520장/50조건 7종 NR-IQA 산출(hsmb/cpbd/niqe/piqe/brisque/dbcnn/arniqa). defocus(ISO=400) 102장 식별. 산출물: `data/ps3010/01~04_*_2605171535.{xlsx,png}`. 실행시간 34.5분, CUDA 사용 (2026-05-17 완료)
- [DONE] E3 스크립트 재부팅 복구성 강화 — `ps3010`/`ps3020` 체크포인트를 이미지 단위(`condition+frame`)로 변경, `ps3030` 체크포인트 원자적 저장·중복제거 적용, `ps3040` 단계 체크포인트(`_checkpoint_stage.json`, `_checkpoint_pool.csv`) + `--resume` 추가. 윈도우 재부팅/강제종료 후 체크포인트부터 재개 가능 (2026-05-17 완료)
- [DONE] common_iqa7.py HSMBCalculator 교체 및 검증 완료 — 기존 v2 계통(Scharr+CLAHE+Lap+FFT 융합) → ps5010 v1 정식 구현(Sobel+mean임계+순수 Weibull CDF)으로 교체. 15000lx-500us-00 이미지 01.png 기준 common_iqa7=0.8888, ps2010=0.8888 (Δ=0.0000). d0900 target(0.8893) Δ=0.0005. uv sync + ps5101 GPU 테스트 정상 확인 (2026-05-15 완료)
- [DONE] common_iqa7 7종 IQA 동작 검증 완료 — compute_all_from_path() 9컬럼 산출: hsmb✅ niqe✅ niqe_matlab✅ piqe✅ brisque✅ brisque_matlab✅ dbcnn✅ arniqa✅ cpbd✅(patch 적용 후). cpbd의 scipy.ndimage.imread 제거 이슈는 `scripts/patch_cpbd.py`로 해결 — `.venv/.../cpbd/compute.py` import를 cv2 fallback으로 교체. 절차: PRD §7.1 참조 (2026-05-15 완료)
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
| GPU | NVIDIA GeForce GTX 750 Ti 2GB (Compute Capability 5.0) |
| Driver | 566.14 |
| CUDA | 12.7 (12.x 하위호환) |
| 설치 torch | 2.11.0+cu128 (주의: CC 5.0 미지원, 호환 버전 재설치 검토 필요) |
| pip 명령 | (TBD) CC 5.0 지원용 구버전 또는 CPU 버전 검토 |
| cpbd 패치 | `uv sync`/`uv add` 후 **반드시** `uv run python scripts/patch_cpbd.py` 재실행 (cpbd compute.py의 scipy.ndimage.imread 제거 대응, 멱등). 절차: PRD §7.1 |

## 대기 ToDo

> `cctodo add` 명령으로 추가된 항목.

### ~~C001~~ [DONE] d0004 §환경 메모 GPU 정보 현행화 — RTX 3070(CC 8.6) → GTX 750 Ti(CC 5.0) 수정 완료 (2026-05-17)

### C002 [CHECK] 타 컴퓨터에서 ps3010~ps3040 재시작(체크포인트) 검증 절차
#### 등록일: 2026-05-17 | 우선순위: high
#### ToDo 내용
1) 사전 준비
- OS: Windows 10/11 PowerShell
- 작업경로: `C:\Users\oaiskoo\doom\3_code\0003_HSMB`
- 의존성: `uv sync`
- cpbd 패치: `uv run python scripts/patch_cpbd.py`

2) 테스트 데이터 최소셋 준비(빠른 검증용)
- ps3010: `data/ps1010_chungsong_MTF/`에서 임의 조건 1~2개 폴더 유지
- ps3020: `data/ps1301_real_crack_cam2/`에서 임의 조건 1~2개 폴더 유지
- ps3030: `data/ps1302_print_crack/`에서 `cam1_*.png` 10장 내외 유지
- ps3040: ps3010/ps3020 결과 xlsx가 존재해야 함

3) 강제 중단 후 재개 검증(핵심)
- ps3010 실행: `python src/ps3010_e3_1_ps1010_iqa.py --device cpu`
- 1~2분 후 강제 종료: `Ctrl+C` 또는 프로세스 종료
- 체크포인트 확인: `data/ps3010/_checkpoint.csv` 생성/행 증가 확인
- 재개 실행: `python src/ps3010_e3_1_ps1010_iqa.py --resume --device cpu`
- 기대결과: 이미 처리된 `condition+frame` 중복 없이 이어서 완료

- ps3020 실행/중단/재개도 동일:
  - `python src/ps3020_e3_2_ps1301_iqa.py --device cpu`
  - `python src/ps3020_e3_2_ps1301_iqa.py --resume --device cpu`
  - 체크포인트: `data/ps3020/_checkpoint.csv`

- ps3030 실행/중단/재개도 동일:
  - `python src/ps3030_e3_3_ps1302_iqa.py --device cpu`
  - `python src/ps3030_e3_3_ps1302_iqa.py --resume --device cpu`
  - 체크포인트: `data/ps3030/_checkpoint.csv`
  - 기대결과: `filename` 기준 중복 제거, 원자적 저장으로 파일 손상 없음

4) ps3040 단계 체크포인트 검증
- 실행: `python src/ps3040_e3_4_pool_iqa.py`
- 중간 강제 종료 후 재개: `python src/ps3040_e3_4_pool_iqa.py --resume`
- 체크파일 확인:
  - `data/ps3040/_checkpoint_stage.json` (`stage=merged|saved`)
  - `data/ps3040/_checkpoint_pool.csv`
- 기대결과: 병합 완료 이후에는 재병합 없이 저장 단계부터 진행

5) 중복/정합 검증
- ps3010/3020/3030 체크포인트 중복 점검
  - `condition+frame`(ps3010/3020), `filename`(ps3030) 중복 0건
- 최종 산출물 생성 확인
  - ps3010: `01/02/03/04_*`
  - ps3020: `01/02/03/04_*`
  - ps3030: `01/04_*`
  - ps3040: `e3_4_pool_manifest.csv`, `01/02/04_*`

6) 장애 원인 추적(타 컴퓨터에서 재부팅/종료 발생 시)
- 발생 시각 기록(초 단위)
- 직후 이벤트 로그 수집:
  - `Get-WinEvent`로 `Kernel-Power(41)`, `EventLog(6008)`, `WHEA`, `BugCheck(1001)` 추출
- GPU 경로 의심 시 CPU 고정 재실행으로 비교
  - `--device cpu`에서 안정, GPU에서만 종료되면 CUDA/드라이버 이슈로 분류

7) 검증 완료 기준(Exit Criteria)
- 각 스크립트 1회 이상 강제 중단 후 `--resume` 성공
- 체크포인트 파일 손상/중복 없음
- 최종 산출물 정상 생성
- 재부팅/강제종료 발생 시 이벤트 로그 근거 확보
