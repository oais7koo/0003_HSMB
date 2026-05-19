#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oohistory_run.py - 프로젝트 변경 이력 관리 (상세: doc/a0009_script.md)"""

import sys
import sys as _sys
if _sys.stdout.encoding and _sys.stdout.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stdout.reconfigure(encoding='utf-8')
if _sys.stderr.encoding and _sys.stderr.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stderr.reconfigure(encoding='utf-8')
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# --- oo_common inline ---
import re as _re
_SKILLS_DIR = Path(__file__).parent.parent.parent

def _print_skill_help(skill_name):
    if sys.stdout.encoding and sys.stdout.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
        sys.stdout.reconfigure(encoding='utf-8')
    _sf = _SKILLS_DIR / skill_name / "SKILL.md"
    if not _sf.exists():
        print(f"[ERROR] .agents/skills/{skill_name}/SKILL.md not found")
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

SKILL_NAME = "cchistory"
VERSION = "v01"
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent
DOC_DIR = PROJECT_ROOT / "00_doc"
HISTORY_FILE = DOC_DIR / "sp00" / "d0010_history.md"
TODO_FILE = DOC_DIR / "sp00" / "d0004_todo.md"

# --- SP 지원 ---
def _get_sp_from_state() -> int:
    state_file = PROJECT_ROOT / ".omc" / "state" / "context.json"
    if state_file.exists():
        try:
            import json as _json
            data = _json.loads(state_file.read_text(encoding="utf-8"))
            return int(data.get("sp", 0))
        except Exception:
            pass
    return 0

def _detect_sp_cwd() -> int:
    for part in Path.cwd().parts:
        for sp in range(1, 10):
            if part.startswith(f"0{sp}_"):
                return sp
    return 0

def resolve_sp(sp_arg=None) -> int:
    """SP 번호 결정: --sp 인자 > cccontext 상태 > CWD 감지 > 기본값 0"""
    if sp_arg is not None:
        return int(sp_arg)
    ctx = _get_sp_from_state()
    if ctx:
        return ctx
    return _detect_sp_cwd()

def get_sp_doc_dir(sp_num: int) -> Path:
    return PROJECT_ROOT / "00_doc" / f"sp{sp_num:02d}"

def get_doc_path(sp_num: int, base_num: int, suffix: str) -> Path:
    if sp_num == 0:
        filename = f"d{base_num:04d}_{suffix}.md"
    else:
        filename = f"d{sp_num * 10000 + base_num}_{suffix}.md"
    return get_sp_doc_dir(sp_num) / filename
# --- end SP 지원 ---

import re

# 유효한 태그 목록
VALID_TAGS = ["HOTFIX", "BUGFIX", "IMPROVE", "ENHANCE", "FEATURE", "REFACTOR", "DOCS", "CONFIG"]

# 이슈 우선순위 → 이력 태그 매핑
PRIORITY_TO_TAG = {
    "CRITICAL": "HOTFIX",
    "ERROR": "BUGFIX",
    "WARNING": "IMPROVE",
    "INFO": "ENHANCE"
}


def print_usage():
    """사용법 출력"""
    print(f"Log started at {datetime.now()}")
    print("cchistory - 프로젝트 변경 이력 관리")
    print()
    print("사용법:")
    print("    cchistory run              이력 현황 조회 (기본)")
    print("    cchistory run [태그] [제목] 이력 항목 추가")
    print("    cchistory list             최근 이력 조회 (최근 10건)")
    print("    cchistory create           d0010_history.md 신규 생성")
    print("    cchistory search [키워드]  이력 검색")
    print("    cchistory version          버전 목록 조회")
    print("    cchistory sync             ccfix 완료 항목 동기화")
    print()
    print("태그 종류:")
    print("    HOTFIX   - 긴급 수정")
    print("    BUGFIX   - 버그 수정")
    print("    IMPROVE  - 개선 사항")
    print("    ENHANCE  - 기능 향상")
    print("    FEATURE  - 신규 기능")
    print("    REFACTOR - 코드 리팩토링")
    print("    DOCS     - 문서 변경")
    print("    CONFIG   - 설정 변경")
    print()
    print("옵션:")
    print("    --dry-run               sync 시 미리보기만 (실제 동기화 안 함)")
    print("    --force                 create 시 기존 파일 덮어쓰기")
    print()
    print("예시:")
    print("    python .agents/skills/cchistory/scripts/oohistory_run.py run")
    print("    python .agents/skills/cchistory/scripts/oohistory_run.py run BUGFIX \"API 버그 수정\"")
    print("    python .agents/skills/cchistory/scripts/oohistory_run.py search DB")
    print("    python .agents/skills/cchistory/scripts/oohistory_run.py sync --dry-run")


