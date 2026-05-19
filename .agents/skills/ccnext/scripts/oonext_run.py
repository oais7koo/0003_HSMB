#!/usr/bin/env python3
"""
oonext_run.py

PRD, Plan, Todo 문서를 분석하여 다음 우선 작업을 추천한다.
"""

import sys
import os
import re
import json
import argparse
import datetime
from pathlib import Path

# Windows 한글 인코딩 처리
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

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


DOC_DIR = Path("00_doc")
PROJECT_ROOT = Path(".")

# 우선순위 점수 매핑
SCORE_MAP = {
    # todo Active Issues
    "CRITICAL": 100,
    "ERROR": 80,
    "WARNING": 40,
    "INFO": 10,
    # todo 커스텀 Todo
    "high": 70, "높음": 70, "HIGH": 70,
    "medium": 50, "보통": 50, "MEDIUM": 50, "MED": 50,
    "low": 30, "낮음": 30, "LOW": 30,
    # plan 우선순위
    "High": 60,
    "Medium": 40,
    "Low": 20,
    # 기술 부채
    "P1": 55,
    "P2": 35,
    "P3": 20,
}


def get_current_sp() -> str:
    state_file = PROJECT_ROOT / ".omc" / "state" / "context.json"
    if state_file.exists():
        try:
            data = json.loads(state_file.read_text(encoding="utf-8"))
            return data.get("sp", "00")
        except Exception:
            pass
    return "00"


def get_sp_list():
    """활성 서브프로젝트 번호 목록 반환."""
    sps = ["00"]
    for sp_num in range(1, 11):
        prefix = f"{sp_num:02d}_"
        matches = list(PROJECT_ROOT.glob(f"{prefix}*/"))
        if any(m.is_dir() for m in matches):
            sps.append(f"{sp_num:02d}")
    return sps


def resolve_target_sps(current_sp: str, args) -> list:
    """분석 대상 SP 목록을 결정한다."""
    if args.sp is not None:
        return [f"{int(args.sp):02d}"]
    if args.all_sps:
        return get_sp_list()
    return [current_sp]


def doc_path(sp: str, doc_type: str) -> Path:
    """SP별 문서 경로 반환 (SP 서브폴더 구조 대응)."""
    sp_num = int(sp)
    sp_folder = f"sp{sp_num:02d}"
    if sp_num == 0:
        prefix = ""
    else:
        prefix = str(sp_num)
    names = {
        "prd": f"d{prefix}0001_prd.md",
        "plan": f"d{prefix}0002_plan.md",
        "todo": f"d{prefix}0004_todo.md",
    }
    # SP 서브폴더 우선, 없으면 플랫 구조 폴백
    sp_path = DOC_DIR / sp_folder / names[doc_type]
    if sp_path.exists():
        return sp_path
    return DOC_DIR / names[doc_type]


def get_todo_dir(sp: str) -> Path | None:
    """SP의 상세 ToDo 폴더 경로 (`todo/`) 반환. 부재 시 None."""
    sp_num = int(sp)
    sp_folder = f"sp{sp_num:02d}"
    todo_dir = DOC_DIR / sp_folder / "todo"
    return todo_dir if todo_dir.exists() else None


def extract_status_from_detail(detail_path: Path) -> str | None:
    """todo/{ID}.md 헤더에서 상태 추출. (OPEN/IN_PROGRESS/HOLD/DONE)"""
    if not detail_path.exists():
        return None
    try:
        head = detail_path.read_text(encoding="utf-8")[:2000]
    except Exception:
        return None
    m = re.search(r"상태:\s*(\w+)", head)
    return m.group(1) if m else None


