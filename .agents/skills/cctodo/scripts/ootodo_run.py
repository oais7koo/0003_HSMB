#!/usr/bin/env python3
"""ootodo_run.py — Todo 자동 처리 스킬

Todo 형식 (섹션 기반):
    ## 대기 ToDo

    ### C001 [SP명] 제목
    #### 등록일: YYYY-MM-DD | 우선순위: medium
    #### ToDo 내용
    본문 내용 (선택)

    ## 완료 ToDo

    ### C000 이전 완료 항목
    #### 등록일: YYYY-MM-DD | 우선순위: medium
    #### ToDo 내용
    본문 내용
    #### 완료일: YYYY-MM-DD
    #### 완료 내용
    완료 시 한 작업 설명

Usage:
    cctodo "내용"          # 추가 + 즉시 처리
    cctodo                 # 대기 중 전체 처리
    cctodo list            # 전체 SP 대기 업무 조회
    cctodo status          # 상태 조회
    cctodo add [text]      # 추가만 (처리 안함)
    cctodo clear           # 완료된 Todo → d0010 아카이브
"""
import sys
import re
from pathlib import Path
from datetime import datetime

# --- oo_common inline ---
import re as _re

_SKILLS_DIR = Path(__file__).parent.parent.parent


def _print_skill_help(skill_name):
    if sys.stdout.encoding and sys.stdout.encoding.lower() in ("cp949", "cp1252", "ascii"):
        sys.stdout.reconfigure(encoding="utf-8")
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


# --- end oo_common inline ---

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path.cwd()
DEFAULT_TODO_FILE = "d0004_todo.md"


# ============================================================
# Path Helpers
# ============================================================


def get_sp_doc_dir(sp: str = "00") -> Path:
    sp_folder = f"sp{int(sp):02d}"
    sp_path = PROJECT_ROOT / "00_doc" / sp_folder
    if sp_path.exists():
        return sp_path
    return PROJECT_ROOT / "00_doc"


def get_todo_file(sp: str = "00") -> Path:
    doc_dir = get_sp_doc_dir(sp)
    if sp == "00":
        return doc_dir / DEFAULT_TODO_FILE
    doc_num = int(sp) * 10000 + 4
    return doc_dir / f"d{doc_num}_todo.md"


def get_history_file(sp: str = "00") -> Path:
    doc_dir = get_sp_doc_dir(sp)
    if sp == "00":
        return doc_dir / "d0010_history.md"
    doc_num = int(sp) * 10000 + 10
    return doc_dir / f"d{doc_num}_history.md"


def get_todo_dir(sp: str = "00") -> Path:
    """ToDo 상세 폴더 경로 반환 (00_doc/sp{NN}/todo/). 존재 여부와 무관하게 경로 반환."""
    return get_sp_doc_dir(sp) / "todo"


def get_todo_detail_file(sp: str, todo_id: str) -> Path:
    """ToDo ID에 대응하는 상세 파일 경로 (todo/{ID}.md)."""
    return get_todo_dir(sp) / f"{todo_id}.md"


def create_todo_detail_file(sp: str, todo_id: str, title: str, priority: str = "medium") -> Path | None:
    """todo/{ID}.md 상세 파일을 _template.md 기반으로 생성.

    이미 파일이 존재하거나 todo 폴더가 없으면 None 반환.
    템플릿 부재 시 최소 헤더만 작성.
    """
    todo_dir = get_todo_dir(sp)
    if not todo_dir.exists():
        return None  # 폴더 미도입 SP는 건너뜀 (인덱스만 사용)

    detail_path = todo_dir / f"{todo_id}.md"
    if detail_path.exists():
        return detail_path  # 이미 존재하면 그대로 반환 (idempotent)

    template_path = todo_dir / "_template.md"
    if template_path.exists():
        body = template_path.read_text(encoding="utf-8")
        # 템플릿의 플레이스홀더 치환
        body = body.replace("{ID}", todo_id, 1)
        body = body.replace("{제목}", title, 1)
        body = body.replace("{HIGH/MED/LOW/WARNING/ERROR/CRITICAL}", priority, 1)
        body = body.replace("{OPEN/IN_PROGRESS/HOLD/DONE}", "OPEN", 1)
        body = body.replace("{YYYY-MM-DD}", get_today(), 1)
    else:
        body = (
            f"# {todo_id} — {title}\n\n"
            f"> 우선순위: {priority} | 상태: OPEN | 등록: {get_today()}\n\n"
            f"## 1. 배경 / 문제\n\n(작성 필요)\n\n"
            f"## 2. 작업 범위\n\n(작성 필요)\n\n"
            f"## 6. 완료 기준 (DoD)\n\n- [ ] (작성 필요)\n"
        )

    detail_path.write_text(body, encoding="utf-8")
    return detail_path


def mark_todo_detail_done(sp: str, todo_id: str, commit_hash: str = "") -> bool:
    """todo/{ID}.md 헤더의 `상태: OPEN/IN_PROGRESS` 표기를 DONE으로 갱신.

    파일 없거나 헤더 패턴 미일치 시 False 반환.
    """
    detail_path = get_todo_detail_file(sp, todo_id)
    if not detail_path.exists():
        return False

    content = detail_path.read_text(encoding="utf-8")
    today = get_today()
    commit_part = f" | 완료 커밋: {commit_hash}" if commit_hash else ""

    # 헤더 패턴: `> 우선순위: ... | 상태: ... | 등록: YYYY-MM-DD` (등록일 이후 기존 완료 표기는 group 4로 캡쳐 후 폐기 → 중복 방지)
    pattern = re.compile(
        r"^(>\s*우선순위:\s*[^|]+\|\s*상태:\s*)([^|]+?)(\s*\|\s*등록:\s*\d{4}-\d{2}-\d{2})[^\n]*$",
        re.MULTILINE,
    )
    new_content, n = pattern.subn(
        lambda m: f"{m.group(1)}DONE{m.group(3)} | 완료일: {today}{commit_part}",
        content,
        count=1,
    )
    if n == 0:
        return False

    detail_path.write_text(new_content, encoding="utf-8")
    return True


