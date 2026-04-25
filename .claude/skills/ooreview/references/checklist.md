# ooreview check 체크리스트

> ooreview 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md, scripts/ooreview_run.py 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version ↔ 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | 에이전트 가용성 | code-reviewer(opus), security-reviewer, quality-reviewer 에이전트 존재 | CRITICAL |
| C04 | Codex CLI 선택적 가용 | `--codex` 옵션 사용 시 `codex` CLI 실행 가능 | WARNING |
| C05 | 병렬 실행 구조 | 3개 에이전트를 병렬(run_in_background)로 호출하는지 검증 | ERROR |
| C06 | 결과 집계 | 3개 에이전트 결과를 하나의 리포트로 통합 출력 | ERROR |
| C07 | d{SP}0004 등록 | 이슈를 `00_doc/sp{NN}/d{SP}0004_todo.md`에 등록 | WARNING |

## check 출력 형식

```
[ooreview check]

C01 필수 파일 존재             [OK]
C02 버전 일치                  [OK]
C03 에이전트 가용성            [OK]
C04 Codex CLI 선택적 가용      [WARN]  codex CLI 미설치 (--codex 비활성)
C05 병렬 실행 구조             [OK]
C06 결과 집계                  [OK]
C07 d{SP}0004 등록             [OK]

소계: OK:6 | WARN:1 | FAIL:0
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | ❌ | 스킬 동작 불가 (즉시 조치) |
| ERROR | ⚠️ | 정상 동작 어려움 (24시간 내) |
| WARNING | ⚡ | 품질 저하 (1주 내) |
| INFO | ℹ️ | 개선 권장 (백로그) |

## 리뷰 체크 항목 (에이전트별 참조)

> 스킬 자체 건강 체크와 별도로, 각 에이전트가 수행하는 리뷰 항목

### code-reviewer(opus)

- [ ] SRP, 과도한 결합, API 계약, 하위 호환성, 추상화 수준, 300줄 초과 파일
- [ ] 의미 있는 네이밍, 매직 넘버, 중첩 depth ≤4, 함수 길이 ≤50줄
- [ ] DRY, 프로젝트 패턴 일관성, deprecated API 미사용

### security-reviewer(sonnet)

- [ ] OWASP A01/A02/A03/A05/A07/A09
- [ ] 하드코딩 시크릿, PII 로그, 에러 메시지 내부 노출
- [ ] 외부 입력 검증, Path traversal, 파일 업로드 제한

### quality-reviewer(sonnet)

- [ ] O(n²) 루프, N+1 쿼리, 메모리 누수, 캐시 활용
- [ ] 테스트 가능성, 명시적 에러 처리, 비동기 예외 처리

### Codex 2차 리뷰 집중 영역

- [ ] 엣지 케이스, 레이스 컨디션, 오프바이원, 타임아웃/무한루프, 리소스 누수
