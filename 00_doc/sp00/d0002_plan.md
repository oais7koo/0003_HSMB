# HSMB v2 NR-IQA 논문 재투고 — 구현 계획

> PRD: `00_doc/sp00/d0001_prd.md` v05 참조 | 생성: `ooplan run` (Track 1 전체)

## 1. 문서이력관리

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v02 | 2026-05-15 | PRD v06 동기화 — E002에 F002-4~7 (E3 실험군 4건) 추가, S1~S3 스프린트 재배치 |
| v01 | 2026-04-26 | 초기 생성 — Track 1 전체(Phase 1~4) WBS 분해, 모두 미착수 가정 |

---

## 2. 구현 개요

> PRD d0001 §2 참조 (목적·범위 반복 기재 금지)

| 항목 | 내용 |
|------|------|
| 대상 트랙 | **Track 1만** (재투고) — Track 2(v2 알고리즘 개선)는 별도 plan으로 분리 |
| 구현 관점 목적 | v1 알고리즘 동결 상태에서 **Reviewer C3·C4 대응 근거**와 **신규 실험 결과**를 산출하여 논문 재작성 가능 상태로 만든다 |
| 우선순위 | Phase 1 (분석) ‖ Phase 1.5 (실험) → Phase 2 (보강) → Phase 3 (협업 통합, 외부 트리거) → Phase 4 (작성) |
| Out-of-Scope | F04, F05 (v2 알고리즘) — Track 2 / F13 (추가 데이터셋) — TBD |

---

## 3. WBS — Epic / Feature / Task

> PRD §5 기능요구사항(F01~F15) 기반 분해. F04, F05는 Track 2 이관으로 제외.

### E001. v1 기반 분석 (Phase 1)

| Feature ID | 기능명 | PRD 매핑 | 우선순위 | 상태 |
|-----------|--------|---------|:-------:|------|
| F001-1 | v1 코드 서머리 | F01 | Must | ⚪ |
| F001-2 | 선행연구 서베이 | F02 | Must | ⚪ |
| F001-3 | v1 ablation study (C4) | F03 | Must | ⚪ |

#### F001-1. v1 코드 서머리

| Task ID | 내용 | 산출물 |
|---------|------|--------|
| F001-1.1 | `data/01_기존/` 74개 스크립트 인벤토리 작성 | `tmp/v1_inventory.csv` |
| F001-1.2 | 핵심 알고리즘 버전 계통 추적 (HSMB v1 final 식별) | `00_doc/sp00/d0007_v1_lineage.md` |
| F001-1.3 | v1 정리·모듈화 → `src/hsmb/v1.py` | `src/hsmb/v1.py` + 단위테스트 |

#### F001-2. 선행연구 서베이

| Task ID | 내용 | 산출물 |
|---------|------|--------|
| F001-2.1 | NR-IQA 분야 SOTA 정리 (2020~2026) | `00_doc/sp00/d0020_survey_nr_iqa.md` |
| F001-2.2 | 모션블러 특화 메트릭 정리 | 위 문서 §모션블러 |
| F001-2.3 | 터널검사·downstream(crack) 관련 정리 | 위 문서 §downstream |

#### F001-3. v1 ablation study (C4 대응)

| Task ID | 내용 | 산출물 |
|---------|------|--------|
| F001-3.1 | 파라미터 grid 정의 (EdgeWeight, JNB, β) | `src/hsmb/ablation.py` |
| F001-3.2 | 50조건 데이터에 grid 실행 → PLCC/SROCC 매트릭스 | `data/exp/ablation_results.csv` |
| F001-3.3 | 민감도 분석 + 최적값 이론 근거 작성 | `00_doc/sp00/d0030_ablation_report.md` |

### E002. 신규 실험 (Phase 1.5, Phase 1과 병행)

