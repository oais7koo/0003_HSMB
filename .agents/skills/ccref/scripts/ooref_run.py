#!/usr/bin/env python3
"""
ooref_run.py

프레임워크 레퍼런스 관리 스킬 스크립트
- ccref list: 사용 가능한 프레임워크 레퍼런스 목록
- ccref run: 현재 프로젝트 기술스펙 감지 + 레퍼런스 기준 체크
- ccref run [path]: 특정 프로젝트 경로 체크
- ccref run [framework]: 특정 프레임워크 강제 지정

Usage:
    uv run python .agents/skills/ccref/scripts/ooref_run.py list
    uv run python .agents/skills/ccref/scripts/ooref_run.py run
    uv run python .agents/skills/ccref/scripts/ooref_run.py run D:/resilio/3_code/0002_CCone
    uv run python .agents/skills/ccref/scripts/ooref_run.py run fast-api
"""

import sys
import re
from pathlib import Path

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

# Windows 콘솔 UTF-8
if sys.stdout.encoding and sys.stdout.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    sys.stdout.reconfigure(encoding='utf-8')

# 레퍼런스 경로
REF_DIR = _SKILLS_DIR.parent / "reference" / "development"

# 알려진 프레임워크 이름 목록 (run [framework] 감지용)
KNOWN_FRAMEWORKS = ["fast-api", "fastapi", "django", "streamlit"]


# ─────────────────────────────────────────
# ccref list
# ─────────────────────────────────────────

def cmd_list():
    readme = REF_DIR / "README.md"
    print("# ccref list - 프레임워크 레퍼런스 목록\n")

    if not readme.exists():
        print(f"[ERROR] README.md 없음: {readme}")
        return

    content = readme.read_text(encoding="utf-8")

    # 프레임워크 목록 섹션 추출
    fw_match = re.search(r"(## 프레임워크 목록\n\n.+?)(?=\n##|\Z)", content, re.DOTALL)
    if fw_match:
        print(fw_match.group(1).strip())
    print()

    # 실제 폴더 목록
    print("## 실제 레퍼런스 폴더\n")
    folders = sorted(d for d in REF_DIR.iterdir() if d.is_dir())
    if folders:
        for folder in folders:
            doc_count = len(list(folder.glob("*.md")))
            print(f"- `{folder.name}/` — {doc_count}개 문서")
    else:
        print("- (없음)")
    print()

    # 감지 규칙 섹션 추출
    detect_match = re.search(r"(## 감지 규칙\n\n.+?)(?=\n##|\Z)", content, re.DOTALL)
    if detect_match:
        print(detect_match.group(1).strip())


# ─────────────────────────────────────────
# 프레임워크 자동 감지
# ─────────────────────────────────────────

def detect_framework(project_path: Path) -> str | None:
    # pyproject.toml
    pyproject = project_path / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text(encoding="utf-8", errors="ignore")
        if "fastapi" in content.lower():
            return "fast-api"
        if "django" in content.lower():
            return "django"

    # requirements.txt
    requirements = project_path / "requirements.txt"
    if requirements.exists():
        content = requirements.read_text(encoding="utf-8", errors="ignore")
        if "fastapi" in content.lower():
            return "fast-api"
        if "django" in content.lower():
            return "django"

    # main.py import 패턴
    main_py = project_path / "main.py"
    if main_py.exists():
        content = main_py.read_text(encoding="utf-8", errors="ignore")
        if "from fastapi" in content or "import fastapi" in content.lower():
            return "fast-api"

    # Django: manage.py + settings.py
    if (project_path / "manage.py").exists():
        return "django"

    # Streamlit: import streamlit 패턴 (*.py 파일 검색)
    for py_file in list(project_path.glob("*.py"))[:10]:
        try:
            if "import streamlit" in py_file.read_text(encoding="utf-8", errors="ignore"):
                return "streamlit"
        except Exception:
            pass

    return None