def get_today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


# ============================================================
# Parsing — 섹션 기반 커스텀 Todo
# ============================================================


def find_last_custom_id(content: str) -> int:
    r"""### C\d+ 헤딩에서 마지막 번호 반환 (없으면 0)."""
    matches = re.findall(r"^### C(\d+)\b", content, re.MULTILINE)
    if matches:
        return max(int(m) for m in matches)
    return 0


def _get_section_content(content: str, header: str) -> str:
    """## 헤더 섹션 내용 추출 (다음 ## 또는 EOF까지)."""
    escaped = re.escape(header)
    m = re.search(
        rf"^{escaped}[ \t]*\n(.*?)(?=^## |\Z)",
        content,
        re.DOTALL | re.MULTILINE,
    )
    return m.group(1) if m else ""


def _parse_section_blocks(section_text: str) -> list[dict]:
    """섹션 내 ### C/T 블록들을 파싱하여 dict 목록 반환."""
    todos: list[dict] = []
    splits = list(re.finditer(r"^### (.+)$", section_text, re.MULTILINE))

    for i, match in enumerate(splits):
        heading = match.group(1).strip()
        block_start = match.end()
        block_end = splits[i + 1].start() if i + 1 < len(splits) else len(section_text)
        block_body = section_text[block_start:block_end]

        # ID + 제목: "C008 [ooprd] 제목" or "T010 제목"
        id_m = re.match(r"([CT]\d+)\s*(.*)", heading)
        if not id_m:
            continue
        todo_id = id_m.group(1)
        title = id_m.group(2).strip()

        # 메타/내용 파싱 (#### 섹션 기반)
        meta_line = ""
        body = ""
        done_date_str = ""
        done_body = ""

        # #### 섹션 분리
        h4_splits = list(re.finditer(r"^#### (.+)$", block_body, re.MULTILINE))
        if h4_splits:
            for j, h4 in enumerate(h4_splits):
                h4_title = h4.group(1).strip()
                h4_end = h4_splits[j + 1].start() if j + 1 < len(h4_splits) else len(block_body)
                h4_body = block_body[h4.end():h4_end].strip()
                if "등록일:" in h4_title:
                    meta_line = h4_title
                elif h4_title == "ToDo 내용":
                    body = h4_body
                elif h4_title.startswith("완료일:"):
                    done_date_str = h4_title.replace("완료일:", "").strip()
                elif h4_title == "완료 내용":
                    done_body = h4_body
        else:
            # 레거시 형식 (#### 없는 구버전)
            lines = block_body.split("\n")
            for idx, line in enumerate(lines):
                if "등록일:" in line:
                    meta_line = line.strip()
                    body = "\n".join(lines[idx + 1:]).strip()
                    break

        date_m = re.search(r"등록일:\s*(\d{4}-\d{2}-\d{2})", meta_line)
        prio_m = re.search(r"우선순위:\s*(\w+)", meta_line)
        done_m = re.search(r"완료:\s*(\d{4}-\d{2}-\d{2})", meta_line)
        done_date = done_date_str or (done_m.group(1) if done_m else "")

        todos.append({
            "id": todo_id,
            "title": title,
            "content": title,  # backward compat
            "date": date_m.group(1) if date_m else "",
            "priority": prio_m.group(1) if prio_m else "medium",
            "done_date": done_m.group(1) if done_m else "",
            "body": body,
            "note": "-",  # backward compat
        })

    return todos


def parse_waiting_todos(content: str) -> list[dict]:
    """## 대기 ToDo 섹션의 ### 블록 파싱."""
    section = _get_section_content(content, "## 대기 ToDo")
    return _parse_section_blocks(section)


def parse_completed_todos(content: str) -> list[dict]:
    """## 완료 ToDo 섹션의 ### 블록 파싱."""
    section = _get_section_content(content, "## 완료 ToDo")
    return _parse_section_blocks(section)


def parse_debug_issues(content: str) -> list[dict]:
    """(레거시) 해결된 이슈 테이블 파싱 — 이전 형식 호환용."""
    return []


def clear_debug_issues(content: str) -> str:
    """(레거시) 이전 디버깅 섹션 정리 — 현재 형식에서는 no-op."""
    return content


def parse_pending_issue_items(content: str) -> list[dict]:
    """## 대기 ToDo 섹션의 T/A/S/W 접두사 이슈 블록 파싱."""
    items = []
    section = _get_section_content(content, "## 대기 ToDo")
    splits = list(re.finditer(r"^### (.+)$", section, re.MULTILINE))

    for i, match in enumerate(splits):
        heading = match.group(1).strip()
        block_start = match.end()
        block_end = splits[i + 1].start() if i + 1 < len(splits) else len(section)
        block_body = section[block_start:block_end]

        id_m = re.match(r"([TASWD]\d+)\s*(.*)", heading)
        if not id_m:
            continue
        issue_id = id_m.group(1)
        title = id_m.group(2).strip()

        meta_line = ""
        for line in block_body.split("\n"):
            if "등록일:" in line:
                meta_line = line.strip()
                break

        prio_m = re.search(r"우선순위:\s*(\w+)", meta_line)
        priority = prio_m.group(1).upper() if prio_m else "ERROR"

        items.append({
            "id": issue_id,
            "priority": priority,
            "content": title,
        })

    return items


def summarize_content(text: str, limit: int = 50) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[:limit - 3] + "..."


def _priority_rank(value: str) -> int:
    order = {
        "CRITICAL": 0, "HIGH": 0, "MUST": 0,
        "ERROR": 1,
        "WARNING": 2,
        "MEDIUM": 3, "SHOULD": 3,
        "INFO": 4,
        "LOW": 5, "COULD": 5,
        "CUSTOM": 6,
    }
    return order.get(value.upper(), 9)


# ============================================================
# Content Manipulation
# ============================================================


