#!/usr/bin/env python3
"""
ooenv_settings.py

머신별 Claude 설정 자동 동기화

Usage:
    uv run python .claude/skills/ooenv/scripts/ooenv_settings.py
    uv run python .claude/skills/ooenv/scripts/ooenv_settings.py --dry-run
    uv run python .claude/skills/ooenv/scripts/ooenv_settings.py --register
"""

import argparse
import json
import platform
import sys
from pathlib import Path

# Windows 콘솔 UTF-8 인코딩 설정
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ============================================================
# Configuration
# ============================================================

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = SKILL_DIR.parent.parent.parent  # .claude/skills/ooenv/ → project root
MACHINES_JSON = SKILL_DIR / "references" / "machines.json"
HOME_DIR = Path.home()
GLOBAL_SETTINGS = HOME_DIR / ".claude" / "settings.json"
LOCAL_SETTINGS = PROJECT_ROOT / ".claude" / "settings.local.json"


# ============================================================
# Helpers
# ============================================================

def log_ok(msg: str):
    print(f"  ✅ {msg}")

def log_warn(msg: str):
    print(f"  ⚠️ {msg}")

def log_fail(msg: str):
    print(f"  ❌ {msg}")

def log_info(msg: str):
    print(f"  ℹ️ {msg}")


def load_json(path: Path) -> dict:
    """JSON 파일 로드. 없으면 빈 dict 반환."""
    if not path.exists():
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path: Path, data: dict):
    """JSON 파일 저장."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')


def get_hostname() -> str:
    """현재 컴퓨터의 hostname 반환."""
    return platform.node().lower()


def deep_merge(base: dict, override: dict) -> dict:
    """딕셔너리 깊은 병합. override가 base 위에 덮어씀."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def diff_settings(current: dict, expected: dict, prefix: str = "") -> list[str]:
    """expected에 있지만 current에 없거나 다른 항목 목록 반환."""
    diffs = []
    for key, value in expected.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if key not in current:
            diffs.append(f"누락: {full_key}")
        elif isinstance(value, dict) and isinstance(current.get(key), dict):
            diffs.extend(diff_settings(current[key], value, full_key))
        elif current.get(key) != value:
            diffs.append(f"불일치: {full_key}")
    return diffs


# ============================================================
# Core Functions
# ============================================================

def sync_settings(machine_config: dict, dry_run: bool = False) -> int:
    """머신 설정을 글로벌/로컬에 동기화. 변경 수 반환."""
    changes = 0

    # 1. 글로벌 설정 동기화
    print("\n## 글로벌 설정 (~/.claude/settings.json)\n")
    expected_global = machine_config.get("settings_global", {})

    if not expected_global:
        log_info("글로벌 설정 정의 없음 → 건너뜀")
    else:
        current_global = load_json(GLOBAL_SETTINGS)

        # 글로벌에는 statusLine만 있어야 함
        extra_keys = [k for k in current_global if k not in expected_global]
        if extra_keys:
            log_warn(f"글로벌에 불필요한 항목: {', '.join(extra_keys)}")
            if not dry_run:
                for k in extra_keys:
                    del current_global[k]
                changes += len(extra_keys)
                save_json(GLOBAL_SETTINGS, current_global)
                log_ok("글로벌 불필요 항목 제거 완료")

        # expected 항목 확인
        diffs = diff_settings(current_global, expected_global)
        if diffs:
            for d in diffs:
                log_warn(d)
            if not dry_run:
                merged = deep_merge(current_global, expected_global)
                # 불필요 항목 제거 후 expected만 남김
                final = {k: merged[k] for k in expected_global if k in merged}
                save_json(GLOBAL_SETTINGS, final)
                log_ok("글로벌 설정 업데이트 완료")
                changes += len(diffs)
        else:
            log_ok("글로벌 설정 정상")

    # 2. 로컬 설정 동기화
    print("\n## 로컬 설정 (.claude/settings.local.json)\n")
    expected_local = machine_config.get("settings_local", {})

    if not expected_local:
        log_info("로컬 설정 정의 없음 → 건너뜀")
    else:
        current_local = load_json(LOCAL_SETTINGS)
        diffs = diff_settings(current_local, expected_local)

        if diffs:
            for d in diffs:
                log_warn(d)
            if not dry_run:
                merged = deep_merge(current_local, expected_local)
                save_json(LOCAL_SETTINGS, merged)
                log_ok("로컬 설정 업데이트 완료")
                changes += len(diffs)
        else:
            log_ok("로컬 설정 정상")

    return changes


