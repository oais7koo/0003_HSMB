"""oo* 스킬 스크립트에 show checklist 서브명령어 일괄 추가"""
import re
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent.parent

FUNCTION_CODE = '''
def cmd_show_checklist():
    """references/checklist.md 내용 출력"""
    checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[{SKILL_NAME}] checklist.md 없음: {checklist_path}")
        return
    print(checklist_path.read_text(encoding="utf-8"))

'''

# args[0] 직접 사용 버전 (cmd/subcommand 변수 없는 파일용)
DISPATCH_ARGS0 = (
    '    if args and args[0].lower() == "show" and len(args) > 1 and args[1].lower() == "checklist":\n'
    '        cmd_show_checklist()\n'
    '        return\n'
)


def has_function(content: str) -> bool:
    return "def cmd_show_checklist" in content


def has_dispatch(content: str) -> bool:
    main_idx = content.find("\ndef main():")
    if main_idx == -1:
        return False
    return "cmd_show_checklist()" in content[main_idx:]


def add_function(content: str) -> str:
    idx = content.find("\ndef main():")
    if idx == -1:
        return content
    return content[:idx] + FUNCTION_CODE + content[idx:]


def detect_cmd_var(lines: list[str]) -> str | None:
    """main() 안에서 cmd/subcommand 변수명 감지"""
    in_main = False
    for line in lines:
        if "def main():" in line:
            in_main = True
        if in_main:
            m = re.search(r'\b(subcommand|cmd|first_arg)\s*=\s*(?:args\[0\]|first_arg)(?:\.lower\(\))?', line)
            if m:
                return m.group(1)
    return None


def make_dispatch(cmd_var: str | None) -> str:
    if cmd_var:
        return (
            f'    if {cmd_var} in ("show",) and len(args) > 1 and args[1].lower() == "checklist":\n'
            f'        cmd_show_checklist()\n'
            f'        return\n'
        )
    return DISPATCH_ARGS0


def add_dispatch(content: str) -> tuple[str, str]:
    lines = content.splitlines(keepends=True)
    cmd_var = detect_cmd_var(lines)
    dispatch = make_dispatch(cmd_var)

    # 패턴 1: '알 수 없는 명령' 라인 앞
    for i, line in enumerate(lines):
        if "알 수 없는 명령" in line and "def " not in line and not line.lstrip().startswith("#"):
            indent = len(line) - len(line.lstrip())
            if indent > 0:
                adjusted = "\n".join(
                    " " * indent + l[4:] if l.startswith("    ") else " " * indent + l
                    for l in dispatch.rstrip("\n").splitlines()
                ) + "\n"
            else:
                adjusted = dispatch
            lines.insert(i, adjusted)
            return "".join(lines), "before_unknown"

    # 패턴 2: if/elif 체인의 마지막 else: 앞 (main 내부)
    in_main = False
    for i, line in enumerate(lines):
        if "def main():" in line:
            in_main = True
        if in_main and line.strip() == "else:":
            prev = lines[i - 1].strip() if i > 0 else ""
            if prev.startswith("elif") or prev.endswith(":"):
                lines.insert(i, dispatch)
                return "".join(lines), "before_else"

    # 패턴 3: catch-all 'if first_arg and not first_arg.startswith' 앞
    in_main = False
    for i, line in enumerate(lines):
        if "def main():" in line:
            in_main = True
        if in_main and "first_arg" in line and "not first_arg.startswith" in line:
            lines.insert(i, dispatch)
            return "".join(lines), "before_catch_all"

    # 패턴 4: cmd/subcommand 변수 설정 직후
    in_main = False
    for i, line in enumerate(lines):
        if "def main():" in line:
            in_main = True
        if in_main:
            m = re.search(r'\b(subcommand|cmd|first_arg)\s*=\s*(?:args\[0\]|first_arg)(?:\.lower\(\))?', line)
            if m:
                lines.insert(i + 1, dispatch)
                return "".join(lines), "after_cmd_assign"

    # 패턴 5: 'if not args or args[0].lower() in ("help"' 블록 뒤 (FUNC_ONLY 파일)
    in_main = False
    for i, line in enumerate(lines):
        if "def main():" in line:
            in_main = True
        if in_main and 'args[0].lower() in' in line and 'help' in line:
            # 해당 블록의 끝(return 줄) 다음에 삽입
            for j in range(i, min(i + 10, len(lines))):
                if lines[j].strip() == "return":
                    lines.insert(j + 1, DISPATCH_ARGS0)
                    return "".join(lines), "after_help_return"
            break

    # 패턴 6: sys.argv 직접 체크 — def main(): 바로 다음 줄에 삽입 (만능 fallback)
    SYSARGV_DISPATCH = (
        '    if len(sys.argv) > 2 and sys.argv[1].lower() == "show" and sys.argv[2].lower() == "checklist":\n'
        '        cmd_show_checklist()\n'
        '        return\n'
    )
    in_main = False
    for i, line in enumerate(lines):
        if "def main():" in line:
            in_main = True
            # 다음 줄(함수 첫 줄) 바로 앞에 삽입
            lines.insert(i + 1, SYSARGV_DISPATCH)
            return "".join(lines), "sysargv_at_main_start"

    return content, "no_match"


def patch_file(script_path: Path) -> str:
    content = script_path.read_text(encoding="utf-8")

    if has_function(content) and has_dispatch(content):
        return "SKIP"

    checklist = script_path.parent.parent / "references" / "checklist.md"
    if not checklist.exists():
        return "NO_CHECKLIST"

    if not has_function(content):
        content = add_function(content)

    if not has_dispatch(content):
        content, method = add_dispatch(content)
    else:
        method = "had_dispatch"

    script_path.write_text(content, encoding="utf-8")
    return f"OK ({method})"


def main():
    scripts = sorted(SKILLS_DIR.glob("oo*/scripts/*_run.py"))
    results = []

    for script in scripts:
        status = patch_file(script)
        results.append((script.parent.parent.name, script.name, status))

    print(f"{'스킬':<25} {'파일':<30} {'결과'}")
    print("-" * 75)
    counts: dict[str, int] = {}
    for skill, fname, status in results:
        print(f"{skill:<25} {fname:<30} {status}")
        key = status.split("(")[0].strip()
        counts[key] = counts.get(key, 0) + 1

    print(f"\n소계: {' | '.join(f'{k}={v}' for k, v in counts.items())}")


if __name__ == "__main__":
    main()
