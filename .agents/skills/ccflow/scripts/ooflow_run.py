"""
ooflow_run.py — ccflow 스킬 스크립트
전체 SW 개발 워크플로우 오케스트레이터 (기획→설계→개발→검증→완료)

서브명령어:
  help                    도움말
  version                 버전 정보 (v02)
  status [--sp N]         현재 SP 워크플로우 진행 현황
  check [--sp N]          checklist.md 기반 체크
  run [OPTIONS]           dry-run 미리보기 → 확인 → 실행 지시 출력
    --dry-run             계획만 출력 (실제 실행 없음)
    --yes                 확인 없이 즉시 실행
    --interactive         단계별 확인 (CRITICAL 시 중단)
    --sp N                특정 SP 지정
    --until 단계          기획|설계|개발|검증 까지만
    --feature dXXXX       특정 Feature 1개만
  show checklist          역할 수행 체크리스트 표시
"""
import sys
import io
import re
from pathlib import Path
from typing import Optional

# Windows 환경 UTF-8 출력 보장
if hasattr(sys.stdout, 'buffer') and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── 경로 설정 ──────────────────────────────────────────────────
SKILL_DIR = Path(__file__).parent.parent
SKILL_MD = SKILL_DIR / "SKILL.md"
PROJECT_ROOT = SKILL_DIR.parent.parent.parent  # 0001_SApp
DOC_ROOT = PROJECT_ROOT / "00_doc"

# ── 상수 ────────────────────────────────────────────────────────
STAGE_ORDER = ["기획", "설계", "개발", "검증", "완료"]
STAGE_KEYWORD = {
    "기획": "_상세기획_",
    "설계": "_상세설계_",
    "개발": "_상세개발_",
    "검증": "_상세검증_",
}
STAGE_ICON = {
    "기획": "⚪", "설계": "🔵", "개발": "🟡",
    "검증": "🟢", "완료": "✅", "미착수": "⬜",
}
LINKED_SKILLS = ["oofeature", "oodev", "oocheck", "oofix", "oodoc", "oohistory", "oocommit"]


# ── SP 유틸 ─────────────────────────────────────────────────────
def get_sp_number(sp_arg: Optional[str] = None) -> int:
    if sp_arg is not None:
        return int(sp_arg)
    cwd = Path.cwd()
    for part in reversed(cwd.parts):
        m = re.match(r'^0(\d)_', part)
        if m:
            return int(m.group(1))
    return 0


def get_doc_dir(sp: int) -> Path:
    return DOC_ROOT / f"sp{sp:02d}"


def get_plan_path(sp: int) -> Optional[Path]:
    doc_dir = get_doc_dir(sp)
    doc_num = sp * 10000 + 2
    matches = list(doc_dir.glob(f"d{doc_num}_*.md")) + list(doc_dir.glob(f"d{doc_num:05d}_*.md"))
    if matches:
        return matches[0]
    p = doc_dir / f"d{doc_num:05d}_plan.md"
    return p if p.exists() else None


# ── plan.md 파싱 ─────────────────────────────────────────────────
def extract_features_from_plan(plan_path: Path) -> list:
    """plan.md Feature 테이블에서 doc_id가 있는 항목 추출"""
    features = []
    if not plan_path or not plan_path.exists():
        return features
    content = plan_path.read_text(encoding="utf-8")
    # | F10.2 | E10 | 4_47 | 썸네일관리 ... | Should | d40447 |
    pattern = re.compile(
        r'\|\s*(F[\d.]+)\s*\|\s*([^\|]*?)\s*\|\s*([^\|]*?)\s*\|\s*([^\|]+?)\s*\|\s*([^\|]+?)\s*\|\s*(d\d+)\s*\|'
    )
    for m in pattern.finditer(content):
        features.append({
            'id': m.group(1).strip(),
            'epic': m.group(2).strip(),
            'page': m.group(3).strip(),
            'name': m.group(4).strip()[:20],
            'priority': m.group(5).strip(),
            'doc_id': m.group(6).strip(),
            'stage': '미착수',
        })
    return features


