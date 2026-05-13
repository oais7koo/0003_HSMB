#!/usr/bin/env python3
"""
oodata_run.py - data/ 폴더 백업/복원 스킬
Usage: uv run python .claude/skills/ccdata/scripts/oodata_run.py [backup|restore|list|status|help]
"""
import sys
import shutil
from pathlib import Path
import re as _re

# --- oo_common inline ---
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

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

SKILL_NAME = "ccdata"
VERSION = "v01"

# 프로젝트 루트: scripts/ → ccdata/ → skills/ → .claude/ → project_root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_BACKUP_PATH = Path(r"f:\udd\data_exa\exa63_dual_branch")


# ============================================================
# 유틸리티
# ============================================================

def ask_backup_path(default: Path) -> Path:
    print(f"백업 경로 입력 (Enter = {default}): ", end="", flush=True)
    user_input = input().strip()
    return Path(user_input) if user_input else default


def folder_size_mb(folder: Path) -> float:
    try:
        return sum(f.stat().st_size for f in folder.rglob("*") if f.is_file()) / (1024 * 1024)
    except Exception:
        return 0.0


def list_data_folders() -> list:
    """data/ 내 실제 ps 폴더 목록 (_backup 마커·숨김 제외)"""
    if not DATA_DIR.exists():
        return []
    return sorted(
        p for p in DATA_DIR.iterdir()
        if p.is_dir() and not p.name.endswith("_backup") and not p.name.startswith(".")
    )


def list_backup_markers() -> list:
    """data/ 내 _backup 마커 폴더 목록"""
    if not DATA_DIR.exists():
        return []
    return sorted(p for p in DATA_DIR.iterdir() if p.is_dir() and p.name.endswith("_backup"))


def select_from_list(items: list, label_fn, prompt: str) -> list:
    """목록에서 사용자 선택 (번호 / 쉼표 복수 / all / 0=취소)"""
    if not items:
        print("[INFO] 선택 가능한 항목이 없습니다.")
        return []

    print(f"\n{prompt}")
    for i, item in enumerate(items, 1):
        print(f"  [{i}] {label_fn(item)}")
    print(f"  [0] 취소\n")
    print("선택 (번호, 복수=쉼표 구분, all=전체): ", end="", flush=True)
    raw = input().strip()

    if not raw or raw == "0":
        return []
    if raw.lower() == "all":
        return list(items)

    selected = []
    for token in raw.split(","):
        token = token.strip()
        if token.isdigit():
            idx = int(token) - 1
            if 0 <= idx < len(items):
                selected.append(items[idx])
            else:
                print(f"  [WARN] 범위 초과: {token}")
    return selected


def confirm(message: str) -> bool:
    print(f"\n{message} (y/N): ", end="", flush=True)
    return input().strip().lower() == "y"


# ============================================================
# 서브명령어
# ============================================================

def cmd_list():
    print(f"\n[ccdata list] data/ 폴더 현황")
    print(f"  DATA_DIR: {DATA_DIR}\n")

    folders = list_data_folders()
    markers = list_backup_markers()

    print(f"실제 폴더 ({len(folders)}개):")
    if folders:
        for f in folders:
            mb = folder_size_mb(f)
            print(f"  {f.name:<25}  {mb:>8.1f} MB")
    else:
        print("  (없음)")

    print(f"\n백업 마커 ({len(markers)}개) — 외부로 이동된 항목:")
    if markers:
        for m in markers:
            ps_name = m.name.removesuffix("_backup")
            print(f"  {m.name:<25}  (원본: {ps_name})")
    else:
        print("  (없음)")


def cmd_backup():
    print(f"\n[ccdata backup]\n")

    backup_root = ask_backup_path(DEFAULT_BACKUP_PATH)

    folders = list_data_folders()

    def label(f: Path) -> str:
        mb = folder_size_mb(f)
        return f"{f.name}  ({mb:.1f} MB)"

    selected = select_from_list(folders, label, "백업할 폴더를 선택하세요:")
    if not selected:
        print("[INFO] 취소되었습니다.")
        return

    print(f"\n  백업 경로 : {backup_root}")
    print(f"  대상      : {[f.name for f in selected]}")

    if not confirm("백업을 진행하시겠습니까?"):
        print("[INFO] 취소되었습니다.")
        return

    backup_root.mkdir(parents=True, exist_ok=True)

    success, errors = [], []
    for folder in selected:
        dest = backup_root / folder.name
        marker = DATA_DIR / f"{folder.name}_backup"
        try:
            if dest.exists():
                print(f"  [SKIP] {folder.name}: 대상 경로 이미 존재 ({dest})")
                errors.append((folder.name, "대상 경로 이미 존재"))
                continue
            print(f"  이동 중: {folder.name} → {dest} ...", end="", flush=True)
            shutil.move(str(folder), str(dest))
            marker.mkdir(exist_ok=True)
            print(" ✓")
            success.append(folder.name)
        except Exception as e:
            print(f" FAIL: {e}")
            errors.append((folder.name, str(e)))

    print(f"\n완료: 성공 {len(success)}개 / 실패 {len(errors)}개")
    if errors:
        for name, reason in errors:
            print(f"  [FAIL] {name}: {reason}")


