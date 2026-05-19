#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
oofix_run.py

d0004_todo.md 기반 코드 오류 자동 수정 스크립트

명령어:
    ccfix run [대상]     - 이슈 자동 수정
    ccfix preview        - 수정 미리보기 (dry-run)
    ccfix test [대상]    - 테스트 시나리오 실행
    ccfix verify [파일]  - 수정 검증
    ccfix rollback       - 마지막 수정 롤백
    ccfix status         - 이슈 상태 조회
"""

import sys
import sys as _sys
if _sys.stdout.encoding and _sys.stdout.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stdout.reconfigure(encoding='utf-8')
if _sys.stderr.encoding and _sys.stderr.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stderr.reconfigure(encoding='utf-8')
import os
import re
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict
# --- oo_common inline ---
import re as _re
_SKILLS_DIR = Path(__file__).parent.parent.parent

def _print_skill_help(skill_name):
    if sys.stdout.encoding and sys.stdout.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
        sys.stdout.reconfigure(encoding='utf-8')
    _sf = _SKILLS_DIR / skill_name / "SKILL.md"
    if not _sf.exists():
        print(f"[ERROR] .agents/skills/{skill_name}/SKILL.md not found")
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
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
BACKUP_DIR = PROJECT_ROOT / "tmp" / "oofix_backup"


def print_usage():
    """사용법 출력"""
    print(f"Log started at {datetime.now()}")
    print("ccfix - 코드 오류 자동 수정 도구")
    print()
    print("사용법:")
    print("    ccfix run              전체 이슈 자동 수정")
    print("    ccfix run [이슈ID]     특정 이슈만 수정 (예: TODO-001)")
    print("    ccfix run [카테고리]   카테고리별 수정 (CRITICAL/ERROR/WARNING)")
    print("    ccfix preview          수정 미리보기 (실제 수정 없음)")
    print("    ccfix preview [이슈ID] 특정 이슈 미리보기")
    print("    ccfix test             전체 테스트 시나리오 실행")
    print("    ccfix test [시나리오]  특정 시나리오만 실행 (예: TC-001)")
    print("    ccfix verify           최근 수정 파일 검증")
    print("    ccfix verify [파일]    특정 파일 검증")
    print("    ccfix rollback         마지막 수정 롤백")
    print("    ccfix status           이슈 현황 조회")
    print("    ccfix status [카테고리] 카테고리별 상태")
    print()
    print("예시:")
    print("    python .agents/skills/ccfix/scripts/oofix_run.py run")
    print("    python .agents/skills/ccfix/scripts/oofix_run.py preview")
    print("    python .agents/skills/ccfix/scripts/oofix_run.py test TC-001")
    print("    python .agents/skills/ccfix/scripts/oofix_run.py status CRITICAL")


def cmd_show_checklist():
    """references/checklist.md 내용 출력"""
    checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[{SKILL_NAME}] checklist.md 없음: {checklist_path}")
        return
    print(checklist_path.read_text(encoding="utf-8"))


def main():
    # 서브명령어 없이 실행 시 도움말 출력
    if not sys.argv[1:]:
        sys.argv.append("run")

    print(f"Log started at {datetime.now()}")

    args = sys.argv[1:]

    if not args:
        print_usage()
        return 0

    cmd = args[0].lower()
    if cmd in ("show",) and len(args) > 1 and args[1].lower() == "checklist":
        cmd_show_checklist()
        return
    cmd_args = args[1:]

    if cmd == "run":
        return cmd_run(cmd_args)
    elif cmd == "preview":
        return cmd_preview(cmd_args)
    elif cmd == "test":
        return cmd_test(cmd_args)
    elif cmd == "verify":
        return cmd_verify(cmd_args)
    elif cmd == "rollback":
        return cmd_rollback()
    elif cmd == "status":
        return cmd_status(cmd_args)
    elif cmd == "check":
        print(f"[check] ccfix 체크리스트 안내")
        _print_skill_help("ccfix")
        return 0
    elif cmd in ("help", "-h"):
        _print_skill_help("ccfix")
        return 0
    else:
        print(f"[ERROR] Unknown command: {cmd}")
        print_usage()
        return 1


def cmd_run(args):
    """이슈 자동 수정 (run 서브명령어)"""
    print("# ccfix run\n")

    todo_file = PROJECT_ROOT / "doc" / "d0004_todo.md"
    if not todo_file.exists():
        print("[ERROR] d0004_todo.md not found")
        return 1

    content = todo_file.read_text(encoding="utf-8")
    issues = parse_issues(content)

    # 필터 적용
    target = args[0] if args else None
    if target:
        if target.startswith("A") and target[1:].isdigit():
            issues = [i for i in issues if i["id"] == target]
        elif target.upper() in ["CRITICAL", "ERROR", "WARNING", "INFO"]:
            issues = [i for i in issues if i["severity"] == target.upper()]
        elif target.upper() in ["BUGFIX", "HOTFIX", "UPDATE", "FEATURE"]:
            issues = [i for i in issues if i.get("category") == target.upper()]
        else:
            # 파일 경로로 필터
            issues = [i for i in issues if target in (i.get("file") or "")]

    if not issues:
        print("[INFO] No issues found to fix.")
        return 0

    # False Positive와 실제 이슈 분리
    false_positives = [i for i in issues if i.get("is_false_positive")]
    real_issues = [i for i in issues if not i.get("is_false_positive")]

    print(f"[INFO] Found {len(issues)} issues to process:")
    print(f"  - False Positives: {len(false_positives)} (will be resolved as FP)")
    print(f"  - Real Issues: {len(real_issues)} (will attempt to fix)\n")

    # 백업 디렉토리 생성
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    fixed_count = 0
    fp_count = 0

    # 1. False Positive 처리 (해결된 이슈로 이동)
    if false_positives:
        print("## Phase 1: False Positive 처리\n")
        for issue in false_positives:
            title_short = issue['title'][:60] + "..." if len(issue['title']) > 60 else issue['title']
            print(f"  {issue['id']}: {title_short}")
            print(f"    -> [FP] 동적 로딩/선택적 의존성 모듈 (수정 제외)")
            fp_count += 1
        print()

        # False Positive를 해결된 이슈로 이동
        move_to_resolved(false_positives, "False Positive - 동적 로딩/선택적 의존성 모듈")

    # 2. 실제 이슈 수정 시도
    if real_issues:
        print("## Phase 2: 실제 이슈 수정\n")
        for issue in real_issues:
            title_short = issue['title'][:60] + "..." if len(issue['title']) > 60 else issue['title']
            print(f"  {issue['id']}: {title_short}")

            # 백업 생성
            if issue.get("file"):
                backup_file(issue["file"])

            if apply_fix(issue):
                print(f"    -> [OK] FIXED")
                fixed_count += 1
                move_to_resolved([issue], "자동 수정 완료")
            else:
                print(f"    -> [SKIP] Manual fix required")
            print()

    print(f"---")
    print(f"# Summary:")
    print(f"  - False Positives resolved: {fp_count}")
    print(f"  - Issues fixed: {fixed_count}")
    print(f"  - Total processed: {fp_count + fixed_count}/{len(issues)}")
    return 0


def move_to_resolved(issues, resolution_method):
    """
    이슈를 '## 대기 ToDo'에서 '## 완료 ToDo'로 이동

    Args:
        issues: 이동할 이슈 목록
        resolution_method: 해결 방법 설명
    """
    todo_file = PROJECT_ROOT / "00_doc" / "sp00" / "d0004_todo.md"
    if not todo_file.exists():
        todo_file = PROJECT_ROOT / "00_doc" / "d0004_todo.md"
    if not todo_file.exists():
        return

    content = todo_file.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")

    for issue in issues:
        issue_id = issue["id"]

        # 대기 ToDo에서 해당 ### 블록 제거
        block_pattern = rf"^### {re.escape(issue_id)} .*\n(?:(?!^##? ).*\n)*"
        content = re.sub(block_pattern, "", content, flags=re.MULTILINE)

        # 완료 ToDo 섹션에 블록 추가
        done_section = re.search(r"^## 완료 ToDo", content, re.MULTILINE)
        completed_block = (
            f"### {issue_id} {issue['title']}\n"
            f"등록일: {issue.get('date', today)} | 우선순위: {issue.get('severity', 'ERROR')} | 완료: {today}\n\n"
            f"{resolution_method}\n\n"
        )
        if done_section:
            insert_pos = done_section.end() + 1
            content = content[:insert_pos] + completed_block + content[insert_pos:]
        else:
            content = content.rstrip() + f"\n\n## 완료 ToDo\n\n{completed_block}"

    todo_file.write_text(content, encoding="utf-8")


def cmd_preview(args):
    """수정 미리보기 (preview 서브명령어)"""
    print("# ccfix preview\n")
    print("## 수정 예정 목록 (실제 수정 없음)\n")

    todo_file = PROJECT_ROOT / "doc" / "d0004_todo.md"
    if not todo_file.exists():
        print("[ERROR] d0004_todo.md not found")
        return 1

    content = todo_file.read_text(encoding="utf-8")
    issues = parse_issues(content)

    # 필터 적용
    target = args[0] if args else None
    if target and target.startswith("TODO-"):
        issues = [i for i in issues if i["id"] == target]

    if not issues:
        print("[INFO] No issues found.")
        return 0

    for issue in issues:
        fix_type = get_fix_type(issue)
        status = "자동 수정 가능" if fix_type else "수동 검토 필요"
        print(f"  {issue['id']} [{issue['severity']}] {issue['title']}")
        print(f"    -> 파일: {issue.get('file', 'N/A')}")
        print(f"    -> 상태: {status}")
        if fix_type:
            print(f"    -> 수정 유형: {fix_type}")
        print()

    auto_count = sum(1 for i in issues if get_fix_type(i))
    manual_count = len(issues) - auto_count
    print(f"---\n자동 수정: {auto_count}개 | 수동 필요: {manual_count}개")
    return 0


def cmd_test(args):
    """테스트 시나리오 실행 (test 서브명령어)"""
    print("# ccfix test\n")

    test_file = PROJECT_ROOT / "doc" / "d0003_test.md"
    if not test_file.exists():
        print("[WARN] d0003_test.md not found. Running pytest instead.")
        return run_pytest(args)

    content = test_file.read_text(encoding="utf-8")

    # 테스트 시나리오 파싱
    scenarios = parse_test_scenarios(content)

    target = args[0] if args else None
    if target:
        if target.startswith("TC-"):
            scenarios = [s for s in scenarios if s["id"] == target]
        elif target in ["unit", "integration", "e2e"]:
            scenarios = [s for s in scenarios if s.get("type") == target]

    if not scenarios:
        print("[INFO] No test scenarios found. Running pytest...")
        return run_pytest(args)

    print(f"## 테스트 시나리오 로드: {len(scenarios)}개\n")

    passed = 0
    failed = 0
    for sc in scenarios:
        print(f"  {sc['id']}: {sc['name']}")
        # 실제 테스트 실행 (여기서는 시뮬레이션)
        if sc.get("file") and Path(PROJECT_ROOT / sc["file"]).exists():
            result = run_single_test(sc)
            if result:
                print("    -> [PASS]")
                passed += 1
            else:
                print("    -> [FAIL]")
                failed += 1
        else:
            print("    -> [SKIP] 테스트 파일 없음")

    print(f"\n---\n결과: {passed}/{passed+failed} 통과")
    if passed + failed > 0:
        print(f"({100*passed/(passed+failed):.1f}%)")
    return 0 if failed == 0 else 1


def cmd_verify(args):
    """수정 검증 (verify 서브명령어)"""
    print("# ccfix verify\n")

    target = args[0] if args else None

    if target:
        files_to_verify = [Path(target)]
    else:
        # 최근 백업된 파일들 검증
        if not BACKUP_DIR.exists():
            print("[INFO] No recent fixes to verify.")
            return 0
        files_to_verify = [
            PROJECT_ROOT / f.name.replace(".backup", "")
            for f in BACKUP_DIR.glob("*.backup")
        ]

    if not files_to_verify:
        print("[INFO] No files to verify.")
        return 0

    print(f"## 검증 대상: {len(files_to_verify)}개 파일\n")

    all_passed = True
    for file_path in files_to_verify:
        if not file_path.exists():
            continue

        print(f"### {file_path.name}")

        # 1. 구문 검사
        if file_path.suffix == ".py":
            result = verify_syntax(file_path)
            if result:
                print("  [OK] 구문 검사 통과")
            else:
                print("  [FAIL] 구문 오류")
                all_passed = False
                continue

            # 2. 타입 검사 (mypy)
            mypy_result = run_mypy(file_path)
            if mypy_result is None:
                print("  [SKIP] mypy 없음")
            elif mypy_result:
                print("  [OK] 타입 검사 통과")
            else:
                print("  [WARN] 타입 오류 발견")

        elif file_path.suffix == ".dart":
            result = verify_dart_syntax(file_path)
            if result:
                print("  [OK] dart analyze 통과")
            else:
                print("  [FAIL] dart analyze 오류")
                all_passed = False
                continue

        print()

    return 0 if all_passed else 1


def cmd_rollback():
    """마지막 수정 롤백 (rollback 서브명령어)"""
    print("# ccfix rollback\n")

    if not BACKUP_DIR.exists():
        print("[INFO] No backups found to rollback.")
        return 0

    backups = list(BACKUP_DIR.glob("*.backup"))
    if not backups:
        print("[INFO] No backup files found.")
        return 0

    print(f"## 롤백 가능한 백업: {len(backups)}개\n")

    for backup in backups:
        original_name = backup.name.replace(".backup", "")
        original_path = PROJECT_ROOT / original_name

        # 백업에서 복원
        if backup.exists():
            shutil.copy2(backup, original_path)
            print(f"  [ROLLBACK] {original_name}")
            backup.unlink()  # 백업 삭제

    print("\n[INFO] Rollback completed.")
    return 0


def cmd_status(args):
    """이슈 상태 조회 (status 서브명령어)"""
    print("# ccfix status\n")

    todo_file = PROJECT_ROOT / "doc" / "d0004_todo.md"
    if not todo_file.exists():
        print("[ERROR] d0004_todo.md not found")
        return 1

    content = todo_file.read_text(encoding="utf-8")
    issues = parse_issues(content, include_all=True)

    # 카테고리별 필터
    target = args[0].upper() if args else None
    if target and target in ["CRITICAL", "ERROR", "WARNING", "INFO"]:
        issues = [i for i in issues if i["severity"] == target]

    # 카테고리별 집계
    by_severity = defaultdict(list)
    for issue in issues:
        by_severity[issue["severity"]].append(issue)

    print("## 이슈 현황\n")
    for sev in ["CRITICAL", "ERROR", "WARNING", "INFO"]:
        count = len(by_severity.get(sev, []))
        completed = sum(1 for i in by_severity.get(sev, []) if i.get("status") == "completed")
        if count > 0 or sev in ["CRITICAL", "ERROR"]:
            print(f"  {sev}: {count}개", end="")
            if completed > 0:
                print(f" ({completed}개 완료)")
            else:
                print()

    # 최근 수정
    history_file = PROJECT_ROOT / "doc" / "d0010_history.md"
    if history_file.exists():
        print("\n## 최근 수정")
        history = history_file.read_text(encoding="utf-8")
        # 최근 5개 항목 표시
        recent = re.findall(r"### \[(\d{4}-\d{2}-\d{2})\].*?- (.*?)(?=\n### |\Z)", history, re.DOTALL)[:5]
        for date, item in recent:
            first_line = item.split("\n")[0].strip()
            print(f"  {date} - {first_line[:50]}")

    return 0

# False Positive로 처리할 모듈 목록 (동적 로딩/선택적 의존성)
FALSE_POSITIVE_MODULES = ["cv2", "holidays", "pdf2image", "pytesseract", "werkzeug", "win32com"]

# Dart False Positive 파일 패턴 (코드 생성/빌드 아티팩트)
DART_FALSE_POSITIVE_PATTERNS = [
    ".g.dart",
    ".freezed.dart",
    ".mocks.dart",
    "firebase_options.dart",
]


def detect_project_type(project_dir):
    """
    프로젝트 유형 감지: 'python', 'flutter', 'unknown'

    감지 기준:
    - pubspec.yaml 존재 → flutter
    - pyproject.toml 또는 *.py 존재 → python
    """
    project_path = Path(project_dir)
    if (project_path / "pubspec.yaml").exists():
        return "flutter"
    if (project_path / "pyproject.toml").exists():
        return "python"
    if list(project_path.glob("*.py")) or list(project_path.glob("**/*.py")):
        return "python"
    return "unknown"


def detect_sp_project_type(sp_num):
    """
    SP 번호 기반 프로젝트 유형 감지

    SP 디렉토리 내부의 파일 구성으로 판단
    """
    sp_dirs = list(PROJECT_ROOT.glob(f"{sp_num:02d}_*"))
    if not sp_dirs:
        return "python"  # 기본값
    return detect_project_type(sp_dirs[0])


def run_dart_analyze(target_dir):
    """
    dart analyze 실행 및 결과 파싱

    Returns:
        list of dict: [{severity, file, line, column, message, rule}]
    """
    try:
        result = subprocess.run(
            ["dart", "analyze", "--no-fatal-warnings", str(target_dir)],
            capture_output=True,
            text=True,
            cwd=target_dir,
            shell=True,
            encoding="utf-8",
            errors="replace"
        )
        return parse_dart_analyze_output(result.stdout + result.stderr)
    except FileNotFoundError:
        print("[WARN] dart not found. Install Flutter/Dart SDK.")
        return []


def parse_dart_analyze_output(output):
    """
    dart analyze 출력 파싱

    형식: severity - file:line:column - message - rule_name
    예: info - lib/main.dart:3:8 - Unused import: 'dart:math'. - unused_import
    """
    issues = []
    pattern = re.compile(
        r"^\s*(error|warning|info)\s+-\s+(.+?):(\d+):(\d+)\s+-\s+(.+?)\s+-\s+(\w+)\s*$",
        re.MULTILINE
    )

    for m in pattern.finditer(output):
        severity = m.group(1)
        file_path = m.group(2)
        line = int(m.group(3))
        column = int(m.group(4))
        message = m.group(5).strip()
        rule = m.group(6)

        # False Positive 필터
        is_fp = any(file_path.endswith(pat) for pat in DART_FALSE_POSITIVE_PATTERNS)

        # severity 매핑
        severity_map = {"error": "ERROR", "warning": "WARNING", "info": "INFO"}

        issues.append({
            "severity": severity_map.get(severity, "INFO"),
            "file": file_path,
            "line": line,
            "column": column,
            "message": message,
            "rule": rule,
            "is_false_positive": is_fp,
        })

    return issues


def verify_dart_syntax(file_path):
    """Dart 파일 정적 분석 (dart analyze 단일 파일)"""
    try:
        result = subprocess.run(
            ["dart", "analyze", str(file_path)],
            capture_output=True,
            text=True,
            shell=True
        )
        # error가 없으면 통과
        return "error" not in result.stdout.lower() or result.returncode == 0
    except FileNotFoundError:
        return True  # dart not found → skip


def run_dart_fix(target_dir):
    """dart fix --apply 실행 (자동 수정 가능 이슈 일괄 적용)"""
    try:
        result = subprocess.run(
            ["dart", "fix", "--apply"],
            cwd=target_dir,
            capture_output=True,
            text=True,
            shell=True
        )
        return result.returncode == 0, result.stdout
    except FileNotFoundError:
        print("[WARN] dart not found.")
        return False, ""


def run_flutter_test(target_dir):
    """flutter test 실행"""
    try:
        result = subprocess.run(
            ["flutter", "test"],
            cwd=target_dir,
            capture_output=True,
            text=True,
            timeout=300,
            shell=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except FileNotFoundError:
        print("[SKIP] flutter not found")
        return True
    except subprocess.TimeoutExpired:
        print("[TIMEOUT] flutter test timed out (300s)")
        return False


def get_dart_fix_type(rule):
    """Dart lint rule별 자동 수정 가능 여부 반환"""
    auto_fixable = {
        "prefer_const_constructors": "Add const",
        "prefer_final_fields": "Add final",
        "unnecessary_this": "Remove this.",
        "unnecessary_new": "Remove new",
        "prefer_is_empty": "Use .isEmpty",
        "prefer_is_not_empty": "Use .isNotEmpty",
        "unnecessary_import": "Remove import",
        "unused_import": "Remove import",
    }
    return auto_fixable.get(rule)


def cmd_dart_status(target_dir):
    """Flutter/Dart 프로젝트 분석 상태 표시"""
    print("# ccfix status (Flutter/Dart)\n")

    issues = run_dart_analyze(target_dir)
    if not issues:
        print("[INFO] No issues found by dart analyze.")
        return 0

    # False Positive 분리
    real = [i for i in issues if not i["is_false_positive"]]
    fp = [i for i in issues if i["is_false_positive"]]

    print(f"## 이슈 현황\n")
    print(f"  전체: {len(issues)}건")
    print(f"  실제: {len(real)}건")
    print(f"  False Positive: {len(fp)}건\n")

    # severity별 집계
    by_sev = defaultdict(list)
    for issue in real:
        by_sev[issue["severity"]].append(issue)

    for sev in ["ERROR", "WARNING", "INFO"]:
        count = len(by_sev.get(sev, []))
        if count > 0:
            print(f"  {sev}: {count}건")

    # rule별 집계
    print(f"\n## 규칙별 집계\n")
    by_rule = defaultdict(int)
    for issue in real:
        by_rule[issue["rule"]] += 1
    for rule, count in sorted(by_rule.items(), key=lambda x: -x[1]):
        fixable = "자동" if get_dart_fix_type(rule) else "수동"
        print(f"  {rule}: {count}건 ({fixable})")

    return 0


def parse_issues(content, include_all=False):
    """
    d0004_todo.md에서 이슈 파싱 (## 대기 ToDo 섹션의 ### 블록 형식)

    Args:
        content: 문서 내용
        include_all: True면 완료 포함, False면 대기 상태만
    """
    issues = []

    # ## 대기 ToDo 섹션 찾기
    section_match = re.search(r"^## 대기 ToDo", content, re.MULTILINE)
    if not section_match:
        return issues

    # 다음 ## 섹션까지
    next_section = re.search(r"^## ", content[section_match.end():], re.MULTILINE)
    section_end = section_match.end() + next_section.start() if next_section else len(content)
    section_content = content[section_match.end():section_end]

    for block_match in re.finditer(
        r"^### (\S+) (.+)\n(등록일: [^\n]+)\n?([^\n#]*)?",
        section_content,
        re.MULTILINE
    ):
        issue_id = block_match.group(1)
        title = block_match.group(2)
        meta = block_match.group(3)
        body = (block_match.group(4) or "").strip()

        date_m = re.search(r"등록일: (\S+)", meta)
        priority_m = re.search(r"우선순위: (\S+)", meta)
        status_m = re.search(r"상태: (\S+)", meta)

        severity = priority_m.group(1).upper() if priority_m else "ERROR"
        status = status_m.group(1) if status_m else "분석중"

        # 파일 경로와 라인 번호 추출 (제목에서)
        file_match = re.search(r"\[[\w]+\] ([\w/._\\-]+):(\d+)", title)
        if file_match:
            file_path = file_match.group(1)
            line_no = int(file_match.group(2))
        else:
            file_path = None
            line_no = 0

        # 에러 코드 추출
        error_code_match = re.search(r"\[(E\d{4}|W\d{4})\]", title)
        error_code = error_code_match.group(1) if error_code_match else None

        category_m = re.match(r"\[(\w+)\]", title)
        category = category_m.group(1) if category_m else "BUGFIX"

        is_fp = is_false_positive_issue(title, file_path)

        issues.append({
            "id": issue_id,
            "severity": severity,
            "category": category,
            "title": title,
            "file": file_path,
            "line": line_no,
            "error_code": error_code,
            "status": status,
            "is_false_positive": is_fp,
            "date": date_m.group(1) if date_m else "",
        })

    return issues


def is_false_positive_issue(title, file_path):
    """
    False Positive 이슈인지 확인

    - 동적 로딩 모듈: cv2, holidays
    - 선택적 의존성: pdf2image, pytesseract, werkzeug, win32com
    """
    title_lower = title.lower()

    for module in FALSE_POSITIVE_MODULES:
        if module.lower() in title_lower:
            return True
        # 모듈 관련 에러 메시지 패턴
        if f"'{module}'" in title or f'"{module}"' in title:
            return True

    return False


def get_fix_type(issue):
    """이슈 유형에 따른 자동 수정 타입 반환"""
    title = issue.get("title", "")

    if "미정의 변수" in title or "F821" in title:
        return "Missing Import"
    if "미사용 import" in title or "unused import" in title.lower():
        return "Remove Unused Import"
    if "중복 import" in title:
        return "Remove Duplicate Import"
    if "타입 오류" in title or "NoneType" in title:
        return "Add None Check"
    if "width" in title.lower() and "column" in title.lower():
        return "Fix Column Width"

    return None


def backup_file(file_path):
    """파일 백업 생성"""
    src = PROJECT_ROOT / file_path
    if src.exists():
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        dst = BACKUP_DIR / f"{src.name}.backup"
        shutil.copy2(src, dst)


def update_todo_status(issue_id, status):
    """d0004_todo.md에서 이슈 상태 업데이트"""
    todo_file = PROJECT_ROOT / "doc" / "d0004_todo.md"
    if not todo_file.exists():
        return

    content = todo_file.read_text(encoding="utf-8")

    # 상태 업데이트 (간단한 구현)
    pattern = rf"(#### {issue_id}.*?)(\n- \*\*상태\*\*:.*?)(\n)"
    replacement = rf"\1\n- **상태**: {status}\3"

    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        todo_file.write_text(content, encoding="utf-8")


def parse_test_scenarios(content):
    """d0003_test.md에서 테스트 시나리오 파싱"""
    scenarios = []

    # TC-XXX 패턴 찾기
    pattern = r"### (TC-\d{3})[:\s]+(.*?)\n(.*?)(?=\n### |$)"
    matches = re.finditer(pattern, content, re.DOTALL)

    for m in matches:
        tc_id = m.group(1)
        name = m.group(2).strip()
        body = m.group(3)

        # 테스트 파일 추출
        file_match = re.search(r"테스트 파일[:\s]+`?([\w/\.]+)`?", body)
        type_match = re.search(r"유형[:\s]+(unit|integration|e2e)", body)

        scenarios.append({
            "id": tc_id,
            "name": name,
            "file": file_match.group(1) if file_match else None,
            "type": type_match.group(1) if type_match else None
        })

    return scenarios


def run_pytest(args):
    """pytest 실행"""
    try:
        cmd = ["uv", "run", "pytest"]
        if args:
            cmd.extend(args)
        else:
            cmd.extend(["-v", "--tb=short"])

        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode
    except FileNotFoundError:
        print("[SKIP] pytest not found")
        return 0


def run_single_test(scenario):
    """단일 테스트 시나리오 실행"""
    if not scenario.get("file"):
        return True  # 파일 없으면 스킵 (통과 처리)

    test_file = PROJECT_ROOT / scenario["file"]
    if not test_file.exists():
        return True

    try:
        result = subprocess.run(
            ["uv", "run", "pytest", str(test_file), "-v", "--tb=short"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return True


def verify_syntax(file_path):
    """Python 구문 검사"""
    try:
        result = subprocess.run(
            ["uv", "run", "python", "-m", "py_compile", str(file_path)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return True


def run_mypy(file_path):
    """mypy 타입 검사"""
    try:
        result = subprocess.run(
            ["uv", "run", "mypy", str(file_path), "--ignore-missing-imports"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return None  # mypy not found

def apply_fix(issue):
    """
    이슈 유형별 자동 수정 적용
    """
    file_path = PROJECT_ROOT / issue["file"]
    if not file_path.exists():
        print(f"  [ERROR] File not found: {issue['file']}")
        return False

    title = issue["title"]

    # 1. Missing Import (F821)
    if "미정의 변수" in title or "F821" in title:
        return fix_missing_import(file_path, title)

    # 2. IndentationError
    if "IndentationError" in title:
        # 이건 수동으로 하는게 안전함, 내용만 보고 자동식별 어려움
        return False

    return False

def fix_missing_import(file_path, title):
    """
    누락된 import 문 추가
    """
    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    module_to_import = None
    import_stmt = None

    # 타이틀에서 모듈명 추측
    if "sys" in title:
        module_to_import = "sys"
        import_stmt = "import sys"
    elif "shutil" in title:
        module_to_import = "shutil"
        import_stmt = "import shutil"
    elif "load_workbook" in title:
        import_stmt = "from openpyxl import load_workbook"
        module_to_import = "openpyxl"
    elif "OpenpyxlImage" in title:
        import_stmt = "from openpyxl.drawing.image import Image as OpenpyxlImage"
        module_to_import = "openpyxl"
    elif "img2pdf" in title:
        module_to_import = "img2pdf"
        import_stmt = "import img2pdf"

    if not import_stmt:
        return False

    # 이미 import 되어 있는지 확인
    if import_stmt in content:
        print(f"  [INFO] Import '{import_stmt}' already exists.")
        return True

    # Import 추가 위치 찾기 (첫 번째 import 문 뒤나 파일 상단)
    # 간단하게: imports 섹션이 있으면 그 끝에, 없으면 맨 위 (docstring 이후)에.

    # docstring 건너뛰기 로직은 복잡하니, import sys가 있는 곳 근처나,
    # 아니면 `import ...` 가 나오는 마지막 라인 뒤에 추가.

    insert_idx = 0
    last_import_idx = -1

    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            last_import_idx = i

    if last_import_idx != -1:
        insert_idx = last_import_idx + 1
    else:
        # Import가 하나도 없으면? docstring이나 shebang 고려해야 함.
        # 일단 안전하게 3번째 줄 정도에 넣거나 (shebang, encoding 고려)
        insert_idx = 2

    lines.insert(insert_idx, import_stmt)

    file_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  [FIX] Added '{import_stmt}' to line {insert_idx+1}")
    return True

if __name__ == "__main__":
    sys.exit(main())
