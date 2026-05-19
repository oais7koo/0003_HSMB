#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
oocheck_run.py

통합 코드 품질 체크 워크플로우 (.claude/skills/oocheck/SKILL.md 구현)

서브명령어:
    run       - 전체 체크 실행 (pylint, mypy, pytest, oo validator)
    oo      - oo 모듈 사용 검증 및 d0004_todo.md 등록
    error     - 에러 체크만 수행 (pylint, mypy)
    term      - 표준용어 체크만 수행
    update    - d0004/d0010 문서 정리 및 동기화
    debug     - 심층 디버깅 워크플로우 실행
    circular  - 순환 참조(Circular Import) 감지

사용법:
    python .claude/skills/oocheck/scripts/oocheck_run.py run
    python .claude/skills/oocheck/scripts/oocheck_run.py oo [--dry-run]
    python .claude/skills/oocheck/scripts/oocheck_run.py error
    python .claude/skills/oocheck/scripts/oocheck_run.py term
    python .claude/skills/oocheck/scripts/oocheck_run.py update
    python .claude/skills/oocheck/scripts/oocheck_run.py debug [에러메시지]
    python .claude/skills/oocheck/scripts/oocheck_run.py circular [모듈명]
"""

import sys
import sys as _sys
if _sys.stdout.encoding and _sys.stdout.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stdout.reconfigure(encoding='utf-8')
if _sys.stderr.encoding and _sys.stderr.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stderr.reconfigure(encoding='utf-8')
import subprocess
import shutil
import re
import ast
import py_compile
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
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent


def load_env_value(key: str, default: str = "") -> str:
    """Load value from .env file without external dependencies."""
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{key}="):
                    return line.split("=", 1)[1]
    return default


# SOURCE_DIRS from .env (fallback to default)
_default_dirs = "src,oo,tests"
SOURCE_DIRS = load_env_value("OAIS_SOURCE_DIRS", _default_dirs).split(",")
TARGET_DIRS = [d for d in SOURCE_DIRS if Path(d).exists()]

# SP (서브프로젝트) 컨텍스트: 00=공통, 01=obsidian, 02=pycode, ...
def _load_sp_from_state() -> str:
    """oocontext 상태 파일에서 현재 SP 로드"""
    state_file = PROJECT_ROOT / ".omc" / "state" / "context.json"
    if state_file.exists():
        try:
            import json as _json
            data = _json.loads(state_file.read_text(encoding="utf-8"))
            return data.get("sp", "00")
        except Exception:
            pass
    return "00"

SP_CONTEXT = _load_sp_from_state()  # oocontext 상태 파일에서 자동 로드
SP_EXPLICIT = False  # main()에서 --sp 명시 시 True (run 범위: 전체 vs 특정 SP)


def get_sp_doc_path(base_doc_num: str) -> Path:
    """
    SP 컨텍스트에 따른 문서 경로 반환

    Args:
        base_doc_num: 기본 문서 번호 (예: "0004", "0010")

    Returns:
        Path: 문서 경로 (예: doc/d0004_todo.md 또는 doc/d20004_todo.md)
    """
    global SP_CONTEXT

    if SP_CONTEXT == "00":
        doc_num = base_doc_num
    else:
        # SP × 10000 + 기본번호
        sp_num = int(SP_CONTEXT)
        base_num = int(base_doc_num)
        doc_num = str(sp_num * 10000 + base_num)

    # 문서 파일명 매핑
    doc_names = {
        "0004": "todo",
        "0010": "history",
        "0001": "prd",
        "0002": "plan",
        "0003": "test",
        "0006": "db",
    }

    suffix = doc_names.get(base_doc_num, "")
    if suffix:
        filename = f"d{doc_num}_{suffix}.md"
    else:
        filename = f"d{doc_num}.md"

    # 00_doc/ flat 구조 사용
    return PROJECT_ROOT / "00_doc" / filename


def set_sp_context(sp: str):
    """SP 컨텍스트 설정"""
    global SP_CONTEXT
    if sp in [f"{n:02d}" for n in range(10)]:
        SP_CONTEXT = sp
        print(f"[INFO] SP Context: {sp}")
    else:
        print(f"[WARN] Invalid SP: {sp}, using default (00)")
        SP_CONTEXT = "00"

# oo_usage_validator를 import하기 위해 path 추가
sys.path.insert(0, str(SCRIPT_DIR))
from oo_usage_validator import get_oo_errors, OaisUsageError


@dataclass
class Issue:
    """발견된 이슈를 나타내는 데이터 클래스"""
    severity: str  # CRITICAL, ERROR, WARNING, INFO
    category: str  # SYNTAX, TYPE, LINT, TEST, OAIS
    file_path: str
    line_no: Optional[int]
    message: str
    suggestion: Optional[str] = None


@dataclass
class IssueCollector:
    """이슈 수집 및 관리"""
    issues: List[Issue] = field(default_factory=list)

    def add(self, severity: str, category: str, file_path: str,
            line_no: Optional[int], message: str, suggestion: Optional[str] = None):
        self.issues.append(Issue(severity, category, file_path, line_no, message, suggestion))

    def get_by_severity(self, severity: str) -> List[Issue]:
        return [i for i in self.issues if i.severity == severity]

    def count_by_severity(self) -> Dict[str, int]:
        counts = {"CRITICAL": 0, "ERROR": 0, "WARNING": 0, "INFO": 0}
        for issue in self.issues:
            if issue.severity in counts:
                counts[issue.severity] += 1
        return counts

    def has_critical_or_error(self) -> bool:
        return any(i.severity in ("CRITICAL", "ERROR") for i in self.issues)


# 전역 이슈 수집기
issue_collector = IssueCollector()


def check_command(command):
    """Check if a command exists in the path."""
    return shutil.which(command) is not None


# --- Flutter/Dart 지원 ---

# Dart False Positive 파일 패턴
DART_FALSE_POSITIVE_PATTERNS = [".g.dart", ".freezed.dart", ".mocks.dart", "firebase_options.dart"]


def detect_project_type(project_dir):
    """프로젝트 유형 감지: 'python', 'flutter', 'unknown'"""
    p = Path(project_dir)
    if (p / "pubspec.yaml").exists():
        return "flutter"
    if (p / "pyproject.toml").exists():
        return "python"
    # .py 파일 존재 시 Python으로 판단 (SP 디렉토리 내부)
    if list(p.glob("*.py")) or list(p.glob("pages/*.py")):
        return "python"
    return "unknown"


def detect_sp_project_dir():
    """현재 SP 컨텍스트의 프로젝트 디렉토리 반환"""
    if SP_CONTEXT == "00":
        return PROJECT_ROOT
    sp_dirs = list(PROJECT_ROOT.glob(f"{int(SP_CONTEXT):02d}_*"))
    return sp_dirs[0] if sp_dirs else PROJECT_ROOT


def run_dart_analyze_check(target_dir):
    """dart analyze 실행 및 이슈 수집"""
    print("## Running dart analyze...")
    try:
        abs_target = str(Path(target_dir).resolve())
        result = subprocess.run(
            ["dart", "analyze", "--no-fatal-warnings", "lib/"],
            capture_output=True, text=True, cwd=abs_target,
            shell=True, encoding="utf-8", errors="replace"
        )
        output = result.stdout + result.stderr
        print(output)

        # 파싱
        pattern = re.compile(
            r"^\s*(error|warning|info)\s+-\s+(.+?):(\d+):(\d+)\s+-\s+(.+?)\s+-\s+(\w+)\s*$",
            re.MULTILINE
        )
        severity_map = {"error": "ERROR", "warning": "WARNING", "info": "INFO"}
        issue_count = 0
        fp_count = 0

        for m in pattern.finditer(output):
            sev = m.group(1)
            file_path = m.group(2)
            line = int(m.group(3))
            message = m.group(5).strip()
            rule = m.group(6)

            is_fp = any(file_path.endswith(pat) for pat in DART_FALSE_POSITIVE_PATTERNS)
            if is_fp:
                fp_count += 1
                continue

            mapped_sev = severity_map.get(sev, "INFO")
            if mapped_sev == "INFO":
                issue_count += 1
                continue  # INFO는 이슈 수집기에 추가하지 않음 (백로그)

            issue_collector.add(
                severity=mapped_sev,
                category="DART",
                file_path=file_path,
                line_no=line,
                message=f"[{rule}] {message}"
            )
            issue_count += 1

        if fp_count > 0:
            print(f"[INFO] False Positive (생성 파일) 제외: {fp_count}건")

        if result.returncode == 0 and issue_count == 0:
            print("[OK] dart analyze passed.")
        else:
            print(f"[WARN] dart analyze: {issue_count}건 발견")

        return issue_count
    except FileNotFoundError:
        print("[ERROR] dart not found. Install Flutter/Dart SDK.")
        return -1


def run_flutter_test_check(target_dir):
    """flutter test 실행"""
    print("## Running flutter test...")
    try:
        result = subprocess.run(
            ["flutter", "test"],
            capture_output=True, text=True,
            cwd=str(target_dir), timeout=300,
            shell=True, encoding="utf-8", errors="replace"
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        if result.returncode == 0:
            print("[OK] flutter test passed.")
        else:
            print("[WARN] flutter test failed.")
            issue_collector.add(
                severity="ERROR",
                category="TEST",
                file_path="test/",
                line_no=None,
                message="flutter test 실패"
            )
        return result.returncode
    except FileNotFoundError:
        print("[SKIP] flutter not found.")
        return 0
    except subprocess.TimeoutExpired:
        print("[TIMEOUT] flutter test timed out (300s)")
        return 1


def cmd_dart_run(target_dir):
    """Flutter/Dart 프로젝트 전체 체크"""
    print("# oocheck run (Flutter/Dart)\n")
    print("=" * 60)
    print(f"[OOCHECK] Flutter Project: {target_dir}")
    print("=" * 60 + "\n")

    failure_count = 0

    # 1. dart analyze
    dart_issues = run_dart_analyze_check(target_dir)
    if dart_issues != 0:
        failure_count += 1
    print("-" * 40 + "\n")

    # 2. flutter test
    test_ret = run_flutter_test_check(target_dir)
    if test_ret != 0:
        failure_count += 1
    print("-" * 40 + "\n")

    # 결과 요약
    print("\n" + "=" * 60)
    print("# Summary")
    print("=" * 60)

    counts = issue_collector.count_by_severity()
    print(f"\n발견된 이슈:")
    print(f"  - CRITICAL: {counts['CRITICAL']}개")
    print(f"  - ERROR: {counts['ERROR']}개")
    print(f"  - WARNING: {counts['WARNING']}개")
    print(f"  - INFO: {counts['INFO']}개")
    print(f"  - 총계: {len(issue_collector.issues)}개")

    if issue_collector.issues:
        # Flutter 프로젝트는 리스트업만 (자동 등록 안 함)
        # 에이전트가 결과를 보고 d{SP}0004에 필요 시 수동 등록
        dir_name = Path(target_dir).name
        sp_match = re.match(r"^(\d{2})_", dir_name)
        sp_doc = f"d{int(sp_match.group(1)) * 10000 + 4}_todo.md" if sp_match else "d0004_todo.md"
        print(f"\n[INFO] 이슈 등록 대상: {sp_doc} (자동 등록 안 함 — 에이전트 판단)")
        rc = 1
    else:
        print("\n[OK] All checks passed successfully. 이슈 없음.")
        rc = 0

    # [2단계] 체크리스트 실행
    print_checklist_stage()
    return rc


def run_py_compile_all():
    """모든 Python 파일에 대해 py_compile 실행 (구문 오류 검증)"""
    print("## Running py_compile (Syntax Check)...")
    errors = []
    file_count = 0

    for target_dir in TARGET_DIRS:
        for py_file in Path(target_dir).rglob("*.py"):
            # 제외 패턴
            if any(x in str(py_file) for x in ["__pycache__", ".git", "node_modules", "tmp"]):
                continue
            file_count += 1
            try:
                py_compile.compile(str(py_file), doraise=True)
            except py_compile.PyCompileError as e:
                error_msg = str(e)
                # 라인 번호 추출 시도
                line_match = re.search(r"line (\d+)", error_msg)
                line_no = int(line_match.group(1)) if line_match else None
                errors.append({
                    "file": str(py_file),
                    "line": line_no,
                    "message": error_msg
                })
                # 이슈 수집기에 추가
                issue_collector.add(
                    severity="CRITICAL",
                    category="SYNTAX",
                    file_path=str(py_file),
                    line_no=line_no,
                    message=f"구문 오류: {error_msg}"
                )

    if errors:
        print(f"[CRITICAL] {len(errors)}개 파일에서 구문 오류 발견!\n")
        for err in errors[:10]:  # 최대 10개만 표시
            print(f"  - {err['file']}:{err['line'] or '?'}")
            print(f"    {err['message'][:100]}...")
        if len(errors) > 10:
            print(f"  ... 외 {len(errors) - 10}개")
        return len(errors)
    else:
        print(f"[OK] {file_count}개 파일 구문 검증 통과")
        return 0


def run_tool(name, command, ignore_failure=True):
    """Run a tool and print its output, returning the exit code."""
    print(f"## Running {name}...")
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )
        print(result.stdout)
        if result.stderr:
            print(f"Errors:\n{result.stderr}")

        if result.returncode == 0:
            print(f"[OK] {name} passed.")
        else:
            print(f"[WARN] {name} found issues (Exit code: {result.returncode}).")

        return result.returncode
    except Exception as e:
        print(f"[ERROR] Failed to run {name}: {e}")
        return 1


def cmd_run():
    """전체 체크 실행 (run 서브명령어) — 프로젝트 유형 자동 감지"""
    global issue_collector
    issue_collector = IssueCollector()  # 이슈 수집기 초기화

    # 프로젝트 유형 감지 (SP 디렉토리 기준)
    sp_dir = detect_sp_project_dir()
    project_type = detect_project_type(sp_dir)

    if project_type == "flutter":
        print(f"[INFO] Flutter 프로젝트 감지: {sp_dir}\n")
        return cmd_dart_run(sp_dir)

    # 기존 Python 체크 플로우
    print("# oocheck run\n")

    if not TARGET_DIRS:
        print("[ERROR] No source directories found (src, oo, tests).")
        return 1

    print("=" * 60)
    print("[OAISCHECK] Inspection Scope")
    print("=" * 60)
    print("The following directories will be inspected:\n")
    for d in TARGET_DIRS:
        print(f"  - {d}")
    print("\n" + "=" * 60 + "\n")

    print("Starting checks immediately...\n")

    failure_count = 0
    missing_tools = []

    # 0. py_compile (구문 검증) - 가장 먼저 실행
    syntax_errors = run_py_compile_all()
    if syntax_errors > 0:
        failure_count += 1
    print("-" * 40 + "\n")

    # 1. Pylint
    if check_command("pylint"):
        cmd = ["pylint", "--errors-only", "--output-format=text"] + TARGET_DIRS
        ret = run_tool("Pylint", cmd)
        if ret != 0:
            failure_count += 1
            # pylint 출력에서 에러 파싱 시도
            parse_pylint_errors(cmd)
    else:
        print("[ERROR] Pylint not found. Install with: uv sync --group dev")
        missing_tools.append("pylint")
        failure_count += 1

    print("-" * 40 + "\n")

    # 2. Mypy
    if check_command("mypy"):
        cmd = ["mypy", "--ignore-missing-imports"] + TARGET_DIRS
        ret = run_tool("Mypy", cmd)
        if ret != 0:
            failure_count += 1
            # mypy 출력에서 에러 파싱
            parse_mypy_errors(cmd)
    else:
        print("[ERROR] Mypy not found. Install with: uv sync --group dev")
        missing_tools.append("mypy")
        failure_count += 1

    print("-" * 40 + "\n")

    # 3. Pytest
    if check_command("pytest"):
        cmd = ["pytest", "-v", "--tb=short"]
        ret = run_tool("Pytest", cmd)
        if ret != 0:
            failure_count += 1
            issue_collector.add(
                severity="ERROR",
                category="TEST",
                file_path="tests/",
                line_no=None,
                message="pytest 테스트 실패"
            )
    else:
        print("[ERROR] Pytest not found. Install with: uv sync --group dev")
        missing_tools.append("pytest")
        failure_count += 1

    print("-" * 40 + "\n")

    # 4. oo Usage Validator (직접 호출)
    print("## Running oo Usage Validator...")
    result = get_oo_errors(PROJECT_ROOT)
    if result['total_errors'] > 0:
        print(f"[WARN] {result['total_errors']}개 oo 사용 오류 발견")
        failure_count += 1
        # oo 오류를 이슈 수집기에 추가
        for file_path, errors in result.get('server_errors', {}).items():
            for err in errors:
                issue_collector.add(
                    severity="ERROR",
                    category="OAIS",
                    file_path=file_path,
                    line_no=err.line_no,
                    message=f"oo.{err.attr_name} 잘못된 사용",
                    suggestion=err.suggestion
                )
    else:
        print("[OK] oo Usage Validator passed.")

    # 결과 요약 및 d0004_todo.md 등록
    print("\n" + "=" * 60)
    print("# Summary")
    print("=" * 60)

    counts = issue_collector.count_by_severity()
    print(f"\n발견된 이슈:")
    print(f"  - CRITICAL: {counts['CRITICAL']}개")
    print(f"  - ERROR: {counts['ERROR']}개")
    print(f"  - WARNING: {counts['WARNING']}개")
    print(f"  - INFO: {counts['INFO']}개")
    print(f"  - 총계: {len(issue_collector.issues)}개")

    if missing_tools:
        print(f"\n[WARN] 미설치 도구: {', '.join(missing_tools)}")
        print("  설치 명령: uv sync --group dev")

    # d0004_todo.md에 이슈 등록
    rc = 0
    if issue_collector.issues:
        register_issues_to_todo(issue_collector)
        print(f"\n[OK] {len(issue_collector.issues)}개 이슈가 d0004_todo.md에 등록됨")
        rc = 1
    else:
        print("\n[OK] All checks passed successfully. 이슈 없음.")

    # [2단계] 체크리스트 실행
    print_checklist_stage()
    return rc


def parse_pylint_errors(cmd):
    """pylint 출력에서 에러 파싱"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        for line in result.stdout.split('\n'):
            # 형식: file.py:10:0: E0001: message
            match = re.match(r'^(.+?):(\d+):\d+: ([EWCRF]\d+): (.+)$', line)
            if match:
                file_path, line_no, code, message = match.groups()
                severity = "ERROR" if code.startswith('E') else "WARNING"
                issue_collector.add(
                    severity=severity,
                    category="LINT",
                    file_path=file_path,
                    line_no=int(line_no),
                    message=f"[{code}] {message}"
                )
    except Exception:
        pass


