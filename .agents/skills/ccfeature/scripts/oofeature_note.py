#!/usr/bin/env python3
"""
oofeature_note.py - 상세 문서 경로 탐색 헬퍼
Usage:
  uv run python oofeature_note.py dXXXX --find [--sp N]   # 파일 경로만 출력
  uv run python oofeature_note.py dXXXX "내용" [--sp N]   # 직접 ## 메모 추가 (fallback)
"""
import sys
import json
from pathlib import Path
from datetime import date

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
DOC_ROOT = PROJECT_ROOT / "00_doc"

STAGES = ["상세기획", "상세설계", "상세구현", "상세검증"]


def get_current_sp() -> str:
    context_file = PROJECT_ROOT / ".codex" / "skills" / "cccontext" / "references" / "current_context.json"
    if context_file.exists():
        try:
            data = json.loads(context_file.read_text(encoding="utf-8"))
            return str(data.get("sp", "00"))
        except Exception:
            pass
    return "00"


def find_doc(doc_num: str, sp: str) -> Path | None:
    sp_dir = DOC_ROOT / f"sp{sp.zfill(2)}"
    if not sp_dir.exists():
        return None
    for stage in STAGES:
        matches = list(sp_dir.glob(f"{doc_num}_{stage}_*.md"))
        if matches:
            return matches[0]
    return None


def append_memo(doc_path: Path, content: str, section_hint: str = "") -> None:
    """## 메모 섹션에 이력 추가 (Claude가 본문 통합 후 호출)"""
    text = doc_path.read_text(encoding="utf-8")
    today = date.today().strftime("%Y-%m-%d")
    note_text = f"{content} ({section_hint})" if section_hint else content
    new_row = f"| {today} | {note_text} |"

    MEMO_HEADER = "## 메모"
    TABLE_HEADER = "| 날짜 | 내용 |"
    TABLE_SEP = "|------|------|"

    if MEMO_HEADER in text:
        lines = text.splitlines(keepends=True)
        result = []
        i = 0
        inserted = False
        while i < len(lines):
            line = lines[i]
            result.append(line)
            if not inserted and line.strip() == MEMO_HEADER:
                i += 1
                while i < len(lines) and not lines[i].strip():
                    result.append(lines[i])
                    i += 1
                if i < len(lines) and lines[i].strip().startswith("| 날짜"):
                    result.append(lines[i])
                    i += 1
                    if i < len(lines) and lines[i].strip().startswith("|---"):
                        result.append(lines[i])
                        i += 1
                    while i < len(lines) and lines[i].strip().startswith("|"):
                        result.append(lines[i])
                        i += 1
                    result.append(new_row + "\n")
                else:
                    result.append(f"{TABLE_HEADER}\n{TABLE_SEP}\n{new_row}\n")
                inserted = True
                continue
            i += 1
        if not inserted:
            text = "".join(result).rstrip()
            text += f"\n\n{TABLE_HEADER}\n{TABLE_SEP}\n{new_row}\n"
            doc_path.write_text(text, encoding="utf-8")
            return
        doc_path.write_text("".join(result), encoding="utf-8")
    else:
        text = text.rstrip()
        text += f"\n\n{MEMO_HEADER}\n\n{TABLE_HEADER}\n{TABLE_SEP}\n{new_row}\n"
        doc_path.write_text(text, encoding="utf-8")


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("help", "-h", "--help"):
        print("Usage:")
        print("  ccf note dXXXX --find [--sp N]          # 파일 경로 출력")
        print("  ccf note dXXXX \"내용\" [--sp N]          # ## 메모에 직접 추가")
        print("  ccf note dXXXX --memo \"내용\" [--sp N]   # Codex 통합 후 이력 기록")
        return

    doc_num = None
    content = None
    sp = None
    find_mode = False
    memo_mode = False
    section_hint = ""

    i = 0
    while i < len(args):
        if args[i] == "--sp" and i + 1 < len(args):
            sp = args[i + 1]
            i += 2
        elif args[i] == "--find":
            find_mode = True
            i += 1
        elif args[i] == "--memo":
            memo_mode = True
            i += 1
        elif args[i] == "--section" and i + 1 < len(args):
            section_hint = args[i + 1]
            i += 2
        elif doc_num is None:
            doc_num = args[i]
            i += 1
        elif content is None:
            content = args[i]
            i += 1
        else:
            i += 1

    if not doc_num:
        print("[ERROR] 문서 번호 필요")
        sys.exit(1)

    if sp is None:
        sp = get_current_sp()

    doc_path = find_doc(doc_num, sp)
    if not doc_path:
        print(f"[ERROR] SP{sp}에서 {doc_num} 상세 문서를 찾을 수 없음")
        sys.exit(1)

    if find_mode:
        # 파일 경로만 출력 (Claude가 Read/Edit에 사용)
        print(str(doc_path))
        return

    if not content:
        print("[ERROR] 내용 필요")
        sys.exit(1)

    if memo_mode:
        # Claude가 본문 통합 완료 후 이력만 기록
        append_memo(doc_path, content, section_hint)
        today = date.today().strftime("%Y-%m-%d")
        print(f"[ccfeature note] {doc_path.name}")
        print(f"  이력 기록: [{today}] {content}")
    else:
        # fallback: 메모만 추가
        append_memo(doc_path, content)
        today = date.today().strftime("%Y-%m-%d")
        print(f"[ccfeature note] {doc_path.name}")
        print(f"  메모 추가: [{today}] {content}")


if __name__ == "__main__":
    main()