# ── 상세 문서 스캔 ────────────────────────────────────────────────
def get_detail_doc_stages(sp: int) -> dict:
    """doc_id → 현재 단계 매핑 (가장 앞선 단계 기준)"""
    doc_dir = get_doc_dir(sp)
    result = {}
    for stage in STAGE_ORDER[:-1]:  # 완료 제외
        keyword = STAGE_KEYWORD[stage]
        for f in doc_dir.glob(f"*{keyword}*.md"):
            doc_id = f.stem.split("_")[0]
            if doc_id not in result:
                result[doc_id] = stage
            else:
                # 더 앞선 단계로 덮어쓰지 않음 (현재 단계 유지)
                prev_idx = STAGE_ORDER.index(result[doc_id])
                curr_idx = STAGE_ORDER.index(stage)
                if curr_idx > prev_idx:
                    result[doc_id] = stage
    return result


# ── 상태 스캔 ─────────────────────────────────────────────────────
def scan_status(sp: int) -> dict:
    plan_path = get_plan_path(sp)
    features = extract_features_from_plan(plan_path) if plan_path else []
    stages = get_detail_doc_stages(sp)

    unstarted, in_progress, done = [], [], []
    for f in features:
        stage = stages.get(f['doc_id'], '미착수')
        f['stage'] = stage
        if stage == '미착수':
            unstarted.append(f)
        elif stage == '검증':
            done.append(f)
        else:
            in_progress.append(f)

    return {
        'sp': sp,
        'plan_path': plan_path,
        'features': features,
        'unstarted': unstarted,
        'in_progress': in_progress,
        'done': done,
    }


# ── 서브명령어 구현 ───────────────────────────────────────────────
def cmd_status(sp_arg=None):
    sp = get_sp_number(sp_arg)
    s = scan_status(sp)
    print(f"[ccflow status] SP{sp:02d}")
    print()
    if not s['features']:
        print("  plan.md에서 Feature를 찾을 수 없습니다.")
        return
    total = len(s['features'])
    print(f"  전체: {total} | 미착수: {len(s['unstarted'])} | 진행중: {len(s['in_progress'])} | 완료: {len(s['done'])}")
    print()
    for f in s['features']:
        icon = STAGE_ICON.get(f['stage'], '⬜')
        print(f"  {icon}  {f['doc_id']:8s}  {f['name']:20s}  {f['stage']}")
    print()
    if s['unstarted']:
        print(f"  미착수 {len(s['unstarted'])}개 → `ccflow run`으로 자동 처리 가능")


def cmd_check(sp_arg=None):
    sp = get_sp_number(sp_arg)
    results = {}

    # C01: 필수 파일 존재
    results['C01'] = SKILL_MD.exists() and Path(__file__).exists()

    # C02: 버전 일치
    c02 = False
    if SKILL_MD.exists():
        text = SKILL_MD.read_text(encoding="utf-8")
        meta_m = re.search(r'version:\s*(v\d+)', text)
        tbl_m = re.search(r'ccflow version.*?\((v\d+)\)', text)
        c02 = bool(meta_m and tbl_m and meta_m.group(1) == tbl_m.group(1))
    results['C02'] = c02

    # C03: 연계 스킬 존재
    missing = [s for s in LINKED_SKILLS if not (SKILL_DIR.parent / s / "SKILL.md").exists()]
    results['C03'] = (missing, len(missing) == 0)

    # C04: 튜토리얼 동기화 (파일 존재 여부만 체크)
    tut = PROJECT_ROOT / "00_doc" / "tutorial" / "11_SW개발워크플로우.md"
    results['C04'] = tut.exists()

    # C05: PRD/Plan 존재
    doc_dir = get_doc_dir(sp)
    prd_num = sp * 10000 + 1
    plan_num = sp * 10000 + 2
    prd_ok = bool(list(doc_dir.glob(f"d{prd_num}_*.md")) + list(doc_dir.glob(f"d{prd_num:05d}_*.md")))
    plan_ok = bool(list(doc_dir.glob(f"d{plan_num}_*.md")) + list(doc_dir.glob(f"d{plan_num:05d}_*.md")))
    results['C05'] = prd_ok and plan_ok

    print("[ccflow check]")
    print()

    def flag(ok): return "[OK]" if ok else "[FAIL]"
    def wflag(ok): return "[OK]" if ok else "[WARN]"

    print(f"C01 필수 파일 존재     {flag(results['C01'])}")
    print(f"C02 버전 일치         {flag(results['C02'])}")
    missing_list, c03_ok = results['C03']
    print(f"C03 연계 스킬 존재    {flag(c03_ok)}" + (f"  누락: {', '.join(missing_list)}" if not c03_ok else ""))
    print(f"C04 튜토리얼 동기화   {wflag(results['C04'])}")
    print(f"C05 PRD/Plan 존재     {wflag(results['C05'])}")

    ok = sum(1 for k, v in results.items() if k != 'C03' and v) + (1 if c03_ok else 0)
    warn = (0 if results['C04'] else 1) + (0 if results['C05'] else 1)
    err = (0 if results['C01'] else 1) + (0 if results['C02'] else 1) + (0 if c03_ok else 1)
    print()
    print(f"소계: OK:{ok} | WARN:{warn} | ERROR:{err}")