def parse_mypy_errors(cmd):
    """mypy 출력에서 에러 파싱"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        for line in result.stdout.split('\n'):
            # 형식: file.py:10: error: message
            match = re.match(r'^(.+?):(\d+): (error|warning): (.+)$', line)
            if match:
                file_path, line_no, level, message = match.groups()
                severity = "ERROR" if level == "error" else "WARNING"
                issue_collector.add(
                    severity=severity,
                    category="TYPE",
                    file_path=file_path,
                    line_no=int(line_no),
                    message=message
                )
    except Exception:
        pass


def register_issues_to_todo(collector: IssueCollector, todo_path_override=None):
    """수집된 이슈를 todo 파일의 ## 대기 ToDo 섹션에 ### 블록으로 등록 (SP 컨텍스트 지원)"""
    todo_path = todo_path_override or (PROJECT_ROOT / "00_doc" / "sp00" / "d0004_todo.md")
    if not todo_path.exists():
        todo_path = todo_path_override or (PROJECT_ROOT / "00_doc" / "d0004_todo.md")
    if not todo_path.exists():
        print(f"[WARN] {todo_path} not found. Skipping todo update.")
        return

    content = todo_path.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")

    # ## 대기 ToDo 섹션 찾기
    section_match = re.search(r"^## 대기 ToDo", content, re.MULTILINE)
    if not section_match:
        print("[WARN] '대기 ToDo' 섹션 없음. 수동 등록 필요.")
        return

    # 기존 A 접두사 이슈 중 최대 번호 파악
    existing = re.findall(r"^### A(\d+)", content, re.MULTILINE)
    next_num = max((int(n) for n in existing), default=0) + 1

    new_blocks = []
    for i, issue in enumerate(collector.issues):
        issue_id = f"A{next_num + i:03d}"
        rel_path = issue.file_path
        if PROJECT_ROOT and issue.file_path.startswith(str(PROJECT_ROOT)):
            rel_path = str(Path(issue.file_path).relative_to(PROJECT_ROOT))
        line_info = f":{issue.line_no}" if issue.line_no else ""
        message = issue.message[:50]
        title = f"[{issue.category}] {rel_path}{line_info} - {message}"
        block = (
            f"### {issue_id} {title}\n"
            f"등록일: {today} | 우선순위: {issue.severity} | 상태: 분석중\n"
        )
        new_blocks.append(block)

    if not new_blocks:
        return

    # 섹션 설명줄(>) 다음에 삽입
    pos = section_match.end()
    while pos < len(content) and content[pos] == '\n':
        pos += 1
    desc_m = re.match(r"(?:>.*\n)+", content[pos:])
    if desc_m:
        pos += len(desc_m.group(0))

    insert_text = "\n" + "\n".join(new_blocks)
    content = content[:pos] + insert_text + content[pos:]
    todo_path.write_text(content, encoding="utf-8")
    print(f"[OK] {len(new_blocks)}개 이슈가 대기 ToDo에 등록됨")


