"""
ooflow_run.py — ccflow 스킬 스크립트
전체 SW 개발 워크플로우 오케스트레이터 (기획→설계→개발→검증→완료)

todo 게이트 방식: 사전 todo 점검 → 검증·기획·설계(탐지) → 상세설계 게이트
→ todo 0건일 때만 개발·검증·완료 진행.

서브명령어:
  help                    도움말
  version                 버전 정보 (v04)
  status [--sp N]         현재 SP 워크플로우 진행 현황
  check [--sp N]          checklist.md 기반 체크
  run [OPTIONS]           사전 todo 점검 → dry-run 미리보기 → 확인 → 실행 지시 출력
    --dry-run             계획만 출력 (실제 실행 없음)
    --yes                 확인 없이 즉시 실행
    --interactive         단계별 확인 (CRITICAL 시 중단)
    --sp N                특정 SP 지정
    --until 단계          기획|설계|개발|검증 까지만
    --feature dXXXX       특정 Feature 1개만
  plan [OPTIONS]          사전 todo 점검 + 검증·기획·설계까지만 전반 검토
    --dry-run             계획만 출력 (실제 실행 없음)
    --sp N                특정 SP 지정
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
LINKED_SKILLS = ["ccfeature", "ccdev", "cccheck", "ccreview", "ccfix", "ccdoc", "cchistory", "cccommit"]


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


def get_todo_path(sp: int) -> Optional[Path]:
    """d{SP}0004_todo.md 경로 반환 (없으면 None)"""
    doc_dir = get_doc_dir(sp)
    doc_num = sp * 10000 + 4
    matches = list(doc_dir.glob(f"d{doc_num}_*.md")) + list(doc_dir.glob(f"d{doc_num:05d}_*.md"))
    if matches:
        return matches[0]
    # sp00은 d0004_todo.md 형식
    p = doc_dir / f"d{doc_num:04d}_todo.md"
    return p if p.exists() else None


# ── 사전 todo 점검 ───────────────────────────────────────────────
OPEN_TODO_KEYWORDS = ("대기", "pending", "진행중", "진행 중", "in progress", "in-progress", "open")


def count_open_todos(sp: int) -> int:
    """d{SP}0004_todo.md에서 미해결 todo 개수를 센다.

    todo 행 패턴: `| ID | ... | 상태 |` 형식에서 상태 셀이
    대기/pending/진행중 등인 행. 파일이 없거나 0건이면 0을 반환한다.
    """
    todo_path = get_todo_path(sp)
    if not todo_path or not todo_path.exists():
        return 0
    content = todo_path.read_text(encoding="utf-8")
    count = 0
    for line in content.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        # 구분선(---) 또는 헤더 행 제외
        if all(set(c) <= set("-: ") for c in cells):
            continue
        last = cells[-1].lower()
        if any(kw in last for kw in OPEN_TODO_KEYWORDS):
            count += 1
    return count


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
    print("  [1] ccprd run          → PRD 정합성 검증")
    print("  [2] ccplan run         → Plan 갱신")
    print("  [3] ccfeature needed   → 미착수 Feature 확인")
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
    print(f"  [{4+n*5}] ccdoc run")
    print(f"  [{5+n*5}] cchistory run")
    print(f"  [{6+n*5}] cccommit run (최종)")
    print()
    print(f"총 예상 스킬 호출: {total_calls}회")

    return {'targets': targets, 'sp': sp, 'until': until_stage}


def print_todo_gate_check(sp: int) -> int:
    """Step 0 사전 todo 점검 출력. 미해결 todo 개수를 반환한다."""
    open_count = count_open_todos(sp)
    todo_path = get_todo_path(sp)
    print()
    print("─" * 60)
    print("[Step 0] 사전 todo 점검")
    print("─" * 60)
    if open_count > 0:
        rel = todo_path.name if todo_path else f"d{sp*10000+4:05d}_todo.md"
        print(f"  ⚠️  미해결 todo {open_count}건 발견 — {rel}")
        print("  → 기존 todo를 먼저 처리한 후 ooflow를 실행하세요.")
        print("  → Claude는 미해결 todo를 하나씩 보여주며 처리 여부를 사용자에게 문의할 것.")
    else:
        print("  ✅ 미해결 todo 없음 — 워크플로우 진행 가능")
    return open_count


def print_run_instructions(plan: dict, interactive: bool = False, review_enabled: bool = True,
                           plan_mode: bool = False):
    """Codex 오케스트레이션용 실행 지시 출력

    plan_mode=True: Step 0(사전 todo 점검) + Step 1(검증·기획·설계)까지만 출력.
                    항상 상세설계 단계에서 멈춤 (개발·검증·완료 미출력).
    """
    sp = plan['sp']
    targets = plan['targets']
    until = plan['until']

    if not targets:
        return

    if plan_mode:
        mode_note = " [plan 모드 — 상세설계까지 전반 검토]"
    elif interactive:
        mode_note = " [--interactive: CRITICAL 발생 시 사용자 확인]"
    else:
        mode_note = " [todo 게이트 방식]"
    label = "ccflow plan" if plan_mode else "ccflow run"
    print()
    print("=" * 60)
    print(f"[{label}] 실행 지시{mode_note}")
    print("=" * 60)
    print()
    print("다음 순서대로 스킬을 실행하세요:\n")

    print("  # ── [Step 1] 검증·기획·설계 (탐지 모드) ──")
    print("  #   ccprd/ccplan 정합성 검증 + 기획·설계는 탐지 위주.")
    print("  #   자동 수정하지 말 것 — 발견된 정합성/설계 문제는")
    print(f"  #   전부 d{sp*10000+4:05d}_todo.md(또는 d0004_todo.md)에 적재.")
    step = 1
    print(f"  [{step:02d}] ccprd run --sp {sp:02d}      # PRD 정합성 검증 (탐지)")
    step += 1
    print(f"  [{step:02d}] ccplan run --sp {sp:02d}     # Plan 정합성 검증 (탐지)")
    step += 1
    print(f"  [{step:02d}] ccfeature needed --sp {sp:02d}")
    step += 1
    print()

    # plan 모드 또는 run 모드 모두: 기획·설계 단계 먼저 출력
    print("  # ── [Step 1 계속] Feature별 기획·설계 (탐지) ──")
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
                print(f"  [{step:02d}] ccfeature next {doc_id}   # 상세기획 생성")
                step += 1
            elif s == "설계":
                print(f"  [{step:02d}] ccfeature next {doc_id}   # 기획→설계 전환")
                step += 1
    print()

    # ── 상세설계 게이트 ──────────────────────────────────────────
    print("─" * 60)
    print("[Step 2] 상세설계 게이트")
    print("─" * 60)
    print(f"  검증·기획·설계 단계에서 d{sp*10000+4:05d}_todo.md(또는 d0004_todo.md)에")
    print("  신규 todo가 적재됐는지 확인할 것.")
    print("  ▸ 신규 todo 있음 → 상세설계 단계에서 중단(개발·검증으로 진행 금지).")
    print("    \"발생한 todo를 전부 해결한 후 ooflow를 다시 실행하세요\" 안내 +")
    print("    발생한 todo를 하나씩 보여주며 처리 여부를 사용자에게 문의.")
    print("  ▸ 신규 todo 없음(0건) → [Step 3] 개발·검증·완료로 진행.")
    print()

    if plan_mode:
        print("=" * 60)
        print("[ccflow plan] 검토 종료 — 상세설계 단계까지만 진행")
        print("=" * 60)
        print("  plan 모드는 게이트와 무관하게 항상 상세설계에서 멈춥니다.")
        print("  개발을 진행하려면: ccflow run")
        return

    # ── [Step 3] 개발·검증·완료 (todo 0건일 때만) ────────────────
    print("  # ── [Step 3] 개발·검증·완료 (d0004 신규 todo 0건일 때만 진행) ──")
    for f in targets:
        doc_id = f['doc_id']
        name = f['name']
        stage = f['stage']
        print(f"  # ── {doc_id} {name} ──")

        if stage == '미착수':
            remaining = STAGE_ORDER[:-1]
        else:
            idx = STAGE_ORDER.index(stage)
            remaining = STAGE_ORDER[idx + 1:-1]
        if until != "완료" and until in STAGE_ORDER:
            until_idx = STAGE_ORDER.index(until)
            remaining = [s for s in remaining if STAGE_ORDER.index(s) <= until_idx]

        for s in remaining:
            if s == "개발":
                print(f"  [{step:02d}] cctest write {doc_id}   # TDD RED: TC 코드 작성")
                step += 1
                print(f"  [{step:02d}] ccdev run {doc_id}      # TDD GREEN: 최소 구현")
                step += 1
                print(f"  [{step:02d}] cctest run {doc_id}     # 테스트 실행 (PASS 확인)")
                step += 1
            elif s == "검증":
                print(f"  [{step:02d}] cccheck run {doc_id}    # 정적 분석")
                step += 1
                if review_enabled:
                    print(f"  [{step:02d}] ccreview run {doc_id}   # AI 리뷰 (설계·보안·품질 + Codex 2차)")
                    step += 1

        if until == "완료" or until not in STAGE_ORDER:
            print(f"  [{step:02d}] ccfeature next {doc_id}   # 완료 처리")
            step += 1
            print(f"  [{step:02d}] cccommit run")
            step += 1

        print()

    print("  # ── [Step 4] 마무리 ──")
    print(f"  [{step:02d}] ccdoc run")
    step += 1
    print(f"  [{step:02d}] cchistory run")
    step += 1
    print(f"  [{step:02d}] cccommit run   # 최종 커밋")
    print()
    print("  ※ [개발 단계 이슈 처리 — 설계와 다름]")
    print("  ※ cccheck/ccreview 이슈 발견 시:")
    print(f"  ※   → d{sp*10000+4:05d}_todo.md(또는 d0004_todo.md)에 적재")
    print("  ※   → ccfix 자동 실행 → 재검증 (중단하지 않고 계속 진행)")
    if interactive:
        print("  ※ --interactive 모드: CRITICAL 3회 실패 시 사용자에게 확인 요청")
    if not review_enabled:
        print("  ※ --no-review: ccreview 단계 생략됨 (모든 Feature)")

    # ── ccflow 완료 후 권장 사항 ─────────────────────────────────
    print()
    print("─" * 60)
    print("[ccflow 완료 후 권장 — 수동 Codex 리뷰]")
    print("─" * 60)
    print("  [A] /codex:review              → 일반 리뷰 (설계·버그·개선)")
    print("      • Codex 인터랙티브 UI에서 변경분 전체 종합 검토")
    print("      • 자동 ccreview(codex:rescue read-only)와 별개")
    print("      • 풍부한 UI: 인라인 코드 인용, 색상 표시")
    print("      • 권장 시점: Phase/마일스톤 종료, PR 작성 전 self-review")
    print("      • 옵션: --wait (작은 변경) / --background (큰 변경)")
    print()
    print("  [B] /codex:adversarial-review  → 보안 특화 (공격적 7개 면)")
    print("      • 적대적 관점에서 7개 공격 면 체계적 검토")
    print("        1) 인증/권한       2) 데이터 손실    3) 롤백 안전성")
    print("        4) 레이스 컨디션   5) 빈 상태 엣지   6) 버전 스큐")
    print("        7) 관찰성 갭(로깅·모니터링)")
    print("      • 필수 적용 시점:")
    print("        - 인증·세션·토큰 처리 변경")
    print("        - 결제·금융·개인정보 처리 변경")
    print("        - 외부 API 노출 (REST/GraphQL endpoint 추가)")
    print("        - DB 스키마 마이그레이션")
    print("        - 프로덕션 배포 직전")
    print("      • 비용 주의: /codex:review 보다 토큰 소모 큼")
    print()
    print("  사용 가이드:")
    print("    일반 기능       → [A] /codex:review")
    print("    보안 민감       → [B] /codex:adversarial-review (필수)")
    print("    Phase 종료      → [A] → [B] 둘 다 권장")
    print("    상세 안내       → 00_doc/tutorial/11_SW개발워크플로우.md §6.5")


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
        print("ccflow v04")
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
        review_enabled = "--no-review" not in args
        sp_arg = args[args.index("--sp") + 1] if "--sp" in args else None
        until = args[args.index("--until") + 1] if "--until" in args else None
        feature_id = args[args.index("--feature") + 1] if "--feature" in args else None

        sp = get_sp_number(sp_arg)

        # Step 0: 사전 todo 점검
        open_todos = print_todo_gate_check(sp)
        print()

        plan = build_plan(sp, until=until, feature_id=feature_id)

        if dry_run or not plan['targets']:
            return

        if not yes_mode:
            print()
            prompt = "위 계획으로 실행하시겠습니까? [y/N] "
            if open_todos > 0:
                prompt = f"미해결 todo {open_todos}건이 있습니다. 그래도 실행하시겠습니까? [y/N] "
            try:
                ans = input(prompt).strip().lower()
            except EOFError:
                ans = "n"
            if ans not in ("y", "yes"):
                print("실행 취소.")
                return

        print_run_instructions(plan, interactive=interactive, review_enabled=review_enabled)
        return

    if args[0] == "plan":
        dry_run = "--dry-run" in args
        sp_arg = args[args.index("--sp") + 1] if "--sp" in args else None

        sp = get_sp_number(sp_arg)

        # Step 0: 사전 todo 점검
        print_todo_gate_check(sp)
        print()

        # plan 모드는 항상 설계 단계까지만 전반 검토
        plan = build_plan(sp, until="설계", feature_id=None)

        if dry_run or not plan['targets']:
            return

        print_run_instructions(plan, plan_mode=True)
        return

    print(f"알 수 없는 서브명령어: {args[0]}")
    print("사용법: ccflow help")


if __name__ == "__main__":
    main()
