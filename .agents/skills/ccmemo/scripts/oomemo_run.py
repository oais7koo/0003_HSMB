#!/usr/bin/env python3
"""
oomemo_run.py - ccmemo 스킬 스크립트 (임시 메모 읽기/쓰기)
Usage: uv run python .agents/skills/ccmemo/scripts/oomemo_run.py [w|r|run|help|version|status] [내용]
"""
import sys
from pathlib import Path
import re as _re
import datetime

# --- oo_common inline ---
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

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

SKILL_NAME = "ccmemo"
VERSION = "v05"
MEMO_FILE = Path("00_doc/zzz.md")

READ_KEYWORDS  = ["읽어", "가져와", "보여줘", "확인해", "뭐야", "뭐가 있어", "조회", "뭐있어", "뭔지"]
WRITE_KEYWORDS = ["저장해", "써줘", "기록해", "메모해", "바꿔", "업데이트", "저장", "적어"]


def cmd_version():
    print(f"[{SKILL_NAME}] 버전: {VERSION}")


def cmd_status():
    exists = MEMO_FILE.exists()
    size = MEMO_FILE.stat().st_size if exists else 0
    print(f"[{SKILL_NAME} status]")
    print(f"  파일: {MEMO_FILE}")
    print(f"  존재: {'O' if exists else 'X'}")
    if exists:
        print(f"  크기: {size} bytes")
        mtime = datetime.datetime.fromtimestamp(MEMO_FILE.stat().st_mtime)
        print(f"  수정: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")


def cmd_read():
    if not MEMO_FILE.exists():
        print("(비어 있음)")
        return
    content = MEMO_FILE.read_text(encoding="utf-8")
    if not content.strip():
        print("(비어 있음)")
    else:
        print(content)


def cmd_write(content: str):
    if not content.strip():
        print("[ERROR] 저장할 내용이 없습니다.")
        sys.exit(1)
    MEMO_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMO_FILE.write_text(content, encoding="utf-8")
    print(f"00_doc/zzz.md에 저장했습니다.")


def cmd_run(instruction: str):
    """키워드 기반으로 읽기/쓰기 자동 판단. 모호하면 읽기 우선."""
    instr_lower = instruction.lower()

    is_read  = any(k in instruction for k in READ_KEYWORDS)
    is_write = any(k in instruction for k in WRITE_KEYWORDS)

    if is_read and not is_write:
        cmd_read()
        return

    if is_write:
        # 키워드 앞 내용을 저장 대상으로 추출 (키워드 제거)
        content = instruction
        for k in WRITE_KEYWORDS:
            content = content.replace(k, "").strip()
        if not content:
            print("[WARN] 저장할 내용을 찾지 못했습니다. 지시사항을 그대로 저장합니다.")
            content = instruction
        cmd_write(content)
        return

    # 모호한 경우 → 읽기 우선
    print(f"[INFO] 의도가 모호합니다. 안전하게 읽기를 실행합니다.")
    cmd_read()


def cmd_no_args():
    """인자 없음: 직전 대화 저장은 AI 컨텍스트 필요 → 안내만 출력."""
    print("[ccmemo]")
    print("직전 대화 저장은 AI가 직접 처리합니다.")
    print("")
    print("스크립트로 사용할 수 있는 명령어:")
    print("  ccmemo r          → 메모 읽기")
    print("  ccmemo w [내용]   → 메모 덮어쓰기")
    print("  ccmemo run [지시] → 읽기/쓰기 자동 판단")


def main():
    args = sys.argv[1:]

    if not args:
        cmd_no_args()
        return

    sub = args[0].lower()

    if sub in ("help", "-h", "--help"):
        _print_skill_help(SKILL_NAME)
    elif sub == "version":
        cmd_version()
    elif sub == "status":
        cmd_status()
    elif sub == "r":
        cmd_read()
    elif sub == "w":
        content = " ".join(args[1:])
        cmd_write(content)
    elif sub == "run":
        instruction = " ".join(args[1:])
        if not instruction:
            print("[ERROR] run 뒤에 지시사항을 입력하세요.")
            print("  예) ccmemo run zzz에 뭐가 있어?")
            sys.exit(1)
        cmd_run(instruction)
    else:
        # 첫 인자가 서브명령어가 아닌 경우 → 내용으로 간주해 쓰기
        content = " ".join(args)
        cmd_write(content)


if __name__ == "__main__":
    main()