| Feature ID | 기능명                   | PRD 매핑 | 우선순위 | 상태            |
| ---------- | --------------------- | ------ | :--: | ------------- |
| F002-1     | E1-1 NR-IQA 측정 (47조건) | F14a   | Must | ⚪ ← **다음 작업** |
| F002-2     | E1-2 BEW 상관 분석        | F14b   | Must | ⚪             |
| F002-3     | E2 HSMB-크랙검출 상관       | F15    | Must | ⚪             |
| F002-4     | E3-1 ps1010 IQA 분석    | F16a   | Must | ⚪             |
| F002-5     | E3-2 ps1301 IQA 분석    | F16b   | Must | ⚪             |
| F002-6     | E3-3 ps1302 IQA 분석    | F16c   | Must | ⚪             |
| F002-7     | E3-4 ps1010+ps1301 통합 풀 IQA | F16d | Must | ⚪          |

#### F002-1. E1-1 NR-IQA 측정 (다음 작업)

| Task ID | 내용 | 산출물 |
|---------|------|--------|
| F002-1.1 | `ps2000_통합IQA.py` v04를 47조건 폴더 일괄 실행으로 확장 | `src/ps2000_batch_runner.py` |
| F002-1.2 | NR-IQA 7종 스코어 산출 (HSMB + 비교 6종) | `data/exp/e1_iqa_scores.csv` |
| F002-1.3 | 조건별(조도×ISO×셔터속도×속도) 집계표 생성 | `00_doc/sp00/d0040_e1_scores.md` |

#### F002-2. E1-2 BEW 상관 분석

| Task ID | 내용 | 산출물 |
|---------|------|--------|
| F002-2.1 | 47조건 BEW-H, BEW-V 측정 | `data/exp/e1_bew.csv` |
| F002-2.2 | NR-IQA × BEW scatter + PLCC/SROCC 산출 | `00_doc/sp00/d0041_e1_correlation.md` + figures |
| F002-2.3 | 이방성 분석 (BEW_H − BEW_V), defocus 케이스 검증 | 위 문서 §이방성 |

#### F002-3. E2 HSMB-크랙검출 상관

| Task ID | 내용 | 산출물 |
|---------|------|--------|
| F002-3.1 | 보유 DL crack detection 모델 환경 구성 | `src/crack_detector/` |
| F002-3.2 | 샘플 이미지 추론 → 이미지별 F1 산출 | `data/exp/e2_crack_f1.csv` |
| F002-3.3 | HSMB × F1 scatter + 상관계수 분석 | `00_doc/sp00/d0042_e2_correlation.md` |

#### F002-4. E3-1 ps1010 IQA 분석 (PRD F16a)

| Task ID | 내용 | 산출물 |
|---------|------|--------|
| F002-4.1 | `ps2000_batch_runner.py` 입력 인자에 `ps1010_chungsong_MTF/` 추가 | runner 수정 |
| F002-4.2 | 50조건 frame 507장 → 7종 NR-IQA 스코어 일괄 산출 | `data/exp/e3_1_ps1010_iqa.csv` |
| F002-4.3 | 조건별·전체 기술통계 + 히스토그램 리포트 | `00_doc/sp00/d0043_e3_1_ps1010.md` |

#### F002-5. E3-2 ps1301 IQA 분석 (PRD F16b)

| Task ID | 내용 | 산출물 |
|---------|------|--------|
| F002-5.1 | ps1301(45GB) 샘플링 전략 결정 (전수/N장 랜덤/계층 샘플) | 결정 노트 |
| F002-5.2 | 7종 NR-IQA 일괄 산출 (GPU 메모리·런타임 모니터) | `data/exp/e3_2_ps1301_iqa.csv` |
| F002-5.3 | 기술통계 + 히스토그램 리포트 | `00_doc/sp00/d0044_e3_2_ps1301.md` |

#### F002-6. E3-3 ps1302 IQA 분석 (PRD F16c)

| Task ID | 내용 | 산출물 |
|---------|------|--------|
| F002-6.1 | ps1302 입력 인자 추가, 7종 NR-IQA 일괄 산출 | `data/exp/e3_3_ps1302_iqa.csv` |
| F002-6.2 | 기술통계 + 히스토그램 리포트 (controlled 비교군) | `00_doc/sp00/d0045_e3_3_ps1302.md` |

