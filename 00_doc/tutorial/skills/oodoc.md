# oodoc Tutorial

> d0001~d0010 문서 생성, 최적화, 검증 자동화 | 버전: v13 | 카테고리: doc-env

## §1 이유 (Reason)

프로젝트 문서(PRD, 계획, 테스트, TODO, 이력 등)를 체계적으로 관리합니다.

## §2 빠른 시작 (Quick Start)

```bash
oodoc generate
```

현재 SP의 d0001~d0010 문서 자동 생성

## §3 자주 쓰는 명령 (Frequent Commands)

| 명령어 | 설명 |
|--------|------|
| `oodoc generate` | 문서 생성 |
| `oodoc optimize` | 최적화 |
| `oodoc check` | 검증 |
| `oodoc update` | 자동 갱신 |
| `oodoc list` | 목록 |

## §4 권장 흐름 (Recommended Flow)

1. `oodoc generate` → d0001~d0010 생성
2. 각 문서 수동 입력
3. 코드 변경 시 `oodoc update`
4. `oodoc check --quality` → 품질 검증

## §5 전체 명령어 (All Commands)

```
oodoc help
oodoc version
oodoc generate [OPTIONS]
oodoc optimize [OPTIONS]
oodoc check [OPTIONS]
oodoc update [--auto]
oodoc list
oodoc clear
oodoc std
```

## §6 상세 사용법 (Detailed Usage)

**10개 문서:**
- d{SP}0001 — PRD
- d{SP}0002 — 구현 계획
- d{SP}0003 — 테스트
- d{SP}0004 — TODO/이슈
- d{SP}0005 — 라이브러리
- d{SP}0006 — DB
- d{SP}0008 — 사용자
- d{SP}0009 — 환경
- d{SP}0010 — 이력

## §7 실전 예시 (Real Examples)

```bash
oocontext set 02
oodoc generate
oodoc check --quality
oodoc update --auto
```

## §8 입출력 (Input/Output)

**입력:** 코드 파일, 기존 문서
**출력:** 생성된 문서, 검증 리포트

## §9 FAQ

**Q: 문서가 중복되면?**
A: 최신 버전 유지. 이전 버전은 아카이브.

**Q: 자동 갱신이 실수할 수 있나?**
A: 가능. `--dry-run` 으로 미리 확인.

## §10 서브에이전트 (Sub-agents)

- document-generator, code-analyzer, document-validator

## §11 관련 스킬 (Related Skills)

- `ooplan`, `ootest`, `ootodo`, `oohistory`

---

**버전**: v13 | **카테고리**: doc-env | **업데이트**: 2026-04-14
