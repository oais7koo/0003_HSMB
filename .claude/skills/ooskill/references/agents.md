# ooskill 에이전트 참조

> ooskill 스킬에서 위임하는 서브에이전트 목록과 역할 정의
> 에이전트 정의 위치: `.claude/agents/`

## 서브에이전트 매핑

| 단계 | 에이전트 | 모델 | 역할 | 병렬 |
|------|----------|------|------|:----:|
| 스킬 분석 | `Explore` | haiku | 파일 탐색, 패턴 추출 | O |
| 최적화 검토 | `ooqa` | sonnet | 중복/누락 분석 | O |
| 파일 수정 | `task-executor` | sonnet | 스킬 파일 수정 | O |
| 검증 | `task-checker` | sonnet | 수정 결과 검증 | - |

## 위임 규칙

| 작업 유형 | 에이전트 | 조건 |
|----------|----------|------|
| 코드 구현/수정 | `task-executor` | 파일 수정이 필요한 모든 작업 |
| Python 리뷰 | `python-code-reviewer` | scripts/*.py 품질 검토 |
| 구현 검증 | `task-checker` | 수정 후 결과 확인 |
| 품질/중복 분석 | `ooqa` | 스킬 간 중복·누락 분석 |
| 탐색/패턴 추출 | `Explore` | 파일 목록 수집, 키워드 검색 |

## 에이전트 검색 경로

```
.claude/agents/
├── ooqa.md                 # 품질 분석 (에이전트 전용)
├── task-executor.md        # 태스크 실행
├── task-checker.md         # 태스크 검증
├── python-code-reviewer.md # Python 코드 리뷰
└── ...
```

## 참고

- 에이전트 카탈로그 전체: `.claude/CLAUDE.md` 에이전트 섹션
- 공통 위임 원칙: `.claude/guides/common_guide.md`
