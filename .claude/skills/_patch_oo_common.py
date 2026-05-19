#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
oo_common inline 블록 및 help 핸들러 일괄 패치 스크립트
"""

import re
import sys
from pathlib import Path

BASE = Path(__file__).parent

# NEW_BLOCK: regex 패턴 내 \n 은 실제 이스케이프 시퀀스여야 하므로
# 파이썬 소스 문자열에서 \\n 으로 작성해야 파일에 \n 리터럴로 저장됨
NEW_BLOCK = (
    "# --- oo_common inline ---\n"
    "import re as _re\n"
    "_SKILLS_DIR = Path(__file__).parent.parent.parent\n"
    "\n"
    "def _print_skill_help(skill_name):\n"
    '    _sf = _SKILLS_DIR / skill_name / "SKILL.md"\n'
    "    if not _sf.exists():\n"
    '        print(f"[ERROR] .claude/skills/{skill_name}/SKILL.md not found")\n'
    "        return\n"
    '    _c = _sf.read_text(encoding="utf-8")\n'
    '    _m = _re.search(r"## \\uc11c\\ube0c\\uba85\\ub839\\uc5b4\\n\\n((?:\\\\|.+\\n)+)", _c)\n'
    "    if _m:\n"
    '        print(f"`{skill_name} help` \\uc11c\\ube0c\\uba85\\ub839\\uc5b4 \\ubaa9\\ub85d:\\n")\n'
    "        print(_m.group(1).strip())\n"
    "    else:\n"
    '        print(f"[WARN] \\uc11c\\ube0c\\uba85\\ub839\\uc5b4 \\uc139\\uc158 \\uc5c6\\uc74c: {skill_name}/SKILL.md")\n'
    "\n"
    "def show_help_if_no_args(skill_name, args):\n"
    "    if not args:\n"
    "        _print_skill_help(skill_name)\n"
    "        return True\n"
    "    return False\n"
    "# --- end oo_common inline ---"
)

# 각 파일의 (skill_name, file_path, help_handler_replacements) 목록
TARGETS = [
    ("oocheck",   "oocheck/scripts/oocheck_run.py",   [
        (r'    elif subcommand in \("-h", "--help", "help"\):\n        print_usage\(\)\n        return 0',
         '    elif subcommand in ("-h", "--help", "help"):\n        _print_skill_help("oocheck")\n        return 0'),
    ]),
    ("oocommit",  "oocommit/scripts/oocommit_run.py", [
        (r'    elif cmd in \("help", "-h"\):\n        print\("oocommit \[run\|commit\|sync\|preview\|clear\|status\|help\]\\nGit \ucf54\ubc0b \ubc0f \uc774\ub825 \uc815\ub9ac"\)\n        return 0',
         '    elif cmd in ("help", "-h"):\n        _print_skill_help("oocommit")\n        return 0'),
    ]),
    ("oocontext", "oocontext/scripts/oocontext_run.py", [
        (r'    elif cmd in \("help", "-h"\):\n        print\("oocontext \[N\|clear\|list\|show\|status\|version\|help\]\\n\uc11c\ube0c\ud504\ub85c\uc81d\ud2b8 \ucee8\ud14d\uc2a4\ud2b8 \uad00\ub9ac"\)',
         '    elif cmd in ("help", "-h"):\n        _print_skill_help("oocontext")'),
    ]),
    ("oodb",      "oodb/scripts/oodb_run.py",         [
        (r'    elif cmd in \("help", "-h"\):\n        print\("oodb \[run\|optimize\|doc\|status\|help\]\\nDB \uc218\uc815 \ubc0f \ucd5c\uc801\ud654"\)\n        return 0',
         '    elif cmd in ("help", "-h"):\n        _print_skill_help("oodb")\n        return 0'),
    ]),
    ("oodoc",     "oodoc/scripts/oodoc_run.py",       [
        (r'    if len\(sys\.argv\) > 1 and sys\.argv\[1\] in \("help", "-h"\):\n        print\("oodoc \[run\|gen\|list\|plan\|help\]\\n\ubb38\uc11c \uc0dd\uc131 \ud1b5\ud569"\)\n        return 0',
         '    if len(sys.argv) > 1 and sys.argv[1] in ("help", "-h"):\n        _print_skill_help("oodoc")\n        return 0'),
    ]),
    ("oofix",     "oofix/scripts/oofix_run.py",       [
        (r'    elif cmd in \("help", "-h"\):\n        print\("oofix \[run\|preview\|test\|verify\|rollback\|status\|help\]\\n\ucf54\ub4dc \uc624\ub958 \uc790\ub3d9 \uc218\uc815"\)\n        return 0',
         '    elif cmd in ("help", "-h"):\n        _print_skill_help("oofix")\n        return 0'),
    ]),
    ("oohistory", "oohistory/scripts/oohistory_run.py", [
        (r'    elif cmd in \("help", "-h"\):\n        print\("oohistory \[run\|list\|create\|search\|sync\|version\|help\]\\n\uc644\ub8cc \ud56d\ubaa9 \uc774\ub825 \uad00\ub9ac"\)\n        return 0',
         '    elif cmd in ("help", "-h"):\n        _print_skill_help("oohistory")\n        return 0'),
    ]),
    ("oolib",     "oolib/scripts/oolib_run.py",       [
        (r'    elif cmd in \("help", "-h"\):\n        print\("oolib \[run\|optimize\|doc\|status\|help\]\\noo \ubaa8\ub4c8 \uc218\uc815/\ucd5c\uc801\ud654"\)\n        return 0',
         '    elif cmd in ("help", "-h"):\n        _print_skill_help("oolib")\n        return 0'),
    ]),
    ("oonext",    "oonext/scripts/oonext_run.py",     []),
    ("oopaper",   "oopaper/scripts/oopaper_run.py",   [
        (r'    if len\(sys\.argv\) > 1 and sys\.argv\[1\] in \("help", "-h"\):\n        print\("oopaper \[run\|status\|sync-list\|fix\|quality\|download\|help\]\\n\ud1b5\ud569 \ubb38\ud5cc \uad00\ub9ac"\)\n        return',
         '    if len(sys.argv) > 1 and sys.argv[1] in ("help", "-h"):\n        _print_skill_help("oopaper")\n        return'),
        (r"    if args\.command == 'help' or \(len\(sys\.argv\) > 1 and sys\.argv\[1\] in \(\"help\", \"-h\"\)\):\n        print\(\"oopaper \[run\|status\|sync-list\|fix\|quality\|download\|help\]\\n\ud1b5\ud569 \ubb38\ud5cc \uad00\ub9ac\"\)\n        return",
         "    if args.command == 'help' or (len(sys.argv) > 1 and sys.argv[1] in (\"help\", \"-h\")):\n        _print_skill_help(\"oopaper\")\n        return"),
    ]),
    ("ooprd",     "ooprd/scripts/ooprd_run.py",       [
        (r'    elif cmd in \("help", "-h"\):\n        print\("ooprd \[run\|template\|validate\|update\|section\|help\]\\nPRD \uc0dd\uc131 \ubc0f \uc815\ud569\uc131 \uac80\uc99d"\)\n        return 0',
         '    elif cmd in ("help", "-h"):\n        _print_skill_help("ooprd")\n        return 0'),
    ]),
    ("ooreport",  "ooreport/scripts/ooreport_run.py", [
        (r'    elif cmd in \("help", "-h"\):\n        print\("ooreport \[run\|update\|list\|help\]\\n\ub9ac\ud3ec\ud2b8 \uc790\ub3d9 \uc0dd\uc131"\)\n        return 0',
         '    elif cmd in ("help", "-h"):\n        _print_skill_help("ooreport")\n        return 0'),
    ]),
    ("ooskill",   "ooskill/scripts/ooskill_run.py",   [
        (r'    elif cmd in \("-h", "--help", "help"\):\n        show_help_if_no_args\("ooskill", \[\]\)\n        return 0',
         '    elif cmd in ("-h", "--help", "help"):\n        _print_skill_help("ooskill")\n        return 0'),
    ]),
    ("oostart",   "oostart/scripts/oostart_run.py",   [
        (r'    if sys\.argv\[1:\] and sys\.argv\[1\] in \("help", "-h"\):\n        print\("oostart \[run\|help\]\\n\uc138\uc158 \uc2dc\uc791 \uc6cc\ud06c\ud50c\ub85c\uc6b0"\)\n        return',
         '    if sys.argv[1:] and sys.argv[1] in ("help", "-h"):\n        _print_skill_help("oostart")\n        return'),
    ]),
    ("oostop",    "oostop/scripts/oostop_run.py",     [
        (r'    elif cmd in \("help", "-h"\):\n        print\("oostop \[run\|readme\|sync\|cleanup\|help\]\\n\uc138\uc158 \uc885\ub8cc \uc6cc\ud06c\ud50c\ub85c\uc6b0"\)\n        return 0',
         '    elif cmd in ("help", "-h"):\n        _print_skill_help("oostop")\n        return 0'),
    ]),
    ("oosurvey",  "oosurvey/scripts/oosurvey_run.py", [
        (r'    elif cmd in \("help", "-h"\):\n        print\("oosurvey \[run\|list\|status\|version\|help\]\\n\ub17c\ubb38 \uc11c\ubca0\uc774 \ubc0f \ubd84\uc11d"\)',
         '    elif cmd in ("help", "-h"):\n        _print_skill_help("oosurvey")'),
    ]),
    ("oosync",    "oosync/scripts/oosync_run.py",     []),
    ("ootest",    "ootest/scripts/ootest_run.py",     [
        (r'    elif cmd in \("help", "-h"\):\n        print\("ootest \[run\|preview\|help\]\\n\ud1b5\ud569 \ud14c\uc2a4\ud2b8 \uc2e4\ud589"\)\n        return 0',
         '    elif cmd in ("help", "-h"):\n        _print_skill_help("ootest")\n        return 0'),
    ]),
    ("ootodo",    "ootodo/scripts/ootodo_run.py",     [
        (r'    if subcommand in \("help", "-h"\):\n        print\("ootodo \[add\|clear\|status\|help\]\\nTODO \uc790\ub3d9 \ucc98\ub9ac"\)\n        return',
         '    if subcommand in ("help", "-h"):\n        _print_skill_help("ootodo")\n        return'),
    ]),
]

BLOCK_PATTERN = re.compile(
    r'# --- oo_common inline ---\r?\n.*?# --- end oo_common inline ---',
    re.DOTALL
)


def patch_file(skill_name, rel_path, help_replacements):
    fpath = BASE / rel_path
    if not fpath.exists():
        print(f"[SKIP] {rel_path} (파일 없음)")
        return False

    # 파일을 utf-8로 읽기
    raw = fpath.read_bytes()
    try:
        original = raw.decode('utf-8')
    except UnicodeDecodeError:
        original = raw.decode('utf-8-sig')

    # CRLF → LF 정규화 후 처리, 마지막에 원본 line ending 복원
    use_crlf = '\r\n' in original
    content = original.replace('\r\n', '\n')

    # 1) oo_common 블록 교체
    if BLOCK_PATTERN.search(content):
        content = BLOCK_PATTERN.sub(NEW_BLOCK, content)
    else:
        print(f"[WARN] {rel_path}: oo_common inline 블록 없음")

    # 2) help 핸들러 교체 (LF 정규화된 상태에서 매칭)
    for old_pat, new_str in help_replacements:
        replaced = re.sub(old_pat, new_str, content)
        if replaced == content:
            print(f"[WARN] {skill_name}: help 패턴 미매칭 → 직접 문자열 탐색 시도")
            # 직접 탐색으로 재시도
            content = _try_direct_replace(content, skill_name)
        else:
            content = replaced

    if content.replace('\r\n', '\n') == original.replace('\r\n', '\n'):
        print(f"[NO-CHANGE] {rel_path}")
        return False

    # 원본 line ending 복원
    if use_crlf:
        content = content.replace('\n', '\r\n')

    fpath.write_text(content, encoding='utf-8')
    print(f"[OK] {rel_path}")
    return True


def _try_direct_replace(content, skill_name):
    """regex 미매칭 시 간단한 줄 단위 탐색으로 print one-liner 교체"""
    lines = content.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # "help" 핸들러 줄 + 다음 줄이 print(... one-liner 패턴
        if (('elif cmd in' in line or 'elif subcommand in' in line or 'if subcommand in' in line)
                and ('"help"' in line or '"-h"' in line or '"--help"' in line)):
            result.append(line)
            # 다음 줄이 print( 로 시작하면 교체
            if i + 1 < len(lines) and lines[i+1].strip().startswith('print('):
                indent = len(lines[i+1]) - len(lines[i+1].lstrip())
                result.append(' ' * indent + f'_print_skill_help("{skill_name}")')
                i += 2
                continue
        result.append(line)
        i += 1
    return '\n'.join(result)


def main():
    ok = 0
    skip = 0
    for skill_name, rel_path, help_replacements in TARGETS:
        changed = patch_file(skill_name, rel_path, help_replacements)
        if changed:
            ok += 1
        else:
            skip += 1

    print(f"\n완료: {ok}개 수정, {skip}개 변경없음")


if __name__ == "__main__":
    main()
