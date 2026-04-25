# oowork 가이드

## 문서 이력 관리
- v01 2026-04-21 — 초기 생성

---

## 1. 개요

**oowork**: 장기 작업 워크플로우 관리. 계획·진행·완료·검증 단계 관리.

- **참조**:  (서브명령어·워크플로우)
- **이 문서**: 방법론(How) — 실행 패턴, 입력/출력 형식, 사용 가이드

---

## 2. 기본 사용법

```bash
# 등록된 프로세스 확인
oowork list

# 전체 파이프라인 실행
oowork run 기술수요조사 --topic "3-3 AI학습자동화" --keywords "MLOps,AutoML"

# 특정 단계만
oowork run 기술수요조사 --topic "1-3 엣지전처리" --step 2

# 범위 실행
oowork run 기술수요조사 --topic "3-1 데이터센터" --step 1-3

# 중단 후 재개
oowork run 기술수요조사 --resume

# 새 프로세스 등록
oowork add 예비창업검토
```

---

## 3. 워크플로우

```
1. 프로세스 파일 로드 (references/processes/{이름}.md)
2. 옵션 파싱 (topic, keywords, step 등)
3. 상태 파일 확인 (이전 실행 이력)
4. 단계별 순차 실행
   - 각 단계 시작 시 사용자 확인
   - 의존성 검증 (이전 단계 출력물 존재 확인)
   - 도구/스킬 호출
   - 출력물 검증 (파일 생성, 내용 검증)
   - 상태 업데이트
5. 완료 리포트 출력
```

---

## 4. 프로세스 파일 형식

`references/processes/{프로세스명}.md`에 정의:

```markdown
# 프로세스명

## meta
- version: v01
- author: 작성자
- description: 설명

## steps

### step.0 단계명
- tool: 사용할 스킬/도구
- input: 입력 (이전 단계 참조 가능: ${step.N.output})
- output: 출력 경로 패턴
- rules: 적용 규칙 (쉼표 구분)
- confirm: true/false (사용자 확인 필요 여부)
- sub_steps:
  1. 세부 작업 1
  2. 세부 작업 2
```

---

## 5. 상태 파일 형식

상태 파일 위치: `{workdir}/.oowork/{프로세스명}_state.json`

```json
{
  "process": "기술수요조사",
  "topic": "1-3 엣지전처리",
  "started": "2026-03-24T14:00:00",
  "current_step": 2,
  "steps": {
    "0": {"status": "done", "output": ["03_paper/11_paper_en/..."]},
    "1": {"status": "done", "output": ["02_기획/21_서베이.md"]},
    "2": {"status": "running", "output": []},
    "3": {"status": "pending"},
    "4": {"status": "pending"}
  }
}
```

---

## 6. 입출력 형식

| 항목 | 내용 |
|------|------|
| 입력 | 서브명령어 인자 또는 현재 SP 컨텍스트 |
| 출력 | 터미널 출력 또는 문서 파일 생성 |
| 로그 | 에러 발생 시 d{SP}0004_todo.md 등록 |

---

## 7. 주의사항

- SP 컨텍스트 확인 후 실행 (SKILL.md 참조)
- 상세 서브명령어는 SKILL.md 참조