#### F002-7. E3-4 ps1010+ps1301 통합 풀 IQA (PRD F16d)

| Task ID | 내용 | 산출물 |
|---------|------|--------|
| F002-7.1 | ps1010 + ps1301 이미지 풀 통합 입력 경로 구성 (심볼릭/manifest CSV) | `data/exp/e3_4_pool_manifest.csv` |
| F002-7.2 | 통합 풀에 대한 7종 NR-IQA 일괄 산출 | `data/exp/e3_4_pool_iqa.csv` |
| F002-7.3 | 개별 E3-1·E3-2 결과 vs 통합 풀 분포 대조 리포트 (혼합 풀 특성 분석) | `00_doc/sp00/d0046_e3_4_pool.md` |

### E003. 논문 보강 (Phase 2)

| Feature ID | 기능명 | PRD 매핑 | 우선순위 | 상태 |
|-----------|--------|---------|:-------:|------|
| F003-1 | v1 50조건 전체 벤치마크 | F06 | Must | ⚪ |
| F003-2 | Complex-blur stress test | F11 | Should | ⚪ |

#### F003-1. v1 50조건 전체 벤치마크

| Task ID | 내용 | 산출물 |
|---------|------|--------|
| F003-1.1 | 50조건 ground_truth 수령·검증 | `data/exp/gt_50.csv` |
| F003-1.2 | v1 알고리즘 고정 실행 → PLCC/SROCC 재현 | `data/exp/v1_50_results.csv` |
| F003-1.3 | 공개 IQA 데이터셋 평가 (MMP-2K, TID2013) | 위 결과 + 논문 §V-D 표 |

#### F003-2. Complex-blur stress test

| Task ID | 내용 | 산출물 |
|---------|------|--------|
| F003-2.1 | ISO=400 조건 데이터 별도 분리 | `data/exp/complex_blur_subset/` |
| F003-2.2 | HSMB 응답성·모노토닉 분석 | `00_doc/sp00/d0050_complex_blur.md` |
| F003-2.3 | 의도적 defocus 서술 정정 (PRD §2.6) | `260422_HSMB논문 수정안/docs/section06_draft.md` 수정 |

### E004. 협업 결과 통합 (Phase 3, 외부 트리거)

> **트리거 조건**: KICT Chulhee Lee Task A·B 결과 수령 (TBD-5 일정 미정)

| Feature ID | 기능명 | PRD 매핑 | 우선순위 | 상태 |
|-----------|--------|---------|:-------:|------|
| F004-1 | downstream 분석 지원 (C3) | F07 | Must | ⚪ blocked |
| F004-2 | §V-E 신규 작성 | F08 | Must | ⚪ blocked |
| F004-3 | §VI-B·C 완성 | F09 | Must | ⚪ blocked |

#### F004-1. downstream 분석 지원 (C3 대응)

| Task ID | 내용 | 산출물 |
|---------|------|--------|
| F004-1.1 | Task B 결과 수령·검증 | `data/exp/task_b_crack_results/` |
| F004-1.2 | HSMB threshold pre-filtering 효과 분석 | `00_doc/sp00/d0060_downstream_analysis.md` |

#### F004-2. §V-E 신규 작성

| Task ID | 내용 | 산출물 |
|---------|------|--------|
| F004-2.1 | crack detection 실험 결과 섹션 초안 | `260422_HSMB논문 수정안/docs/section_v_e_draft.md` |
| F004-2.2 | Figure·Table 생성 | `figures/v_e_*.png` |

#### F004-3. §VI-B·C 완성

| Task ID | 내용 | 산출물 |
|---------|------|--------|
| F004-3.1 | Task A 결과 수령 → §VI-B 통합 | `260422_HSMB논문 수정안/docs/section06_draft.md` |
| F004-3.2 | E1-2 결과 → §VI-C 완성 | 위 문서 §VI-C |

### E005. 논문 작성·투고 (Phase 4)

