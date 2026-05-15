"""
[oopaper_backup.py]
03_paper/ 내 PDF 파일을 외부 백업 경로로 이동하거나 복원합니다.
hostname을 자동 감지하여 컴퓨터별 백업 경로를 선택합니다.

사용법:
    uv run python .claude/skills/oopaper/scripts/oopaper_backup.py backup [--dry-run] [--folder ID] [--subdir DIR]
    uv run python .claude/skills/oopaper/scripts/oopaper_backup.py restore [--dry-run] [--folder ID] [--subdir DIR]
    uv run python .claude/skills/oopaper/scripts/oopaper_backup.py status
    uv run python .claude/skills/oopaper/scripts/oopaper_backup.py config --path PATH
    uv run python .claude/skills/oopaper/scripts/oopaper_backup.py config --list

설정 파일 구조 (03_paper/backup_config.json):
    {
      "hosts": {
        "hostname1": "C:/path/to/backup",
        "hostname2": "D:/other/backup"
      }
    }
"""

import argparse
import json
import shutil
import socket
import sys
from pathlib import Path

# Windows CP949 인코딩 문제 방지
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# scripts/ → oopaper/ → skills/ → .claude/ → PROJECT_ROOT
# OAIS=03_paper/ 하위, 독립 프로젝트=루트 직하 양쪽 호환
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
PAPER_BASE = PROJECT_ROOT / "03_paper" if (PROJECT_ROOT / "03_paper").exists() else PROJECT_ROOT
CONFIG_FILE = PAPER_BASE / "backup_config.json"

# 백업 대상 하위 폴더 (00_down 제외)
BACKUP_SUBDIRS = ["01_book_ko", "02_book_en", "03_book_ja", "11_paper_en", "12_paper_ko"]


def get_hostname():
    return socket.gethostname()


def load_backup_dir():
    """현재 hostname에 맞는 백업 경로를 반환. 없으면 None."""
    hostname = get_hostname()

    if not CONFIG_FILE.exists():
        print(f"[ERROR] 설정 파일 없음: {CONFIG_FILE}")
        print(f"  → 먼저 등록: uv run python ... config --path <백업경로>")
        return None

    with open(CONFIG_FILE, encoding="utf-8") as f:
        config = json.load(f)

    hosts = config.get("hosts", {})
    if hostname not in hosts:
        print(f"[ERROR] 이 컴퓨터({hostname})의 백업 경로가 등록되지 않았습니다.")
        print(f"  → 등록 명령: uv run python ... config --path <백업경로>")
        if hosts:
            print(f"  → 등록된 호스트: {', '.join(hosts.keys())}")
        return None

    backup_dir = Path(hosts[hostname])
    if not backup_dir.exists():
        print(f"[WARNING] 백업 경로가 존재하지 않습니다: {backup_dir}")
        print(f"  → 경로를 확인하거나 드라이브/폴더를 마운트하세요.")
        return None

    return backup_dir


def save_host_config(backup_dir: str):
    """현재 hostname으로 백업 경로를 등록/업데이트."""
    hostname = get_hostname()
    backup_path = str(Path(backup_dir).as_posix())

    # 기존 설정 로드
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, encoding="utf-8") as f:
            config = json.load(f)
        # 구버전 형식 자동 마이그레이션
        if "backup_dir" in config and "hosts" not in config:
            old_host = config.get("hostname", "unknown")
            old_dir = config.get("backup_dir", "")
            config = {"hosts": {old_host: old_dir}}
    else:
        config = {"hosts": {}}

    config["hosts"][hostname] = backup_path

    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"[OK] 설정 저장: {CONFIG_FILE}")
    print(f"     hostname  : {hostname}")
    print(f"     backup_dir: {backup_path}")


def collect_pdfs(base_dir: Path, subdirs: list, folder_filter: str = None, subdir_filter: str = None):
    """base_dir 내 PDF 파일 목록 수집. (base_dir 기준 상대경로, 절대경로) 반환"""
    results = []
    targets = [subdir_filter] if subdir_filter else subdirs
    for subdir in targets:
        src = base_dir / subdir
        if not src.exists():
            continue
        for pdf in sorted(src.rglob("*.pdf")):
            rel = pdf.relative_to(base_dir)
            if folder_filter:
                parts = rel.parts
                if len(parts) < 2 or parts[1] != folder_filter:
                    continue
            results.append((rel, pdf))
    return results


def cmd_backup(args):
    backup_base = load_backup_dir()
    if not backup_base:
        return

    pdfs = collect_pdfs(PAPER_BASE, BACKUP_SUBDIRS, args.folder, args.subdir)
    if not pdfs:
        print("[INFO] 백업할 PDF 없음.")
        return

    print(f"[backup] 호스트: {get_hostname()}")
    print(f"[backup] 대상 {len(pdfs)}개 → {backup_base}")
    if args.dry_run:
        print("  (dry-run 모드: 실제 이동 안 함)\n")

    moved = 0
    for rel, src in pdfs:
        dst = backup_base / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if args.dry_run:
            print(f"  [이동예정] {rel}")
        else:
            shutil.move(str(src), str(dst))
            print(f"  [이동] {rel}")
            moved += 1

    if not args.dry_run:
        print(f"\n[완료] {moved}개 PDF 백업 완료.")