def add_todo_to_waiting(
    content: str, text: str, priority: str = "medium", note: str = "-"
) -> tuple[str, str]:
    """## 대기 ToDo 섹션에 새 ### C{N} 블록 삽입."""
    last_id = find_last_custom_id(content)
    new_id = f"C{last_id + 1:03d}"
    today = get_today()

    new_block = (
        f"### {new_id} {text}\n"
        f"#### 등록일: {today} | 우선순위: {priority}\n"
        f"#### ToDo 내용\n"
    )

    section_match = re.search(r"^## 대기 ToDo[ \t]*\n", content, re.MULTILINE)
    if section_match:
        pos = section_match.end()
        # 선행 빈 줄 건너뛰기
        while pos < len(content) and content[pos] == '\n':
            pos += 1
        # 설명 줄(> ...) 건너뛰기
        desc_m = re.match(r"(?:>.*\n)+", content[pos:])
        if desc_m:
            pos += len(desc_m.group(0))
        # 기존 placeholder 제거
        rest = re.sub(r"\(항목 없음\)\n?", "", content[pos:], count=1)
        new_content = content[:pos] + "\n" + new_block + "\n" + rest.lstrip('\n')
    else:
        new_section = (
            f"\n## 대기 ToDo\n\n"
            f"> `cctodo add` 명령으로 추가된 항목.\n\n"
            f"{new_block}"
        )
        new_content = content.rstrip() + "\n" + new_section

    return new_content, new_id


def move_todo_to_completed(content: str, todo_id: str) -> str:
    """todo_id 블록을 ## 대기 ToDo → ## 완료 ToDo로 이동."""
    today = get_today()

    # 블록 시작 찾기
    start_pat = re.compile(rf"^### {re.escape(todo_id)}\b", re.MULTILINE)
    start_m = start_pat.search(content)
    if not start_m:
        return content

    block_start = start_m.start()

    # 블록 끝 찾기 (다음 ### 또는 ## 헤딩, 또는 EOF)
    end_pat = re.compile(r"^(?:### |## )", re.MULTILINE)
    end_m = end_pat.search(content, start_m.end())
    block_end = end_m.start() if end_m else len(content)

    original_block = content[block_start:block_end]

    # 완료 섹션 추가 (이미 완료일이 있으면 스킵)
    if "#### 완료일:" not in original_block:
        # #### 형식: 블록 끝에 완료일/완료 내용 섹션 추가
        updated_block = original_block.rstrip() + f"\n#### 완료일: {today}\n#### 완료 내용\n"
    else:
        updated_block = original_block

    # 원본 제거
    new_content = content[:block_start] + content[block_end:]

    # ## 완료 ToDo 섹션에 추가
    completed_m = re.search(r"^## 완료 ToDo[ \t]*\n", new_content, re.MULTILINE)
    if completed_m:
        insert_pos = completed_m.end()
        new_content = new_content[:insert_pos] + updated_block + new_content[insert_pos:]
    else:
        # 섹션 없으면 ## 대기 ToDo 다음 ## 섹션 앞에 생성
        waiting_m = re.search(r"^## 대기 ToDo", new_content, re.MULTILINE)
        after = waiting_m.end() if waiting_m else 0
        next_h2 = re.search(r"^## ", new_content[after:], re.MULTILINE)
        if next_h2:
            insert_pos = after + next_h2.start()
        else:
            insert_pos = len(new_content)
        new_content = (
            new_content[:insert_pos].rstrip()
            + f"\n\n## 완료 ToDo\n\n{updated_block}"
            + new_content[insert_pos:].lstrip()
        )

    return new_content


def parse_resolved_issues(content: str) -> list[dict]:
    """## 완료 ToDo → clear 시 d0010으로 이동할 목록."""
    todos = parse_completed_todos(content)
    return [
        {
            "id": t["id"],
            "date": t["date"],
            "category": "CUSTOM",
            "content": t["title"],
            "resolved_date": t["done_date"] or get_today(),
            "resolution": "완료",
            "source": "completed_todo",
        }
        for t in todos
    ]


def clear_resolved_issues(content: str) -> str:
    """## 완료 ToDo 섹션 내용을 제거 (섹션 헤더는 유지)."""
    # 섹션 내용(### 블록들)만 제거, 헤더는 유지
    return re.sub(
        r"(^## 완료 ToDo[ \t]*\n).*?(?=^## |\Z)",
        r"\g<1>",
        content,
        flags=re.DOTALL | re.MULTILINE,
    )


def extract_block_raw(content: str, todo_id: str) -> tuple[int, int, str]:
    """content에서 todo_id 블록의 (시작, 끝, 텍스트) 반환."""
    start_pat = re.compile(rf"^### {re.escape(todo_id)}\b", re.MULTILINE)
    start_m = start_pat.search(content)
    if not start_m:
        return -1, -1, ""
    block_start = start_m.start()
    end_pat = re.compile(r"^(?:### |## |---)", re.MULTILINE)
    end_m = end_pat.search(content, start_m.end())
    block_end = end_m.start() if end_m else len(content)
    return block_start, block_end, content[block_start:block_end]


def strip_completion_from_block(block_text: str) -> str:
    """블록에서 #### 완료일: 및 #### 완료 내용 섹션 제거."""
    m = re.search(r"\n#### 완료일:", block_text)
    if m:
        return block_text[:m.start()].rstrip() + "\n"
    return block_text


def move_completed_to_waiting(content: str, todo_id: str, note: str = "") -> str:
    """완료 ToDo 블록을 대기 ToDo로 복원 + 재개 메모 추가."""
    today = get_today()
    start, end, block_text = extract_block_raw(content, todo_id)
    if start == -1:
        return content

    restored = strip_completion_from_block(block_text)
    if note:
        restored = restored.rstrip() + f"\n#### 재개 메모: {today} — {note}\n"

    new_content = content[:start] + content[end:]

    waiting_m = re.search(r"^## 대기 ToDo[ \t]*\n", new_content, re.MULTILINE)
    if waiting_m:
        pos = waiting_m.end()
        while pos < len(new_content) and new_content[pos] == "\n":
            pos += 1
        desc_m = re.match(r"(?:>.*\n)+", new_content[pos:])
        if desc_m:
            pos += len(desc_m.group(0))
        new_content = new_content[:pos] + "\n" + restored + "\n" + new_content[pos:]
    return new_content