| Feature ID | 기능명 | PRD 매핑 | 우선순위 | 상태 |
|-----------|--------|---------|:-------:|------|
| F005-1 | 논문 전체 재작성 | F10 | Must | ⚪ blocked |
| F005-2 | 투고 준비 | F10 | Must | ⚪ blocked (TBD-1 저널 결정) |

#### F005-1. 논문 전체 재작성

| Task ID | 내용 | 산출물 |
|---------|------|--------|
| F005-1.1 | §I~§VII 구조 재정비 | `260422_HSMB논문 수정안/docs/full_draft_v2.md` |
| F005-1.2 | Reviewer 응답서 작성 (C1~C4 대응) | `260422_HSMB논문 수정안/docs/response_to_reviewers.md` |
| F005-1.3 | 협저자 검토·수정 사이클 | 위 draft v2~vN |

#### F005-2. 투고 준비

| Task ID | 내용 | 산출물 |
|---------|------|--------|
| F005-2.1 | 목표 저널 결정 + 양식 변환 (LaTeX/Word) | `submission/{journal}/manuscript.{ext}` |
| F005-2.2 | Cover letter, supplementary materials | `submission/{journal}/cover_letter.md` |
| F005-2.3 | 투고 시스템 업로드 | submission record |

---

## 4. 스프린트 계획

> 협업자 일정(TBD-5) 미정으로 날짜는 명목적. 실제 시작 시 `ooplan sync`로 갱신.

| Sprint | 명목 기간 | 목표 | Feature |
|--------|----------|------|---------|
| **S1** | W1~W2 | E1-1·E3-1 실행 + v1 인벤토리 | F002-1, F002-4, F001-1 |
| S2 | W3~W4 | E1-2 BEW 상관 + E3-2·E3-3 IQA + 선행연구 정리 | F002-2, F002-5, F002-6, F001-2 |
| S3 | W5~W6 | E2 크랙검출 상관 + E3-4 통합 풀 IQA + ablation 그리드 정의 | F002-3, F002-7, F001-3 (3.1) |
| S4 | W7~W8 | ablation 실행·분석 (C4 근거 확립) | F001-3 (3.2~3.3) |
| S5 | W9~W10 | 50조건 v1 벤치마크 + complex-blur | F003-1, F003-2 |
| **S6** | trigger | 협업자 결과 통합 (외부 일정 종속) | F004-1, F004-2, F004-3 |
| S7 | trigger+2W | 논문 전체 draft v2 | F005-1 |
| S8 | trigger+4W | 협저자 검토 → 투고 | F005-1 (1.3), F005-2 |

> **마일스톤**: M1=E1·E2 완료(S3) / M2=Phase 1 완료(S5) / M3=draft v2 완성(S7) / M4=투고(S8)

---

## 5. 기술 설계

### 5.1 아키텍처

```
src/hsmb/                        # 알고리즘 코어 (모듈화 신규)
  ├── v1.py                      # v1 알고리즘 (data/01_기존/에서 정리·이관)
  ├── metrics.py                 # 비교 NR-IQA 6종 래퍼 (pyiqa 활용)
  ├── ablation.py                # 파라미터 grid 실행
  └── benchmark.py               # 데이터셋 평가 파이프라인

src/                              # 실행 스크립트 (현재 ps2000 존재)
  ├── ps2000_통합IQA.py          # 단일 실행 (기존 v04, 유지)
  ├── ps2000_batch_runner.py     # 47조건 일괄 실행 (신규)
  ├── crack_detector/            # E2 DL 모델 래퍼 (신규)
  └── ps5101_pytorch_gpu_test_v01.py  # GPU 검증 (기존)

data/exp/                         # 실험 결과 누적 폴더 (신규)
  ├── ablation_results.csv
  ├── e1_iqa_scores.csv
  ├── e1_bew.csv
  ├── e2_crack_f1.csv
  ├── e3_1_ps1010_iqa.csv          # E3-1 ps1010 7종 NR-IQA
  ├── e3_2_ps1301_iqa.csv          # E3-2 ps1301 7종 NR-IQA
  ├── e3_3_ps1302_iqa.csv          # E3-3 ps1302 7종 NR-IQA
  ├── e3_4_pool_manifest.csv       # E3-4 ps1010+ps1301 통합 풀 manifest
  ├── e3_4_pool_iqa.csv            # E3-4 통합 풀 7종 NR-IQA
  ├── v1_50_results.csv
  └── complex_blur_subset/

tests/                            # pytest (신규)
  ├── test_hsmb_v1.py
  ├── test_metrics.py
  └── test_ablation.py
```

