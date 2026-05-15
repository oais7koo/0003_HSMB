# oofeature Tutorial

> 기능별 상세 문서(상세기획/설계/구현/검증/완료) 생성·단계 전환·현황 관리 | 최종 업데이트: 2026-04-29

## 개요

상세 문서 5단계(기획→설계→구현→검증→완료) 생명주기를 관리하는 스킬. 단계가 파일명에 포함되어 rename으로 단계 전환하며, plan.md Feature와 교차 비교로 미착수 Feature를 리스트업한다. 번호(dXXXX)는 단계가 바뀌어도 불변.

대상: `00_doc/sp{N}/dXXXX_상세*.md` | 번호 범위: 0001~0999 공통, 1000~9999 상세 전용

## 명령어

| 명령어 | 설명 |
|--------|------|
| `oofeature new dXXXX "기능명"` | 상세기획 문서 생성 (공통 템플릿) |
| `oofeature new dXXXX "기능명" --stage 설계` | 특정 단계로 생성 |
| `oofeature new dXXXX "기능명" --framework streamlit` | Streamlit 전용 템플릿 |
| `oofeature next dXXXX` | 다음 단계 rename + 연계 스킬 실행 |
| `oofeature next this` | 직전 작업 상세 문서 다음 단계 |
| `oofeature stage dXXXX 단계` | 단계 수동 변경 (rename만) |
| `oofeature list` | 현재 SP 상세 문서 목록 + 단계 현황 |
| `oofeature needed [--sp N]` | plan.md Feature 교차 비교 → 미착수 리스트업 |
| `oofeature sync` | plan.md 8.2절 강제 갱신 |
| `oofeature update` | 변경 감지 → 상세기획 롤백 후보 표시 |
| `oofeature update --apply` | 롤백 실행 |
| `oofeature update --dry` | 롤백 미리보기 |
| `oofeature note dXXXX "내용"` | ## 메모 섹션에 날짜+내용 추가 |
| `oofeature issue dXXXX "이슈내용"` | ## 이슈 섹션에 추가 (🔴 미해결) |
| `oofeature issue dXXXX --resolve` | 최신 미해결 이슈 → ✅ 해결 |
| `oofeature check [--sp N]` | 정합성 검증 (V01~V08) |
| `oofeature rmdup [--sp N]` | 같은 번호 복수 단계 파일 → 최신만 유지 |

## 주요 사용 예시

```bash
# 1. plan.md 미착수 Feature 확인
oofeature needed

# 2. 상세기획 생성 (파일 없으면 자동 생성)
oofeature next d41010

# 3. 기획→설계 전환
oofeature next d41010

# 4. 설계→구현 전환 (oodev run 자동 연계)
oofeature next d41010

# 5. 구현→검증 전환 (oocheck run 자동 연계)
oofeature next d41010

# 6. 검증→완료 전환 (oocommit run 자동 연계)
oofeature next d41010

# 이슈 등록 / 해결
oofeature issue d41010 "API 응답 형식 불일치"
oofeature issue d41010 --resolve

# 현황 조회
oofeature list
```

## 워크플로우

```
⚪ 상세기획 → 🔵 상세설계 → 🟡 상세구현 → 🟢 상세검증 → ✅ 상세완료
```

| 단계 전환 | next 연계 동작 |
|-----------|--------------|
| 기획 → 설계 | 안내만 (설계 작성 후 재실행) |
| 설계 → 구현 | `oodev run dXXXX` 자동 실행 (TDD RED/GREEN) |
| 구현 → 검증 | `oocheck run dXXXX` 자동 실행 |
| 검증 → 완료 | `oocommit run` 자동 실행 |

**주의**: 설계→구현 전환 직후 반드시 `oodev run dXXXX` 실행 — 건너뛰면 TDD 사이클 누락.

## 관련 스킬

| 스킬 | 연동 내용 |
|------|----------|
| `ooplan` | plan.md 8.2절 상세 문서 현황 갱신 |
| `oodev` | 설계→구현 전환 시 자동 연계 (TDD) |
| `oocheck` | 구현→검증 전환 시 자동 연계 |
| `oofix` | 이슈 해결 후 검증 재실행 |
| `oocommit` | 검증→완료 전환 시 자동 연계 |