def remove_block_from_content(content: str, todo_id: str) -> str:
    """content에서 todo_id 블록 제거."""
    start, end, _ = extract_block_raw(content, todo_id)
    if start == -1:
        return content
    return content[:start] + content[end:]


def parse_completed_block_for_archive(content: str, todo_id: str) -> dict | None:
    """특정 완료 블록을 아카이브용 dict로 파싱."""
    _, _, block_text = extract_block_raw(content, todo_id)
    if not block_text:
        return None
    title_m = re.match(r"^### (.+)$", block_text, re.MULTILINE)
    title = title_m.group(1).strip() if title_m else todo_id
    done_m = re.search(r"^#### 완료일:\s*(.+)$", block_text, re.MULTILINE)
    done_date = done_m.group(1).strip() if done_m else get_today()
    done_body_m = re.search(r"^#### 완료 내용\n(.*?)(?=^####|\Z)", block_text, re.MULTILINE | re.DOTALL)
    done_body = done_body_m.group(1).strip() if done_body_m else ""
    return {
        "id": todo_id,
        "title": title,
        "content": title,
        "date": get_today(),
        "done_date": done_date,
        "done_body": done_body,
        "category": "CUSTOM",
        "source": "ootodo_audit",
    }


def add_single_to_history(history_content: str, todo: dict, sp: str = "00") -> str:
    """단일 완료 항목을 d0010에 추가."""
    today = get_today()
    max_num = max(
        (int(m.group(1)) for m in re.finditer(r"^###\s+(\d+)\.", history_content, re.MULTILINE)),
        default=0,
    )
    next_num = max_num + 1
    done_body_section = ""
    if todo.get("done_body"):
        done_body_section = f"\n#### {next_num}.2. 완료 내용\n\n{todo['done_body']}\n"
    new_entry = (
        f"## {today}\n\n"
        f"### {next_num}. [DONE] {todo['id']} — {todo['title']}\n\n"
        f"#### {next_num}.1. 작업 내용\n\n"
        f"- __상태__: [DONE]\n"
        f"- __완료일__: {todo.get('done_date', today)}\n"
        f"- __작업 유형__: CUSTOM (cctodo audit)\n"
        f"{done_body_section}\n"
        f"---\n\n"
    )
    m = re.search(r"^## ", history_content, re.MULTILINE)
    if m:
        return history_content[:m.start()] + new_entry + history_content[m.start():]
    return history_content.rstrip("\n") + "\n\n" + new_entry


def add_to_history_archive(content: str, issues: list[dict], sp: str = "00") -> str:
    """완료 이슈를 d0010_history.md에 날짜 기반 엔트리로 추가."""
    if not issues:
        return content

    today = get_today()
    max_num = max(
        (int(m.group(1)) for m in re.finditer(r"^###\s+(\d+)\.", content, re.MULTILINE)),
        default=0,
    )
    next_num = max_num + 1

    item_rows = "\n".join(
        f"| {i['id']} | {i.get('date', today)} | {i['content']} |"
        for i in issues
    )

    new_entry = (
        f"## {today}\n\n"
        f"### {next_num}. [ARCHIVE] cctodo clear — SP{sp} 완료 항목 아카이브\n\n"
        f"#### {next_num}.1. 작업 내용\n\n"
        f"- __상태__: [DONE]\n"
        f"- __완료일__: {today}\n"
        f"- __작업 유형__: ARCHIVE (cctodo clear)\n\n"
        f"#### {next_num}.2. 아카이브 항목\n\n"
        f"| ID | 날짜 | 내용 |\n"
        f"| :--- | :--- | :--- |\n"
        f"{item_rows}\n\n"
        f"---\n\n"
    )

    date_header = f"\n## {today}\n"
    if date_header in content:
        entry_body = "\n".join(new_entry.split("\n")[2:])
        idx = content.index(date_header) + len(date_header)
        while idx < len(content) and content[idx] == "\n":
            idx += 1
        return content[:idx] + entry_body + content[idx:]

    m = re.search(r"^## ", content, re.MULTILINE)
    if m:
        return content[:m.start()] + new_entry + content[m.start():]

    return content.rstrip("\n") + "\n\n" + new_entry


# ============================================================
# Skill Routing
# ============================================================


def get_processing_skill(tag: str, content: str) -> str:
    tag = tag.upper().strip()
    content_lower = content.lower()

    tag_map = {
        "FEATURE": "oodev", "BUGFIX": "oofix", "HOTFIX": "oofix",
        "DOCS": "ooprd", "UPDATE": "ooenv", "CONFIG": "ooenv",
        "PPT": "ooppt", "PAPER": "ooreport", "IMPROVE": "oodev",
        "REFACTOR": "oodev", "TEST": "ootest",
    }
    if tag in tag_map:
        return tag_map[tag]

    if "문서" in content_lower or "doc" in content_lower:
        return "ooprd"
    if "에러" in content_lower or "fix" in content_lower or "수정" in content_lower:
        return "oofix"
    if "테스트" in content_lower or "test" in content_lower:
        return "ootest"
    if "ppt" in content_lower or "발표" in content_lower:
        return "ooppt"
    if "논문" in content_lower or "paper" in content_lower:
        return "ooreport"
    if "설정" in content_lower or "config" in content_lower:
        return "ooenv"
    return "oodev"


# ============================================================
# Commands
# ============================================================