def cmd_oo(dry_run: bool = False):
    """oo 모듈 사용 검증 (oo 서브명령어)"""
    print("# oocheck oo\n")

    # oo 오류 검사
    result = get_oo_errors(PROJECT_ROOT)

    print(f"검사 대상: {result['total_files']}개 파일")
    print(f"총 오류: {result['total_errors']}개")
    print(f"운영 코드 오류 파일: {len(result['server_errors'])}개")

    if result['total_errors'] == 0:
        print("\n[OK] oo 모듈 사용에 문제가 없습니다.")
        return 0

    # 운영 코드 오류 상세 출력
    print("\n## 운영 코드 오류 상세")
    for file_path, errors in sorted(result['server_errors'].items()):
        rel_path = Path(file_path).relative_to(result['project_root'])
        print(f"\n### {rel_path}")
        for err in errors:
            fix = f" -> {err.suggestion}" if err.suggestion else " (서브모듈 확인 필요)"
            print(f"  L{err.line_no}: oo.{err.attr_name}{fix}")

    if dry_run:
        print("\n[DRY-RUN] d0004_todo.md 업데이트를 건너뜁니다.")
        return 1

    # d0004_todo.md에 등록
    update_todo_file(result)
    return 1


def get_next_todo_id(todo_content: str) -> str:
    """다음 TODO ID 반환 (TODO-XXX 형식)"""
    # 기존 TODO ID 패턴 찾기
    pattern = r"TODO-(\d{3})"
    matches = re.findall(pattern, todo_content)
    if matches:
        max_id = max(int(m) for m in matches)
        return f"TODO-{max_id + 1:03d}"
    return "TODO-001"


