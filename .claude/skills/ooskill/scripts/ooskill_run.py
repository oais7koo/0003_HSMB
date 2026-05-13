#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ooskill_run.py - oo 스킬 최적화 검증

서브명령어:
    status    - 서브명령어 목록, 스킬 현황, 최적화 요약
    version   - 스킬 버전 정보 (v01)
    validate  - 서브에이전트/명령어 활용 최적화 검증
    run       - 전체 스킬 자동 최적화 수행
    run [스킬명] - 특정 스킬만 최적화

사용법:
    uv run python .claude/skills/ooskill/scripts/ooskill_run.py status
    uv run python .claude/skills/ooskill/scripts/ooskill_run.py validate
    uv run python .claude/skills/ooskill/scripts/ooskill_run.py run
    uv run python .claude/skills/ooskill/scripts/ooskill_run.py run oocheck
"""

import sys
import re
from pathlib import Path
from datetime import datetime

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

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
    _c = _sf.read_text(encoding="utf-8").replace('\r\r\n', '\n').replace('\r\n', '\n').replace('\r', '\n')
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
SKILLS_DIR = _SKILLS_DIR
SCRIPT_DIR = Path(__file__).parent

# 권장 에이전트 목록 (SKILL.md 검증 기준)
KNOWN_AGENTS = [
    "task-executor", "python-code-reviewer", "task-checker", "ooqa",
    "code-error-checker", "oo-web-test-orchestrator", "data-analyst",
    "academic-researcher", "Explore", "general-purpose", "Plan",
    "ai-engineer", "frontend-developer", "web-design-expert",
    "data-engineer", "data-scientist", "translator",
]

# 서브에이전트 섹션 검증 제외 화이트리스트
# - alias 스킬: 한 줄짜리 라우팅 → 위임 불필요
# - 단순 표시/메모 스킬: 출력/저장만 수행 → 위임 불필요
SKIP_AGENT_CHECK = {
    # alias (oocontext/oodev/oofeature/oocheck/oostart 라우팅)
    "ooc", "ood", "oof", "ook", "oos",
    # 단순 표시/메모/도움말
    "oohelp", "oomemo", "oonow", "ooprevious", "ootoken",
}

# 권장 명령어 목록
KNOWN_COMMANDS = [
    "analyze", "build", "implement", "improve", "test",
    "troubleshoot", "document", "cleanup", "design", "git",
    "estimate", "explain", "task", "spawn", "load", "index",
]

def log_ok(msg):   print(f"[OK]   {msg}")
def log_warn(msg): print(f"[WARN] {msg}")
def log_info(msg): print(f"[INFO] {msg}")
def log_err(msg):  print(f"[ERROR] {msg}")


# ─────────────────────────────────────────────
# 분석 함수
# ─────────────────────────────────────────────

def collect_skill_files(skill_name: str = None) -> list[Path]:
    """oo*/SKILL.md 파일 목록 반환 (특정 스킬 지정 가능)"""
    if skill_name:
        target = SKILLS_DIR / skill_name / "SKILL.md"
        if target.exists():
            return [target]
        else:
            log_err(f"스킬 파일 없음: {target}")
            return []
    return sorted(SKILLS_DIR.glob("oo*/SKILL.md"))


def analyze_skill(skill_md: Path) -> dict:
    """단일 SKILL.md 파일 분석"""
    content = skill_md.read_text(encoding="utf-8")
    skill_name = skill_md.parent.name
    issues = []

    # 1. 서브에이전트 활용 분석 (서브에이전트 / 에이전트 활용 둘 다 인정)
    has_agent_section = bool(
        re.search(r"^##.*(?:서브에이전트|에이전트 활용|에이전트 매핑)", content, re.MULTILINE)
    )
    agent_refs = re.findall(r"`([a-z][a-z0-9\-]+)`", content)
    used_agents = [a for a in agent_refs if a in KNOWN_AGENTS]

    # 병렬 처리 언급 여부
    has_parallel = bool(re.search(r"병렬|parallel|run_in_background|O\s*$", content, re.MULTILINE))

    # 2. 명령어 활용 분석
    has_command_section = bool(re.search(r"^##.*관련 명령어|^>.*관련 명령어", content, re.MULTILINE))
    used_commands = [c for c in KNOWN_COMMANDS if c in content]

    # 3. 이슈 식별 (alias/단순 표시 스킬은 서브에이전트 섹션 검증 제외)
    if not has_agent_section and not used_agents and skill_name not in SKIP_AGENT_CHECK:
        issues.append("서브에이전트 섹션/참조 없음 → 에이전트 활용 검토")

    if has_agent_section and not has_parallel:
        issues.append("병렬 처리 미언급 → Task(run_in_background=true) 활용 검토")

    if not used_commands:
        issues.append("sc/ 명령어 참조 없음 → 관련 명령어 섹션 추가 검토")

    # 4. 크기 정보
    lines = len(content.splitlines())
    ko_chars = len(re.findall(r'[가-힣]', content))
    en_chars = len(content) - ko_chars
    tokens = ko_chars // 2 + en_chars // 4

    return {
        "name": skill_name,
        "path": skill_md,
        "lines": lines,
        "tokens": tokens,
        "has_agent_section": has_agent_section,
        "used_agents": used_agents,
        "has_parallel": has_parallel,
        "has_command_section": has_command_section,
        "used_commands": used_commands,
        "issues": issues,
    }


# ─────────────────────────────────────────────
# 서브명령어 구현
# ─────────────────────────────────────────────

def cmd_status():
    """status - 서브명령어 목록, 스킬 현황, 최적화 요약"""
    print("# ooskill status\n")
    print(f"실행: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    # 서브명령어 목록
    print("## 서브명령어\n")
    print("| 명령어 | 설명 |")
    print("|--------|------|")
    print("| `ooskill status`        | 현황 요약 (이 화면) |")
    print("| `ooskill version`       | 버전 정보 (v01) |")
    print("| `ooskill validate`      | 서브에이전트/명령어 최적화 검증 |")
    print("| `ooskill run`           | 전체 스킬 자동 최적화 |")
    print("| `ooskill run [스킬명]`  | 특정 스킬만 최적화 |")
    print()

    # 스킬 현황
    skill_files = collect_skill_files()
    print(f"## 스킬 현황\n")
    print(f"- 총 스킬 수: {len(skill_files)}개")

    if skill_files:
        total_lines = 0
        total_tokens = 0
        issue_count = 0

        for sf in skill_files:
            info = analyze_skill(sf)
            total_lines += info["lines"]
            total_tokens += info["tokens"]
            issue_count += len(info["issues"])

        avg_tokens = total_tokens // len(skill_files) if skill_files else 0
        print(f"- 총 라인 수: {total_lines:,}줄")
        print(f"- 총 토큰 추정: {total_tokens:,} 토큰")
        print(f"- 스킬당 평균: {avg_tokens:,} 토큰")
        print(f"- 최적화 이슈: {issue_count}건\n")

        # 크기 상위 5개
        top5 = sorted(skill_files, key=lambda f: f.stat().st_size, reverse=True)[:5]
        print("## 크기 상위 5개\n")
        print(f"{'스킬':<22} {'토큰':>6} {'라인':>5}")
        print("-" * 36)
        for sf in top5:
            info = analyze_skill(sf)
            print(f"{info['name']:<22} {info['tokens']:>6,} {info['lines']:>5}")
        print()

        # 최적화 요약
        print("## 최적화 요약\n")
        skills_no_agent = sum(
            1 for sf in skill_files
            if not analyze_skill(sf)["has_agent_section"]
            and sf.parent.name not in SKIP_AGENT_CHECK
        )
        skills_no_parallel = sum(
            1 for sf in skill_files
            if analyze_skill(sf)["has_agent_section"] and not analyze_skill(sf)["has_parallel"]
        )
        skills_no_cmd = sum(1 for sf in skill_files if not analyze_skill(sf)["used_commands"])

        print(f"| 항목 | 해당 스킬 | 권장 조치 |")
        print(f"|------|----------|-----------|")
        print(f"| 에이전트 섹션 없음 | {skills_no_agent}개 | 서브에이전트 활용 검토 |")
        print(f"| 병렬처리 미언급   | {skills_no_parallel}개 | run_in_background 추가 |")
        print(f"| sc/ 명령어 미참조 | {skills_no_cmd}개 | 관련 명령어 섹션 추가 |")
        print()
        print(f"[TIP] `ooskill validate` 로 상세 분석 / `ooskill run` 으로 자동 최적화")

    return 0


def cmd_version():
    """version - 스킬 버전 정보"""
    print("# ooskill version\n")
    print("버전: v04")
    print("설명: oo SKILL.md 서브에이전트/명령어 최적화 검증 스킬")
    print(f"위치: .claude/skills/ooskill/")
    return 0


def cmd_validate(skill_name: str = None):
    """validate - 최적화 기회 식별 및 개선 권장사항 출력"""
    print("# ooskill validate\n")

    skill_files = collect_skill_files(skill_name)
    if not skill_files:
        return 1

    print(f"대상: {len(skill_files)}개 SKILL.md\n")

    results = [analyze_skill(sf) for sf in skill_files]
    issues_found = [r for r in results if r["issues"]]

    if not issues_found:
        log_ok("모든 스킬이 최적화 기준을 충족합니다.")
        return 0

    print(f"## 최적화 기회: {len(issues_found)}개 스킬\n")
    print(f"{'스킬':<22} {'토큰':>6} {'에이전트':^6} {'병렬':^4} {'명령어':^6}  이슈")
    print("-" * 80)

    for r in results:
        agent_mark = "O" if r["has_agent_section"] else "X"
        parallel_mark = "O" if r["has_parallel"] else "-"
        cmd_mark = "O" if r["used_commands"] else "X"
        issue_str = "; ".join(r["issues"]) if r["issues"] else "OK"
        flag = " !" if r["issues"] else ""
        print(f"{r['name']:<22} {r['tokens']:>6,}  {agent_mark:^6} {parallel_mark:^4} {cmd_mark:^6}  {issue_str[:40]}{flag}")

    print()
    print("## 개선 권장사항\n")

    # 에이전트 미활용 (alias/단순 표시 스킬은 제외)
    no_agent = [
        r for r in results
        if not r["has_agent_section"]
        and not r["used_agents"]
        and r["name"] not in SKIP_AGENT_CHECK
    ]
    if no_agent:
        print(f"### 서브에이전트 미활용 ({len(no_agent)}개)\n")
        for r in no_agent:
            print(f"  - `{r['name']}`: 서브에이전트 섹션 추가 권장")
            print(f"    → 분석/탐색: `Explore`, 구현: `task-executor`, 검증: `task-checker`")
        print()

    # 병렬 처리 미언급
    no_parallel = [r for r in results if r["has_agent_section"] and not r["has_parallel"]]
    if no_parallel:
        print(f"### 병렬 처리 미언급 ({len(no_parallel)}개)\n")
        for r in no_parallel:
            print(f"  - `{r['name']}`: 병렬 처리 여부 명시 권장")
            print(f"    → 에이전트 테이블에 '병렬' 열 추가, `Task(run_in_background=true)` 활용")
        print()

    # sc/ 명령어 미참조
    no_cmd = [r for r in results if not r["used_commands"]]
    if no_cmd:
        print(f"### sc/ 명령어 미참조 ({len(no_cmd)}개)\n")
        for r in no_cmd:
            print(f"  - `{r['name']}`: 관련 명령어 참조 추가 권장")
        print()

    print(f"[TIP] `ooskill run` 으로 자동 최적화 적용 가능")
    return 0


def cmd_validate_checklist(fix: bool = False):
    """validate-checklist - 모든 oo* 스킬의 checklist.md 표준 포맷 검증"""
    import re as _re
    print("[ooskill validate-checklist]\n")

    # checklist.md 검증 제외 대상
    # - alias 스킬: 단순 라우팅만 수행, 독자 checklist 불필요
    # - 단순 메모/표시 스킬: 자가 건강 점검할 상태 없음
    SKIP_CHECKLIST = {"ooc", "ood", "oof", "ook", "oos", "oomemo"}

    skills = sorted([d for d in SKILLS_DIR.iterdir() if d.is_dir() and d.name.startswith("oo")])
    TABLE_HEADER = "| ID | 항목 | 검증 내용 | 심각도 |"
    VALID_SEV = {"CRITICAL", "ERROR", "WARNING", "INFO"}

    rows = []
    pass_count = warn_count = fail_count = skip_count = 0

    for skill_dir in skills:
        skill = skill_dir.name

        if skill in SKIP_CHECKLIST:
            rows.append((skill, "SKIP", "-", "-", "-", "-", "-", "SKIP"))
            skip_count += 1
            continue

        checklist = skill_dir / "references" / "checklist.md"

        if not checklist.exists():
            rows.append((skill, "FAIL", "-", "-", "-", "-", "0", "FAIL"))
            fail_count += 1
            continue

        content = checklist.read_text(encoding="utf-8")
        has_c01 = "| C01 |" in content
        has_c02 = "| C02 |" in content
        has_table = TABLE_HEADER in content
        sev_vals = _re.findall(r'\|\s*(CRITICAL|ERROR|WARNING|INFO)\s*\|', content)
        item_count = len(_re.findall(r'^\| C\d+', content, _re.MULTILINE))

        c01_s = "OK" if has_c01 else "FAIL"
        c02_s = "OK" if has_c02 else "FAIL"
        table_s = "OK" if has_table else "WARN"
        sev_s = "OK" if sev_vals else "WARN"

        is_fail = not has_c01 or not has_c02
        # 항목 수 범위: 3~20 (스킬 복잡도에 따라 유연 허용)
        is_warn = not has_table or not sev_vals or item_count < 3 or item_count > 20
        if is_fail:
            result, fail_count = "FAIL", fail_count + 1
        elif is_warn:
            result, warn_count = "WARN", warn_count + 1
        else:
            result, pass_count = "PASS", pass_count + 1

        rows.append((skill, "OK", c01_s, c02_s, table_s, sev_s, str(item_count), result))

    print("| 스킬 | 파일 | C01 | C02 | 테이블 | 심각도 | 항목수 | 결과 |")
    print("|------|------|-----|-----|--------|--------|--------|------|")
    for r in rows:
        print(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} |")
    summary = f"\n소계: PASS:{pass_count} | WARN:{warn_count} | FAIL:{fail_count}"
    if skip_count:
        summary += f" | SKIP:{skip_count} (alias/memo)"
    print(summary)
    return 0


def _parse_frontmatter(content: str) -> dict:
    """SKILL.md YAML frontmatter 파싱 (name, description, category, version)"""
    result = {}
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        return result
    fm = fm_match.group(1)
    for field in ('name', 'description', 'version', 'category'):
        m = re.search(rf'^  {field}:\s*["\']?(.+?)["\']?\s*$', fm, re.MULTILINE)
        if not m:
            m = re.search(rf'^{field}:\s*["\']?(.+?)["\']?\s*$', fm, re.MULTILINE)
        if m:
            result[field] = m.group(1).strip().strip('"\'')
    return result


def _collect_all_skills() -> list[dict]:
    """모든 스킬 스캔 (oo* + alias 포함)"""
    skills = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        content = skill_md.read_text(encoding="utf-8")
        fm = _parse_frontmatter(content)
        if not fm.get('name'):
            continue
        is_alias = 'alias' in fm.get('description', '').lower()
        skills.append({
            'name': fm.get('name', skill_dir.name),
            'description': fm.get('description', ''),
            'category': fm.get('category', 'unknown'),
            'version': fm.get('version', '-'),
            'is_alias': is_alias,
            'path': skill_md,
        })
    return skills


def cmd_update(dry_run: bool = False):
    """update - 스킬 현황 재스캔 → CLAUDE.md 카탈로그 현행화"""
    mode = "[DRY-RUN]" if dry_run else ""
    print(f"# ooskill update {mode}\n")
    print(f"실행: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    all_skills = _collect_all_skills()
    oo_skills = [s for s in all_skills if s['name'].startswith('oo') and not s['is_alias']]
    alias_skills = [s for s in all_skills if s['is_alias']]
    other_skills = [s for s in all_skills if not s['name'].startswith('oo') and not s['is_alias']]

    print(f"## 스캔 결과\n")
    print(f"- oo 스킬: {len(oo_skills)}개")
    print(f"- alias 스킬: {len(alias_skills)}개")
    print(f"- 기타 스킬: {len(other_skills)}개")
    print(f"- 합계: {len(all_skills)}개\n")

    # alias 목록 출력
    if alias_skills:
        print(f"## 등록된 Alias\n")
        print(f"| 약어 | 원본 스킬 | 버전 |")
        print(f"|------|----------|------|")
        for s in alias_skills:
            # description에서 원본 스킬명 추출
            orig = re.search(r'^(\w+)\s+스킬의 약어', s['description'])
            orig_name = orig.group(1) if orig else '-'
            print(f"| `{s['name']}` | `{orig_name}` | {s['version']} |")
        print()

    # category별 oo 스킬 분류
    categories = {}
    for s in oo_skills:
        cat = s['category']
        categories.setdefault(cat, []).append(s)

    print(f"## oo 스킬 카탈로그 (카테고리별)\n")
    for cat, skills in sorted(categories.items()):
        print(f"### {cat} ({len(skills)}개)\n")
        print(f"| 스킬 | 버전 | 설명 요약 |")
        print(f"|------|------|----------|")
        for s in sorted(skills, key=lambda x: x['name']):
            desc_short = s['description'][:40] + '...' if len(s['description']) > 40 else s['description']
            print(f"| `{s['name']}` | {s['version']} | {desc_short} |")
        print()

    # CLAUDE.md 카탈로그 갱신
    claude_md = SKILLS_DIR.parent / "CLAUDE.md"
    if not claude_md.exists():
        log_warn(f"CLAUDE.md 없음: {claude_md}")
        return 0

    content = claude_md.read_text(encoding="utf-8")

    # alias 섹션이 없으면 추가 (oo 스킬 시스템 섹션 뒤에)
    alias_section_header = "### alias 스킬"
    if alias_skills and alias_section_header not in content:
        alias_block = f"\n{alias_section_header}\n\n| 약어 | 원본 스킬 |\n|------|----------|\n"
        for s in alias_skills:
            orig = re.search(r'^(\w+)\s+스킬의 약어', s['description'])
            orig_name = orig.group(1) if orig else '-'
            alias_block += f"| `{s['name']}` | `{orig_name}` |\n"

        # "## oo 스킬 시스템" 또는 마지막 oo 스킬 테이블 뒤에 삽입
        insert_marker = re.search(r'\n## (범용 명령어|에이전트)', content)
        if insert_marker:
            pos = insert_marker.start()
            new_content = content[:pos] + alias_block + content[pos:]
        else:
            new_content = content + alias_block

        if not dry_run:
            claude_md.write_text(new_content, encoding="utf-8")
            log_ok(f"CLAUDE.md alias 섹션 추가 ({len(alias_skills)}개)")
        else:
            log_info(f"[DRY-RUN] CLAUDE.md alias 섹션 추가 예정 ({len(alias_skills)}개)")
    elif alias_section_header in content:
        log_ok(f"CLAUDE.md alias 섹션 이미 존재")

    print()
    if dry_run:
        print("[DRY-RUN] 실제 파일 수정 없음. `ooskill update` 로 적용하세요.")
    else:
        print(f"[OK] 인덱스 갱신 완료 ({len(all_skills)}개 스킬)")
    return 0


def cmd_show_checklist():
    """show checklist - references/checklist.md 내용 출력"""
    checklist = SKILLS_DIR / "ooskill" / "references" / "checklist.md"
    if not checklist.exists():
        log_err(f"checklist.md 없음: {checklist}")
        return 1
    print(checklist.read_text(encoding="utf-8"))
    return 0


def cmd_check():
    """check - checklist.md 기반 ooskill 자체 건강 상태 점검"""
    checklist_path = SKILLS_DIR / "ooskill" / "references" / "checklist.md"
    print("[ooskill check]\n")

    results = []

    # C01 필수 파일 존재
    skill_md = SKILLS_DIR / "ooskill" / "SKILL.md"
    results.append(("C01", "필수 파일 존재", "OK" if skill_md.exists() else "ERROR"))

    # C02 버전 일치
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        fm = _parse_frontmatter(content)
        ver_fm = fm.get("version", "").strip("v")
        ver_table = re.search(r'`ooskill version`.*\(v(\d+)\)', content)
        ver_t = ver_table.group(1) if ver_table else None
        results.append(("C02", "버전 일치", "OK" if ver_fm == ver_t else "WARN"))
    else:
        results.append(("C02", "버전 일치", "SKIP"))

    # C03 스킬 디렉터리 스캔
    skills = list(SKILLS_DIR.glob("oo*/SKILL.md"))
    results.append(("C03", "스킬 디렉터리 스캔", f"OK ({len(skills)}개)" if skills else "ERROR"))

    # C04 agents.md 존재
    agents_md = SKILLS_DIR.parent / "agents.md"
    results.append(("C04", "agents.md 존재", "OK" if agents_md.exists() else "WARN"))

    # C05 검증 기준 정의
    results.append(("C05", "검증 기준 정의", "OK" if checklist_path.exists() else "ERROR"))

    # C09 CLAUDE.md 스킬 등록
    claude_md = SKILLS_DIR.parent / "CLAUDE.md"
    if claude_md.exists():
        c = claude_md.read_text(encoding="utf-8")
        unregistered = [sf.parent.name for sf in skills if sf.parent.name not in c]
        results.append(("C09", "CLAUDE.md 스킬 등록",
                        f"OK" if not unregistered else f"WARN ({len(unregistered)}개 미등록)"))
    else:
        results.append(("C09", "CLAUDE.md 스킬 등록", "ERROR (파일 없음)"))

    # C12 help 스크립트화
    run_py = SKILLS_DIR / "ooskill" / "scripts" / "ooskill_run.py"
    if run_py.exists():
        rc = run_py.read_text(encoding="utf-8")
        results.append(("C12", "help 완전스크립트화",
                        "OK" if "_print_skill_help" in rc else "ERROR"))
    else:
        results.append(("C12", "help 완전스크립트화", "ERROR (스크립트 없음)"))

    # C17 guide.md 존재 및 완전성
    SKIP_GUIDE = {"ooc", "ood", "oof", "ook", "oos", "oohelp", "oomemo", "oonow", "ooprevious", "ootoken"}
    target_skill_dirs = sorted([
        d for d in SKILLS_DIR.iterdir()
        if d.is_dir() and d.name.startswith("oo") and d.name not in SKIP_GUIDE
    ])
    missing_guide = []
    thin_guide = []
    for sd in target_skill_dirs:
        guide = sd / "references" / "guide.md"
        if not guide.exists():
            missing_guide.append(sd.name)
        else:
            gc = guide.read_text(encoding="utf-8")
            if len(gc.splitlines()) < 30 or "```" not in gc:
                thin_guide.append(sd.name)
    if missing_guide:
        short = missing_guide[:5]
        suffix = f"...외 {len(missing_guide)-5}개" if len(missing_guide) > 5 else ""
        c17_status = f"WARN ({len(missing_guide)}개 누락: {', '.join(short)}{suffix})"
    elif thin_guide:
        c17_status = f"INFO ({len(thin_guide)}개 내용 빈약: {', '.join(thin_guide[:3])})"
    else:
        c17_status = "OK"
    results.append(("C17", "guide.md 존재 및 완전성", c17_status))

    # C18 SKILL.md/guide.md 역할 분리
    # ① guide.md에 ## 서브명령어 섹션 존재 → 명령어 목록 중복 (WARN)
    # ② SKILL.md 코드블록 ≥10 → guide.md 분리 권장 (INFO)
    c18_warn = []
    c18_info = []
    for sd in target_skill_dirs:
        skill_md = sd / "SKILL.md"
        guide_md = sd / "references" / "guide.md"
        if not skill_md.exists() or not guide_md.exists():
            continue
        sc = skill_md.read_text(encoding="utf-8")
        gc = guide_md.read_text(encoding="utf-8")
        # ① guide.md에 서브명령어 섹션 헤더 존재
        has_cmd_section = bool(re.search(r'^## (?:서브명령어|명령어)\s*$', gc, re.MULTILINE))
        # ② SKILL.md 코드블록 수 (15개 이상 WARN, 10~14개 INFO)
        code_blocks = len(re.findall(r'```', sc))
        if has_cmd_section:
            c18_warn.append(sd.name)
        elif code_blocks >= 15:
            c18_warn.append(f"{sd.name}({code_blocks}개)")
        elif code_blocks >= 10:
            c18_info.append(f"{sd.name}({code_blocks}개)")
    if c18_warn:
        short = c18_warn[:5]
        suffix = f"...외 {len(c18_warn)-5}개" if len(c18_warn) > 5 else ""
        c18_status = f"WARN ({len(c18_warn)}개: {', '.join(short)}{suffix}) — guide.md로 코드블록 이동 필요"
    elif c18_info:
        short = c18_info[:4]
        suffix = f"...외 {len(c18_info)-4}개" if len(c18_info) > 4 else ""
        c18_status = f"INFO (코드블록 10~14개 {len(c18_info)}개: {', '.join(short)}{suffix})"
    else:
        c18_status = "OK"
    results.append(("C18", "SKILL.md/guide.md 역할 분리", c18_status))

    ok = warn = info = err = 0
    for cid, label, status in results:
        tag = "[OK]  " if status.startswith("OK") else ("[WARN] " if status.startswith("WARN") else ("[INFO] " if status.startswith("INFO") else "[ERROR]"))
        print(f"{cid} {label:<28} {tag} {status}")
        if status.startswith("OK"):     ok += 1
        elif status.startswith("WARN"): warn += 1
        elif status.startswith("INFO"): info += 1
        else: err += 1

    info_part = f" | INFO:{info}" if info else ""
    print(f"\n소계: OK:{ok} | WARN:{warn}{info_part} | ERROR:{err}")
    return 0


def cmd_run(skill_name: str = None, dry_run: bool = False):
    """run - 자동 최적화 수행 후 스킬 인덱스 현행화 (update 통합)"""
    target = skill_name or "전체"
    print(f"# ooskill run [{target}]\n")

    skill_files = collect_skill_files(skill_name)
    if not skill_files:
        return 1

    print(f"대상: {len(skill_files)}개 SKILL.md\n")

    modified = 0
    results = []

    for sf in skill_files:
        info = analyze_skill(sf)
        if not info["issues"]:
            continue

        content = sf.read_text(encoding="utf-8")
        original = content
        changes = []

        # 1. 에이전트 섹션에 병렬 열 추가
        if info["has_agent_section"] and not info["has_parallel"]:
            # "| 단계 | 에이전트 | 역할 |" → "| 단계 | 에이전트 | 역할 | 병렬 |" 로 업그레이드
            content, changed = _add_parallel_column(content)
            if changed:
                changes.append("에이전트 테이블 병렬 열 추가")

        # 2. sc/ 명령어 섹션 추가 (관련 명령어가 아예 없을 때)
        if not info["used_commands"] and not info["has_command_section"]:
            content, changed = _add_related_commands_hint(content, info["name"])
            if changed:
                changes.append("관련 명령어 참조 추가")

        if changes:
            sf.write_text(content, encoding="utf-8")
            modified += 1
            results.append((info["name"], changes))
            log_ok(f"{info['name']}: {', '.join(changes)}")
        else:
            log_info(f"{info['name']}: 자동 수정 불가 (수동 검토 필요)")

    print()
    print("=" * 60)
    print(f"완료: {modified}개 스킬 수정됨\n")

    if results:
        print("## 수정 내역\n")
        for name, changes in results:
            print(f"  - `{name}`: {', '.join(changes)}")
    else:
        print("[INFO] 자동 수정 가능한 항목 없음.")
        print("[TIP] `ooskill validate` 로 수동 개선 권장사항 확인")

    # 분리 원칙: run은 배치 실행만 수행. 현행화는 `ooskill update`로 별도 실행.
    if modified > 0:
        print()
        print("[TIP] CLAUDE.md 카탈로그 및 기타 현행화는 `ooskill update` 실행")

    return 0


# ─────────────────────────────────────────────
# 헬퍼: 자동 수정 함수
# ─────────────────────────────────────────────

def _add_parallel_column(content: str) -> tuple[str, bool]:
    """서브에이전트 섹션 테이블에 병렬 열 추가 (열 이름/개수 무관하게 처리)"""
    # 서브에이전트 섹션 찾기 (## N. 서브에이전트 또는 ## 서브에이전트 활용 등)
    section_match = re.search(r'^##[^\n]*(?:서브에이전트|에이전트 활용)[^\n]*$', content, re.MULTILINE)
    if not section_match:
        return content, False

    section_start = section_match.end()
    next_section = re.search(r'^##', content[section_start:], re.MULTILINE)
    section_end = section_start + next_section.start() if next_section else len(content)
    section_content = content[section_start:section_end]

    # 테이블 헤더 + 구분선 찾기 (임의 열 이름)
    header_match = re.search(r'^(\|(?:[^|\n]+\|)+)\n(\|(?:[-:| ]+\|)+)', section_content, re.MULTILINE)
    if not header_match:
        return content, False

    header_line = header_match.group(1)
    sep_line = header_match.group(2)

    # 이미 병렬 있으면 skip
    if '병렬' in header_line:
        return content, False

    # 새 헤더/구분선 구성 (끝 | 앞에 병렬 열 추가)
    new_header = header_line.rstrip() + " 병렬 |"
    new_sep = sep_line.rstrip() + ":----:|"
    orig_pipe_count = header_line.count('|')  # 원래 헤더의 | 개수

    # 섹션 내 헤더/구분선 교체
    new_section = (
        section_content[:header_match.start()]
        + new_header + "\n" + new_sep
        + section_content[header_match.end():]
    )

    # 구분선 이후 데이터 행에 " - |" 추가 (원래 헤더와 | 개수 같은 행)
    sep_pos = new_section.find(new_sep) + len(new_sep)
    before_data = new_section[:sep_pos]
    data_part = new_section[sep_pos:]

    def add_parallel_cell(m):
        line = m.group(0)
        if line.count('|') == orig_pipe_count:
            return line.rstrip() + " - |"
        return line

    data_part = re.sub(r'^\|[^\n]+\|$', add_parallel_cell, data_part, flags=re.MULTILINE)
    new_section = before_data + data_part

    new_content = content[:section_start] + new_section + content[section_end:]
    return new_content, True


def _add_related_commands_hint(content: str, skill_name: str) -> tuple[str, bool]:
    """관련 명령어 참조 1줄 추가 (마지막 섹션 앞)"""
    # 이미 있으면 skip
    if "관련 명령어" in content:
        return content, False

    # sc/ 명령어 추론 (스킬 이름 기반)
    cmd_map = {
        "oocheck": "analyze, troubleshoot",
        "oofix":   "improve, troubleshoot",
        "oodev":   "implement, build",
        "ootest":  "test",
        "oolib":   "cleanup, analyze",
        "oodb":    "analyze, design",
        "ooprd":   "design",
        "ooplan":  "design, task",
        "oodoc":   "document",
        "oocommit":"git",
    }
    cmds = cmd_map.get(skill_name, "analyze, implement")
    hint = f"\n> **관련 명령어**: {cmds} (`.claude/commands/sc/`)\n"

    # 마지막 ## 섹션 앞에 삽입
    last_section = list(re.finditer(r'\n## ', content))
    if last_section:
        insert_pos = last_section[-1].start()
        new_content = content[:insert_pos] + hint + content[insert_pos:]
        return new_content, True

    # 없으면 파일 끝에 추가
    return content.rstrip() + "\n" + hint, True


# ─────────────────────────────────────────────
# main
# ─────────────────────────────────────────────

def main():
    if not sys.argv[1:]:
        sys.argv.append("run")

    print(f"Log started at {datetime.now()}")

    args = sys.argv[1:]
    if not args:
        cmd_status()
        return 0

    cmd = args[0].lower()
    cmd_args = [a for a in args[1:] if not a.startswith("--")]

    if cmd == "status":
        return cmd_status()
    elif cmd == "version":
        return cmd_version()
    elif cmd == "validate":
        skill_name = cmd_args[0] if cmd_args else None
        return cmd_validate(skill_name)
    elif cmd == "validate-checklist":
        fix = "--fix" in args
        return cmd_validate_checklist(fix)
    elif cmd == "run":
        skill_name = cmd_args[0] if cmd_args else None
        dry_run = "--dry-run" in args
        return cmd_run(skill_name, dry_run=dry_run)
    elif cmd == "show":
        sub = cmd_args[0] if cmd_args else ""
        if sub == "checklist":
            return cmd_show_checklist()
        else:
            log_err(f"알 수 없는 show 대상: {sub} (사용 가능: checklist)")
            return 1
    elif cmd == "check":
        return cmd_check()
    elif cmd == "update":
        import subprocess
        scripts_dir = Path(__file__).parent
        dry_run = "--dry-run" in args
        forward = [a for a in args[1:] if a.startswith("--")]
        target = cmd_args[0] if cmd_args else None

        # 업데이트 타겟 레지스트리
        # "func": 내부 함수 호출 (dry_run 인자 전달)
        # "script": 외부 스크립트 실행 (플래그 forward)
        UPDATE_TARGETS = {
            "catalog": {
                "kind": "func",
                "call": lambda: cmd_update(dry_run=dry_run),
                "desc": "CLAUDE.md 스킬 카탈로그 현행화 (alias 섹션 포함)",
            },
            "run-update-ref": {
                "kind": "script",
                "script": "ooskill_run_update_ref.py",
                "desc": "모든 oo* 스킬에 run/update 분리 원칙 참조 블록 삽입/갱신",
            },
            "gemma": {
                "kind": "script",
                "script": "ooskill_gemma_ref.py",
                "desc": "모든 oo* 스킬에 Gemma 위임 참조 블록 삽입/갱신",
            },
        }

        def _run_target(name: str) -> int:
            t = UPDATE_TARGETS[name]
            if t["kind"] == "func":
                return t["call"]() or 0
            return subprocess.call(
                [sys.executable, str(scripts_dir / t["script"]), *forward]
            )

        if target is None:
            print(f"# ooskill update (전체 현행화){'  [DRY-RUN]' if dry_run else ''}")
            print()
            print(f"등록된 타겟: {len(UPDATE_TARGETS)}개")
            print()
            rc = 0
            for name, meta in UPDATE_TARGETS.items():
                print(f"## [{name}] {meta['desc']}")
                print()
                result = _run_target(name)
                print()
                if result != 0:
                    rc = result
            return rc

        if target not in UPDATE_TARGETS:
            log_err(f"알 수 없는 update 타겟: {target}")
            print(f"사용 가능: {', '.join(UPDATE_TARGETS.keys())}")
            return 1

        return _run_target(target)
    elif cmd in ("-h", "--help", "help"):
        _print_skill_help("ooskill")
        return 0
    else:
        log_err(f"알 수 없는 서브명령어: {cmd}")
        show_help_if_no_args("ooskill", [])
        return 1


if __name__ == "__main__":
    sys.exit(main())
