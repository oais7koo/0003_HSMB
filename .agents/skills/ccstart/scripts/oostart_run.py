#!/usr/bin/env python3
"""
oostart_run.py

This script implements the session start workflow as defined in .claude/skills/oostart/SKILL.md.
It checks the status of key documentation files and prints a checklist for the user.
"""

import sys
import os
import json
import datetime
import subprocess
import shutil
from pathlib import Path

# Windows 한글 인코딩 처리
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
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

# Configuration
DOC_DIR_SP00 = Path("00_doc/sp00")
DOC_DIR_FLAT = Path("00_doc")
GUIDE_DIR = Path(".claude/guides")
COMMON_GUIDE = "common_guide.md"
ENV_FILE = Path(".env")


def is_no_sp_project() -> bool:
    """
    SP 미사용 독립 프로젝트 여부 판정 (common_guide §4.2.6).
    우선순위:
      1. .env의 OAIS_NO_SP=1 → 독립 프로젝트로 확정
      2. 00_doc/ 존재하고 00_doc/sp00/ 없음 → flat 구조로 추정
      3. 그 외 → SP 모드
    """
    env_vars = _parse_env_file()
    if env_vars.get("OAIS_NO_SP", "").strip() in ("1", "true", "True"):
        return True
    if DOC_DIR_FLAT.exists() and not DOC_DIR_SP00.exists():
        # 00_doc/ 안에 sp 서브폴더 없이 d*.md 파일이 직접 있는 경우
        sp_subdirs = list(DOC_DIR_FLAT.glob("sp[0-9][0-9]"))
        flat_docs = list(DOC_DIR_FLAT.glob("d[0-9]*.md"))
        if not sp_subdirs and flat_docs:
            return True
    return False

# 필수 환경변수 설정
REQUIRED_ENV_VARS = {
    "PYTHONUTF8": "1",  # Windows cp949 인코딩 문제 방지
}

# 존재만 체크하는 환경변수 (값 자동 추가 안 함, 없으면 WARN)
OPTIONAL_ENV_VARS = [
    "SKILLSMP_API_KEY",  # SkillsMP marketplace API
]


def check_and_fix_env():
    """
    .env 파일에서 필수 환경변수를 확인하고, 없으면 자동 추가.
    Returns: list of (var, status) tuples
    """
    results = []

    # .env 파일 읽기
    env_content = ENV_FILE.read_text(encoding="utf-8") if ENV_FILE.exists() else ""
    env_lines = env_content.splitlines()

    # 현재 설정된 변수 파싱
    env_vars = {}
    for line in env_lines:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            env_vars[key.strip()] = val.strip()

    additions = []
    for var, expected_val in REQUIRED_ENV_VARS.items():
        if var in env_vars:
            results.append((var, "OK", env_vars[var]))
        else:
            additions.append(f"{var}={expected_val}")
            results.append((var, "FIXED", expected_val))

    # 존재만 체크하는 변수 (WARN)
    for var in OPTIONAL_ENV_VARS:
        if var in env_vars:
            results.append((var, "OK", env_vars[var][:20] + "..."))
        else:
            results.append((var, "WARN", "미설정 (.env에 추가 필요)"))

    # 없는 항목 자동 추가
    if additions:
        new_content = env_content.rstrip() + "\n" + "\n".join(additions) + "\n"
        ENV_FILE.write_text(new_content, encoding="utf-8")

    return results

def _parse_env_file():
    """현재 .env 파일을 파싱하여 dict 반환."""
    env_vars = {}
    if not ENV_FILE.exists():
        return env_vars
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            env_vars[key.strip()] = val.strip()
    return env_vars