### 5.2 기술 스택 상세

| 구분 | 기술 | 버전 | 용도 |
|------|------|------|------|
| 언어 | Python | 3.13 | 전체 |
| 패키지 관리 | uv | latest | cu128 explicit index |
| 수치/이미지 | numpy, scipy, opencv-python-headless | 4.13+ | Sobel, EVP |
| NR-IQA | pyiqa | 0.1.15+ | 비교 메트릭 6종 |
| 딥러닝 | torch, torchvision | 2.11.0+cu128 | E2 크랙검출 |
| 데이터 | pandas, openpyxl | latest | CSV/XLSX |
| 시각화 | matplotlib | 3.10+ | 논문 figure |
| 통계 | scipy.stats | (포함) | PLCC, SROCC |
| 테스트 | pytest | latest | unit + regression |
| 코드 품질 | pylint, mypy, black, isort | latest | dev 그룹 (todo F-1) |

> **GPU**: RTX 3070 8GB, CUDA 13.0 (cu128 호환). 검증 완료.

### 5.3 폴더 구조 (변경 후)

위 §5.1 참조. 핵심: `src/hsmb/` 패키지 신설 + `data/exp/` 결과 누적.

### 5.4 주요 모듈

| 파일 | 함수/클래스 | 역할 |
|------|-----------|------|
| `src/hsmb/v1.py` | `compute_hsmb(img) -> float` | v1 알고리즘 단일 진입점 |
| `src/hsmb/v1.py` | `compute_bew_hv(img) -> tuple[float, float]` | BEW-H, BEW-V 측정 |
| `src/hsmb/metrics.py` | `compute_all_nr_iqa(img) -> dict[str, float]` | 7종 NR-IQA 일괄 |
| `src/hsmb/ablation.py` | `run_ablation_grid(dataset, grid) -> DataFrame` | 파라미터 그리드 실행 |
| `src/hsmb/benchmark.py` | `evaluate_on_dataset(metric_fn, gt) -> dict` | PLCC/SROCC 산출 |
| `src/ps2000_batch_runner.py` | `__main__` | E1-1 실행 진입점 |

### 5.5 DB 스키마

해당 없음 (실험 결과는 CSV·XLSX·MD로 관리).

---

## 6. 리스크

| ID | 리스크 | 영향도 | 대응 방안 |
|----|--------|:-----:|----------|
| R01 | 협업자(KICT) Task A·B 결과 지연 → Phase 3·4 블록 | **고** | Phase 1·1.5·2를 협업자 무관 트랙으로 우선 완주, S6 트리거 대기 |
| R02 | v1 코드(90 스크립트)에서 final 버전 식별 불명확 | 중 | F001-1.2에서 git log + 파일 mtime + 결과 CSV 일치성 교차 검증 |
| R03 | E1-1 47조건 일괄 실행 시간(GPU) 과다 | 중 | 조건별 분할 실행 + 중간 체크포인트 CSV 저장 (이미 940장 30분 내외 입증) |
| R04 | ablation grid 폭발 (3 파라미터 × 50조건 × N grid) | 중 | 각 파라미터 grid 5~7점으로 제한, 50조건은 stratified subset 사용 |
| R05 | Reviewer C4 이론적 근거 — 사후 정당화로 보일 위험 | 중 | ablation 결과로 경험적 최적값 제시 + JNB 원논문 인용 보강 |
| R06 | 의도적 defocus 서술 누락 시 일관성 깨짐 | 중 | F003-2.3에서 §VI-C 전면 수정 + 체크리스트화 |
| R07 | 목표 저널 미결(TBD-1) → S8 양식 변환 시점 불확실 | 저 | M3 시점에서 저널 재선정 review |
| R08 | dev 그룹 도구 미설치(pylint 등) → 코드 품질 게이트 약함 | 저 | `pyproject.toml`에 `[dependency-groups]` 추가 (todo) |
| R09 | ps1301(45GB) 전수 IQA 산출 시 GPU·디스크 시간 과다 | 중 | F002-5.1에서 샘플링 전략 선결정 (계층 샘플 N장 권장), GPU 배치 + 중간 체크포인트 |
| R10 | E3-4 통합 풀 manifest 구성 시 파일명 충돌 (ps1010·ps1301 동일 이름) | 저 | manifest CSV에 출처(`source_ps`) 컬럼 + 원본 절대경로 보존 |

