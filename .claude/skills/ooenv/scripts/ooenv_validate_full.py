"""
ooenv validate --full: 스킬 참조 정합성 검증 스크립트

oo*.md 스킬 파일을 스캔하여 참조된 에이전트/커맨드/MCP를 추출하고
현재 환경과 교차 검증합니다.

검증 대상:
1. 에이전트: .claude/agents/, .claude/agents/ 존재 확인
2. 커맨드: .claude/commands/sc/, .claude/commands/ 존재 확인
3. MCP: .mcp.json 설정 존재 확인
"""

import re
import sys
import io
import json
import argparse
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# Windows 콘솔 UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


@dataclass
class ValidationResult:
    """검증 결과"""
    skill_file: str
    agents_found: list = field(default_factory=list)
    agents_missing: list = field(default_factory=list)
    commands_found: list = field(default_factory=list)
    commands_missing: list = field(default_factory=list)
    mcps_found: list = field(default_factory=list)
    mcps_missing: list = field(default_factory=list)


@dataclass
class PluginResult:
    """플러그인 검증 결과"""
    installed: list = field(default_factory=list)
    missing: list = field(default_factory=list)


@dataclass
class ClaudeInstallResult:
    """Claude Code 설치 상태"""
    found: bool = False
    path: str = ""
    is_native: bool = False
    npm_duplicate: bool = False
    version: str = ""


@dataclass
class EnvironmentInfo:
    """현재 환경 정보"""
    agents_claude: set = field(default_factory=set)    # .claude/agents/ 에이전트
    commands_claude: set = field(default_factory=set)   # .claude/commands/sc/ 커맨드
    mcp_servers: set = field(default_factory=set)       # .mcp.json MCP 서버
    enabled_plugins: dict = field(default_factory=dict) # settings.json enabledPlugins


# 필수 플러그인 (키 prefix로 매칭)
# NOTE: document-skills 제거 (anthropic-agent-skills 마켓플레이스에 더 이상 없음, 2026-05-03)
REQUIRED_PLUGINS = [
    'oh-my-claudecode',
    'context7',
    'superpowers',
    'codex',
]


def validate_claude_install() -> ClaudeInstallResult:
    """Claude Code 설치 상태 검증 (native vs npm)"""
    result = ClaudeInstallResult()

    # 1. where claude로 경로 확인
    try:
        proc = subprocess.run(
            ['where', 'claude'], capture_output=True, text=True, timeout=5
        )
        if proc.returncode == 0 and proc.stdout.strip():
            paths = proc.stdout.strip().splitlines()
            result.found = True
            result.path = paths[0].strip()
            # .local\bin 포함 → native, node_modules/npm 포함 → npm global
            path_lower = result.path.lower()
            if '.local' in path_lower and 'bin' in path_lower:
                result.is_native = True
            elif 'node_modules' in path_lower or 'npm' in path_lower:
                result.is_native = False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # 2. claude --version 확인
    if result.found:
        try:
            proc = subprocess.run(
                ['claude', '--version'], capture_output=True, text=True, timeout=10
            )
            if proc.returncode == 0 and proc.stdout.strip():
                result.version = proc.stdout.strip().splitlines()[0]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    # 3. npm global 중복 확인
    try:
        proc = subprocess.run(
            ['npm', 'list', '-g', '@anthropic-ai/claude-code', '--depth=0'],
            capture_output=True, text=True, timeout=10
        )
        if proc.returncode == 0 and '@anthropic-ai/claude-code' in proc.stdout:
            result.npm_duplicate = True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return result


def validate_plugins(env: EnvironmentInfo) -> PluginResult:
    """필수 플러그인 설치 여부 검증"""
    result = PluginResult()
    for required in REQUIRED_PLUGINS:
        found = False
        for key, enabled in env.enabled_plugins.items():
            if key.startswith(required) and enabled:
                found = True
                result.installed.append(f"{required} ({key})")
                break
        if not found:
            # 등록은 되어 있지만 비활성인 경우 구분
            for key, enabled in env.enabled_plugins.items():
                if key.startswith(required) and not enabled:
                    result.missing.append(f"{required} (비활성: {key})")
                    found = True
                    break
            if not found:
                result.missing.append(f"{required} (미설치)")
    return result


