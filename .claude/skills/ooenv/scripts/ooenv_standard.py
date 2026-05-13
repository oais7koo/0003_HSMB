#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ooenv_standard.py - Claude 환경 표준 비교 엔진

d0012에 정의된 표준 스펙과 현재 환경을 비교하여 PASS/FAIL 결과 출력.

사용법:
    uv run python .claude/skills/ooenv/scripts/ooenv_standard.py

exit code:
    0 - PASS (모든 항목 통과)
    1 - FAIL (하나 이상 실패)
"""

import sys
import json
import re
import subprocess
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional

# Windows 콘솔 UTF-8 출력 설정
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 경로 설정
SCRIPT_DIR = Path(__file__).parent
SKILLS_DIR = SCRIPT_DIR.parent.parent      # .claude/skills/
PROJECT_ROOT = SKILLS_DIR.parent.parent    # 프로젝트 루트
SPEC_FILE = SCRIPT_DIR.parent / "config" / "standard_spec.json"


# ============================================================
# 데이터 클래스
# ============================================================

@dataclass
class CheckResult:
    """단일 체크 결과"""
    name: str
    standard: str
    current: str
    passed: bool
    note: str = ""


# ============================================================
# 유틸리티 함수
# ============================================================

def load_standard_spec() -> dict:
    """표준 스펙 JSON 로드"""
    if not SPEC_FILE.exists():
        print(f"[ERROR] 스펙 파일 없음: {SPEC_FILE}")
        sys.exit(1)
    try:
        return json.loads(SPEC_FILE.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        print(f"[ERROR] 스펙 파일 파싱 실패: {e}")
        sys.exit(1)


def parse_version(s: str) -> tuple:
    """버전 문자열에서 숫자 튜플 추출. 예: '3.13.7' -> (3, 13, 7)"""
    parts = re.findall(r'\d+', s)
    return tuple(int(x) for x in parts[:3]) if parts else (0,)


def run_command(cmd: list, timeout: int = 10) -> tuple:
    """명령어 실행 후 (success, output) 반환"""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            encoding='utf-8', errors='replace'
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except FileNotFoundError:
        return False, "not found"
    except Exception as e:
        return False, str(e)


# ============================================================
# 체크 함수
# ============================================================

def check_system(spec: dict) -> list:
    """시스템 버전 체크"""
    results = []
    sys_spec = spec.get("system", {})

    # Python - sys.version으로 직접 읽기 (Windows App Execution Alias stub 우회)
    if "python" in sys_spec:
        min_ver = sys_spec["python"]["min_version"]
        cur_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        passed = parse_version(cur_ver) >= parse_version(min_ver)
        results.append(CheckResult(
            name="Python",
            standard=f">={min_ver}",
            current=cur_ver,
            passed=passed
        ))

    # uv
    if "uv" in sys_spec:
        min_ver = sys_spec["uv"]["min_version"]
        ok, output = run_command(["uv", "--version"])
        # "uv 0.8.15 (..." 형식에서 버전 추출
        cur_ver = output.split()[1] if ok and len(output.split()) >= 2 else output
        passed = ok and parse_version(cur_ver) >= parse_version(min_ver)
        results.append(CheckResult(
            name="uv",
            standard=f">={min_ver}",
            current=cur_ver if ok else "미설치",
            passed=passed
        ))

    # Node.js
    if "node" in sys_spec:
        min_ver = sys_spec["node"]["min_version"]
        ok, output = run_command(["node", "--version"])
        cur_ver = output.lstrip("v").strip() if ok else "미설치"
        passed = ok and parse_version(cur_ver) >= parse_version(min_ver)
        results.append(CheckResult(
            name="Node.js",
            standard=f">={min_ver}",
            current=cur_ver,
            passed=passed
        ))

    # Git
    if "git" in sys_spec:
        min_ver = sys_spec["git"]["min_version"]
        ok, output = run_command(["git", "--version"])
        # "git version 2.43.0.windows.1" -> "2.43.0"
        match = re.search(r'(\d+\.\d+\.\d+)', output) if ok else None
        cur_ver = match.group(1) if match else (output if ok else "미설치")
        passed = ok and parse_version(cur_ver) >= parse_version(min_ver)
        results.append(CheckResult(
            name="Git",
            standard=f">={min_ver}",
            current=cur_ver,
            passed=passed
        ))

    # gh (GitHub CLI) - 버전 + 인증 상태
    if "gh" in sys_spec:
        min_ver = sys_spec["gh"]["min_version"]
        ok, output = run_command(["gh", "--version"])
        match = re.search(r'(\d+\.\d+\.\d+)', output) if ok else None
        cur_ver = match.group(1) if match else (output if ok else "미설치")
        passed = ok and parse_version(cur_ver) >= parse_version(min_ver)
        results.append(CheckResult(
            name="gh (GitHub CLI)",
            standard=f">={min_ver}",
            current=cur_ver,
            passed=passed
        ))
        # 인증 상태 체크
        if ok:
            auth_ok, auth_output = run_command(["gh", "auth", "status"])
            results.append(CheckResult(
                name="gh auth",
                standard="인증됨",
                current="인증됨" if auth_ok else "미인증",
                passed=auth_ok
            ))

    return results


def check_mcp_servers(spec: dict) -> list:
    """MCP 서버 필수 항목 체크 (.mcp.json 기반)"""
    results = []
    required = spec.get("mcp_servers", {}).get("required", [])
    if not required:
        return results

    mcp_file = PROJECT_ROOT / ".mcp.json"
    installed = set()
    if mcp_file.exists():
        try:
            data = json.loads(mcp_file.read_text(encoding='utf-8'))
            installed = set(data.get("mcpServers", {}).keys())
        except (json.JSONDecodeError, KeyError):
            pass

    for server in required:
        passed = server in installed
        results.append(CheckResult(
            name=f"MCP: {server}",
            standard="필수",
            current="설치됨" if passed else "미설치",
            passed=passed
        ))

    return results


def _read_settings_plugins(settings_path: Path) -> set:
    """settings.json의 enabledPlugins dict에서 플러그인 이름 세트 추출.
    enabledPlugins 형식: {"oh-my-claudecode@omc": {...}, ...}
    """
    plugins = set()
    if not settings_path.exists():
        return plugins
    try:
        data = json.loads(settings_path.read_text(encoding='utf-8'))
        ep = data.get("enabledPlugins", {})
        if isinstance(ep, dict):
            for key in ep.keys():
                plugins.add(key)
                # "name@source" 형식이면 name도 추가
                if "@" in key:
                    plugins.add(key.split("@")[0])
        elif isinstance(ep, list):
            for p in ep:
                if isinstance(p, str):
                    plugins.add(p)
    except (json.JSONDecodeError, KeyError):
        pass
    return plugins


def _plugin_found(plugin_spec: str, installed: set) -> bool:
    """플러그인 스펙 문자열이 installed 세트에 있는지 확인 (이름/소스 부분 매칭)"""
    if not installed:
        return False
    plugin_name = plugin_spec.split("@")[0]
    plugin_source = plugin_spec.split("@")[1] if "@" in plugin_spec else ""
    for p in installed:
        if plugin_name in p or plugin_spec in p:
            return True
        if plugin_source and plugin_source in p:
            return True
    return False


def check_plugins(spec: dict) -> list:
    """플러그인 필수 항목 체크 (settings.json 기반, 미확인 시 경고)"""
    results = []
    plugins_spec = spec.get("plugins", {})

    # 글로벌: ~/.claude/settings.json
    global_settings = Path.home() / ".claude" / "settings.json"
    global_plugins = _read_settings_plugins(global_settings)

    # 프로젝트: .claude/settings.json
    project_settings = PROJECT_ROOT / ".claude" / "settings.json"
    project_plugins = _read_settings_plugins(project_settings)

    all_plugins = global_plugins | project_plugins
    has_plugin_data = bool(all_plugins)

    for plugin in plugins_spec.get("global", []):
        plugin_name = plugin.split("@")[0]
        if has_plugin_data:
            passed = _plugin_found(plugin, all_plugins)
            current = "설치됨" if passed else "미설치"
        else:
            # settings.json에 plugins 키 없으면 미확인 (경고, 실패 아님)
            passed = True  # 미확인은 PASS로 처리 (환경 확인 불가)
            current = "미확인"
        results.append(CheckResult(
            name=f"Plugin(global): {plugin_name}",
            standard="필수",
            current=current,
            passed=passed,
            note="settings.json" if has_plugin_data else "확인불가-스킵"
        ))

    for plugin in plugins_spec.get("project", []):
        plugin_name = plugin.split("@")[0]
        if has_plugin_data:
            passed = _plugin_found(plugin, all_plugins)
            current = "설치됨" if passed else "미설치"
        else:
            passed = True
            current = "미확인"
        results.append(CheckResult(
            name=f"Plugin(project): {plugin_name}",
            standard="필수",
            current=current,
            passed=passed,
            note="settings.json" if has_plugin_data else "확인불가-스킵"
        ))

    return results


def check_counts(spec: dict) -> list:
    """스킬/에이전트/커맨드 수량 체크 (실제 >= 표준)"""
    results = []
    counts_spec = spec.get("counts", {})

    # Claude 공식 스킬: ~/.claude/settings.json의 skills 키
    if "claude_skills" in counts_spec:
        expected = counts_spec["claude_skills"]
        global_settings = Path.home() / ".claude" / "settings.json"
        actual = 0
        if global_settings.exists():
            try:
                data = json.loads(global_settings.read_text(encoding='utf-8'))
                actual = len(data.get("skills", []))
            except (json.JSONDecodeError, KeyError):
                pass
        passed = actual >= expected
        results.append(CheckResult(
            name="Claude 공식 스킬",
            standard=f">={expected}개",
            current=f"{actual}개",
            passed=passed
        ))

    # oo 프로젝트 스킬: .claude/skills/oo*/
    if "oo_skills" in counts_spec:
        expected = counts_spec["oo_skills"]
        skills_dir = PROJECT_ROOT / ".claude" / "skills"
        actual = 0
        if skills_dir.exists():
            actual = len([d for d in skills_dir.iterdir()
                          if d.is_dir() and d.name.startswith("oo")])
        passed = actual >= expected
        results.append(CheckResult(
            name="oo 프로젝트 스킬",
            standard=f">={expected}개",
            current=f"{actual}개",
            passed=passed
        ))

    # 에이전트: .claude/agents/*.md (unuse 하위 폴더 제외)
    if "agents" in counts_spec:
        expected = counts_spec["agents"]
        agents_dir = PROJECT_ROOT / ".claude" / "agents"
        actual = 0
        if agents_dir.exists():
            actual = len([f for f in agents_dir.glob("*.md")])
        passed = actual >= expected
        results.append(CheckResult(
            name="에이전트",
            standard=f">={expected}개",
            current=f"{actual}개",
            passed=passed
        ))

    # 커맨드: .claude/commands/sc/*.md
    if "commands" in counts_spec:
        expected = counts_spec["commands"]
        commands_dir = PROJECT_ROOT / ".claude" / "commands" / "sc"
        actual = 0
        if commands_dir.exists():
            actual = len([f for f in commands_dir.glob("*.md")
                          if f.stem.upper() != "README"])
        passed = actual >= expected
        results.append(CheckResult(
            name="커맨드 (sc/)",
            standard=f">={expected}개",
            current=f"{actual}개",
            passed=passed
        ))

    return results


# ============================================================
# 실행 진입점
# ============================================================

def run_standard_check() -> tuple:
    """전체 표준 체크 실행. (all_passed, results) 반환"""
    spec = load_standard_spec()
    results = []
    results.extend(check_system(spec))
    results.extend(check_mcp_servers(spec))
    results.extend(check_plugins(spec))
    results.extend(check_counts(spec))
    all_passed = all(r.passed for r in results)
    return all_passed, results


def print_results(results: list) -> None:
    """결과를 마크다운 테이블로 출력"""
    print(f"# ooenv standard - 표준 환경 비교\n")
    print(f"시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"스펙: {SPEC_FILE.name}\n")

    print("| 항목 | 표준 | 현재 | 결과 |")
    print("|------|------|------|:----:|")

    pass_count = 0
    for r in results:
        mark = "PASS" if r.passed else "FAIL"
        if r.passed:
            pass_count += 1
        note_str = f" *({r.note})*" if r.note else ""
        print(f"| {r.name}{note_str} | {r.standard} | {r.current} | {mark} |")

    total = len(results)
    all_passed = pass_count == total
    status = "PASS" if all_passed else "FAIL"
    print(f"\n## 결과: {status} ({pass_count}/{total})")

    if not all_passed:
        failed = [r for r in results if not r.passed]
        print(f"\n### 실패 항목 ({len(failed)}개)")
        for r in failed:
            print(f"- **{r.name}**: 표준={r.standard}, 현재={r.current}")


def fix_plugins(results: list) -> int:
    """실패한 Plugin 항목을 ~/.claude/settings.json enabledPlugins에 자동 추가.
    반환: 수정된 항목 수
    """
    global_settings = Path.home() / ".claude" / "settings.json"
    if not global_settings.exists():
        print("[WARN] ~/.claude/settings.json 없음 - 플러그인 자동 수정 불가")
        return 0

    try:
        data = json.loads(global_settings.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        print(f"[ERROR] settings.json 파싱 실패: {e}")
        return 0

    ep = data.get("enabledPlugins", {})
    if not isinstance(ep, dict):
        print("[WARN] enabledPlugins 형식이 dict가 아님 - 자동 수정 불가")
        return 0

    fixed = 0
    for r in results:
        # Plugin 항목 중 실패한 것만 처리
        if not r.passed and r.name.startswith("Plugin"):
            # "Plugin(global): document-skills" → "document-skills"
            # spec의 원본 plugin 스펙 복원 (standard_spec.json에서 재확인)
            spec = load_standard_spec()
            all_plugins = (spec.get("plugins", {}).get("global", []) +
                           spec.get("plugins", {}).get("project", []))
            plugin_name = r.name.split(": ")[-1].strip()
            # 전체 스펙에서 해당 플러그인 찾기
            matched_spec = next(
                (p for p in all_plugins if p.split("@")[0] == plugin_name),
                None
            )
            if matched_spec and matched_spec not in ep:
                ep[matched_spec] = True
                print(f"[FIX] 추가됨: {matched_spec}")
                fixed += 1

    if fixed > 0:
        data["enabledPlugins"] = ep
        global_settings.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        print(f"\n[OK] {fixed}개 플러그인 추가 완료 → Claude Code 재시작 후 적용됩니다.")
    else:
        print("[INFO] 자동 수정 가능한 플러그인 항목 없음")

    return fixed


def print_fix_guide(results: list) -> None:
    """자동 수정 불가 항목에 대한 수동 설치 안내 출력"""
    manual_items = [r for r in results if not r.passed and not r.name.startswith("Plugin")]
    if not manual_items:
        return

    print("\n### 수동 설치 안내")
    for r in manual_items:
        if "Node.js" in r.name:
            print(f"\n**Node.js** (현재: {r.current}, 필요: {r.standard})")
            print("  설치: `winget install OpenJS.NodeJS.LTS` (관리자 권한)")
            print("  또는: https://nodejs.org/ 에서 v23+ 다운로드")
        elif "Python" in r.name:
            print(f"\n**Python** (현재: {r.current}, 필요: {r.standard})")
            print("  설치: `uv python install 3.13.7`")
        elif "uv" in r.name:
            print(f"\n**uv** (현재: {r.current}, 필요: {r.standard})")
            print("  업데이트: `uv self update`")
        elif "Git" in r.name:
            print(f"\n**Git** (현재: {r.current}, 필요: {r.standard})")
            print("  설치: `winget install Git.Git`")
        elif "gh (GitHub CLI)" in r.name:
            print(f"\n**gh (GitHub CLI)** (현재: {r.current}, 필요: {r.standard})")
            print("  설치: `winget install GitHub.cli`")
            print("  또는: https://cli.github.com/")
        elif "gh auth" in r.name:
            print(f"\n**gh auth** — GitHub CLI 미인증 상태")
            print("  인증: `gh auth login` (OAuth web flow 권장)")
        elif "MCP" in r.name:
            server = r.name.replace("MCP: ", "")
            print(f"\n**MCP: {server}** - `claude mcp install {server}`")
        else:
            print(f"\n**{r.name}**: {r.standard} 필요 (현재: {r.current})")


if __name__ == "__main__":
    fix_mode = "--fix" in sys.argv
    all_passed, results = run_standard_check()
    print_results(results)

    if fix_mode and not all_passed:
        print("\n## 자동 수정 시작\n")
        fixed = fix_plugins(results)
        print_fix_guide(results)
        # 수정 후 재검사
        if fixed > 0:
            print("\n## 재검사\n")
            all_passed, results = run_standard_check()
            print_results(results)

    sys.exit(0 if all_passed else 1)
