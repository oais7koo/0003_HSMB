#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oosurvey_run.py - 논문 서베이 및 분석 스크립트 (v07)

선행연구 정리 및 추가 연구 제안 기능 포함
"""

import sys
import sys as _sys
if _sys.stdout.encoding and _sys.stdout.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stdout.reconfigure(encoding='utf-8')
if _sys.stderr.encoding and _sys.stderr.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stderr.reconfigure(encoding='utf-8')
import os
from pathlib import Path
from datetime import datetime

# --- oo_common inline ---
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
PROJECT_ROOT = _SKILLS_DIR.parent.parent
DOC_DIR = PROJECT_ROOT / "00_doc" / "sp00"

# Default paths
DEFAULT_PAPER_DIR = Path(os.getenv("OAIS_PAPER_DIR", "../0002_paper/02_paper"))
DEFAULT_OUTPUT = DOC_DIR / "d0110_survey.md"

SKILL_NAME = "ccsurvey"
SKILL_VERSION = "v07"
SKILL_DOC = ".claude/skills/ccsurvey/SKILL.md"

SUBCOMMANDS = [
    "ccsurvey status",
    "ccsurvey version",
    "ccsurvey list",
    "ccsurvey list --all",
    "ccsurvey list --pending",
    "ccsurvey list --recent N",
    "ccsurvey list --search KEYWORD",
    "ccsurvey run",
    "ccsurvey run --topic TOPIC",
    "ccsurvey run --topic TOPIC --output FILE",
    "ccsurvey run --paper-dir PATH",
    "ccsurvey deeprun",
    "ccsurvey compare",
    "ccsurvey cite --format FORMAT",
    "ccsurvey add FOLDER",
]


def show_help():
    """Show help message."""
    print(f"## {SKILL_NAME}")
    print()
    print("**용도**: 논문 서베이 및 분석, 선행연구 정리, 추가 연구 제안")
    print()
    print("### 서브명령어")
    print()
    for cmd in SUBCOMMANDS:
        print(f"- `{cmd}`")
    print()
    print(f"**상세 문서**: `{SKILL_DOC}`")


def show_version():
    """Show version info."""
    print(f"{SKILL_NAME} version")
    print(f"- 스킬: {SKILL_NAME}")
    print(f"- 버전: {SKILL_VERSION}")
    print(f"- 최종 수정: 2026-02-02")
    print(f"- 설명: 논문 서베이 및 분석, 선행연구 정리, 추가 연구 제안")


def get_paper_dir(args: list) -> Path:
    """Get paper directory from args or env."""
    for i, arg in enumerate(args):
        if arg == "--paper-dir" and i + 1 < len(args):
            return Path(args[i + 1])
    return DEFAULT_PAPER_DIR


def get_topic(args: list) -> str:
    """Get topic from args or PRD."""
    for i, arg in enumerate(args):
        if arg == "--topic" and i + 1 < len(args):
            return args[i + 1]

    # Try to extract from PRD
    prd_path = DOC_DIR / "d0001_prd.md"
    if prd_path.exists():
        content = prd_path.read_text(encoding='utf-8')
        # Simple extraction - look for project name or research topic
        for line in content.split('\n'):
            if '목적' in line or '주제' in line or 'topic' in line.lower():
                return line.split('|')[-1].strip() if '|' in line else ""
    return ""


def get_output_path(args: list) -> Path:
    """Get output file path from args."""
    for i, arg in enumerate(args):
        if arg == "--output" and i + 1 < len(args):
            return Path(args[i + 1])
    return DEFAULT_OUTPUT


def cmd_status(args: list):
    """Show status of paper folder and survey."""
    paper_dir = get_paper_dir(args)
    output_path = get_output_path(args)

    print("# ccsurvey status")
    print()

    # Paper directory status
    print("## 논문 폴더")
    print()

    if paper_dir.is_absolute():
        full_path = paper_dir
    else:
        full_path = PROJECT_ROOT / paper_dir

    if full_path.exists():
        paper_folders = [f for f in full_path.iterdir() if f.is_dir()]
        paper_list_path = full_path / "paper_list.md"

        print(f"| 항목 | 값 |")
        print(f"|------|-----|")
        print(f"| 경로 | `{paper_dir}` |")
        print(f"| 논문 폴더 수 | {len(paper_folders)} |")
        print(f"| paper_list.md | {'O' if paper_list_path.exists() else 'X'} |")
    else:
        log_warn(f"논문 폴더 없음: {paper_dir}")

    print()

    # Survey document status
    print("## 서베이 문서")
    print()

    if output_path.exists():
        stat = output_path.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
        print(f"| 항목 | 값 |")
        print(f"|------|-----|")
        print(f"| 경로 | `{output_path.relative_to(PROJECT_ROOT)}` |")
        print(f"| 최종 수정 | {mtime} |")
        print(f"| 크기 | {stat.st_size:,} bytes |")
    else:
        log_info(f"서베이 문서 없음: {output_path}")


def cmd_list(args: list):
    """List papers in the folder."""
    paper_dir = get_paper_dir(args)

    if paper_dir.is_absolute():
        full_path = paper_dir
    else:
        full_path = PROJECT_ROOT / paper_dir

    print("# ccsurvey list")
    print()
    print(f"논문 폴더: `{paper_dir}`")
    print()

    # Check for paper_list.md first
    paper_list_path = full_path / "paper_list.md"
    if paper_list_path.exists():
        print("**참조**: paper_list.md")
        print()
        content = paper_list_path.read_text(encoding='utf-8')
        # Find and print the table
        in_table = False
        for line in content.split('\n'):
            if '|' in line and ('No.' in line or '폴더ID' in line or '---' in line):
                in_table = True
            if in_table:
                print(line)
                if line.strip() == '' or (line.strip() and '|' not in line):
                    break
        return

    # Scan folder directly
    if not full_path.exists():
        log_error(f"폴더 없음: {full_path}")
        return

    paper_folders = sorted([f for f in full_path.iterdir() if f.is_dir()])

    print(f"| # | 폴더명 | 파일 수 |")
    print(f"|---|--------|--------|")

    for i, folder in enumerate(paper_folders[:20], 1):  # Limit to 20
        files = list(folder.iterdir())
        print(f"| {i} | {folder.name} | {len(files)} |")

    if len(paper_folders) > 20:
        print(f"\n... 외 {len(paper_folders) - 20}개")

    print(f"\n**총 {len(paper_folders)}개 논문 폴더**")


def cmd_run(args: list):
    """Run survey analysis."""
    paper_dir = get_paper_dir(args)
    topic = get_topic(args)
    output_path = get_output_path(args)
    dry_run = "--dry-run" in args

    print("# ccsurvey run")
    print()

    # Resolve paths
    if paper_dir.is_absolute():
        full_paper_path = paper_dir
    else:
        full_paper_path = PROJECT_ROOT / paper_dir

    print("## 설정")
    print()
    print(f"| 항목 | 값 |")
    print(f"|------|-----|")
    print(f"| 논문 폴더 | `{paper_dir}` |")
    print(f"| 연구 주제 | {topic if topic else '(PRD에서 추출 또는 --topic 지정 필요)'} |")
    print(f"| 출력 파일 | `{output_path}` |")
    print(f"| Dry Run | {'O' if dry_run else 'X'} |")
    print()

    if not full_paper_path.exists():
        log_error(f"논문 폴더 없음: {full_paper_path}")
        return

    if not topic:
        log_warn("연구 주제가 지정되지 않았습니다. --topic 옵션을 사용하세요.")
        print()
        print("**예시:**")
        print("```bash")
        print('ccsurvey run --topic "딥러닝 기반 크랙 탐지"')
        print("```")
        return

    # Scan papers
    paper_folders = sorted([f for f in full_paper_path.iterdir() if f.is_dir()])

    print("## 분석 계획")
    print()
    print(f"- 스캔 대상: {len(paper_folders)}개 논문 폴더")
    print(f"- 주제 키워드: `{topic}`")
    print()

    if dry_run:
        print("**[Dry Run]** 실제 분석은 수행되지 않습니다.")
        print()
        print("분석 대상 폴더:")
        for i, folder in enumerate(paper_folders[:10], 1):
            print(f"  {i}. {folder.name}")
        if len(paper_folders) > 10:
            print(f"  ... 외 {len(paper_folders) - 10}개")
        return

    print("## 실행 안내")
    print()
    print("이 명령어는 에이전트가 다음 작업을 수행합니다:")
    print()
    print("1. **논문 폴더 스캔**: 서머리/전문 파일 읽기")
    print("2. **관련성 분석**: 주제 키워드 매칭")
    print("3. **선행연구 정리**: 관련 논문 내용 요약")
    print("4. **추가 연구 제안**: 연구 갭 및 후속 방향 도출")
    print("5. **문서 생성**: 결과를 출력 파일에 저장")
    print()
    print("**에이전트 실행 프롬프트:**")
    print()
    print("```")
    print(f"주제 '{topic}'에 대해 {full_paper_path} 폴더의 논문들을 분석하고,")
    print(f"선행연구 내용을 정리하여 {output_path}에 저장하세요.")
    print("추가 분석이 필요한 논문과 연구 방향도 제안해주세요.")
    print("```")


def cmd_show_checklist():
    """references/checklist.md 내용 출력"""
    checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[{SKILL_NAME}] checklist.md 없음: {checklist_path}")
        return
    print(checklist_path.read_text(encoding="utf-8"))


def main():
    """Main entry point."""
    args = sys.argv[1:]

    if not args:
        args = ["run"]

    cmd = args[0]
    if cmd in ("show",) and len(args) > 1 and args[1].lower() == "checklist":
        cmd_show_checklist()
        return

    if cmd == "status":
        cmd_status(args[1:])
    elif cmd == "version":
        show_version()
    elif cmd == "list":
        cmd_list(args[1:])
    elif cmd == "run":
        cmd_run(args[1:])
    elif cmd in ["deeprun", "compare", "cite", "add"]:
        print(f"# ccsurvey {cmd}")
        print()
        print(f"`{cmd}` 명령어는 에이전트가 직접 수행합니다.")
        print()
        print(f"**상세 가이드**: `{SKILL_DOC}` 섹션 참조")
    elif cmd in ("help", "-h"):
        _print_skill_help("ccsurvey")
    else:
        show_help()


if __name__ == "__main__":
    main()
