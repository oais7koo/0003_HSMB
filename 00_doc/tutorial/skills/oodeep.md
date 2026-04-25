# oodeep Tutorial

> PyTorch GPU 효율성 모니터링 및 자동 최적화 | 버전: v01 | 카테고리: core-dev

## §1 이유 (Reason)

딥러닝 모델 학습 시 GPU 메모리 사용률, 처리 속도 등을 실시간 모니터링하고, 자동으로 배치 크기, 워커 수, 혼합정밀도 등을 최적화합니다.

## §2 빠른 시작 (Quick Start)

```bash
oodeep run --script train.py
```

자동 감지: PyTorch 코드 분석 → 모니터링 → 최적화 제안

## §3 자주 쓰는 명령 (Frequent Commands)

| 명령어 | 설명 |
|--------|------|
| `oodeep run` | 모니터링 + 최적화 |
| `oodeep monitor` | 모니터링만 |
| `oodeep optimize` | 최적화 제안 |
| `oodeep report` | 성능 리포트 |

## §4 권장 흐름 (Recommended Flow)

1. PyTorch 학습 스크립트 준비
2. `oodeep run --script train.py` 실행
3. 자동 모니터링 및 제안
4. `oodeep report` → 성능 개선 결과 확인

## §5 전체 명령어 (All Commands)

```
oodeep help
oodeep version
oodeep run [SCRIPT] [OPTIONS]
oodeep monitor [SCRIPT]
oodeep optimize [OPTIONS]
oodeep report
```

## §6 상세 사용법 (Detailed Usage)

**모니터링 지표:**
- GPU 메모리 사용률 (%)
- GPU 처리율 (%)
- 배치 처리 시간
- 메모리 피크값

**자동 최적화 5단계:**
1. batch_size 조정
2. num_workers 최적화
3. pin_memory=True 적용
4. 혼합정밀도 활성화
5. torch.compile 적용

## §7 실전 예시 (Real Examples)

```bash
oodeep run --script 01_algorithm/train_model.py
oodeep monitor --script train.py --no-optimize
oodeep optimize --enable-mixed-precision
oodeep report --before after
```

## §8 입출력 (Input/Output)

**입력:** PyTorch 학습 스크립트
**출력:** 모니터링 로그, 최적화 제안, 비교 리포트

## §9 FAQ

**Q: GPU가 없으면?**
A: CPU 모드로 실행되지만, GPU 최적화 불가.

**Q: 최적화가 항상 성능을 개선하나?**
A: 대부분 5-30% 개선. 극단적 최적화는 정확도 하락 가능.

## §10 서브에이전트 (Sub-agents)

- pytorch-specialist, gpu-optimizer, performance-monitor

## §11 관련 스킬 (Related Skills)

- `oodev`, `ootest`, `oocheck`, `ooopti`

---

**버전**: v01 | **카테고리**: core-dev | **업데이트**: 2026-04-14
