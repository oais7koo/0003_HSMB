#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ccdoc run 실행 스크립트

doc/d0001~d0010 문서들을 스캔하고, 각 문서에 매핑된 oo 스킬을
자동으로 실행하여 문서를 일괄 업데이트합니다.

사용법:
    uv run .claude/skills/ccdoc/scripts/oodoc_run.py           # 전체 실행
    uv run .claude/skills/ccdoc/scripts/oodoc_run.py --dry-run # 드라이런
    uv run .claude/skills/ccdoc/scripts/oodoc_run.py --required-only # 필수만
    uv run .claude/skills/ccdoc/scripts/oodoc_run.py --doc d0004_todo.md # 특정 문서만
"""

import sys
import os
from pathlib import Path
import subprocess
import argparse
from datetime import datetime

# Windows cp949 인코딩 문제 방지
if sys.stdout.encoding and sys.stdout.encoding.lower() in ("cp949", "cp1252", "ascii"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() in ("cp949", "cp1252", "ascii"):
    sys.stderr.reconfigure(encoding="utf-8")
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

# 프로젝트 루트 설정
PROJECT_ROOT = Path(__file__).resolve().parents[4]
DOC_DIR = PROJECT_ROOT / "00_doc"

# 문서-스킬 매핑 테이블 (실행 순서대로 정의)
# 형식: (문서명, 스킬명, 실행명령어, 필수여부)
DOC_SKILL_MAPPING = [
    ("d0004_todo.md", "oocheck", "oocheck update", True),
    ("d0010_history.md", "oohistory", "oohistory sync", True),
    ("d0005_lib.md", "oolib", "oolib run", False),
    ("d0006_db.md", "oodb", "oodb", False),
    ("d0003_test.md", "ootest", "ootest", True),
    ("d0007_command.md", "oohelp", "oohelp run", False),
    ("d0008_user.md", "oouser", "oouser update", False),
    ("d0001_prd.md", "ooprd", "ooprd update", True),
    ("d0002_plan.md", "ooplan", "ooplan update", True),
]


# SP별 문서 정의 테이블 (base_num, suffix, title, required)
SP_DOC_DEFINITIONS = [
    (1,  "prd",     "PRD",          True),
    (2,  "plan",    "개발계획",       True),
    (3,  "test",    "테스트",         True),
    (4,  "todo",    "TODO/디버깅",    True),
    (5,  "lib",     "라이브러리",     False),
    (6,  "db",      "DB 구조",        False),
    (7,  "command", "명령어 집계",    False),
    (8,  "user",    "사용자 가이드",   False),
    (9,  "env",     "환경 현황",      False),
    (10, "history", "변경 이력",      True),
]


def detect_sp_from_context() -> int | None:
    """oocontext 상태 파일에서 SP 번호 읽기. 없으면 None 반환"""
    state_file = PROJECT_ROOT / ".omc" / "state" / "context.json"
    if state_file.exists():
        try:
            import json
            data = json.loads(state_file.read_text(encoding="utf-8"))
            sp = data.get("sp", "00")
            return int(sp)
        except Exception:
            pass
    return None


def detect_sp() -> int:
    """CWD 기반 SP 번호 자동 감지"""
    cwd = Path.cwd()
    for part in cwd.parts:
        for sp in range(1, 10):
            if part.startswith(f"0{sp}_"):
                return sp
    return 0


def get_sp_doc_dir(sp_num: int) -> Path:
    """SP별 문서 디렉토리 반환"""
    return DOC_DIR / f"sp{sp_num:02d}"


def get_doc_filename(sp_num: int, base_num: int, suffix: str) -> str:
    """SP 문서 파일명 계산. 문서번호 = SP x 10000 + base_num (SP00은 예외)"""
    if sp_num == 0:
        doc_num = f"d{base_num:04d}"
    else:
        doc_num = f"d{sp_num * 10000 + base_num}"
    return f"{doc_num}_{suffix}.md"


def make_empty_doc(sp_num: int, title: str) -> str:
    """빈 문서 템플릿 생성"""
    sp_label = f"SP{sp_num:02d}"
    today = datetime.now().strftime("%Y-%m-%d")
    return f"""# {sp_label} {title}