def cmd_list(sp: str | None = None):
    todo_files: list[tuple[str, Path]] = []

    if sp and sp != "00":
        f = get_todo_file(sp)
        if f.exists():
            todo_files.append((f"SP{int(sp):02d}", f))
    elif sp == "00":
        f = get_todo_file("00")
        if f.exists():
            todo_files.append(("SP00", f))
    else:
        for f in sorted((PROJECT_ROOT / "00_doc").glob("sp*/d*0004_todo.md")):
            m = re.search(r"sp(\d{2})", str(f.parent).lower())
            if m:
                todo_files.append((f"SP{m.group(1)}", f))

    rows = []
    counts: dict[str, int] = {}

    for sp_name, todo_file in todo_files:
        c = todo_file.read_text(encoding="utf-8")
        for todo in parse_waiting_todos(c):
            rows.append({"sp": sp_name, "id": todo["id"], "priority": todo["priority"], "content": todo["content"]})
        for issue in parse_pending_issue_items(c):
            rows.append({"sp": sp_name, "id": issue["id"], "priority": issue["priority"], "content": issue["content"]})

    rows.sort(key=lambda r: (_priority_rank(r["priority"]), r["sp"], r["id"]))
    for row in rows:
        counts[row["sp"]] = counts.get(row["sp"], 0) + 1

    print("# cctodo list - 전체 대기 업무\n")
    if not rows:
        print("(대기 중인 항목 없음)")
        return

    print("| SP | ID | 우선순위 | 내용 |")
    print("|:--:|----|:--------:|------|")
    for row in rows:
        print(f"| {row['sp']} | {row['id']} | {row['priority']} | {summarize_content(row['content'])} |")

    summary = ", ".join(f"{s}: {c}건" for s, c in sorted(counts.items()))
    print(f"\n총 {len(rows)}건 대기 중 ({summary})")


def cmd_status(sp: str = "00"):
    todo_file = get_todo_file(sp)
    if not todo_file.exists():
        print(f"오류: {todo_file} 파일이 존재하지 않습니다.")
        return

    content = todo_file.read_text(encoding="utf-8")
    todos = parse_waiting_todos(content)

    print("# cctodo status - 대기 중인 Todo 목록\n")
    if not todos:
        print("(대기 중인 항목 없음)")
        return

    for todo in todos:
        print(f"### {todo['id']} {todo['title']}")
        print(f"등록일: {todo['date']} | 우선순위: {todo['priority']}")
        if todo["body"]:
            body_preview = todo["body"][:100]
            if len(todo["body"]) > 100:
                body_preview += "..."
            print(f"\n{body_preview}")
        print()

    print(f"총 {len(todos)}개 항목")

    high = [t for t in todos if t["priority"].lower() in ("high", "critical")]
    if high:
        print("\n## 처리 권장 (high 이상)")
        for t in high:
            skill = get_processing_skill("", t["content"])
            print(f"- [{t['id']}] {t['content']} → {skill} run")


def cmd_add(text: str, priority: str = "medium", note: str = "-", sp: str = "00"):
    todo_file = get_todo_file(sp)
    if not todo_file.exists():
        print(f"오류: {todo_file} 파일이 존재하지 않습니다.")
        return

    content = todo_file.read_text(encoding="utf-8")
    new_content, new_id = add_todo_to_waiting(content, text, priority, note)
    todo_file.write_text(new_content, encoding="utf-8")

    # todo/ 폴더가 존재하면 상세 파일 자동 생성 (idempotent)
    detail_path = create_todo_detail_file(sp, new_id, text, priority)

    print("# cctodo add - Todo 추가 완료\n")
    print(f"[OK] {new_id} 추가됨\n")
    print(f"### {new_id} {text}")
    print(f"등록일: {get_today()} | 우선순위: {priority}")
    print(f"\n인덱스: {todo_file.relative_to(PROJECT_ROOT)}")
    if detail_path is not None:
        print(f"상세  : {detail_path.relative_to(PROJECT_ROOT)} (편집 권장)")


def cmd_add_and_run(text: str, priority: str = "medium", note: str = "-", sp: str = "00"):
    todo_file = get_todo_file(sp)
    if not todo_file.exists():
        print(f"오류: {todo_file} 파일이 존재하지 않습니다.")
        return

    content = todo_file.read_text(encoding="utf-8")
    new_content, new_id = add_todo_to_waiting(content, text, priority, note)
    todo_file.write_text(new_content, encoding="utf-8")

    print("# cctodo - Todo 추가 및 즉시 처리\n")
    print("## 1. 추가 완료\n")
    print(f"[OK] {new_id} 추가됨\n")
    print(f"### {new_id} {text}")
    print(f"등록일: {get_today()} | 우선순위: {priority}")

    tag = "MISC"
    m = re.match(r"^\[([A-Z]+)\]", text)
    if m:
        tag = m.group(1)
    skill = get_processing_skill(tag, text)

    print("\n## 2. 즉시 처리\n")
    print(">>> 다음 업무를 처리하세요:")
    print(f"    내용: {text}")
    print(f"    권장 실행: {skill} run")
    print(f"\n    완료 후 해당 항목을 '## 완료 ToDo' 섹션으로 이동하세요.")
    print(f"    - 항목 ID: {new_id}")
    print(f"    - 파일: {todo_file.relative_to(PROJECT_ROOT)}")


def cmd_clear(sp: str = "00", dry_run: bool = False):
    todo_file = get_todo_file(sp)
    history_file = get_history_file(sp)

    if not todo_file.exists():
        print(f"오류: {todo_file} 파일이 존재하지 않습니다.")
        return
    if not history_file.exists():
        print(f"오류: {history_file} 파일이 존재하지 않습니다.")
        return

    todo_content = todo_file.read_text(encoding="utf-8")
    issues = parse_resolved_issues(todo_content)

    print("# cctodo clear - 완료 항목 아카이브\n")
    if not issues:
        print("[OK] 아카이브할 완료된 Todo가 없습니다.")
        return

    print(f"## 아카이브 대상: {len(issues)}개 항목\n")
    for issue in issues:
        print(f"- {issue['id']}: {summarize_content(issue['content'])}")

    if dry_run:
        print("\n[DRY-RUN] 실제 이동은 수행하지 않습니다.")
        return

    history_content = history_file.read_text(encoding="utf-8")
    new_history = add_to_history_archive(history_content, issues, sp)
    new_todo = clear_resolved_issues(todo_content)

    history_file.write_text(new_history, encoding="utf-8")
    todo_file.write_text(new_todo, encoding="utf-8")

    print("\n## 완료\n")
    print(f"- {len(issues)}개 항목 아카이브 완료")
    print(f"- 소스: {todo_file.relative_to(PROJECT_ROOT)}")
    print(f"- 대상: {history_file.relative_to(PROJECT_ROOT)}")


