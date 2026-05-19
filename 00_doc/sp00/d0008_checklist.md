# 프로젝트 체크리스트

## 1. 문서 정보

- 문서번호: d0008
- 작성일: 2026-05-17
- 관리 스킬: `cccheck`
- 범위: HSMB 프로젝트 전용 체크리스트

## 2. 프로젝트 체크리스트

> 이 문서는 현재 프로젝트에 직접 연결되는 체크리스트만 관리한다.
> oo* 스킬 내부 `references/checklist.md`는 각 스킬 자체 체크리스트이며, 이 문서와 분리한다.
> `cccheck add checklist "..."`는 이 섹션에 새 항목을 추가한다.

### N001 [NAMING] clean clear cleanup 용어를 같은 의미로 쓰는지 점검하고 하나로 통일
- 등록일: 2026-05-17
- 분류: NAMING
- 우선순위: HIGH
- 상태: OPEN
- 메모: 자동 분류됨


## 3. 코드 및 분류 규칙

| Prefix | 분류 | 의미 |
|--------|------|------|
| `N` | NAMING | 용어, 명명, 표현 통일 |
| `Q` | QUALITY | 품질, 점검, 정합성 |
| `T` | TEST | 테스트, 재현, 검증 |
| `D` | DOC | 문서, 기록, 추적성 |
| `O` | OPS | 운영 절차, 실행, 복구 |
| `S` | SECURITY | 보안, 안전, 권한 |
| `G` | GENERAL | 기타 일반 항목 |

## 4. 운영 규칙

1. oo* 스킬 체크리스트는 각 스킬 디렉터리의 `references/checklist.md`에서 관리한다.
2. `d0008_checklist.md`는 특정 프로젝트와 직접 관련된 체크리스트만 기록한다.
3. `cccheck add checklist "..."`는 항목 성격에 따라 Prefix, 분류, 우선순위를 자동 부여한다.
4. 기본 상태는 `OPEN`이며 필요 시 `IN_PROGRESS`, `DONE`, `HOLD`로 수동 갱신한다.