# ─────────────────────────────────────────
# FastAPI 체크 로직
# ─────────────────────────────────────────

def check_fastapi(project_path: Path) -> list[dict]:
    issues = []

    # 1. 필수 파일/폴더 체크 (01_directory_structure.md 기준)
    required = [
        ("main.py",  False, "CRITICAL", "01_directory_structure", "`main.py` 없음 — FastAPI 앱 진입점 필요"),
        ("routers",  True,  "ERROR",    "01_directory_structure", "`routers/` 폴더 없음 — API 엔드포인트 분리 필요"),
        ("models",   True,  "ERROR",    "01_directory_structure", "`models/` 폴더 없음 — DB/Pydantic 스키마 분리 필요"),
        ("tests",    True,  "ERROR",    "08_testing",             "`tests/` 폴더 없음 — pytest 테스트 필요"),
        ("batch",    True,  "WARNING",  "06_batch_engine",        "`batch/` 폴더 없음 — 배치 처리 엔진 미구현 (비동기 작업 필요 시 검토)"),
        ("admin",    True,  "WARNING",  "09_admin_dashboard",     "`admin/` 폴더 없음 — 관리자 대시보드 미구현 (필요 시 검토)"),
    ]
    for name, is_dir, level, ref, msg in required:
        target = project_path / name
        exists = target.is_dir() if is_dir else target.is_file()
        if not exists:
            issues.append({"level": level, "ref": ref, "msg": f"[{level}] {msg}"})

    # 2. 설정 파일 체크 (02_config_pattern.md 기준)
    config_files = list(project_path.glob("*_config.py"))
    if not config_files:
        issues.append({
            "level": "ERROR",
            "ref": "02_config_pattern",
            "msg": "[ERROR] `*_config.py` 없음 — 설정 파일 분리 필요 (네이밍: `{project}_config.py`)",
        })

    # 3. main.py 패턴 체크 (03_main_app.md 기준)
    main_py = project_path / "main.py"
    if main_py.exists():
        try:
            content = main_py.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()

            # 파일 크기
            if len(lines) > 150:
                issues.append({
                    "level": "WARNING",
                    "ref": "01_directory_structure",
                    "msg": f"[WARNING] `main.py` {len(lines)}줄 — 권장 150줄 초과 (미들웨어/핸들러 분리 검토)",
                })

            # lifespan 사용 여부
            if "lifespan" not in content:
                issues.append({
                    "level": "WARNING",
                    "ref": "03_main_app",
                    "msg": "[WARNING] `main.py`에 `lifespan` 없음 — 앱 시작/종료 이벤트 핸들러 필요",
                })

            # 전역 예외 핸들러
            if "exception_handler" not in content and "add_exception_handler" not in content:
                issues.append({
                    "level": "WARNING",
                    "ref": "07_error_handling",
                    "msg": "[WARNING] 전역 예외 핸들러 없음 — `add_exception_handler` 사용 검토",
                })

            # rate limiting
            if "slowapi" not in content and "rate_limit" not in content.lower() and "RateLimiter" not in content:
                issues.append({
                    "level": "INFO",
                    "ref": "03_main_app",
                    "msg": "[INFO] Rate Limiting 미적용 — slowapi 사용 검토",
                })
        except Exception:
            pass

    # 4. routers/ 파일 크기 체크
    routers_dir = project_path / "routers"
    if routers_dir.exists():
        for py_file in routers_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            try:
                lines = len(py_file.read_text(encoding="utf-8", errors="ignore").splitlines())
                if lines > 300:
                    issues.append({
                        "level": "WARNING",
                        "ref": "01_directory_structure",
                        "msg": f"[WARNING] `routers/{py_file.name}` {lines}줄 — 권장 300줄 초과 (업무별 라우터 분리 검토)",
                    })
            except Exception:
                pass

    # 5. 테스트 구조 체크 (08_testing.md 기준)
    tests_dir = project_path / "tests"
    if tests_dir.exists():
        if not (tests_dir / "conftest.py").exists():
            issues.append({
                "level": "WARNING",
                "ref": "08_testing",
                "msg": "[WARNING] `tests/conftest.py` 없음 — pytest fixture 파일 필요",
            })
        test_files = list(tests_dir.glob("test_*.py"))
        if not test_files:
            issues.append({
                "level": "ERROR",
                "ref": "08_testing",
                "msg": "[ERROR] `tests/test_*.py` 없음 — 테스트 파일 필요",
            })

    return issues


