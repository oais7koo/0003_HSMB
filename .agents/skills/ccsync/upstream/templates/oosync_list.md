# oosync list 출력 템플릿

## 문서 이력 관리
- v03 2026-04-19 — Sync 컬럼 → Push/Pull 분리 컬럼으로 변경
- v02 2026-01-15 — 박스 테이블 형식으로 변경
- v01 2026-01-15 — 초기 버전 생성 - cmd_list 출력 템플릿화

---

> oosync list 명령어의 출력 형식을 정의하는 템플릿입니다.
> 변수는 `{variable_name}` 형식으로 사용합니다.

## 사용 변수

| 변수명 | 설명 | 예시 |
|--------|------|------|
| `{scan_path}` | 스캔 경로 | D:\resilio\3_code |
| `{table_output}` | 박스 테이블 (동적 생성) | - |
| `{total_count}` | 총 프로젝트 수 | 5 |

---

## 템플릿 본문

```template
# oosync list - 프로젝트 목록

스캔 경로: `{scan_path}`

{table_output}

총 {total_count}개 프로젝트 발견
```

## 박스 테이블 형식

```
┌────┬───────────────────────┬─────────┬──────────┬──────┬──────┐
│ #  │ Project               │  Status │ .claude/ │ Push │ Pull │
├────┼───────────────────────┼─────────┼──────────┼──────┼──────┤
│  1 │ 0001_SApp             │  Full   │    O     │  2   │  OK  │
│  2 │ 0002_CCone            │  Full   │    O     │  1   │  OK  │
│  3 │ 0004_a2z_ocr          │  Full   │    O     │  OK  │  1   │
│  4 │ 0013_dualbranck       │  Full   │    O     │  2   │  OK  │
│  5 │ 0014_atoz_AI_designer │  Full   │    O     │  OK  │  OK  │
└────┴───────────────────────┴─────────┴──────────┴──────┴──────┘
```

---

## 섹션별 템플릿

### project_rows (프로젝트 행)

```template
| {index} | {project_name} | {status} | {has_claude} | {push} | {pull} |
```

### 행 변수

| 변수명 | 설명 | 값 |
|--------|------|-----|
| `{index}` | 순번 | 1, 2, 3... |
| `{project_name}` | 프로젝트명 | 0001_vibe |
| `{status}` | 환경 상태 | Full / None |
| `{has_claude}` | .claude/ 존재 | O / X |
| `{push}` | push 필요 파일 수 | OK / 숫자 / - |
| `{pull}` | pull 필요 파일 수 | OK / 숫자 / - |

### push/pull 값 정의

| 값 | 조건 | 설명 |
|-----|------|------|
| OK | count == 0 | 동기화 완료 |
| 숫자 | count > 0 | 차이 파일 수 |
| - | status != Full | 비교 불가 |

**Push**: ONLY_SOURCE, NEWER_SOURCE (소스 → 대상)
**Pull**: ONLY_TARGET, NEWER_TARGET, CONFLICT (대상 → 소스)

---

## 관련 파일

- 스크립트: `.claude/skills/oosync/scripts/oosync_run.py`
- 스킬 문서: `.claude/skills/oosync/SKILL.md`
- 관련 템플릿: `.claude/skills/oosync/templates/oosync_view.md`, `.claude/skills/oosync/templates/oosync_diff.md`