def parse_history_entries(content):
    """d0010_history.md에서 이력 항목 파싱"""
    entries = []

    # #### YYYY-MM-DD 또는 #### YYYY-MM-DD - [TAG] 패턴
    pattern = r"####\s+(\d{4}-\d{2}-\d{2})(?:\s+-\s+)?(\w+)?\s*(.*?)(?=\n####|\n###|\Z)"

    matches = re.finditer(pattern, content, re.DOTALL)
    for m in matches:
        date = m.group(1)
        tag = m.group(2) or ""
        rest = m.group(3).strip()

        # 제목 추출
        lines = rest.split("\n")
        title = lines[0].strip() if lines else ""

        entries.append({
            "date": date,
            "tag": tag,
            "title": title,
            "body": rest
        })

    return entries


def parse_versions(content):
    """버전 정보 파싱"""
    versions = []

    # ### X.X [vN.N.N] 또는 ### X.X vN.N.N 패턴
    pattern = r"###\s+\d+\.\d+\s+(v[\d.]+|\[현재 버전\])(?:\s+\(([^)]+)\))?"

    matches = re.finditer(pattern, content)
    for m in matches:
        version = m.group(1)
        status = m.group(2) or "릴리스됨"
        versions.append({
            "version": version,
            "status": status
        })

    return versions


def cmd_run(args):
    """이력 현황 조회 또는 이력 추가 (run 서브명령어)"""
    print("# cchistory run\n")

    # 인자가 있으면 이력 추가
    if args:
        return add_history_entry(args)

    # 없으면 현황 조회
    if not HISTORY_FILE.exists():
        print(f"[WARN] {HISTORY_FILE}가 없습니다.")
        print("[TIP] cchistory create 로 생성하세요.")
        return 0

    content = HISTORY_FILE.read_text(encoding="utf-8")
    entries = parse_history_entries(content)

    print(f"이력 파일: {HISTORY_FILE}")
    print()

    # 태그별 집계
    tag_counts = defaultdict(int)
    for e in entries:
        if e['tag']:
            tag_counts[e['tag']] += 1

    print("## 태그별 현황\n")
    print("| 태그 | 건수 |")
    print("|------|------|")
    for tag in VALID_TAGS:
        count = tag_counts.get(tag, 0)
        if count > 0:
            print(f"| {tag} | {count} |")

    print()
    print(f"---\n총 {len(entries)}건")
    return 0


def add_history_entry(args):
    """이력 항목 추가"""
    if len(args) < 2:
        print("[ERROR] 태그와 제목을 모두 지정하세요.")
        print("사용법: cchistory run [태그] [제목]")
        return 1

    tag = args[0].upper()
    title = " ".join(args[1:])

    if tag not in VALID_TAGS:
        print(f"[ERROR] 유효하지 않은 태그: {tag}")
        print(f"유효한 태그: {', '.join(VALID_TAGS)}")
        return 1

    if not HISTORY_FILE.exists():
        print(f"[WARN] {HISTORY_FILE}가 없습니다.")
        print("[TIP] cchistory create 로 먼저 생성하세요.")
        return 1

    content = HISTORY_FILE.read_text(encoding="utf-8")

    # 현재 날짜
    today = datetime.now().strftime("%Y-%m-%d")

    # 새 항목
    new_entry = f"\n#### {today} - {tag} {title}\n- **파일**: `(파일 경로)`\n- **내용**: (변경 내용)\n"

    # "진행중" 섹션 찾기
    in_progress_pattern = r"(###\s+\d+\.\d+\s+\[현재 버전\]\s*\(진행중\))"
    match = re.search(in_progress_pattern, content)

    if match:
        # 진행중 섹션 바로 뒤에 추가
        insert_pos = match.end()
        content = content[:insert_pos] + new_entry + content[insert_pos:]
    else:
        # 없으면 "## 2. 변경 이력" 섹션 뒤에 추가
        change_section = re.search(r"(##\s+\d+\.\s+변경 이력)", content)
        if change_section:
            insert_pos = change_section.end()
            content = content[:insert_pos] + new_entry + content[insert_pos:]
        else:
            content += new_entry

    HISTORY_FILE.write_text(content, encoding="utf-8")
    print(f"[OK] 이력 추가됨: [{tag}] {title}")
    print(f"파일: {HISTORY_FILE}")
    return 0


