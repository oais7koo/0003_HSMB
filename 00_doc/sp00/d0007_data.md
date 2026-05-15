# data/ 폴더 구조 (프로젝트 공통)

> data/ 는 SP에 무관한 프로젝트 루트 공통 폴더이며, 본 문서는 oodata 스킬이 관리한다.

## 문서 이력 관리
- 2026-05-15 11:57:32 — oodata run 자동 생성/업데이트

## 서브폴더 목록

| 폴더 | 상태 | 설명 |
|------|------|------|
| 01_기존/ | 존재 (2310.8 MB) |  |
| 02_260422_HSMB논문 수정안/ | 존재 (1.1 MB) |  |
| ps1010_chungsong_MTF/ | 존재 (2067.1 MB) |  |
| ps1204_kict_eSFR/ | 존재 (1460.0 MB) |  |
| ps1206_청송터널 데이터 원본/ | 백업됨 |  |
| ps1301_real_crack_cam2/ | 존재 (45111.4 MB) |  |
| ps1302_print_crack/ | 존재 (3070.1 MB) |  |
| ps1600_hsmb 기존값비교/ | 존재 (0.0 MB) | MTF(15000)-IQA 지표.xlsx 결과가 0715버전보다 좋음 — ps2000 현재 파라미터(edge_weight=0.8/beta=1.8/JNB=2.5/p_jnb=cumsum[45])가 PRD §4.1 사양(EdgeWeight=1.5/β=2.0/JNB=3/p_jnb=0.63)과 불일치. 어느 파라미터 세트가 더 좋은 결과를 내는지 ablation으로 확인 필요 |
| ps2000/ | 존재 (2.6 MB) |  |
| ps2010/ | 존재 (0.5 MB) |  |

> data/ 경로: `C:\Users\oaiskoo\doom\3_code\0003_HSMB\data`
> 외부 백업 기본 경로: `f:\udd\data_exa\exa63_dual_branch`

## 폴더 상세

### 01_기존/

- 상태: 존재 (2310.8 MB)
- 총 파일 수: 9848개
- 주요 확장자: `.png` 9472, `.xlsx` 272, `.py` 74, `.ipynb` 8, `.py_` 6
- 서브폴더:
  - `data/` (9757 files)
  - `doc/` (0 files)
  - `src/` (0 files)
- 추정 성격: 이미지 위주 (9472/9848)

### 02_260422_HSMB논문 수정안/

- 상태: 존재 (1.1 MB)
- 총 파일 수: 3316개
- 주요 확장자: `.png` 3244, `.xlsx` 53, `.csv` 10, `.md` 6, `.py` 3
- 서브폴더:
  - `data/` (3296 files)
  - `doc/` (0 files)
  - `docs/` (6 files)
  - `results_expected/` (7 files)
  - `scripts/` (3 files)
- 추정 성격: 이미지 위주 (3244/3316)

### ps1010_chungsong_MTF/

- 상태: 존재 (2067.1 MB)
- 총 파일 수: 3367개
- 주요 확장자: `.png` 2777, `.csv` 582, `.json` 4, `.fits` 3, `.xlsx` 1
- 서브폴더:
  - `low_2.5m_60km_2.5m_ISO100/` (93 files)
  - `low_2.5m_60km_2.5m_ISO1600/` (64 files)
  - `low_2.5m_60km_2.5m_ISO200/` (54 files)
  - `low_2.5m_60km_2.5m_ISO400/` (58 files)
  - `low_2.5m_60km_2.5m_ISO800/` (62 files)
  - `low_2.5m_80km_2.5m_ISO100/` (58 files)
  - `low_2.5m_80km_2.5m_ISO1600/` (75 files)
  - `low_2.5m_80km_2.5m_ISO200/` (58 files)
  - `low_2.5m_80km_2.5m_ISO400/` (61 files)
  - `low_2.5m_80km_2.5m_ISO800/` (66 files)
  - `low_3.5m_60km_3.5m_ISO100/` (70 files)
  - `low_3.5m_60km_3.5m_ISO1600/` (69 files)
  - `low_3.5m_60km_3.5m_ISO200/` (75 files)
  - `low_3.5m_60km_3.5m_ISO400/` (53 files)
  - `low_3.5m_60km_3.5m_ISO800/` (64 files)
  - `low_3.5m_80km_3.5m_ISO100/` (54 files)
  - `low_3.5m_80km_3.5m_ISO1600/` (69 files)
  - `low_3.5m_80km_3.5m_ISO200/` (56 files)
  - `low_3.5m_80km_3.5m_ISO400/` (46 files)
  - `low_3.5m_80km_3.5m_ISO800/` (66 files)
  - … 외 30개
- 추정 성격: 이미지 위주 (2777/3367) · 원본 데이터 추정 (백업 정책: 제외)

### ps1204_kict_eSFR/