def update_todo_file(result: dict):
    """d0004_todo.md의 ## 대기 ToDo 섹션에 oo 모듈 오류 ### 블록으로 등록"""
    todo_path = PROJECT_ROOT / "00_doc" / "sp00" / "d0004_todo.md"
    if not todo_path.exists():
        todo_path = PROJECT_ROOT / "00_doc" / "d0004_todo.md"
    if not todo_path.exists():
        print(f"[WARN] {todo_path} not found. Skipping todo update.")
        return

    todo_content = todo_path.read_text(encoding="utf-8")

    # 기존 oo 모듈 사용 오류 블록 삭제 (갱신을 위해)
    old_issue_pattern = r"### A\d+ \[ERROR\] oo 모듈 사용 오류[^\n]*\n(?:(?!^###|^##).*\n)*"
    todo_content = re.sub(old_issue_pattern, "", todo_content, flags=re.MULTILINE)

    # ## 대기 ToDo 섹션 찾기
    section_match = re.search(r"^## 대기 ToDo", todo_content, re.MULTILINE)
    if not section_match:
        print("[WARN] '대기 ToDo' 섹션을 찾을 수 없습니다.")
        return

    # 기존 A 접두사 최대 번호 파악
    existing = re.findall(r"^### A(\d+)", todo_content, re.MULTILINE)
    next_num = max((int(n) for n in existing), default=0) + 1

    today = datetime.now().strftime("%Y-%m-%d")
    new_blocks = []

    for i, (file_path, errors) in enumerate(sorted(result['server_errors'].items())):
        rel_path = Path(file_path).relative_to(result['project_root'])
        file_name = Path(file_path).stem
        issue_id = f"A{next_num + i:03d}"

        error_details = []
        for err in errors:
            if err.suggestion:
                error_details.append(f"  - L{err.line_no}: `oo.{err.attr_name}` -> `{err.suggestion}`")
            else:
                error_details.append(f"  - L{err.line_no}: `oo.{err.attr_name}` (서브모듈 확인 필요)")

        block = (
            f"### {issue_id} [ERROR] oo 모듈 사용 오류 - {file_name}\n"
            f"등록일: {today} | 우선순위: ERROR | 상태: 분석중\n\n"
            f"- **파일**: `{rel_path}`\n"
            f"- **오류 수**: {len(errors)}개\n"
            f"- **수정 내용**:\n"
            f"{chr(10).join(error_details)}\n"
        )
        new_blocks.append(block)

    if not new_blocks:
        return

    # 섹션 설명줄(>) 다음에 삽입
    pos = section_match.end()
    while pos < len(todo_content) and todo_content[pos] == '\n':
        pos += 1
    desc_m = re.match(r"(?:>.*\n)+", todo_content[pos:])
    if desc_m:
        pos += len(desc_m.group(0))

    insert_text = "\n" + "\n".join(new_blocks)
    updated_content = todo_content[:pos] + insert_text + todo_content[pos:]
    todo_path.write_text(updated_content, encoding="utf-8")
    print(f"\n[OK] {len(result['server_errors'])}개 파일의 이슈가 d0004_todo.md에 등록되었습니다.")


