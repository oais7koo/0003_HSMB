#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
oofeature_update.py
plan.md 변경 기반 상세 문서 영향 분석 및 단계 롤백

사용법:
    uv run python .agents/skills/ccfeature/scripts/oofeature_update.py [--sp N] [--dry-run] [--apply]

옵션:
    --from-plan    plan.md 변경 기반 분석 (기본 동작)
    --sp N         특정 SP 지정 (기본: 현재 cccontext SP)
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
_SKILLS_DIR = Path(__file__).parent.parent.parent  # .agents/skills/
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

    print(f"[ccfeature update --from-plan] SP{int(sp):02d}")
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
        print(f"  ccfeature update --from-plan --apply{hint} --sp {sp}")
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
        print("  2. ccdev run dXXXX  → 재구현")
        print("  3. ccplan sync      → plan.md 8.2절 갱신")


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
    """cccheck run dXXXX 실행. Returns (has_issues: bool, output: str)"""
    oocheck_script = _SKILLS_DIR / "cccheck" / "scripts" / "oocheck_run.py"
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
        return False, f"[ERROR] cccheck 실행 실패: {e}"


def run_from_doc(sp: str, dry_run: bool, apply: bool, skip_check: bool = False):
    """상세구현 단계 문서 변경 감지 → cccheck 자동 실행 → 이슈 발견 시 기획 단계 롤백 제안"""
    print(f"[ccfeature update --from-doc] SP{int(sp):02d}")
    if skip_check:
        print("(--skip-check: cccheck 생략 모드)")
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
        # 4. cccheck 실행 → 이슈 있는 문서만 롤백 대상
        affected = []
        for doc_path, doc_num, stage, func_name in candidates:
            print(f"cccheck run {doc_num} 실행 중...")
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
        print(f"  ccfeature update --from-doc --apply{skip_arg} --sp {sp}")
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
        print("  2. ccfeature next dXXXX  → 기획→설계 재전환")
        print("  3. ccplan sync           → plan.md 8.2절 갱신")


# --- 코드파일 vs 상세 문서 교차검사 (인라인) ---
_SP04_EXCLUDE = {"__init__.py", "youtube_collector.py"}
_SP04_EXCLUDE_SUFFIX = "===.py"
_SP05_EXCLUDE = {"__init__.py", "router.py"}
_SP05_FILE_KEYWORDS: dict[str, list[str]] = {
    "auth.py":          ["사용자API", "인증", "로그인", "토큰"],
    "users.py":         ["사용자", "user"],
    "news.py":          ["뉴스API", "뉴스"],
    "notices.py":       ["공지사항API", "공지사항"],
    "koreapeople.py":   ["대한노인회", "koreapeople"],
    "welfare.py":       ["복지API", "복지"],
    "jobs.py":          ["일자리API", "일자리"],
    "bookmarks.py":     ["북마크API", "북마크"],
    "comments.py":      ["댓글API", "댓글"],
    "search.py":        ["통합검색API", "검색API", "검색"],
    "likes.py":         ["좋아요API", "좋아요"],
    "hospitals.py":     ["병원API", "병원"],
    "drugstores.py":    ["약국API", "약국"],
    "data_versions.py": ["데이터버전API", "데이터버전", "data_version"],
    "districts.py":     ["행정구역API", "행정구역"],
    "medical.py":       ["의료API", "시니어의료API", "의료"],
    "events.py":        ["이벤트API", "이벤트"],
    "faq.py":           ["FAQAPI", "FAQ"],
    "inquiry.py":       ["문의API", "문의"],
    "health.py":        ["건강정보API", "건강API", "건강"],
}


def _get_doc_names(sp: str) -> list[str]:
    sp_folder = DOC_DIR / f"sp{int(sp):02d}"
    if not sp_folder.exists():
        return []
    pattern = re.compile(r"^d\d+_상세(기획|설계|구현|검증|완료)_.+\.md$")
    return [f.name for f in sp_folder.iterdir() if pattern.match(f.name)]


def _has_doc(keywords: list[str], doc_names: list[str]) -> bool:
    expanded = list(keywords)
    for kw in keywords:
        for i in range(1, len(kw) - 1):
            sub = kw[i:]
            if len(sub) >= 3:
                expanded.append(sub)
    return any(kw in doc for kw in expanded for doc in doc_names)