def cmd_audit(sp: str = "00"):
    """완료 ToDo를 하나씩 검증 지침과 함께 출력."""
    todo_file = get_todo_file(sp)
    if not todo_file.exists():
        print(f"[ERROR] 파일 없음: {todo_file}")
        return

    content = todo_file.read_text(encoding="utf-8")
    section = _get_section_content(content, "## 완료 ToDo")
    splits = list(re.finditer(r"^### (.+)$", section, re.MULTILINE))

    if not splits:
        print("# cctodo audit\n\n검증할 완료 항목이 없습니다.")
        return

    print(f"# cctodo audit — 완료 항목 검증\n")
    print(f"SP{int(sp):02d} 완료 ToDo {len(splits)}개 항목을 순서대로 검증하세요.\n")
    print(f"---\n")

    for i, m in enumerate(splits, 1):
        heading = m.group(1).strip()
        block_start = m.end()
        block_end = splits[i].start() if i < len(splits) else len(section)
        block_body = section[block_start:block_end]

        id_m = re.match(r"(\S+)\s*(.*)", heading)
        todo_id = id_m.group(1) if id_m else f"#{i}"
        title_rest = id_m.group(2).strip() if id_m else heading

        todo_body_m = re.search(r"^#### ToDo 내용\n(.*?)(?=^####|\Z)", block_body, re.MULTILINE | re.DOTALL)
        todo_body = todo_body_m.group(1).strip() if todo_body_m else ""

        done_body_m = re.search(r"^#### 완료 내용\n(.*?)(?=^####|\Z)", block_body, re.MULTILINE | re.DOTALL)
        done_body = done_body_m.group(1).strip() if done_body_m else ""

        print(f"## [{i}/{len(splits)}] {todo_id}: {title_rest}")
        if todo_body:
            print(f"\n**원래 할 일**: {todo_body[:200]}")
        print(f"\n**완료 내용**:")
        print(done_body[:400] if done_body else "(완료 내용 없음)")
        print(f"\n**검증**: 위 완료 내용이 실제 코드/파일에 반영되어 있는지 확인하세요.")
        print(f"\n**판정 후 실행**:")
        print(f"```")
        print(f"# OK  → cctodo history {todo_id} --sp {sp}")
        print(f"# FAIL→ cctodo reopen {todo_id} \"실패 이유\" --sp {sp}")
        print(f"```\n")
        print(f"---\n")


def cmd_reopen(todo_id: str, note: str = "", sp: str = "00"):
    """완료 항목을 대기로 복원 + 재개 메모 추가."""
    todo_file = get_todo_file(sp)
    if not todo_file.exists():
        print(f"[ERROR] 파일 없음: {todo_file}")
        return

    content = todo_file.read_text(encoding="utf-8")
    _, _, block_text = extract_block_raw(content, todo_id)
    if not block_text:
        print(f"[ERROR] {todo_id} 항목을 찾을 수 없습니다.")
        return

    new_content = move_completed_to_waiting(content, todo_id, note)
    todo_file.write_text(new_content, encoding="utf-8")

    print(f"# cctodo reopen\n")
    print(f"[OK] {todo_id} → 대기 ToDo로 복원됨")
    if note:
        print(f"재개 메모: {note}")
    print(f"파일: {todo_file.relative_to(PROJECT_ROOT)}")


def cmd_history_one(todo_id: str, sp: str = "00"):
    """특정 완료 항목을 d0010에 아카이브하고 todo에서 제거."""
    todo_file = get_todo_file(sp)
    history_file = get_history_file(sp)

    if not todo_file.exists():
        print(f"[ERROR] 파일 없음: {todo_file}")
        return
    if not history_file.exists():
        print(f"[ERROR] history 파일 없음: {history_file}")
        return

    todo_content = todo_file.read_text(encoding="utf-8")
    todo_data = parse_completed_block_for_archive(todo_content, todo_id)
    if not todo_data:
        print(f"[ERROR] {todo_id} 항목을 찾을 수 없습니다.")
        return

    history_content = history_file.read_text(encoding="utf-8")
    new_history = add_single_to_history(history_content, todo_data, sp)
    new_todo = remove_block_from_content(todo_content, todo_id)

    history_file.write_text(new_history, encoding="utf-8")
    todo_file.write_text(new_todo, encoding="utf-8")

    print(f"# cctodo history\n")
    print(f"[OK] {todo_id} → {history_file.name} 아카이브 완료")
    print(f"제목: {todo_data['title'][:80]}")


def _body_without_history(content: str) -> str:
    """문서이력 라인(- vNN YYYY-MM-DD —) 제외한 본문 반환 (diff 기준)."""
    return re.sub(r"^- v\d+ \d{4}-\d{2}-\d{2} —[^\n]*\n", "", content, flags=re.MULTILINE)


def _next_version(content: str) -> str:
    """현재 문서이력의 가장 큰 버전 다음 번호 반환."""
    versions = re.findall(r"^- v(\d+) ", content, flags=re.MULTILINE)
    max_v = max((int(v) for v in versions), default=0)
    return f"v{max_v + 1:02d}"


def _sort_waiting_blocks_by_priority(content: str) -> tuple[str, bool]:
    """## 대기 ToDo 섹션의 ### 블록을 우선순위 순으로 정렬. (new_content, changed)"""
    section_match = re.search(
        r"^## 대기 ToDo[ \t]*\n(.*?)(?=^## |\Z)",
        content,
        re.DOTALL | re.MULTILINE,
    )
    if not section_match:
        return content, False

    section_body = section_match.group(1)
    splits = list(re.finditer(r"^### .+$", section_body, re.MULTILINE))
    if len(splits) <= 1:
        return content, False

    intro = section_body[: splits[0].start()]
    blocks: list[str] = []
    for i, m in enumerate(splits):
        end = splits[i + 1].start() if i + 1 < len(splits) else len(section_body)
        blocks.append(section_body[m.start():end])

    def block_priority(block: str) -> int:
        prio_m = re.search(r"우선순위:\s*(\w+)", block)
        return _priority_rank(prio_m.group(1)) if prio_m else 9

    sorted_blocks = sorted(blocks, key=block_priority)
    if blocks == sorted_blocks:
        return content, False

    new_section = intro + "".join(sorted_blocks)
    new_content = content[:section_match.start(1)] + new_section + content[section_match.end(1):]
    return new_content, True