# 프레임워크 → 체크 함수 매핑
FRAMEWORK_CHECKERS = {
    "fast-api": check_fastapi,
    "fastapi": check_fastapi,
}


# ─────────────────────────────────────────
# ccref run
# ─────────────────────────────────────────

def cmd_run(args: list[str]):
    # 인자 파싱: 경로인지 프레임워크명인지 판별
    project_path = Path.cwd()
    framework_override = None

    for arg in args:
        p = Path(arg)
        if p.exists() and p.is_dir():
            project_path = p.resolve()
        elif arg.lower() in KNOWN_FRAMEWORKS:
            framework_override = arg.lower()

    print("# ccref run — 레퍼런스 적용 체크\n")
    print(f"**프로젝트**: `{project_path}`")

    # 프레임워크 감지
    framework = framework_override or detect_framework(project_path)

    if not framework:
        print("\n[INFO] 감지된 프레임워크 없음")
        print("- `pyproject.toml` 또는 `requirements.txt`에 프레임워크 의존성 추가 필요")
        print("- 또는 `ccref run [framework]` 으로 직접 지정")
        print("\n`ccref list` 로 지원 목록 확인")
        return

    # fast-api 정규화
    if framework == "fastapi":
        framework = "fast-api"

    print(f"**프레임워크**: `{framework}`")

    ref_path = REF_DIR / framework
    if not ref_path.exists():
        print(f"\n[ERROR] 레퍼런스 없음: `.codex/reference/development/{framework}/`")
        print("→ `ccsync` 로 레퍼런스 동기화 후 재시도")
        return

    doc_count = len(list(ref_path.glob("*.md")))
    print(f"**레퍼런스**: `.codex/reference/development/{framework}/` ({doc_count}개 문서)")
    print()
    print("---\n")

    # 체크 실행
    checker = FRAMEWORK_CHECKERS.get(framework)
    if not checker:
        print(f"[INFO] `{framework}` 체크 로직 미구현 — 레퍼런스 문서 수동 확인 필요")
        print(f"→ `.codex/reference/development/{framework}/` 참조")
        return

    issues = checker(project_path)

    if not issues:
        print("## 결과: 이상 없음 ✅\n")
        print("레퍼런스 기준 체크 통과 — 모든 패턴 적용됨")
        return

    # 레벨별 분류
    levels: dict[str, list] = {"CRITICAL": [], "ERROR": [], "WARNING": [], "INFO": []}
    for issue in issues:
        lvl = issue.get("level", "INFO")
        if lvl in levels:
            levels[lvl].append(issue)

    total = len(issues)
    print(f"## 결과: {total}개 문제 발견\n")

    # 요약 테이블
    print("| 수준 | 개수 |")
    print("|------|------|")
    for lvl in ["CRITICAL", "ERROR", "WARNING", "INFO"]:
        if levels[lvl]:
            print(f"| {lvl} | {len(levels[lvl])} |")
    print()

    # 상세 목록
    for lvl in ["CRITICAL", "ERROR", "WARNING", "INFO"]:
        if not levels[lvl]:
            continue
        print(f"### {lvl}\n")
        for issue in levels[lvl]:
            ref = issue.get("ref", "")
            ref_str = f" (ref: `{ref}.md`)" if ref else ""
            print(f"- {issue['msg']}{ref_str}")
        print()

    print("---")
    print(f"레퍼런스: `.codex/reference/development/{framework}/`")