def _check_sp04(doc_names: list[str]) -> list[dict]:
    pages_dir = PROJECT_ROOT / "04_backoffice" / "pages"
    if not pages_dir.exists():
        return []
    missing = []
    for py_file in sorted(pages_dir.glob("*.py")):
        name = py_file.name
        if name in _SP04_EXCLUDE or name.endswith(_SP04_EXCLUDE_SUFFIX):
            continue
        parts = py_file.stem.split("_", 2)
        feature_name = parts[2] if len(parts) >= 3 else py_file.stem
        if not _has_doc([feature_name], doc_names):
            missing.append({"file": name, "feature": feature_name})
    return missing


def _check_sp05(doc_names: list[str]) -> list[dict]:
    api_dir = PROJECT_ROOT / "05_api_server" / "api" / "v1"
    if not api_dir.exists():
        return []
    missing = []
    for py_file in sorted(api_dir.glob("*.py")):
        name = py_file.name
        if name in _SP05_EXCLUDE:
            continue
        keywords = _SP05_FILE_KEYWORDS.get(name, [py_file.stem])
        if not _has_doc(keywords, doc_names):
            missing.append({"file": name, "feature": py_file.stem})
    return missing


def _run_needed_check(sp: str):
    """코드파일 vs 상세 문서 교차검사 (누락 문서 감지) — SP04/SP05만 지원"""
    sp_int = int(sp)
    if sp_int not in (4, 5):
        return

    print()
    print("## 코드파일 vs 상세 문서 교차검사")
    print()

    doc_names = _get_doc_names(sp)
    if sp_int == 4:
        missing = _check_sp04(doc_names)
        label = "백오피스 페이지"
    else:
        missing = _check_sp05(doc_names)
        label = "API 라우터"

    if not missing:
        print(f"✅ 모든 {label} 파일에 상세 문서가 존재합니다.")
    else:
        print(f"⚠️  상세 문서 누락 {label}: {len(missing)}개\n")
        print(f"| {'파일':<35} | {'기능명':<25} |")
        print(f"|{'-'*37}|{'-'*27}|")
        for m in missing:
            print(f"| {m['file']:<35} | {m['feature']:<25} |")
        print(f"\n→ `ccf new dXXXX \"기능명\"` 으로 상세 문서 생성하세요.")