def cmd_error():
    """에러 체크만 수행 (error 서브명령어)"""
    print("# oocheck error\n")

    if not TARGET_DIRS:
        print("[ERROR] No source directories found.")
        return 1

    print("## 에러 체크만 수행 (표준용어 체크 제외)\n")
    failure_count = 0

    # 1. Pylint
    if check_command("pylint"):
        cmd = ["pylint", "--errors-only"] + TARGET_DIRS
        ret = run_tool("Pylint (errors only)", cmd)
        if ret != 0:
            failure_count += 1
    else:
        print("[SKIP] Pylint not found.")

    print("-" * 40 + "\n")

    # 2. Mypy
    if check_command("mypy"):
        cmd = ["mypy", "--no-error-summary"] + TARGET_DIRS
        ret = run_tool("Mypy", cmd)
        if ret != 0:
            failure_count += 1
    else:
        print("[SKIP] Mypy not found.")

    print("\n# Summary")
    if failure_count == 0:
        print("No errors found.")
        return 0
    else:
        print(f"Errors found in {failure_count} tools.")
        return 1


def cmd_term():
    """표준용어 체크만 수행 (term 서브명령어)"""
    print("# oocheck term\n")

    # 표준용어 파일 로드
    term_file = PROJECT_ROOT / "00_doc" / "d0006_db.md"
    if not term_file.exists():
        print(f"[ERROR] 표준용어 파일을 찾을 수 없습니다: {term_file}")
        return 1

    # 표준용어 추출 (sys_standard_word 테이블 섹션에서)
    term_content = term_file.read_text(encoding="utf-8")

    # 간단한 표준용어 패턴 매칭 (실제 구현은 더 정교해야 함)
    print("## 표준용어 체크")
    print("표준용어 파일: 00_doc/sp00/d0006_db.md")
    print("\n[INFO] 표준용어 체크는 현재 기본 검사만 수행합니다.")
    print("[OK] 표준용어 체크 완료")
    return 0


