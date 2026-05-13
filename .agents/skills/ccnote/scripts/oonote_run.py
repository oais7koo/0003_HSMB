"""
[oonote_run.py]
연구노트 관리 스크립트.
날짜/시간 기반으로 d{SP}0020_연구노트.md에 노트를 추가하고 조회합니다.

사용법:
    uv run python .claude/skills/ccnote/scripts/oonote_run.py add "내용" [--title "제목"] [--tag "태그"] [--ref "참조"] [--sp N]
    uv run python .claude/skills/ccnote/scripts/oonote_run.py today [--sp N]
    uv run python .claude/skills/ccnote/scripts/oonote_run.py list [날짜] [--all] [--sp N]
    uv run python .claude/skills/ccnote/scripts/oonote_run.py search "키워드" [--tag "태그"] [--date "YYYY-MM"] [--limit N] [--sp N]
    uv run python .claude/skills/ccnote/scripts/oonote_run.py status [--sp N]
    uv run python .claude/skills/ccnote/scripts/oonote_run.py init [--sp N]
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

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

# Windows CP949 인코딩 문제 방지
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# scripts/ → ccnote/ → skills/ → .claude/ → PROJECT_ROOT
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
DOC_BASE = PROJECT_ROOT / "00_doc"

# SP별 문서 파일명 매핑 (번호 = d{SP}0020)
SP_DOC_MAP = {
    0:  "d0020_연구노트.md",
    1:  "d10020_연구노트.md",
    2:  "d20020_연구노트.md",
    3:  "d30020_연구노트.md",
    4:  "d40020_연구노트.md",
    5:  "d50020_연구노트.md",
    6:  "d60020_연구노트.md",
    7:  "d70020_연구노트.md",
}

WEEKDAY_KO = ["월", "화", "수", "목", "금", "토", "일"]

# 태그 목록
KNOWN_TAGS = ["실험", "분석", "회의", "아이디어", "문제", "해결", "참고", "계획"]


def get_note_file(sp: int) -> Path:
    filename = SP_DOC_MAP.get(sp, "d0020_연구노트.md")
    return DOC_BASE / filename


def get_project_name(sp: int) -> str:
    names = {
        0: "OAIS",
        1: "Obsidian",
        2: "PyCode",
        3: "Paper",
        4: "YouTube GraphRAG",
        5: "KWorks Web",
        6: "SSweb",
        7: "KWweb",
    }
    return names.get(sp, f"SP{sp:02d}")


def format_date_header(dt: datetime) -> str:
    weekday = WEEKDAY_KO[dt.weekday()]
    return f"## {dt.strftime('%Y-%m-%d')} ({weekday})"


def init_note_file(note_file: Path, sp: int):
    """연구노트 파일 초기 생성."""
    project_name = get_project_name(sp)
    today = datetime.now().strftime("%Y-%m-%d")
    content = f"""# {project_name} 연구노트

## 문서이력관리

| 버전 | 날짜 | 변경내용 |
|------|------|---------|
| v01 | {today} | 초기 생성 |

---

"""
    note_file.parent.mkdir(parents=True, exist_ok=True)
    note_file.write_text(content, encoding="utf-8")
    print(f"[OK] 연구노트 파일 생성: {note_file.relative_to(PROJECT_ROOT)}")


def bump_version(content: str, today: str) -> str:
    """문서이력관리 테이블에서 최신 버전을 증가시킨다."""
    lines = content.splitlines()
    last_version = "v01"
    last_version_line = -1

    for i, line in enumerate(lines):
        if line.startswith("| v") and "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3 and parts[1].startswith("v"):
                last_version = parts[1]
                last_version_line = i

    if last_version_line == -1:
        return content

    # 버전 증가 (v01 → v02)
    try:
        num = int(last_version[1:]) + 1
        new_version = f"v{num:02d}"
    except ValueError:
        return content

    new_line = f"| {new_version} | {today} | 연구노트 추가 |"
    lines.insert(last_version_line + 1, new_line)
    return "\n".join(lines)


def cmd_add(args):
    note_file = get_note_file(args.sp)

    # 파일 없으면 자동 생성
    if not note_file.exists():
        init_note_file(note_file, args.sp)

    content = note_file.read_text(encoding="utf-8")
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    time_str = args.time if args.time else now.strftime("%H:%M")

    # 태그 처리
    tag_str = f"[{args.tag}] " if args.tag else ""
    title_str = args.title if args.title else args.content[:30].replace("\n", " ")
    ref_str = f"\n\n**참조**: `{args.ref}`" if args.ref else ""

    # 새 노트 블록
    note_block = f"""### {time_str} | {tag_str}{title_str}
{args.content}{ref_str}

