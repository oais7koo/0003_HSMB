#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ooenv_claude_settings.py - Claude 설정 파일 관리

3가지 체크:
  CHECK-1: 글로벌 ~/.claude/settings.json에서 statusLine 외 항목 자동 삭제
  CHECK-2: 삭제 전 프로젝트 .claude/settings.json에 없으면 이동 여부 질문
  CHECK-3: 프로젝트 enabledPlugins 중 미설치 플러그인 발견 시 설치 여부 질문

사용법:
    uv run python .claude/skills/ooenv/scripts/ooenv_claude_settings.py
    uv run python .claude/skills/ooenv/scripts/ooenv_claude_settings.py --dry-run
    uv run python .claude/skills/ooenv/scripts/ooenv_claude_settings.py --yes  # 모든 질문 자동 y

exit code:
    0 - 완료 (변경 있음 or 없음)
    1 - 오류
"""

import sys
import json
import subprocess
from pathlib import Path

# Windows 콘솔 UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 경로
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent  # .claude/skills/ooenv/scripts/ → 프로젝트 루트
GLOBAL_SETTINGS = Path.home() / ".claude" / "settings.json"
PROJECT_SETTINGS = PROJECT_ROOT / ".claude" / "settings.json"

# 글로벌에 유지할 키 (머신별 설정)
GLOBAL_KEEP_KEYS = {"statusLine"}


# ============================================================
# 유틸리티
# ============================================================

def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 파싱 실패 ({path}): {e}")
        sys.exit(1)


def save_json(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )


def ask(question: str, auto_yes: bool) -> bool:
    """y/n 질문. auto_yes=True면 항상 y."""
    if auto_yes:
        print(f"{question} → (자동 y)")
        return True
    while True:
        ans = input(f"{question} (y/n): ").strip().lower()
        if ans in ('y', 'yes'):
            return True
        if ans in ('n', 'no'):
            return False
        print("  y 또는 n을 입력하세요.")


def deep_get(data: dict, key: str):
    """중첩 키 접근. 점(.) 구분은 없고 최상위 키만 지원."""
    return data.get(key)


def deep_set(data: dict, key: str, value) -> dict:
    data[key] = value
    return data


def run_command(cmd: list) -> tuple:
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=15,
            encoding='utf-8', errors='replace'
        )
        return result.returncode == 0, (result.stdout + result.stderr).strip()
    except Exception as e:
        return False, str(e)


# ============================================================
# CHECK-1 & CHECK-2: 글로벌 설정 정리
# ============================================================

def check_global_settings(dry_run: bool, auto_yes: bool) -> int:
    """
    글로벌 settings.json에서 GLOBAL_KEEP_KEYS 외 항목 처리.
    - 프로젝트에 없으면 이동 여부 질문 (CHECK-2)
    - 자동 삭제 (CHECK-1)
    반환: 변경 항목 수
    """
    print("\n" + "="*60)
    print("CHECK-1/2: 글로벌 설정 정리")
    print("="*60)

    if not GLOBAL_SETTINGS.exists():
        print(f"  [SKIP] {GLOBAL_SETTINGS} 없음")
        return 0

    global_data = load_json(GLOBAL_SETTINGS)
    project_data = load_json(PROJECT_SETTINGS)

    # 삭제 대상 키 목록
    excess_keys = [k for k in global_data if k not in GLOBAL_KEEP_KEYS]

    if not excess_keys:
        print("  [OK] 글로벌 설정에 statusLine 외 항목 없음")
        return 0

    print(f"\n  글로벌에서 발견된 추가 항목 ({len(excess_keys)}개):")
    for k in excess_keys:
        in_project = k in project_data
        status = "프로젝트에 있음" if in_project else "프로젝트에 없음 ⚠️"
        print(f"    - {k}: {status}")

    changed = 0
    keys_to_delete = []

    for key in excess_keys:
        in_project = key in project_data
        value = global_data[key]

        if not in_project:
            # CHECK-2: 프로젝트에 없으면 이동 여부 질문
            print(f"\n  [{key}] 프로젝트 설정에 없습니다.")
            move = ask(f"  → 프로젝트(.claude/settings.json)로 이동할까요?", auto_yes)
            if move:
                if not dry_run:
                    project_data = deep_set(project_data, key, value)
                    save_json(PROJECT_SETTINGS, project_data)
                print(f"  [이동] {key} → .claude/settings.json")
                changed += 1
            else:
                print(f"  [경고] {key} 설정이 삭제됩니다 (소멸)")
        else:
            print(f"\n  [{key}] 프로젝트에 이미 있음 → 글로벌에서 자동 삭제")

        keys_to_delete.append(key)

    # CHECK-1: 글로벌에서 삭제
    if keys_to_delete:
        if not dry_run:
            for key in keys_to_delete:
                global_data.pop(key, None)
            save_json(GLOBAL_SETTINGS, global_data)
        print(f"\n  [삭제] 글로벌에서 {len(keys_to_delete)}개 항목 제거: {', '.join(keys_to_delete)}")
        changed += len(keys_to_delete)

    return changed


# ============================================================
# CHECK-3: 플러그인 설치 확인
# ============================================================

def get_installed_plugins() -> set:
    """
    실제 설치된 플러그인 목록 조회.
    - ~/.claude/.skills/ 디렉터리 탐색
    - claude 명령어로 확인 시도
    """
    installed = set()

    # 방법 1: ~/.claude/.skills/ 탐색
    skills_paths = [
        Path.home() / ".claude" / ".skills",
        Path.home() / ".claude" / "plugins",
        Path.home() / ".claude" / "skills",
    ]
    for skills_dir in skills_paths:
        if skills_dir.exists():
            for item in skills_dir.iterdir():
                if item.is_dir():
                    installed.add(item.name)

    # 방법 2: claude plugin list (가능한 경우)
    ok, output = run_command(["claude", "plugin", "list"])
    if ok and output:
        for line in output.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                # "oh-my-claudecode@omc  installed" 형태
                parts = line.split()
                if parts:
                    installed.add(parts[0])
                    if "@" in parts[0]:
                        installed.add(parts[0].split("@")[0])

    return installed


def check_plugins(dry_run: bool, auto_yes: bool) -> int:
    """
    CHECK-3: 프로젝트 enabledPlugins 중 true인데 미설치인 플러그인 → 설치 여부 질문
    반환: 설치 시도 항목 수
    """
    print("\n" + "="*60)
    print("CHECK-3: 플러그인 설치 확인")
    print("="*60)

    if not PROJECT_SETTINGS.exists():
        print(f"  [SKIP] {PROJECT_SETTINGS} 없음")
        return 0

    project_data = load_json(PROJECT_SETTINGS)
    enabled_plugins = project_data.get("enabledPlugins", {})

    if not enabled_plugins:
        print("  [SKIP] enabledPlugins 항목 없음")
        return 0

    # true로 설정된 플러그인만 대상
    required = [k for k, v in enabled_plugins.items() if v is True]
    if not required:
        print("  [OK] 활성화된 플러그인 없음")
        return 0

    print(f"\n  활성화된 플러그인 ({len(required)}개) 확인 중...")
    installed = get_installed_plugins()

    if not installed:
        print("  [INFO] 설치 플러그인 목록 조회 불가 (확인 건너뜀)")
        print("         직접 확인: Claude Code > Plugins 메뉴")
        return 0

    changed = 0
    missing = []

    for plugin_key in required:
        plugin_name = plugin_key.split("@")[0]
        # 설치 여부 확인 (이름 or 전체 키 매칭)
        is_installed = (
            plugin_key in installed or
            plugin_name in installed or
            any(plugin_name in p for p in installed)
        )

        status = "✅ 설치됨" if is_installed else "❌ 미설치"
        print(f"    {plugin_key}: {status}")
        if not is_installed:
            missing.append(plugin_key)

    if not missing:
        print("\n  [OK] 모든 플러그인 설치됨")
        return 0

    print(f"\n  미설치 플러그인 {len(missing)}개 발견")
    for plugin_key in missing:
        print(f"\n  [{plugin_key}] 설치되어 있지 않습니다.")
        if dry_run:
            print(f"  [dry-run] claude plugin install {plugin_key}")
            changed += 1
            continue
        do_install = ask(f"  → 설치할까요?", auto_yes)
        if do_install:
            if not dry_run:
                ok, output = run_command(["claude", "plugin", "install", plugin_key])
                if ok:
                    print(f"  [OK] {plugin_key} 설치 완료")
                    changed += 1
                else:
                    print(f"  [WARN] 설치 실패: {output}")
                    print(f"         수동 설치: Claude Code > Plugins > {plugin_key}")
            else:
                print(f"  [dry-run] claude plugin install {plugin_key}")
                changed += 1
        else:
            print(f"  [건너뜀] {plugin_key}")

    return changed


# ============================================================
# 메인
# ============================================================

def main():
    dry_run = "--dry-run" in sys.argv
    auto_yes = "--yes" in sys.argv

    if dry_run:
        print("[DRY-RUN 모드] 실제 변경 없음\n")

    print("Claude 설정 파일 관리")
    print(f"  글로벌: {GLOBAL_SETTINGS}")
    print(f"  프로젝트: {PROJECT_SETTINGS}")

    total_changed = 0
    total_changed += check_global_settings(dry_run, auto_yes)
    total_changed += check_plugins(dry_run, auto_yes)

    print("\n" + "="*60)
    if total_changed > 0:
        suffix = " (dry-run)" if dry_run else ""
        print(f"완료: {total_changed}개 항목 처리{suffix}")
    else:
        print("완료: 변경 사항 없음")
    print("="*60)


if __name__ == "__main__":
    main()