# ─────────────────────────────────────────
# ccref add checklist
# ─────────────────────────────────────────

def cmd_add_checklist(args: list[str]):
    """checklist.md에 항목 추가"""
    if not args:
        print("[ERROR] 추가할 항목 내용을 입력하세요")
        print("사용법: ccref add checklist \"항목 내용\"")
        return

    text = " ".join(args).strip().strip('"').strip("'")
    checklist_path = _SKILLS_DIR / "ccref" / "references" / "checklist.md"

    if not checklist_path.exists():
        print(f"[ERROR] checklist.md 없음: {checklist_path}")
        return

    content = checklist_path.read_text(encoding="utf-8")

    # 마지막 체크리스트 섹션에 추가
    new_item = f"- [ ] {text}\n"
    if content.endswith("\n"):
        content += new_item
    else:
        content += "\n" + new_item

    checklist_path.write_text(content, encoding="utf-8")
    print(f"[ccref] 체크리스트 항목 추가: {text}")
    print(f"→ {checklist_path}")


# ─────────────────────────────────────────
# ccref check
# ─────────────────────────────────────────

def _capture(fn, *args, **kwargs) -> str:
    """함수 stdout 출력을 문자열로 캡처"""
    import io
    old = sys.stdout
    sys.stdout = buf = io.StringIO()
    try:
        fn(*args, **kwargs)
    finally:
        sys.stdout = old
    return buf.getvalue()