def cmd_restore(args):
    backup_base = load_backup_dir()
    if not backup_base:
        return

    pdfs = collect_pdfs(backup_base, BACKUP_SUBDIRS, args.folder, args.subdir)
    if not pdfs:
        print("[INFO] 복원할 PDF 없음.")
        return

    print(f"[restore] 호스트: {get_hostname()}")
    print(f"[restore] 대상 {len(pdfs)}개 → {PAPER_BASE}")
    if args.dry_run:
        print("  (dry-run 모드: 실제 이동 안 함)\n")

    moved = 0
    for rel, src in pdfs:
        dst = PAPER_BASE / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if args.dry_run:
            print(f"  [복원예정] {rel}")
        else:
            shutil.copy2(str(src), str(dst))
            print(f"  [복원] {rel}")
            moved += 1

    if not args.dry_run:
        print(f"\n[완료] {moved}개 PDF 복원 완료. (백업본 유지)")


def cmd_status(args):
    hostname = get_hostname()
    print(f"[status] 호스트  : {hostname}")
    print(f"         프로젝트: {PAPER_BASE}")

    backup_base = None
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, encoding="utf-8") as f:
            config = json.load(f)
        hosts = config.get("hosts", {})
        if hostname in hosts:
            backup_base = Path(hosts[hostname])
            exists_mark = "(존재)" if backup_base.exists() else "(없음 - 경고)"
            print(f"         백업경로: {backup_base} {exists_mark}")
        else:
            print(f"         백업경로: (미등록 - 이 호스트 설정 없음)")
        if hosts:
            print(f"         등록호스트: {', '.join(hosts.keys())}")
    else:
        print(f"         백업경로: (설정 파일 없음)")
    print()

    for subdir in BACKUP_SUBDIRS:
        src_dir = PAPER_BASE / subdir
        src_count = len(list(src_dir.rglob("*.pdf"))) if src_dir.exists() else 0

        bak_count = 0
        if backup_base and backup_base.exists():
            bak_dir = backup_base / subdir
            bak_count = len(list(bak_dir.rglob("*.pdf"))) if bak_dir.exists() else 0

        print(f"  {subdir}/")
        print(f"    원본: {src_count}개 PDF")
        if backup_base:
            print(f"    백업: {bak_count}개 PDF")
        print()


def cmd_config(args):
    if args.list:
        if not CONFIG_FILE.exists():
            print("[INFO] 설정 파일 없음.")
            return
        with open(CONFIG_FILE, encoding="utf-8") as f:
            config = json.load(f)
        hosts = config.get("hosts", {})
        hostname = get_hostname()
        print(f"설정 파일: {CONFIG_FILE}")
        print(f"현재 호스트: {hostname}")
        print("등록된 호스트:")
        for h, d in hosts.items():
            marker = " ← 현재" if h == hostname else ""
            print(f"  {h}: {d}{marker}")
        return

    if not args.path:
        print("[ERROR] --path 또는 --list 옵션을 지정하세요.")
        return

    save_host_config(args.path)


def main():
    parser = argparse.ArgumentParser(description="oopaper backup/restore (hostname 자동 감지)")
    sub = parser.add_subparsers(dest="command")

    # backup
    p_bak = sub.add_parser("backup", help="PDF를 백업 경로로 이동")
    p_bak.add_argument("--dry-run", action="store_true", help="실제 이동 없이 목록만 출력")
    p_bak.add_argument("--folder", metavar="ID", help="특정 폴더만 (예: 260222-1921)")
    p_bak.add_argument("--subdir", metavar="DIR", help="특정 하위 폴더만 (예: 11_paper_en)")

    # restore
    p_res = sub.add_parser("restore", help="백업 경로에서 PDF 복원")
    p_res.add_argument("--dry-run", action="store_true", help="실제 이동 없이 목록만 출력")
    p_res.add_argument("--folder", metavar="ID", help="특정 폴더만")
    p_res.add_argument("--subdir", metavar="DIR", help="특정 하위 폴더만")

    # status
    sub.add_parser("status", help="원본/백업 PDF 현황")

    # config
    p_cfg = sub.add_parser("config", help="백업 경로 설정")
    p_cfg.add_argument("--path", metavar="PATH", help="이 컴퓨터의 백업 경로 등록")
    p_cfg.add_argument("--list", action="store_true", help="등록된 모든 호스트 목록 출력")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    dispatch = {
        "backup": cmd_backup,
        "restore": cmd_restore,
        "status": cmd_status,
        "config": cmd_config,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