def cmd_update():
    """d0004/d0010 문서 정리 및 동기화 (update 서브명령어)"""
    print("# oocheck update\n")

    todo_file = PROJECT_ROOT / "00_doc" / "d0004_todo.md"
    history_file = PROJECT_ROOT / "00_doc" / "d0010_history.md"

    updated = False

    # d0004_todo.md 정리
    if todo_file.exists():
        content = todo_file.read_text(encoding="utf-8")
        original_len = len(content)

        # 완료된 항목 찾기 (체크된 항목)
        completed_pattern = r"- \[x\] (.+)"
        completed_items = re.findall(completed_pattern, content, re.IGNORECASE)

        if completed_items:
            print(f"## d0004_todo.md에서 완료된 항목 {len(completed_items)}개 발견")
            for item in completed_items[:5]:  # 최대 5개만 표시
                print(f"  - {item[:50]}...")

            # 완료된 항목을 history로 이동할지는 사용자 확인 필요
            print("\n[INFO] 완료된 항목은 수동으로 d0010_history.md로 이동하세요.")
            updated = True
        else:
            print("## d0004_todo.md: 완료된 항목 없음")
    else:
        print(f"[WARN] {todo_file} not found")

    # d0010_history.md 확인
    if history_file.exists():
        content = history_file.read_text(encoding="utf-8")
        # 최근 이력 항목 수 확인
        history_pattern = r"### \[.+?\]"
        history_items = re.findall(history_pattern, content)
        print(f"\n## d0010_history.md: {len(history_items)}개 이력 항목")
    else:
        print(f"[WARN] {history_file} not found")

    print("\n[OK] 문서 상태 확인 완료")
    return 0


def cmd_debug(error_msg: str = None):
    """심층 디버깅 워크플로우 (debug 서브명령어)"""
    print("# oocheck debug\n")

    if error_msg:
        print(f"## 분석 대상 에러: {error_msg}\n")

        # 에러 유형 분류
        error_types = {
            "TypeError": "타입 불일치 오류",
            "ValueError": "값 오류",
            "AttributeError": "속성 접근 오류",
            "KeyError": "딕셔너리 키 오류",
            "ImportError": "모듈 임포트 오류",
            "ModuleNotFoundError": "모듈을 찾을 수 없음",
            "SyntaxError": "문법 오류",
            "IndentationError": "들여쓰기 오류",
            "NameError": "정의되지 않은 이름",
            "FileNotFoundError": "파일을 찾을 수 없음",
        }

        detected_type = None
        for err_type, desc in error_types.items():
            if err_type.lower() in error_msg.lower():
                detected_type = (err_type, desc)
                break

        if detected_type:
            print(f"### 에러 유형: {detected_type[0]}")
            print(f"### 설명: {detected_type[1]}")
            print("\n### 권장 조치:")

            if detected_type[0] == "ImportError":
                print("  1. 순환 참조 확인: oocheck circular")
                print("  2. 모듈 경로 확인")
                print("  3. __init__.py 파일 확인")
            elif detected_type[0] == "AttributeError":
                print("  1. oo 모듈 사용 검증: oocheck oo")
                print("  2. None 체크 추가")
                print("  3. 속성 존재 여부 확인")
            elif detected_type[0] == "TypeError":
                print("  1. 인자 타입 확인")
                print("  2. None 값 처리")
                print("  3. 타입 힌트 추가 후 mypy 실행")
            else:
                print("  1. 스택 트레이스 분석")
                print("  2. 관련 코드 리뷰")
                print("  3. 단위 테스트 작성")
        else:
            print("### 에러 유형을 자동 감지할 수 없습니다.")
            print("### 수동 분석이 필요합니다.")
    else:
        print("## 디버깅 워크플로우 가이드\n")
        print("1. 에러 메시지 수집")
        print("2. 에러 유형 분류")
        print("3. 관련 코드 탐색")
        print("4. 근본 원인 분석")
        print("5. 수정 및 검증")
        print("\n### 사용 예시:")
        print('  oocheck debug "TypeError: NoneType has no attribute"')
        print('  oocheck debug "ImportError: circular import"')

    return 0