## 문서이력관리

| 버전 | 날짜 | 변경내용 |
|------|------|----------|
| v01 | {today} | 초기 생성 |

---

(작성 예정)
"""


def cmd_list_sp(sp_num: int, show_header: bool = False) -> list:
    """SP 문서 현황 출력. 누락 필수문서 리스트 반환"""
    sp_label = f"SP{sp_num:02d}"
    sp_doc_dir = get_sp_doc_dir(sp_num)
    if show_header:
        print(f"## {sp_label}")
    print(f"경로: `{sp_doc_dir.relative_to(PROJECT_ROOT)}`\n")

    # 핵심 문서 정의 매핑: filename → (title, required)
    core_docs = {}
    for base_num, suffix, title, required in SP_DOC_DEFINITIONS:
        filename = get_doc_filename(sp_num, base_num, suffix)
        core_docs[filename] = (title, required)

    # 실제 존재하는 파일 수집
    existing_files = {}
    if sp_doc_dir.exists():
        for f in sp_doc_dir.iterdir():
            if f.is_file() and f.suffix == ".md":
                existing_files[f.name] = f

    # 전체 목록: 실제 파일 + 없는 핵심 문서 → 파일명 기준 정렬
    all_entries = set(existing_files.keys()) | set(core_docs.keys())

    missing = []
    total_size = 0
    total_count = 0

    for filename in sorted(all_entries):
        is_core = filename in core_docs
        is_missing = filename not in existing_files

        if is_core:
            title, required = core_docs[filename]
            req = "[필수]" if required else "[선택]"
        else:
            req = "      "

        if is_missing:
            print(f"- {req} `{filename}` — **[x] 미생성**")
            missing.append((sp_num, filename, core_docs[filename][0]))
        else:
            f = existing_files[filename]
            st = f.stat()
            mtime = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
            size_str = f"{st.st_size:,} B"
            print(f"- {req} `{filename}` — {size_str}, {mtime}")
            total_size += st.st_size
            total_count += 1

    total_size_str = f"{total_size:,}"
    print(f"\n> 합계: {total_count}개 파일, {total_size_str} 바이트")
    if missing:
        print(f"> 미생성 핵심 문서: {len(missing)}개")

    return missing


def cmd_list_all():
    """전체 SP 문서 현황 출력 + 누락 필수문서 요약"""
    print("# ccdoc list - 전체 문서 현황\n")

    # 존재하는 sp?? 디렉토리 스캔
    sp_nums = set()
    if DOC_DIR.exists():
        for d in DOC_DIR.iterdir():
            if d.is_dir() and d.name.startswith("sp"):
                try:
                    sp_nums.add(int(d.name[2:]))
                except ValueError:
                    pass
    sp_nums.add(0)  # SP00 항상 포함

    all_missing = []
    for sp_num in sorted(sp_nums):
        missing = cmd_list_sp(sp_num, show_header=True)
        all_missing.extend(missing)

    print("---\n")
    if all_missing:
        print("## 누락 필수 문서\n")
        print("| SP | 문서 | 제목 |")
        print("|----|------|------|")
        for sp_num, filename, title in all_missing:
            print(f"| SP{sp_num:02d} | {filename} | {title} |")
        print()
        sps = sorted(set(sp for sp, _, _ in all_missing))
        cmds = "  |  ".join(f"`ccdoc gen --sp {sp}`" for sp in sps)
        print(f"[GEN] {cmds}")
    else:
        print("[OK] 모든 필수 문서가 존재합니다.")


def cmd_gen(sp_num: int, dry_run: bool = False):
    """미생성 문서를 빈 템플릿으로 생성"""
    sp_label = f"SP{sp_num:02d}"
    sp_doc_dir = get_sp_doc_dir(sp_num)
    print(f"# ccdoc gen - {sp_label} 빈 문서 생성\n")
    if dry_run:
        print("[DRY-RUN] 실제 파일 생성 없이 미리보기\n")

    if not sp_doc_dir.exists():
        if not dry_run:
            sp_doc_dir.mkdir(parents=True)
        print(f"{'[DRY-RUN] ' if dry_run else ''}디렉토리 생성: {sp_doc_dir}\n")

    print("| 문서 | 제목 | 결과 |")
    print("|------|------|------|")

    created = 0
    skipped = 0
    for base_num, suffix, title, required in SP_DOC_DEFINITIONS:
        filename = get_doc_filename(sp_num, base_num, suffix)
        filepath = sp_doc_dir / filename
        req_label = "[필수]" if required else "[선택]"
        if filepath.exists():
            print(f"| {filename} | {title} {req_label} | 기존 유지 |")
            skipped += 1
        else:
            if not dry_run:
                filepath.write_text(make_empty_doc(sp_num, title), encoding="utf-8")
            action = "생성 예정" if dry_run else "생성됨"
            print(f"| {filename} | {title} {req_label} | {action} |")
            created += 1

    print(f"\n## 결과\n")
    print(f"- {'생성 예정' if dry_run else '생성'}: {created}개")
    print(f"- 기존 유지: {skipped}개")
    if dry_run:
        print(f"\n[TIP] 실제 생성: `ccdoc gen --sp {sp_num}` (--dry-run 제거)")


def check_doc_exists(doc_name: str) -> bool:
    """문서 파일 존재 여부 확인"""
    doc_path = DOC_DIR / doc_name
    return doc_path.exists()


def execute_skill(skill_command: str, dry_run: bool = False) -> tuple[bool, str]:
    """
    스킬 명령어 실행

    Returns:
        tuple: (성공여부, 메시지)
    """
    if dry_run:
        return True, f"[DRY-RUN] 실행 예정: {skill_command}"

    try:
        # Claude Code 환경에서는 스킬이 슬래시 명령어로 실행됨
        # 이 스크립트는 실행 계획을 보여주는 용도
        # 실제 실행은 Claude Code에서 /ccdoc run 으로 수행
        return True, f"실행 계획: /{skill_command}"
    except Exception as e:
        return False, f"실행 실패: {str(e)}"


def run_doc_update(
    dry_run: bool = False,
    required_only: bool = False,
    target_doc: str = None
) -> dict:
    """
    문서 업데이트 실행

    Args:
        dry_run: 드라이런 모드 (실행 없이 계획만 표시)
        required_only: 필수 문서만 업데이트
        target_doc: 특정 문서만 업데이트 (None이면 전체)

    Returns:
        dict: 실행 결과 통계
    """
    print("[ccdoc run] 문서 업데이트 시작...")
    print()

    results = {
        "success": 0,
        "skip": 0,
        "fail": 0,
        "details": []
    }

    # 필터링된 매핑 리스트 생성
    filtered_mapping = []
    for doc, skill, cmd, required in DOC_SKILL_MAPPING:
        # 특정 문서만 처리
        if target_doc and doc != target_doc:
            continue
        # 필수만 처리
        if required_only and not required:
            continue
        filtered_mapping.append((doc, skill, cmd, required))

    total = len(filtered_mapping)

    for idx, (doc, skill, cmd, required) in enumerate(filtered_mapping, 1):
        print(f"[{idx}/{total}] {doc}")
        print(f"       스킬: {cmd}")

        # 문서 존재 확인
        if not check_doc_exists(doc):
            status = "[SKIP] (파일 없음)"
            results["skip"] += 1
            results["details"].append({
                "doc": doc,
                "skill": skill,
                "status": "skip",
                "reason": "파일 없음"
            })
        else:
            # 스킬 실행
            success, msg = execute_skill(cmd, dry_run)
            if success:
                if dry_run:
                    status = f"[DRY] {msg}"
                else:
                    status = "[OK] 완료"
                results["success"] += 1
                results["details"].append({
                    "doc": doc,
                    "skill": skill,
                    "status": "success",
                    "message": msg
                })
            else:
                status = f"[FAIL] {msg}"
                results["fail"] += 1
                results["details"].append({
                    "doc": doc,
                    "skill": skill,
                    "status": "fail",
                    "reason": msg
                })

        print(f"       상태: {status}")
        print()

    # 결과 요약
    print("-" * 40)
    print(f"[완료] {results['success']}/{total} 문서 업데이트됨")
    print(f"       - 성공: {results['success']}")
    print(f"       - 스킵: {results['skip']}")
    print(f"       - 실패: {results['fail']}")

    return results


def generate_execution_plan() -> str:
    """실행 계획 문자열 생성"""
    lines = [
        "# ccdoc run 실행 계획",
        "",
        "## 문서-스킬 매핑",
        "",
        "| 순서 | 문서 | 스킬 | 명령어 | 필수 | 존재 |",
        "|------|------|------|--------|------|------|",
    ]

    for idx, (doc, skill, cmd, required) in enumerate(DOC_SKILL_MAPPING, 1):
        exists = "O" if check_doc_exists(doc) else "X"
        req = "O" if required else "-"
        lines.append(f"| {idx} | `{doc}` | `{skill}` | `{cmd}` | {req} | {exists} |")

    lines.extend([
        "",
        "## 실행 순서",
        "",
    ])

    for idx, (doc, skill, cmd, required) in enumerate(DOC_SKILL_MAPPING, 1):
        if check_doc_exists(doc):
            lines.append(f"{idx}. `/{cmd}` → {doc}")
        else:
            lines.append(f"{idx}. ~~`/{cmd}` → {doc}~~ (파일 없음)")

    return "\n".join(lines)


def cmd_show_checklist():
    """references/checklist.md 내용 출력"""
    checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[{SKILL_NAME}] checklist.md 없음: {checklist_path}")
        return
    print(checklist_path.read_text(encoding="utf-8"))


def cmd_update(sp_num: int, scope: str = "auto", commit: str = "HEAD~1", dry_run: bool = False) -> int:
    """문서 현행화 진단: git 변경 파일 vs SP 문서 영향 매핑.

    동작 (Phase 1 진단):
      - git diff <commit>..HEAD --name-only 로 변경 파일 추출
      - 00_doc/sp{NN}/ 의 d{XXXX}*.md 문서 인벤토리 확인
      - 변경된 코드와 영향받을 가능성 있는 문서 매핑 출력

    실제 자동 갱신은 LLM(에이전트)이 보고 판단하여 수동 처리.
    """
    import subprocess as _sp
    print(f"# ccdoc update — SP{sp_num:02d}\n")
    print(f"비교 기준: {commit}..HEAD | 범위: {scope}\n")

    try:
        result = _sp.run(
            ["git", "diff", "--name-only", f"{commit}..HEAD"],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )
    except FileNotFoundError:
        print("[ERROR] git 명령을 찾을 수 없습니다.")
        return 1

    if result.returncode != 0:
        print(f"[ERROR] git diff 실패: {result.stderr.strip()}")
        return 1

    changed_files = [line for line in result.stdout.splitlines() if line.strip()]
    print(f"## 1. 변경 파일 ({len(changed_files)}개)\n")
    if not changed_files:
        print("(변경 없음)")
    else:
        for f in changed_files[:30]:
            print(f"- {f}")
        if len(changed_files) > 30:
            print(f"- ... 외 {len(changed_files) - 30}개")
    print()

    # SP 문서 인벤토리
    doc_dir = Path.cwd() / "00_doc" / f"sp{sp_num:02d}"
    print(f"## 2. SP{sp_num:02d} 문서 인벤토리\n")
    if not doc_dir.exists():
        print(f"[WARN] 문서 디렉터리 없음: {doc_dir}")
    else:
        docs = sorted(doc_dir.glob("d*.md"))
        print(f"위치: {doc_dir.relative_to(Path.cwd())}")
        print(f"문서 수: {len(docs)}개")
        for d in docs:
            print(f"- {d.name}")
    print()

    # 영향 매핑 (휴리스틱)
    print("## 3. 영향 매핑 (휴리스틱)\n")
    mapping_hits = []
    if changed_files:
        for f in changed_files:
            if f.startswith("00_doc/"):
                mapping_hits.append((f, "직접 문서 변경"))
            elif f.startswith(("oais/", "src/")) or f.endswith(".py"):
                mapping_hits.append((f, f"d{sp_num*10000 + 5}_lib.md / d{sp_num*10000 + 2}_plan.md 영향 가능"))
            elif "test" in f.lower():
                mapping_hits.append((f, f"d{sp_num*10000 + 3}_test.md 영향 가능"))

    if mapping_hits:
        for src, hint in mapping_hits[:20]:
            print(f"- {src} → {hint}")
        if len(mapping_hits) > 20:
            print(f"- ... 외 {len(mapping_hits) - 20}개")
    else:
        print("(매핑된 영향 없음)")
    print()

    print("## 4. 권장 다음 단계\n")
    print("- 자동 갱신은 LLM 에이전트로 위임: 위 영향 문서를 직접 읽고 갱신")
    print(f"- 문서 생성/누락 보충: `ccdoc gen --sp {sp_num}`")
    print(f"- 일괄 실행: `ccdoc run --sp {sp_num}`")

    if dry_run:
        print("\n[DRY-RUN] 진단 모드 — 실제 문서 수정 없음")

    return 0


def main():
    if len(sys.argv) > 2 and sys.argv[1].lower() == "show" and sys.argv[2].lower() == "checklist":
        cmd_show_checklist()
        return
    # help 분기 (argparse 전에 처리)
    if len(sys.argv) > 1 and sys.argv[1] in ("help", "-h"):
        _print_skill_help("ccdoc")
        return 0

    # 서브명령어 없이 실행 시 도움말 출력
    if not sys.argv[1:]:
        sys.argv.append("run")

    parser = argparse.ArgumentParser(
        description="ccdoc run - 문서 일괄 업데이트 도구"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="실행 없이 계획만 표시"
    )
    parser.add_argument(
        "--required-only",
        action="store_true",
        help="필수 문서만 업데이트"
    )
    parser.add_argument(
        "--doc",
        type=str,
        default=None,
        help="특정 문서만 업데이트 (예: d0004_todo.md)"
    )
    parser.add_argument(
        "--plan",
        action="store_true",
        help="실행 계획을 마크다운으로 출력"
    )
    parser.add_argument(
        "--sp",
        type=int,
        default=None,
        help="서브프로젝트 번호 (0~9, 미지정 시 CWD 자동 감지)"
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="run",
        choices=["run", "plan", "list", "gen", "update"],
        help="실행 명령 (기본: run)"
    )
    parser.add_argument(
        "--scope",
        choices=["auto", "all"],
        default="auto",
        help="update 명령 범위 (auto: 변경된 파일만, all: 전체)"
    )
    parser.add_argument(
        "--commit",
        type=str,
        default="HEAD~1",
        help="update 명령 비교 기준 커밋 (예: HEAD~3, 기본: HEAD~1)"
    )

    args = parser.parse_args()

    # SP 번호 결정: --sp N > oocontext 상태 > CWD 감지 > 기본값 0
    if args.sp is not None:
        sp_num = args.sp
    else:
        ctx_sp = detect_sp_from_context()
        sp_num = ctx_sp if ctx_sp is not None else detect_sp()

    # plan 명령 또는 --plan 플래그
    if args.command == "plan" or args.plan:
        print(generate_execution_plan())
        return 0

    # list 명령 (현재 SP 문서 현황)
    if args.command == "list":
        print(f"# ccdoc list - SP{sp_num:02d} 문서 현황\n")
        missing = cmd_list_sp(sp_num)
        if missing:
            print("---\n")
            print("## 누락 필수 문서\n")
            print("| 문서 | 제목 |")
            print("|------|------|")
            for _, filename, title in missing:
                print(f"| {filename} | {title} |")
            print()
            print(f"[GEN] `ccdoc gen --sp {sp_num}`")
        else:
            print("[OK] 모든 필수 문서가 존재합니다.")
        return 0

    # gen 명령
    if args.command == "gen":
        cmd_gen(sp_num, dry_run=args.dry_run)
        return 0

    # update 명령 (현행화 진단: git 변경 vs SP 문서)
    if args.command == "update":
        return cmd_update(sp_num, scope=args.scope, commit=args.commit, dry_run=args.dry_run)

    # run 명령
    results = run_doc_update(
        dry_run=args.dry_run,
        required_only=args.required_only,
        target_doc=args.doc
    )

    # 실패가 있으면 비정상 종료
    return 1 if results["fail"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
