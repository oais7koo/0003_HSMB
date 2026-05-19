#!/usr/bin/env python3
"""
oofeature_issue.py - 상세 문서 ## 이슈 섹션에 이슈 추가/해결 처리
Usage:
  uv run python oofeature_issue.py dXXXX "이슈내용" [--sp N]       # 이슈 추가
  uv run python oofeature_issue.py dXXXX --find [--sp N]           # 파일 경로 출력
  uv run python oofeature_issue.py dXXXX --resolve [--sp N]        # 최신 미해결 이슈 → 해결
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

STATUS_OPEN = "🔴 미해결"
STATUS_DONE = "✅ 해결"

ISSUE_HEADER = "## 이슈"
TABLE_HEADER = "| 날짜 | 내용 | 상태 |"
TABLE_SEP    = "|------|------|------|"


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


def append_issue(doc_path: Path, content: str) -> None:
    """## 이슈 섹션에 새 이슈 행 추가 (상태: 🔴 미해결)"""
    text = doc_path.read_text(encoding="utf-8")
    today = date.today().strftime("%Y-%m-%d")
    new_row = f"| {today} | {content} | {STATUS_OPEN} |"

    if ISSUE_HEADER in text:
        lines = text.splitlines(keepends=True)
        result = []
        i = 0
        inserted = False
        while i < len(lines):
            line = lines[i]
            result.append(line)
            if not inserted and line.strip() == ISSUE_HEADER:
                i += 1
                # 빈 줄 통과
                while i < len(lines) and not lines[i].strip():
                    result.append(lines[i])
                    i += 1
                # 테이블 헤더 처리
                if i < len(lines) and lines[i].strip().startswith("| 날짜"):
                    result.append(lines[i]); i += 1
                    if i < len(lines) and lines[i].strip().startswith("|---"):
                        result.append(lines[i]); i += 1
                    # 기존 행 유지
                    while i < len(lines) and lines[i].strip().startswith("|"):
                        result.append(lines[i]); i += 1
                    result.append(new_row + "\n")
                else:
                    result.append(f"{TABLE_HEADER}\n{TABLE_SEP}\n{new_row}\n")
                inserted = True
                continue
            i += 1
        if not inserted:
            body = "".join(result).rstrip()
            body += f"\n\n{ISSUE_HEADER}\n\n{TABLE_HEADER}\n{TABLE_SEP}\n{new_row}\n"
            doc_path.write_text(body, encoding="utf-8")
            return
        doc_path.write_text("".join(result), encoding="utf-8")
    else:
        text = text.rstrip()
        text += f"\n\n{ISSUE_HEADER}\n\n{TABLE_HEADER}\n{TABLE_SEP}\n{new_row}\n"
        doc_path.write_text(text, encoding="utf-8")


def resolve_latest(doc_path: Path) -> bool:
    """## 이슈 섹션에서 가장 마지막 🔴 미해결 행을 ✅ 해결로 변경"""
    text = doc_path.read_text(encoding="utf-8")
    if ISSUE_HEADER not in text:
        print(f"[ERROR] ## 이슈 섹션 없음: {doc_path.name}")
        return False

    lines = text.splitlines(keepends=True)
    # 이슈 섹션 내 행 인덱스 수집
    in_issue = False
    open_indices = []
    for idx, line in enumerate(lines):
        if line.strip() == ISSUE_HEADER:
            in_issue = True
            continue
        if in_issue:
            if line.strip().startswith("## "):  # 다음 섹션 시작
                break
            if STATUS_OPEN in line:
                open_indices.append(idx)

    if not open_indices:
        print("[INFO] 미해결 이슈 없음")
        return False

    target = open_indices[-1]
    lines[target] = lines[target].replace(STATUS_OPEN, STATUS_DONE)
    doc_path.write_text("".join(lines), encoding="utf-8")
    return True


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("help", "-h", "--help"):
        print("Usage:")
        print('  ccf issue dXXXX "이슈내용" [--sp N]   # 이슈 추가 (🔴 미해결)')
        print("  ccf issue dXXXX --find [--sp N]       # 파일 경로 출력")
        print("  ccf issue dXXXX --resolve [--sp N]    # 최신 미해결 → ✅ 해결")
        return

    doc_num = None
    content = None
    sp = None
    find_mode = False
    resolve_mode = False

    i = 0
    while i < len(args):
        if args[i] == "--sp" and i + 1 < len(args):
            sp = args[i + 1]; i += 2
        elif args[i] == "--find":
            find_mode = True; i += 1
        elif args[i] == "--resolve":
            resolve_mode = True; i += 1
        elif doc_num is None:
            doc_num = args[i]; i += 1
        elif content is None:
            content = args[i]; i += 1
        else:
            i += 1

    if not doc_num:
        print("[ERROR] 문서 번호 필요 (예: d41001)")
        sys.exit(1)

    if sp is None:
        sp = get_current_sp()

    doc_path = find_doc(doc_num, sp)
    if not doc_path:
        print(f"[ERROR] SP{sp}에서 {doc_num} 상세 문서를 찾을 수 없음")
        sys.exit(1)

    if find_mode:
        print(str(doc_path))
        return

    if resolve_mode:
        ok = resolve_latest(doc_path)
        if ok:
            print(f"[ccfeature issue] {doc_path.name}")
            print(f"  최신 미해결 이슈 → {STATUS_DONE}")
        return

    if not content:
        print("[ERROR] 이슈 내용 필요")
        sys.exit(1)

    append_issue(doc_path, content)
    today = date.today().strftime("%Y-%m-%d")
    print(f"[ccfeature issue] {doc_path.name}")
    print(f"  이슈 추가: [{today}] {content} | {STATUS_OPEN}")


if __name__ == "__main__":
    main()