---

## 7. 의사결정 로그

| 날짜 | 결정 사항 | 근거 |
|------|----------|------|
| 2026-04-22 | HSMB v1 알고리즘 동결, 재투고 우선 | PRD §2.3 — 변경 시 모든 수치 재실험 비용 |
| 2026-04-22 | v2 개선은 Track 2(후속 논문)로 분리 | 동상 |
| 2026-04-24 | 터널표준영상(`ps1204_kict_eSFR/`) E1 실험 도입 | PRD v05 — Reviewer 추가 증거 보강 |
| 2026-04-22 | ISO 400 조건을 "의도적 defocus"로 재해석 | PRD §2.6 — 이방성 분석으로 검증 |
| 2026-04-26 | Plan 범위 = Track 1 전체, 모두 미착수 가정 | 사용자 확인 (ooplan run) |
| 2026-04-26 | `src/hsmb/` 패키지 신설 (현재 단일 스크립트 → 모듈화) | 단위테스트·재사용성 + PRD §8 목표 구조 |
| 2026-04-26 | 스프린트 단위 = 명목 2주, 협업자 일정 시 trigger 방식 | TBD-5 일정 미정 대응 |
| 2026-05-15 | E3 4건(F16a~d)을 E002 Epic에 통합 — 별도 Epic 신설 대신 기존 신규 실험 그룹 확장 | E1·E2와 동일 인프라(ps2000_batch_runner) 재사용 가능 |
| 2026-05-15 | E3-4 "결합"의 의미를 데이터 통합 풀로 확정 (분포 대조 아님) | PRD v06 §2.7.2 사용자 확인 (2026-05-15) |

---

## 8. 진행추적

### 8.1 Feature 목록

| Feature ID | 기능명 | Epic | 우선순위 | PRD | 상태 |
|-----------|--------|------|:-------:|------|------|
| F001-1 | v1 코드 서머리 | E001 | Must | F01 | ⚪ |
| F001-2 | 선행연구 서베이 | E001 | Must | F02 | ⚪ |
| F001-3 | v1 ablation study | E001 | Must | F03 | ⚪ |
| F002-1 | E1-1 NR-IQA 측정 | E002 | Must | F14a | ⚪ ← 다음 |
| F002-2 | E1-2 BEW 상관 분석 | E002 | Must | F14b | ⚪ |
| F002-3 | E2 HSMB-크랙검출 상관 | E002 | Must | F15 | ⚪ |
| F002-4 | E3-1 ps1010 IQA 분석 | E002 | Must | F16a | ⚪ |
| F002-5 | E3-2 ps1301 IQA 분석 | E002 | Must | F16b | ⚪ |
| F002-6 | E3-3 ps1302 IQA 분석 | E002 | Must | F16c | ⚪ |
| F002-7 | E3-4 ps1010+ps1301 통합 풀 IQA | E002 | Must | F16d | ⚪ |
| F003-1 | v1 50조건 벤치마크 | E003 | Must | F06 | ⚪ |
| F003-2 | Complex-blur stress test | E003 | Should | F11 | ⚪ |
| F004-1 | downstream 분석 지원 | E004 | Must | F07 | ⚪ blocked |
| F004-2 | §V-E 신규 작성 | E004 | Must | F08 | ⚪ blocked |
| F004-3 | §VI-B·C 완성 | E004 | Must | F09 | ⚪ blocked |
| F005-1 | 논문 전체 재작성 | E005 | Must | F10 | ⚪ blocked |
| F005-2 | 투고 준비 | E005 | Must | F10 | ⚪ blocked |