def _update_env_var(key, value):
    """
    .env 파일에서 key 값을 value로 업데이트 (없으면 추가).
    """
    content = ENV_FILE.read_text(encoding="utf-8") if ENV_FILE.exists() else ""
    lines = content.splitlines()
    updated = False
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"{key}=") or stripped.startswith(f"{key} ="):
            new_lines.append(f"{key}={value}")
            updated = True
        else:
            new_lines.append(line)
    if not updated:
        new_lines.append(f"{key}={value}")
    ENV_FILE.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def _search_sync_target(folder_name="3_code"):
    """
    folder_name 폴더를 자동 탐색.
    탐색 순서:
      1. 현재 프로젝트 부모 디렉토리 (../3_code)
      2. Windows 드라이브 루트 (C~Z:\3_code)
      3. 홈 디렉토리 하위
    Returns: Path if found, None otherwise
    """
    cwd = Path.cwd()

    candidates = []

    # 1. 현재 프로젝트 부모 및 조부모
    for parent in [cwd.parent, cwd.parent.parent]:
        candidates.append(parent / folder_name)

    # 2. Windows 드라이브 루트
    if sys.platform == "win32":
        for drive_letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            candidates.append(Path(f"{drive_letter}:/{folder_name}"))

    # 3. 홈 디렉토리
    candidates.append(Path.home() / folder_name)

    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate

    return None


def check_sync_target():
    """
    OAIS_SYNC_TARGET 경로 검증.
    - 설정되어 있고 존재하면 OK
    - 설정은 됐지만 경로 없으면 → 자동 탐색
    - 설정 자체가 없으면 → 자동 탐색
    - 탐색 성공 → .env 자동 업데이트 (FIXED)
    - 탐색 실패 → WARN + 수동 설정 안내
    Returns: (status, path_str) where status in OK/FIXED/WARN
    """
    env_vars = _parse_env_file()
    raw_target = env_vars.get("OAIS_SYNC_TARGET", "").strip()

    # 현재 설정 경로 resolve
    resolved = None
    if raw_target:
        p = Path(raw_target)
        resolved = p if p.is_absolute() else (Path.cwd() / p).resolve()

    # 경로 존재 확인
    if resolved and resolved.exists():
        return "OK", str(resolved)

    # 자동 탐색
    found = _search_sync_target("3_code")
    if found:
        # 상대경로로 표현 가능하면 상대경로로 저장
        try:
            rel = found.relative_to(Path.cwd())
            save_val = str(rel).replace("\\", "/")
        except ValueError:
            save_val = str(found)
        _update_env_var("OAIS_SYNC_TARGET", save_val)
        return "FIXED", str(found)

    return "WARN", raw_target or "(미설정)"


# Auto-load 필수 문서 (2개만 체크)
# - 참고 문서는 on-demand로 Read 도구로 로드
# - Context 효율성: 필수 2개 = ~6k tokens, 참고 6개 = ~24k tokens
DOCS_TO_CHECK = [
    "d0000_manual.md",   # 전체 사용 매뉴얼
    "d0001_prd.md",      # PRD - 프로젝트 요구사항
    "d0004_todo.md",     # TODO/디버깅 - 이슈 추적
]

# Subproject configuration
SP_RANGE = range(1, 11)  # 01 ~ 10
PROJECT_ROOT = Path(".")


def get_current_sp() -> str:
    """oocontext 설정에서 현재 SP 번호를 읽는다.

    Returns: SP 번호 문자열 (예: "00", "03"), 미설정 시 "00"
    """
    state_file = PROJECT_ROOT / ".omc" / "state" / "context.json"
    if state_file.exists():
        try:
            data = json.loads(state_file.read_text(encoding="utf-8"))
            return data.get("sp", "00")
        except Exception:
            pass
    return "00"

def check_file_status(file_path):
    """
    Checks if a file exists and returns its last modified time.
    """
    if not file_path.exists():
        return "Not Found", None

    mtime = file_path.stat().st_mtime
    dt = datetime.datetime.fromtimestamp(mtime)
    return "Exists", dt.strftime("%Y-%m-%d %H:%M:%S")

def check_subprojects():
    """
    Scans for subproject directories (01_* ~ 10_*) and reports status.
    """
    found = []
    for sp_num in SP_RANGE:
        prefix = f"{sp_num:02d}_"
        matches = sorted(PROJECT_ROOT.glob(f"{prefix}*/"))
        for m in matches:
            if m.is_dir():
                found.append((sp_num, m.name))
    return found