def build_plan(sp: int, until: Optional[str], feature_id: Optional[str]) -> dict:
    """dry-run 계획 출력 + dict 반환"""
    s = scan_status(sp)

    if feature_id:
        targets = [f for f in s['features'] if f['doc_id'] == feature_id]
    else:
        targets = s['unstarted'] + s['in_progress']

    until_stage = until or "완료"

    print(f"[ccflow dry-run] SP{sp:02d}")
    print()
    print("실행 예정 단계:")
    print("  [1] ooprd run          → PRD 정합성 검증")
    print("  [2] ooplan run         → Plan 갱신")
    print("  [3] oofeature needed   → 미착수 Feature 확인")
    print()

    if not targets:
        print("  처리할 Feature가 없습니다. (모두 완료 또는 검증 단계)")
        return {'targets': [], 'sp': sp, 'until': until_stage}

    print(f"처리 대상 Feature ({len(targets)}개):")
    for f in targets:
        stage = f['stage']
        icon = STAGE_ICON.get(stage, '⬜')
        remaining = STAGE_ORDER[STAGE_ORDER.index(stage) if stage != '미착수' else 0:]
        if stage != '미착수':
            remaining = STAGE_ORDER[STAGE_ORDER.index(stage) + 1:]
        if until_stage != "완료" and until_stage in remaining:
            remaining = remaining[:remaining.index(until_stage) + 1]
        steps_str = "→".join(remaining) if remaining else "완료"
        print(f"  {icon}  {f['doc_id']:8s}  {f['name']:20s}  [{steps_str}]")

    n = len(targets)
    total_calls = 3 + n * 5 + 3  # 공통 3 + Feature당 5 + 마무리 3
    print()
    print(f"  [4~{3+n*5}] Feature별 순차 실행 ({n} × 5단계 = {n*5} 스킬 호출)")
    print(f"  [{4+n*5}] oodoc run")
    print(f"  [{5+n*5}] oohistory run")
    print(f"  [{6+n*5}] oocommit run (최종)")
    print()
    print(f"총 예상 스킬 호출: {total_calls}회")

    return {'targets': targets, 'sp': sp, 'until': until_stage}