def load_environment(project_root: Path) -> EnvironmentInfo:
    """현재 환경 정보 로드"""
    env = EnvironmentInfo()

    # .claude/agents/ 에이전트 로드
    claude_agents = project_root / '.claude' / 'agents'
    if claude_agents.exists():
        for f in claude_agents.glob('*.md'):
            env.agents_claude.add(f.stem)

    # .claude/commands/sc/ 커맨드 로드 (활성 + unuse/ 비활성 모두 known으로 처리)
    claude_commands = project_root / '.claude' / 'commands' / 'sc'
    if claude_commands.exists():
        for f in claude_commands.glob('*.md'):
            if f.stem != 'README':
                env.commands_claude.add(f.stem)
        for f in (claude_commands / 'unuse').glob('*.md'):
            if f.stem != 'README':
                env.commands_claude.add(f.stem)

    # .claude/settings.json enabledPlugins 로드
    settings_json = project_root / '.claude' / 'settings.json'
    if settings_json.exists():
        try:
            data = json.loads(settings_json.read_text(encoding='utf-8'))
            env.enabled_plugins = data.get('enabledPlugins', {})
        except (json.JSONDecodeError, KeyError):
            pass

    # .mcp.json MCP 서버 로드
    mcp_json = project_root / '.mcp.json'
    if mcp_json.exists():
        try:
            data = json.loads(mcp_json.read_text(encoding='utf-8'))
            if 'mcpServers' in data:
                env.mcp_servers = set(data['mcpServers'].keys())
        except (json.JSONDecodeError, KeyError):
            pass

    return env


def extract_agents(content: str) -> set:
    """스킬 파일에서 참조된 에이전트 추출"""
    agents = set()

    # 패턴 1: Task(subagent_type="xxx" or subagent_type='xxx')
    pattern1 = r'subagent_type\s*=\s*["\']([^"\']+)["\']'
    for match in re.finditer(pattern1, content):
        agents.add(match.group(1))

    # 패턴 2: 테이블 첫 번째 컬럼에서 에이전트 추출 (행 시작 | 바로 다음 컬럼만)
    # 예: | task-executor | ... |  <- 첫 컬럼만 추출 (nvidia-smi 등 3번째 컬럼 오탐 방지)
    # 조건: 하이픈을 포함하고 영문 소문자/숫자/하이픈만으로 구성된 두 단어 이상
    table_pattern = r'^\|\s*`?([a-z][a-z0-9]*(?:-[a-z][a-z0-9]*)+)`?\s*\|'
    for match in re.finditer(table_pattern, content, re.MULTILINE):
        name = match.group(1)
        agents.add(name)

    # 패턴 3: .claude/agents/xxx.md 참조
    pattern3 = r'.claude/agents/([^/\s\)]+)\.md'
    for match in re.finditer(pattern3, content):
        agents.add(match.group(1))

    # 패턴 4: .claude/agents/xxx.md 참조
    pattern4 = r'\.claude/agents/([^/\s\)]+)\.md'
    for match in re.finditer(pattern4, content):
        agents.add(match.group(1))

    # 내장 에이전트 및 플레이스홀더 제외
    builtin = {'Explore', 'explore', 'general-purpose', 'Plan'}
    # 패키지 이름 제외 (python-docx, python-pptx, mermaid-cli 등은 에이전트가 아님)
    placeholders = {'xxx', 'name', '[name]', 'example', 'sample', 'sync-agents',
                    'sync-skills', 'python-pptx', 'python-docx', 'mermaid-cli',
                    'ooqa', '*',
                    # CLI/MCP 패키지명 (에이전트가 아님)
                    'claude-code',
                    'oh-my-claude-sisyphus', 'brave-search', 'puppeteer-mcp-server',
                    'figma-mcp', 'server-brave-search', 'server-puppeteer',
                    # CSS/HTML 클래스명 (에이전트가 아님)
                    'section-title', 'sub-title', 'main-content', 'nav-bar',
                    # ooskill 서브명령어 (에이전트가 아님)
                    'run-update-ref',
                    }  # ooqa는 파일명에 하이픈 없음, *는 와일드카드
    agents = agents - builtin - placeholders

    # [xxx] 형태의 플레이스홀더 제거
    # 와일드카드(*) 포함 항목 제거
    agents = {a for a in agents if not (a.startswith('[') or a.endswith(']') or '*' in a)}

    return agents