def cmd_check():
    """checklist.md 기반으로 ccref 스킬 자체 기능 검증"""
    checklist_path = _SKILLS_DIR / "ccref" / "references" / "checklist.md"
    print("# ccref check — 스킬 기능 검증\n")

    if not checklist_path.exists():
        print(f"[ERROR] checklist.md 없음: {checklist_path}")
        return

    # 체크리스트 항목 파싱
    content = checklist_path.read_text(encoding="utf-8")
    items = re.findall(r"- \[ \] (.+)", content)
    if not items:
        print("[WARN] 체크리스트 항목 없음")
        return

    passed, failed = [], []

    # ── list 기능 검증 ──────────────────────
    list_out = _capture(cmd_list)

    def check_item(label: str, condition: bool):
        if condition:
            passed.append(label)
        else:
            failed.append(label)

    check_item(
        "ccref list — README.md 파싱하여 프레임워크 목록 정확히 표시",
        "프레임워크 목록" in list_out and "FastAPI" in list_out,
    )
    check_item(
        "ccref list — 실제 폴더 목록 + 문서 수 표시",
        "실제 레퍼런스 폴더" in list_out and "fast-api/" in list_out,
    )
    check_item(
        "ccref list — 감지 규칙 표시",
        "감지 규칙" in list_out,
    )

    # ── run 기능 검증 (FastAPI 프로젝트 대상) ──
    # 실제 FastAPI 프로젝트 찾기 (3_code/ 하위)
    code_dir = _SKILLS_DIR.parent.parent.parent / "3_code"
    fastapi_project = None
    if code_dir.exists():
        for proj in code_dir.iterdir():
            if proj.is_dir() and (proj / "main.py").exists():
                content_check = (proj / "main.py").read_text(encoding="utf-8", errors="ignore")
                if "fastapi" in content_check.lower():
                    fastapi_project = proj
                    break

    # 프레임워크 자동 감지
    detected = detect_framework(fastapi_project) if fastapi_project else None
    check_item(
        "ccref run — 프레임워크 자동 감지",
        detected in ("fast-api", "fastapi") if fastapi_project else
        detect_framework(Path.cwd()) is None,  # FastAPI 없는 환경에서 None 반환이 정상
    )

    # run 출력 검증: 빈 프로젝트 (구조 체크용)
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        run_out = _capture(cmd_run, [str(tmp), "fast-api"])

    check_item(
        "ccref run — 프레임워크 강제 지정 동작",
        "fast-api" in run_out and "레퍼런스 적용 체크" in run_out,
    )
    check_item(
        "ccref run — 디렉토리 구조 체크",
        "main.py" in run_out or "routers" in run_out,
    )
    check_item(
        "ccref run — 설정 파일 분리 체크",
        "_config.py" in run_out,
    )
    check_item(
        "ccref run — 테스트 구조 체크",
        "tests" in run_out.lower(),
    )
    check_item(
        "ccref run — 문제점 레벨별 출력",
        any(lvl in run_out for lvl in ["CRITICAL", "ERROR", "WARNING", "INFO"]),
    )

    # 코드 패턴 체크: main.py 있지만 lifespan 없는 프로젝트로 검증
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        (tmp / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()\n", encoding="utf-8")
        pattern_out = _capture(cmd_run, [str(tmp), "fast-api"])

    check_item(
        "ccref run — 코드 패턴 체크 (lifespan, rate limiting, 예외 핸들러)",
        "lifespan" in pattern_out or "Rate Limiting" in pattern_out or "exception_handler" in pattern_out,
    )

    # 경로 지정 동작
    run_path_out = _capture(cmd_run, [str(Path.cwd())])
    check_item(
        "ccref run [path] — 특정 프로젝트 경로 지정 동작",
        "레퍼런스 적용 체크" in run_path_out,
    )

    # add checklist 기능 검증
    import tempfile as _tf
    with _tf.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("# 테스트 체크리스트\n\n")
        tmp_cl = Path(f.name)
    original_cl = checklist_path

    # 임시 checklist로 교체 후 테스트
    _orig_path = _SKILLS_DIR / "ccref" / "references" / "checklist.md"
    _backup = _orig_path.read_text(encoding="utf-8")
    try:
        _orig_path.write_text("# 테스트 체크리스트\n\n", encoding="utf-8")
        _capture(cmd_add_checklist, ["테스트 항목"])
        _added = _orig_path.read_text(encoding="utf-8")
        check_item(
            "ccref add checklist — 항목이 checklist.md에 정상 추가되는지 확인",
            "- [ ] 테스트 항목" in _added,
        )
    finally:
        _orig_path.write_text(_backup, encoding="utf-8")
        try:
            tmp_cl.unlink()
        except Exception:
            pass

    # ── 결과 출력 ──────────────────────────
    total = len(passed) + len(failed)
    print(f"## 결과: {len(passed)}/{total} 통과\n")

    if passed:
        print("### PASS ✅\n")
        for item in passed:
            print(f"- {item}")
        print()

    if failed:
        print("### FAIL ❌\n")
        for item in failed:
            print(f"- {item}")
        print()

    if not failed:
        print("모든 체크리스트 항목 통과 ✅")
    else:
        print(f"[ACTION] {len(failed)}개 항목 수정 필요 — `ccref` 스크립트 검토")


# ─────────────────────────────────────────
# main
# ─────────────────────────────────────────

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

    if show_help_if_no_args("ccref", args):
        return

    sub = args[0].lower()
    rest = args[1:]

    if sub == "list":
        cmd_list()
    elif sub == "run":
        cmd_run(rest)
    elif sub == "check":
        cmd_check()
    elif sub == "add":
        if rest and rest[0].lower() == "checklist":
            cmd_add_checklist(rest[1:])
        else:
            print(f"[ERROR] 알 수 없는 add 대상: {rest}")
            print("사용법: ccref add checklist \"항목 내용\"")
    elif sub == "version":
        print("ccref v01")
    elif sub == "status":
        cmd_list()
    else:
        print(f"[ERROR] 알 수 없는 서브명령어: {sub}")
        _print_skill_help("ccref")


if __name__ == "__main__":
    main()
