#!/usr/bin/env python3
"""oosync_run.py - Vibe 환경 동기화 (상세: doc/a0009_script.md)"""

import os
import sys

# Windows cp949 환경에서 UTF-8 출력 강제
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import shutil
import filecmp
import json
from datetime import datetime
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

# ============================================================
# Configuration
# ============================================================

CURRENT_PROJECT = Path.cwd()
PARENT_DIR = CURRENT_PROJECT.parent

# OAIS 프로젝트에서만 실행 강제 (정본 원칙)
if not (CURRENT_PROJECT / ".oais_root").exists():
    print("[ERROR] oosync는 OAIS(1_oais) 프로젝트에서만 실행 가능합니다.")
    print(f"  현재 위치: {CURRENT_PROJECT}")
    print(f"  OAIS가 .codex/ 의 정본(source of truth)이므로, 동기화는 OAIS에서만 수행하세요.")
    sys.exit(1)
SCRIPT_DIR = Path(__file__).parent
TEMPLATE_DIR = SCRIPT_DIR.parent / "templates"  # .agents/skills/ccsync/templates

# 동기화 대상 스캔 경로 (.env의 OAIS_SYNC_TARGET 또는 기본값)
_sync_target_env = os.environ.get("OAIS_SYNC_TARGET", "")
if _sync_target_env:
    _sync_target_path = Path(_sync_target_env)
    TARGET_SCAN_DIR = (_sync_target_path if _sync_target_path.is_absolute()
                       else (CURRENT_PROJECT / _sync_target_path).resolve())
elif PARENT_DIR.name == "3_code":
    # 프로젝트가 이미 3_code/ 내부에 있으면 PARENT_DIR 자체가 스캔 대상
    TARGET_SCAN_DIR = PARENT_DIR
else:
    TARGET_SCAN_DIR = PARENT_DIR / "3_code"

# 추가 스캔 경로 (TARGET_SCAN_DIR 외부 프로젝트)
EXTRA_SCAN_PATHS = [
    Path("C:/Users/ookoo/home/1_oo"),
]

# sync_config.json으로 대상 프로젝트 오버라이드
_sync_config_path = Path(__file__).parent.parent / "references" / "sync_config.json"
if _sync_config_path.exists():
    try:
        _sync_cfg = json.loads(_sync_config_path.read_text(encoding="utf-8"))
        _cfg_targets = [Path(t["path"]) for t in _sync_cfg.get("targets", []) if t.get("path")]
        if _cfg_targets:
            EXTRA_SCAN_PATHS = _cfg_targets
    except Exception:
        pass

# 동기화 대상 파일/폴더 (v/는 제외 - 레거시, 최초 삭제 후 동기화 불필요)
SYNC_TARGETS = [
    ".codex/",
    "00_doc/tutorial/",
    "CLAUDE.md",
    "AGENTS.md",
    "GEMINI.md",
    ".mcp.json",
    ".codex/",
    ".agents/",
    ".gemini/",
    "cclaude.bat",
    "cclaude.sh",
    "ccodex.bat",
    "gemma.ps1",
    "gemma.sh",
    ".github/",
]

# 동기화 제외 패턴
EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    ".git",
    "tmp",
    ".venv",
    "node_modules",
    "worktrees",  # git/에이전트 격리 worktree 디렉토리 (.codex/worktrees/ — 동기화 대상 아님)
    "settings.local.json",  # 프로젝트별 로컬 설정
    "last_model.json",  # gemma 모델 선택 (머신별 로컬 설정)
    "sp_config.json",  # 프로젝트별 SP 목록 (cccontext/references/sp_config.json)
    "scheduled_tasks.lock",  # OMC 스케줄러 lock 파일 (프로젝트별 로컬)
    "skills_to_codex",  # ccporting 산출물 (대상 프로젝트별 독립 생성)
    ".ccporting_state",  # ccporting 포팅 상태 (머신별 로컬)
    ".ccporting_audit_report.json",  # ccporting 감사 결과 (머신별 로컬)
]

# Vibe 환경 판별 기준 (.codex/ 존재 여부로 Full 판정)
VIBE_INDICATORS = {
    "claude_dir": ".codex",
}


# ============================================================
# Git-based Sync State
# ============================================================

SYNC_STATE_DIR = CURRENT_PROJECT / "data" / "04_claude_backup" / ".oosync_state"


def _get_git_commit_hash() -> str:
    """현재 OAIS repo의 HEAD 커밋 해시 반환"""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(CURRENT_PROJECT), capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def _get_git_changed_files(since_hash: str) -> set[str]:
    """since_hash 이후 .codex/ 및 SYNC_TARGETS에서 변경된 파일 목록"""
    import subprocess
    changed = set()
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", since_hash, "HEAD", "--"] + [t.rstrip("/") for t in SYNC_TARGETS],
            cwd=str(CURRENT_PROJECT), capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            for line in result.stdout.strip().splitlines():
                if line.strip():
                    changed.add(line.strip().replace("\\", "/"))
    except Exception:
        pass
    return changed


def load_sync_state(project_name: str) -> dict:
    """프로젝트별 동기화 상태 로드"""
    state_file = SYNC_STATE_DIR / f"{project_name}.json"
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_sync_state(project_name: str, commit_hash: str, file_hashes: dict | None = None):
    """동기화 완료 시 커밋 해시 + 파일별 md5 해시 기록"""
    SYNC_STATE_DIR.mkdir(parents=True, exist_ok=True)
    existing = load_sync_state(project_name)
    state = {
        "last_sync_commit": commit_hash,
        "last_sync_date": datetime.now().isoformat(),
        "project": project_name,
        "file_hashes": file_hashes if file_hashes is not None else existing.get("file_hashes", {}),
    }
    state_file = SYNC_STATE_DIR / f"{project_name}.json"
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def get_git_changed_since_sync(project_name: str) -> tuple[set[str], str, str]:
    """마지막 동기화 이후 git에서 변경된 파일 반환

    Returns:
        (changed_files, last_sync_hash, current_hash)
    """
    state = load_sync_state(project_name)
    last_hash = state.get("last_sync_commit", "")
    current_hash = _get_git_commit_hash()

    if not last_hash or not current_hash:
        return set(), last_hash, current_hash

    if last_hash == current_hash:
        return set(), last_hash, current_hash

    changed = _get_git_changed_files(last_hash)
    return changed, last_hash, current_hash


# ============================================================
# Helper Functions
# ============================================================

def is_excluded(path: Path) -> bool:
    """Check if path should be excluded from sync."""
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith("*"):
            if path_str.endswith(pattern[1:]):
                return True
        elif pattern in path_str:
            return True
    return False


def get_file_mtime(file_path: Path) -> datetime | None:
    """Get file modification time."""
    if file_path.exists():
        return datetime.fromtimestamp(file_path.stat().st_mtime)
    return None


def get_git_blob_hash(file_path: Path) -> str:
    """파일의 git blob hash 반환 (git hash-object 사용)."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "hash-object", str(file_path)],
            capture_output=True, text=True
        )
        return result.stdout.strip()
    except Exception:
        return ""


def find_git_root(path: Path) -> Path | None:
    """주어진 경로에서 git 루트 디렉토리 탐색."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, cwd=str(path if path.is_dir() else path.parent)
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except Exception:
        pass
    return None


def blob_in_git_history(repo_root: Path, rel_path: str, blob_hash: str) -> bool:
    """blob hash가 해당 repo의 git 히스토리(해당 파일)에 존재하는지 확인."""
    import subprocess
    if not blob_hash or not repo_root:
        return False
    try:
        log_result = subprocess.run(
            ["git", "log", "--all", "--format=%H", "--", rel_path],
            capture_output=True, text=True, cwd=str(repo_root)
        )
        commits = [c for c in log_result.stdout.strip().split("\n") if c]
        for commit in commits:
            ls_result = subprocess.run(
                ["git", "ls-tree", commit, rel_path],
                capture_output=True, text=True, cwd=str(repo_root)
            )
            # ls-tree 출력: <mode> blob <blob_hash>\t<path>
            if blob_hash in ls_result.stdout:
                return True
    except Exception:
        pass
    return False