def extract_commands(content: str) -> set:
    """스킬 파일에서 참조된 커맨드 추출"""
    commands = set()

    # 패턴 1: .claude/commands/sc/xxx.md 참조
    pattern1 = r'.claude/commands/sc/([^/\s\)]+)\.md'
    for match in re.finditer(pattern1, content):
        name = match.group(1)
        if name != 'README':
            commands.add(name)

    # 패턴 2: .claude/commands/xxx.md 참조
    pattern2 = r'\.claude/commands/([^/\s\)]+)\.md'
    for match in re.finditer(pattern2, content):
        commands.add(match.group(1))

    # 플레이스홀더 및 와일드카드 제외
    placeholders = {'xxx', '*', 'example', 'sample', '[name]'}
    commands = commands - placeholders
    commands = {c for c in commands if not (c.startswith('[') or c.endswith(']') or '*' in c)}

    return commands


def extract_mcps(content: str) -> set:
    """스킬 파일에서 참조된 MCP 서버 추출"""
    mcps = set()

    # 패턴 1: mcp__xxx__ 형태
    pattern1 = r'mcp__([a-z][a-z0-9_-]*)__'
    for match in re.finditer(pattern1, content):
        mcps.add(match.group(1))

    # 플레이스홀더 제외
    placeholders = {'xxx', 'example', 'sample'}
    mcps = mcps - placeholders

    return mcps


def validate_skill(skill_path: Path, env: EnvironmentInfo) -> ValidationResult:
    """단일 스킬 파일 검증"""
    content = skill_path.read_text(encoding='utf-8')
    result = ValidationResult(skill_file=skill_path.name)

    # 에이전트 검증
    agents = extract_agents(content)
    all_agents = env.agents_claude
    # 에이전트 이름 정규화 (하이픈/언더스코어 변환, 하이픈 제거)
    all_agents_normalized = {a.replace('_', '-') for a in all_agents}
    all_agents_normalized |= {a.replace('-', '_') for a in all_agents}
    all_agents_normalized |= {a.replace('-', '') for a in all_agents}  # oo-qa -> ooqa
    all_agents |= all_agents_normalized

    for agent in agents:
        # 플러그인 제공 에이전트 예외 처리 (codex:rescue 등 plugin:name 형식)
        if ':' in agent:
            result.agents_found.append(agent + ' (plugin)')
            continue
        agent_normalized = agent.replace('_', '-')
        agent_no_hyphen = agent.replace('-', '')
        # oo- 접두사 변형 체크
        agent_with_oo = f"oo-{agent}"
        if (agent in all_agents or agent_normalized in all_agents or
            agent_no_hyphen in all_agents or agent_with_oo in all_agents):
            result.agents_found.append(agent)
        else:
            result.agents_missing.append(agent)

    # 커맨드 검증
    commands = extract_commands(content)
    all_commands = env.commands_claude
    for cmd in commands:
        if cmd in all_commands:
            result.commands_found.append(cmd)
        else:
            result.commands_missing.append(cmd)

    # MCP 검증
    mcps = extract_mcps(content)
    for mcp in mcps:
        # MCP 이름 정규화
        mcp_normalized = mcp.replace('_', '-')
        # 여러 형태로 검색
        if mcp in env.mcp_servers or mcp_normalized in env.mcp_servers:
            result.mcps_found.append(mcp)
        else:
            # 내장 도구 (Claude Code 기본 제공)
            builtin_tools = ['grep', 'glob', 'read', 'write', 'edit', 'bash', 'ide']
            # 선택적 MCP (설치되지 않아도 경고만)
            # github: Claude 플러그인 또는 내장 환경으로 제공 (PLUGIN_REPLACED_MCP_SERVERS 참조)
            optional_mcps = ['serena', 'playwright', 'context7', 'magic', 'github', 'filesystem']
            if mcp.lower() in builtin_tools:
                result.mcps_found.append(mcp + ' (builtin)')
            elif mcp.lower() in optional_mcps:
                result.mcps_found.append(mcp + ' (optional)')
            else:
                result.mcps_missing.append(mcp)

    return result


