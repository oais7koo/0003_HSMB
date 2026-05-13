"""ccopti - 알고리즘/코드 최적화 스크립트

대상 파일의 성능 프로파일링, 복잡도 분석, 벤치마크를 수행한다.

Usage:
    uv run python .claude/skills/ccopti/scripts/ooopti_run.py profile <file>
    uv run python .claude/skills/ccopti/scripts/ooopti_run.py complexity <file>
    uv run python .claude/skills/ccopti/scripts/ooopti_run.py benchmark <file> <function>
    uv run python .claude/skills/ccopti/scripts/ooopti_run.py status
"""

import cProfile
import io
import pstats
import sys
import sys as _sys
if _sys.stdout.encoding and _sys.stdout.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stdout.reconfigure(encoding='utf-8')
if _sys.stderr.encoding and _sys.stderr.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stderr.reconfigure(encoding='utf-8')

# --- oo_common inline ---
from pathlib import Path
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
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OOOPTI_VERSION = "v01"


def cmd_profile(target: str, top_n: int = 10):
    """cProfile 기반 프로파일링."""
    target_path = Path(target)
    if not target_path.exists():
        print(f"  파일 없음: {target}")
        return

    print(f"[ccopti profile] {target}")
    print(f"  프로파일러: cProfile")
    print()

    # cProfile 실행
    profiler = cProfile.Profile()
    try:
        profiler.run(f"exec(open(r'{target_path}').read())")
    except Exception as e:
        print(f"  실행 오류: {e}")
        return

    # 결과 출력
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("cumulative")
    stats.print_stats(top_n)

    output = stream.getvalue()
    print(output)

    # 핫스팟 요약
    print(f"  Top {top_n} 핫스팟 출력 완료")
    print(f"  전체 함수 수: {len(stats.stats)}")


def cmd_complexity(target: str):
    """파일 내 함수별 복잡도 힌트 분석."""
    target_path = Path(target)
    if not target_path.exists():
        print(f"  파일 없음: {target}")
        return

    print(f"[ccopti complexity] {target}")
    print()

    text = target_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    # 간단한 복잡도 힌트 분석
    nested_loops = 0
    functions = []
    current_func = None
    func_loops = 0

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # 함수 감지
        if stripped.startswith("def "):
            if current_func:
                functions.append((current_func, func_loops))
            current_func = stripped.split("(")[0].replace("def ", "")
            func_loops = 0

        # 루프 감지
        if stripped.startswith(("for ", "while ")) and current_func:
            # 들여쓰기 깊이로 중첩 추정
            indent = len(line) - len(line.lstrip())
            func_loops = max(func_loops, indent // 4)

    if current_func:
        functions.append((current_func, func_loops))

    # 복잡도 추정 테이블
    print("| 함수 | 루프 중첩 | 추정 복잡도 |")
    print("|------|:--------:|-----------|")

    complexity_map = {0: "O(1)", 1: "O(n)", 2: "O(n^2)", 3: "O(n^3)"}

    for func_name, depth in functions:
        est = complexity_map.get(depth, f"O(n^{depth})")
        flag = " <<<" if depth >= 2 else ""
        print(f"| {func_name} | {depth} | {est}{flag} |")

    print(f"\n  함수 {len(functions)}개 분석 완료")
    warnings = sum(1 for _, d in functions if d >= 2)
    if warnings:
        print(f"  주의: 중첩 루프 {warnings}건 (O(n^2) 이상)")


def cmd_benchmark(target: str, func_name: str, iterations: int = 1000):
    """함수 벤치마크."""
    print(f"[ccopti benchmark] {target}::{func_name}")
    print(f"  반복: {iterations}회")
    print()
    print("  벤치마크는 대화형으로 실행합니다.")
    print("  사용법:")
    print(f'    python -m timeit -n {iterations} "import {Path(target).stem}; {Path(target).stem}.{func_name}()"')


def cmd_status():
    """현재 상태 출력."""
    print(f"[ccopti status]")
    print(f"  버전: {OOOPTI_VERSION}")
    print(f"  프로파일러: cProfile (내장)")
    print()

    # 최적화 리포트 존재 확인
    doc_dir = ROOT / "00_doc"
    reports = list(doc_dir.glob("d*0012_optimization.md"))
    if reports:
        print(f"  리포트: {len(reports)}건")
        for r in reports:
            print(f"    - {r.name}")
    else:
        print("  리포트: 없음")


def cmd_show_checklist():
    """references/checklist.md 내용 출력"""
    checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[{SKILL_NAME}] checklist.md 없음: {checklist_path}")
        return
    print(checklist_path.read_text(encoding="utf-8"))


def main():
    args = sys.argv[1:]

    if show_help_if_no_args("ccopti", args):
        return

    cmd = args[0]

    if cmd == "profile" and len(args) >= 2:
        top_n = 10
        if "--top" in args:
            idx = args.index("--top")
            if idx + 1 < len(args):
                top_n = int(args[idx + 1])
        cmd_profile(args[1], top_n)
    elif cmd == "complexity" and len(args) >= 2:
        cmd_complexity(args[1])
    elif cmd == "benchmark" and len(args) >= 3:
        iterations = 1000
        if "--iterations" in args:
            idx = args.index("--iterations")
            if idx + 1 < len(args):
                iterations = int(args[idx + 1])
        cmd_benchmark(args[1], args[2], iterations)
    elif cmd == "status":
        cmd_status()
    else:
        if cmd in ("show",) and len(args) > 1 and args[1].lower() == "checklist":
            cmd_show_checklist()
            return
        print(f"알 수 없는 명령: {cmd}")
        print("ooopti_run.py help 로 사용법 확인")


if __name__ == "__main__":
    main()