def check_tutorial_sync_flags() -> dict | None:
    """
    .omc/sync-flags/tutorial_sync.json 플래그 파일 확인.
    동기화 필요 항목이 있으면 dict 반환, 없으면 None.
    """
    flags_file = PROJECT_ROOT / ".omc" / "sync-flags" / "tutorial_sync.json"
    if not flags_file.exists():
        return None
    try:
        flags = json.loads(flags_file.read_text(encoding="utf-8"))
        skill_to_tut = flags.get("skill_to_tutorial", [])
        tut_to_skill = flags.get("tutorial_to_skill", [])
        if skill_to_tut or tut_to_skill:
            return {"skill_to_tutorial": skill_to_tut, "tutorial_to_skill": tut_to_skill}
    except Exception:
        pass
    return None


def check_venv_os_compat() -> tuple[str, str]:
    """
    .venv가 현재 OS와 호환되는지 검증.
    - Windows venv: .venv/Scripts/python.exe
    - POSIX venv:   .venv/bin/python
    불일치 시 .venv 삭제 후 `uv sync` 실행.
    Returns: (status, message) where status in OK/FIXED/SKIP/WARN/ERROR
    """
    venv_dir = PROJECT_ROOT / ".venv"
    if not venv_dir.exists():
        return "SKIP", ".venv 없음 (uv sync 필요 시 수동 실행)"

    is_win = sys.platform == "win32"
    win_marker = venv_dir / "Scripts" / "python.exe"
    posix_marker = venv_dir / "bin" / "python"

    if is_win:
        compatible = win_marker.exists()
        expected = "Scripts/python.exe"
    else:
        compatible = posix_marker.exists()
        expected = "bin/python"

    if compatible:
        return "OK", f".venv ↔ {sys.platform} 호환"

    # 불일치 → 삭제 후 재생성
    try:
        shutil.rmtree(venv_dir)
    except Exception as e:
        return "ERROR", f".venv 삭제 실패: {e}"

    uv = shutil.which("uv")
    if not uv:
        return "WARN", f".venv 삭제 완료 (OS 불일치: {expected} 없음) — uv 미설치, 수동 `uv sync` 필요"

    try:
        result = subprocess.run(
            [uv, "sync"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=600
        )
        if result.returncode == 0:
            return "FIXED", f".venv 재생성 완료 (OS 불일치로 재빌드)"
        return "WARN", f"uv sync 실패: {result.stderr.strip()[:120]}"
    except subprocess.TimeoutExpired:
        return "WARN", "uv sync 타임아웃 (600s)"
    except Exception as e:
        return "WARN", str(e)[:120]


def run_qmd_update() -> tuple[str, str]:
    """
    qmd update 실행. 변경된 파일만 재인덱싱.
    Returns: (status, message) where status in OK/SKIP/WARN
    """
    try:
        if sys.platform == "win32":
            bash = shutil.which("bash")
            if not bash:
                return "SKIP", "bash 미설치"
            cmd = [bash, "-c", "qmd update"]
        else:
            cmd = ["qmd", "update"]
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=120
        )
        if result.returncode == 0:
            # 결과에서 핵심 수치 추출 (예: "Indexed: 3 new, 1 updated, 12000 unchanged")
            output = result.stdout.strip()
            for line in output.splitlines():
                if "Indexed:" in line or "new," in line or "updated" in line:
                    return "OK", line.strip()
            return "OK", "인덱스 업데이트 완료"
        else:
            return "WARN", result.stderr.strip()[:80] or "업데이트 실패"
    except FileNotFoundError:
        return "SKIP", "qmd 미설치 (npm install -g @tobilu/qmd)"
    except subprocess.TimeoutExpired:
        return "WARN", "타임아웃 (120s) - 파일 수가 많음"
    except Exception as e:
        return "WARN", str(e)[:80]


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
    # 서브명령어 없이 실행 시 도움말 출력
    if not sys.argv[1:]:
        sys.argv.append("run")

    if sys.argv[1:] and sys.argv[1] in ("help", "-h"):
        _print_skill_help("oostart")
        return

    no_sp = is_no_sp_project()
    current_sp = get_current_sp()
    if no_sp:
        sp_label = "독립 프로젝트 (SP 미사용)"
    else:
        sp_label = f"SP{int(current_sp):02d}" if current_sp != "00" else "SP00 (공통)"

    print("# oostart Session Start Workflow\n")
    print(f"Current Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Current Context: **{sp_label}**\n")

    # 환경 설정 체크
    print("## 0-0. 환경 설정 체크 (.env)\n")
    env_results = check_and_fix_env()
    for var, status, val in env_results:
        if status == "OK":
            print(f"[OK]    {var}={val}")
        else:
            print(f"[FIXED] {var}={val}  ← .env에 자동 추가됨")

    # .venv OS 호환성 체크
    venv_status, venv_msg = check_venv_os_compat()
    tag = {"OK": "[OK]   ", "FIXED": "[FIXED]", "SKIP": "[SKIP] ", "WARN": "[WARN] ", "ERROR": "[ERROR]"}.get(venv_status, "[?]    ")
    print(f"{tag} .venv OS compat: {venv_msg}")

    # oosync 대상 경로 체크
    sync_status, sync_path = check_sync_target()
    if sync_status == "OK":
        print(f"[OK]    OAIS_SYNC_TARGET={sync_path}")
    elif sync_status == "FIXED":
        print(f"[FIXED] OAIS_SYNC_TARGET={sync_path}  ← 자동 탐색 후 .env 업데이트됨")
    else:
        print(f"[WARN]  OAIS_SYNC_TARGET 경로를 찾을 수 없음 ({sync_path})")
        print(f"        → .env에 직접 설정 필요: OAIS_SYNC_TARGET=<경로>")
    print()

    # Subproject check (SP 미사용 독립 프로젝트는 스킵)
    if no_sp:
        print("## 0-1. Subproject Status\n")
        print("[독립 프로젝트] SP 체계 미사용 (.env: OAIS_NO_SP=1 또는 00_doc/ flat 구조 감지)\n")
        print("- 00_doc/ 아래 d0001~d9999 기본번호 직접 사용 (sp 서브폴더 없음)\n")
        subprojects = []
    else:
        print("## 0-1. Subproject Status\n")
        subprojects = check_subprojects()
        active_count = len(subprojects)
        max_count = len(SP_RANGE)
        print(f"Active: {active_count} / {max_count}\n")
        print("| SP | Directory | Status |")
        print("|----|-----------|--------|")
        active_nums = {sp[0] for sp in subprojects}
        for sp_num, name in subprojects:
            print(f"| SP{sp_num:02d} | {name}/ | Active |")
        for sp_num in SP_RANGE:
            if sp_num not in active_nums:
                print(f"| SP{sp_num:02d} | - | Not Created |")
        print()

    print("## 0-2. Common Guide Load (Required)\n")
    guide_path = GUIDE_DIR / COMMON_GUIDE
    status, mtime = check_file_status(guide_path)
    if status == "Exists":
        print(f"[OK] {guide_path} - Last Modified: {mtime}")
        print(f"     -> Read this file first for project standards\n")
    else:
        print(f"[WARNING] {guide_path} - Not Found")
        print(f"     -> Create common_guide.md for project standards\n")

    # QMD 인덱스 업데이트
    print("## 0-3. QMD Index Update\n")
    qmd_status, qmd_msg = run_qmd_update()
    if qmd_status == "OK":
        print(f"[OK]   qmd update 완료: {qmd_msg}")
    elif qmd_status == "SKIP":
        print(f"[SKIP] {qmd_msg}")
    else:
        print(f"[WARN] {qmd_msg}")
    print()

    print("## 1. Document Status Check\n")
    print("| Document | 위치 | Status | Last Modified |")
    print("|----------|------|--------|---------------|")

    doc_dir = DOC_DIR_FLAT if no_sp else DOC_DIR_SP00
    doc_label = "00_doc/" if no_sp else "00_doc/sp00/"

    # 공통 문서 체크
    for doc_name in DOCS_TO_CHECK:
        file_path = doc_dir / doc_name
        status, mtime = check_file_status(file_path)
        print(f"| {doc_name} | {doc_label} | {status} | {mtime if mtime else '-'} |")

    # 현재 SP 전용 문서 추가 체크 (SP 모드이면서 sp00이 아닌 경우)
    if not no_sp and current_sp != "00":
        sp_num = int(current_sp)
        sp_doc_dir = Path("00_doc") / f"sp{sp_num:02d}"
        sp_doc_label = f"00_doc/sp{sp_num:02d}/"
        sp_docs = [
            f"d{sp_num}0001_prd.md",
            f"d{sp_num}0004_todo.md",
        ]
        for doc_name in sp_docs:
            file_path = sp_doc_dir / doc_name
            status, mtime = check_file_status(file_path)
            print(f"| {doc_name} | {sp_doc_label} | {status} | {mtime if mtime else '-'} |")
    print("\n")

    print("## 2. Sync Checklist (Action Required)\n")
    print("### d0001_prd.md (Requirements)")
    print("- [ ] Check for new requirements")
    print("- [ ] Check for modified features")
    print("- [ ] Check for deleted features\n")

    print("### d0004_todo.md (Tasks & Issues)")
    print("- [ ] Check completed tasks")
    print("- [ ] Register new issues")
    print("- [ ] Update progress status\n")

    # 현재 SP 전용 체크리스트 (sp00이 아닌 경우)
    if current_sp != "00":
        sp_num = int(current_sp)
        print(f"### d{sp_num}0004_todo.md (SP{sp_num:02d} Tasks & Issues)")
        print("- [ ] Check SP-specific completed tasks")
        print("- [ ] Register SP-specific new issues")
        print("- [ ] Update SP progress status\n")

    print("### d0010_history.md (History)")
    print("- [ ] Add recent change history")
    print("- [ ] Update version information\n")

    print("## 3. oocheck Preparation\n")
    print("- [ ] Run `oocheck run` to verify code quality")
    print("  - [ ] Check for CRITICAL issues (Must fix immediately)")
    print("  - [ ] Check for ERROR issues (Fix in this session)")
    print("- [ ] Run `oocheck update` to organize documents\n")

    print("## 4. Session Ready Report Template\n")
    print("Copy and fill this section when ready:\n")
    print("```markdown")
    print("## 세션 준비 완료")
    print("")
    print("### 문서 동기화")
    print("- d0001_prd.md: [변경없음/업데이트됨]")
    print("- d0004_todo.md: [변경없음/업데이트됨]")
    print("- d0010_history.md: [변경없음/업데이트됨]")
    print("")
    print("### oocheck 결과")
    print("- CRITICAL: 0건")
    print("- ERROR: X건")
    print("- WARNING: Y건")
    print("- INFO: Z건")
    print("")
    print("### 다음 작업")
    print("- [ ] 우선 처리할 이슈")
    print("- [ ] 예정된 기능 구현")
    print("```")
    print()

    print_context_setup(current_sp, subprojects, no_sp)

