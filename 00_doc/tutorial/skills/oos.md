# oos Tutorial

> oostart 스킬의 약어 alias. | 버전: v01 | 카테고리: meta-util

## 1. 이 스킬은 왜 필요한가?

oostart 스킬의 약어 alias.

## 2. 빠른 시작 (5분 가이드)

```bash
# 기본 실행
oos run

# 상태 확인
oos status

# 도움말
oos help
```

## 3. 전체 서브명령어

(명령어 테이블 없음)

## 4. 상세 사용법

### 스킬 요약

| 항목 | 내용 |
|------|------|
| **핵심 역할** | `oostart` 스킬의 약어 alias — 세션 시작 워크플로우 |
| **하는 것** | `oostart` 스킬 실행 + 완료 후 SP 선택 프롬프트 |
| **하지 않는 것** | 파일 수정, 코드 실행 |
| **에이전트 호환** | 범용 — `oostart`을 직접 호출하는 것으로 대체 가능 |

### 실행 후 처리 (필수)

`oostart` 스크립트 실행이 완료되면 **반드시** 아래 순서로 처리하세요:

1. 스크립트 출력 결과를 간략히 요약 표시
2. 다음 형식으로 SP 선택 테이블을 출력:

| 번호 | SP | 폴더 |
|------|----|------|
| 0 | SP00 | 공통 |
| 1 | SP01 | 01_obsidian |
| 2 | SP02 | 02_pycode |
| 4 | SP04 | 04_scraping |
| 5 | SP05 | 05_youtube_graphRAG |
| 6 | SP06 | 06_oohwp_skill |
| 7 | SP07 | 07_designsystem |
| 8 | SP08 | 08_RRag |
| 9 | SP09 | 09_ooppt |

3. "**작업할 서브프로젝트 번호를 선택하세요 (0-9, Enter=현재 유지):**" 질문
4. 사용자 입력값 N을 받아 즉시 `oocontext N` 실행 (Skill 도구로 `oocontext` 호출, args=N)
5. Enter(빈 입력) 시 현재 컨텍스트 유지 (oocontext 호출 생략)

## 5. 워크플로우

(워크플로우 정보는 SKILL.md 참조)

## 6. 실전 예시

### 기본 사용
```bash
# 전체 실행
oos run
```

## 7. 입출력

(입출력 정보는 SKILL.md 참조)

## 8. 자주 묻는 질문 (FAQ)

> 실전 사용 중 FAQ가 축적되면 이 섹션에 추가됩니다.
>
> `ootutorial add-faq {skill_name} "질문" "답변"` 으로 추가 가능

## 9. 서브에이전트

(서브에이전트 정보 없음)

## 10. 관련 스킬

(관련 스킬 정보 없음)

---

> 생성일: 2026-04-17 19:50 | ootutorial v02