---
"""

    # 오늘 날짜 섹션 확인
    date_header = format_date_header(now)
    if date_header in content:
        # 오늘 섹션의 첫 번째 ### 이전에 삽입 (섹션 끝에 추가)
        # 단순히 다음 ## 섹션 전에 삽입
        lines = content.splitlines(keepends=True)
        insert_pos = len(lines)
        in_today = False
        for i, line in enumerate(lines):
            if line.strip() == date_header:
                in_today = True
            elif in_today and line.startswith("## ") and line.strip() != date_header:
                insert_pos = i
                break
        lines.insert(insert_pos, note_block + "\n")
        content = "".join(lines)
    else:
        # 오늘 날짜 섹션 추가 (파일 끝에)
        content = content.rstrip() + f"\n\n{date_header}\n\n{note_block}\n"

    # 버전 업데이트
    content = bump_version(content, today_str)

    note_file.write_text(content, encoding="utf-8")
    print(f"[OK] 연구노트 추가 완료")
    print(f"     파일: {note_file.relative_to(PROJECT_ROOT)}")
    print(f"     날짜: {today_str} {time_str}")
    print(f"     내용: {title_str}")


def cmd_today(args):
    note_file = get_note_file(args.sp)
    if not note_file.exists():
        print(f"[INFO] 연구노트 파일 없음: {note_file.relative_to(PROJECT_ROOT)}")
        print("       → `ccnote init` 으로 생성하세요.")
        return

    content = note_file.read_text(encoding="utf-8")
    now = datetime.now()
    date_header = format_date_header(now)

    if date_header not in content:
        print(f"[INFO] 오늘({now.strftime('%Y-%m-%d')}) 작성된 노트가 없습니다.")
        return

    # 오늘 섹션 추출
    lines = content.splitlines()
    in_today = False
    today_lines = []
    for line in lines:
        if line.strip() == date_header:
            in_today = True
            today_lines.append(line)
        elif in_today:
            if line.startswith("## ") and line.strip() != date_header:
                break
            today_lines.append(line)

    print("\n".join(today_lines))


def cmd_list(args):
    note_file = get_note_file(args.sp)
    if not note_file.exists():
        print(f"[INFO] 연구노트 파일 없음: {note_file.relative_to(PROJECT_ROOT)}")
        return

    content = note_file.read_text(encoding="utf-8")
    lines = content.splitlines()

    if args.all or not args.date:
        # 날짜 목록만 출력
        dates = [l.strip() for l in lines if l.startswith("## 20")]
        if not dates:
            print("[INFO] 기록된 날짜가 없습니다.")
            return
        print(f"[연구노트 날짜 목록] {note_file.relative_to(PROJECT_ROOT)}")
        for d in dates:
            # 해당 날짜의 노트 수 세기
            count = 0
            in_section = False
            for l in lines:
                if l.strip() == d:
                    in_section = True
                elif in_section and l.startswith("## 20"):
                    break
                elif in_section and l.startswith("### "):
                    count += 1
            print(f"  {d[3:]}  ({count}개)")
    else:
        # 특정 날짜 조회
        target = args.date
        found = False
        in_section = False
        section_lines = []
        for line in lines:
            if target in line and line.startswith("## "):
                in_section = True
                found = True
                section_lines.append(line)
            elif in_section:
                if line.startswith("## ") and target not in line:
                    break
                section_lines.append(line)
        if found:
            print("\n".join(section_lines))
        else:
            print(f"[INFO] {target} 날짜의 노트가 없습니다.")


def cmd_search(args):
    note_file = get_note_file(args.sp)
    if not note_file.exists():
        print(f"[INFO] 연구노트 파일 없음: {note_file.relative_to(PROJECT_ROOT)}")
        return

    content = note_file.read_text(encoding="utf-8")
    keyword = args.keyword
    limit = args.limit

    results = []
    lines = content.splitlines()
    current_date = ""
    current_time = ""
    current_tag = ""
    current_block = []
    in_block = False

    def flush_block():
        if current_block and keyword.lower() in "\n".join(current_block).lower():
            # 태그 필터
            if args.tag and f"[{args.tag}]" not in "\n".join(current_block):
                return
            # 날짜 필터
            if args.date and not current_date.startswith(args.date):
                return
            results.append({
                "date": current_date,
                "time": current_time,
                "tag": current_tag,
                "lines": current_block[:],
            })

    for line in lines:
        if line.startswith("## 20"):
            current_date = line[3:13] if len(line) > 12 else line[3:]
        elif line.startswith("### "):
            flush_block()
            in_block = True
            current_block = [line]
            # 시간/태그 파싱: "### HH:MM | [태그] 제목"
            rest = line[4:]
            if " | " in rest:
                parts = rest.split(" | ", 1)
                current_time = parts[0].strip()
                title_part = parts[1].strip()
                if title_part.startswith("[") and "]" in title_part:
                    end = title_part.index("]")
                    current_tag = title_part[1:end]
                else:
                    current_tag = ""
            else:
                current_time = ""
                current_tag = ""
        elif in_block and line.strip() == "---":
            current_block.append(line)
            flush_block()
            in_block = False
            current_block = []
        elif in_block:
            current_block.append(line)

    flush_block()

    if not results:
        print(f"[검색] '{keyword}' - 결과 없음")
        return

    print(f"[검색] '{keyword}'  |  {len(results)}건 발견\n")
    for r in results[-limit:]:
        tag_display = f"[{r['tag']}] " if r['tag'] else ""
        header = r['lines'][0] if r['lines'] else ""
        body_lines = [l for l in r['lines'][1:] if l.strip() and l.strip() != "---"]
        body_preview = " ".join(body_lines)[:80]
        print(f"[{r['date']} {r['time']}] {tag_display}{header[4:] if header.startswith('### ') else header}")
        if body_preview:
            print(f"  {body_preview}...")
        print()


def cmd_status(args):
    note_file = get_note_file(args.sp)
    sp_label = f"SP{args.sp:02d}"
    print(f"[ccnote status] {sp_label}")
    print(f"파일  : {note_file.relative_to(PROJECT_ROOT)}")

    if not note_file.exists():
        print("상태  : 파일 없음 (ccnote init 으로 생성)")
        return

    content = note_file.read_text(encoding="utf-8")
    lines = content.splitlines()

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    this_month = now.strftime("%Y-%m")

    total_notes = 0
    today_notes = 0
    month_notes = 0
    date_count = 0
    current_date = ""
    tag_count: dict = {}

    for line in lines:
        if line.startswith("## 20"):
            current_date = line[3:13] if len(line) > 12 else line[3:]
            date_count += 1
        elif line.startswith("### "):
            total_notes += 1
            if current_date == today_str:
                today_notes += 1
            if current_date.startswith(this_month):
                month_notes += 1
            # 태그 집계
            rest = line[4:]
            if " | " in rest:
                title_part = rest.split(" | ", 1)[1].strip()
                if title_part.startswith("[") and "]" in title_part:
                    tag = title_part[1:title_part.index("]")]
                    tag_count[tag] = tag_count.get(tag, 0) + 1

    tag_summary = ", ".join(
        f"[{t}] {c}" for t, c in sorted(tag_count.items(), key=lambda x: -x[1])
    ) or "없음"

    print(f"전체  : {total_notes}개 노트 | {date_count}일 기록")
    print(f"이번달: {month_notes}개 노트 ({this_month})")
    print(f"오늘  : {today_notes}개 노트 ({today_str})")
    print(f"태그  : {tag_summary}")


def cmd_init(args):
    note_file = get_note_file(args.sp)
    if note_file.exists():
        print(f"[INFO] 이미 존재: {note_file.relative_to(PROJECT_ROOT)}")
        return
    init_note_file(note_file, args.sp)


def cmd_show_checklist():
    """references/checklist.md 내용 출력"""
    checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[{SKILL_NAME}] checklist.md 없음: {checklist_path}")
        return
    print(checklist_path.read_text(encoding="utf-8"))


def main():
    if len(sys.argv) > 2 and sys.argv[1].lower() == "show" and sys.argv[2].lower() == "checklist":
        cmd_show_checklist()
        return
    if show_help_if_no_args("ccnote", sys.argv[1:]):
        return 0
    parser = argparse.ArgumentParser(description="ccnote - 연구노트 관리")
    parser.add_argument("--sp", type=int, default=0, metavar="N", help="서브프로젝트 번호 (기본: 0)")
    sub = parser.add_subparsers(dest="command")

    # add
    p_add = sub.add_parser("add", help="연구노트 추가")
    p_add.add_argument("content", help="노트 내용")
    p_add.add_argument("--title", metavar="제목", help="제목 지정")
    p_add.add_argument("--tag", metavar="태그", help="태그 지정 (실험/분석/회의/아이디어/문제/해결/참고/계획)")
    p_add.add_argument("--ref", metavar="참조", help="참조 파일/링크")
    p_add.add_argument("--time", metavar="HH:MM", help="시간 수동 지정")

    # today
    sub.add_parser("today", help="오늘 노트 표시")

    # list
    p_list = sub.add_parser("list", help="날짜별 조회")
    p_list.add_argument("date", nargs="?", help="날짜 (YYYY-MM-DD)")
    p_list.add_argument("--all", action="store_true", help="전체 날짜 목록")

    # search
    p_search = sub.add_parser("search", help="키워드 검색")
    p_search.add_argument("keyword", help="검색 키워드")
    p_search.add_argument("--tag", metavar="태그", help="태그 필터")
    p_search.add_argument("--date", metavar="YYYY-MM", help="월 필터")
    p_search.add_argument("--limit", type=int, default=10, help="최대 결과 수 (기본: 10)")

    # status
    sub.add_parser("status", help="현황 표시")

    # init
    sub.add_parser("init", help="연구노트 파일 초기 생성")

    # check (status의 alias)
    sub.add_parser("check", help="체크리스트/현황 표시")

    args = parser.parse_args()

    if not args.command:
        # 기본: today
        args.command = "today"
        cmd_today(args)
        return

    dispatch = {
        "add": cmd_add,
        "today": cmd_today,
        "list": cmd_list,
        "search": cmd_search,
        "status": cmd_status,
        "init": cmd_init,
        "check": cmd_status,
    }

    if args.command in dispatch:
        dispatch[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