def extract_meta_from_detail(detail_path: Path) -> dict | None:
    """todo/{ID}.md 첫 헤더에서 우선순위·상태·제목 추출.

    예: `# R160-2 — get_columns_for_mapping ...`
        `> 우선순위: LOW | 상태: OPEN | 등록: 2026-05-11`
    """
    if not detail_path.exists():
        return None
    try:
        head = detail_path.read_text(encoding="utf-8")[:3000]
    except Exception:
        return None

    title_m = re.search(r"^#\s+\S+\s*(?:—|-)\s*(.+)$", head, re.MULTILINE)
    title = title_m.group(1).strip() if title_m else ""

    prio_m = re.search(r"우선순위:\s*(\w+)", head)
    priority = prio_m.group(1) if prio_m else "medium"

    status_m = re.search(r"상태:\s*(\w+)", head)
    status = status_m.group(1) if status_m else "OPEN"

    return {"title": title, "priority": priority, "status": status}


def extract_todos_from_folder(sp: str) -> list:
    """todo/ 폴더의 모든 {ID}.md를 스캔하여 항목 추출 (DONE 제외)."""
    items = []
    todo_dir = get_todo_dir(sp)
    if todo_dir is None:
        return items

    for md in sorted(todo_dir.glob("*.md")):
        # README·_template 같은 메타 파일 제외
        if md.stem.startswith("_") or md.stem.upper() == "README":
            continue
        meta = extract_meta_from_detail(md)
        if meta is None:
            continue
        if meta["status"] == "DONE":
            continue

        todo_id = md.stem
        priority = meta["priority"]
        score = SCORE_MAP.get(priority, SCORE_MAP.get(priority.upper(), 30))
        if meta["status"] == "HOLD":
            score = max(score // 2, 5)

        prefix = todo_id[0]
        if prefix in ("T", "A", "S", "W", "D"):
            source = "todo/이슈"
        elif prefix == "R":
            source = "todo/리팩토링"
        else:
            source = "todo/커스텀"

        items.append({
            "score": score,
            "source": source,
            "sp": sp,
            "desc": f"{todo_id}: {meta['title'][:60]}",
            "priority": priority,
            "status": meta["status"],
        })
    return items


def read_file_safe(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def extract_todo_items(content: str, sp: str) -> list:
    """## 대기 ToDo 섹션의 모든 ### ID 블록 항목 추출.

    지원 헤더 형식:
      ### {ID} {title}                          (레거시, 등록일 라인 필요)
      ### {ID} [{TYPE}][{PRIORITY}] {title}     (현재 SP04 형식)

    우선순위 추출 순서:
      1. 헤더의 [{PRIORITY}] 태그 (HIGH/MED/LOW/CRITICAL/ERROR/WARNING/INFO)
      2. 블록 본문의 `- 우선순위: {LEVEL}` 라인
      3. 블록 본문의 `등록일: ... 우선순위: ...` (레거시)
      4. 기본값: medium
    """
    items = []
    section_match = re.search(r"^## 대기 ToDo", content, re.MULTILINE)
    if not section_match:
        return items

    next_section = re.search(r"^## ", content[section_match.end():], re.MULTILINE)
    section_end = section_match.end() + next_section.start() if next_section else len(content)
    section_content = content[section_match.end():section_end]

    # 모든 ### 헤더 위치 수집 후 각 블록을 다음 ### 또는 섹션 끝까지로 분할
    headers = list(re.finditer(r"^### (\S+) (.+)$", section_content, re.MULTILINE))
    if not headers:
        return items

    for idx, hdr in enumerate(headers):
        issue_id = hdr.group(1)
        title_raw = hdr.group(2).strip()
        block_start = hdr.end()
        block_end = headers[idx + 1].start() if idx + 1 < len(headers) else len(section_content)
        block = section_content[block_start:block_end]

        # 1) 헤더의 [PRIORITY] 태그에서 추출 (마지막 대괄호 태그를 우선순위로 간주)
        tags = re.findall(r"\[([A-Z가-힣]+)\]", title_raw)
        priority = None
        title_clean = title_raw
        if tags:
            # 마지막 태그가 우선순위일 가능성 높음. 알려진 키워드만 채택.
            known_priorities = {"CRITICAL", "ERROR", "WARNING", "INFO",
                                "HIGH", "MEDIUM", "MED", "LOW",
                                "높음", "보통", "낮음"}
            for tag in reversed(tags):
                if tag in known_priorities:
                    priority = tag
                    break
            # 제목에서 모든 대괄호 태그 제거하여 깔끔한 desc 생성
            title_clean = re.sub(r"\[[A-Z가-힣]+\]", "", title_raw).strip()

        # 2) `- 우선순위:` 라인
        if priority is None:
            m = re.search(r"^\s*-\s*우선순위[:：]\s*(\S+)", block, re.MULTILINE)
            if m:
                priority = m.group(1).rstrip("()[]")

        # 3) 레거시 `등록일: ... 우선순위:` 라인
        if priority is None:
            m = re.search(r"등록일[:：][^\n]*우선순위[:：]\s*(\S+)", block)
            if m:
                priority = m.group(1)

        # 4) 기본값
        if priority is None:
            priority = "medium"

        score = SCORE_MAP.get(priority, SCORE_MAP.get(priority.upper(), 30))

        # ID 접두사로 소스 구분 (T/A/S/W/D = 이슈, R = 리팩토링/요구사항, C/기타 = 커스텀)
        prefix = issue_id[0] if issue_id else "C"
        if prefix in ("T", "A", "S", "W", "D"):
            source = "todo/이슈"
        elif prefix == "R":
            source = "todo/리팩토링"
        else:
            source = "todo/커스텀"

        # 상세 파일 상태 확인 — todo/{ID}.md 가 있으면 우선 적용
        todo_dir = get_todo_dir(sp)
        detail_status = None
        if todo_dir is not None:
            detail_status = extract_status_from_detail(todo_dir / f"{issue_id}.md")
            if detail_status == "DONE":
                continue  # 완료 항목은 추천 제외
            if detail_status == "HOLD":
                score = max(score // 2, 5)  # 보류는 점수 절반 (최소 5)

        items.append({
            "score": score,
            "source": source,
            "sp": sp,
            "desc": f"{issue_id}: {title_clean[:60]}",
            "priority": priority,
            "status": detail_status or "OPEN",
        })
    return items


# 하위 호환을 위한 alias
def extract_todo_issues(content: str, sp: str) -> list:
    """(레거시) extract_todo_items의 이슈 항목만 반환."""
    return [i for i in extract_todo_items(content, sp) if i["source"] == "todo/이슈"]


def extract_todo_custom(content: str, sp: str) -> list:
    """(레거시) extract_todo_items의 커스텀 항목만 반환."""
    return [i for i in extract_todo_items(content, sp) if i["source"] == "todo/커스텀"]


def extract_plan_items(content: str, sp: str) -> list:
    """plan 문서에서 향후 계획 및 기술 부채 항목 추출."""
    items = []

    # "향후 계획" 섹션에서 테이블 추출 (2컬럼: 항목|우선순위 또는 3컬럼: ID|항목|우선순위)
    plan_match = re.search(
        r"##\s*\d+\.\s*향후 계획[^\n]*\n\n?\|[^\n]+\n\|[-\s|]+\n((?:\|[^\n]+\n)*)",
        content, re.IGNORECASE
    )
    if plan_match:
        rows = plan_match.group(1).strip().split("\n")
        for row in rows:
            cells = [c.strip() for c in row.split("|") if c.strip()]
            if len(cells) >= 2:
                # 2컬럼 (항목, 우선순위) 또는 3컬럼 (ID, 항목, 우선순위)
                if len(cells) == 2:
                    desc, priority = cells[0], cells[1]
                else:
                    desc, priority = cells[-2], cells[-1]
                score = SCORE_MAP.get(priority, 40)
                items.append({
                    "score": score,
                    "source": "plan",
                    "sp": sp,
                    "desc": desc[:60],
                    "priority": priority,
                })

    # "기술 부채" 섹션에서 추출
    debt_match = re.search(
        r"##\s*\d+\.\s*기술 부채.*?\n\|.*?\n\|[-\s|]+\n((?:\|.*\n)*)",
        content, re.IGNORECASE
    )
    if debt_match:
        rows = debt_match.group(1).strip().split("\n")
        for row in rows:
            cells = [c.strip() for c in row.split("|") if c.strip()]
            if len(cells) >= 3:
                debt_id = cells[0]
                desc = cells[1]
                priority = cells[2] if len(cells) >= 3 else "P2"
                score = SCORE_MAP.get(priority, 35)
                items.append({
                    "score": score,
                    "source": "plan/부채",
                    "sp": sp,
                    "desc": f"{debt_id}: {desc[:55]}",
                    "priority": priority,
                })

    # "마일스톤" 섹션에서 미완료 항목 추출
    milestone_match = re.search(
        r"##\s*\d+\.\s*마일스톤.*?\n\|.*?\n\|[-\s|]+\n((?:\|.*\n)*)",
        content, re.IGNORECASE
    )
    if milestone_match:
        rows = milestone_match.group(1).strip().split("\n")
        for row in rows:
            cells = [c.strip() for c in row.split("|") if c.strip()]
            if len(cells) >= 3:
                m_id = cells[0]
                desc = cells[1]
                status = cells[2]
                if "완료" not in status and "Done" not in status:
                    items.append({
                        "score": 45,
                        "source": "plan/마일스톤",
                        "sp": sp,
                        "desc": f"{m_id}: {desc[:55]}",
                        "priority": "예정",
                    })

    return items


def extract_prd_unimplemented(content: str, sp: str) -> list:
    """PRD에서 미구현 항목 추출 (상태 컬럼이 있는 테이블만 대상)."""
    items = []
    # 상태 컬럼을 가진 테이블에서 "예정/미구현/TODO/계획중/진행중" 상태인 행만 추출
    # 헤더에 "상태" 컬럼이 있는 테이블 블록 찾기
    table_pattern = re.compile(
        r"(\|[^\n]*상태[^\n]*\|)\n(\|[-\s|]+\|)\n((?:\|[^\n]+\|\n)*)",
        re.IGNORECASE
    )
    for table_match in table_pattern.finditer(content):
        header = table_match.group(1)
        header_cells = [c.strip() for c in header.split("|") if c.strip()]
        # 상태 컬럼 인덱스 찾기
        status_idx = None
        for idx, cell in enumerate(header_cells):
            if "상태" in cell:
                status_idx = idx
                break
        if status_idx is None:
            continue

        rows = table_match.group(3).strip().split("\n")
        for row in rows:
            cells = [c.strip() for c in row.split("|") if c.strip()]
            if len(cells) <= status_idx:
                continue
            status = cells[status_idx]
            if re.search(r"예정|미구현|TODO|계획중|진행중", status, re.IGNORECASE):
                # 설명: 상태 컬럼 제외한 첫 번째~두 번째 컬럼
                desc_parts = [c for i, c in enumerate(cells) if i != status_idx]
                desc = " ".join(desc_parts[:2])[:60]
                items.append({
                    "score": 25,
                    "source": "prd",
                    "sp": sp,
                    "desc": desc,
                    "priority": status,
                })
    return items


def analyze_sp(sp: str, sources: list) -> list:
    """특정 SP의 문서를 분석하여 작업 항목을 추출.

    우선순위:
    1. `todo/` 폴더 존재 시 → 폴더 스캔 (각 {ID}.md 헤더에서 메타 추출)
    2. 인덱스 ### 헤더 형식 → 폴백
    """
    all_items = []

    if "todo" in sources or "all" in sources:
        folder_items = extract_todos_from_folder(sp)
        if folder_items:
            all_items.extend(folder_items)
        else:
            todo_content = read_file_safe(doc_path(sp, "todo"))
            if todo_content:
                all_items.extend(extract_todo_items(todo_content, sp))

    if "plan" in sources or "all" in sources:
        plan_content = read_file_safe(doc_path(sp, "plan"))
        if plan_content:
            all_items.extend(extract_plan_items(plan_content, sp))

    if "prd" in sources or "all" in sources:
        prd_content = read_file_safe(doc_path(sp, "prd"))
        if prd_content:
            all_items.extend(extract_prd_unimplemented(prd_content, sp))

    return all_items


def print_results(items: list, top_n: int, current_sp: str, analyzed_sps: list):
    """추천 결과 출력."""
    # 점수 내림차순 정렬
    items.sort(key=lambda x: x["score"], reverse=True)

    # 상위 N개 선택
    display_items = items[:top_n] if top_n > 0 else items

    sp_label = f"SP{int(current_sp):02d}" if current_sp != "00" else "SP00 (공통)"
    analyzed_label = ", ".join(f"SP{s}" for s in analyzed_sps)

    print(f"# ccnext - 다음 작업 추천\n")
    print(f"현재 컨텍스트: **{sp_label}**")
    print(f"분석 대상: {analyzed_label}")
    print(f"분석 시각: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    if not display_items:
        print("## 결과\n")
        print("추천할 작업이 없습니다. 모든 항목이 완료된 상태입니다.\n")
        return

    print(f"## 추천 작업 (상위 {len(display_items)}개)\n")
    print("| 순위 | 점수 | 출처 | SP | 내용 |")
    print("|:----:|:----:|------|:--:|------|")
    for i, item in enumerate(display_items, 1):
        print(f"| {i} | {item['score']} | {item['source']} | {item['sp']} | {item['desc']} |")
    print()

    # 요약 통계
    issue_items = [x for x in items if x["source"] == "todo/이슈"]
    custom_items = [x for x in items if x["source"] == "todo/커스텀"]
    plan_items = [x for x in items if x["source"].startswith("plan")]
    prd_items = [x for x in items if x["source"] == "prd"]

    critical = sum(1 for x in issue_items if x["priority"] == "CRITICAL")
    error = sum(1 for x in issue_items if x["priority"] == "ERROR")
    warning = sum(1 for x in issue_items if x["priority"] == "WARNING")

    print("## 요약\n")
    print(f"- 활성 이슈: {len(issue_items)}건 (CRITICAL: {critical}, ERROR: {error}, WARNING: {warning})")
    print(f"- 대기 Todo: {len(custom_items)}건")
    print(f"- 계획 항목: {len(plan_items)}건")
    print(f"- PRD 미구현: {len(prd_items)}건")
    print(f"- **전체: {len(items)}건**")

    if display_items:
        top = display_items[0]
        print(f"\n> **권장**: {top['desc']}")


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
    parser = argparse.ArgumentParser(description="ccnext - 다음 작업 우선순위 추천")
    parser.add_argument("command", nargs="?", default="run", help="서브명령어")
    parser.add_argument("--sp", type=str, default=None, help="특정 SP만 분석")
    parser.add_argument("--all-sps", action="store_true", help="전체 SP를 분석")
    parser.add_argument("--top", type=int, default=5, help="상위 N개 표시")
    parser.add_argument("--all", action="store_true", help="모든 항목 표시")
    parser.add_argument("--source", type=str, default="all",
                        choices=["all", "todo", "plan", "prd"],
                        help="특정 출처만 분석")
    args = parser.parse_args()

    # help 서브명령어
    if args.command == "help":
        _print_skill_help("ccnext")
        return

    if args.command == "version":
        print("ccnext v01")
        return

    if args.command == "status":
        show_help_if_no_args("ccnext", [])
        return

    # run 실행
    current_sp = get_current_sp()
    target_sps = resolve_target_sps(current_sp, args)

    sources = [args.source] if args.source != "all" else ["all"]
    top_n = 0 if args.all else args.top

    # 전체 SP 분석
    all_items = []
    for sp in target_sps:
        all_items.extend(analyze_sp(sp, sources))

    print_results(all_items, top_n, current_sp, target_sps)


if __name__ == "__main__":
    main()