def get_file_hash(file_path: Path) -> str:
    """파일 md5 해시 반환 (존재하지 않으면 빈 문자열)."""
    import hashlib
    if not file_path.exists() or not file_path.is_file():
        return ""
    h = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def compare_files(source: Path, target: Path, last_hash: str = "") -> str:
    """
    Compare two files and return status.

    Args:
        source: Source file path
        target: Target file path
        last_hash: MD5 hash at last sync time. If provided, detects CONFLICT
                   (both sides changed since last sync).

    Returns:
        ONLY_SOURCE : Only exists in source
        ONLY_TARGET : Only exists in target
        NEWER_SOURCE: Source is newer
        NEWER_TARGET: Target is newer
        CONFLICT    : Both sides changed since last sync (merge needed)
        SAME        : Files are identical
    """
    source_exists = source.exists()
    target_exists = target.exists()

    if source_exists and not target_exists:
        return "ONLY_SOURCE"
    elif not source_exists and target_exists:
        return "ONLY_TARGET"
    elif source_exists and target_exists:
        if source.is_file() and target.is_file():
            if filecmp.cmp(source, target, shallow=False):
                return "SAME"
            # CRLF/LF 정규화 후 내용 비교 (줄바꿈만 다른 경우 SAME 처리)
            try:
                src_text = source.read_bytes().replace(b"\r\n", b"\n")
                tgt_text = target.read_bytes().replace(b"\r\n", b"\n")
                if src_text == tgt_text:
                    return "SAME"
            except Exception:
                pass
            # 1) last_hash 기반 정확 분류 (양쪽 변경 추적)
            if last_hash:
                source_hash = get_file_hash(source)
                target_hash = get_file_hash(target)
                src_changed = (source_hash != last_hash)
                tgt_changed = (target_hash != last_hash)
                if src_changed and tgt_changed:
                    return "CONFLICT"
                if src_changed:
                    return "NEWER_SOURCE"
                if tgt_changed:
                    return "NEWER_TARGET"
                # 양쪽 모두 last_hash와 같은데 내용이 다른 이론적 모순
                return "CONFLICT"
            # 2) git 히스토리 양방향 검사
            source_repo = find_git_root(source)
            if source_repo:
                try:
                    rel_path = str(source.relative_to(source_repo)).replace("\\", "/")
                    target_blob = get_git_blob_hash(target)
                    if target_blob and blob_in_git_history(source_repo, rel_path, target_blob):
                        return "NEWER_SOURCE"
                except Exception:
                    pass
            target_repo = find_git_root(target)
            if target_repo:
                try:
                    target_rel = str(target.relative_to(target_repo)).replace("\\", "/")
                    source_blob = get_git_blob_hash(source)
                    if source_blob and blob_in_git_history(target_repo, target_rel, source_blob):
                        return "NEWER_TARGET"
                except Exception:
                    pass
            # 3) 결정 불가: 1_oais → 3_code/* 일방향 push 모델이므로 NEWER_SOURCE 폴백
            return "NEWER_SOURCE"
        return "DIFFERENT"
    return "NONE"


def get_status_symbol(status: str) -> str:
    """Get display symbol for status."""
    symbols = {
        "ONLY_SOURCE": "->",
        "ONLY_TARGET": "<-",
        "NEWER_SOURCE": ">>",
        "NEWER_TARGET": "<<",
        "CONFLICT": "!!",
        "SAME": "==",
        "DIFFERENT": "!=",
        "NONE": "--",
    }
    return symbols.get(status, "?")


# ============================================================
# Template System
# ============================================================

import re

# 공용 template_loader import (스킬 간 공유)
_shared_dir = str(SCRIPT_DIR.parent.parent)  # .codex/skills
if _shared_dir not in sys.path:
    sys.path.insert(0, _shared_dir)
from _shared.template_loader import load_template_block  # noqa: E402


# 템플릿 파일 경로
TEMPLATE_LIST_PATH = TEMPLATE_DIR / "oosync_list.md"

# 템플릿 문자열 정의
TEMPLATE_VIEW_HEADER = """# ccsync view - 차이점 비교

## 비교 대상

| 항목 | 값 |
|------|-----|
| 소스 (현재) | `{source_project}` |
| 대상 | `{target_project}` |
| 대상 Vibe 상태 | {env_status} |
| .codex/ | {has_claude} |
"""

TEMPLATE_VIEW_SUMMARY_HEADER = """
## 요약

| 상태 | 기호 | 설명 | 개수 |
|------|------|------|------|
| SAME | == | 동일 | {same_count} |
"""

TEMPLATE_VIEW_SUMMARY_ROW = "| {status} | {symbol} | {desc} | {count} |"

TEMPLATE_VIEW_TOTAL = """
**총 {total_files}개 파일 중 {diff_count}개 차이**
"""

TEMPLATE_VIEW_DETAIL_HEADER = """
## 상세 차이점

| 상태 | 파일 | 소스 수정일 | 대상 수정일 |
|:----:|------|------------|------------|
"""

TEMPLATE_VIEW_DETAIL_ROW = "| {symbol} | `{file_path}` | {source_mtime} | {target_mtime} |"

TEMPLATE_VIEW_NO_DIFF = """
모든 파일이 동일합니다.
"""

# 상태 정보 매핑
STATUS_INFO = {
    "ONLY_SOURCE": ("->", "대상에 없음 -> 복사 필요"),
    "ONLY_TARGET": ("<-", "현재에 없음 <- 가져오기"),
    "NEWER_SOURCE": (">>", "현재가 최신 -> 덮어쓰기"),
    "NEWER_TARGET": ("<<", "대상이 최신 <- 가져오기"),
    "CONFLICT":     ("!!", "양쪽 모두 변경됨 -> 수동 merge 필요"),
}

# Diff 상태 설명 (더 명확한 버전)
DIFF_STATUS_DESC = {
    "ONLY_SOURCE": ("->", "대상에 없음"),
    "ONLY_TARGET": ("<-", "소스에 없음"),
    "NEWER_SOURCE": (">>", "소스가 최신"),
    "NEWER_TARGET": ("<<", "대상이 최신"),
    "CONFLICT":    ("!!", "양쪽 모두 변경 (CONFLICT)"),
}

# ============================================================
# Diff Template System
# ============================================================

TEMPLATE_DIFF_ALL_HEADER = """# ccsync diff - 전체 차이점 비교

## 비교 대상

| 항목 | 값 |
|------|-----|
| 소스 (현재) | `{source_project}` |
| 대상 | `{target_project}` |
| 차이 파일 수 | {total_count}개 |

---
"""

TEMPLATE_DIFF_FILE_HEADER = """
## [{current_index}/{total_count}] {file_path}

| 항목 | 값 |
|------|-----|
| 소스 (현재) | `{source_project}` - {source_mtime} |
| 대상 | `{target_project}` - {target_mtime} |
| 비교 결과 | **{status_desc}** ({status_symbol}) |
| 변경 내용 | {change_summary} |
"""

TEMPLATE_DIFF_CONTENT = """
### 차이점

```diff
{diff_content}
```
"""

TEMPLATE_DIFF_SEPARATOR = """
---
"""

TEMPLATE_DIFF_ONLY_SOURCE = """
### 파일 내용 (소스에만 존재)

```
{file_content}
```
"""

TEMPLATE_DIFF_ONLY_TARGET = """
### 파일 내용 (대상에만 존재)

```
{file_content}
```
"""


def generate_change_summary(status: str, added: int, removed: int, line_count: int = 0) -> str:
    """변경 요약 문자열 생성"""
    if status == "ONLY_SOURCE":
        return f"소스에만 존재 (신규 파일, {line_count}줄)"
    elif status == "ONLY_TARGET":
        return f"대상에만 존재 ({line_count}줄)"
    elif status == "NEWER_SOURCE":
        if added > 0 and removed == 0:
            return f"소스에 +{added}줄 추가 (대상에 없음)"
        elif added == 0 and removed > 0:
            return f"소스에서 -{removed}줄 삭제"
        else:
            return f"소스에 +{added}줄, -{removed}줄 변경"
    elif status == "NEWER_TARGET":
        if added > 0 and removed == 0:
            return f"대상에 +{added}줄 추가 (소스에 없음)"
        elif added == 0 and removed > 0:
            return f"대상에서 -{removed}줄 삭제"
        else:
            return f"대상에 +{added}줄, -{removed}줄 변경"
    return "알 수 없음"


def render_diff_output(data: dict, include_content: bool = True) -> str:
    """
    템플릿을 사용하여 diff 출력 생성

    Args:
        data: 렌더링에 필요한 데이터
        include_content: diff 내용 포함 여부

    Returns:
        렌더링된 출력 문자열
    """
    output = []

    # 파일 헤더
    output.append(TEMPLATE_DIFF_FILE_HEADER.format(
        current_index=data["current_index"],
        total_count=data["total_count"],
        file_path=data["file_path"],
        source_project=data["source_project"],
        target_project=data["target_project"],
        source_mtime=data["source_mtime"],
        target_mtime=data["target_mtime"],
        status_desc=data["status_desc"],
        status_symbol=data["status_symbol"],
        change_summary=data["change_summary"],
    ))

    # diff 내용
    if include_content and data.get("diff_content"):
        if data["status"] == "ONLY_SOURCE":
            output.append(TEMPLATE_DIFF_ONLY_SOURCE.format(
                file_content=data["diff_content"]
            ))
        elif data["status"] == "ONLY_TARGET":
            output.append(TEMPLATE_DIFF_ONLY_TARGET.format(
                file_content=data["diff_content"]
            ))
        else:
            output.append(TEMPLATE_DIFF_CONTENT.format(
                diff_content=data["diff_content"]
            ))

    output.append(TEMPLATE_DIFF_SEPARATOR)

    return "\n".join(output)


