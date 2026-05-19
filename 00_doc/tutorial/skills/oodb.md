# oodb Tutorial

> 데이터베이스 설계, 마이그레이션, 검증, 최적화 | 버전: v04 | 카테고리: doc-env

## §1 이유 (Reason)
SQLite 데이터베이스의 설계, 무결성 검증, 마이그레이션, 최적화를 체계적으로 관리합니다.

## §2 빠른 시작 (Quick Start)

```bash
oodb validate
```

자동 감지: 현재 SP의 DB 검증 → 이슈 등록

## §3 자주 쓰는 명령 (Frequent Commands)

| 명령어 | 설명 |
|--------|------|
| `oodb validate` | 무결성 검증 |
| `oodb design [TABLE]` | 테이블 설계 |
| `oodb migrate` | 스키마 마이그레이션 |
| `oodb optimize` | 성능 최적화 |
| `oodb backup` | 백업 생성 |

## §4 권장 흐름 (Recommended Flow)

1. **설계**: `oodb design [TABLE]`
2. **검증**: `oodb validate`
3. **마이그레이션**: `oodb migrate`
4. **최적화**: `oodb optimize`
5. **백업**: `oodb backup`

## §5 전체 명령어 (All Commands)

```
oodb help
oodb version
oodb validate [OPTIONS]
oodb design [TABLE] [OPTIONS]
oodb migrate [SCRIPT]
oodb optimize [OPTIONS]
oodb backup
oodb restore [BACKUP_FILE]
```

## §6 상세 사용법 (Detailed Usage)

**3단계 워크플로우:**

1. Validate Phase (SQL 검증)
2. Analysis Phase (무결성 확인)
3. Fix Phase (에이전트 병렬)

**백업 정책:**
- 형식: `db/backup_YYYYMMDD-HHMM.db`
- 최근 5개 유지 (자동 정리)

## §7 실전 예시 (Real Examples)

```bash
oodb validate
oodb design common_user
oodb migrate migrations/add_user_roles.sql
oodb optimize --analyze
oodb backup
```

## §8 입출력 (Input/Output)

**입력:** SQL 스크립트, 테이블 정의
**출력:** 검증 리포트, 설계 문서, 백업

## §9 FAQ

**Q: 백업은 자동으로?**
A: 마이그레이션 전 자동. 수동은 `oodb backup`.

**Q: 마이그레이션 중 오류?**
A: 자동으로 이전 백업에서 복원.

## §10 서브에이전트 (Sub-agents)

- database-engineer, sql-validator, optimization-specialist

## §11 관련 스킬 (Related Skills)

- `oodev`, `ootest`, `ooenv`, `oohistory`

---

**버전**: v04 | **카테고리**: doc-env | **업데이트**: 2026-04-14
