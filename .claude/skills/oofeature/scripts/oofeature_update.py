#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
oofeature_update.py
plan.md 변경 기반 상세 문서 영향 분석 및 단계 롤백

사용법:
    uv run python .claude/skills/oofeature/scripts/oofeature_update.py [--sp N] [--dry-run] [--apply]

옵션:
    --from-plan    plan.md 변경 기반 분석 (기본 동작)
    --sp N         특정 SP 지정 (기본: 현재 oocontext SP)
    --dry-run      분석만, 실제 수정 없음 (기본값)
    --apply        실제 파일 rename 실행
"""

import sys
import re
import subprocess
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
DOC_DIR = PROJECT_ROOT / "00_doc"
_SKILLS_DIR = Path(__file__).parent.parent.parent  # .claude/skills/
STATE_FILE = PROJECT_ROOT / ".omc" / "state" / "context.json"

STAGES = ["기획", "설계", "구현", "검증"]
STAGE_ICON = {"기획": "⚪", "설계": "🔵", "구현": "🟡", "검증": "🟢"}
FILE_PATTERN = re.compile(r'^(d\d{5,})_상세(기획|설계|구현|검증)_(.+)\.md$')
DOC_NUM_RE = re.compile(r'd\d{5,}')


def get_current_sp() -> str:
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            return data.get("sp", "00")
        except Exception:
            pass
    return "00"


def get_sp_folder(sp: str) -> str:
    return f"sp{int(sp):02d}"


def find_plan_path(sp: str) -> Path:
    sp_num = int(sp)
    doc_num = sp_num * 10000 + 2
    return DOC_DIR / get_sp_folder(sp) / f"d{doc_num:05d}_plan.md"


def get_plan_changed_doc_nums(plan_path: Path) -> tuple[set, bool]:
    """
    git diff로 plan.md 변경된 줄에서 doc 번호 추출.
    Returns (changed_doc_nums: set, has_diff: bool)
    """
    def _run_diff(extra_args):
        try:
            result = subprocess.run(
                ["git", "-C", str(PROJECT_ROOT), "diff"] + extra_args + ["--", str(plan_path)],
                capture_output=True, text=True, encoding="utf-8", errors="replace"
            )
            return result.stdout
        except Exception:
            return ""

    # 워킹트리 변경 먼저, 없으면 staged 확인
    diff = _run_diff(["HEAD"])
    if not diff.strip():
        diff = _run_diff(["--cached"])

    if not diff.strip():
        return set(), False

    # 추가/변경된 줄('+' 시작)에서 doc 번호만 추출
    changed_nums: set[str] = set()
    for line in diff.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            changed_nums.update(DOC_NUM_RE.findall(line))

    return changed_nums, True


def scan_detail_docs(sp: str) -> list[tuple]:
    """SP 폴더의 상세 문서 목록 반환 [(path, doc_num, stage, func_name), ...]"""
    sp_dir = DOC_DIR / get_sp_folder(sp)
    if not sp_dir.exists():
        return []
    docs = []
    for f in sorted(sp_dir.iterdir()):
        if not f.is_file() or not f.name.endswith(".md"):
            continue
        m = FILE_PATTERN.match(f.name)
        if m:
            docs.append((f, m.group(1), m.group(2), m.group(3)))
    return docs


def prev_stage(stage: str) -> str | None:
    idx = STAGES.index(stage)
    return STAGES[idx - 1] if idx > 0 else None


def do_rollback(doc_path: Path, doc_num: str, from_stage: str, func_name: str, dry_run: bool) -> bool:
    """파일명을 이전 단계로 rename"""
    to_stage = prev_stage(from_stage)
    if not to_stage:
        return False
    new_name = f"{doc_num}_상세{to_stage}_{func_name}.md"
    new_path = doc_path.parent / new_name

    if dry_run:
        print(f"  [DRY-RUN] {doc_path.name}")
        print(f"           → {new_name}")
        return True

    if new_path.exists():
        print(f"  [ERROR] 대상 파일 이미 존재: {new_name}")
        return False

    doc_path.rename(new_path)
    print(f"  [OK] {doc_path.name}")
    print(f"     → {new_name}")
    return True


def run_from_plan(sp: str, dry_run: bool, apply: bool):
    plan_path = find_plan_path(sp)

    print(f"[oofeature update --from-plan] SP{int(sp):02d}")
    print()

    if not plan_path.exists():
        print(f"[ERROR] plan.md 없음: {plan_path.relative_to(PROJECT_ROOT)}")
        return

    # 1. plan.md 변경 감지
    changed_nums, has_diff = get_plan_changed_doc_nums(plan_path)

    if not has_diff:
        print(f"plan.md 변경 없음 (git diff 기준): {plan_path.name}")
        print()
        print("※ 전체 활성 상세 문서 현황을 표시합니다 (--apply로 수동 롤백 가능):")
        changed_nums = None  # None = 전체 표시 모드
    else:
        print(f"plan.md 변경 감지 → 영향 doc번호: {', '.join(sorted(changed_nums)) if changed_nums else '(없음)'}")

    print()

    # 2. 상세 문서 스캔
    docs = scan_detail_docs(sp)
    if not docs:
        print(f"상세 문서 없음: 00_doc/sp{int(sp):02d}/")
        return

    # 3. 영향 분석
    affected: list[tuple] = []   # (path, doc_num, stage, func_name, action)
    safe: list[tuple] = []       # 영향 없거나 기획 단계 문서

    for doc_path, doc_num, stage, func_name in docs:
        if changed_nums is None:
            # 전체 표시 모드: 설계/구현/검증만 후보
            if stage in ("설계", "구현", "검증"):
                affected.append((doc_path, doc_num, stage, func_name, "검토필요"))
            else:
                safe.append((doc_path, doc_num, stage, func_name))
        else:
            if doc_num in changed_nums and stage in ("설계", "구현", "검증"):
                affected.append((doc_path, doc_num, stage, func_name, "롤백권장"))
            else:
                safe.append((doc_path, doc_num, stage, func_name))

    # 4. 결과 출력
    if not affected:
        print("영향받는 활성 상세 문서 없음.")
        return

    print(f"## 영향 문서 ({len(affected)}개, 롤백 후보)")
    print()
    print("| 문서번호 | 기능명 | 현재단계 | 롤백→ | 권장조치 |")
    print("|---------|--------|:-------:|:-----:|---------|")

    for doc_path, doc_num, stage, func_name, action in affected:
        to_stage = prev_stage(stage) or "-"
        icon = STAGE_ICON.get(stage, "")
        print(f"| {doc_num} | {func_name} | {icon}{stage} | {to_stage} | {action} |")

    print()

    if not apply:
        hint = " --dry-run" if dry_run else ""
        print(f"실제 롤백을 수행하려면 --apply 옵션을 추가하세요:")
        print(f"  oofeature update --from-plan --apply{hint} --sp {sp}")
        return

    # 5. 실제 롤백 (--apply)
    print(f"## 롤백 실행{'  [DRY-RUN]' if dry_run else ''}")
    print()

    success = 0
    for doc_path, doc_num, stage, func_name, _ in affected:
        if not prev_stage(stage):
            print(f"  [SKIP] {doc_num} ({stage}) — 이전 단계 없음")
            continue
        if do_rollback(doc_path, doc_num, stage, func_name, dry_run):
            success += 1

    print()
    print(f"완료: {success}/{len(affected)}개 롤백{'(DRY-RUN)' if dry_run else ''}")

    if success > 0 and not dry_run:
        print()
        print("다음 단계:")
        print("  1. 롤백된 상세 문서 내용 검토 및 수정")
        print("  2. oodev run dXXXX  → 재구현")
        print("  3. ooplan sync      → plan.md 8.2절 갱신")


def get_changed_files() -> list[str]:
    """git diff로 변경된 파일 목록 반환 (워킹트리 우선, 없으면 staged)"""
    def _run(extra_args):
        try:
            result = subprocess.run(
                ["git", "-C", str(PROJECT_ROOT), "diff"] + extra_args + ["--name-only"],
                capture_output=True, text=True, encoding="utf-8", errors="replace"
            )
            return result.stdout.strip().splitlines()
        except Exception:
            return []

    files = _run(["HEAD"])
    return files if files else _run(["--cached"])


def run_oocheck(doc_num: str) -> tuple[bool, str]:
    """oocheck run dXXXX 실행. Returns (has_issues: bool, output: str)"""
    oocheck_script = _SKILLS_DIR / "oocheck" / "scripts" / "oocheck_run.py"
    if not oocheck_script.exists():
        return False, "[WARN] oocheck_run.py 없음 — 체크 생략"
    try:
        result = subprocess.run(
            [sys.executable, str(oocheck_script), "run", doc_num],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(PROJECT_ROOT)
        )
        output = result.stdout + (result.stderr or "")
        has_issues = bool(re.search(r'\[CRITICAL\]|\[ERROR\]', output))
        return has_issues, output
    except Exception as e:
        return False, f"[ERROR] oocheck 실행 실패: {e}"


def run_from_doc(sp: str, dry_run: bool, apply: bool, skip_check: bool = False):
    """상세구현 단계 문서 변경 감지 → oocheck 자동 실행 → 이슈 발견 시 기획 단계 롤백 제안"""
    print(f"[oofeature update --from-doc] SP{int(sp):02d}")
    if skip_check:
        print("(--skip-check: oocheck 생략 모드)")
    print()

    # 1. 변경된 파일 목록
    changed = get_changed_files()
    if not changed:
        print("변경된 파일 없음 (git diff 기준)")
        return

    # 2. SP 폴더 내 상세구현 단계 문서만 필터
    sp_folder = get_sp_folder(sp)
    candidates: list[tuple] = []

    for rel_path in changed:
        p = Path(rel_path.replace("\\", "/"))
        parts = p.parts
        if len(parts) < 3:
            continue
        if parts[0] != "00_doc" or parts[1] != sp_folder:
            continue
        m = FILE_PATTERN.match(p.name)
        if not m:
            continue
        doc_num, stage, func_name = m.group(1), m.group(2), m.group(3)
        if stage != "구현":  # 구현 단계만 대상
            continue
        abs_path = PROJECT_ROOT / p
        if abs_path.exists():
            candidates.append((abs_path, doc_num, stage, func_name))

    if not candidates:
        print("대상 없음: 변경된 상세구현 단계 문서 없음")
        return

    print(f"## 변경 감지된 상세구현 문서 ({len(candidates)}개)")
    for _, doc_num, _, func_name in candidates:
        print(f"  - {doc_num} ({func_name})")
    print()

    # 3. --skip-check이면 바로 롤백 후보로 처리
    if skip_check:
        affected = candidates
    else:
        # 4. oocheck 실행 → 이슈 있는 문서만 롤백 대상
        affected = []
        for doc_path, doc_num, stage, func_name in candidates:
            print(f"oocheck run {doc_num} 실행 중...")
            has_issues, output = run_oocheck(doc_num)
            lines = output.strip().splitlines()
            for line in lines[-8:]:
                print(f"  {line}")
            print()
            if has_issues:
                affected.append((doc_path, doc_num, stage, func_name))
                print(f"  → [CRITICAL/ERROR] 이슈 발견 → 기획 롤백 대상")
            else:
                print(f"  → 이슈 없음 → 롤백 불필요")
            print()

    if not affected:
        print("기획 롤백 대상 없음 (이슈 미발견)")
        return

    # 5. 롤백 후보 표시
    print(f"## 기획 롤백 후보 ({len(affected)}개)")
    print()
    print("| 문서번호 | 기능명 | 현재단계 | 롤백→ |")
    print("|---------|--------|:-------:|:-----:|")
    for _, doc_num, stage, func_name in affected:
        icon = STAGE_ICON.get(stage, "")
        print(f"| {doc_num} | {func_name} | {icon}{stage} | ⚪기획 |")
    print()

    if not apply:
        skip_arg = " --skip-check" if skip_check else ""
        print(f"실제 롤백을 수행하려면 --apply 옵션을 추가하세요:")
        print(f"  oofeature update --from-doc --apply{skip_arg} --sp {sp}")
        return

    # 6. 기획 단계로 롤백
    print(f"## 롤백 실행{'  [DRY-RUN]' if dry_run else ''}")
    print()

    success = 0
    for doc_path, doc_num, stage, func_name in affected:
        new_name = f"{doc_num}_상세기획_{func_name}.md"
        new_path = doc_path.parent / new_name

        if dry_run:
            print(f"  [DRY-RUN] {doc_path.name}")
            print(f"           → {new_name}")
            success += 1
            continue

        if new_path.exists():
            print(f"  [ERROR] 대상 파일 이미 존재: {new_name}")
            continue

        doc_path.rename(new_path)
        print(f"  [OK] {doc_path.name}")
        print(f"     → {new_name}")
        success += 1

    print()
    print(f"완료: {success}/{len(affected)}개 롤백{'(DRY-RUN)' if dry_run else ''}")

    if success > 0 and not dry_run:
        print()
        print("다음 단계:")
        print("  1. 기획 내용 검토 및 보완")
        print("  2. oofeature next dXXXX  → 기획→설계 재전환")
        print("  3. ooplan sync           → plan.md 8.2절 갱신")


def run_auto(sp: str, dry_run: bool, apply: bool):
    """통합 변경 감지 → oocheck 검토 → 상세기획으로 롤백
    - plan.md 변경: 영향 doc 무조건 롤백 (계획이 바뀌면 재기획 필요)
    - 상세 문서 변경: oocheck 실행 → CRITICAL/ERROR 있을 때만 롤백
    """
    print(f"[oofeature update] SP{int(sp):02d}")
    print()

    affected: dict[str, tuple] = {}  # doc_num → (path, stage, func_name, reason)

    # 1. plan.md 변경에서 영향 doc 번호 추출 → 무조건 롤백 대상
    plan_path = find_plan_path(sp)
    if plan_path.exists():
        plan_nums, has_diff = get_plan_changed_doc_nums(plan_path)
        if has_diff and plan_nums:
            print(f"plan.md 변경 감지 → 영향 doc: {', '.join(sorted(plan_nums))}")
            all_docs = scan_detail_docs(sp)
            for doc_path, doc_num, stage, func_name in all_docs:
                if doc_num in plan_nums and stage != "기획":
                    affected[doc_num] = (doc_path, stage, func_name, "plan 변경")

    # 2. 변경된 상세 문서 감지 → oocheck 실행 → 이슈 있는 것만 롤백 대상
    changed_files = get_changed_files()
    sp_folder = get_sp_folder(sp)
    doc_candidates: list[tuple] = []

    for rel_path in changed_files:
        p = Path(rel_path.replace("\\", "/"))
        if len(p.parts) < 3:
            continue
        if p.parts[0] != "00_doc" or p.parts[1] != sp_folder:
            continue
        m = FILE_PATTERN.match(p.name)
        if not m:
            continue
        doc_num, stage, func_name = m.group(1), m.group(2), m.group(3)
        if stage == "기획":
            continue
        abs_path = PROJECT_ROOT / p
        if abs_path.exists() and doc_num not in affected:
            doc_candidates.append((abs_path, doc_num, stage, func_name))

    if doc_candidates:
        print(f"상세 문서 변경 감지 → {len(doc_candidates)}개 oocheck 실행 중...")
        print()
        for doc_path, doc_num, stage, func_name in doc_candidates:
            print(f"  oocheck run {doc_num} ({func_name}) ...")
            has_issues, output = run_oocheck(doc_num)
            lines = output.strip().splitlines()
            for line in lines[-6:]:
                print(f"    {line}")
            if has_issues:
                affected[doc_num] = (doc_path, stage, func_name, "코드 이슈")
                print(f"  → [CRITICAL/ERROR] 발견 → 롤백 대상")
            else:
                print(f"  → 이슈 없음 → 롤백 불필요")
            print()

    if not affected:
        print("변경된 상세 문서 없음 — 롤백 불필요")
        return

    print()

    # 3. 롤백 후보 표시
    print(f"## 상세기획 롤백 후보 ({len(affected)}개)")
    print()
    print("| 문서번호 | 기능명 | 현재단계 | 롤백→ | 사유 |")
    print("|---------|--------|:-------:|:-----:|------|")
    for doc_num, (doc_path, stage, func_name, reason) in sorted(affected.items()):
        icon = STAGE_ICON.get(stage, "")
        print(f"| {doc_num} | {func_name} | {icon}{stage} | ⚪기획 | {reason} |")
    print()

    if not apply:
        dry_str = " --dry" if dry_run else ""
        print("실제 롤백을 수행하려면 --apply 옵션을 추가하세요:")
        print(f"  oofeature update --apply{dry_str}")
        return

    # 4. 롤백 실행 (모두 상세기획으로)
    print(f"## 롤백 실행{'  [DRY-RUN]' if dry_run else ''}")
    print()

    success = 0
    for doc_num, (doc_path, stage, func_name, reason) in sorted(affected.items()):
        new_name = f"{doc_num}_상세기획_{func_name}.md"
        new_path = doc_path.parent / new_name

        if dry_run:
            print(f"  [DRY-RUN] {doc_path.name}")
            print(f"           → {new_name}")
            success += 1
            continue

        if new_path.exists():
            print(f"  [ERROR] 대상 파일 이미 존재: {new_name}")
            continue

        doc_path.rename(new_path)
        print(f"  [OK] {doc_path.name}")
        print(f"     → {new_name}")
        success += 1

    print()
    print(f"완료: {success}/{len(affected)}개 롤백{'(DRY-RUN)' if dry_run else ''}")

    if success > 0 and not dry_run:
        print()
        print("다음 단계:")
        print("  1. 상세기획 내용 검토 및 보완")
        print("  2. oofeature next dXXXX  → 기획→설계 재전환")
        print("  3. ooplan sync           → plan.md 8.2절 갱신")


def main():
    args = sys.argv[1:]

    sp = None
    dry_run = "--dry-run" in args or "--dry" in args
    apply = "--apply" in args or "--force" in args

    for i, a in enumerate(args):
        if a == "--sp" and i + 1 < len(args):
            sp = args[i + 1].zfill(2)

    if sp is None:
        sp = get_current_sp()

    skip_check = "--skip-check" in args

    # 기존 명시적 플래그 (하위 호환)
    if "--from-doc" in args:
        run_from_doc(sp, dry_run=dry_run, apply=apply, skip_check=skip_check)
    elif "--from-plan" in args:
        run_from_plan(sp, dry_run=dry_run, apply=apply)
    else:
        # 통합 자동 감지 모드 (신규 기본)
        run_auto(sp, dry_run=dry_run, apply=apply)


if __name__ == "__main__":
    main()