def cmd_list():
    """최근 이력 조회 (list 서브명령어)"""
    print("# cchistory list\n")

    if not HISTORY_FILE.exists():
        print(f"[WARN] {HISTORY_FILE}가 없습니다.")
        return 0

    content = HISTORY_FILE.read_text(encoding="utf-8")
    entries = parse_history_entries(content)

    if not entries:
        print("[INFO] 이력 항목이 없습니다.")
        return 0

    # 최근 10건
    recent = entries[:10]

    print("## 최근 이력 (최대 10건)\n")
    print("| 날짜 | 태그 | 제목 |")
    print("|------|------|------|")

    for e in recent:
        tag = e['tag'] or "-"
        title = e['title'][:40] if e['title'] else "-"
        print(f"| {e['date']} | {tag} | {title} |")

    print()
    print(f"---\n총 {len(entries)}건 중 {len(recent)}건 표시")
    return 0


def cmd_create():
    """d0010_history.md 신규 생성 (create 서브명령어)"""
    print("# cchistory create\n")

    if HISTORY_FILE.exists():
        print(f"[WARN] {HISTORY_FILE}가 이미 존재합니다.")
        if "--force" not in sys.argv:
            print("[INFO] 덮어쓰려면 --force 옵션을 사용하세요.")
            return 1

    today = datetime.now().strftime("%Y-%m-%d")

    template = f"""# d0010_history.md - 프로젝트 변경 이력

## 문서 이력 관리
| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v01 | {today} | 최초 생성 |

---

## 1. 개요

이 문서는 프로젝트의 주요 변경사항을 기록합니다.

---

## 2. 변경 이력

### 2.1 [현재 버전] (진행중)

#### {today} - DOCS 이력 문서 생성
- **파일**: `doc/d0010_history.md`
- **내용**: 변경 이력 문서 최초 생성

---

## 3. 버전 요약

| 버전 | 날짜 | 주요 변경 | 항목 수 |
|------|------|----------|--------|
| [현재] | {today} | 초기 설정 | 1건 |

---

## 4. 통계

### 4.1 태그별 현황

| 태그 | 건수 | 비율 |
|------|------|------|
| DOCS | 1 | 100% |

---
"""

    DOC_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(template, encoding="utf-8")
    print(f"[OK] 이력 문서 생성됨: {HISTORY_FILE}")
    return 0


def cmd_search(args):
    """이력 검색 (search 서브명령어)"""
    print("# cchistory search\n")

    if not args:
        print("[ERROR] 검색 키워드를 지정하세요.")
        print("사용법: cchistory search [키워드]")
        return 1

    keyword = " ".join(args).lower()

    if not HISTORY_FILE.exists():
        print(f"[WARN] {HISTORY_FILE}가 없습니다.")
        return 0

    content = HISTORY_FILE.read_text(encoding="utf-8")
    entries = parse_history_entries(content)

    # 키워드 검색
    results = []
    for e in entries:
        search_text = f"{e['tag']} {e['title']} {e['body']}".lower()
        if keyword in search_text:
            results.append(e)

    print(f"검색어: {keyword}")
    print()

    if not results:
        print("[INFO] 검색 결과가 없습니다.")
        return 0

    print(f"## 검색 결과: {len(results)}건\n")
    print("| 날짜 | 태그 | 제목 |")
    print("|------|------|------|")

    for e in results:
        tag = e['tag'] or "-"
        title = e['title'][:40] if e['title'] else "-"
        print(f"| {e['date']} | {tag} | {title} |")

    return 0


def cmd_version():
    """버전 목록 조회 (version 서브명령어)"""
    print("# cchistory version\n")

    if not HISTORY_FILE.exists():
        print(f"[WARN] {HISTORY_FILE}가 없습니다.")
        return 0

    content = HISTORY_FILE.read_text(encoding="utf-8")
    versions = parse_versions(content)

    if not versions:
        print("[INFO] 버전 정보가 없습니다.")
        return 0

    print("## 버전 목록\n")
    print("| 버전 | 상태 |")
    print("|------|------|")

    for v in versions:
        print(f"| {v['version']} | {v['status']} |")

    print()
    print(f"---\n총 {len(versions)}개 버전")
    return 0


