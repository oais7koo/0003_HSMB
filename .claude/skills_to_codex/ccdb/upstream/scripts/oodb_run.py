#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
oodb_run.py

DB 수정 및 최적화 스크립트

명령어:
    oodb status           DB 상태 및 미해결 이슈 요약
    oodb run              Phase 1 + Phase 2 실행 (분석 → 기록 → 전체 수정 → 문서 업데이트)
    oodb optimize         run + 최적화 (인덱스, 쿼리, 정규화)
    oodb doc              문서화만 수행 (d0006_db.md 업데이트)
"""

import re
import sys
import sys as _sys
if _sys.stdout.encoding and _sys.stdout.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stdout.reconfigure(encoding='utf-8')
if _sys.stderr.encoding and _sys.stderr.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stderr.reconfigure(encoding='utf-8')
import sqlite3
from pathlib import Path
from datetime import datetime
# --- oo_common inline ---
import re as _re
_SKILLS_DIR = Path(__file__).parent.parent.parent

def _print_skill_help(skill_name):
    if sys.stdout.encoding and sys.stdout.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
        sys.stdout.reconfigure(encoding='utf-8')
    _sf = _SKILLS_DIR / skill_name / "SKILL.md"
    if not _sf.exists():
        print(f"[ERROR] .claude/skills/{skill_name}/SKILL.md not found")
        return
    _c = _sf.read_text(encoding="utf-8")
    _m = _re.search(r"##[^\n]*(?:서브명령어|명령어)\n\n((?:\|.+\n)+)", _c)
    if _m:
        print(f"`{skill_name} help` 서브명령어 목록:\n")
        print(_m.group(1).strip())
    else:
        print(f"[WARN] 서브명령어 섹션 없음: {skill_name}/SKILL.md")

def show_help_if_no_args(skill_name, args):
    if not args or args[0].lower() in ("help", "-h", "--help"):
        _print_skill_help(skill_name)
        return True
    return False
# --- end oo_common inline ---

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DB_DIR = PROJECT_ROOT / "db"
DOC_DIR = PROJECT_ROOT / "doc"
TMP_DIR = PROJECT_ROOT / "tmp"
TODO_FILE = DOC_DIR / "d0004_todo.md"
DB_DOC_FILE = DOC_DIR / "d0006_db.md"

# 기본 DB 파일
DEFAULT_DB_PATH = DB_DIR / "sene.sqlite"

# ID prefix for oodb tasks
ID_PREFIX = "D"


def print_usage():
    """사용법 출력"""
    print(f"Log started at {datetime.now()}")
    print("oodb - DB 수정 및 최적화 워크플로우")
    print()
    print("사용법:")
    print("    oodb status           DB 상태 및 미해결 이슈 요약")
    print("    oodb run              Phase 1 + Phase 2 실행 (분석 → 기록 → 수정 → 문서)")
    print("    oodb optimize         run + 최적화 (인덱스, 쿼리, 정규화)")
    print("    oodb doc              문서화만 수행 (d0006_db.md 업데이트)")
    print()
    print("옵션:")
    print("    --db <path>             DB 파일 경로 지정")
    print("    --table [name]          특정 테이블만 대상")
    print("    --dry-run               실제 수정 없이 분석만")
    print("    --interactive           각 단계마다 사용자 승인")
    print("    --report                리포트 생성 (tmp/)")
    print()
    print("예시:")
    print("    uv run python .claude/skills/oodb/scripts/oodb_run.py status")
    print("    uv run python .claude/skills/oodb/scripts/oodb_run.py run")
    print("    uv run python .claude/skills/oodb/scripts/oodb_run.py optimize --table users")


def extract_db_issues_from_todo():
    """d0004_todo.md에서 DB 관련 이슈 추출"""
    if not TODO_FILE.exists():
        return []

    content = TODO_FILE.read_text(encoding="utf-8")
    issues = []

    # 테이블 형식 파싱: | ID | 날짜 | 내용 | 우선순위 | 상태 |
    pattern = r"\|\s*(D\d+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|"

    for match in re.finditer(pattern, content):
        issue_id = match.group(1).strip()
        date = match.group(2).strip()
        desc = match.group(3).strip()
        priority = match.group(4).strip()
        status = match.group(5).strip()

        issues.append({
            "id": issue_id,
            "date": date,
            "description": desc,
            "priority": priority,
            "status": status
        })

    return issues


def get_db_info(db_path):
    """DB 기본 정보 조회"""
    if not db_path.exists():
        return None

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 테이블 목록
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        # 인덱스 목록
        cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index'")
        indexes = cursor.fetchall()

        conn.close()

        return {
            "tables": tables,
            "indexes": indexes,
            "table_count": len(tables),
            "index_count": len(indexes)
        }
    except Exception as e:
        return {"error": str(e)}


def check_integrity(db_path):
    """DB 무결성 검사"""
    issues = []

    if not db_path.exists():
        return [{"type": "ERROR", "message": f"DB 파일을 찾을 수 없습니다: {db_path}"}]

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 1. 무결성 검사
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()[0]
        if result != "ok":
            issues.append({
                "type": "INTEGRITY",
                "message": f"무결성 검사 실패: {result}"
            })

        # 2. FK 검사
        cursor.execute("PRAGMA foreign_key_check")
        fk_issues = cursor.fetchall()
        for fk in fk_issues:
            issues.append({
                "type": "FK",
                "message": f"FK 위반: 테이블 {fk[0]}, rowid {fk[1]}, 참조 테이블 {fk[2]}"
            })

        conn.close()
    except Exception as e:
        issues.append({
            "type": "ERROR",
            "message": str(e)
        })

    return issues


def analyze_optimization_candidates(db_path, target_table=None):
    """최적화 대상 분석"""
    candidates = []

    if not db_path.exists():
        return candidates

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 테이블 목록
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        if target_table:
            tables = [t for t in tables if target_table.lower() in t.lower()]

        for table in tables:
            suggestions = []

            # 1. 테이블 크기 확인
            cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
            row_count = cursor.fetchone()[0]

            # 2. 인덱스 현황 확인
            cursor.execute(f"PRAGMA index_list({table})")
            indexes = cursor.fetchall()

            # 3. 컬럼 정보
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()

            # 최적화 제안
            if row_count > 10000 and len(indexes) == 0:
                suggestions.append("대용량 테이블에 인덱스 없음 - 인덱스 추가 검토")

            if row_count > 100000:
                suggestions.append(f"대용량 테이블 ({row_count:,}행) - 파티셔닝 검토")

            # PK 없는 경우
            has_pk = any(col[5] for col in columns)  # col[5]는 pk 플래그
            if not has_pk:
                suggestions.append("PK 없음 - PK 추가 검토")

            if suggestions:
                candidates.append({
                    "table": table,
                    "row_count": row_count,
                    "index_count": len(indexes),
                    "column_count": len(columns),
                    "suggestions": suggestions
                })

        conn.close()
    except Exception as e:
        candidates.append({
            "table": "ERROR",
            "suggestions": [str(e)]
        })

    return candidates


def get_next_todo_id():
    """다음 TODO ID 생성"""
    if not TODO_FILE.exists():
        return f"{ID_PREFIX}001"

    content = TODO_FILE.read_text(encoding="utf-8")
    pattern = rf"\|\s*{ID_PREFIX}(\d+)\s*\|"
    matches = re.findall(pattern, content)

    if not matches:
        return f"{ID_PREFIX}001"

    max_num = max(int(m) for m in matches)
    return f"{ID_PREFIX}{max_num + 1:03d}"


def cmd_status(db_path, options):
    """상태 및 이슈 요약"""
    print("# oodb status\n")

    # 0. 서브명령어 리스트
    print("## 서브명령어\n")
    print("| 명령어 | 설명 |")
    print("|--------|------|")
    print("| `oodb status` | 서브명령어 리스트, DB 상태/미해결 이슈 |")
    print("| `oodb run` | validate + 분석 + 수정 (3-Phase 통합) |")
    print("| `oodb validate` | SQL 쿼리 스키마 검증만 (EXPLAIN) |")
    print("| `oodb optimize` | run + 최적화 |")
    print("| `oodb doc` | d0006_db.md 문서화 |")
    print()

    # 1. DB 기본 정보
    print("## DB 기본 정보\n")

    if not db_path.exists():
        print(f"[ERROR] DB 파일을 찾을 수 없습니다: {db_path}")
        return 1

    info = get_db_info(db_path)

    if "error" in info:
        print(f"[ERROR] {info['error']}")
        return 1

    print(f"  DB 경로: {db_path}")
    print(f"  파일 크기: {db_path.stat().st_size:,} bytes")
    print(f"  테이블 수: {info['table_count']}개")
    print(f"  인덱스 수: {info['index_count']}개")
    print()

    # 테이블 목록
    print("### 테이블 목록")
    for table in info["tables"][:10]:
        print(f"  - {table}")
    if len(info["tables"]) > 10:
        print(f"  ... 외 {len(info['tables']) - 10}개")
    print()

    # 2. 무결성 검사
    print("## 무결성 검사\n")

    integrity_issues = check_integrity(db_path)

    if not integrity_issues:
        print("  [OK] 무결성 검사 통과")
    else:
        print(f"  [WARNING] {len(integrity_issues)}개 이슈 발견")
        for issue in integrity_issues[:5]:
            print(f"    [{issue['type']}] {issue['message']}")
    print()

    # 3. d0004 이슈 현황
    print("## d0004_todo.md DB 관련 이슈\n")

    issues = extract_db_issues_from_todo()

    if not issues:
        print("  DB 관련 이슈가 없습니다.")
    else:
        pending = [i for i in issues if i["status"] in ["대기", "pending"]]
        in_progress = [i for i in issues if i["status"] in ["진행중", "in_progress"]]

        print(f"  대기 중: {len(pending)}개")
        print(f"  진행 중: {len(in_progress)}개")
        print()

        for issue in issues[:5]:
            print(f"  [{issue['id']}] {issue['description'][:50]}...")
    print()

    print("---")
    print("[TIP] 'oodb run'으로 문제점 수정을 시작하세요.")

    return 0


def cmd_run(db_path, options):
    """현재 문제점 수정"""
    print("# oodb run\n")
    print("=== DB 문제점 수정 ===\n")

    dry_run = options.get("dry_run", False)
    target_table = options.get("table")

    if dry_run:
        print("[DRY-RUN] 실제 수정 없이 분석만 수행합니다.\n")

    # 1. DB 확인
    print("## 1단계: DB 확인\n")

    if not db_path.exists():
        print(f"[ERROR] DB 파일을 찾을 수 없습니다: {db_path}")
        return 1

    info = get_db_info(db_path)
    print(f"  DB: {db_path.name}")
    print(f"  테이블: {info['table_count']}개")
    print()

    # 2. d0004 이슈 확인
    print("## 2단계: d0004_todo.md 이슈 확인\n")

    issues = extract_db_issues_from_todo()
    pending_issues = [i for i in issues if i["status"] in ["대기", "pending"]]

    print(f"  DB 관련 대기 이슈: {len(pending_issues)}개\n")

    # 3. 무결성 검사
    print("## 3단계: 무결성 검사\n")

    integrity_issues = check_integrity(db_path)

    if not integrity_issues:
        print("  [OK] 무결성 검사 통과")
    else:
        print(f"  [WARNING] {len(integrity_issues)}개 이슈 발견")
        for issue in integrity_issues:
            print(f"    [{issue['type']}] {issue['message']}")
    print()

    # 4. 수정 대상 요약
    print("## 4단계: 수정 대상 요약\n")

    total_issues = len(pending_issues) + len(integrity_issues)

    if total_issues == 0:
        print("  수정할 이슈가 없습니다. DB가 정상입니다.")
        return 0

    print(f"  총 {total_issues}개 이슈\n")

    # 5. 수정 가이드
    print("## 5단계: 수정 가이드\n")
    print("  [INFO] oodb는 서브에이전트 기반으로 동작합니다.")
    print("  [TIP] Task tool로 data-analyst, task-executor를 사용하세요.")
    print()
    print("### 수정 워크플로우")
    print("  1. 이슈별로 TODO 상태를 '진행중'으로 변경")
    print("  2. 스키마/데이터 수정 수행")
    print("  3. 무결성 재검증")
    print("  4. 수정 완료 시 '해결된 이슈' 섹션으로 이동")
    print()

    if dry_run:
        print("[DRY-RUN] 완료. 실제 수정은 수행되지 않았습니다.")

    return 0


def cmd_optimize(db_path, options):
    """문제점 수정 + 최적화"""
    print("# oodb optimize\n")
    print("=== DB 수정 + 최적화 ===\n")

    dry_run = options.get("dry_run", False)
    target_table = options.get("table")

    if dry_run:
        print("[DRY-RUN] 실제 수정 없이 분석만 수행합니다.\n")

    # 1. run 워크플로우 먼저 실행
    print("## Phase 1: 문제점 수정 (run)\n")
    cmd_run(db_path, options)

    print("\n" + "=" * 50 + "\n")

    # 2. 최적화 분석
    print("## Phase 2: 최적화 분석\n")

    candidates = analyze_optimization_candidates(db_path, target_table)

    if not candidates:
        print("  최적화가 필요한 테이블이 없습니다.")
    else:
        print(f"### 최적화 대상 테이블 ({len(candidates)}개)\n")

        for item in candidates:
            print(f"  **{item['table']}**")
            if "row_count" in item:
                print(f"    - 행 수: {item['row_count']:,}")
                print(f"    - 인덱스: {item['index_count']}개")
            for suggestion in item["suggestions"]:
                print(f"    - [제안] {suggestion}")
            print()

    # 3. 최적화 체크리스트
    print("### 최적화 체크리스트\n")
    print("  [ ] 자주 조회되는 컬럼에 인덱스 추가")
    print("  [ ] 복합 인덱스 검토")
    print("  [ ] 미사용 인덱스 제거")
    print("  [ ] N+1 쿼리 제거")
    print("  [ ] 정규화/역정규화 검토")
    print()

    # 4. 가이드
    print("## 최적화 가이드\n")
    print("  [INFO] oodb optimize는 서브에이전트 기반으로 동작합니다.")
    print("  [TIP] data-analyst로 상세 분석을 받으세요.")
    print()
    print("### TODO 등록 형식")
    print(f"  | {get_next_todo_id()} | {datetime.now().strftime('%Y-%m-%d')} | [OPT] table_name - 설명 | 중간 | 대기 |")
    print()

    if dry_run:
        print("[DRY-RUN] 완료. 실제 수정은 수행되지 않았습니다.")

    return 0


def cmd_schema(db_path, options):
    """스키마 추출"""
    print("# oodb schema\n")

    if not db_path.exists():
        print(f"[ERROR] DB 파일을 찾을 수 없습니다: {db_path}")
        return 1

    target_table = options.get("table")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 테이블 목록
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        if target_table:
            tables = [t for t in tables if target_table.lower() in t.lower()]

        print(f"DB: {db_path.name}\n")

        for table in sorted(tables):
            print(f"## {table}\n")

            # 컬럼 정보
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()

            print("| 컬럼명 | 타입 | PK | NULL | 기본값 |")
            print("|--------|------|----|------|--------|")

            for col in columns:
                cid, name, ctype, notnull, default, pk = col
                pk_mark = "O" if pk else ""
                null_mark = "N" if notnull else "Y"
                default_val = default if default else ""
                print(f"| {name} | {ctype} | {pk_mark} | {null_mark} | {default_val} |")

            print()

        conn.close()
        print(f"---\n총 {len(tables)}개 테이블")

    except Exception as e:
        print(f"[ERROR] {e}")
        return 1

    return 0


def cmd_doc(db_path, options):
    """문서화만 수행"""
    print("# oodb doc\n")
    print("=== d0006_db.md 문서 업데이트 ===\n")

    # 기존 oodb_update.py의 문서화 로직 호출
    from oodb_update import cmd_run as update_run
    return update_run(db_path, export_words=True)


def parse_options(args):
    """옵션 파싱"""
    options = {
        "dry_run": "--dry-run" in args,
        "interactive": "--interactive" in args,
        "report": "--report" in args,
        "table": None,
        "db_path": DEFAULT_DB_PATH
    }

    # --table [name]
    if "--table" in args:
        idx = args.index("--table")
        if idx + 1 < len(args) and not args[idx + 1].startswith("--"):
            options["table"] = args[idx + 1]

    # --db <path>
    if "--db" in args:
        idx = args.index("--db")
        if idx + 1 < len(args):
            db_path = Path(args[idx + 1])
            if not db_path.is_absolute():
                db_path = PROJECT_ROOT / db_path
            options["db_path"] = db_path

    return options


def cmd_show_checklist():
    """references/checklist.md 내용 출력"""
    checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[{SKILL_NAME}] checklist.md 없음: {checklist_path}")
        return
    print(checklist_path.read_text(encoding="utf-8"))


def main():
    # 서브명령어 없이 실행 시 도움말 출력
    if not sys.argv[1:]:
        sys.argv.append("run")

    print(f"Log started at {datetime.now()}")

    args = sys.argv[1:]

    if not args:
        print_usage()
        return 0

    cmd = args[0].lower()
    if cmd in ("show",) and len(args) > 1 and args[1].lower() == "checklist":
        cmd_show_checklist()
        return
    options = parse_options(args)
    db_path = options["db_path"]

    if cmd == "status":
        return cmd_status(db_path, options)
    elif cmd == "run":
        return cmd_run(db_path, options)
    elif cmd == "optimize":
        return cmd_optimize(db_path, options)
    elif cmd == "check":
        # check [--fix]: --fix 있으면 optimize, 없으면 안내
        if options.get("fix") or "--fix" in args:
            return cmd_optimize(db_path, options)
        print(f"[check] oodb 체크리스트 안내 (--fix 로 optimize 수행)")
        _print_skill_help("oodb")
        return 0
    elif cmd == "doc":
        return cmd_doc(db_path, options)
    elif cmd in ("help", "-h"):
        _print_skill_help("oodb")
        return 0
    else:
        print(f"[ERROR] Unknown command: {cmd}")
        print_usage()
        return 1


if __name__ == "__main__":
    sys.exit(main())
