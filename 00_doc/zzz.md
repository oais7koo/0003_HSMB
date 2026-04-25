# 대화 메모 (2026-04-23 현재)

## 사용자 요청
CUDA torch 설치 (RTX 3070, Driver 581.57, CUDA 13.0)

## AI 응답 (현재 작업 상태)

### 작업 맥락
`ps2000_통합IQA.py` v04에 DL-IQA (DBCNN + ARNIQA, pyiqa) 통합 완료.
GPU 가속을 위해 CPU 전용 torch 2.11.0+cpu → CUDA 버전으로 교체 중.

### 시도 이력
1. `uv sync` with cu128 index → torch 2.11.0+cu128 다운로드는 되나 c10.dll 잠금 (os error 32)으로 설치 실패
2. `.venv` 삭제 + `uv sync` 재시도 → 동일 오류 반복
3. pip으로 직접 설치 시도 중:
   ```
   .venv/Scripts/pip install --force-reinstall --no-deps torch==2.11.0+cu128 torchvision==0.26.0+cu128 --index-url https://download.pytorch.org/whl/cu128
   ```
   → exit code 0 완료 (백그라운드 b12xt08zo)

### 현재 상태
- pyproject.toml: cu128 explicit index + [tool.uv.sources] 설정 완료
- torch 버전 요건: `>=2.6.0` (cu128 인덱스 제공 범위)
- pip install 결과 미확인 상태 (사용자가 검증 전에 중단)

### 다음 단계
```python
.venv/Scripts/python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
```
로 CUDA 활성화 확인 후 `ps5101_pytorch_gpu_test_v01.py` 실행
