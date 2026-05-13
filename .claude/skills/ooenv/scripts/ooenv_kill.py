#!/usr/bin/env python3
"""
ooenv_kill.py

좀비 프로세스 탐지 및 종료 (Windows 전용)

Usage:
    uv run python .claude/skills/ooenv/scripts/ooenv_kill.py node
    uv run python .claude/skills/ooenv/scripts/ooenv_kill.py node --dry-run
    uv run python .claude/skills/ooenv/scripts/ooenv_kill.py node --force
    uv run python .claude/skills/ooenv/scripts/ooenv_kill.py --list
"""

import argparse
import subprocess
import sys

# Windows 콘솔 UTF-8 인코딩 설정
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ============================================================
# Configuration
# ============================================================

# 지원 프로세스 목록: key=별칭, value=실제 프로세스명
PROCESS_MAP = {
    "node": "node.exe",
    "python": "python.exe",
    "chrome": "chrome.exe",
    "edge": "msedge.exe",
}


# ============================================================
# Functions
# ============================================================

def get_processes(image_name: str) -> list[dict]:
    """tasklist로 프로세스 목록 조회"""
    cmd = ["tasklist", "/FI", f"IMAGENAME eq {image_name}", "/FO", "CSV", "/NH"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return []

    processes = []
    for line in result.stdout.strip().split('\n'):
        line = line.strip()
        if not line or "No tasks" in line or "정보 없음" in line:
            continue
        # CSV 파싱: "이미지 이름","PID","세션 이름","세션#","메모리 사용"
        parts = [p.strip('"') for p in line.split('","')]
        if len(parts) >= 5:
            try:
                pid = int(parts[1])
                mem_str = parts[4].replace(',', '').replace(' K', '').replace(' ', '')
                mem_kb = int(mem_str) if mem_str.isdigit() else 0
                processes.append({
                    "name": parts[0],
                    "pid": pid,
                    "session": parts[2],
                    "mem_kb": mem_kb,
                })
            except (ValueError, IndexError):
                continue

    return processes


def kill_processes(pids: list[int], force: bool = False) -> tuple[int, int]:
    """프로세스 종료. (성공, 실패) 수 반환"""
    success = 0
    fail = 0
    for pid in pids:
        cmd = ["taskkill", "/PID", str(pid)]
        if force:
            cmd.append("/F")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            success += 1
        else:
            fail += 1
            print(f"  실패 PID {pid}: {result.stderr.strip()}")
    return success, fail


def format_mem(kb: int) -> str:
    """KB를 읽기 쉬운 형태로 변환"""
    if kb >= 1024 * 1024:
        return f"{kb / (1024 * 1024):.1f} GB"
    elif kb >= 1024:
        return f"{kb / 1024:.1f} MB"
    return f"{kb} KB"


def show_list():
    """지원 프로세스 별칭 목록 표시"""
    print("# 지원 프로세스 목록\n")
    print(f"{'별칭':<10} {'프로세스명':<20}")
    print(f"{'-'*10} {'-'*20}")
    for alias, exe in PROCESS_MAP.items():
        print(f"{alias:<10} {exe:<20}")


def main():
    parser = argparse.ArgumentParser(description="좀비 프로세스 탐지 및 종료")
    parser.add_argument("target", nargs="?", help="종료 대상 (node, python, chrome, edge)")
    parser.add_argument("--dry-run", action="store_true", help="종료 없이 목록만 표시")
    parser.add_argument("--force", action="store_true", help="강제 종료 (/F)")
    parser.add_argument("--list", action="store_true", help="지원 프로세스 목록 표시")
    args = parser.parse_args()

    if args.list:
        show_list()
        return

    if not args.target:
        parser.error("종료 대상을 지정하세요 (예: node). --list로 목록 확인")

    target = args.target.lower()
    if target not in PROCESS_MAP:
        print(f"오류: '{target}'은 지원되지 않는 대상입니다.")
        print(f"지원 목록: {', '.join(PROCESS_MAP.keys())}")
        sys.exit(1)

    image_name = PROCESS_MAP[target]

    print(f"# ooenv kill {target} - 프로세스 탐지\n")

    # 1. 프로세스 조회
    processes = get_processes(image_name)

    if not processes:
        print(f"{image_name} 프로세스가 없습니다.")
        return

    # 2. 목록 표시
    total_mem = sum(p["mem_kb"] for p in processes)
    print(f"## {image_name} 프로세스 {len(processes)}개 (총 {format_mem(total_mem)})\n")
    print(f"{'PID':>8}  {'메모리':>10}  {'세션'}")
    print(f"{'-'*8}  {'-'*10}  {'-'*15}")
    for p in sorted(processes, key=lambda x: x["mem_kb"], reverse=True):
        print(f"{p['pid']:>8}  {format_mem(p['mem_kb']):>10}  {p['session']}")

    if args.dry_run:
        print(f"\n(--dry-run: 종료하지 않음)")
        return

    # 3. 종료 실행
    pids = [p["pid"] for p in processes]
    mode = "강제 종료" if args.force else "종료"
    print(f"\n## {mode} 실행\n")

    success, fail = kill_processes(pids, force=args.force)
    print(f"\n결과: 성공 {success}개, 실패 {fail}개")

    if fail > 0 and not args.force:
        print("팁: --force 옵션으로 강제 종료 가능")


if __name__ == "__main__":
    main()