def cmd_sync():
    """ccfix 완료 항목 동기화 (sync 서브명령어)"""
    dry_run = "--dry-run" in sys.argv
    print("# cchistory sync\n")
    if dry_run:
        print("[DRY-RUN] 실제 동기화 없이 미리보기만 실행\n")

    if not TODO_FILE.exists():
        print(f"[WARN] {TODO_FILE}가 없습니다.")
        return 0

    if not HISTORY_FILE.exists():
        print(f"[WARN] {HISTORY_FILE}가 없습니다.")
        print("[TIP] cchistory create 로 먼저 생성하세요.")
        return 0

    todo_content = TODO_FILE.read_text(encoding="utf-8")

    # "해결됨" 상태 항목 찾기
    # 패턴: - [x] [PRIORITY] 설명 또는 해결됨/완료 표시가 있는 항목
    resolved_pattern = r"-\s*\[x\]\s*\[(\w+)\]\s*(.+?)(?:\n|$)"

    matches = re.finditer(resolved_pattern, todo_content, re.IGNORECASE)
    resolved_items = []

    for m in matches:
        priority = m.group(1).upper()
        description = m.group(2).strip()

        # 태그 매핑
        tag = PRIORITY_TO_TAG.get(priority, "IMPROVE")

        resolved_items.append({
            "priority": priority,
            "tag": tag,
            "description": description
        })

    if not resolved_items:
        print("[INFO] 동기화할 완료 항목이 없습니다.")
        return 0

    print(f"## 동기화 대상: {len(resolved_items)}건\n")

    for item in resolved_items:
        print(f"  [{item['priority']}] -> [{item['tag']}] {item['description'][:40]}")

    print()

    if dry_run:
        print("[DRY-RUN] 미리보기 완료")
        print("[TIP] 실제 동기화: cchistory sync (--dry-run 제거)")
        return 0

    # 실행
    history_content = HISTORY_FILE.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")

    added = 0
    for item in resolved_items:
        new_entry = f"\n#### {today} - {item['tag']} {item['description']}\n- **원본**: d0004_todo.md [{item['priority']}]\n"

        # 진행중 섹션에 추가
        in_progress_pattern = r"(###\s+\d+\.\d+\s+\[현재 버전\]\s*\(진행중\))"
        match = re.search(in_progress_pattern, history_content)

        if match:
            insert_pos = match.end()
            history_content = history_content[:insert_pos] + new_entry + history_content[insert_pos:]
            added += 1

    if added > 0:
        HISTORY_FILE.write_text(history_content, encoding="utf-8")
        print(f"\n[OK] {added}건 동기화 완료")
    else:
        print("[WARN] 진행중 섹션을 찾을 수 없습니다.")

    return 0


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

    # --sp 옵션 추출
    sp_arg = None
    for _i, _a in enumerate(args):
        if _a == "--sp" and _i + 1 < len(args):
            try:
                sp_arg = int(args[_i + 1])
            except ValueError:
                pass
            args = args[:_i] + args[_i + 2:]
            break

    # SP 결정 및 전역 경로 업데이트
    global HISTORY_FILE, TODO_FILE, DOC_DIR
    sp_num = resolve_sp(sp_arg)
    DOC_DIR = get_sp_doc_dir(sp_num)
    HISTORY_FILE = get_doc_path(sp_num, 10, "history")
    TODO_FILE = get_doc_path(sp_num, 4, "todo")
    if sp_num:
        print(f"[INFO] SP{sp_num:02d} 컨텍스트 적용")

    if not args:
        print_usage()
        return 0

    cmd = args[0].lower()
    if cmd in ("show",) and len(args) > 1 and args[1].lower() == "checklist":
        cmd_show_checklist()
        return
    cmd_args = args[1:]

    # 옵션 제거
    cmd_args = [a for a in cmd_args if not a.startswith("--")]

    if cmd == "run":
        return cmd_run(cmd_args)
    elif cmd == "list":
        return cmd_list()
    elif cmd == "create":
        return cmd_create()
    elif cmd == "search":
        return cmd_search(cmd_args)
    elif cmd == "version":
        return cmd_version()
    elif cmd == "sync":
        return cmd_sync()
    elif cmd == "check":
        print(f"[check] cchistory 체크리스트 안내")
        _print_skill_help("cchistory")
        return 0
    elif cmd in ("help", "-h"):
        _print_skill_help("cchistory")
        return 0
    else:
        print(f"[ERROR] Unknown command: {cmd}")
        print_usage()
        return 1


if __name__ == "__main__":
    sys.exit(main())
