# ooref check 체크리스트

> ooref 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md, scripts/ooref_run.py 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version ↔ 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | 레퍼런스 디렉터리 존재 | `.claude/reference/development/` 접근 가능 | CRITICAL |
| C04 | README.md 파싱 | development/README.md에서 프레임워크 목록 정상 파싱 | ERROR |
| C05 | 프레임워크 자동 감지 | pyproject.toml/requirements.txt/main.py 기반 감지 동작 | ERROR |
| C06 | 체크 규칙 로드 | 프레임워크별 규칙(디렉토리 구조·파일 크기·패턴) 로드 | WARNING |
| C07 | 결과 심각도 분류 | CRITICAL/ERROR/WARNING/INFO 수준별 출력 | WARNING |
| C08 | 경로/프레임워크 인자 | `ooref run [path]` / `ooref run [framework]` 옵션 동작 | WARNING |

## check 출력 형식

```
[ooref check]

C01 필수 파일 존재             [OK]
C02 버전 일치                  [OK]
C03 레퍼런스 디렉터리 존재     [OK]
C04 README.md 파싱             [OK]
C05 프레임워크 자동 감지       [OK]
C06 체크 규칙 로드             [OK]
C07 결과 심각도 분류           [OK]
C08 경로/프레임워크 인자       [OK]

소계: OK:8 | WARN:0 | FAIL:0
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | ❌ | 스킬 동작 불가 (즉시 조치) |
| ERROR | ⚠️ | 정상 동작 어려움 (24시간 내) |
| WARNING | ⚡ | 품질 저하 (1주 내) |
| INFO | ℹ️ | 개선 권장 (백로그) |

## 기능 체크 (ooref 스킬이 제공하는 기능 검증)

> 스킬 자체 건강 체크와 별도로, 각 서브명령어의 기능 검증 체크리스트

- [ ] `ooref list` — README.md 파싱하여 프레임워크 목록 정확히 표시
- [ ] `ooref list` — 실제 폴더 목록 + 문서 수 + 감지 규칙 표시
- [ ] `ooref run` — 프레임워크 자동 감지 (pyproject.toml, requirements.txt, main.py)
- [ ] `ooref run` — 디렉토리 구조 체크 (필수 폴더/파일)
- [ ] `ooref run` — 파일 크기 체크 (main.py ≤150줄, routers/*.py ≤300줄)
- [ ] `ooref run` — 코드 패턴 체크 (lifespan, rate limiting, 예외 핸들러)
- [ ] `ooref run` — 설정 파일 분리 체크 (*_config.py)
- [ ] `ooref run` — 테스트 구조 체크 (conftest.py, test_*.py)
- [ ] `ooref run [path]` / `ooref run [framework]` 옵션 동작
- [ ] `ooref add checklist` — 항목 정상 추가