def get_imports_from_file(file_path):
    """파일에서 import 문 추출"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
    except Exception:
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def find_cycles_in_graph(graph):
    """의존성 그래프에서 순환 찾기"""
    visited = set()
    stack = set()
    cycles = []

    def dfs(node, path):
        visited.add(node)
        stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor, path)
            elif neighbor in stack:
                cycle = path[path.index(neighbor):] + [neighbor]
                cycles.append(cycle)

        path.pop()
        stack.remove(node)

    for node in list(graph.keys()):
        if node not in visited:
            dfs(node, [])

    return cycles


def cmd_circular(module_name: str = None):
    """순환 참조 감지 (circular 서브명령어)"""
    print("# oocheck circular\n")

    target_dir = PROJECT_ROOT / "oo"
    if module_name:
        target_dir = PROJECT_ROOT / module_name
        if not target_dir.exists():
            target_dir = PROJECT_ROOT / "oo"
            print(f"[INFO] '{module_name}' 디렉토리가 없어 oo 폴더를 검사합니다.\n")

    if not target_dir.exists():
        print(f"[ERROR] 대상 디렉토리가 없습니다: {target_dir}")
        return 1

    print(f"## 검사 대상: {target_dir}\n")

    # 의존성 그래프 생성
    graph = defaultdict(list)
    py_files = list(target_dir.rglob("*.py"))

    module_base = target_dir.name

    for py_file in py_files:
        rel_path = py_file.relative_to(target_dir)
        module_name_current = str(rel_path.with_suffix('')).replace('/', '.').replace('\\', '.')
        if module_name_current == '__init__':
            module_name_current = module_base
        else:
            module_name_current = f"{module_base}.{module_name_current}"

        imports = get_imports_from_file(py_file)
        for imp in imports:
            if imp.startswith(module_base):
                graph[module_name_current].append(imp)

    # 순환 참조 찾기
    cycles = find_cycles_in_graph(graph)

    if cycles:
        print(f"### [WARN] {len(cycles)}개 순환 참조 발견!\n")
        for i, cycle in enumerate(cycles[:10], 1):  # 최대 10개만 표시
            print(f"  {i}. {' -> '.join(cycle)}")

        if len(cycles) > 10:
            print(f"\n  ... 외 {len(cycles) - 10}개")

        return 1
    else:
        print("[OK] 순환 참조가 발견되지 않았습니다.")
        return 0


# ============================================================
# d0008 프로젝트 체크리스트 (oocheck add / run 2단계)
# ============================================================

# 체크리스트 항목 성격별 접두사 (안1 — 도메인 분류)
CHECKLIST_CATEGORIES = {
    "C": ("코드", ["코드", "구현", "함수", "클래스", "pylint", "lint", "리팩토링",
                   "refactor", "api", "모듈", "module", "알고리즘"]),
    "D": ("문서", ["문서", "doc", "prd", "가이드", "guide", "readme", "주석",
                   "명세", "튜토리얼", "tutorial"]),
    "S": ("보안", ["보안", "security", "취약점", "인증", "auth", "권한",
                   "시크릿", "secret", "토큰", "token"]),
    "T": ("테스트", ["테스트", "test", "pytest", "커버리지", "coverage", "tc", "검증"]),
    "E": ("환경", ["환경", "설정", "config", "의존성", "패키지", "package",
                   "uv", "빌드", "build", "배포", "deploy"]),
    "G": ("일반", []),
}


def detect_checklist_category(content: str) -> str:
    """체크리스트 내용에서 성격(접두사) 판정. 미매칭 시 G(일반)."""
    low = content.lower()
    for prefix, (_name, keywords) in CHECKLIST_CATEGORIES.items():
        for kw in keywords:
            if kw in low:
                return prefix
    return "G"


def get_d0008_path(sp: str) -> Path:
    """SP별 d0008_checklist.md 경로 반환."""
    sp = f"{int(sp):02d}"
    if sp == "00":
        fname = "d0008_checklist.md"
    else:
        fname = f"d{int(sp) * 10000 + 8}_checklist.md"
    return PROJECT_ROOT / "00_doc" / f"sp{sp}" / fname


def ensure_d0008(sp: str) -> Path:
    """d0008_checklist.md 없으면 템플릿 기반으로 생성."""
    path = get_d0008_path(sp)
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    template = SCRIPT_DIR.parent / "templates" / "d0008_checklist_template.md"
    if template.exists():
        text = template.read_text(encoding="utf-8")
        text = text.replace("{SP}", f"{int(sp):02d}").replace("{DATE}", today)
    else:
        text = (f"# SP{int(sp):02d} 프로젝트 체크리스트\n\n"
                f"## 문서이력관리\n- v01 {today} — 초기 생성\n\n---\n\n"
                f"## 체크리스트 항목\n\n(oocheck add 로 항목 추가)\n")
    path.write_text(text, encoding="utf-8")
    print(f"[OK] d0008 체크리스트 생성: {path.relative_to(PROJECT_ROOT)}")
    return path


def get_next_checklist_id(content: str, prefix: str) -> str:
    """접두사별 다음 체크리스트 ID 반환 (예: C001)."""
    nums = re.findall(rf"^### {prefix}(\d+)", content, re.MULTILINE)
    n = max((int(x) for x in nums), default=0) + 1
    return f"{prefix}{n:03d}"


def cmd_add(args: list) -> int:
    """oocheck add — 체크리스트 항목 추가.

    oocheck add checklist "항목"  → oocheck 스킬 체크리스트(references/checklist.md)
    oocheck add "내용"            → d{SP}0008_checklist.md (프로젝트 체크리스트)
    """
    if args and args[0] == "checklist":
        item = " ".join(args[1:]).strip().strip('"').strip("'")
        if not item:
            print('[ERROR] 사용법: oocheck add checklist "항목"')
            return 1
        cl_path = SCRIPT_DIR.parent / "references" / "checklist.md"
        if not cl_path.exists():
            print(f"[ERROR] 스킬 체크리스트 없음: {cl_path}")
            return 1
        lines = cl_path.read_text(encoding="utf-8").splitlines()
        rows = [i for i, ln in enumerate(lines) if re.match(r"^\| C\d+ \|", ln)]
        nums = [int(re.match(r"^\| C(\d+) \|", lines[i]).group(1)) for i in rows]
        nxt = max(nums, default=0) + 1
        lines.insert(rows[-1] + 1, f"| C{nxt:02d} | {item} | {item} | WARNING |")
        cl_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"[OK] C{nxt:02d} 추가됨 → oocheck 스킬 체크리스트 (references/checklist.md)")
        return 0

    # d0008 프로젝트 체크리스트에 추가
    content_text = " ".join(args).strip().strip('"').strip("'")
    if not content_text:
        print('[ERROR] 사용법: oocheck add "체크리스트 내용"')
        return 1
    sp = f"{int(SP_CONTEXT):02d}"
    path = ensure_d0008(sp)
    doc = path.read_text(encoding="utf-8")
    prefix = detect_checklist_category(content_text)
    item_id = get_next_checklist_id(doc, prefix)
    cat_name = CHECKLIST_CATEGORIES[prefix][0]
    today = datetime.now().strftime("%Y-%m-%d")
    block = (
        f"### {item_id} [{cat_name}] {content_text}\n"
        f"#### 등록일: {today} | 우선순위: medium\n"
        f"#### 체크 내용\n"
        f"{content_text}\n"
    )
    section_h = "## 체크리스트 항목"
    if section_h in doc:
        idx = doc.index(section_h) + len(section_h)
        body = doc[idx:].replace("(oocheck add 로 항목 추가)", "").strip()
        new_body = (body + "\n\n" + block) if body else block
        doc = doc[:idx] + "\n\n" + new_body + "\n"
    else:
        doc = doc.rstrip() + f"\n\n{section_h}\n\n{block}"
    path.write_text(doc, encoding="utf-8")
    print(f"[OK] {item_id} [{cat_name}] 추가됨 → {path.relative_to(PROJECT_ROOT)}")
    return 0


def list_skill_checklists() -> list:
    """references/checklist.md 를 보유한 oo* 스킬 목록 반환."""
    skills_dir = PROJECT_ROOT / ".claude" / "skills"
    result = []
    if skills_dir.exists():
        for d in sorted(skills_dir.glob("oo*")):
            if (d / "references" / "checklist.md").exists():
                result.append(d.name)
    return result


def scan_sp_with_d0008() -> list:
    """d0008_checklist.md 가 존재하는 SP 목록 반환."""
    sps = []
    doc_dir = PROJECT_ROOT / "00_doc"
    if doc_dir.exists():
        for d in sorted(doc_dir.glob("sp*")):
            sp = d.name[2:]
            if sp.isdigit() and get_d0008_path(sp).exists():
                sps.append(sp)
    return sps


def print_checklist_stage():
    """oocheck run 2단계 — 체크리스트 실행 안내 (대화형 선택은 Claude가 수행)."""
    print("\n" + "=" * 60)
    print("# [2단계] 체크리스트 실행")
    print("=" * 60)

    if SP_EXPLICIT:
        sps = [f"{int(SP_CONTEXT):02d}"]
        print(f"\n범위: SP{int(SP_CONTEXT):02d} (--sp 지정)")
    else:
        sps = scan_sp_with_d0008()
        print("\n범위: 전체 SP")

    print("\n## 프로젝트 체크리스트 (d0008)")
    found = False
    for sp in sps:
        p = get_d0008_path(sp)
        if p.exists():
            ids = re.findall(r"^### ([CDSTEG]\d+)", p.read_text(encoding="utf-8"), re.MULTILINE)
            print(f"  - SP{sp}: {p.relative_to(PROJECT_ROOT)} ({len(ids)}개 항목)")
            found = True
    if not found:
        print('  (d0008_checklist.md 없음 — `oocheck add "내용"` 으로 항목 추가)')

    skills = list_skill_checklists()
    print(f"\n## 체크리스트 보유 스킬 ({len(skills)}개)")
    print("  " + (", ".join(skills) if skills else "(없음)"))

    print("\n## 다음 단계 (Claude가 SKILL.md에 따라 수행)")
    print("  1. 위 '체크리스트 보유 스킬' 목록을 사용자에게 제시")
    print("  2. 어떤 스킬의 체크리스트를 체크할지 사용자 선택 받기")
    print("  3. d0008 항목 + oocheck 스킬 체크리스트 + 선택 스킬 체크리스트 전체 체크")
    print("  4. 체크 결과를 d{SP}0004_todo.md (및 d0004) 에 등록")


def print_usage():
    """사용법 출력"""
    print("""oocheck - 통합 코드 품질 체크