def cmd_update(sp: str = "00", message: str | None = None, no_sort: bool = False, dry_run: bool = False):
    """todo 문서 현행화: 항목 통계·우선순위 재정렬·문서이력 버전 자동 증가."""
    todo_file = get_todo_file(sp)
    if not todo_file.exists():
        print(f"[ERROR] 파일 없음: {todo_file}")
        return 1

    print(f"# cctodo update (SP{int(sp):02d})\n")
    print(f"대상: {todo_file.relative_to(PROJECT_ROOT)}\n")

    content = todo_file.read_text(encoding="utf-8")
    body_before = _body_without_history(content)

    # 1. 현황 통계
    waiting = parse_waiting_todos(content)
    completed = parse_completed_todos(content)
    pending_issues = parse_pending_issue_items(content)

    print("## 1. 현황\n")
    print(f"- 대기 ToDo (C-블록): {len(waiting)}개")
    print(f"- 대기 이슈 (T/A/S/W/D-블록): {len(pending_issues)}개")
    print(f"- 완료 ToDo: {len(completed)}개")
    if completed:
        print(f"\n→ 완료 항목 검증: `cctodo audit --sp {sp}`")
        print(f"→ 무효 항목 복원: `cctodo reopen [ID] \"메모\" --sp {sp}`")
        print(f"→ 검증 후 아카이브: `cctodo history [ID] --sp {sp}` 또는 `cctodo clear --sp {sp}`")
    print()

    updated_content = content

    # 2. 우선순위 재정렬
    print("## 2. 우선순위 재정렬\n")
    if no_sort:
        print("[SKIP] --no-sort 옵션으로 정렬 생략")
    else:
        sorted_content, changed = _sort_waiting_blocks_by_priority(updated_content)
        if changed:
            print("[OK] 대기 ToDo 블록을 우선순위 순으로 재정렬 (CRITICAL → HIGH → ERROR → ... → LOW)")
            updated_content = sorted_content
        else:
            print("[INFO] 이미 정렬된 상태 — 변경 없음")
    print()

    # 3. 변경 감지 + 문서이력 갱신
    body_after = _body_without_history(updated_content)
    print("## 3. 결과\n")

    if body_before == body_after:
        print("[INFO] 변경된 내용이 없습니다. 버전을 올리지 않습니다.")
        return 0

    today = get_today()
    new_version = _next_version(updated_content)
    msg = message or "todo 문서 현행화 (cctodo update)"
    new_history_line = f"- {new_version} {today} — {msg}\n"

    history_match = re.search(r"^## 문서이력관리[ \t]*\n", updated_content, re.MULTILINE)
    if history_match:
        insert_pos = history_match.end()
        updated_content = updated_content[:insert_pos] + new_history_line + updated_content[insert_pos:]
    else:
        print("[WARN] '## 문서이력관리' 섹션을 찾지 못했습니다. 이력 추가 생략.")

    if dry_run:
        print(f"[DRY-RUN] 추가될 이력: {new_history_line.strip()}")
        print(f"[DRY-RUN] 파일 저장 안 함")
        return 0

    todo_file.write_text(updated_content, encoding="utf-8")
    print(f"[OK] 문서이력 업데이트: {new_version}")
    print(f"[OK] 메시지: {msg}")
    return 0


def cmd_run(sp: str = "00", dry_run: bool = False, max_items: int = 0):
    todo_file = get_todo_file(sp)
    if not todo_file.exists():
        print(f"오류: {todo_file} 파일이 존재하지 않습니다.")
        return

    content = todo_file.read_text(encoding="utf-8")
    todos = parse_waiting_todos(content)

    print("# cctodo - 대기 중 업무 자동 처리\n")
    if not todos:
        print("[OK] 처리할 대기 중 업무가 없습니다.")
        return

    if max_items > 0:
        todos = todos[:max_items]

    print(f"## 처리 대상: {len(todos)}개 항목\n")

    todo_actions = []
    for todo in todos:
        tag = "MISC"
        m = re.match(r"^\[([A-Z]+)\]", todo["content"])
        if m:
            tag = m.group(1)
        skill = get_processing_skill(tag, todo["content"])
        todo_actions.append({"todo": todo, "skill": skill})

    for item in todo_actions:
        todo = item["todo"]
        pmark = "[!]" if todo["priority"].lower() in ("high", "critical") else ""
        print(f"- {pmark}[{todo['id']}] {todo['content']}")
        print(f"  → 권장 스킬: {item['skill']} run")

    if dry_run:
        print("\n[DRY-RUN] 실제 처리는 수행하지 않습니다.")
        return

    print("\n" + "=" * 50)
    print("## 처리 시작")
    print("=" * 50 + "\n")

    for i, item in enumerate(todo_actions, 1):
        todo = item["todo"]
        skill = item["skill"]
        print(f"\n### [{i}/{len(todo_actions)}] {todo['id']}: {todo['content']}")
        print("\n>>> 다음 업무를 처리하세요:")
        print(f"    내용: {todo['content']}")
        print(f"    권장 실행: {skill} run")
        print("\n    완료 후 순서:")
        print(f"    1. 해당 항목을 '## 완료 ToDo' 섹션으로 이동")
        print(f"       - 항목 ID: {todo['id']}")
        print(f"       - 파일: {todo_file.relative_to(PROJECT_ROOT)}")
        print(f"    2. oocommit run  ← 커밋 + 이력 이동")
        print(f"    3. 다음 항목으로 이동")

    print("\n" + "=" * 50)
    print(f"\n총 {len(todo_actions)}개 항목 처리 지침 출력 완료.")


