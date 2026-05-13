#!/usr/bin/env python3
"""ccbatch - 모든 oo* 스킬에 동일한 서브명령어 일괄 실행"""

import sys
import io
import re
import subprocess
from pathlib import Path

# Windows cp949 터미널에서 UTF-8 출력 강제
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def find_skills_root() -> Path:
    # .claude/skills/ccbatch/scripts/oobatch_run.py → .claude/skills/
    return Path(__file__).parent.parent.parent


def scan_skills_for_subcmd(skills_root: Path, subcmd: str) -> list[dict]:
    """oo* 스킬 중 subcmd를 가진 스킬 탐지"""
    results = []
    for skill_dir in sorted(skills_root.glob("oo*")):
        if not skill_dir.is_dir() or skill_dir.name == "ccbatch":
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        content = skill_md.read_text(encoding="utf-8")
        skill_name = skill_dir.name

        # 서브명령어 테이블 행 탐지: | `skill subcmd` | 또는 | skill subcmd |
        pattern = rf"\|\s*`?{re.escape(skill_name)}\s+{re.escape(subcmd)}`?\s*\|"
        has_subcmd = bool(re.search(pattern, content, re.IGNORECASE))

        if has_subcmd:
            script = skill_dir / "scripts" / f"{skill_name}_run.py"
            results.append({
                "name": skill_name,
                "script": script if script.exists() else None,
            })
    return results


def run_skill(skill: dict, subcmd_args: list[str]) -> dict:
    name = skill["name"]
    script = skill["script"]

    if not script:
        return {"name": name, "status": "SKIP", "message": "스크립트 없음"}

    try:
        result = subprocess.run(
            ["uv", "run", "python", str(script)] + subcmd_args,
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120
        )
        if result.returncode == 0:
            return {"name": name, "status": "OK", "output": result.stdout}
        else:
            return {"name": name, "status": "FAIL",
                    "output": result.stdout + result.stderr,
                    "message": f"exit {result.returncode}"}
    except subprocess.TimeoutExpired:
        return {"name": name, "status": "TIMEOUT", "message": "120초 초과"}
    except Exception as e:
        return {"name": name, "status": "ERROR", "message": str(e)}


def cmd_list(skills_root: Path, subcmd: str):
    skills = scan_skills_for_subcmd(skills_root, subcmd)
    print(f"# ccbatch list `{subcmd}`\n")
    if not skills:
        print(f"`{subcmd}` 서브명령어를 가진 oo* 스킬이 없습니다.")
        return
    print(f"| # | 스킬 | 스크립트 |")
    print(f"|---|------|---------|")
    for i, s in enumerate(skills, 1):
        print(f"| {i} | `{s['name']}` | {'O' if s['script'] else '-'} |")
    print(f"\n총 {len(skills)}개")


def cmd_run(skills_root: Path, subcmd_args: list[str]):
    subcmd = " ".join(subcmd_args)
    skills = scan_skills_for_subcmd(skills_root, subcmd_args[0])

    print(f"# ccbatch {subcmd}\n")
    if not skills:
        print(f"`{subcmd_args[0]}` 서브명령어를 가진 oo* 스킬이 없습니다.")
        return

    print(f"대상 스킬: {len(skills)}개\n")
    results = []
    for skill in skills:
        print(f"▶ {skill['name']} {subcmd}...", flush=True)
        r = run_skill(skill, subcmd_args)
        results.append(r)
        icon = {"OK": "✅", "SKIP": "⏭", "FAIL": "❌", "TIMEOUT": "⏱", "ERROR": "❌"}.get(r["status"], "?")
        msg = r.get("message", "")
        print(f"  {icon} {r['status']}" + (f": {msg}" if msg else ""))

    ok    = sum(1 for r in results if r["status"] == "OK")
    skip  = sum(1 for r in results if r["status"] == "SKIP")
    fail  = sum(1 for r in results if r["status"] in ("FAIL", "ERROR", "TIMEOUT"))

    print(f"\n## 결과 요약\n")
    print(f"| 상태 | 수 |")
    print(f"|------|---|")
    print(f"| ✅ OK | {ok} |")
    print(f"| ⏭ SKIP | {skip} |")
    print(f"| ❌ FAIL | {fail} |")


def main():
    args = sys.argv[1:]
    if not args or args[0] == "help":
        print("사용법: oobatch_run.py <subcmd> [옵션]")
        print("       oobatch_run.py list <subcmd>")
        print("예:    oobatch_run.py check")
        print("       oobatch_run.py check --fix")
        return

    skills_root = find_skills_root()

    if args[0] == "list" and len(args) > 1:
        cmd_list(skills_root, " ".join(args[1:]))
    else:
        cmd_run(skills_root, args)


if __name__ == "__main__":
    main()