- 상태: 존재 (1460.0 MB)
- 총 파일 수: 510개
- 주요 확장자: `.png` 470, `.csv` 40
- 서브폴더:
  - `00_BEW, MTF50(해석값)/` (40 files)
  - `15000lx_0640_500us_00/` (10 files)
  - `15000lx_0640_500us_10/` (10 files)
  - `15000lx_0640_500us_30/` (10 files)
  - `15000lx_0640_500us_50/` (10 files)
  - `15000lx_0640_500us_70/` (10 files)
  - `15000lx_1250_250us_00/` (10 files)
  - `15000lx_1250_250us_10/` (10 files)
  - `15000lx_1250_250us_30/` (10 files)
  - `15000lx_1250_250us_50/` (10 files)
  - `15000lx_1250_250us_70/` (10 files)
  - `15000lx_1600_050us_00/` (10 files)
  - `15000lx_1600_050us_10/` (10 files)
  - `15000lx_1600_050us_30/` (10 files)
  - `15000lx_1600_050us_50/` (10 files)
  - `15000lx_1600_050us_70/` (10 files)
  - `15000lx_1600_100us_00/` (10 files)
  - `15000lx_1600_100us_10/` (10 files)
  - `15000lx_1600_100us_30/` (10 files)
  - `15000lx_1600_100us_50/` (10 files)
  - … 외 28개
- 추정 성격: 이미지 위주 (470/510) · 원본 데이터 추정 (백업 정책: 제외)

### ps1206_청송터널 데이터 원본/

- 상태: 백업됨
- 비고: 외부 경로로 이동됨 (data/ 본체 없음)

### ps1301_real_crack_cam2/

- 상태: 존재 (45111.4 MB)
- 총 파일 수: 737개
- 주요 확장자: `.png` 737
- 서브폴더:
  - `crack_d25_ISO100_V60/` (11 files)
  - `crack_d25_ISO100_V80/` (14 files)
  - `crack_d25_ISO1600_V60/` (14 files)
  - `crack_d25_ISO1600_V80/` (14 files)
  - `crack_d25_ISO200_V60/` (16 files)
  - `crack_d25_ISO200_V80/` (14 files)
  - `crack_d25_ISO400_V60/` (15 files)
  - `crack_d25_ISO400_V80/` (14 files)
  - `crack_d25_ISO800_V60/` (14 files)
  - `crack_d25_ISO800_V80/` (15 files)
  - `crack_d35_ISO100_V60/` (16 files)
  - `crack_d35_ISO100_V80/` (13 files)
  - `crack_d35_ISO1600_V60/` (16 files)
  - `crack_d35_ISO1600_V80/` (14 files)
  - `crack_d35_ISO200_V60/` (17 files)
  - `crack_d35_ISO200_V80/` (13 files)
  - `crack_d35_ISO400_V60/` (15 files)
  - `crack_d35_ISO400_V80/` (15 files)
  - `crack_d35_ISO800_V60/` (14 files)
  - `crack_d35_ISO800_V80/` (14 files)
  - … 외 30개
- 추정 성격: 균열 데이터 · 이미지 위주 (737/737) · 원본 데이터 추정 (백업 정책: 제외)

### ps1302_print_crack/

- 상태: 존재 (3070.1 MB)
- 총 파일 수: 50개
- 주요 확장자: `.png` 50
- 서브폴더: 없음 (루트에 파일만)
- 추정 성격: 균열 데이터 · 이미지 위주 (50/50) · 원본 데이터 추정 (백업 정책: 제외)

### ps1600_hsmb 기존값비교/

- 상태: 존재 (0.0 MB)
- 코멘트: MTF(15000)-IQA 지표.xlsx 결과가 0715버전보다 좋음 — ps2000 현재 파라미터(edge_weight=0.8/beta=1.8/JNB=2.5/p_jnb=cumsum[45])가 PRD §4.1 사양(EdgeWeight=1.5/β=2.0/JNB=3/p_jnb=0.63)과 불일치. 어느 파라미터 세트가 더 좋은 결과를 내는지 ablation으로 확인 필요
- 총 파일 수: 2개
- 주요 확장자: `.xlsx` 2
- 서브폴더: 없음 (루트에 파일만)
- 추정 성격: Excel 시트 위주 (2/2) · 원본 데이터 추정 (백업 정책: 제외)

### ps2000/

- 상태: 존재 (2.6 MB)
- 총 파일 수: 6개
- 주요 확장자: `.xlsx` 6
- 서브폴더:
  - `00_old/` (3 files)
- 추정 성격: Excel 시트 위주 (6/6)

### ps2010/

- 상태: 존재 (0.5 MB)
- 총 파일 수: 6개
- 주요 확장자: `.xlsx` 6
- 서브폴더: 없음 (루트에 파일만)
- 추정 성격: Excel 시트 위주 (6/6)