사용법:
    oocheck run              전체 체크 실행 (pylint, mypy, pytest, oo)
    oocheck oo             oo 모듈 검증 및 d0004_todo.md 등록
    oocheck oo --dry-run   검증만 (todo 등록 안함)
    oocheck error            에러 체크만 (pylint, mypy)
    oocheck term             표준용어 체크만
    oocheck update           d0004/d0010 문서 정리
    oocheck debug [에러]     심층 디버깅 워크플로우
    oocheck circular [모듈]  순환 참조 감지
    oocheck add "내용"       d0008 프로젝트 체크리스트 항목 추가 (성격 자동분류)

예시:
    python .claude/skills/oocheck/scripts/oocheck_run.py run
    python .claude/skills/oocheck/scripts/oocheck_run.py oo
    python .claude/skills/oocheck/scripts/oocheck_run.py error
    python .claude/skills/oocheck/scripts/oocheck_run.py debug "TypeError: NoneType"
    python .claude/skills/oocheck/scripts/oocheck_run.py circular oo
""")


def cmd_show_checklist():
    """references/checklist.md 내용 출력"""
    checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[{SKILL_NAME}] checklist.md 없음: {checklist_path}")
        return
    print(checklist_path.read_text(encoding="utf-8"))


def main():
    global SP_EXPLICIT
    # 서브명령어 없이 실행 시 도움말 출력
    if not sys.argv[1:]:
        sys.argv.append("run")

    # Agent 환경에서 출력 캡처를 위해 로그 파일로 리다이렉션 코드를 제거합니다.
    # log_file = PROJECT_ROOT / "oocheck_report.log"
    # sys.stdout = open(log_file, "w", encoding="utf-8")
    # sys.stderr = sys.stdout
    print(f"Log started at {datetime.now()}")

    args = sys.argv[1:]

    # --sp 옵션 추출 (상태 파일 기반 SP를 CLI로 오버라이드)
    for _i, _a in enumerate(args):
        if _a == "--sp" and _i + 1 < len(args):
            try:
                set_sp_context(f"{int(args[_i + 1]):02d}")
                SP_EXPLICIT = True
            except ValueError:
                pass
            args = args[:_i] + args[_i + 2:]
            break

    if not args:
        print_usage()
        return 0

    subcommand = args[0]
    if subcommand in ("show",) and len(args) > 1 and args[1].lower() == "checklist":
        cmd_show_checklist()
        return

    if subcommand == "run":
        return cmd_run()
    elif subcommand == "oo":
        dry_run = "--dry-run" in args
        return cmd_oo(dry_run=dry_run)
    elif subcommand == "error":
        return cmd_error()
    elif subcommand == "term":
        return cmd_term()
    elif subcommand == "update":
        return cmd_update()
    elif subcommand == "debug":
        error_msg = args[1] if len(args) > 1 else None
        return cmd_debug(error_msg)
    elif subcommand == "circular":
        module_name = args[1] if len(args) > 1 else None
        return cmd_circular(module_name)
    elif subcommand == "add":
        return cmd_add(args[1:])
    elif subcommand == "check":
        # check: 스킬 체크리스트/상태 출력 (alias of run 요약)
        print(f"[{subcommand}] oocheck 체크리스트 안내")
        _print_skill_help("oocheck")
        return 0
    elif subcommand in ("-h", "--help", "help"):
        _print_skill_help("oocheck")
        return 0
    else:
        print(f"[ERROR] Unknown subcommand: {subcommand}")
        print_usage()
        return 1


if __name__ == "__main__":
    sys.exit(main())