def render_view_output(data: dict) -> str:
    """
    템플릿을 사용하여 view 출력 생성

    Args:
        data: 렌더링에 필요한 데이터
            - source_project: 소스 프로젝트명
            - target_project: 대상 프로젝트명
            - env_status: 환경 상태
            - has_claude: .codex/ 존재 여부
            - has_claude: .codex/ 존재 여부
            - same_count: 동일 파일 수
            - status_counts: 상태별 개수 딕셔너리
            - comparison_results: 비교 결과 리스트

    Returns:
        렌더링된 출력 문자열
    """
    output = []

    # 헤더
    output.append(TEMPLATE_VIEW_HEADER.format(
        source_project=data["source_project"],
        target_project=data["target_project"],
        env_status=data["env_status"],
        has_claude=data["has_claude"],
    ))

    # 요약 테이블
    output.append(TEMPLATE_VIEW_SUMMARY_HEADER.format(same_count=data["same_count"]))

    for status, (symbol, desc) in STATUS_INFO.items():
        count = data["status_counts"].get(status, 0)
        if count > 0:
            output.append(TEMPLATE_VIEW_SUMMARY_ROW.format(
                status=status,
                symbol=symbol,
                desc=desc,
                count=count
            ))

    # 총계
    total_files = data["same_count"] + len(data["comparison_results"])
    diff_count = len(data["comparison_results"])
    output.append(TEMPLATE_VIEW_TOTAL.format(
        total_files=total_files,
        diff_count=diff_count
    ))

    # 상세 차이점
    if data["comparison_results"]:
        output.append(TEMPLATE_VIEW_DETAIL_HEADER)
        for result in data["comparison_results"]:
            source_dt = result["source_mtime"].strftime("%Y-%m-%d %H:%M") if result["source_mtime"] else "-"
            target_dt = result["target_mtime"].strftime("%Y-%m-%d %H:%M") if result["target_mtime"] else "-"
            output.append(TEMPLATE_VIEW_DETAIL_ROW.format(
                symbol=result["symbol"],
                file_path=result["path"],
                source_mtime=source_dt,
                target_mtime=target_dt
            ))
    else:
        output.append(TEMPLATE_VIEW_NO_DIFF)

    return "\n".join(output)


def render_box_table(projects: list) -> str:
    """
    박스 문자를 사용하여 테이블 생성

    Args:
        projects: 프로젝트 리스트 [{name, status, has_claude, push, pull}]

    Returns:
        박스 테이블 문자열
    """
    col_widths = {
        "idx": 4,
        "name": max(7, max((len(p["name"]) for p in projects), default=7)) + 2,
        "status": 9,
        "codex": 10,
        "push": 6,
        "pull": 6,
    }

    def sep_line(left, mid, right):
        return (left + "─" * col_widths["idx"] + mid +
                "─" * col_widths["name"] + mid +
                "─" * col_widths["status"] + mid +
                "─" * col_widths["codex"] + mid +
                "─" * col_widths["push"] + mid +
                "─" * col_widths["pull"] + right)

    lines = []
    lines.append(sep_line("┌", "┬", "┐"))

    header = ("│" + " # ".center(col_widths["idx"]) +
              "│" + " Project".ljust(col_widths["name"]) +
              "│" + " Status ".center(col_widths["status"]) +
              "│" + " .codex/ ".center(col_widths["codex"]) +
              "│" + " Push ".center(col_widths["push"]) +
              "│" + " Pull ".center(col_widths["pull"]) + "│")
    lines.append(header)
    lines.append(sep_line("├", "┼", "┤"))

    for idx, proj in enumerate(projects, 1):
        row = ("│" + str(idx).rjust(col_widths["idx"] - 1) + " " +
               "│" + " " + proj["name"].ljust(col_widths["name"] - 1) +
               "│" + proj["status"].center(col_widths["status"]) +
               "│" + proj["has_claude"].center(col_widths["codex"]) +
               "│" + proj["push"].center(col_widths["push"]) +
               "│" + proj["pull"].center(col_widths["pull"]) + "│")
        lines.append(row)

    lines.append(sep_line("└", "┴", "┘"))
    return "\n".join(lines)


def render_list_output(data: dict) -> str:
    """
    템플릿을 사용하여 list 출력 생성

    Args:
        data: 렌더링에 필요한 데이터
            - scan_path: 스캔 경로
            - projects: 프로젝트 리스트 [{name, status, has_claude, sync}]
            - total_count: 총 프로젝트 수

    Returns:
        렌더링된 출력 문자열
    """
    # 템플릿 파일에서 로드 시도
    template = load_template_block(TEMPLATE_LIST_PATH)

    # 템플릿이 없으면 기본 템플릿 사용
    if not template:
        template = """# ccsync list - 프로젝트 목록

스캔 경로: `{scan_path}`

{table_output}

총 {total_count}개 프로젝트 발견

## 상태 설명
- Full: vibe 환경 구축 완료 (.codex/ 존재)
- None: vibe 환경 없음 (새로 구축 가능)

## Sync 컬럼
- OK: 동기화 완료 (차이 없음)
- 숫자: 동기화 필요 (차이 파일 수)
- -: 비교 불가 (Full 상태 아님)"""

    # 박스 테이블 생성
    table_output = render_box_table(data["projects"])

    # 템플릿 렌더링
    return template.format(
        scan_path=data["scan_path"],
        table_output=table_output,
        total_count=data["total_count"]
    )


def find_project_by_name(name: str) -> Path | None:
    """
    Find project by name or 4-digit prefix.

    Examples:
        "0003" -> "0003_CCone"
        "0003_CCone" -> "0003_CCone"
        "1_oo" -> EXTRA_SCAN_PATHS의 1_oo
    """
    # Check extra scan paths first (exact match by folder name)
    for extra_path in EXTRA_SCAN_PATHS:
        if extra_path.exists() and extra_path.name == name:
            return extra_path
        # Also match partial name
        if extra_path.exists() and name in extra_path.name:
            return extra_path

    # Direct match in TARGET_SCAN_DIR (3_code/)
    direct_path = TARGET_SCAN_DIR / name
    if direct_path.exists():
        return direct_path

    # Try prefix match (4-digit number) in TARGET_SCAN_DIR
    if TARGET_SCAN_DIR.exists() and len(name) == 4 and name.isdigit():
        for item in TARGET_SCAN_DIR.iterdir():
            if item.is_dir() and item.name.startswith(name + "_"):
                return item
            if item.is_dir() and item.name == name:
                return item

    # Fallback: search in TARGET_SCAN_DIR by partial name
    if TARGET_SCAN_DIR.exists():
        for item in TARGET_SCAN_DIR.iterdir():
            if item.is_dir() and name in item.name:
                return item

    return None


def collect_files(base_path: Path, relative_path: str) -> list[Path]:
    """Collect all files under a path recursively."""
    full_path = base_path / relative_path
    files = []

    if not full_path.exists():
        return files

    if full_path.is_file():
        if not is_excluded(full_path):
            files.append(Path(relative_path))
    elif full_path.is_dir():
        for item in full_path.rglob("*"):
            if item.is_file() and not is_excluded(item):
                rel = item.relative_to(base_path)
                files.append(rel)

    return files


def quick_diff_count(target_project: Path) -> int:
    """Quick count of differences between current and target project."""
    push, pull = quick_diff_detail(target_project)
    return push + pull


def quick_diff_detail(target_project: Path) -> tuple[int, int]:
    """Return (push_count, pull_count) for a target project.

    push: ONLY_SOURCE, NEWER_SOURCE  (source → target)
    pull: ONLY_TARGET, NEWER_TARGET, CONFLICT  (target → source)
    """
    all_files = set()
    for target in SYNC_TARGETS:
        source_files = collect_files(CURRENT_PROJECT, target.rstrip("/"))
        target_files = collect_files(target_project, target.rstrip("/"))
        all_files.update(source_files)
        all_files.update(target_files)

    push_count = 0
    pull_count = 0
    for rel_path in all_files:
        source_path = CURRENT_PROJECT / rel_path
        target_path = target_project / rel_path
        status = compare_files(source_path, target_path)
        if status in ("ONLY_SOURCE", "NEWER_SOURCE"):
            push_count += 1
        elif status in ("ONLY_TARGET", "NEWER_TARGET", "CONFLICT"):
            pull_count += 1

    return push_count, pull_count


# ============================================================
# Commands
# ============================================================

def cmd_status():
    """Show status and available subcommands."""
    print("# ccsync - Vibe 환경 동기화\n")
    print("## 서브명령어\n")
    print("| 명령어 | 설명 |")
    print("|--------|------|")
    print("| `ccsync status` | 현재 상태 (이 화면) |")
    print("| `ccsync list` | 동기화 가능한 프로젝트 목록 |")
    print("| `ccsync files` | 동기화 대상 파일/폴더 목록 |")
    print("| `ccsync view [project]` | 차이점 비교 (읽기 전용) |")
    print("| `ccsync run [project]` | 동기화 실행 |")
    print("| `ccsync run --push-only` | **push만 필요한 모든 프로젝트 일괄 동기화** |")
    print("| `ccsync run --push-only --dry-run` | 동기화 미리보기 (실제 복사 안 함) |")
    print("| `ccsync diff [project] [file]` | 파일 내용 비교 |")
    print()
    print(f"## 현재 프로젝트\n")
    print(f"- 경로: `{CURRENT_PROJECT}`")
    print(f"- 대상 스캔: `{TARGET_SCAN_DIR}`")