def validate_all(project_root: Path, verbose: bool = False) -> list:
    """모든 oo*.md 스킬 검증"""
    env = load_environment(project_root)
    results = []

    skills_dir = project_root / '.claude' / 'skills'
    skill_files = []
    if skills_dir.exists():
        for d in sorted(skills_dir.iterdir()):
            if d.is_dir() and d.name.startswith('oo'):
                skill_md = d / 'SKILL.md'
                if skill_md.exists():
                    skill_files.append(skill_md)

    print("=" * 60)
    print("ooenv validate --full: 스킬 참조 정합성 검증")
    print("=" * 60)
    print(f"\n스킬 파일 수: {len(skill_files)}")
    print(f"환경 에이전트 (.claude/agents/): {len(env.agents_claude)}개")
    print(f"환경 커맨드 (.claude/commands/sc/): {len(env.commands_claude)}개")
    print(f"MCP 서버: {len(env.mcp_servers)}개 - {', '.join(env.mcp_servers) if env.mcp_servers else '없음'}")
    print(f"플러그인: {len(env.enabled_plugins)}개 등록")
    print("-" * 60)

    # Claude Code 설치 검증
    claude_result = validate_claude_install()
    print("\n[Claude Code 설치 검증]")
    if not claude_result.found:
        print("  ❌ Claude Code 미설치 (where claude 실패)")
    else:
        if claude_result.version:
            print(f"  버전: {claude_result.version}")
        print(f"  경로: {claude_result.path}")
        if claude_result.is_native:
            print("  ✅ Native 설치 (.local/bin)")
        else:
            print("  ⚠️ npm global 설치 → native 설치 권장")
        if claude_result.npm_duplicate:
            print("  ❌ npm global 중복 감지 → npm uninstall -g @anthropic-ai/claude-code 권고")
        elif claude_result.is_native:
            print("  ✅ npm global 중복 없음")
    print("-" * 60)

    # 플러그인 검증
    plugin_result = validate_plugins(env)
    print("\n[플러그인 검증]")
    for p in plugin_result.installed:
        print(f"  ✅ {p}")
    for p in plugin_result.missing:
        print(f"  ❌ {p}")
    if not plugin_result.missing:
        print("  → 필수 플러그인 모두 정상")
    print("-" * 60)

    for skill_path in skill_files:
        result = validate_skill(skill_path, env)
        results.append(result)

        has_issues = result.agents_missing or result.commands_missing or result.mcps_missing

        if verbose or has_issues:
            print(f"\n[{result.skill_file}]")

            if result.agents_found and verbose:
                print(f"  ✅ 에이전트: {', '.join(result.agents_found)}")
            if result.agents_missing:
                print(f"  ❌ 에이전트 누락: {', '.join(result.agents_missing)}")

            if result.commands_found and verbose:
                print(f"  ✅ 커맨드: {', '.join(result.commands_found)}")
            if result.commands_missing:
                print(f"  ❌ 커맨드 누락: {', '.join(result.commands_missing)}")

            if result.mcps_found and verbose:
                print(f"  ✅ MCP: {', '.join(result.mcps_found)}")
            if result.mcps_missing:
                print(f"  ❌ MCP 누락: {', '.join(result.mcps_missing)}")

    return results, plugin_result, claude_result


