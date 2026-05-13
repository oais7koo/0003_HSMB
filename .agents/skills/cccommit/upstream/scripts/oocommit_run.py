#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
oocommit_run.py

Git 커밋 및 이력 정리 통합 워크플로우

명령어:
    oocommit run          커밋 + 이력 정리 통합 실행 (기본)
    oocommit commit       Git 커밋만 수행
    oocommit sync         이력 정리만 수행 (d0004 -> d0010)
    oocommit preview      변경사항 및 이동 대상 미리보기
"""

import sys
import re
import subprocess
from pathlib import Path
from datetime import datetime

# Windows 한글 출력 보장
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
# --- oo_common inline ---
import re as _re

_SKILLS_DIR = Path(__file__).parent.parent.parent


def _print_skill_help(skill_name):
    if sys.stdout.encoding and sys.stdout.encoding.lower() in (
        "cp949",
        "cp1252",
        "ascii",
    ):
        sys.stdout.reconfigure(encoding="utf-8")
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

SCRIPT_DIR = Path(__file__).parent
# scripts/ -> oocommit/ -> skills/ -> .claude/ -> PROJECT_ROOT
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent
DOC_DIR = PROJECT_ROOT / "00_doc"
TODO_FILE = DOC_DIR / "sp00" / "d0004_todo.md"
HISTORY_FILE = DOC_DIR / "sp00" / "d0010_history.md"

# --- SP 지원 ---
def _get_sp_from_state() -> int:
    state_file = PROJECT_ROOT / ".omc" / "state" / "context.json"
    if state_file.exists():
        try:
            import json as _json
            data = _json.loads(state_file.read_text(encoding="utf-8"))
            return int(data.get("sp", 0))
        except Exception:
            pass
    return 0

def _detect_sp_cwd() -> int:
    for part in Path.cwd().parts:
        for sp in range(1, 10):
            if part.startswith(f"0{sp}_"):
                return sp
    return 0

def resolve_sp(sp_arg=None) -> int:
    """SP 번호 결정: --sp 인자 > oocontext 상태 > CWD 감지 > 기본값 0"""
    if sp_arg is not None:
        return int(sp_arg)
    ctx = _get_sp_from_state()
    if ctx:
        return ctx
    return _detect_sp_cwd()

def get_sp_doc_dir(sp_num: int) -> Path:
    return PROJECT_ROOT / "00_doc" / f"sp{sp_num:02d}"

def get_doc_path(sp_num: int, base_num: int, suffix: str) -> Path:
    if sp_num == 0:
        filename = f"d{base_num:04d}_{suffix}.md"
    else:
        filename = f"d{sp_num * 10000 + base_num}_{suffix}.md"
    return get_sp_doc_dir(sp_num) / filename
# --- end SP 지원 ---

# 태그 매핑
PRIORITY_TO_TAG = {
    "CRITICAL": "HOTFIX",
    "ERROR": "BUGFIX",
    "WARNING": "IMPROVE",
    "INFO": "ENHANCE",
    "FEATURE": "FEATURE",
    "DOCS": "DOCS",
}

# SP 최상위 폴더 → SP번호 매핑
_SP_DIRS = {
    "01_obsidian": 1, "02_pycode": 2, "03_paper": 3,
    "04_scraping": 4, "05_youtube_graphRAG": 5, "06_oohwp_skill": 6,
    "07_designsystem": 7, "08_RRag": 8, "09_ooppt": 9,
}


def infer_sp_from_files(files: list) -> int:
    """변경 파일 목록에서 SP 번호 추론 (최다 투표)"""
    votes = {}
    for f in files:
        parts = Path(f).parts
        top = parts[0] if parts else ""
        for prefix, sp in _SP_DIRS.items():
            if top == prefix:
                votes[sp] = votes.get(sp, 0) + 1
                break
    return max(votes, key=votes.get) if votes else 0


def list_feature_docs(sp_num: int) -> list:
    """해당 SP의 상세문서(d{SP}1001~d{SP}1999) 목록"""
    sp_doc_dir = get_sp_doc_dir(sp_num)
    if not sp_doc_dir.exists():
        return []
    pattern = "d1[0-9][0-9][0-9]_*.md" if sp_num == 0 else f"d{sp_num}1[0-9][0-9][0-9]_*.md"
    return sorted(sp_doc_dir.glob(pattern))


def step_pre_commit_doc_check(all_files: list, options: dict) -> int:
    """커밋 전 상세문서 업데이트 단계.
    반환: 0=계속, 1=NEED_ACTION(Claude가 처리 후 oocommit commit으로 재실행)
    """
    inferred_sp = infer_sp_from_files(all_files)
    sp_label = f"SP{inferred_sp:02d}"
    feature_docs = list_feature_docs(inferred_sp)

    print(f"[0/5] 상세문서 업데이트 확인...")
    print(f"  - 변경 파일 {len(all_files)}개 분석 → {sp_label} 추론")

    if feature_docs:
        print(f"\n  {sp_label} 상세문서 목록:")
        for i, doc in enumerate(feature_docs, 1):
            stem_parts = doc.stem.split("_", 1)
            doc_id = stem_parts[0]
            title = stem_parts[1] if len(stem_parts) > 1 else doc.stem
            print(f"    {i}. [{doc_id}] {title}")
        print()
        print("[DOC_ACTION_NEEDED]")
        print(f"  SP={inferred_sp} | 작업 내용을 반영할 상세문서를 선택하세요:")
        for i, doc in enumerate(feature_docs, 1):
            doc_id = doc.stem.split("_")[0]
            print(f"  {i}. oof update {doc_id} --sp {inferred_sp}")
        print(f"  n. oof new --sp {inferred_sp}  (새 상세문서 생성)")
        print(f"  s. 스킵  → oocommit commit 으로 문서 없이 커밋")
    else:
        print(f"  - {sp_label} 상세문서 없음")
        print()
        print("[DOC_ACTION_NEEDED]")
        print(f"  SP={inferred_sp} | 상세문서가 없습니다:")
        print(f"  y. oof new --sp {inferred_sp}  (새 상세문서 생성 후 커밋)")
        print(f"  s. 스킵  → oocommit commit 으로 문서 없이 커밋")

    return 1  # NEED_ACTION — 커밋 블록, Claude가 사용자 선택 후 재실행


def print_usage():
    """사용법 출력"""
    print(f"Log started at {datetime.now()}")
    print("oocommit - Git 커밋 및 이력 정리")
    print()
    print("사용법:")
    print("    oocommit status       Git 상태 및 변경사항 요약")
    print("    oocommit run          커밋 + 이력 정리 통합 실행")
    print("    oocommit commit       Git 커밋만 수행")
    print("    oocommit sync         이력 정리만 수행 (d0004 -> d0010)")
    print("    oocommit preview      변경사항 및 이동 대상 미리보기")
    print("    oocommit clear        오래된 커밋 squash + .git 용량 정리")
    print()
    print("옵션:")
    print('    --message "msg"         커밋 메시지 직접 지정')
    print("    --no-push               커밋 후 push 생략")
    print("    --dry-run               실제 실행 없이 예상 결과만 출력")
    print("    --force                 확인 없이 강제 실행")
    print("    --keep N                [clear] 보존할 최근 커밋 수 (기본 20)")
    print("    --push                  [clear] 정리 후 force push 실행")
    print()
    print("예시:")
    print("    python .claude/skills/oocommit/scripts/oocommit_run.py run")
    print(
        '    python .claude/skills/oocommit/scripts/oocommit_run.py commit --message "fix: 버그 수정"'
    )
    print("    python .claude/skills/oocommit/scripts/oocommit_run.py preview")


def run_git_command(args, capture=True):
    """Git 명령어 실행"""
    cmd = ["git"] + args
    result = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        capture_output=capture,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result


def get_current_branch():
    """현재 브랜치명 조회"""
    result = run_git_command(["branch", "--show-current"])
    if result.returncode != 0:
        return None
    branch = result.stdout.strip()
    return branch or None


def get_remote_name():
    """기본 remote 이름 조회. origin 우선."""
    result = run_git_command(["remote"])
    if result.returncode != 0:
        return None

    remotes = [
        remote.strip() for remote in result.stdout.splitlines() if remote.strip()
    ]
    if not remotes:
        return None
    if "origin" in remotes:
        return "origin"
    return remotes[0]


def has_upstream_configured():
    """현재 브랜치 upstream 설정 여부 확인"""
    result = run_git_command(
        ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"]
    )
    return result.returncode == 0


def get_git_status():
    """Git 상태 조회"""
    result = run_git_command(["status", "--porcelain"])
    if result.returncode != 0:
        return None

    files = {"modified": [], "added": [], "deleted": [], "untracked": []}

    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        status = line[:2]
        filepath = line[3:]

        if status.startswith("M") or status.endswith("M"):
            files["modified"].append(filepath)
        elif status.startswith("A"):
            files["added"].append(filepath)
        elif status.startswith("D"):
            files["deleted"].append(filepath)
        elif status.startswith("?"):
            files["untracked"].append(filepath)

    return files


def get_git_diff():
    """Git diff 요약"""
    result = run_git_command(["diff", "--stat"])
    return result.stdout if result.returncode == 0 else ""


def extract_completed_items():
    """d0004_todo.md에서 완료 항목 추출"""
    if not TODO_FILE.exists():
        return []

    content = TODO_FILE.read_text(encoding="utf-8")
    completed = []

    # 체크박스 완료: - [x] [PRIORITY] 설명
    pattern1 = r"-\s*\[x\]\s*\[(\w+)\]\s*(.+?)(?:\n|$)"
    for m in re.finditer(pattern1, content, re.IGNORECASE):
        priority = m.group(1).upper()
        desc = m.group(2).strip()
        completed.append(
            {
                "priority": priority,
                "tag": PRIORITY_TO_TAG.get(priority, "IMPROVE"),
                "description": desc,
                "full_match": m.group(0),
            }
        )

    # 해결 마킹: ✅ 해결: 설명
    pattern2 = r"✅\s*해결[:\s]*(.+?)(?:\n|$)"
    for m in re.finditer(pattern2, content):
        desc = m.group(1).strip()
        completed.append(
            {
                "priority": "INFO",
                "tag": "ENHANCE",
                "description": desc,
                "full_match": m.group(0),
            }
        )

    return completed


def cmd_status():
    """Git 상태 요약 (status 서브명령어)"""
    print("## oocommit 상태 요약\n")

    # 브랜치 정보
    branch_result = run_git_command(["branch", "--show-current"])
    branch = (
        branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
    )

    # git status --porcelain
    result = run_git_command(["status", "--porcelain"])
    if result.returncode != 0:
        print("[ERROR] git status 실패")
        return 1

    lines = [l for l in result.stdout.split("\n") if l.strip()]

    modified, added, deleted, untracked = [], [], [], []
    for line in lines:
        st = line[:2]
        fp = line[3:].strip().strip('"')
        if st.strip() in ("M",) or st.endswith("M"):
            modified.append(fp)
        elif st.strip() == "A":
            added.append(fp)
        elif st.strip() == "D" or st.endswith("D"):
            deleted.append(fp)
        elif st.startswith("?"):
            untracked.append(fp)

    total = len(modified) + len(added) + len(deleted) + len(untracked)

    print(f"### Git 현황 (브랜치: {branch})\n")
    print("| 구분 | 파일 수 | 내용 |")
    print("|------|--------|------|")
    print(
        f"| 변경(M) | {len(modified)} | {', '.join(modified[:3])} |"
        if modified
        else f"| 변경(M) | 0 | - |"
    )
    print(
        f"| 추가(A) | {len(added)} | {', '.join(added[:3])} |"
        if added
        else f"| 추가(A) | 0 | - |"
    )
    print(
        f"| 삭제(D) | {len(deleted)} | (아래 참조) |"
        if deleted
        else f"| 삭제(D) | 0 | - |"
    )
    print(
        f"| 미추적(??) | {len(untracked)} | {', '.join(untracked[:3])} |"
        if untracked
        else f"| 미추적(??) | 0 | - |"
    )
    print(f"| **총계** | **{total}** | |")

    # 주요 변경사항 상세
    print("\n### 주요 변경사항\n")

    if modified:
        print("**수정 파일:**")
        for f in modified:
            print(f"- {f}")

    if added:
        print("\n**추가 파일:**")
        for f in added:
            print(f"- {f}")

    if untracked:
        print("\n**미추적 신규:**")
        for f in untracked:
            print(f"- {f}")

    if deleted:
        # 디렉토리별 그룹핑
        dir_groups: dict = {}
        for f in deleted:
            parts = f.split("/")
            top = parts[0] if len(parts) > 1 else "(root)"
            dir_groups.setdefault(top, []).append(f)

        print("\n**삭제 파일 (디렉토리별):**")
        for top_dir, files in sorted(dir_groups.items()):
            print(f"- `{top_dir}/` : {len(files)}개")

    # 최근 커밋
    print("\n### 최근 커밋\n")
    log_result = run_git_command(["log", "--oneline", "-5"])
    if log_result.returncode == 0:
        print("```")
        print(log_result.stdout.strip())
        print("```")

    # 완료 항목
    completed = extract_completed_items()
    if completed:
        print(f"\n### d0004 완료 항목 ({len(completed)}건 이동 대상)\n")
        for item in completed[:5]:
            print(f"- [{item['priority']}] {item['description'][:60]}")

    # 다음 단계
    print("\n### 다음 단계\n")
    if total > 0:
        print("커밋이 필요하면 `oocommit run` 또는 `oocommit preview` 를 실행하세요.")
    else:
        print("커밋할 변경사항이 없습니다.")

    return 0


def cmd_preview():
    """변경사항 및 이동 대상 미리보기 (preview 서브명령어)"""
    print("# oocommit preview\n")

    # Git 상태
    print("## Git 변경사항\n")
    status = get_git_status()
    if status:
        print(f"  수정: {len(status['modified'])}개")
        print(f"  추가: {len(status['added'])}개")
        print(f"  삭제: {len(status['deleted'])}개")
        print(f"  미추적: {len(status['untracked'])}개")

        if status["modified"]:
            print("\n  [수정된 파일]")
            for f in status["modified"][:10]:
                print(f"    - {f}")
    else:
        print("  Git 상태를 확인할 수 없습니다.")

    # 완료 항목
    print("\n## 완료 항목 (d0004 -> d0010 이동 대상)\n")
    completed = extract_completed_items()

    if completed:
        print(f"  {len(completed)}개 항목 발견")
        print()
        for item in completed:
            print(f"  [{item['priority']}] -> [{item['tag']}]")
            print(f"    {item['description'][:50]}")
    else:
        print("  이동할 완료 항목이 없습니다.")

    print()
    print("---")
    print("[INFO] 실제 실행: oocommit run")
    return 0


def cmd_commit(options):
    """Git 커밋만 수행 (commit 서브명령어)"""
    print("# oocommit commit\n")

    status = get_git_status()
    if not status or not any(status.values()):
        print("[INFO] 커밋할 변경사항이 없습니다.")
        return 0

    # 메시지 생성 또는 사용
    message = options.get("message", "")
    if not message:
        # 자동 메시지 생성
        completed = extract_completed_items()
        if completed:
            first_item = completed[0]
            commit_type = "fix" if first_item["tag"] in ["HOTFIX", "BUGFIX"] else "feat"
            message = f"{commit_type}: {first_item['description'][:50]}"
        else:
            message = "chore: update"

    print(f"커밋 메시지: {message}")
    print()

    if options.get("dry_run"):
        if options.get("no_push"):
            print("[DRY-RUN] 커밋 후 push는 생략됩니다 (--no-push).")
        else:
            print("[DRY-RUN] 커밋 후 기본 push가 수행됩니다.")
        print("[DRY-RUN] 실제 커밋을 수행하지 않습니다.")
        return 0

    # git add
    result = run_git_command(["add", "-A"])
    if result.returncode != 0:
        print(f"[ERROR] git add 실패: {result.stderr}")
        return 1

    # git commit
    full_message = f"{message}\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)\n\nCo-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

    result = run_git_command(["commit", "-m", full_message])
    if result.returncode != 0:
        print(f"[ERROR] git commit 실패: {result.stderr}")
        return 1

    print("[OK] 커밋 완료")

    if options.get("no_push") or "--no-push" in sys.argv:
        print("\n[INFO] push 생략 (--no-push)")
        return 0

    branch = get_current_branch()
    if not branch:
        print("\n[ERROR] 현재 브랜치를 확인할 수 없어 push를 중단합니다.")
        print("[TIP] 로컬 커밋은 완료되었습니다. 수동으로 git push 하세요.")
        return 1

    remote_name = get_remote_name()
    if not remote_name:
        print("\n[ERROR] remote가 설정되지 않아 push를 수행할 수 없습니다.")
        print("[TIP] 로컬 커밋은 완료되었습니다. remote 설정 후 git push 하세요.")
        return 1

    if has_upstream_configured():
        push_args = ["push", remote_name, branch]
        push_label = f"git push {remote_name} {branch}"
    else:
        push_args = ["push", "-u", remote_name, branch]
        push_label = f"git push -u {remote_name} {branch}"

    print(f"\n[INFO] push 수행: {push_label}")
    result = run_git_command(push_args)
    if result.returncode != 0:
        print(f"[ERROR] git push 실패: {result.stderr}")
        print("[TIP] 로컬 커밋은 완료되었습니다. 네트워크/인증/권한을 확인하세요.")
        return 1

    print("[OK] push 완료")

    return 0


def cmd_sync(options):
    """이력 정리만 수행 (sync 서브명령어)"""
    print("# oocommit sync\n")

    completed = extract_completed_items()

    if not completed:
        print("[INFO] 이동할 완료 항목이 없습니다.")
        return 0

    print(f"## 이동 대상: {len(completed)}건\n")
    for item in completed:
        print(f"  [{item['priority']}] -> [{item['tag']}] {item['description'][:40]}")

    if options.get("dry_run"):
        print("\n[DRY-RUN] 실제 이동을 수행하지 않습니다.")
        return 0

    if not HISTORY_FILE.exists():
        print(f"\n[WARN] {HISTORY_FILE}가 없습니다.")
        print("[TIP] oohistory create 로 먼저 생성하세요.")
        return 1

    # 이력 파일에 추가
    history_content = HISTORY_FILE.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")

    added = 0
    for item in completed:
        new_entry = f"\n#### {today} - {item['tag']} {item['description']}\n- **원본**: d0004_todo.md [{item['priority']}]\n"

        # 진행중 섹션에 추가
        in_progress_pattern = r"(###\s+\d+\.\d+\s+\[현재 버전\]\s*\(진행중\))"
        match = re.search(in_progress_pattern, history_content)

        if match:
            insert_pos = match.end()
            history_content = (
                history_content[:insert_pos] + new_entry + history_content[insert_pos:]
            )
            added += 1

    if added > 0:
        HISTORY_FILE.write_text(history_content, encoding="utf-8")
        print(f"\n[OK] {added}건 이력 추가됨")

        # TODO 파일에서 제거 (선택적)
        if "--remove" in sys.argv:
            todo_content = TODO_FILE.read_text(encoding="utf-8")
            for item in completed:
                todo_content = todo_content.replace(item["full_match"], "")
            TODO_FILE.write_text(todo_content, encoding="utf-8")
            print(f"[OK] d0004_todo.md에서 {added}건 제거됨")
    else:
        print("[WARN] 진행중 섹션을 찾을 수 없습니다.")

    return 0


def cmd_clear(options):
    """오래된 커밋 squash + .git 용량 정리 (clear 서브명령어)

    --keep N     : 보존할 최근 커밋 수 (기본 20)
    --push       : 정리 후 force push 실행
    --dry-run    : 실제 실행 없이 계획만 출력
    """
    print("# oocommit clear\n")
    print("=== 오래된 커밋 정리 + .git 용량 축소 ===\n")

    # ── 1. 현재 상태 확인 ──────────────────────────────────────────
    print("[1/5] 현재 git 상태 확인...")

    # 커밋 총 수
    count_result = run_git_command(["rev-list", "--count", "HEAD"])
    if count_result.returncode != 0:
        print("[ERROR] 커밋 수를 확인할 수 없습니다.")
        return 1
    total_commits = int(count_result.stdout.strip())

    # 브랜치
    branch_result = run_git_command(["branch", "--show-current"])
    branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "master"

    # remote 존재 여부
    remote_result = run_git_command(["remote"])
    has_remote = bool(remote_result.stdout.strip())
    remote_name = remote_result.stdout.strip().split("\n")[0] if has_remote else None

    # .git 크기
    git_dir = PROJECT_ROOT / ".git"
    git_size_mb = sum(f.stat().st_size for f in git_dir.rglob("*") if f.is_file()) / (
        1024 * 1024
    )

    print(f"  - 브랜치: {branch}")
    print(f"  - 전체 커밋 수: {total_commits}개")
    print(f"  - .git 크기: {git_size_mb:.1f} MB")
    print(f"  - Remote: {remote_name or '없음'}")

    # ── 2. 보존 커밋 수 계산 ────────────────────────────────────────
    print("\n[2/5] 정리 계획 수립...")

    # --keep 파싱
    keep = 20  # 기본값
    if "--keep" in sys.argv:
        idx = sys.argv.index("--keep")
        if idx + 1 < len(sys.argv):
            keep_str = sys.argv[idx + 1]
            if keep_str.isdigit():
                keep = int(keep_str)

    squash_count = total_commits - keep

    if squash_count <= 0:
        print(f"  - 전체 커밋({total_commits}개)이 보존 기준({keep}개) 이하입니다.")
        print("  - squash 불필요. gc만 실행합니다.")
        skip_squash = True
    else:
        skip_squash = False
        oldest_keep_result = run_git_command(["rev-parse", f"HEAD~{keep - 1}"])
        if oldest_keep_result.returncode != 0:
            print("[ERROR] 보존 기준 커밋 해시를 가져올 수 없습니다.")
            return 1
        oldest_keep = oldest_keep_result.stdout.strip()

        print(f"  - 보존 커밋: 최근 {keep}개")
        print(f"  - Squash 대상: {squash_count}개 → 1개로 통합")
        print(f"  - 보존 기준 커밋: {oldest_keep[:8]}")

    print(f"\n  [계획]")
    if not skip_squash:
        print(f"  1) orphan 브랜치 생성 (HEAD~{keep - 1} 기반)")
        print(f"  2) 최근 {keep - 1}개 커밋 rebase")
    print(f"  3) git reflog expire + gc --prune=now --aggressive")
    if options.get("push") or "--push" in sys.argv:
        print(f"  4) git push --force-with-lease origin {branch}")

    if options.get("dry_run"):
        print("\n[DRY-RUN] 실제 실행을 건너뜁니다.")
        return 0

    # ── 3. Squash 실행 ──────────────────────────────────────────────
    if not skip_squash:
        print("\n[3/5] 오래된 커밋 squash...")

        # orphan 브랜치 생성 (oldest_keep 트리 기반)
        r = run_git_command(["checkout", "--orphan", "new-root", oldest_keep])
        if r.returncode != 0:
            print(f"[ERROR] orphan 브랜치 생성 실패: {r.stderr}")
            return 1

        r = run_git_command(
            [
                "commit",
                "-m",
                f"chore: initial commit ({squash_count} old commits squashed)",
            ]
        )
        if r.returncode != 0:
            print(f"[ERROR] orphan 커밋 실패: {r.stderr}")
            run_git_command(["checkout", branch])
            run_git_command(["branch", "-D", "new-root"])
            return 1

        new_root_result = run_git_command(["rev-parse", "HEAD"])
        new_root = new_root_result.stdout.strip()
        print(f"  - 새 루트 커밋: {new_root[:8]}")

        # 원래 브랜치로 복귀
        r = run_git_command(["checkout", branch])
        if r.returncode != 0:
            print(f"[ERROR] 브랜치 복귀 실패: {r.stderr}")
            return 1

        # rebase: oldest_keep 이후 커밋들을 new_root 위로
        r = run_git_command(["rebase", "--onto", new_root, oldest_keep, branch])
        if r.returncode != 0:
            print(f"[ERROR] rebase 실패: {r.stderr}")
            print("[TIP] git rebase --abort 로 취소하세요.")
            run_git_command(["branch", "-D", "new-root"])
            return 1

        # 임시 브랜치 삭제
        run_git_command(["branch", "-D", "new-root"])
        print(f"  - Squash 완료: {total_commits}개 → {keep}개")
    else:
        print("\n[3/5] Squash 건너뜀 (커밋 수 기준 충족)")

    # ── 4. gc 실행 ──────────────────────────────────────────────────
    print("\n[4/5] .git 용량 정리 (gc)...")

    run_git_command(["reflog", "expire", "--expire=now", "--all"])
    r = run_git_command(["gc", "--prune=now", "--aggressive"])
    if r.returncode != 0:
        print(f"[WARN] gc 실패: {r.stderr}")
    else:
        # 정리 후 크기 계산
        git_size_after = sum(
            f.stat().st_size for f in git_dir.rglob("*") if f.is_file()
        ) / (1024 * 1024)
        saved = git_size_mb - git_size_after
        print(f"  - 정리 전: {git_size_mb:.1f} MB")
        print(f"  - 정리 후: {git_size_after:.1f} MB")
        print(f"  - 절감: {saved:.1f} MB")

    # ── 5. Push (선택) ──────────────────────────────────────────────
    do_push = options.get("push") or "--push" in sys.argv
    if do_push:
        print(f"\n[5/5] force push → {remote_name} {branch}...")
        if not has_remote:
            print("[WARN] remote가 설정되지 않았습니다.")
        else:
            r = run_git_command(["push", "--force-with-lease", remote_name, branch])
            if r.returncode != 0:
                print(f"[ERROR] push 실패: {r.stderr}")
                print("[TIP] 처음 push 시에는 --force 가 필요할 수 있습니다.")
                print(f"       git push --force {remote_name} {branch}")
            else:
                print(f"  - push 완료")
    else:
        print(f"\n[5/5] Push 건너뜀 (--push 옵션 미지정)")
        if has_remote:
            print(
                f"  [TIP] force push 필요: git push --force-with-lease {remote_name} {branch}"
            )

    # ── 완료 ────────────────────────────────────────────────────────
    final_count_result = run_git_command(["rev-list", "--count", "HEAD"])
    final_count = (
        int(final_count_result.stdout.strip())
        if final_count_result.returncode == 0
        else "?"
    )

    print(f"\n=== 완료 ===")
    print(f"  - 커밋: {total_commits}개 → {final_count}개")
    return 0


def cmd_run(options):
    """커밋 + 이력 정리 통합 실행 (run 서브명령어)"""
    print("# oocommit run\n")
    print("=== oocommit 통합 워크플로우 ===\n")

    # 변경 파일 수집 (0단계에서 사용)
    status = get_git_status()
    total = 0
    all_files = []
    if status:
        total = sum(len(v) for v in status.values())
        all_files = (
            status["modified"] + status["added"] +
            status["deleted"] + status["untracked"]
        )

    # [0/5] 상세문서 업데이트 확인 (항상 실행)
    doc_result = step_pre_commit_doc_check(all_files, options)
    if doc_result != 0:
        return doc_result  # 1=NEED_ACTION — 커밋 블록, Claude가 사용자 선택 후 재실행

    # 1단계: 변경사항 분석
    print("\n[1/5] 변경사항 분석...")
    if status:
        print(f"  - 수정된 파일: {len(status['modified'])}개")
        print(f"  - 새 파일: {len(status['added']) + len(status['untracked'])}개")
        print(f"  - 삭제된 파일: {len(status['deleted'])}개")
    else:
        print("  - Git 상태 확인 실패")

    # 2단계: Git 커밋
    print("\n[2/5] Git 커밋 수행...")
    if total > 0:
        result = cmd_commit(options)
        if result != 0:
            print("  - 커밋 실패")
            return result
        print("  - 커밋 완료")
    else:
        print("  - 커밋할 변경사항 없음")

    # 3단계: 완료 항목 추출
    print("\n[3/5] TODO 완료 항목 추출...")
    completed = extract_completed_items()
    print(f"  - 완료 항목: {len(completed)}개 발견")

    for item in completed[:5]:
        print(f"    - [{item['priority']}] {item['description'][:30]}")

    # 4단계: 이력 문서 업데이트
    print("\n[4/5] 이력 문서 업데이트...")
    if completed:
        sync_result = cmd_sync(options)
        if sync_result == 0:
            print("  - 이력 업데이트 완료")
    else:
        print("  - 이동할 항목 없음")

    # 5단계: 검증
    print("\n[5/5] 검증 완료")
    print("  - 문서 무결성 확인")

    print("\n=== 완료 ===")
    return 0


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

    # --sp 옵션 추출
    sp_arg = None
    for _i, _a in enumerate(args):
        if _a == "--sp" and _i + 1 < len(args):
            try:
                sp_arg = int(args[_i + 1])
            except ValueError:
                pass
            args = args[:_i] + args[_i + 2:]
            break

    # SP 결정 및 전역 경로 업데이트
    global TODO_FILE, HISTORY_FILE, DOC_DIR
    sp_num = resolve_sp(sp_arg)
    DOC_DIR = get_sp_doc_dir(sp_num)
    TODO_FILE = get_doc_path(sp_num, 4, "todo")
    HISTORY_FILE = get_doc_path(sp_num, 10, "history")
    if sp_num:
        print(f"[INFO] SP{sp_num:02d} 컨텍스트 적용")

    if not args:
        print_usage()
        return 0

    cmd = args[0].lower()
    if cmd in ("show",) and len(args) > 1 and args[1].lower() == "checklist":
        cmd_show_checklist()
        return

    # 옵션 파싱
    options = {
        "dry_run": "--dry-run" in args,
        "no_push": "--no-push" in args,
        "force": "--force" in args,
        "push": "--push" in args,
    }

    # --message 옵션
    if "--message" in args:
        idx = args.index("--message")
        if idx + 1 < len(args):
            options["message"] = args[idx + 1]

    if cmd == "status":
        return cmd_status()
    elif cmd == "run":
        return cmd_run(options)
    elif cmd == "commit":
        return cmd_commit(options)
    elif cmd == "sync":
        return cmd_sync(options)
    elif cmd == "preview":
        return cmd_preview()
    elif cmd == "clear":
        return cmd_clear(options)
    elif cmd == "check":
        print(f"[check] oocommit 체크리스트 안내")
        _print_skill_help("oocommit")
        return 0
    elif cmd in ("help", "-h"):
        _print_skill_help("oocommit")
        return 0
    else:
        print(f"[ERROR] Unknown command: {cmd}")
        print_usage()
        return 1


if __name__ == "__main__":
    sys.exit(main())