def get_git_last_modified(path: Path) -> str | None:
    """git log으로 경로의 마지막 커밋 날짜 반환 (YYYY-MM-DD)"""
    try:
        result = subprocess.run(
            ["git", "-C", str(PROJECT_ROOT), "log", "-1", "--format=%ai", "--", str(path)],
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        date_str = result.stdout.strip()
        return date_str[:10] if date_str else None
    except Exception:
        return None


def parse_doc_history_date(doc_path: Path) -> str | None:
    """문서이력관리 섹션의 최신 날짜 파싱 (예: - v17 2026-04-18 — ...)"""
    if not doc_path.exists():
        return None
    try:
        content = doc_path.read_text(encoding="utf-8")
        m = re.search(r'## 문서이력관리(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if not m:
            return None
        dates = re.findall(r'(\d{4}-\d{2}-\d{2})', m.group(1))
        return max(dates) if dates else None
    except Exception:
        return None


_SP_CODE_DIRS = {
    1: "01_obsidian",
    2: "02_pycode",
    3: "03_paper",
    4: "04_backoffice",
    5: "05_api_server",
    6: "06_oohwp_skill",
    7: "07_designsystem",
    8: "08_RRag",
    9: "09_ooppt",
}


def detect_priority(sp: str) -> dict:
    """문서 vs 코드 우선순위 자동 판단.
    신호: (1) git log 코드 최근 변경일, (2) git log 문서 최근 변경일,
          (3) plan.md 문서이력관리 마지막 날짜
    Returns: {direction, confidence, signals, dates}
    """
    sp_int = int(sp)
    sp_folder = get_sp_folder(sp)

    # git 날짜 수집
    doc_dir = DOC_DIR / sp_folder
    doc_git_date = get_git_last_modified(doc_dir)

    code_dir_name = _SP_CODE_DIRS.get(sp_int)
    code_git_date = None
    if code_dir_name:
        code_path = PROJECT_ROOT / code_dir_name
        if code_path.exists():
            code_git_date = get_git_last_modified(code_path)

    # 문서이력관리 최신 날짜 (plan.md 기준)
    plan_path = find_plan_path(sp)
    history_date = parse_doc_history_date(plan_path)

    signals = []
    score = 0  # 양수: 문서 최신, 음수: 코드 최신

    if doc_git_date and code_git_date:
        if doc_git_date > code_git_date:
            score += 2
            signals.append(f"문서 git({doc_git_date}) > 코드 git({code_git_date})")
        elif code_git_date > doc_git_date:
            score -= 2
            signals.append(f"코드 git({code_git_date}) > 문서 git({doc_git_date})")
        else:
            signals.append(f"동일 날짜({doc_git_date})")

    if history_date:
        if code_git_date and history_date < code_git_date:
            score -= 1
            signals.append(f"문서이력 마지막({history_date}) < 코드 변경({code_git_date})")
        elif doc_git_date and history_date >= doc_git_date:
            score += 1
            signals.append(f"문서이력 마지막({history_date}) ≥ 문서 git({doc_git_date})")

    if score >= 2:
        direction, confidence = "문서→코드", "high" if score >= 3 else "medium"
    elif score <= -2:
        direction, confidence = "코드→문서", "high" if score <= -3 else "medium"
    else:
        direction, confidence = "불명확", "low"

    return {
        "direction": direction,
        "confidence": confidence,
        "signals": signals,
        "doc_git_date": doc_git_date,
        "code_git_date": code_git_date,
        "history_date": history_date,
    }


def run_auto(sp: str, dry_run: bool, apply: bool):
    """통합 변경 감지 → cccheck 검토 → 상세기획으로 롤백
    - plan.md 변경: 영향 doc 무조건 롤백 (계획이 바뀌면 재기획 필요)
    - 상세 문서 변경: cccheck 실행 → CRITICAL/ERROR 있을 때만 롤백
    - 코드파일 교차검사: SP04/SP05 누락 문서 감지 (항상 실행)
    """
    print(f"[ccfeature update] SP{int(sp):02d}")
    print()

    # 우선순위 자동 판단
    priority = detect_priority(sp)
    confidence_icon = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(priority["confidence"], "")
    print(f"## 우선순위 분석")
    print(f"  방향: {priority['direction']}  신뢰도: {confidence_icon}{priority['confidence']}")
    for sig in priority["signals"]:
        print(f"  · {sig}")
    if priority["direction"] == "문서→코드":
        print(f"  → 문서가 최신입니다. `ccdev run`으로 코드를 문서에 맞춰 업데이트하세요.")
    elif priority["direction"] == "코드→문서":
        print(f"  → 코드가 최신입니다. 문서를 코드에 맞춰 롤백/업데이트합니다.")
    else:
        print(f"  → 신호가 불명확합니다. 아래 변경 감지 결과를 참고하세요.")
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

    # 2. 변경된 상세 문서 감지 → cccheck 실행 → 이슈 있는 것만 롤백 대상
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
        print(f"상세 문서 변경 감지 → {len(doc_candidates)}개 cccheck 실행 중...")
        print()
        for doc_path, doc_num, stage, func_name in doc_candidates:
            print(f"  cccheck run {doc_num} ({func_name}) ...")
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
    else:
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
            print(f"  ccfeature update --apply{dry_str}")
        else:
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
                print("  2. ccfeature next dXXXX  → 기획→설계 재전환")
                print("  3. ccplan sync           → plan.md 8.2절 갱신")

    # 항상: 코드파일 vs 상세 문서 교차검사
    _run_needed_check(sp)


# ---- doc_id 모드: ccf update <doc_id> [--sp N] ----

def _find_detail_doc_by_id(doc_id: str, sp: str):
    """(path, stage, func_name) 반환, 없으면 None"""
    sp_folder = get_sp_folder(sp)
    doc_dir = DOC_DIR / sp_folder
    if not doc_dir.exists():
        return None
    for f in sorted(doc_dir.glob(f"{doc_id}_상세*.md")):
        m = FILE_PATTERN.match(f.name)
        if m:
            return (f, m.group(2), m.group(3))
    # 완료 단계 (FILE_PATTERN 미매칭) 허용
    for f in sorted(doc_dir.glob(f"{doc_id}_*.md")):
        parts = f.stem.split("_", 2)
        if len(parts) >= 3 and "상세" in parts[1]:
            stage_part = parts[1].replace("상세", "")
            return (f, stage_part or "완료", parts[2])
    return None


def _parse_req_table(content: str) -> list[dict]:
    """§3 요구사항 테이블 파싱 -> [{"id", "text", "priority"}]"""
    reqs = []
    in_section = False
    for line in content.splitlines():
        if re.match(r'^##\s+3[\.\s]', line):
            in_section = True
            continue
        if in_section and re.match(r'^##\s', line):
            break
        if in_section and line.startswith('|'):
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if parts and re.match(r'^R\d+$', parts[0]):
                reqs.append({
                    "id": parts[0],
                    "text": parts[1] if len(parts) > 1 else "",
                    "priority": parts[2] if len(parts) > 2 else "",
                })
    return reqs


def _parse_py_refs(content: str) -> list[str]:
    """문서 전체에서 .py 파일 경로 참조 추출"""
    refs: set[str] = set()
    for line in content.splitlines():
        for m in re.finditer(r'`([^`]*\.py[^`]*)`', line):
            refs.add(m.group(1).strip())
        for m in re.finditer(r'[\w./-]+/[\w./-]+\.py', line):
            refs.add(m.group(0).strip())
    return [r for r in refs if r and '---' not in r and len(r) < 120]


def _git_diff_files() -> list[str]:
    """변경 파일 목록 (워킹트리 -> staged -> last commit)"""
    def _run(extra: list) -> list[str]:
        try:
            r = subprocess.run(
                ["git", "-C", str(PROJECT_ROOT), "diff"] + extra + ["--name-only"],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
            return [l for l in r.stdout.strip().splitlines() if l.strip()]
        except Exception:
            return []
    files = _run(["HEAD"])
    if not files:
        files = _run(["--cached"])
    if not files:
        files = _run(["HEAD~1", "HEAD"])
    return files


def _next_doc_version(content: str) -> str:
    """문서에서 최대 버전 번호 추출 후 +1 반환"""
    nums = re.findall(r'\bv(\d+)\b', content)
    return f"v{max((int(n) for n in nums), default=0) + 1:02d}"


def run_update_doc(doc_id: str, sp: str, dry_run: bool):
    """
    ccf update <doc_id> [--sp N] [--dry-run]

    Phase 1: 상세문서 + 코드 비교 분석 컨텍스트 수집
    Phase 2: [DOC_UPDATE_NEEDED] 신호 -> Claude가 문서 현행화
    Phase 3: [CODE_IMPL_NEEDED] 신호 -> Claude가 ccdev 배치 실행
    """
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")

    print(f"[ccf update] {doc_id}  SP{int(sp):02d}")
    if dry_run:
        print("(--dry-run: 분석만, 실제 변경 없음)")
    print()

    # 1. 문서 찾기
    found = _find_detail_doc_by_id(doc_id, sp)
    if not found:
        sp_folder = get_sp_folder(sp)
        print(f"[ERROR] 상세문서 없음: {doc_id}")
        print(f"  경로: 00_doc/{sp_folder}/{doc_id}_상세*.md")
        print(f"  -> ccf new {doc_id} \"기능명\" --sp {sp}")
        return

    doc_path, stage, func_name = found
    content = doc_path.read_text(encoding="utf-8")
    rel_path = doc_path.relative_to(PROJECT_ROOT)

    print(f"## 상세문서")
    print(f"  파일  : {doc_path.name}")
    print(f"  기능명: {func_name}")
    print(f"  단계  : {STAGE_ICON.get(stage, '')} {stage}")
    print()

    # 2. 요구사항 파싱
    reqs = _parse_req_table(content)
    print(f"## 요구사항 ({len(reqs)}개)")
    for req in reqs:
        print(f"  [{req['id']}] {req['text'][:60]}  ({req['priority']})")
    if not reqs:
        print("  (없음 -- 문서 §3에 요구사항 추가 필요)")
    print()

    # 3. 코드 참조 파싱
    code_refs = _parse_py_refs(content)
    sp_dir_name = _SP_CODE_DIRS.get(int(sp), "")
    print(f"## 참조 코드 ({len(code_refs)}개)")
    for ref in code_refs[:6]:
        rp = PROJECT_ROOT / ref.lstrip("/").replace("\\", "/")
        exists_mark = "OK" if rp.exists() else "없음"
        print(f"  [{exists_mark}] {ref}")
    if not code_refs:
        print(f"  (없음 -- §1 '원본 페이지' 또는 ## A 섹션에 파일 경로 등록 필요)")
        if sp_dir_name:
            print(f"  SP{int(sp):02d} 코드 디렉토리: {sp_dir_name}/")
    print()

    # 4. 최근 변경 파일 분석
    changed_files = _git_diff_files()
    relevant: list[str] = []
    for f in changed_files:
        fn = f.replace("\\", "/")
        if any(ref.lstrip("/") in fn or fn.endswith(Path(ref).name) for ref in code_refs):
            relevant.append(f)
        elif sp_dir_name and fn.startswith(sp_dir_name):
            relevant.append(f)
    relevant = list(dict.fromkeys(relevant))

    print(f"## 최근 변경 파일")
    print(f"  전체: {len(changed_files)}개  |  SP{int(sp):02d} 관련: {len(relevant)}개")
    for f in relevant[:5]:
        print(f"  · {f}")
    if not relevant and changed_files:
        print(f"  (SP 관련 변경 없음. 전체 변경 일부:)")
        for f in changed_files[:3]:
            print(f"  · {f}")
    print()

    # 5. 신호 출력
    has_code_change = len(relevant) > 0
    next_ver = _next_doc_version(content)

    print(f"[DOC_UPDATE_NEEDED]")
    print(f"  file={rel_path}")
    print(f"  date={today}  version={next_ver}")
    print()
    print(f"  Codex 수행 항목 (상세문서 직접 편집):")
    print(f"  1. ## 변경 이력에 {next_ver} {today} 항목 추가")
    if has_code_change:
        print(f"  2. 구현 완료 요구사항 항목에 체크 마킹 (코드 대조 후)")
        print(f"  3. 아래 변경 파일을 §1 / ## A 섹션에 반영:")
        for f in relevant[:5]:
            print(f"     - {f}")
    else:
        print(f"  2. 코드 참조(§1 '원본 페이지') 등록 여부 확인")
    print()

    if not has_code_change or not code_refs:
        print(f"[CODE_IMPL_NEEDED]")
        print(f"  doc_id={doc_id}  sp={sp}")
        if reqs and not has_code_change:
            print(f"  미구현 의심 요구사항 ({len(reqs)}개):")
            for req in reqs[:5]:
                print(f"    [{req['id']}] {req['text'][:50]}")
        print(f"  배치 실행: ccdev run {doc_id} --sp {sp}")
        print()

    print(f"[NEXT_STEP]")
    if dry_run:
        print(f"  dry-run 완료. 실제 실행: ccf update {doc_id} --sp {sp}")
    else:
        print(f"  1. [DOC_UPDATE_NEEDED] 항목 반영 (상세문서 직접 편집)")
        if not has_code_change or not code_refs:
            print(f"  2. [CODE_IMPL_NEEDED] -> ccdev run {doc_id} --sp {sp}")
        print(f"  3. cccommit commit")


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

    # doc_id 인수 감지: ccf update <doc_id> --sp N
    doc_id = None
    for a in args:
        if re.match(r'^d\d{4,}$', a, re.IGNORECASE):
            doc_id = a
            break

    if doc_id:
        run_update_doc(doc_id, sp, dry_run)
    # 기존 명시적 플래그 (하위 호환)
    elif "--from-doc" in args:
        run_from_doc(sp, dry_run=dry_run, apply=apply, skip_check=skip_check)
    elif "--from-plan" in args:
        run_from_plan(sp, dry_run=dry_run, apply=apply)
    else:
        # 통합 자동 감지 모드 (신규 기본)
        run_auto(sp, dry_run=dry_run, apply=apply)


if __name__ == "__main__":
    main()