def print_summary(results: list, plugin_result: PluginResult = None,
                  claude_result: ClaudeInstallResult = None):
    """결과 요약 출력"""
    total_agents_missing = sum(len(r.agents_missing) for r in results)
    total_commands_missing = sum(len(r.commands_missing) for r in results)
    total_mcps_missing = sum(len(r.mcps_missing) for r in results)
    total_plugins_missing = len(plugin_result.missing) if plugin_result else 0
    claude_issues = 0
    if claude_result:
        if not claude_result.found:
            claude_issues += 1
        if not claude_result.is_native and claude_result.found:
            claude_issues += 1
        if claude_result.npm_duplicate:
            claude_issues += 1

    print("\n" + "=" * 60)
    print("검증 결과 요약")
    print("=" * 60)

    all_pass = (total_agents_missing == 0 and total_commands_missing == 0
                and total_mcps_missing == 0 and total_plugins_missing == 0
                and claude_issues == 0)

    if all_pass:
        print("✅ 모든 참조가 유효합니다!")
    else:
        if total_agents_missing:
            print(f"❌ 에이전트 누락: {total_agents_missing}건")
        if total_commands_missing:
            print(f"❌ 커맨드 누락: {total_commands_missing}건")
        if total_mcps_missing:
            print(f"❌ MCP 누락: {total_mcps_missing}건")
        if total_plugins_missing:
            print(f"❌ 플러그인 누락: {total_plugins_missing}건")
        if claude_issues:
            print(f"⚠️ Claude Code 설치 이슈: {claude_issues}건")

        print("\n[누락 상세]")
        if claude_result and claude_issues:
            if not claude_result.found:
                print("  - [Claude] 미설치")
            if claude_result.found and not claude_result.is_native:
                print("  - [Claude] npm global 설치 → native 설치 권장")
            if claude_result.npm_duplicate:
                print("  - [Claude] npm global 중복 → npm uninstall -g @anthropic-ai/claude-code")
        if plugin_result:
            for p in plugin_result.missing:
                print(f"  - [플러그인] {p}")
        for r in results:
            if r.agents_missing:
                for agent in r.agents_missing:
                    print(f"  - [{r.skill_file}] 에이전트: {agent}")
            if r.commands_missing:
                for cmd in r.commands_missing:
                    print(f"  - [{r.skill_file}] 커맨드: {cmd}")
            if r.mcps_missing:
                for mcp in r.mcps_missing:
                    print(f"  - [{r.skill_file}] MCP: {mcp}")

    return total_agents_missing + total_commands_missing + total_mcps_missing + total_plugins_missing


def generate_todo_entries(results: list, sp: str = "00") -> list:
    """누락 항목에 대한 todo 엔트리 생성"""
    entries = []

    for r in results:
        if r.agents_missing:
            entries.append(f"[VALIDATION] {r.skill_file}: 에이전트 누락 - {', '.join(r.agents_missing)}")
        if r.commands_missing:
            entries.append(f"[VALIDATION] {r.skill_file}: 커맨드 누락 - {', '.join(r.commands_missing)}")
        if r.mcps_missing:
            entries.append(f"[VALIDATION] {r.skill_file}: MCP 누락 - {', '.join(r.mcps_missing)}")

    return entries


def main():
    parser = argparse.ArgumentParser(
        description='ooenv validate --full: 스킬 참조 정합성 검증'
    )
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='상세 출력 (유효한 참조도 표시)')
    parser.add_argument('--sp', type=str, default='00',
                        help='서브프로젝트 번호 (기본: 00)')
    parser.add_argument('--output-todo', action='store_true',
                        help='누락 항목을 todo 형식으로 출력')

    args = parser.parse_args()

    # 프로젝트 루트 찾기
    project_root = Path.cwd()
    while project_root != project_root.parent:
        if (project_root / '.claude').exists():
            break
        project_root = project_root.parent

    if not (project_root / '.claude').exists():
        print("오류: 프로젝트 루트를 찾을 수 없습니다. (.claude 디렉토리 없음)")
        return 1

    results, plugin_result, claude_result = validate_all(project_root, args.verbose)
    missing_count = print_summary(results, plugin_result, claude_result)

    if args.output_todo and missing_count > 0:
        print("\n[Todo 엔트리]")
        entries = generate_todo_entries(results, args.sp)
        for entry in entries:
            print(f"- {entry}")

    return 1 if missing_count > 0 else 0


if __name__ == '__main__':
    exit(main())
