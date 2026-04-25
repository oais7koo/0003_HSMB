# Environment Setup Command: 개발 환경 설정

## 명령어 목적
Python 데이터 사이언스 프로젝트의 개발 환경을 일관성 있게 설정하고 관리합니다.

## 환경 관리 전략

### 1. 패키지 관리
- **Primary**: Pipenv (`Pipfile`, `Pipfile.lock`)
- **Secondary**: npm (JavaScript 도구 관리)
- **Base Python**: Python 3.12

### 2. 핵심 라이브러리 카테고리

#### 데이터 처리 & 분석
```toml
[packages]
pandas = "*"
numpy = "*"
scipy = "*"
statsmodels = "*"
```

#### 시각화
```toml
matplotlib = "*"
seaborn = "*"
plotly = "*"
pygwalker = "*"  # 인터랙티브 EDA
```

#### 머신러닝
```toml
scikit-learn = "*"
pytorch-lightning = "*"
tensorflow = "*"
pycaret = "*"  # AutoML
```

#### 컴퓨터 비전
```toml
opencv-python = "*"
pillow = "*"
scikit-image = "*"
albumentations = "*"  # 데이터 증강
```

#### 이미지 품질 평가 (IQA)
```toml
pyiqa = "*"  # 종합 IQA 메트릭
brisque = "*"  # BRISQUE 메트릭
```

#### 자연어 처리
```toml
nltk = "*"
googletrans = "*"
deep-translator = "*"
newspaper3k = "*"
```

#### 웹 & API
```toml
requests = "*"
beautifulsoup4 = "*"
selenium = "*"
```

#### 유틸리티
```toml
tqdm = "*"  # 진행률 표시
pathlib = "*"
datetime = "*"
pickle = "*"
```

### 3. 환경 설정 명령어

#### 새 환경 생성
```bash
pipenv --python 3.12
pipenv install pandas numpy matplotlib seaborn jupyter
```

#### 기존 환경 복원
```bash
pipenv install --dev
pipenv shell
```

#### Jupyter 환경 설정
```bash
pipenv install jupyter ipykernel
pipenv run python -m ipykernel install --user --name=프로젝트명
```

### 4. 폰트 설정 (한글 지원)

#### matplotlib 한글 폰트 설정
```python
import matplotlib.pyplot as plt
from matplotlib import font_manager

# NanumGothic 폰트 설정
font_path = 'NanumGothic.ttf'
fontprop = font_manager.FontProperties(fname=font_path)
plt.rc('font', family=fontprop.get_name())
plt.rc('axes', unicode_minus=False)  # 마이너스 표시 오류 해결
```

### 5. GPU 환경 설정

#### PyTorch GPU 확인
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"Device count: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"Current device: {torch.cuda.get_device_name()}")
```

#### TensorFlow GPU 확인
```python
import tensorflow as tf
print(f"GPU devices: {tf.config.list_physical_devices('GPU')}")
```

## 프로젝트별 환경 설정

### IQA 프로젝트 환경
- **pyiqa**: 통합 IQA 메트릭 라이브러리
- **opencv-python**: 이미지 전처리
- **pillow**: 이미지 I/O
- **pandas**: 점수 데이터 분석

### 딥러닝 프로젝트 환경
- **pytorch-lightning**: PyTorch 고수준 프레임워크
- **torchvision**: 컴퓨터 비전 데이터셋
- **tensorboard**: 학습 모니터링
- **wandb**: 실험 추적

### 웹 스크래핑 환경
- **selenium**: 동적 웹페이지 크롤링
- **beautifulsoup4**: HTML 파싱
- **requests**: HTTP 요청

## 품질 관리

### 코드 품질 도구
```toml
[dev-packages]
black = "*"        # 코드 포매터
flake8 = "*"       # 린터
pytest = "*"       # 테스트 프레임워크
jupyter = "*"      # 노트북 환경
```

### 의존성 보안 검사
```bash
pipenv check  # 알려진 보안 취약점 확인
pipenv graph  # 의존성 트리 확인
```

### 환경 내보내기
```bash
pipenv requirements > requirements.txt  # pip 호환 형식
pipenv lock -r --dev > requirements-dev.txt  # 개발 의존성 포함
```

## 문제 해결

### 일반적인 오류 해결

#### Java 의존성 오류 (KoNLPy)
```bash
# Windows: Java JDK 설치 필요
# JAVA_HOME 환경변수 설정
```

#### GPU 메모리 부족
```python
# PyTorch 메모리 정리
torch.cuda.empty_cache()

# TensorFlow 메모리 증가 허용
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    tf.config.experimental.set_memory_growth(gpus[0], True)
```

#### 한글 폰트 오류
- `NanumGothic.ttf` 파일이 프로젝트 루트에 있는지 확인
- 시스템 폰트 경로 확인: `font_manager.findSystemFonts()`

## 자동화 스크립트

### 환경 검증 스크립트
```python
import sys
import importlib

required_packages = [
    'pandas', 'numpy', 'matplotlib', 'seaborn',
    'sklearn', 'torch', 'cv2', 'PIL'
]

for package in required_packages:
    try:
        importlib.import_module(package)
        print(f"✅ {package} 설치됨")
    except ImportError:
        print(f"❌ {package} 설치 필요")
```

### 초기화 템플릿
```python
# 표준 라이브러리
import os
import sys
from pathlib import Path

# 데이터 처리
import pandas as pd
import numpy as np

# 시각화
import matplotlib.pyplot as plt
import seaborn as sns

# 한글 폰트 설정
from matplotlib import font_manager
font_path = 'NanumGothic.ttf'
if os.path.exists(font_path):
    fontprop = font_manager.FontProperties(fname=font_path)
    plt.rc('font', family=fontprop.get_name())
    plt.rc('axes', unicode_minus=False)

# 설정
plt.style.use('default')
pd.set_option('display.max_columns', None)
np.random.seed(42)

print("환경 설정 완료!")
```