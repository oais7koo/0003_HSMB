# oodeep 상세 최적화 가이드

## 1. PyTorch GPU 최적화 패턴

### 1.1 DataLoader 최적화

```python
# 비효율적
loader = DataLoader(dataset, batch_size=8)

# 최적화
loader = DataLoader(
    dataset,
    batch_size=64,           # GPU 메모리에 맞게 최대한 크게
    num_workers=4,           # CPU 코어 수의 절반 ~ 동일
    pin_memory=True,         # GPU 전송 속도 향상
    prefetch_factor=2,       # 미리 배치 준비
    persistent_workers=True, # 워커 재사용
)
```

### 1.2 Mixed Precision Training

```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

for data, target in loader:
    optimizer.zero_grad()

    with autocast():
        output = model(data)
        loss = criterion(output, target)

    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

### 1.3 torch.compile (PyTorch 2.0+)

```python
model = torch.compile(model, mode="reduce-overhead")
```

### 1.4 CUDA 최적화 설정

```python
torch.backends.cudnn.benchmark = True
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
```

### 1.5 non_blocking 전송

```python
# 비효율적
data = data.to(device)

# 최적화
data = data.to(device, non_blocking=True)
```

## 2. 비효율 원인별 진단

### 2.1 GPU 사용률 낮음 (< 50%)

| 원인 | 증상 | 해결 |
|------|------|------|
| 데이터 로딩 병목 | GPU 사용률 0-100% 반복 | num_workers 증가 |
| 작은 batch_size | 연산량 부족 | batch_size 증가 |
| CPU 전처리 과다 | GPU idle 시간 김 | GPU 전처리 전환 |
| 동기화 과다 | .item(), print 남용 | 동기화 호출 최소화 |

### 2.2 GPU 메모리 낮음 (< 30%)

| 원인 | 증상 | 해결 |
|------|------|------|
| 작은 batch_size | 메모리 여유 과다 | batch_size 2배 증가 |
| 작은 모델 | 파라미터 수 적음 | 모델 크기는 유지, batch 증가 |
| 불필요한 메모리 해제 | 중간 텐서 삭제 | 필요시만 del 사용 |

### 2.3 OOM (Out of Memory) 대응

| 전략 | 설명 |
|------|------|
| gradient_checkpointing | 메모리-연산 트레이드오프 |
| accumulation | 작은 배치 여러 번 누적 |
| mixed precision | FP16으로 메모리 절반 |
| batch_size 감소 | 최후 수단 |

## 3. 모니터링 지표 해석

### 3.1 정상 상태

```
GPU Utilization: 80-100%  -> 양호
Memory Usage:    60-90%   -> 양호
Temperature:     < 85°C   -> 정상
Power:           70-100%  -> 정상 부하
```

### 3.2 비효율 패턴

```
패턴 A: Util 낮음 + Mem 낮음
  -> batch_size 크게 증가 필요

패턴 B: Util 0-100% 진동 + Mem 높음
  -> DataLoader 병목 (num_workers 증가)

패턴 C: Util 높음 + Mem 낮음
  -> 연산은 효율적, 메모리 여유 있으면 batch 증가 가능

패턴 D: Util 높음 + Mem 높음
  -> 최적 상태, 변경 불필요
```

## 4. batch_size 자동 탐색 전략

```
1. 현재 batch_size로 실행
2. GPU 메모리 사용량 확인
3. 여유 메모리 = 전체 - 사용량
4. 증가 가능량 = 여유 메모리 * 0.8 (안전 마진)
5. 새 batch_size = 현재 * (1 + 증가 가능량 / 사용량)
6. 2의 거듭제곱으로 반올림
```

## 5. 코드 수정 시 주의사항

- 학습 로직(모델 구조, 손실함수, 옵티마이저)은 절대 수정하지 않음
- GPU 효율 관련 파라미터만 수정
- 수정 전 원본을 .bak 파일로 백업
- 수정 내용을 주석으로 명시: `# oodeep: batch_size 32->64`