def print_run_instructions(plan: dict, interactive: bool = False):
    """Claude 오케스트레이션용 실행 지시 출력"""
    sp = plan['sp']
    targets = plan['targets']
    until = plan['until']

    if not targets:
        return

    mode_note = " [--interactive: CRITICAL 발생 시 사용자 확인]" if interactive else " [완전 무인 자동화]"
    print()
    print("=" * 60)
    print(f"[ccflow run] 실행 지시{mode_note}")
    print("=" * 60)
    print()
    print("다음 순서대로 스킬을 실행하세요:\n")

    step = 1
    print(f"  [{step:02d}] ooprd run --sp {sp:02d}")
    step += 1
    print(f"  [{step:02d}] ooplan run --sp {sp:02d}")
    step += 1
    print(f"  [{step:02d}] oofeature needed --sp {sp:02d}")
    step += 1
    print()

    for f in targets:
        doc_id = f['doc_id']
        name = f['name']
        stage = f['stage']
        print(f"  # ── {doc_id} {name} (현재: {stage}) ──")

        # 남은 단계 계산
        if stage == '미착수':
            remaining = STAGE_ORDER[:-1]  # 기획~검증
        else:
            idx = STAGE_ORDER.index(stage)
            remaining = STAGE_ORDER[idx + 1:-1]  # 다음 단계~검증

        # until 적용
        if until != "완료" and until in STAGE_ORDER:
            until_idx = STAGE_ORDER.index(until)
            remaining = [s for s in remaining if STAGE_ORDER.index(s) <= until_idx]

        for s in remaining:
            if s == "기획":
                print(f"  [{step:02d}] oofeature next {doc_id}   # 상세기획 생성")
            elif s == "설계":
                print(f"  [{step:02d}] oofeature next {doc_id}   # 기획→설계 전환")
            elif s == "개발":
                print(f"  [{step:02d}] oodev run {doc_id}")
            elif s == "검증":
                print(f"  [{step:02d}] oocheck run {doc_id}")
            step += 1

        if until == "완료" or until not in STAGE_ORDER:
            print(f"  [{step:02d}] oofeature next {doc_id}   # 완료 처리")
            step += 1
            print(f"  [{step:02d}] oocommit run")
            step += 1

        print()

    print(f"  [{step:02d}] oodoc run")
    step += 1
    print(f"  [{step:02d}] oohistory run")
    step += 1
    print(f"  [{step:02d}] oocommit run   # 최종 커밋")
    print()
    if interactive:
        print("  ※ CRITICAL 이슈 발생 시: oofix run → oocheck run 재검증 (최대 3회)")
        print("  ※ --interactive 모드: CRITICAL 3회 실패 시 사용자에게 확인 요청")
    else:
        print("  ※ CRITICAL/ERROR → oofix run 자동 실행 → 재검증 (최대 3회)")
        print("  ※ WARNING → d{SP}0004_todo.md 등록 후 계속 진행")


def _print_skill_help():
    if not SKILL_MD.exists():
        print("SKILL.md not found")
        return
    lines = SKILL_MD.read_text(encoding="utf-8").splitlines()
    in_table = False
    table_lines = []
    for line in lines:
        if "| 명령어 |" in line and "설명" in line:
            in_table = True
        if in_table:
            if line.startswith("|"):
                table_lines.append(line)
            elif table_lines:
                break
    print("`ccflow` 서브명령어 목록:\n")
    for line in table_lines:
        print(line)


# ── main ─────────────────────────────────────────────────────────
def cmd_show_checklist():
    """references/checklist.md 내용 출력"""
    checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[{SKILL_NAME}] checklist.md 없음: {checklist_path}")
        return
    print(checklist_path.read_text(encoding="utf-8"))


def main():
    if len(sys.argv) > 2 and sys.argv[1].lower() == "show" and sys.argv[2].lower() == "checklist":
        cmd_show_checklist()
        return
    args = sys.argv[1:]

    if not args or args[0] == "help":
        _print_skill_help()
        return

    if args[0] == "version":
        print("ccflow v02")
        return

    if args[0] == "show" and len(args) > 1 and args[1] == "checklist":
        p = SKILL_DIR / "references" / "checklist.md"
        print(p.read_text(encoding="utf-8") if p.exists() else "checklist.md 없음")
        return

    if args[0] == "status":
        sp_arg = args[args.index("--sp") + 1] if "--sp" in args else None
        cmd_status(sp_arg)
        return

    if args[0] == "check":
        sp_arg = args[args.index("--sp") + 1] if "--sp" in args else None
        cmd_check(sp_arg)
        return

    if args[0] == "run":
        dry_run = "--dry-run" in args
        yes_mode = "--yes" in args
        interactive = "--interactive" in args
        sp_arg = args[args.index("--sp") + 1] if "--sp" in args else None
        until = args[args.index("--until") + 1] if "--until" in args else None
        feature_id = args[args.index("--feature") + 1] if "--feature" in args else None

        sp = get_sp_number(sp_arg)
        plan = build_plan(sp, until=until, feature_id=feature_id)

        if dry_run or not plan['targets']:
            return

        if not yes_mode:
            print()
            try:
                ans = input("위 계획으로 실행하시겠습니까? [y/N] ").strip().lower()
            except EOFError:
                ans = "n"
            if ans not in ("y", "yes"):
                print("실행 취소.")
                return

        print_run_instructions(plan, interactive=interactive)
        return

    print(f"알 수 없는 서브명령어: {args[0]}")
    print("사용법: ccflow help")


if __name__ == "__main__":
    main()