> **상태 아이콘**: ⚪미착수 / 🟡진행중 / 🟢검증 / ✅완료 / blocked = 외부 트리거 대기

### 8.2 상세 문서 현황

> 2026-04-26 — 13개 Feature 상세기획 일괄 생성 (`oofeature` 직접 작성). 단계 진행 시 `oofeature next dXXXX`로 rename.

| 문서번호 | 기능명 | 단계 | 연결 Feature | 파일 |
|---------|--------|:----:|-------------|------|
| d1010 | 청송 MTF 데이터셋 | ⚪ | F002 입력 | `d1010_상세기획_청송_MTF_데이터셋.md` |
| d9010 | v1 코드 서머리 | ⚪ | F001-1 | `d9010_상세기획_v1_코드_서머리.md` |
| d9020 | 선행연구 서베이 | ⚪ | F001-2 | `d9020_상세기획_선행연구_서베이.md` |
| d9030 | v1 ablation study | ⚪ | F001-3 | `d9030_상세기획_v1_ablation_study.md` |
| d9040 | E1-1 NR-IQA 측정 | ⚪ | F002-1 | `d9040_상세기획_E1_1_NR_IQA_측정.md` |
| d9050 | E1-2 BEW 상관 분석 | ⚪ | F002-2 | `d9050_상세기획_E1_2_BEW_상관_분석.md` |
| d9060 | E2 HSMB-크랙검출 상관 | ⚪ | F002-3 | `d9060_상세기획_E2_HSMB_크랙검출_상관.md` |
| d3010 | E3-1 ps1010 IQA 분석 | ⚪ | F002-4 | `d3010_상세기획_E3_1_ps1010_IQA.md` |
| d2080 | E3-2 ps1301 IQA 분석 | ⚪ | F002-5 | `d2080_상세기획_E3_2_ps1301_IQA.md` (예정) |
| d2090 | E3-3 ps1302 IQA 분석 | ⚪ | F002-6 | `d2090_상세기획_E3_3_ps1302_IQA.md` (예정) |
| d2100 | E3-4 ps1010+ps1301 통합 풀 IQA | ⚪ | F002-7 | `d2100_상세기획_E3_4_pool_IQA.md` (예정) |
| d9070 | v1 50조건 벤치마크 | ⚪ | F003-1 | `d9070_상세기획_v1_50조건_벤치마크.md` |
| d9080 | Complex-blur stress test | ⚪ | F003-2 | `d9080_상세기획_complex_blur_stress_test.md` |
| d9090 | downstream 분석 지원 | ⚪ | F004-1 | `d9090_상세기획_downstream_분석_지원.md` |
| d9100 | §V-E 신규 작성 | ⚪ | F004-2 | `d9100_상세기획_section_V_E_신규_작성.md` |
| d9110 | §VI-B·C 완성 | ⚪ | F004-3 | `d9110_상세기획_section_VI_BC_완성.md` |
| d5010 | 논문 전체 재작성 | ⚪ | F005-1 | `d5010_상세기획_논문_전체_재작성.md` |
| d5020 | 투고 준비 | ⚪ | F005-2 | `d5020_상세기획_투고_준비.md` |

**단계 아이콘**: ⚪기획 → 🔵설계 → 🟡개발 → 🟢검증 → ✅완료

---

> 참조: `00_doc/sp00/d0001_prd.md` (PRD v05) | `00_doc/sp00/d0004_todo.md` (이슈) | `00_doc/sp00/d0009_env.md` (환경) | `00_doc/sp00/d0010_history.md` (이력)