# ============================================================
# Main
# ============================================================


def cmd_show_checklist():
    """references/checklist.md 내용 출력"""
    checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[{SKILL_NAME}] checklist.md 없음: {checklist_path}")
        return
    print(checklist_path.read_text(encoding="utf-8"))


def main():
    if not sys.argv[1:]:
        sys.argv.append("run")

    args = sys.argv[1:]
    sp = "00"
    dry_run = False
    max_items = 0

    filtered_args = []
    i = 0
    while i < len(args):
        if args[i] == "--sp" and i + 1 < len(args):
            sp = args[i + 1]
            i += 2
        elif args[i] == "--dry-run":
            dry_run = True
            i += 1
        elif args[i] == "--max-items" and i + 1 < len(args):
            max_items = int(args[i + 1])
            i += 2
        else:
            filtered_args.append(args[i])
            i += 1

    args = filtered_args

    if not args:
        cmd_run(sp, dry_run, max_items)
        return

    first_arg = args[0]
    subcommand = first_arg.lower()

    if subcommand in ("help", "-h"):
        _print_skill_help("cctodo")
        return

    if subcommand == "status":
        cmd_status(sp)
        return

    if subcommand == "list":
        cmd_list(None if sp == "00" else sp)
        return

    if subcommand == "run":
        cmd_run(sp, dry_run, max_items)
        return

    if subcommand == "clear":
        cmd_clear(sp, dry_run)
        return

    if subcommand == "audit":
        cmd_audit(sp)
        return

    if subcommand == "reopen":
        if len(args) < 2:
            print("사용법: cctodo reopen [ID] [\"메모\"]  (예: cctodo reopen C012 \"미구현\")")
            return
        todo_id = args[1].upper()
        note = args[2] if len(args) >= 3 else ""
        cmd_reopen(todo_id, note, sp)
        return

    if subcommand == "history":
        if len(args) < 2:
            print("사용법: cctodo history [ID]  (예: cctodo history C012)")
            return
        todo_id = args[1].upper()
        cmd_history_one(todo_id, sp)
        return

    if subcommand == "update":
        message = None
        no_sort = False
        j = 1
        while j < len(args):
            if args[j] == "--message" and j + 1 < len(args):
                message = args[j + 1]
                j += 2
            elif args[j] == "--no-sort":
                no_sort = True
                j += 1
            else:
                j += 1
        cmd_update(sp, message, no_sort, dry_run)
        return

    if subcommand == "complete":
        if len(args) < 2:
            print("사용법: cctodo complete [ID]  (예: cctodo complete C012)")
            return
        todo_id = args[1].upper()
        sp_val = sp
        todo_file = get_todo_file(sp_val)
        if not todo_file.exists():
            print(f"[ERROR] 파일 없음: {todo_file}")
            return
        content = todo_file.read_text(encoding="utf-8")
        new_content = move_todo_to_completed(content, todo_id)
        if new_content == content:
            print(f"[ERROR] {todo_id} 항목을 찾을 수 없습니다.")
            return
        todo_file.write_text(new_content, encoding="utf-8")

        # 상세 파일이 있으면 헤더에 DONE 표기
        detail_marked = mark_todo_detail_done(sp_val, todo_id)
        detail_msg = "상세 파일 DONE 표기 완료" if detail_marked else "상세 파일 없음 (스킵)"

        print(f"# cctodo complete\n\n[OK] {todo_id} → 완료 ToDo 섹션으로 이동됨")
        print(f"     {detail_msg}")
        return

    if subcommand == "add":
        if len(args) < 2:
            print("사용법: cctodo add [text]")
            return
        text = args[1]
        priority = "medium"
        note = "-"
        j = 2
        while j < len(args):
            if args[j] == "--priority" and j + 1 < len(args):
                priority = args[j + 1].lower()
                j += 2
            elif args[j] == "--note" and j + 1 < len(args):
                note = args[j + 1]
                j += 2
            else:
                j += 1
        cmd_add(text, priority, note, sp)
        return

    if subcommand in ("show",) and len(args) > 1 and args[1].lower() == "checklist":
        cmd_show_checklist()
        return

    # 알려진 서브커맨드 외 단일 단어가 들어오면 typo 가능성이 높으므로 거부.
    # (예: 'update' 같은 미구현/오탈자가 cmd_add_and_run으로 빠지는 사고 방지)
    KNOWN_SUBS = {
        "help", "-h", "status", "list", "run", "clear", "audit", "reopen",
        "history", "complete", "add", "update", "show", "version",
    }
    if first_arg and not first_arg.startswith("-"):
        single_word = " " not in first_arg.strip()
        if single_word and first_arg.lower() not in KNOWN_SUBS:
            print(f"[ERROR] 알 수 없는 서브커맨드: '{first_arg}'")
            print("        ToDo로 추가하려면 따옴표로 감싸세요: cctodo \"내용\"")
            print("        서브커맨드 목록: cctodo help")
            return

        text = first_arg
        priority = "medium"
        note = "-"
        j = 1
        while j < len(args):
            if args[j] == "--priority" and j + 1 < len(args):
                priority = args[j + 1].lower()
                j += 2
            elif args[j] == "--note" and j + 1 < len(args):
                note = args[j + 1]
                j += 2
            else:
                j += 1
        cmd_add_and_run(text, priority, note, sp)
        return

    print("cctodo - Todo 자동 처리 스킬")
    print("\n사용법:")
    print('  cctodo "내용"         # 추가 + 즉시 처리')
    print("  cctodo                # 대기 중 업무 전체 처리")
    print("  cctodo list           # 전체 SP 대기 업무 표시")
    print("  cctodo status         # 현재 SP 대기 중 목록 표시")
    print('  cctodo add [text]     # 추가만 (처리 안함)')
    print("  cctodo clear          # 완료 항목 → d0010_history.md 아카이브")
    print("\n옵션:")
    print("  --sp N          서브프로젝트 지정")
    print("  --dry-run       실제 처리 없이 계획만 표시")
    print("  --max-items N   최대 처리 항목 수")


if __name__ == "__main__":
    main()

