#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
oosync_pipeline.py - 표준 검증 → 배포 파이프라인

흐름:
    Phase 1: ooenv standard 실행 → 표준 환경 검증
      ├─ PASS → Phase 2로 진행
      ├─ FAIL + --force → 경고 후 Phase 2 진행
      └─ FAIL → 중단, "표준 검사 실패" 메시지
    Phase 2: ccsync run --push-only 실행
    Phase 3: 결과 요약 출력

옵션:
    --dry-run       Phase 2 미리보기 (실제 동기화 안 함)
    --force         Phase 1 실패해도 Phase 2 강행
    --skip-standard Phase 1 건너뜀
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Windows 콘솔 UTF-8 출력 설정
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 경로 설정
SCRIPT_DIR = Path(__file__).parent
SKILLS_DIR = SCRIPT_DIR.parent.parent      # .claude/skills/
PROJECT_ROOT = SKILLS_DIR.parent.parent    # 프로젝트 루트

STANDARD_SCRIPT = SKILLS_DIR / "ooenv" / "scripts" / "ooenv_standard.py"
SYNC_SCRIPT = SKILLS_DIR / "ccsync" / "scripts" / "oosync_run.py"


# ============================================================
# 유틸리티
# ============================================================

def print_phase(n: int, title: str) -> None:
    """페이즈 헤더 출력"""
    print(f"\n{'='*60}")
    print(f"  Phase {n}: {title}")
    print(f"{'='*60}\n")


# ============================================================
# 페이즈 함수
# ============================================================

def run_phase1(force: bool = False) -> bool:
    """Phase 1: 표준 환경 검증. 통과 여부(또는 force 시 True) 반환."""
    print_phase(1, "ooenv standard - 표준 환경 검증")

    if not STANDARD_SCRIPT.exists():
        print(f"[ERROR] standard 스크립트 없음: {STANDARD_SCRIPT}")
        return False

    result = subprocess.run(
        ["uv", "run", "python", str(STANDARD_SCRIPT)],
        cwd=str(PROJECT_ROOT)
    )
    passed = result.returncode == 0

    if not passed:
        if force:
            print("\n[WARN] 표준 검사 실패 - --force 옵션으로 Phase 2를 강행합니다.")
        else:
            print("\n[FAIL] 표준 검사 실패 - 배포를 중단합니다.")
            print("       강행하려면 --force 옵션을 사용하세요.")

    return passed or force


def run_phase2(dry_run: bool = False) -> bool:
    """Phase 2: ccsync run --push-only. 성공 여부 반환."""
    mode_str = "(dry-run 미리보기)" if dry_run else "(실제 동기화)"
    print_phase(2, f"ccsync run --push-only {mode_str}")

    if not SYNC_SCRIPT.exists():
        print(f"[ERROR] sync 스크립트 없음: {SYNC_SCRIPT}")
        return False

    cmd = ["uv", "run", "python", str(SYNC_SCRIPT), "run", "--push-only"]
    if dry_run:
        cmd.append("--dry-run")

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    return result.returncode == 0


# ============================================================
# 요약 출력
# ============================================================

def print_summary(
    phase1_ok,       # True/False/None(건너뜀)
    phase2_ok,       # True/False/None(미실행)
    dry_run: bool,
    start_time: datetime
) -> None:
    """Phase 3: 결과 요약 테이블 출력"""
    elapsed = (datetime.now() - start_time).total_seconds()

    print("| Phase | 결과 |")
    print("|-------|------|")

    if phase1_ok is None:
        print("| Phase 1: 표준 검증 | 건너뜀 |")
    else:
        print(f"| Phase 1: 표준 검증 | {'PASS' if phase1_ok else 'FAIL'} |")

    if phase2_ok is None:
        print("| Phase 2: 동기화 | 미실행 |")
    else:
        mode = " (dry-run)" if dry_run else ""
        print(f"| Phase 2: 동기화{mode} | {'PASS' if phase2_ok else 'FAIL'} |")

    overall = (phase1_ok is not False) and (phase2_ok is not False)
    print(f"\n**전체 결과**: {'SUCCESS' if overall else 'FAILED'} ({elapsed:.1f}s)")


# ============================================================
# 메인 파이프라인
# ============================================================

def run_pipeline(dry_run: bool = False, force: bool = False, skip_standard: bool = False) -> int:
    """전체 파이프라인 실행. 0=성공, 1=실패."""
    start_time = datetime.now()

    print(f"# ccsync pipeline - 표준 검증 → 배포\n")
    print(f"시각: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"옵션: dry_run={dry_run}, force={force}, skip_standard={skip_standard}")

    phase1_ok = None
    phase2_ok = None

    # Phase 1: 표준 검증
    if skip_standard:
        print("\n[INFO] Phase 1 건너뜀 (--skip-standard)")
        phase1_ok = None  # None = 건너뜀
    else:
        phase1_passed = run_phase1(force=force)
        phase1_ok = phase1_passed

        if not phase1_passed:
            # force 아닌 경우 중단
            print_phase(3, "결과 요약")
            print_summary(phase1_ok=False, phase2_ok=None, dry_run=dry_run, start_time=start_time)
            return 1

    # Phase 2: 동기화
    phase2_passed = run_phase2(dry_run=dry_run)
    phase2_ok = phase2_passed

    # Phase 3: 요약
    print_phase(3, "결과 요약")
    print_summary(phase1_ok=phase1_ok, phase2_ok=phase2_ok, dry_run=dry_run, start_time=start_time)

    return 0 if phase2_passed else 1


def main():
    dry_run = "--dry-run" in sys.argv
    force = "--force" in sys.argv
    skip_standard = "--skip-standard" in sys.argv
    exit_code = run_pipeline(dry_run=dry_run, force=force, skip_standard=skip_standard)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