def register_machine(hostname: str) -> dict:
    """새 머신을 대화형으로 등록."""
    print(f"\n## 새 머신 등록: {hostname}\n")

    alias = input("  별칭 (예: 데스크탑, 노트북): ").strip() or hostname
    user = input(f"  사용자명 [{Path.home().name}]: ").strip() or Path.home().name
    project_root = input(f"  프로젝트 경로 [{PROJECT_ROOT}]: ").strip() or str(PROJECT_ROOT)

    # statusLine
    hud_path = HOME_DIR / ".claude" / "hud" / "omc-hud.mjs"
    hud_cmd = f"node {str(hud_path).replace(chr(92), '/')}"
    use_hud = input(f"  statusLine HUD 사용? [{hud_cmd}] (y/n) [y]: ").strip().lower()

    settings_global = {}
    if use_hud != 'n':
        settings_global["statusLine"] = {
            "type": "command",
            "command": hud_cmd
        }

    # TEMP/TMP
    tmp_dir = PROJECT_ROOT / "tmp"
    tmp_path = input(f"  TEMP/TMP 경로 [{tmp_dir}]: ").strip() or str(tmp_dir)

    settings_local = {
        "env": {
            "TEMP": tmp_path.replace('/', '\\'),
            "TMP": tmp_path.replace('/', '\\')
        }
    }

    machine_config = {
        "alias": alias,
        "user": user,
        "project_root": project_root.replace('/', '\\'),
        "settings_global": settings_global,
        "settings_local": settings_local
    }

    # machines.json에 저장
    machines = load_json(MACHINES_JSON)
    machines[hostname] = machine_config
    save_json(MACHINES_JSON, machines)
    log_ok(f"머신 '{hostname}' ({alias}) 등록 완료")

    return machine_config


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="머신별 Claude 설정 동기화")
    parser.add_argument("--dry-run", action="store_true", help="변경 없이 확인만")
    parser.add_argument("--register", action="store_true", help="현재 머신 강제 등록")
    parser.add_argument("--show", action="store_true", help="현재 머신 설정 표시")
    args = parser.parse_args()

    hostname = get_hostname()
    print(f"# ooenv settings - 머신별 설정 동기화\n")
    print(f"  hostname: {hostname}")
    print(f"  project:  {PROJECT_ROOT}")

    # machines.json 로드
    machines = load_json(MACHINES_JSON)

    if not machines:
        log_fail(f"machines.json 없음: {MACHINES_JSON}")
        print("  → --register로 현재 머신을 등록하세요")
        sys.exit(1)

    # 머신 찾기
    machine_config = machines.get(hostname)

    if args.show:
        if machine_config:
            print(f"\n## 현재 머신 설정 ({hostname})\n")
            print(json.dumps(machine_config, indent=2, ensure_ascii=False))
        else:
            log_warn(f"'{hostname}'은 미등록 머신입니다")
            print(f"\n등록된 머신: {', '.join(machines.keys())}")
        return

    if args.register or not machine_config:
        if not machine_config:
            log_warn(f"'{hostname}'은 등록되지 않은 머신입니다")
        machine_config = register_machine(hostname)

    # 설정 동기화
    mode = "(dry-run) " if args.dry_run else ""
    print(f"\n# {mode}설정 동기화 시작 [{hostname} / {machine_config.get('alias', '')}]")

    changes = sync_settings(machine_config, dry_run=args.dry_run)

    # 결과
    print(f"\n# 결과: {changes}건 {'확인됨 (dry-run)' if args.dry_run else '변경됨'}")

    if args.dry_run and changes > 0:
        print("  → --dry-run 제거 후 재실행하면 자동 적용됩니다")


if __name__ == "__main__":
    main()