def print_context_setup(current_sp: str, subprojects: list, no_sp: bool = False):
    """마지막 단계: 컨텍스트 설정 안내."""
    print("## 5. 컨텍스트 설정\n")

    if no_sp:
        print("**독립 프로젝트**: SP 체계를 사용하지 않음 (common_guide §4.2.6)\n")
        print("- 문서 경로: `00_doc/d0001~d9999` (flat 구조)")
        print("- oocontext: 기본값(SP00) 고정 — 별도 전환 불필요")
        print("- 마커: `.env`의 `OAIS_NO_SP=1` 또는 00_doc/ flat 구조 자동 감지\n")
        return

    sp_num_str = current_sp.zfill(2) if current_sp.isdigit() else "00"
    sp_label = f"SP{int(sp_num_str):02d}" if sp_num_str != "00" else "SP00 (공통)"
    print(f"현재 컨텍스트: **{sp_label}**\n")

    if subprojects:
        print("사용 가능한 서브프로젝트:\n")
        for sp_num, name in subprojects:
            marker = " ← 현재" if f"{sp_num:02d}" == sp_num_str else ""
            print(f"- SP{sp_num:02d}: {name}{marker}")
        print()

    print("[ACTION] oocontext 실행: 작업할 서브프로젝트를 지정하세요.")
    print("  예) oocontext 3  →  SP03으로 전환")
    print("      oocontext 0  →  SP00 공통으로 초기화")
    print("      oocontext    →  현재 컨텍스트 확인만")


if __name__ == "__main__":
    main()