def cmd_restore():
    print(f"\n[ccdata restore]\n")

    backup_root = ask_backup_path(DEFAULT_BACKUP_PATH)

    markers = list_backup_markers()
    if not markers:
        print("[INFO] 복원할 _backup 마커가 없습니다.")
        return

    # (marker_path, ps_name, src_path) 튜플 목록
    restore_items = [
        (m, m.name.removesuffix("_backup"), backup_root / m.name.removesuffix("_backup"))
        for m in markers
    ]

    def label(item) -> str:
        m, ps_name, src = item
        exists = "존재" if src.exists() else "없음"
        return f"{ps_name:<25}  외부: [{exists}] {src}"

    selected = select_from_list(restore_items, label, "복원할 항목을 선택하세요:")
    if not selected:
        print("[INFO] 취소되었습니다.")
        return

    print(f"\n  복원 경로 : {backup_root}")
    print(f"  대상      : {[ps_name for _, ps_name, _ in selected]}")

    if not confirm("복원을 진행하시겠습니까?"):
        print("[INFO] 취소되었습니다.")
        return

    success, errors = [], []
    for marker, ps_name, src in selected:
        dest = DATA_DIR / ps_name
        try:
            if not src.exists():
                print(f"  [SKIP] {ps_name}: 외부 경로 없음 ({src})")
                errors.append((ps_name, "외부 경로 없음"))
                continue
            if dest.exists():
                print(f"  [SKIP] {ps_name}: data/ 에 이미 존재")
                errors.append((ps_name, "data/ 에 이미 존재"))
                continue
            print(f"  복원 중: {src} → {dest} ...", end="", flush=True)
            shutil.move(str(src), str(dest))
            marker.rmdir()
            print(" ✓")
            success.append(ps_name)
        except Exception as e:
            print(f" FAIL: {e}")
            errors.append((ps_name, str(e)))

    print(f"\n완료: 성공 {len(success)}개 / 실패 {len(errors)}개")
    if errors:
        for name, reason in errors:
            print(f"  [FAIL] {name}: {reason}")


def cmd_status():
    print(f"[{SKILL_NAME} status]  버전: {VERSION}")
    print(f"  DATA_DIR     : {DATA_DIR}  ({'존재' if DATA_DIR.exists() else '없음'})")
    print(f"  기본 백업 경로: {DEFAULT_BACKUP_PATH}")
    folders = list_data_folders()
    markers = list_backup_markers()
    print(f"  실제 폴더    : {len(folders)}개")
    print(f"  백업 마커    : {len(markers)}개")


def cmd_version():
    print(f"[{SKILL_NAME}] 버전: {VERSION}")


# ============================================================
# 진입점
# ============================================================

def cmd_show_checklist():
    """references/checklist.md 내용 출력"""
    checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[{SKILL_NAME}] checklist.md 없음: {checklist_path}")
        return
    print(checklist_path.read_text(encoding="utf-8"))


def main():
    args = sys.argv[1:]
    if show_help_if_no_args(SKILL_NAME, args):
        return
    cmd = args[0].lower()
    dispatch = {
        "version": cmd_version,
        "status":  cmd_status,
        "list":    cmd_list,
        "backup":  cmd_backup,
        "restore": cmd_restore,
    }
    fn = dispatch.get(cmd)
    if fn:
        fn()
    else:
        if cmd in ("show",) and len(args) > 1 and args[1].lower() == "checklist":
            cmd_show_checklist()
            return
        print(f"[WARN] 알 수 없는 명령어: {cmd}")
        _print_skill_help(SKILL_NAME)


if __name__ == "__main__":
    main()
