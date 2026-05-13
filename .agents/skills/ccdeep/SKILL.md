---
name: ccdeep
description: "공통 가이드: .claude/guides/common_guide.md | 컨텍스트: .claude/skills/oocontext/SKILL.md"
---

<!-- ccporting:generated-from-upstream -->
<!-- 원본 Claude 스킬은 upstream/ 폴더에 보관된다. -->

> 공통 가이드: .claude/guides/common_guide.md | 컨텍스트: .claude/skills/oocontext/SKILL.md

## 0. 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | PyTorch 딥러닝 코드 GPU 효율성 모니터링 및 자동 최적화 반복 사이클 |
| **하는 것** | 학습 실행, GPU 효율 모니터링, 비효율 감지 시 코드 최적화, 최대 5회 반복 |
| **하지 않는 것** | 일반 코드 최적화(→ooopti), 의존성 관리(→oouv), 모델 평가(→ooresearch) |
| **참조 범위** | 현재 프로젝트 내부 파일만 (PyTorch 코드) / 외부 데이터셋 자동 다운로드 안 함 |
| **수정 대상** | PyTorch 학습 코드 파일 |
| **실행 레벨** | [자동] — 실행→모니터링→판단→최적화→재실행 자동 사이클 |
| **에이전트 호환** | Claude Code 권장 — GPU 환경에서 `uv run` 자동 실행 / 다른 에이전트: GPU 모니터링 결과를 수동 확인 후 최적화 적용 |

## 문서 이력 관리
- v01 2026-03-24 — 문서이력 섹션 추가 (ooskill run 자동)

---

## 1. 개요

PyTorch 딥러닝 코드 실행 시 GPU 효율성을 자동 모니터링하고, 비효율 감지 시 코드를 최적화하는 반복 사이클 스킬.

**핵심 사이클**: 실행 -> 모니터링 -> 판단 -> 중단 -> 최적화 -> 재실행 (최대 5회)

## 2. 서브명령어

| 명령어 | 설명 |
|--------|------|
| `ccdeep help` | 서브명령어 목록 표시 |
| `ccdeep version` | 스킬 버전 정보 (v01) |
| `ccdeep status` | 서브명령어 리스트, GPU 현황 |
| `ccdeep check` | references/checklist.md 기반 검증 |
| `ccdeep check [script]` | references/checklist.md 기반 체크 및 리포팅 / 스크립트 GPU 효율성 사전 분석 (실행 없음) | 터미널 |
| `ccdeep show checklist` | 역할 수행 체크리스트 표시 |
| `ccdeep add checklist "항목"` | 체크리스트 항목 추가 |
| `ccdeep run [script]` | 딥러닝 스크립트 실행 + GPU 최적화 사이클 |
| `ccdeep run [script] --max-iter N` | 최대 반복 횟수 지정 (기본: 5) |
| `ccdeep run [script] --interval N` | 모니터링 간격 초 (기본: 30) |
| `ccdeep run [script] --threshold N` | GPU 사용률 임계값 % (기본: 50) |
| `ccdeep monitor` | GPU 상태만 모니터링 (수정 없음) |

## 3. GPU 효율성 판단 기준

| 지표 | 비효율 기준 | 측정 도구 |
|------|------------|----------|
| GPU Utilization | < 50% (임계값 조정 가능) | nvidia-smi |
| GPU Memory Usage | 전체 메모리 대비 < 30% 사용 | nvidia-smi |

**판단 로직**: 30초 간격으로 3회 연속 샘플링 → 평균값이 임계값 미만이면 비효율로 판단

## 4. 최적화 사이클 워크플로우

```
ccdeep run train.py
    |
    |-> 1. 사전 분석 (코드 읽기, GPU 환경 확인)
    |-> 2. 스크립트 실행 (백그라운드)
    |-> 3. GPU 모니터링 (30초 간격, 3회 샘플링)
    |-> 4. 효율성 판단
    |       ├─ 양호 (>= 임계값): 실행 계속, 주기적 모니터링
    |       └─ 비효율 (< 임계값): 5단계로
    |-> 5. 코드 중단 (프로세스 kill)
    |-> 6. 비효율 원인 분석
    |-> 7. 코드 최적화 적용
    |-> 8. 재실행 (2단계로, 최대 5회)
    |-> 9. 최대 반복 초과 시 사용자에게 보고
```

## 5. 최적화 전략 (우선순위순)

### 5.1 메모리 비효율 (Memory < 30%)

| 순서 | 전략 | 설명 |
|------|------|------|
| 1 | batch_size 증가 | 현재 값의 2배씩 시도 |
| 2 | num_workers 조정 | DataLoader workers 최적화 |
| 3 | pin_memory 활성화 | CPU->GPU 전송 최적화 |
| 4 | prefetch_factor 조정 | 데이터 프리페치 최적화 |

### 5.2 연산 비효율 (Utilization < 50%)

| 순서 | 전략 | 설명 |
|------|------|------|
| 1 | DataLoader 병목 해소 | num_workers, prefetch 조정 |
| 2 | mixed precision 적용 | torch.cuda.amp 활성화 |
| 3 | torch.compile 적용 | PyTorch 2.0+ 컴파일 모드 |
| 4 | 데이터 전처리 최적화 | GPU 전처리로 전환 |

### 5.3 공통 최적화

