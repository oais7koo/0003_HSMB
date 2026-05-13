#!/usr/bin/env python3
"""
[oopaper_run_entry.py]
ccpaper 스킬 메인 진입점. --lang 옵션으로 EN/KO 분기.

사용법:
    uv run python .claude/skills/ccpaper/scripts/oopaper_run_entry.py [--lang en|ko] [subcommand] [options]
    uv run python .claude/skills/ccpaper/scripts/oopaper_run_entry.py status
    uv run python .claude/skills/ccpaper/scripts/oopaper_run_entry.py --lang ko status
"""

import sys
import re as _re
import subprocess
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

_SKILLS_DIR = Path(__file__).parent.parent.parent
_THIS_DIR = Path(__file__).parent

def show_help():
    _sf = _SKILLS_DIR / "ccpaper" / "SKILL.md"
    if _sf.exists():
        _c = _sf.read_text(encoding="utf-8")
        _m = _re.search(r"^# \w+ - (.+)$", _c, _re.MULTILINE)
        print(f"## ccpaper\n\n**용도**: {_m.group(1).strip() if _m else ''}\n")
        _cmds = []
        for _cm in _re.finditer(r"\|\s*`([^`]+)`\s*\|", _c):
            _cc = _cm.group(1).strip()
            if _cc.startswith("ccpaper"):
                _s = _cc.replace("ccpaper", "").strip()
                if _s and _s not in _cmds:
                    _cmds.append(_s)
        print("### 서브명령어\n")
        for _cc in _cmds:
            print(f"- `ccpaper {_cc}`")
        print("\n**상세 문서**: `.claude/skills/ccpaper/SKILL.md`")
    else:
        print("[ERROR] .claude/skills/ccpaper/SKILL.md not found")

def main():
    args = sys.argv[1:]

    # 인수 없으면 help 출력
    if not args:
        show_help()
        return

    # --lang 파싱 (기본: en)
    lang = "en"
    remaining = []
    i = 0
    while i < len(args):
        if args[i] == "--lang" and i + 1 < len(args):
            lang = args[i + 1]
            i += 2
        else:
            remaining.append(args[i])
            i += 1

    # 언어별 스크립트 선택
    if lang == "ko":
        target = _THIS_DIR / "ooessay_run.py"
    else:
        target = _THIS_DIR / "oopaper_run.py"

    # 서브스크립트로 위임
    cmd = [sys.executable, str(target)] + remaining
    result = subprocess.run(cmd)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