def cmd_list():
    """List projects in 3_code/ directory with vibe environment status."""
    # 프로젝트 데이터 수집
    projects = []

    # 1. TARGET_SCAN_DIR (3_code/) 내 프로젝트
    if TARGET_SCAN_DIR.exists():
        for item in sorted(TARGET_SCAN_DIR.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                has_claude = (item / VIBE_INDICATORS["claude_dir"]).exists()

                if has_claude:
                    status = "Full"
                else:
                    status = "None"

                if has_claude:
                    push_cnt, pull_cnt = quick_diff_detail(item)
                    push_mark = "OK" if push_cnt == 0 else str(push_cnt)
                    pull_mark = "OK" if pull_cnt == 0 else str(pull_cnt)
                else:
                    push_mark = pull_mark = "-"

                projects.append({
                    "name": item.name,
                    "status": status,
                    "has_claude": "O" if has_claude else "X",
                    "push": push_mark,
                    "pull": pull_mark,
                })
    else:
        print(f"[WARN] 대상 스캔 디렉토리가 없습니다: {TARGET_SCAN_DIR}")

    # 2. EXTRA_SCAN_PATHS 프로젝트 추가
    for extra_path in EXTRA_SCAN_PATHS:
        if extra_path.exists() and extra_path.is_dir():
            has_claude = (extra_path / VIBE_INDICATORS["claude_dir"]).exists()

            if has_claude:
                status = "Full"
            else:
                status = "None"

            if has_claude:
                push_cnt, pull_cnt = quick_diff_detail(extra_path)
                push_mark = "OK" if push_cnt == 0 else str(push_cnt)
                pull_mark = "OK" if pull_cnt == 0 else str(pull_cnt)
            else:
                push_mark = pull_mark = "-"

            projects.append({
                "name": f"[EXT] {extra_path.name}",
                "status": status,
                "has_claude": "O" if has_claude else "X",
                "push": push_mark,
                "pull": pull_mark,
            })

    # 스캔 경로 문자열
    scan_paths = str(TARGET_SCAN_DIR)
    if EXTRA_SCAN_PATHS:
        extra_names = [str(p) for p in EXTRA_SCAN_PATHS if p.exists()]
        if extra_names:
            scan_paths += " + " + ", ".join(extra_names)

    # 템플릿 기반 출력 생성
    template_data = {
        "scan_path": scan_paths,
        "projects": projects,
        "total_count": len(projects),
    }

    output = render_list_output(template_data)
    print(output)


def cmd_files():
    """Show sync target files/folders."""
    print("# ccsync files - 동기화 대상\n")
    print("## 기본 동기화 대상\n")

    for target in SYNC_TARGETS:
        target_path = CURRENT_PROJECT / target
        if target_path.exists():
            status = "[존재]"
        else:
            status = "[없음]"
        print(f"- `{target}` {status}")

    print("\n## v/ 폴더 상세\n")
    v_path = CURRENT_PROJECT / "v"
    if v_path.exists():
        print("```")
        for item in sorted(v_path.iterdir()):
            if is_excluded(item):
                continue
            if item.is_dir():
                count = len(list(item.rglob("*")))
                print(f"  {item.name}/  ({count} files)")
            else:
                print(f"  {item.name}")
        print("```")

    print("\n## .codex/ 폴더 상세\n")
    claude_path = CURRENT_PROJECT / ".codex"
    if claude_path.exists():
        print("```")
        for item in sorted(claude_path.iterdir()):
            if is_excluded(item):
                continue
            if item.is_dir():
                count = len(list(item.rglob("*")))
                print(f"  {item.name}/  ({count} files)")
            else:
                print(f"  {item.name}")
        print("```")

    print("\n## 제외 패턴\n")
    for pattern in EXCLUDE_PATTERNS:
        print(f"- `{pattern}`")


def cmd_view(project_name: str | None = None):
    """View differences with target project (read-only)."""
    if not project_name:
        print("# ccsync view - 차이점 비교\n")
        print("사용법: `ccsync view [project_name]`\n")
        print("프로젝트명 또는 4자리 번호 입력 가능 (예: 0003 또는 0003_CCone)\n")
        print("`ccsync list`로 프로젝트 목록을 먼저 확인하세요.")
        return

    target_project = find_project_by_name(project_name)
    if not target_project:
        print(f"오류: 프로젝트 '{project_name}'를 찾을 수 없습니다.")
        print("4자리 번호 또는 전체 프로젝트명을 입력하세요.")
        return

    # Check vibe environment status
    has_claude = (target_project / VIBE_INDICATORS["claude_dir"]).exists()
    if has_claude:
        env_status = "Full"
    else:
        env_status = "None"

    # Collect all files to compare
    all_files = set()
    for target in SYNC_TARGETS:
        source_files = collect_files(CURRENT_PROJECT, target.rstrip("/"))
        target_files = collect_files(target_project, target.rstrip("/"))
        all_files.update(source_files)
        all_files.update(target_files)

    # Compare files
    comparison_results = []
    same_count = 0
    _sync_state_view = load_sync_state(target_project.name)
    _file_hashes_view = _sync_state_view.get("file_hashes", {})
    for rel_path in sorted(all_files):
        source_path = CURRENT_PROJECT / rel_path
        target_path = target_project / rel_path

        last_hash = _file_hashes_view.get(str(rel_path).replace("\\", "/"), "")
        status = compare_files(source_path, target_path, last_hash)
        if status == "SAME":
            same_count += 1
        else:
            comparison_results.append({
                "path": str(rel_path),
                "status": status,
                "symbol": get_status_symbol(status),
                "source_mtime": get_file_mtime(source_path),
                "target_mtime": get_file_mtime(target_path),
            })

    # Build status counts
    status_counts = {}
    for result in comparison_results:
        status = result["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    # Prepare data for template rendering
    template_data = {
        "source_project": CURRENT_PROJECT.name,
        "target_project": target_project.name,
        "env_status": env_status,
        "has_claude": "O" if has_claude else "X",
        "same_count": same_count,
        "status_counts": status_counts,
        "comparison_results": comparison_results,
    }

    # Render and print output using template
    output = render_view_output(template_data)
    print(output)


def check_push_only(target_project: Path, allow_delete: bool = False, allow_add: bool = False, force_conflict: bool = False) -> tuple[list, list, list]:
    """
    파일 단위로 push/skip/delete 분류.

    Returns:
        (push_files, skip_files, delete_files)
        push_files: list of Path - ONLY_SOURCE, NEWER_SOURCE (소스가 최신, push 가능)
        skip_files: list of (Path, status) - NEWER_TARGET, ONLY_TARGET (대상이 최신, pull 필요)
        delete_files: list of Path - ONLY_TARGET with allow_delete (대상에만 있는 파일, 삭제 대상)
    """
    all_files = set()
    for target in SYNC_TARGETS:
        source_files = collect_files(CURRENT_PROJECT, target.rstrip("/"))
        target_files = collect_files(target_project, target.rstrip("/"))
        all_files.update(source_files)
        all_files.update(target_files)

    push_files = []
    skip_files = []
    delete_files = []

    _sync_state_push = load_sync_state(target_project.name)
    _file_hashes_push = _sync_state_push.get("file_hashes", {})
    for rel_path in sorted(all_files):
        source_path = CURRENT_PROJECT / rel_path
        target_path = target_project / rel_path
        last_hash = _file_hashes_push.get(str(rel_path).replace("\\", "/"), "")
        status = compare_files(source_path, target_path, last_hash)

        if status == "SAME":
            continue
        elif status == "CONFLICT":
            if force_conflict:
                push_files.append(rel_path)
            else:
                # 양쪽 모두 변경 → 수동 merge 필요, push 금지
                skip_files.append((rel_path, status))
        elif status in ("ONLY_SOURCE", "NEWER_SOURCE"):
            push_files.append(rel_path)
        elif status == "ONLY_TARGET":
            if allow_delete:
                delete_files.append(rel_path)
            elif allow_add:
                pass  # 유지 (무시)
            else:
                skip_files.append((rel_path, status))
        elif status == "NEWER_TARGET":
            skip_files.append((rel_path, status))

    return push_files, skip_files, delete_files


def sync_project_files(target_project: Path, push_files: list, delete_files: list = None, dry_run: bool = False) -> bool:
    """파일 단위로 push_files만 동기화 (skip_files는 건너뜀)."""
    project_name = target_project.name

    git_changed, last_hash, current_hash = get_git_changed_since_sync(project_name)
    if git_changed:
        print(f"    [GIT] 마지막 동기화({last_hash[:8]}) 이후 변경: {len(git_changed)}개 파일")

    for rel_path in push_files:
        source_path = CURRENT_PROJECT / rel_path
        target_path = target_project / rel_path
        if dry_run:
            print(f"    [DRY-RUN] 복사 예정: {rel_path}")
        else:
            if source_path.exists():
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, target_path)

    if delete_files:
        deleted_parents = set()
        for rel_path in delete_files:
            target_path = target_project / rel_path
            if dry_run:
                print(f"    [DRY-RUN] 삭제 예정: {rel_path}")
            else:
                if target_path.exists():
                    target_path.unlink()
                    deleted_parents.add(target_path.parent)
        # 삭제로 비어버린 디렉터리 정리 (target_project 위로는 올라가지 않음)
        if not dry_run:
            for parent in deleted_parents:
                d = parent
                while d != target_project and d.is_dir():
                    try:
                        next(d.iterdir())
                        break  # 비어있지 않음 → 중단
                    except StopIteration:
                        d.rmdir()
                        d = d.parent

    # 복사된 파일의 해시 업데이트
    if not dry_run:
        # 정합성 보장: 동기화 직후 target 전체 스캔으로 file_hashes 재구성.
        # push 안 된 파일도 현재 target hash를 기록해야 다음 비교 시
        # last_hash 가 stale 되어 양쪽 변경으로 오인되는 일이 없다.
        all_hashes = {}
        for sync_target in SYNC_TARGETS:
            tp = target_project / sync_target.rstrip("/")
            if tp.exists():
                if tp.is_file():
                    all_hashes[sync_target.rstrip("/")] = get_file_hash(tp)
                else:
                    for f in tp.rglob("*"):
                        if f.is_file() and not is_excluded(f):
                            rel = str(f.relative_to(target_project)).replace("\\", "/")
                            all_hashes[rel] = get_file_hash(f)
        save_sync_state(project_name, current_hash or "", all_hashes)
        pushed = len(push_files)
        if current_hash:
            print(f"    [GIT] 동기화 상태 기록: {current_hash[:8]} (push {pushed}개 / 해시 {len(all_hashes)}개 재구성)")
        else:
            print(f"    [HASH] 동기화 상태 기록: push {pushed}개 / 해시 {len(all_hashes)}개 재구성")

    return True


def cmd_run_push_only(dry_run: bool = False, allow_delete: bool = False, allow_add: bool = False, force_conflict: bool = False):
    """파일 단위 push 동기화 - 소스 최신 파일만 push, pull 필요 파일은 파일 단위로 건너뜀."""
    print("# ccsync run --push-only\n")
    if dry_run:
        print("[DRY-RUN] 실제 파일 복사 없이 미리보기만 실행\n")
    if allow_delete:
        print("[DELETE] 대상에만 있는 파일 삭제 모드 활성화\n")
    if allow_add:
        print("[ADD] 대상에만 있는 파일 유지 모드 활성화\n")
    if force_conflict:
        print("[FORCE] CONFLICT 파일도 소스로 덮어씀 (양쪽 변경 무시)\n")
    print("파일 단위 push 동기화 (소스 최신 파일만 push, pull 필요 파일은 건너뜀)\n")

    # Collect Full projects
    full_projects = []

    # 1. TARGET_SCAN_DIR (3_code/) 내 프로젝트
    if TARGET_SCAN_DIR.exists():
        for item in sorted(TARGET_SCAN_DIR.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                if item.name == CURRENT_PROJECT.name:
                    continue
                if (item / VIBE_INDICATORS["claude_dir"]).exists():
                    full_projects.append(item)

    # 2. EXTRA_SCAN_PATHS 프로젝트 추가
    for extra_path in EXTRA_SCAN_PATHS:
        if extra_path.exists() and extra_path.is_dir():
            if (extra_path / VIBE_INDICATORS["claude_dir"]).exists():
                full_projects.append(extra_path)

    if not full_projects:
        print("Full 상태의 프로젝트가 없습니다.")
        return

    # 파일 단위 분류
    project_results = []  # (proj, push_files, skip_files, delete_files)

    print("## 프로젝트 검사\n")
    print("| # | Project | Push | Skip(pull필요) | 결과 |")
    print("|---|---------|------|--------------|------|")

    for idx, proj in enumerate(full_projects, 1):
        push_files, skip_files, delete_files = check_push_only(proj, allow_delete=allow_delete, allow_add=allow_add, force_conflict=force_conflict)
        push_count = len(push_files) + len(delete_files)
        skip_count = len(skip_files)

        if push_count == 0 and skip_count == 0:
            result = "동기화 불필요"
        elif push_count > 0:
            result = "동기화 대상"
        else:
            result = "건너뜀 (push없음)"

        print(f"| {idx} | {proj.name} | {push_count} | {skip_count} | {result} |")
        project_results.append((proj, push_files, skip_files, delete_files))

    print()

    # 대상에만 있는 파일(ONLY_TARGET) 삭제 여부 확인
    # --delete: check_push_only가 이미 delete_files로 분류 (질문 생략)
    # --add   : check_push_only가 무시하여 유지 (질문 생략)
    # 둘 다 없으면: 사용자에게 삭제 여부를 물어봄 (기본 N=유지)
    if not dry_run and not allow_delete and not allow_add:
        only_target = []  # (proj, rel_path)
        for proj, pf, sf, df in project_results:
            for rel_path, status in sf:
                if status == "ONLY_TARGET":
                    only_target.append((proj, rel_path))
        if only_target:
            print(f"## 대상에만 있는 파일 ({len(only_target)}개)\n")
            print("소스에 없고 대상 프로젝트에만 존재하는 파일입니다.\n")
            _cur = None
            for proj, rel_path in only_target:
                if proj.name != _cur:
                    print(f"### {proj.name}")
                    _cur = proj.name
                print(f"  - {rel_path}")
            print()
            try:
                answer = input("위 파일들을 대상에서 삭제할까요? (y/N): ").strip().lower()
            except EOFError:
                answer = "n"
            print()
            if answer == "y":
                # ONLY_TARGET 파일을 skip_files → delete_files 로 이동
                project_results = [
                    (
                        proj,
                        pf,
                        [(rp, st) for rp, st in sf if st != "ONLY_TARGET"],
                        df + [rp for rp, st in sf if st == "ONLY_TARGET"],
                    )
                    for proj, pf, sf, df in project_results
                ]
                print(f"[DELETE] 대상 전용 파일 {len(only_target)}개를 삭제합니다.\n")
            else:
                print("[KEEP] 대상 전용 파일을 유지합니다 (삭제 안 함).\n")

    sync_targets = [(proj, pf, sf, df) for proj, pf, sf, df in project_results if len(pf) + len(df) > 0]
    ok_count = sum(1 for _, pf, sf, df in project_results if len(pf) + len(df) == 0 and len(sf) == 0)
    no_push_count = sum(1 for _, pf, sf, df in project_results if len(pf) + len(df) == 0 and len(sf) > 0)

    # CONFLICT 파일 전체 집계 (push 없는 프로젝트 포함)
    all_conflicts = []
    for proj, push_files, skip_files, delete_files in project_results:
        conflict_files = [(rp, st) for rp, st in skip_files if st == "CONFLICT"]
        if conflict_files:
            all_conflicts.append((proj, conflict_files))
    total_conflict_files = sum(len(cf) for _, cf in all_conflicts)

    if not sync_targets and not all_conflicts:
        print("## 결과\n")
        print(f"- OK (동기화 불필요): {ok_count}개")
        print(f"- push없음 (pull만 필요): {no_push_count}개")
        print("\npush할 파일이 없습니다.")
        return

    success_count = 0
    if sync_targets:
        if dry_run:
            print("## 동기화 미리보기\n")
        else:
            print("## 동기화 실행\n")

        for proj, push_files, skip_files, delete_files in sync_targets:
            push_count = len(push_files) + len(delete_files)
            skip_count = len(skip_files)
            non_conflict_skips = [(rp, st) for rp, st in skip_files if st != "CONFLICT"]
            conflict_skips = [(rp, st) for rp, st in skip_files if st == "CONFLICT"]
            if dry_run:
                print(f"- {proj.name} (push: {push_count}개, skip: {skip_count}개):")
                sync_project_files(proj, push_files, delete_files, dry_run=True)
                for rel_path, status in non_conflict_skips[:3]:
                    print(f"    [SKIP] {rel_path} ({status})")
                if len(non_conflict_skips) > 3:
                    print(f"    [SKIP] ... 외 {len(non_conflict_skips) - 3}개")
                for rel_path, _ in conflict_skips:
                    print(f"    [CONFLICT] {rel_path} (push 차단 → merge 필요)")
                success_count += 1
            else:
                print(f"- {proj.name} (push: {push_count}개, skip: {skip_count}개)... ", end="", flush=True)
                if sync_project_files(proj, push_files, delete_files, dry_run=False):
                    print("완료")
                    for rel_path, status in non_conflict_skips[:3]:
                        print(f"    [SKIP] {rel_path} ({status})")
                    if len(non_conflict_skips) > 3:
                        print(f"    [SKIP] ... 외 {len(non_conflict_skips) - 3}개")
                    for rel_path, _ in conflict_skips:
                        print(f"    [CONFLICT] {rel_path} (push 차단 → merge 필요)")
                    success_count += 1
                else:
                    print("실패")

    # CONFLICT 파일: diff 자동 표시 + merge 안내
    if all_conflicts:
        print(f"\n## CONFLICT 파일 ({total_conflict_files}개) - 수동 merge 필요\n")
        print("양쪽 모두 수정된 파일입니다. push가 차단되었습니다.\n")
        for proj, conflict_files in all_conflicts:
            print(f"### {proj.name} ({len(conflict_files)}개 파일)\n")
            for i, (rel_path, _) in enumerate(conflict_files, 1):
                source_file = CURRENT_PROJECT / rel_path
                target_file = proj / rel_path
                diff_data = get_file_diff_data(
                    source_file, target_file,
                    CURRENT_PROJECT.name, proj.name,
                    str(rel_path).replace("\\", "/"), "CONFLICT",
                    i, len(conflict_files)
                )
                print(render_diff_output(diff_data, include_content=True))
            print(f"merge 명령어: `ccsync merge {proj.name} <파일경로>`")
            print(f"내용 비교:    `ccsync diff {proj.name} <파일경로>`\n")

    if dry_run:
        print(f"\n## 미리보기 완료\n")
        if sync_targets:
            print(f"- 동기화 대상: {success_count}/{len(sync_targets)}개")
        print(f"- OK (불필요): {ok_count}개")
        print(f"- push없음 (pull만 필요): {no_push_count}개")
        if total_conflict_files:
            print(f"- CONFLICT (merge 필요): {total_conflict_files}개 파일")
        print("\n[TIP] 실제 동기화: `ccsync run --push-only` (--dry-run 제거)")
    else:
        print(f"\n## 완료\n")
        if sync_targets:
            print(f"- 동기화 성공: {success_count}/{len(sync_targets)}개")
        print(f"- OK (불필요): {ok_count}개")
        print(f"- push없음 (pull만 필요): {no_push_count}개")
        if total_conflict_files:
            print(f"- CONFLICT (merge 필요): {total_conflict_files}개 파일")


def cmd_run(project_name: str | None = None):
    """Run sync comparison with target project."""
    print("# ccsync run - 동기화 실행\n")

    if not project_name:
        print("사용법: `ccsync run [project_name]`\n")
        print("프로젝트명 또는 4자리 번호 입력 가능 (예: 0003 또는 0003_CCone)\n")
        print("`ccsync list`로 프로젝트 목록을 먼저 확인하세요.")
        return

    target_project = find_project_by_name(project_name)
    if not target_project:
        print(f"오류: 프로젝트 '{project_name}'를 찾을 수 없습니다.")
        print("4자리 번호 또는 전체 프로젝트명을 입력하세요.")
        return

    print(f"## 비교 대상\n")
    print(f"- 소스 (현재): `{CURRENT_PROJECT.name}`")
    print(f"- 대상: `{target_project.name}`\n")

    # Collect all files to compare
    all_files = set()
    for target in SYNC_TARGETS:
        source_files = collect_files(CURRENT_PROJECT, target.rstrip("/"))
        target_files = collect_files(target_project, target.rstrip("/"))
        all_files.update(source_files)
        all_files.update(target_files)

    # Compare files
    comparison_results = []
    _sync_state_irun = load_sync_state(target_project.name)
    _file_hashes_irun = _sync_state_irun.get("file_hashes", {})
    for rel_path in sorted(all_files):
        source_path = CURRENT_PROJECT / rel_path
        target_path = target_project / rel_path

        last_hash = _file_hashes_irun.get(str(rel_path).replace("\\", "/"), "")
        status = compare_files(source_path, target_path, last_hash)
        if status != "SAME":  # Only show differences
            comparison_results.append({
                "path": str(rel_path),
                "status": status,
                "symbol": get_status_symbol(status),
                "source_mtime": get_file_mtime(source_path),
                "target_mtime": get_file_mtime(target_path),
            })

    print("## 비교 결과\n")

    if not comparison_results:
        print("모든 파일이 동일합니다. 동기화가 필요하지 않습니다.")
        return

    print("| 상태 | 파일 | 소스 수정일 | 대상 수정일 |")
    print("|------|------|------------|------------|")

    for result in comparison_results:
        source_dt = result["source_mtime"].strftime("%Y-%m-%d %H:%M") if result["source_mtime"] else "-"
        target_dt = result["target_mtime"].strftime("%Y-%m-%d %H:%M") if result["target_mtime"] else "-"
        print(f"| {result['symbol']} | `{result['path']}` | {source_dt} | {target_dt} |")

    print(f"\n총 {len(comparison_results)}개 파일 차이 발견\n")

    # Summary by status
    print("## 상태별 요약\n")
    status_counts = {}
    for result in comparison_results:
        status = result["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    print("| 상태 | 설명 | 개수 | 권장 액션 |")
    print("|------|------|------|----------|")

    status_info = {
        "ONLY_SOURCE": ("→", "대상에 없음 → 복사 필요", "push"),
        "ONLY_TARGET": ("←", "현재에 없음 ← 가져오기", "pull"),
        "NEWER_SOURCE": (">>", "현재가 최신 → 덮어쓰기", "push"),
        "NEWER_TARGET": ("<<", "대상이 최신 ← 가져오기", "pull"),
        "CONFLICT":    ("!!", "양쪽 모두 변경됨 → 수동 merge 필요", "merge"),
    }

    for status, count in status_counts.items():
        if status in status_info:
            symbol, desc, action = status_info[status]
            print(f"| {symbol} | {desc} | {count} | {action} |")


def get_file_diff_data(source_file: Path, target_file: Path, source_project_name: str,
                       target_project_name: str, rel_path: str, status: str,
                       current_index: int, total_count: int) -> dict:
    """단일 파일의 diff 데이터 생성"""
    import difflib

    source_mtime = get_file_mtime(source_file)
    target_mtime = get_file_mtime(target_file)
    source_dt = source_mtime.strftime("%Y-%m-%d %H:%M") if source_mtime else "-"
    target_dt = target_mtime.strftime("%Y-%m-%d %H:%M") if target_mtime else "-"

    symbol, desc = DIFF_STATUS_DESC.get(status, ("?", "알 수 없음"))

    # 파일 내용 및 diff 생성
    diff_content = ""
    added = 0
    removed = 0
    line_count = 0

    if status == "ONLY_SOURCE":
        # 소스에만 존재
        try:
            content = source_file.read_text(encoding='utf-8')
            line_count = len(content.splitlines())
            diff_content = content[:2000] + ("..." if len(content) > 2000 else "")
        except (UnicodeDecodeError, Exception):
            diff_content = "(바이너리 파일 또는 읽기 오류)"
    elif status == "ONLY_TARGET":
        # 대상에만 존재
        try:
            content = target_file.read_text(encoding='utf-8')
            line_count = len(content.splitlines())
            diff_content = content[:2000] + ("..." if len(content) > 2000 else "")
        except (UnicodeDecodeError, Exception):
            diff_content = "(바이너리 파일 또는 읽기 오류)"
    else:
        # 양쪽 모두 존재 - unified diff 생성
        try:
            source_lines = source_file.read_text(encoding='utf-8').splitlines(keepends=True)
            target_lines = target_file.read_text(encoding='utf-8').splitlines(keepends=True)

            diff = difflib.unified_diff(
                target_lines,
                source_lines,
                fromfile=f"[대상] {target_project_name}/{rel_path}",
                tofile=f"[소스] {source_project_name}/{rel_path}",
                lineterm=""
            )
            diff_output = list(diff)

            if diff_output:
                # 추가/삭제 줄 수 계산
                added = sum(1 for line in diff_output if line.startswith('+') and not line.startswith('+++'))
                removed = sum(1 for line in diff_output if line.startswith('-') and not line.startswith('---'))
                # diff 내용 (최대 50줄)
                diff_content = "\n".join(diff_output[:50])
                if len(diff_output) > 50:
                    diff_content += f"\n... (+{len(diff_output) - 50}줄 더)"
        except (UnicodeDecodeError, Exception):
            diff_content = "(바이너리 파일 또는 읽기 오류)"

    change_summary = generate_change_summary(status, added, removed, line_count)

    return {
        "current_index": current_index,
        "total_count": total_count,
        "file_path": rel_path,
        "source_project": source_project_name,
        "target_project": target_project_name,
        "source_mtime": source_dt,
        "target_mtime": target_dt,
        "status": status,
        "status_symbol": symbol,
        "status_desc": desc,
        "change_summary": change_summary,
        "diff_content": diff_content,
        "added": added,
        "removed": removed,
    }


def cmd_diff(project_name: str | None, filename: str | None):
    """Show visual diff between files in current and target project."""
    if not project_name:
        print("# ccsync diff - 파일 비교\n")
        print("사용법: `ccsync diff [project] [filename]`\n")
        print("- filename 생략 시: 모든 차이 파일을 순서대로 표시")
        print("- filename 지정 시: 해당 파일만 비교\n")
        print("`ccsync list`로 프로젝트 목록을 먼저 확인하세요.")
        return

    # Find target project
    target_project = find_project_by_name(project_name)
    if not target_project:
        print(f"오류: 프로젝트 '{project_name}'를 찾을 수 없습니다.")
        return

    # 특정 파일만 비교하는 경우
    if filename:
        filename = filename.replace("\\", "/")
        source_file = CURRENT_PROJECT / filename
        target_file = target_project / filename

        # 파일 상태 확인
        if not source_file.exists() and not target_file.exists():
            print("오류: 양쪽 모두 파일이 존재하지 않습니다.")
            return

        if source_file.exists() and not target_file.exists():
            status = "ONLY_SOURCE"
        elif not source_file.exists() and target_file.exists():
            status = "ONLY_TARGET"
        else:
            source_mtime = get_file_mtime(source_file)
            target_mtime = get_file_mtime(target_file)
            if source_mtime and target_mtime:
                status = "NEWER_SOURCE" if source_mtime > target_mtime else "NEWER_TARGET"
            else:
                status = "NEWER_SOURCE"

        diff_data = get_file_diff_data(
            source_file, target_file,
            CURRENT_PROJECT.name, target_project.name,
            filename, status, 1, 1
        )
        output = render_diff_output(diff_data, include_content=True)
        print(output)
        return

    # 파일명 미지정 - 모든 차이 파일 표시
    # Collect all files to compare
    all_files = set()
    for target in SYNC_TARGETS:
        source_files = collect_files(CURRENT_PROJECT, target.rstrip("/"))
        target_files = collect_files(target_project, target.rstrip("/"))
        all_files.update(source_files)
        all_files.update(target_files)

    # Compare files and collect differences
    comparison_results = []
    _sync_state_diff = load_sync_state(target_project.name)
    _file_hashes_diff = _sync_state_diff.get("file_hashes", {})
    for rel_path in sorted(all_files):
        source_path = CURRENT_PROJECT / rel_path
        target_path = target_project / rel_path

        last_hash = _file_hashes_diff.get(str(rel_path).replace("\\", "/"), "")
        status = compare_files(source_path, target_path, last_hash)
        if status != "SAME":
            comparison_results.append({
                "path": str(rel_path),
                "status": status,
                "source_path": source_path,
                "target_path": target_path,
            })

    if not comparison_results:
        print("# ccsync diff - 파일 비교\n")
        print("모든 파일이 동일합니다. 비교할 차이점이 없습니다.")
        return

    # 전체 헤더 출력
    print(TEMPLATE_DIFF_ALL_HEADER.format(
        source_project=CURRENT_PROJECT.name,
        target_project=target_project.name,
        total_count=len(comparison_results)
    ))

    # 각 파일별 diff 출력
    total_count = len(comparison_results)
    for idx, result in enumerate(comparison_results, 1):
        diff_data = get_file_diff_data(
            result["source_path"],
            result["target_path"],
            CURRENT_PROJECT.name,
            target_project.name,
            result["path"],
            result["status"],
            idx,
            total_count
        )
        output = render_diff_output(diff_data, include_content=True)
        print(output)


def cmd_merge(project_name: str | None, filename: str | None, direction: str = "auto"):
    """Merge files between current and target project."""
    if not project_name:
        print("# ccsync merge - 파일 병합\n")
        print("사용법: `ccsync merge [project] [filename]`\n")
        print("옵션:")
        print("  --pull  : 대상 → 현재 (target → source)")
        print("  --push  : 현재 → 대상 (source → target)")
        print("  (기본값: 최신 버전 방향으로 자동 결정)\n")
        print("`ccsync list`로 프로젝트 목록을 먼저 확인하세요.")
        return

    target_project = find_project_by_name(project_name)
    if not target_project:
        print(f"오류: 프로젝트 '{project_name}'를 찾을 수 없습니다.")
        return

    dir_label = {
        "auto": "자동 (최신 우선)",
        "pull": "← pull (대상→현재)",
        "push": "→ push (현재→대상)",
    }.get(direction, direction)

    print("# ccsync merge - 파일 병합\n")
    print("| 항목 | 값 |")
    print("|------|-----|")
    print(f"| 소스 (현재) | `{CURRENT_PROJECT.name}` |")
    print(f"| 대상 | `{target_project.name}` |")
    print(f"| 방향 | {dir_label} |")
    print()

    if filename:
        filename = filename.replace("\\", "/")
        files_to_process = [filename]
    else:
        all_files: set = set()
        for target in SYNC_TARGETS:
            all_files.update(collect_files(CURRENT_PROJECT, target.rstrip("/")))
            all_files.update(collect_files(target_project, target.rstrip("/")))
        files_to_process = [str(f) for f in sorted(all_files)]

    merged = []
    skipped = []
    errors = []

    _sync_state_merge = load_sync_state(target_project.name)
    _file_hashes_merge = _sync_state_merge.get("file_hashes", {})
    for rel_path in files_to_process:
        source_file = CURRENT_PROJECT / rel_path
        target_file = target_project / rel_path

        last_hash = _file_hashes_merge.get(str(rel_path).replace("\\", "/"), "")
        status = compare_files(source_file, target_file, last_hash)
        if status == "SAME":
            continue

        if direction == "pull":
            if not target_file.exists():
                skipped.append((rel_path, "대상 없음 (pull 불가)"))
                continue
            src, dst = target_file, source_file
            arrow = "← pull"
        elif direction == "push":
            if not source_file.exists():
                skipped.append((rel_path, "소스 없음 (push 불가)"))
                continue
            src, dst = source_file, target_file
            arrow = "→ push"
        else:  # auto
            if status in ("NEWER_TARGET", "ONLY_TARGET"):
                src, dst = target_file, source_file
                arrow = "← pull (대상이 최신)"
            elif status in ("NEWER_SOURCE", "ONLY_SOURCE"):
                src, dst = source_file, target_file
                arrow = "→ push (현재가 최신)"
            elif status == "CONFLICT":
                # CONFLICT: --push/--pull 없으면 소스 우선 (push)
                src, dst = source_file, target_file
                arrow = "→ push (CONFLICT: 소스 우선)"
            else:
                skipped.append((rel_path, f"알 수 없는 상태: {status}"))
                continue

        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src), str(dst))
            merged.append((rel_path, arrow))
        except Exception as e:
            errors.append((rel_path, str(e)))

    print("## 결과\n")
    if merged:
        print("| 파일 | 방향 |")
        print("|------|------|")
        for path, arrow in merged:
            print(f"| `{path}` | {arrow} |")
        print()

    print(f"- 병합: {len(merged)}개")
    if skipped:
        print(f"- 건너뜀: {len(skipped)}개")
        for path, reason in skipped:
            print(f"  [SKIP] {path}: {reason}")
    if errors:
        print(f"- 오류: {len(errors)}개")
        for path, err in errors:
            print(f"  [ERROR] {path}: {err}")


def cmd_backup():
    """Codex 환경 파일을 zip으로 백업."""
    import zipfile

    now = datetime.now().strftime("%y%m%d-%H%M%S")
    backup_dir = CURRENT_PROJECT / "data" / "04_claude_backup"
    backup_dir.mkdir(parents=True, exist_ok=True)
    zip_path = backup_dir / f"{now}.zip"

    targets = [
        ".codex/",
        "00_doc/tutorial/",
        "CLAUDE.md",
        "GEMINI.md",
        ".mcp.json",
        ".omc/project-memory.json",
        "pyproject.toml",
        "cclaude.bat",
        "cclaude.sh",
        "oclaude.bat",
        "ccodex.bat",
        "gemma.ps1",
        "gemma.sh",
        ".github/",
        ".agents/",
        "AGENTS.md",
    ]
    # HOME 기준 글로벌 파일 (~ 접두사): zip 내 _home/ 아래 저장
    home_targets = [
        "~/.codex/.omc/hud-config.json",
    ]
    exclude_dirs = {"__pycache__", "data", "00_data", "sessions", ".git"}

    count = 0
    with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as zf:
        for t in targets:
            full = CURRENT_PROJECT / t
            if full.is_file():
                zf.write(str(full), t)
                count += 1
            elif full.is_dir():
                for dirpath, dirnames, filenames in os.walk(str(full)):
                    # prune: 제외 디렉토리에 진입하지 않음
                    dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
                    for f in filenames:
                        if f.endswith(".pyc"):
                            continue
                        fp = os.path.join(dirpath, f)
                        arcname = os.path.relpath(fp, str(CURRENT_PROJECT))
                        zf.write(fp, arcname)
                        count += 1
        # HOME 기준 글로벌 파일 처리
        home = Path.home()
        for ht in home_targets:
            rel = ht[2:]  # ~/ 제거
            full = home / rel
            arcname = "_home/" + rel.replace("\\", "/")
            if full.is_file():
                zf.write(str(full), arcname)
                count += 1

    size_mb = zip_path.stat().st_size / 1024 / 1024
    print(f"[ccsync backup]")
    print(f"  출력: {zip_path.relative_to(CURRENT_PROJECT)}")
    print(f"  파일: {count}개")
    print(f"  크기: {size_mb:.1f}MB")


def cmd_reset(args: list):
    """소스/대상 프로젝트 동기화 설정을 초기화합니다."""
    config_path = SCRIPT_DIR.parent / "references" / "sync_config.json"

    # 기존 설정 로드
    config = {}
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    # 인수 없음 → 현재 설정 표시
    if not args or args == ["--show"]:
        print("[ccsync reset] 현재 설정\n")
        print(f"소스 폴더: {CURRENT_PROJECT}")
        targets = config.get("targets", [])
        if targets:
            print(f"\n대상 프로젝트 ({len(targets)}개):")
            for t in targets:
                p = Path(t["path"])
                status = "존재" if p.exists() else "없음"
                print(f"  [{status}] {t['path']}")
        else:
            print("\n대상 프로젝트: 없음 (기본 스캔 경로 사용)")
        print("\n사용법:")
        print("  ccsync reset --targets /path1 /path2  # 대상 설정 (하나 이상)")
        print("  ccsync reset --add /path              # 대상 추가")
        print("  ccsync reset --remove /path           # 대상 제거")
        print("  ccsync reset --clear                  # 대상 전체 제거")
        return

    if "--targets" in args:
        idx = args.index("--targets")
        new_paths = [a for a in args[idx + 1:] if not a.startswith("--")]
        if not new_paths:
            print("[ERROR] --targets 뒤에 경로를 하나 이상 입력하세요.")
            return
        target_list = [{"path": str(Path(p)), "name": Path(p).name} for p in new_paths]
        config = {
            "source": str(CURRENT_PROJECT),
            "targets": target_list,
            "updated": datetime.now().isoformat(),
        }
        config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[OK] 설정 저장: {config_path.name}\n")
        print(f"소스: {CURRENT_PROJECT}")
        print(f"대상 ({len(target_list)}개):")
        for t in target_list:
            exists = "존재" if Path(t["path"]).exists() else "없음"
            print(f"  [{exists}] {t['path']}")

    elif "--add" in args:
        idx = args.index("--add")
        if idx + 1 >= len(args):
            print("[ERROR] --add 뒤에 경로를 입력하세요.")
            return
        add_path = str(Path(args[idx + 1]))
        targets = config.get("targets", [])
        if any(t["path"] == add_path for t in targets):
            print(f"[INFO] 이미 등록됨: {add_path}")
            return
        targets.append({"path": add_path, "name": Path(add_path).name})
        config["targets"] = targets
        config["source"] = str(CURRENT_PROJECT)
        config["updated"] = datetime.now().isoformat()
        config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[OK] 대상 추가: {add_path}")
        print(f"현재 대상: {len(targets)}개")

    elif "--remove" in args:
        idx = args.index("--remove")
        if idx + 1 >= len(args):
            print("[ERROR] --remove 뒤에 경로를 입력하세요.")
            return
        remove_path = str(Path(args[idx + 1]))
        targets = config.get("targets", [])
        before = len(targets)
        targets = [t for t in targets if t["path"] != remove_path]
        if len(targets) == before:
            print(f"[WARN] 해당 경로 없음: {remove_path}")
            return
        config["targets"] = targets
        config["updated"] = datetime.now().isoformat()
        config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[OK] 대상 제거: {remove_path}")
        print(f"남은 대상: {len(targets)}개")

    elif "--clear" in args:
        config["targets"] = []
        config["updated"] = datetime.now().isoformat()
        config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
        print("[OK] 대상 전체 제거 완료")

    else:
        print(f"[ERROR] 알 수 없는 옵션: {args}")
        print("사용법: ccsync reset [--targets /path1 /path2 | --add /path | --remove /path | --clear]")


def cmd_restore(backup_name=None):
    """백업 zip에서 복원."""
    import zipfile

    backup_dir = CURRENT_PROJECT / "data" / "04_claude_backup"
    if not backup_dir.exists():
        print("[ERROR] 백업 디렉토리 없음: data/04_claude_backup/")
        return

    # 백업 목록 조회
    backups = sorted(backup_dir.glob("*.zip"), reverse=True)
    if not backups:
        print("[ERROR] 백업 파일 없음")
        return

    if backup_name:
        # 이름으로 검색
        matched = [b for b in backups if backup_name in b.stem]
        if not matched:
            print(f"[ERROR] '{backup_name}' 매칭 백업 없음")
            return
        zip_path = matched[0]
    else:
        # 목록 표시
        print("[ccsync restore] 백업 목록\n")
        print("| # | 파일명 | 크기 |")
        print("|---|--------|------|")
        for i, b in enumerate(backups[:10], 1):
            size_mb = b.stat().st_size / 1024 / 1024
            print(f"| {i} | {b.name} | {size_mb:.1f}MB |")
        if len(backups) > 10:
            print(f"\n... 외 {len(backups) - 10}개")
        print(f"\n사용법: ccsync restore <파일명 또는 번호>")
        print(f"예: ccsync restore {backups[0].stem}")
        return

    # 복원 실행
    print(f"[ccsync restore]")
    print(f"  소스: {zip_path.name}")

    count = 0
    with zipfile.ZipFile(str(zip_path), "r") as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            target = CURRENT_PROJECT / info.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, open(str(target), "wb") as dst:
                dst.write(src.read())
            count += 1

    print(f"  복원: {count}개 파일")
    print(f"  대상: {CURRENT_PROJECT}")


def cmd_show_checklist():
    """references/checklist.md 내용 출력"""
    checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[{SKILL_NAME}] checklist.md 없음: {checklist_path}")
        return
    print(checklist_path.read_text(encoding="utf-8"))


def _scan_full_projects() -> list[Path]:
    """Full 상태 (vibe 환경 설치된) 프로젝트 목록 반환."""
    full_projects = []
    if TARGET_SCAN_DIR.exists():
        for item in sorted(TARGET_SCAN_DIR.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                if item.name == CURRENT_PROJECT.name:
                    continue
                if (item / VIBE_INDICATORS["claude_dir"]).exists():
                    full_projects.append(item)
    for extra_path in EXTRA_SCAN_PATHS:
        if extra_path.exists() and extra_path.is_dir():
            if (extra_path / VIBE_INDICATORS["claude_dir"]).exists():
                full_projects.append(extra_path)
    return full_projects


def _resolve_project(name: str) -> Path | None:
    """이름 또는 4자리 번호로 프로젝트 경로 해석."""
    for tp in _scan_full_projects():
        if tp.name == name or tp.name.startswith(f"{name}_") or tp.name == f"{name}":
            return tp
    return None


def cmd_repair(project_name: str | None = None, dry_run: bool = False):
    """file_hashes 재구성 (stale state 정리).

    동기화 작업 없이 ``last_hash`` 메타데이터만 현재 target 상태로 재구성한다.
    재구성 후 다음 비교 시점부터:
      - source 변경만 있으면 NEWER_SOURCE
      - target 변경만 있으면 NEWER_TARGET
      - 양쪽 모두 변경되면 CONFLICT (정확한 양쪽 변경 추적)

    사용 시점:
      - 동기화 직전 양쪽 상태가 어긋났을 때
      - sync_project_files 가 변경되기 전 기록된 stale state 정리
      - 이전 동기화 메타가 손실되어 모든 변경 파일이 CONFLICT 로 표시될 때
    """
    print("# ccsync repair - file_hashes 재구성\n")
    if dry_run:
        print("[DRY-RUN] 실제 메타 갱신 없이 영향만 표시\n")

    targets: list[Path] = []
    if project_name:
        tp = _resolve_project(project_name)
        if not tp:
            print(f"[ERROR] 프로젝트를 찾을 수 없습니다: {project_name}")
            return 1
        targets = [tp]
    else:
        targets = _scan_full_projects()

    if not targets:
        print("[INFO] Full 상태의 프로젝트가 없습니다.")
        return 0

    print(f"대상: {len(targets)}개 프로젝트\n")

    for tp in targets:
        all_hashes = {}
        for sync_target in SYNC_TARGETS:
            stp = tp / sync_target.rstrip("/")
            if stp.exists():
                if stp.is_file():
                    all_hashes[sync_target.rstrip("/")] = get_file_hash(stp)
                else:
                    for f in stp.rglob("*"):
                        if f.is_file() and not is_excluded(f):
                            rel = str(f.relative_to(tp)).replace("\\", "/")
                            all_hashes[rel] = get_file_hash(f)

        if dry_run:
            print(f"  [DRY-RUN] {tp.name}: {len(all_hashes)}개 파일 해시 재구성 예정")
        else:
            existing = load_sync_state(tp.name)
            commit = existing.get("commit_hash", "")
            save_sync_state(tp.name, commit, all_hashes)
            print(f"  [OK] {tp.name}: {len(all_hashes)}개 파일 해시 재구성 (commit={commit[:8] if commit else 'none'})")

    print("\n## 완료")
    print(f"- 처리: {len(targets)}개 프로젝트")
    if not dry_run:
        print(f"- 다음 `ccsync view` / `ccsync run` 부터 정확한 분류가 적용됩니다.")
    return 0


def main():
    """Main entry point."""
    # 서브명령어 없이 실행 시 도움말 출력
    if not sys.argv[1:]:
        sys.argv.append("run")

    if len(sys.argv) < 2:
        cmd_status()
        return

    # help 분기 (subcommand 처리 전)
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("help", "-h", "--help"):
        _print_skill_help("ccsync")
        sys.exit(0)

    subcommand = sys.argv[1].lower()

    if subcommand == "status":
        cmd_status()
    elif subcommand == "list":
        cmd_list()
    elif subcommand == "files":
        cmd_files()
    elif subcommand == "view":
        project_name = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_view(project_name)
    elif subcommand == "run":
        # Argument parsing: project_name 은 -- 로 시작하지 않는 첫 번째 양수 인자
        positional = [a for a in sys.argv[2:] if not a.startswith("--")]
        project_name = positional[0] if positional else None
        dry_run = "--dry-run" in sys.argv
        allow_delete = "--delete" in sys.argv
        allow_add = "--add" in sys.argv
        force_conflict = "--force" in sys.argv

        # 라우팅 규칙:
        # - `ccsync run` (인자 없음) → 모든 Full 프로젝트에 일괄 push (push-only 기본값)
        # - `ccsync run --push-only [...]` → 명시적 일괄 push (옵션 통과)
        # - `ccsync run <project>` → 특정 프로젝트 비교/동기화
        if "--push-only" in sys.argv or project_name is None:
            cmd_run_push_only(
                dry_run=dry_run,
                allow_delete=allow_delete,
                allow_add=allow_add,
                force_conflict=force_conflict,
            )
        else:
            cmd_run(project_name)
    elif subcommand == "diff":
        project_name = sys.argv[2] if len(sys.argv) > 2 else None
        filename = sys.argv[3] if len(sys.argv) > 3 else None
        cmd_diff(project_name, filename)
    elif subcommand == "merge":
        project_name = sys.argv[2] if len(sys.argv) > 2 else None
        filename = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else None
        direction = "pull" if "--pull" in sys.argv else ("push" if "--push" in sys.argv else "auto")
        cmd_merge(project_name, filename, direction)
    elif subcommand == "reset":
        reset_args = sys.argv[2:]
        cmd_reset(list(reset_args))
    elif subcommand == "backup":
        cmd_backup()
    elif subcommand == "restore":
        backup_name = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_restore(backup_name)
    elif subcommand == "pipeline":
        import subprocess
        pipeline_script = SCRIPT_DIR / "oosync_pipeline.py"
        if not pipeline_script.exists():
            print("[ERROR] pipeline 스크립트 없음: oosync_pipeline.py")
            return
        args = sys.argv[2:]
        subprocess.run(
            ["uv", "run", "python", str(pipeline_script)] + args,
            cwd=str(CURRENT_PROJECT)
        )
    elif subcommand == "repair":
        # ccsync repair [project] [--dry-run]
        project_name = None
        dry_run = "--dry-run" in sys.argv
        for arg in sys.argv[2:]:
            if not arg.startswith("--"):
                project_name = arg
                break
        sys.exit(cmd_repair(project_name=project_name, dry_run=dry_run) or 0)
    elif subcommand == "show" and len(sys.argv) > 2 and sys.argv[2].lower() == "checklist":
        cmd_show_checklist()
    else:
        print(f"알 수 없는 명령어: {subcommand}")
        print("'ccsync status'로 사용 가능한 명령어를 확인하세요.")


if __name__ == "__main__":
    main()