| 전략 | 설명 |
|------|------|
| CUDA 벤치마크 | `torch.backends.cudnn.benchmark = True` |
| 그래디언트 체크포인팅 | 메모리 부족 시 활성화 |
| non_blocking 전송 | `.to(device, non_blocking=True)` |

## 6. 모니터링 스크립트

실행: `uv run python .claude/skills/ccdeep/scripts/oodeep_monitor.py`

### 기능

- nvidia-smi 기반 GPU 사용률/메모리 실시간 모니터링
- JSON 형식 로그 출력
- 프로세스 PID 추적

## 7. 사전 분석 (check)

코드를 실행하지 않고 정적 분석으로 GPU 효율성 문제를 사전 탐지:

| 체크 항목 | 설명 |
|----------|------|
| batch_size | 너무 작은 값 감지 |
| num_workers | 0이면 경고 |
| pin_memory | False이면 권고 |
| mixed precision | amp 미사용 시 권고 |
| DataLoader 설정 | 비효율적 설정 감지 |
| .to(device) 패턴 | non_blocking 미사용 감지 |

## 8. 출력 형식

### 모니터링 리포트

```
# ccdeep - GPU 모니터링 리포트

## GPU 상태
| 항목 | 값 |
|------|-----|
| GPU | NVIDIA RTX 5090 |
| 사용률 | 23% (비효율) |
| 메모리 | 2.1GB / 32GB (6.6%) |
| 온도 | 45°C |

## 판단: 비효율 감지
- GPU 사용률 23% < 임계값 50%
- 메모리 사용률 6.6% < 임계값 30%

## 최적화 계획
1. batch_size: 32 -> 64
2. num_workers: 0 -> 4
3. pin_memory: False -> True
```

### 최종 리포트

```
# ccdeep - 최적화 결과

| 반복 | GPU 사용률 | 메모리 | 변경사항 |
|------|----------|--------|---------|
| 1회 | 23% | 6.6% | 초기 실행 |
| 2회 | 45% | 25% | batch_size 32->64 |
| 3회 | 78% | 48% | num_workers 0->4, amp 적용 |

최종 상태: 최적화 완료 (3회 반복)
```

## 9. 에이전트 출력 규칙

| 규칙 | 설명 |
|------|------|
| 모니터링 결과 즉시 표시 | GPU 상태를 테이블로 출력 |
| 최적화 변경점 명시 | 수정 전/후 값을 명확히 표시 |
| 코드 변경 최소화 | GPU 효율 관련 부분만 수정 |
| 원본 백업 | 수정 전 원본을 .bak으로 백업 |

## 10. 서브에이전트

| 단계 | 에이전트 | 모델 | 역할 | 병렬 |
|------|----------|------|------|:----:|
| 분석 | Explore | haiku | 코드/GPU 환경 스캔 | O |
| 실행 | task-executor | opus | 스크립트 실행/모니터링 | - |
| 최적화 | task-executor | opus | 코드 수정 | - |

## 11. 관련 문서

- `.claude/skills/ccdeep/references/guide.md`: 상세 최적화 가이드
- `.claude/skills/oodev/SKILL.md`: TDD 기반 개발
- `.claude/skills/oocheck/SKILL.md`: 코드 품질 체크

<!-- RUN-UPDATE-REF:START -->

## run과 update 분리 원칙

> 이 스킬은 `.claude/guides/run_update_separation.md` 원칙을 따른다.

| 서브커맨드 | 역할 |
|-----------|------|
| `run` | 이 스킬의 **배치 실행** 또는 구체적인 명령 실행 (일회성) |
| `update` | 최상의 상태로 유지되어야 하는 **모든 상태·설정 현행화** (멱등) |

> `run`에서 자동으로 `update`를 호출하지 않는다. 현행화는 별도 명령으로 실행.

<!-- RUN-UPDATE-REF:END -->

<!-- GEMMA-REF:START -->

## Gemma 위임 (로컬 LLM)

> 이 스킬 업무 중 **단순/반복적인 부분**(번역·요약·분류·Rephrase·포맷 변환 등)은
> 사용자 승인 후 `gemma` 스킬로 위임하여 API 토큰을 절감한다.

| 항목 | 내용 |
|------|------|
| 위임 기준 | `.claude/guides/gemma_delegation.md` 참조 |
| 승인 확인 | "이 작업은 [유형]입니다. 로컬 Gemma로 처리할까요? (y/n, 기본: y)" |
| 실행 명령 | `uv run python .claude/skills/gemma/scripts/gemma_run.py "프롬프트"` |
| 폴백 | 서버 미가동·응답 불량 시 Claude 본체로 자동 전환 |

<!-- GEMMA-REF:END -->
<!-- SAMPLE-REF:START -->

## 샘플 참조 (산출물 품질 향상)

> 산출물 작성 직전, `samples/` 폴더가 존재하면 샘플을 few-shot 참고 자료로 활용한다.

| 항목 | 내용 |
|------|------|
| 샘플 위치 | `.claude/skills/{스킬명}/samples/` |
| 참조 시점 | 산출물 작성 직전 (on-demand, 자동 로드 X) |
| 샘플 있는 경우 | 샘플의 스타일·깊이·어조를 참고하여 산출물 작성 |
| 샘플 없는 경우 | 템플릿(`templates/`)만으로 진행 (현재 상태) |
| 샘플 추가 방법 | 품질 좋은 기존 산출물을 `samples/` 폴더에 저장 |

<!-- SAMPLE-REF:END -->

