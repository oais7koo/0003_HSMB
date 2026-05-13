#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ooenv_run.py - 개발 환경 분석 및 자동 수정 (상세: doc/a0009_script.md)"""

import sys
import sys as _sys
if _sys.stdout.encoding and _sys.stdout.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stdout.reconfigure(encoding='utf-8')
if _sys.stderr.encoding and _sys.stderr.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stderr.reconfigure(encoding='utf-8')
import subprocess
import shutil
import json
import os
from pathlib import Path
from datetime import datetime

# --- oo_common inline ---
import re as _re
_SKILLS_DIR = Path(__file__).parent.parent.parent
_PROJECT_ROOT = _SKILLS_DIR.parent.parent

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

PROJECT_ROOT = _PROJECT_ROOT
SCRIPT_DIR = Path(__file__).parent
DOC_DIR = _PROJECT_ROOT / "00_doc"
TMP_DIR = _PROJECT_ROOT / "tmp"
V_DIR = _SKILLS_DIR
TODO_FILE = DOC_DIR / "d0004_todo.md"
HISTORY_FILE = DOC_DIR / "d0010_history.md"
def log_info(msg): print(f"[INFO] {msg}")
def log_ok(msg): print(f"[OK] {msg}")
def log_warn(msg): print(f"[WARN] {msg}")
def log_error(msg): print(f"[ERROR] {msg}")
def log_tip(msg): print(f"[TIP] {msg}")
def log_dry_run(msg): print(f"[DRY-RUN] {msg}")
def get_date():
    from datetime import datetime as _dt
    return _dt.now().strftime("%Y-%m-%d")

CLAUDE_CONFIG_DIR = Path(os.environ.get('CLAUDE_CONFIG_DIR', Path.home() / ".claude"))
HUD_CONFIG_PATH = CLAUDE_CONFIG_DIR / ".omc" / "hud-config.json"
HUD_SCRIPT_PATH = CLAUDE_CONFIG_DIR / "hud" / "omc-hud.mjs"
MACHINES_JSON = SCRIPT_DIR.parent / "references" / "machines.json"
GLOBAL_SETTINGS = Path.home() / ".claude" / "settings.json"
LOCAL_SETTINGS = PROJECT_ROOT / ".claude" / "settings.local.json"

# Default HUD config (minimal + contextBar, lastSkill, backgroundTasks)
DEFAULT_HUD_CONFIG = {
    "preset": "minimal",
    "elements": {
        "omcLabel": True,
        "ralph": True,
        "prdStory": False,
        "activeSkills": False,
        "lastSkill": True,
        "contextBar": True,
        "agents": True,
        "backgroundTasks": True,
        "todos": True,
        "showCache": False,
        "showCost": False,
        "maxOutputLines": 1
    },
    "thresholds": {
        "contextWarning": 70,
        "contextCritical": 85,
        "ralphWarning": 7
    }
}

MCP_JSON_PATH = PROJECT_ROOT / ".mcp.json"
ENV_REPORT_PATH = DOC_DIR / "sp00" / "d0009_env.md"
TEMPLATE_DIR = SCRIPT_DIR.parent / "templates"
ENV_TEMPLATE_PATH = TEMPLATE_DIR / "ooenv_template.md"

# Dev group required tools
DEV_TOOLS = ["pylint", "mypy", "pytest", "black", "isort", "gh"]

# CLI tool registry - method: "npm" | "winget" | "system"
# NOTE: "claude" 항목 제거됨 (2026-05-03)
#   - native installer(`~/.local/bin/claude.exe`)가 표준 설치 경로
#   - npm 관리 시 ooenv run 단계 13에서 자동 재설치 → validate_full의 npm_duplicate 감지와 충돌
#   - native 설치본은 `claude update`로 자체 업데이트
CLI_REGISTRY = {
    "oh-my-claude-sisyphus": {
        "package": "oh-my-claude-sisyphus",
        "method": "npm",
        "description": "OMC 플러그인",
    },
    "gh": {
        "package": "GitHub.cli",
        "method": "winget",
        "description": "GitHub CLI",
    },
    "qmd": {
        "package": "@tobilu/qmd",
        "method": "npm",
        "description": "로컬 마크다운 검색 엔진 (BM25/벡터/MCP)",
    },
}

# Plugin names for O/X status check (details in template)
PLUGIN_NAMES = [
    "code-review", "commit-commands", "frontend-design", "feature-dev",
    "context7", "serena", "claude-mem", "playwright", "typescript-lsp",
    "pyright-lsp", "security-guidance", "paper-search-tools", "oh-my-claudecode", "pencil",
    "codex", "andrej-karpathy-skills"
]

# 필수 플러그인 목록 (나머지는 선택)
PLUGIN_REQUIRED = {
    "code-review", "commit-commands", "oh-my-claudecode", "context7", "pyright-lsp",
    "andrej-karpathy-skills"
}

# 플러그인 설치 명령어 (§11 누락 시 안내용)
PLUGIN_INSTALL_CMDS = {
    "code-review": "/plugin install code-review@claude-plugins-official",
    "commit-commands": "/plugin install commit-commands@claude-plugins-official",
    "context7": "/plugin install context7@claude-plugins-official",
    "pyright-lsp": "/plugin install pyright-lsp@claude-plugins-official",
    "playwright": "/plugin install playwright@claude-plugins-official",
    "frontend-design": "/plugin install frontend-design@claude-plugins-official",
    "feature-dev": "/plugin install feature-dev@claude-plugins-official",
    "typescript-lsp": "/plugin install typescript-lsp@claude-plugins-official",
    "security-guidance": "/plugin install security-guidance@claude-plugins-official",
    "pencil": "/plugin install pencil",
    "claude-mem": "/plugin marketplace add thedotmack/claude-mem → /plugin install claude-mem",
    "paper-search-tools": "/plugin marketplace add fcakyon/claude-codex-settings → /plugin install paper-search-tools@fcakyon-claude-plugins",
    "oh-my-claudecode": "/plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode → /plugin install oh-my-claudecode → /oh-my-claudecode:omc-setup",
    "codex": "/plugin marketplace add openai/codex-plugin-cc → /plugin install codex@openai-codex → /codex:setup → ! codex login",
    "andrej-karpathy-skills": "/plugin marketplace add forrestchang/andrej-karpathy-skills → /plugin install andrej-karpathy-skills@forrestchang-andrej-karpathy-skills",
}

# Claude skill names for O/X status check (details in template)
CLAUDE_SKILL_NAMES = [
    "algorithmic-art", "brand-guidelines", "canvas-design", "doc-coauthoring",
    "docx", "mcp-builder", "pdf", "pptx", "skill-creator",
    "slack-gif-creator", "theme-factory", "webapp-testing", "web-artifacts-builder", "xlsx"
]

# Agent registry (.claude/agents/*.md)
# Format: "agent_name": "description"
AGENT_REGISTRY = {
    "academic-researcher": "학술 연구",
    "ai-engineer": "AI 엔지니어링",
    "codebase_investigator": "코드베이스 조사",
    "code-error-checker": "코드 에러 체크",
    "data-analyst": "데이터 분석",
    "data-engineer": "데이터 엔지니어링",
    "data-scientist": "데이터 사이언스",
    "frontend-developer": "프론트엔드 개발",
    "img-extract": "이미지 추출",
    "jupyter-specialist": "Jupyter 전문가",
    "oo-leader": "복잡 작업 조율/관리",
    "oo-python-algorithm-expert": "Python 알고리즘 분석",
    "ooppt-agent": "PPT 생성",
    "ooqa": "품질 분석",
    "oowebdesigner": "웹 디자이너",
    "oo-web-test-orchestrator": "웹 테스트",
    "python-code-reviewer": "Python 코드 리뷰",
    "streamlit-code-reviewer": "Streamlit 코드 리뷰",
    "streamlit-implementer": "Streamlit 구현",
    "streamlit-page-designer": "Streamlit 페이지 설계",
    "streamlit-page-planner": "Streamlit 페이지 계획",
    "task-checker": "태스크 검증",
    "task-executor": "태스크 실행",
    "task-orchestrator": "태스크 오케스트레이션",
    "translator": "번역",
    "web-design-expert": "웹 디자인",
}

# Command registry (.claude/commands/sc/*.md)
# Format: "command_name": "description"
COMMAND_REGISTRY = {
    "analyze": "코드 분석",
    "build": "프로젝트 빌드",
    "cleanup": "코드 및 프로젝트 정리",
    "design": "시스템 및 컴포넌트 설계",
    "document": "집중 문서화",
    "estimate": "개발 추정",
    "explain": "코드 및 개념 설명",
    "git": "Git 작업",
    "implement": "기능 구현",
    "improve": "코드 개선",
    "index": "프로젝트 인덱싱",
    "load": "프로젝트 컨텍스트 로드",
    "spawn": "태스크 분할 및 병렬 실행",
    "task": "태스크 관리",
    "test": "테스트 실행",
    "troubleshoot": "문제 해결",
    "workflow": "워크플로우 생성",
}

# MCP servers replaced by Claude plugins (skip in missing check)
# These servers are provided by enabled plugins and don't need .mcp.json entries
PLUGIN_REPLACED_MCP_SERVERS = set()

# Known MCP server package mappings
# Format: "server_name": {"role": "description", "package": "npm_package", "env": {}, "api_key_required": bool}
MCP_SERVER_REGISTRY = {
    "sequential-thinking": {
        "role": "복잡한 다단계 분석/추론",
        "package": "@modelcontextprotocol/server-sequential-thinking",
        "env": {},
        "api_key_required": False,
        "required": True
    },
    "desktop-commander": {
        "role": "파일 I/O, 터미널 명령 실행 (filesystem 대체)",
        "package": "@wonderwhy-er/desktop-commander",
        "env": {},
        "api_key_required": False,
        "required": True
    },
    "puppeteer": {
        "role": "브라우저 자동화/스크래핑",
        "package": "@modelcontextprotocol/server-puppeteer",
        "env": {},
        "api_key_required": False
    },
    "postgres": {
        "role": "PostgreSQL DB 연동",
        "package": "@modelcontextprotocol/server-postgres",
        "env": {"POSTGRES_CONNECTION_STRING": "${POSTGRES_CONNECTION_STRING}"},
        "api_key_required": True,
        "api_key_name": "POSTGRES_CONNECTION_STRING"
    },
    "sqlite": {
        "role": "SQLite DB 연동",
        "package": "@modelcontextprotocol/server-sqlite",
        "env": {},
        "api_key_required": False
    },
    "google": {
        "role": "Google API 연동",
        "package": "@anthropic/mcp-server-google",
        "env": {"GOOGLE_API_KEY": "${GOOGLE_API_KEY}"},
        "api_key_required": True,
        "api_key_name": "GOOGLE_API_KEY"
    },
}


def check_hud_config() -> dict:
    """Check HUD config status and create if missing."""
    result = {
        "script_installed": HUD_SCRIPT_PATH.exists(),
        "config_exists": HUD_CONFIG_PATH.exists(),
        "config": None,
        "created": False
    }

    if result["config_exists"]:
        result["config"] = json.loads(HUD_CONFIG_PATH.read_text(encoding='utf-8'))
    else:
        # Create default config
        HUD_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        HUD_CONFIG_PATH.write_text(
            json.dumps(DEFAULT_HUD_CONFIG, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        result["config"] = DEFAULT_HUD_CONFIG
        result["config_exists"] = True
        result["created"] = True
        log_ok("HUD config created with default settings")

    return result


def _find_in_registry_path(command: str):
    """Search Windows registry PATH for command. Returns Path or None."""
    if os.name != 'nt':
        return None
    try:
        import winreg
        keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
            (winreg.HKEY_CURRENT_USER, r"Environment"),
        ]
        for hive, subkey in keys:
            try:
                k = winreg.OpenKey(hive, subkey)
                val, _ = winreg.QueryValueEx(k, "Path")
                for d in val.split(";"):
                    d = d.strip()
                    if not d:
                        continue
                    p = Path(d) / f"{command}.exe"
                    if p.exists():
                        return p
            except Exception:
                pass
    except Exception:
        pass
    return None


def resolve_command_path(command: str) -> str:
    """Return full path to command, using registry fallback on Windows."""
    found = shutil.which(command)
    if found:
        return found
    p = _find_in_registry_path(command)
    return str(p) if p else command


def check_command(command: str) -> bool:
    """Check if a command exists in the path."""
    if shutil.which(command) is not None:
        return True
    return _find_in_registry_path(command) is not None


def run_command(cmd: list, description: str, capture: bool = True, timeout: int = 30) -> tuple:
    """Run a command and return (success, output)."""
    try:
        if capture:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                check=False,
                cwd=str(PROJECT_ROOT),
                timeout=timeout
            )
            return result.returncode == 0, result.stdout + result.stderr
        else:
            result = subprocess.run(cmd, check=False, cwd=str(PROJECT_ROOT), timeout=timeout)
            return result.returncode == 0, ""
    except subprocess.TimeoutExpired:
        return False, f"[TIMEOUT] {description} timed out after {timeout}s"
    except Exception as e:
        return False, str(e)


def check_dev_tools() -> dict:
    """Check dev tools installation status."""
    status = {}
    for tool in DEV_TOOLS:
        status[tool] = check_command(tool)
    return status


def install_dev_group(dry_run: bool = False) -> bool:
    """Install UV dev group."""
    print("\n## UV Dev Group Install")

    if dry_run:
        print("[DRY-RUN] Will run: uv sync --group dev")
        return True

    print("Running: uv sync --group dev")
    success, output = run_command(["uv", "sync", "--group", "dev"], "UV dev group install")

    if success:
        print("[OK] Dev group installed")
    else:
        print(f"[ERROR] Install failed: {output[:200]}")

    return success


def check_uv_status() -> dict:
    """Check UV dependency status."""
    result = {
        "uv_installed": check_command("uv"),
        "outdated": [],
        "missing": []
    }

    if not result["uv_installed"]:
        return result

    # Check installed packages with uv pip list
    success, output = run_command(["uv", "pip", "list"], "package list")

    return result


def check_omc_setup() -> dict:
    """Check if oh-my-claudecode (OMC) is properly set up.

    Returns: {"plugin": bool, "hud_script": bool, "statusline_ok": bool, "issues": list}
    """
    import os
    result = {"plugin": False, "hud_script": False, "statusline_ok": False, "issues": []}

    user_home = Path(os.environ.get('USERPROFILE', os.environ.get('HOME', '')))

    # 1. 플러그인 설치 여부 (~/.claude/plugins/oh-my-claudecode/ 또는 installed_plugins.json)
    plugin_dir = user_home / ".claude" / "plugins"
    omc_dirs = list(plugin_dir.glob("oh-my-claudecode*")) if plugin_dir.exists() else []
    result["plugin"] = len(omc_dirs) > 0

    # 2. HUD 스크립트 존재 여부
    hud_script = user_home / ".claude" / "hud" / "omc-hud.mjs"
    result["hud_script"] = hud_script.exists()
    if not result["hud_script"]:
        result["issues"].append("omc-hud.mjs 없음 → /oh-my-claudecode:omc-setup 실행 필요")

    # 3. 글로벌 settings.json statusLine → omc-hud 설정 여부
    global_settings = user_home / ".claude" / "settings.json"
    if global_settings.exists():
        try:
            data = json.loads(global_settings.read_text(encoding="utf-8"))
            status_line = data.get("statusLine", {})
            cmd = status_line.get("command", "") if isinstance(status_line, dict) else ""
            result["statusline_ok"] = "omc-hud" in cmd
            if not result["statusline_ok"]:
                result["issues"].append(f"글로벌 statusLine이 omc-hud를 가리키지 않음 (현재: {cmd[:50] or '미설정'})")
        except Exception:
            result["issues"].append("글로벌 settings.json 파싱 오류")

    return result


def check_gsd_installed() -> dict:
    """Check if GSD (get-shit-done-cc) is installed locally or globally.

    Returns: {"local": bool, "global": bool, "version": str}
    """
    import os
    result = {"local": False, "global": False, "version": ""}

    # 로컬 설치 확인 (.claude/commands/gsd/ 존재)
    local_gsd = PROJECT_ROOT / ".claude" / "commands" / "gsd"
    result["local"] = local_gsd.exists() and local_gsd.is_dir()

    # 버전 확인 (.claude/get-shit-done/VERSION)
    local_ver = PROJECT_ROOT / ".claude" / "get-shit-done" / "VERSION"
    if local_ver.exists():
        result["version"] = local_ver.read_text(encoding="utf-8").strip()

    # 글로벌 설치 확인 (~/.claude/commands/gsd/)
    user_home = Path(os.environ.get('USERPROFILE', os.environ.get('HOME', '')))
    global_gsd = user_home / ".claude" / "commands" / "gsd"
    result["global"] = global_gsd.exists() and global_gsd.is_dir()

    return result


def check_git_tmp() -> dict:
    """Check TEMP/TMP for MinGW git.exe compatibility and auto-fix ~/.bashrc."""
    import os
    result = {"ok": False, "fixed": False, "message": "", "details": ""}

    temp = os.environ.get("TEMP", "")
    tmp = os.environ.get("TMP", "")

    # Unix-style path (starts with '/') is incompatible with MinGW git.exe
    if not (temp.startswith("/") or tmp.startswith("/")):
        result["ok"] = True
        result["message"] = f"TEMP/TMP OK: {temp or tmp}"
        return result

    # Check ~/.bashrc for existing fix
    user_home = Path(os.environ.get("USERPROFILE", os.environ.get("HOME", "")))
    bashrc = user_home / ".bashrc"
    already_fixed = False

    if bashrc.exists():
        content = bashrc.read_text(encoding="utf-8", errors="replace")
        already_fixed = "cygpath -m /tmp" in content

    if already_fixed:
        result["ok"] = False
        result["message"] = f"TEMP={temp!r} (Unix경로) — ~/.bashrc에 fix 존재, 새 터미널에서 적용됨"
        result["details"] = "현재 세션에 적용하려면: source ~/.bashrc"
        return result

    # Auto-add fix to ~/.bashrc
    fix_block = (
        "\n# Fix TEMP/TMP for MinGW git.exe (prevents 'unable to write new index file')\n"
        "export TEMP=$(cygpath -m /tmp)\n"
        "export TMP=$(cygpath -m /tmp)\n"
    )
    try:
        with open(str(bashrc), "a", encoding="utf-8") as f:
            f.write(fix_block)
        result["ok"] = False
        result["fixed"] = True
        result["message"] = f"TEMP={temp!r} (Unix경로) — ~/.bashrc에 fix 자동 추가 완료"
        result["details"] = "적용: source ~/.bashrc (또는 새 터미널)"
    except Exception as e:
        result["ok"] = False
        result["message"] = f"TEMP={temp!r} (Unix경로) — ~/.bashrc 쓰기 실패: {e}"
        result["details"] = "수동 추가: echo 'export TEMP=$(cygpath -m /tmp)' >> ~/.bashrc"

    return result


def check_plugins(verbose: bool = False) -> dict:
    """Check plugin status."""
    result = {
        "superpowers": False,
        "message": ""
    }

    # superpowers plugin check (only meaningful in Claude Code environment)
    # Return basic status here
    result["message"] = "Check plugin status in Claude Code environment."

    return result


# ============================================================
# MCP Server Management Functions
# ============================================================

def read_mcp_json() -> dict:
    """Read .mcp.json file."""
    if not MCP_JSON_PATH.exists():
        return {"mcpServers": {}}

    with open(MCP_JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_mcp_json(data: dict) -> bool:
    """Write .mcp.json file."""
    try:
        with open(MCP_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent='\t', ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to write .mcp.json: {e}")
        return False


def get_installed_mcp_servers() -> list:
    """Get list of installed MCP servers from .mcp.json."""
    mcp_data = read_mcp_json()
    return list(mcp_data.get("mcpServers", {}).keys())


def get_missing_mcp_from_validation() -> list:
    """Get missing MCP servers from validation script output."""
    missing = []
    validate_script = SCRIPT_DIR / "ooenv_validate_full.py"

    if not validate_script.exists():
        return missing

    success, output = run_command(
        ["uv", "run", "python", str(validate_script)],
        "validation check"
    )

    # Parse output to find missing MCP servers
    # Look for lines like: "  - [oopaper.md] MCP: paperswithcode"
    for line in output.split('\n'):
        if 'MCP:' in line and '[' in line:
            # Extract MCP server name
            parts = line.split('MCP:')
            if len(parts) > 1:
                mcp_name = parts[1].strip()
                if mcp_name and mcp_name not in missing:
                    missing.append(mcp_name)

    return missing


def generate_mcp_config(server_name: str) -> dict:
    """Generate MCP server configuration for .mcp.json."""
    registry_info = MCP_SERVER_REGISTRY.get(server_name)

    if not registry_info:
        # Unknown server - create basic config
        return {
            "type": "stdio",
            "command": "cmd",
            "args": ["/c", "npx", "-y", server_name],
            "disabled": True,  # Disabled by default for unknown servers
            "_note": "Unknown server - verify package name and enable manually"
        }

    package = registry_info["package"]

    # Check if it uses smithery
    if registry_info.get("smithery"):
        config = {
            "type": "stdio",
            "command": "cmd",
            "args": ["/c", "npx", "-y", "@smithery/cli@latest", "run", package]
        }
    else:
        config = {
            "type": "stdio",
            "command": "cmd",
            "args": ["/c", "npx", "-y", package]
        }

    # Add environment variables if needed
    if registry_info.get("env"):
        config["env"] = registry_info["env"]

    # Add note about API key if required
    if registry_info.get("api_key_required"):
        config["_api_key_required"] = registry_info.get("api_key_name", "API_KEY")

    return config


def install_mcp_server(server_name: str, dry_run: bool = False) -> bool:
    """Install MCP server by adding to .mcp.json."""
    mcp_data = read_mcp_json()

    if server_name in mcp_data.get("mcpServers", {}):
        print(f"  [SKIP] {server_name} already configured")
        return True

    config = generate_mcp_config(server_name)
    registry_info = MCP_SERVER_REGISTRY.get(server_name)

    if dry_run:
        print(f"  [DRY-RUN] Would add: {server_name}")
        if registry_info and registry_info.get("api_key_required"):
            print(f"    [INFO] Requires API key: {registry_info.get('api_key_name')}")
        return True

    # Add to mcp_data
    if "mcpServers" not in mcp_data:
        mcp_data["mcpServers"] = {}

    mcp_data["mcpServers"][server_name] = config

    if write_mcp_json(mcp_data):
        print(f"  [OK] Added: {server_name}")
        if registry_info and registry_info.get("api_key_required"):
            print(f"    [INFO] Set {registry_info.get('api_key_name')} in .env")
        return True
    else:
        print(f"  [ERROR] Failed to add: {server_name}")
        return False


def check_mcp_status() -> dict:
    """Check MCP server status."""
    result = {
        "installed": get_installed_mcp_servers(),
        "missing": [],
        "unknown": []
    }

    # Get missing from validation
    missing_from_validation = get_missing_mcp_from_validation()

    for server in missing_from_validation:
        # Skip servers replaced by Claude plugins
        if server in PLUGIN_REPLACED_MCP_SERVERS:
            continue
        if server in MCP_SERVER_REGISTRY:
            result["missing"].append(server)
        else:
            result["unknown"].append(server)

    return result


def check_qmd_mcp_collection() -> dict:
    """Check if qmd MCP server has --collection arg set to scope searches to this project."""
    mcp_data = read_mcp_json()
    servers = mcp_data.get("mcpServers", {})

    result = {
        "qmd_registered": "qmd" in servers,
        "collection_set": False,
        "collection_value": None,
        "project_folder": PROJECT_ROOT.name,
    }

    if result["qmd_registered"]:
        args = servers["qmd"].get("args", [])
        for flag in ("--collection", "-c"):
            if flag in args:
                idx = args.index(flag)
                if idx + 1 < len(args):
                    result["collection_set"] = True
                    result["collection_value"] = args[idx + 1]
                break

    return result


def check_qmd_required_collections() -> dict:
    """qmd collection list로 1_oais, code(3_code) 컬렉션 등록 여부 확인."""
    import subprocess, shutil
    result = {"available": False, "collections": [], "missing": []}
    required = {"oais": "1_oais 프로젝트", "code": "3_code 프로젝트"}

    qmd_node = shutil.which("qmd")
    node_bin = Path(r"C:\Users\oaiskoo\home\util\nodejs\node-v22.17.0-win-x64\node.exe")
    qmd_js = Path(r"C:\Users\oaiskoo\home\util\nodejs\node-v22.17.0-win-x64\node_modules\@tobilu\qmd\dist\cli\qmd.js")

    try:
        if node_bin.exists() and qmd_js.exists():
            cmd = [str(node_bin), str(qmd_js), "collection", "list"]
        elif qmd_node:
            cmd = [qmd_node, "collection", "list"]
        else:
            return result
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=10).stdout
        result["available"] = True
        for name in required:
            if name in out:
                result["collections"].append(name)
            else:
                result["missing"].append((name, required[name]))
    except Exception:
        pass
    return result


def check_settings_consistency(fix: bool = True) -> dict:
    """machines.json 기반 설정 정합성 검증. fix=True(기본)이면 자동 수정."""
    import platform
    result = {"passed": True, "issues": [], "warnings": [], "fixed": []}

    # 1. machines.json 존재 확인
    if not MACHINES_JSON.exists():
        result["issues"].append("machines.json 파일 없음")
        result["passed"] = False
        return result

    with open(MACHINES_JSON, 'r', encoding='utf-8') as f:
        machines = json.load(f)

    # 2. hostname 등록 확인
    hostname = platform.node().lower()
    if hostname not in machines:
        result["issues"].append(f"'{hostname}' 미등록 → ooenv settings --register 필요")
        result["passed"] = False
        return result

    machine_config = machines[hostname]

    # 3. 글로벌 settings.json 검증 (statusLine만 있어야 함)
    if GLOBAL_SETTINGS.exists():
        with open(GLOBAL_SETTINGS, 'r', encoding='utf-8') as f:
            current_global = json.load(f)
        expected_global = machine_config.get("settings_global", {})
        extra_keys = [k for k in current_global if k not in expected_global]
        if extra_keys:
            if fix:
                for k in extra_keys:
                    del current_global[k]
                with open(GLOBAL_SETTINGS, 'w', encoding='utf-8') as f:
                    json.dump(current_global, f, indent=2, ensure_ascii=False)
                result["fixed"].append(f"~/.claude/settings.json 불필요 항목 자동 삭제: {', '.join(extra_keys)}")
            else:
                result["issues"].append(f"~/.claude/settings.json에 불필요 항목: {', '.join(extra_keys)}")
                result["passed"] = False
        # expected 항목 비교
        for key, value in expected_global.items():
            if key not in current_global:
                result["issues"].append(f"~/.claude/settings.json 누락: {key}")
                result["passed"] = False
            elif current_global[key] != value:
                result["warnings"].append(f"~/.claude/settings.json 불일치: {key}")
    else:
        result["issues"].append("~/.claude/settings.json 파일 없음")
        result["passed"] = False

    # 4. 로컬 settings.local.json 검증
    expected_local = machine_config.get("settings_local", {})
    if expected_local and LOCAL_SETTINGS.exists():
        with open(LOCAL_SETTINGS, 'r', encoding='utf-8') as f:
            current_local = json.load(f)
        for key, value in expected_local.items():
            if key not in current_local:
                result["warnings"].append(f"로컬 누락: {key}")
            elif isinstance(value, dict) and isinstance(current_local.get(key), dict):
                for sk, sv in value.items():
                    if current_local[key].get(sk) != sv:
                        result["warnings"].append(f"로컬 불일치: {key}.{sk}")

    return result


def run_validation(verbose: bool = False) -> dict:
    """Run validation check."""
    result = {
        "passed": True,
        "issues": []
    }

    # Check if validate_full script exists
    validate_script = SCRIPT_DIR / "ooenv_validate_full.py"
    if validate_script.exists():
        success, output = run_command(
            ["uv", "run", "python", str(validate_script)],
            "validation check"
        )
        if not success:
            result["passed"] = False
            result["issues"].append("Validation check failed")

    return result


def get_python_version() -> str:
    """Get Python version."""
    return f"Python {sys.version.split()[0]}"


def get_uv_version() -> str:
    """Get UV version."""
    success, output = run_command(["uv", "--version"], "uv version")
    if success:
        return output.strip()
    return "Unknown"


def get_node_version() -> str:
    """Get Node.js version."""
    success, output = run_command(["node", "--version"], "node version")
    if success:
        return output.strip()
    return "Not installed"


def get_npm_version() -> str:
    """Get npm version."""
    success, output = run_command(["npm", "--version"], "npm version")
    if success:
        return output.strip()
    return "Not installed"


def get_git_version() -> str:
    """Get Git version."""
    success, output = run_command(["git", "--version"], "git version")
    if success:
        return output.strip()
    return "Not installed"


def get_pandoc_version() -> str:
    """Get Pandoc version."""
    success, output = run_command(["pandoc", "--version"], "pandoc version")
    if success:
        return output.split('\n')[0].strip()
    return "Not installed"


def get_installed_packages() -> list:
    """Get list of installed Python packages."""
    success, output = run_command(["uv", "pip", "list", "--format=columns"], "package list")
    packages = []
    if success:
        lines = output.strip().split('\n')
        for line in lines[2:]:  # Skip header
            parts = line.split()
            if len(parts) >= 2:
                packages.append({"name": parts[0], "version": parts[1]})
    return packages


def get_pytorch_info() -> tuple:
    """Get PyTorch version and CUDA availability.

    Note: subprocess로 torch import 시 hang 발생 가능하므로
    uv pip list로 설치 여부만 확인한다 (2026-03-29 개선).
    """
    pytorch_version = "미설치"
    cuda_available = "-"

    # uv pip list에서 torch 버전만 빠르게 확인 (subprocess import 회피)
    success, output = run_command(
        ["uv", "pip", "list", "--format=columns"],
        "pip list for torch",
        timeout=10
    )
    if success and output:
        for line in output.strip().split("\n"):
            parts = line.split()
            if len(parts) >= 2 and parts[0].lower() == "torch":
                pytorch_version = parts[1]
                cuda_available = "확인필요 (uv run python -c 'import torch; print(torch.cuda.is_available())')"
                break

    return pytorch_version, cuda_available


def get_oo_skills() -> list:
    """Get list of oo* skill directories with roles from .claude/skills/.

    Returns list of dicts: [{"name": "oodev", "role": "TDD 기반 개발", "subcmds": "run, test"}, ...]
    """
    skills_dir = PROJECT_ROOT / ".claude" / "skills"
    skills = []
    if skills_dir.exists():
        for d in sorted(skills_dir.iterdir()):
            if d.is_dir() and d.name.startswith("oo") and (d / "SKILL.md").exists():
                role = _extract_skill_role(d / "SKILL.md")
                model = _extract_skill_model(d / "SKILL.md")
                subcmds = _extract_skill_subcmds(d / "SKILL.md", d.name)
                subagent = _detect_subagent(d / "SKILL.md")
                skills.append({"name": d.name, "role": role, "model": model, "subagent": subagent, "subcmds": subcmds})
    return skills


def _extract_skill_subcmds(skill_path: Path, skill_name: str) -> str:
    """Extract subcommands from SKILL.md - handles both `skillname sub` and plain skillname sub formats."""
    def _add(cmds, first):
        if first and first not in cmds and _re.match(r'^[a-zA-Z]', first):
            cmds.append(first)

    try:
        content = skill_path.read_text(encoding='utf-8')
        cmds = []
        # Pattern 1: backtick format | `oodev run` |
        for m in _re.finditer(r"\|\s*`([^`]+)`\s*\|", content):
            cc = m.group(1).strip()
            if cc == skill_name or cc.startswith(skill_name + " "):
                sub = cc[len(skill_name):].strip()
                first = sub.split()[0] if sub.split() else ""
                _add(cmds, first)
        # Pattern 2: plain format | oodev run | (no backticks)
        for m in _re.finditer(r"^\|\s*" + _re.escape(skill_name) + r"\s+([^\s|/]+)", content, _re.MULTILINE):
            first = m.group(1).strip()
            _add(cmds, first)
        return ", ".join(cmds) if cmds else "-"
    except Exception:
        return "-"


def _extract_skill_role(skill_path: Path) -> str:
    """Extract role description from SKILL.md frontmatter description.

    Takes the first sentence (before '. ') from the description field.
    """
    try:
        content = skill_path.read_text(encoding='utf-8')
        import re
        match = re.search(r'^description:\s*["\'](.+?)["\']', content, re.MULTILINE)
        if match:
            desc = match.group(1)
            # Take first sentence (before '. ')
            idx = desc.find('. ')
            if idx > 0:
                return desc[:idx]
            return desc[:50] if len(desc) > 50 else desc
        return "-"
    except Exception:
        return "-"


def _extract_skill_model(skill_path: Path) -> str:
    """Extract model field from SKILL.md frontmatter. Returns '-' if not specified."""
    try:
        content = skill_path.read_text(encoding='utf-8')
        import re
        match = re.search(r'^model:\s*(\S+)', content, re.MULTILINE)
        if match:
            return match.group(1).strip('"\'')
        return "sonnet"
    except Exception:
        return "sonnet"


def _detect_subagent(skill_path: Path) -> str:
    """Detect if skill uses subagents. Returns 'O' or '-'."""
    try:
        import re
        content = skill_path.read_text(encoding='utf-8')
        # subagent_type 명시 (xxx 예시값 제외)
        types = re.findall(r'subagent_type=["\']([^"\']+)["\']', content)
        if any(t != 'xxx' for t in types):
            return 'O'
        # 자동 병렬 실행 징후
        auto_signs = [
            r'핵심 역할[^\n]*서브에이전트',
            r'실행 레벨[^\n]*병렬',
            r'에이전트 호환[^\n]*병렬 서브에이전트 자동',
            r'복수 에이전트를 병렬',
            r'병렬.*리뷰.*에이전트.*자동',
            r'메인 컨텍스트 보호',
            r'직접 처리 금지',
        ]
        if any(re.search(p, content) for p in auto_signs):
            return 'O'
        # 지원 병렬 징후
        support_signs = [
            r'서브에이전트.*병렬처리 지원',
            r'병렬처리.*지원',
            r'섹션별 병렬',
            r'멀티 에이전트 병렬',
        ]
        if any(re.search(p, content) for p in support_signs):
            return 'O'
        # 에이전트 테이블에서 병렬 O 행
        rows = re.findall(r'\|\s*([\w\-:]+)\s*\|[^|]+\|[^|]*\|\s*O\s*\|', content)
        rows = [r for r in rows if r not in ('단계','에이전트','작업','유형','구분','단계1')]
        if rows:
            return 'O'
        return '-'
    except Exception:
        return '-'


def get_agents() -> list:
    """Get list of agent files from .claude/agents/."""
    agents = []
    agent_dir = PROJECT_ROOT / ".claude" / "agents"
    if agent_dir.exists():
        for f in sorted(agent_dir.glob("*.md")):
            agents.append(f.name)
    return agents


def get_commands() -> list:
    """Get list of command files from .claude/commands/sc/."""
    commands = []
    cmd_dir = PROJECT_ROOT / ".claude" / "commands" / "sc"
    if cmd_dir.exists():
        for f in sorted(cmd_dir.glob("*.md")):
            commands.append(f.name)
    return commands


def get_claude_skills() -> list:
    """Get list of installed Claude skills from .claude/skills/."""
    skills = []
    skills_dir = PROJECT_ROOT / ".claude" / "skills"
    if skills_dir.exists():
        for d in sorted(skills_dir.iterdir()):
            if d.is_dir():
                skills.append(d.name)
    return skills


def get_claude_plugins() -> list:
    """Get list of installed Claude plugins from installed_plugins.json.
    Excludes plugins disabled in settings.local.json enabledPlugins."""
    import os
    plugins = []

    # Path to installed_plugins.json
    user_home = Path(os.environ.get('USERPROFILE', os.environ.get('HOME', '')))
    plugins_file = user_home / ".claude" / "plugins" / "installed_plugins.json"

    # Load disabled plugins from project settings.local.json
    disabled_keys = set()
    settings_local = PROJECT_ROOT / ".claude" / "settings.local.json"
    if settings_local.exists():
        try:
            settings_data = json.loads(settings_local.read_text(encoding='utf-8'))
            enabled_plugins = settings_data.get('enabledPlugins', {})
            for key, enabled in enabled_plugins.items():
                if not enabled:
                    disabled_keys.add(key)
        except Exception:
            pass

    if plugins_file.exists():
        data = json.loads(plugins_file.read_text(encoding='utf-8'))
        if 'plugins' in data:
            for plugin_key in sorted(data['plugins'].keys()):
                if plugin_key in disabled_keys:
                    continue
                # Extract plugin name (before @)
                plugin_name = plugin_key.split('@')[0]
                plugins.append(plugin_name)

    return plugins


def generate_env_report(
    tool_status: dict,
    mcp_status: dict,
    validation: dict,
    issues_found: int,
    issues_fixed: int,
    hud_status: dict = None,
    runtime_standards: dict = None
) -> str:
    """Generate d0009_env.md content using template."""
    now = datetime.now()

    # Read template
    if not ENV_TEMPLATE_PATH.exists():
        print(f"[WARN] Template not found: {ENV_TEMPLATE_PATH}")
        return _generate_env_report_fallback(
            tool_status, mcp_status, validation, issues_found, issues_fixed
        )

    template = ENV_TEMPLATE_PATH.read_text(encoding='utf-8')

    # Get versions
    python_ver = get_python_version()
    uv_ver = get_uv_version()
    node_ver = get_node_version()
    npm_ver = get_npm_version()
    git_ver = get_git_version()
    pandoc_ver = get_pandoc_version()

    # Build runtime comparison table
    _std = runtime_standards or {}
    runtime_items = [
        ("Python", python_ver),
        ("UV", uv_ver),
        ("Node.js", node_ver),
        ("npm", npm_ver),
        ("Git", git_ver),
        ("Pandoc", pandoc_ver),
    ]
    runtime_table = ""
    for name, current in runtime_items:
        standard = _std.get(name, "-")
        status = _check_version_ok(current, standard)
        runtime_table += f"| {name} | {current} | {standard} | {status} |\n"

    # Get project info
    project_skills = get_oo_skills()
    claude_skills = get_claude_skills()
    claude_plugins = get_claude_plugins()
    agents = get_agents()
    commands = get_commands()
    packages = get_installed_packages()
    pytorch_ver, cuda_status = get_pytorch_info()

    # Build dev tools table
    dev_tools_table = ""
    for tool, installed in tool_status.items():
        status = "OK" if installed else "X"
        dev_tools_table += f"| {tool} | {status} |\n"

    # Build MCP status table (using MCP_SERVER_REGISTRY)
    mcp_status_table = ""
    mcp_installed_count = 0
    installed_servers = mcp_status['installed']
    for server_name, info in MCP_SERVER_REGISTRY.items():
        is_installed = server_name in installed_servers
        if is_installed:
            mcp_installed_count += 1
        status = "O" if is_installed else "X"
        if is_installed:
            install_cmd = "-"
        else:
            install_cmd = f"npx -y {info['package']}"
            if info.get('api_key_required'):
                install_cmd += f" (requires {info.get('api_key_name', 'API_KEY')})"
        req = "★" if info.get("required") else "-"
        mcp_status_table += f"| {server_name} | {info['role']} | {req} | {status} | `{install_cmd}` |\n"

    # Build plugins O/X status (details in template)
    plugins_installed_count = 0
    plugin_status = {}
    for plugin_name in PLUGIN_NAMES:
        is_installed = plugin_name in claude_plugins
        if is_installed:
            plugins_installed_count += 1
        plugin_status[plugin_name] = "O" if is_installed else "X"

    # Auto-detect new plugins not in PLUGIN_NAMES
    new_plugin_rows = ""
    for plugin_name in claude_plugins:
        if plugin_name not in PLUGIN_NAMES:
            plugins_installed_count += 1
            req = "★" if plugin_name in PLUGIN_REQUIRED else "-"
            new_plugin_rows += f"| {plugin_name} | (신규 감지) | {req} | O | - |\n"
    plugins_total_count = len(PLUGIN_NAMES) + sum(
        1 for p in claude_plugins if p not in PLUGIN_NAMES
    )

    # Build Claude skills O/X status (details in template)
    claude_skills_installed_count = 0
    claude_skill_status = {}
    for skill_name in CLAUDE_SKILL_NAMES:
        is_installed = skill_name in claude_skills
        if is_installed:
            claude_skills_installed_count += 1
        claude_skill_status[skill_name] = "O" if is_installed else "X"

    # Build Claude skills table
    if claude_skills:
        claude_skills_table = "| 스킬 |\n|------|\n"
        for skill in claude_skills:
            claude_skills_table += f"| {skill} |\n"
    else:
        claude_skills_table = "설치된 Claude 스킬이 없습니다.\n"

    # Build project skills table
    if project_skills:
        skills_table = "| 스킬 | 역할 | 모델 | 서브에이전트 |\n|------|------|------|-------------|\n"
        for skill in project_skills:
            skills_table += f"| {skill['name']} | {skill['role']} | {skill['model']} | {skill['subagent']} |\n"
        skills_table += "\n### 4.2.1 주요 서브명령어\n\n"
        skills_table += "| 스킬 | 주요 서브명령어 |\n|------|---------------|\n"
        for skill in project_skills:
            skills_table += f"| {skill['name']} | {skill['subcmds']} |\n"
    else:
        skills_table = "스킬 파일이 없습니다.\n"

    # Build agents table (registry-based with O/X status)
    installed_agents = [a.replace('.md', '') for a in agents]
    agents_installed_count = 0
    agents_table = ""
    for agent_name, description in sorted(AGENT_REGISTRY.items()):
        is_installed = agent_name in installed_agents
        if is_installed:
            agents_installed_count += 1
        status = "O" if is_installed else "X"
        agents_table += f"| {agent_name} | {status} | {description} |\n"

    # Build commands table (registry-based with O/X status)
    installed_commands = [c.replace('.md', '') for c in commands if c != 'README.md']
    commands_installed_count = 0
    commands_table = ""
    for cmd_name, description in sorted(COMMAND_REGISTRY.items()):
        is_installed = cmd_name in installed_commands
        if is_installed:
            commands_installed_count += 1
        status = "O" if is_installed else "X"
        commands_table += f"| {cmd_name} | {status} | {description} |\n"

    # Build packages table
    if packages:
        packages_table = "| 패키지 | 버전 |\n|------|------|\n"
        for pkg in packages[:50]:
            packages_table += f"| {pkg['name']} | {pkg['version']} |\n"
        if len(packages) > 50:
            packages_table += f"\n... 외 {len(packages) - 50}개\n"
    else:
        packages_table = "설치된 패키지가 없습니다.\n"

    # Build CLI tools table
    cli_status = check_cli_status()
    cli_table = ""
    cli_installed_count = 0
    for cmd, info in cli_status.items():
        installed_str = "O" if info["installed"] else "X"
        version_str = info["version"] if info["installed"] else "-"
        if info["installed"]:
            cli_installed_count += 1
        cli_table += f"| {cmd} | {info['description']} | {info['method']} | {installed_str} | {version_str} |\n"

    # Build validation issues section
    validation_issues_section = ""
    if validation.get('issues'):
        validation_issues_section = "### 10.1 검증 이슈\n\n"
        for issue in validation['issues']:
            validation_issues_section += f"- {issue}\n"

    # Replace placeholders
    content = template
    replacements = {
        '{{DATE}}': now.strftime('%Y-%m-%d'),
        '{{DATETIME}}': now.strftime('%Y-%m-%d %H:%M:%S'),
        '{{PYTHON_VERSION}}': python_ver,
        '{{UV_VERSION}}': uv_ver,
        '{{NODE_VERSION}}': node_ver,
        '{{NPM_VERSION}}': npm_ver,
        '{{GIT_VERSION}}': git_ver,
        '{{PANDOC_VERSION}}': pandoc_ver,
        '{{RUNTIME_TABLE}}': runtime_table.rstrip(),
        '{{DEV_TOOLS_TABLE}}': dev_tools_table.rstrip(),
        '{{MCP_INSTALLED_COUNT}}': str(mcp_installed_count),
        '{{MCP_TOTAL_COUNT}}': str(len(MCP_SERVER_REGISTRY)),
        '{{MCP_STATUS_TABLE}}': mcp_status_table.rstrip(),
        '{{PLUGINS_INSTALLED_COUNT}}': str(plugins_installed_count),
        '{{PLUGINS_TOTAL_COUNT}}': str(plugins_total_count),
        '{{PLUGINS_NEW_ROWS}}': new_plugin_rows,
        '{{CLAUDE_SKILLS_INSTALLED_COUNT}}': str(claude_skills_installed_count),
        '{{CLAUDE_SKILLS_COUNT}}': str(len(claude_skills)),
        '{{CLAUDE_SKILLS_TABLE}}': claude_skills_table.rstrip(),
        '{{OAIS_SKILLS_COUNT}}': str(len(project_skills)),
        '{{SKILLS_TABLE}}': skills_table.rstrip(),
        '{{AGENTS_INSTALLED_COUNT}}': str(agents_installed_count),
        '{{AGENTS_TOTAL_COUNT}}': str(len(AGENT_REGISTRY)),
        '{{AGENTS_TABLE}}': agents_table.rstrip(),
        '{{COMMANDS_INSTALLED_COUNT}}': str(commands_installed_count),
        '{{COMMANDS_TOTAL_COUNT}}': str(len(COMMAND_REGISTRY)),
        '{{COMMANDS_TABLE}}': commands_table.rstrip(),
        '{{PACKAGES_COUNT}}': str(len(packages)),
        '{{PYTORCH_VERSION}}': pytorch_ver,
        '{{CUDA_AVAILABLE}}': cuda_status,
        '{{CLI_INSTALLED_COUNT}}': str(cli_installed_count),
        '{{CLI_TOTAL_COUNT}}': str(len(CLI_REGISTRY)),
        '{{CLI_TABLE}}': cli_table.rstrip(),
        '{{ISSUES_FOUND}}': str(issues_found),
        '{{ISSUES_FIXED}}': str(issues_fixed),
        '{{ISSUES_REMAINING}}': str(issues_found - issues_fixed),
        '{{VALIDATION_STATUS}}': 'PASS' if validation['passed'] else 'FAIL',
        '{{VALIDATION_ISSUES_SECTION}}': validation_issues_section.rstrip(),
    }

    # HUD config placeholders
    if hud_status and hud_status.get("config"):
        hud_cfg = hud_status["config"]
        hud_preset = hud_cfg.get("preset", "unknown")
        hud_elements = hud_cfg.get("elements", {})
        hud_on = [k for k, v in hud_elements.items() if v is True]
        hud_off = [k for k, v in hud_elements.items() if v is False]
        replacements['{{HUD_SCRIPT_STATUS}}'] = "O" if hud_status.get("script_installed") else "X"
        replacements['{{HUD_CONFIG_STATUS}}'] = "O" if hud_status.get("config_exists") else "X"
        replacements['{{HUD_PRESET}}'] = hud_preset
        replacements['{{HUD_ELEMENTS_ON}}'] = ", ".join(hud_on) if hud_on else "-"
        replacements['{{HUD_ELEMENTS_OFF}}'] = ", ".join(hud_off) if hud_off else "-"
    else:
        replacements['{{HUD_SCRIPT_STATUS}}'] = "X"
        replacements['{{HUD_CONFIG_STATUS}}'] = "X"
        replacements['{{HUD_PRESET}}'] = "-"
        replacements['{{HUD_ELEMENTS_ON}}'] = "-"
        replacements['{{HUD_ELEMENTS_OFF}}'] = "-"

    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)

    # Replace plugin status placeholders ({{P_plugin-name}} -> O/X)
    for plugin_name, status in plugin_status.items():
        content = content.replace(f'{{{{P_{plugin_name}}}}}', status)

    # Replace Claude skill status placeholders ({{S_skill-name}} -> O/X)
    for skill_name, status in claude_skill_status.items():
        content = content.replace(f'{{{{S_{skill_name}}}}}', status)

    return content


def _generate_env_report_fallback(
    tool_status: dict,
    mcp_status: dict,
    validation: dict,
    issues_found: int,
    issues_fixed: int
) -> str:
    """Fallback report generation when template is not available."""
    now = datetime.now()
    return f"""# d0009_env.md - 개발 환경 현황

> 생성 시간: {now.strftime('%Y-%m-%d %H:%M:%S')}
> 경고: 템플릿 파일을 찾을 수 없어 기본 형식으로 생성되었습니다.

## 검증 결과

- 발견된 이슈: {issues_found}
- 수정된 이슈: {issues_fixed}
- 검증 상태: {'PASS' if validation['passed'] else 'FAIL'}

---

*템플릿 파일 위치: .claude/skills/ooenv/templates/ooenv_template.md*
"""


def extract_standard_spec_section() -> tuple:
    """기존 d0009에서 ## 표준 스펙 섹션 추출. (섹션 텍스트, 런타임 표준값dict) 반환."""
    defaults = {
        "Python": "3.13+",
        "UV": "0.8+",
        "Node.js": "v22+",
        "npm": "-",
        "Git": "2.43+",
        "Pandoc": "3.0+",
    }
    if not ENV_REPORT_PATH.exists():
        return "", defaults

    content = ENV_REPORT_PATH.read_text(encoding="utf-8")
    if "## 표준 스펙" not in content:
        return "", defaults

    # 섹션 추출
    start = content.index("## 표준 스펙")
    rest = content[start:]
    lines = rest.splitlines()
    end_line = len(lines)
    for i, line in enumerate(lines[1:], 1):
        if line.startswith("## ") and "표준 스펙" not in line:
            end_line = i
            break
    section_text = "\n".join(lines[:end_line]).rstrip()

    # 런타임 표 파싱
    runtime_standards = defaults.copy()
    in_runtime = False
    for line in lines:
        if "### 런타임" in line:
            in_runtime = True
        elif in_runtime and line.startswith("### "):
            break
        elif in_runtime and line.startswith("| ") and "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3 and parts[1] not in ("항목", "---", ""):
                key = parts[1]
                val = parts[2]
                if key in runtime_standards:
                    runtime_standards[key] = val

    return section_text, runtime_standards


def _check_version_ok(current: str, standard: str) -> str:
    """현재 버전이 표준 이상이면 ✅, 미달이면 ⚠️, 비교 불가면 ? 반환."""
    import re as _re
    if not standard or standard == "-":
        return "-"
    cur_nums = _re.findall(r'\d+', current)
    std_nums = _re.findall(r'\d+', standard)
    if not cur_nums or not std_nums:
        return "?"
    try:
        for c, s in zip([int(x) for x in cur_nums], [int(x) for x in std_nums]):
            if c > s:
                return "✅"
            if c < s:
                return "⚠️"
        return "✅"
    except Exception:
        return "?"


def write_env_report(
    tool_status: dict,
    mcp_status: dict,
    validation: dict,
    issues_found: int,
    issues_fixed: int,
    hud_status: dict = None
) -> bool:
    """Write environment report to d0009_env.md."""
    DOC_DIR.mkdir(parents=True, exist_ok=True)

    # 기존 표준 스펙 섹션 보존
    std_spec_section, runtime_standards = extract_standard_spec_section()

    content = generate_env_report(
        tool_status, mcp_status, validation, issues_found, issues_fixed, hud_status,
        runtime_standards=runtime_standards
    )

    # 표준 스펙 섹션 삽입 (첫 번째 --- 이후, ## 목차 앞)
    if std_spec_section:
        marker = "---\n\n## 목차"
        if marker in content:
            clean_section = std_spec_section.rstrip()
            if clean_section.endswith("---"):
                clean_section = clean_section[:-3].rstrip()
            content = content.replace(marker, f"---\n\n{clean_section}\n\n---\n\n## 목차", 1)

    ENV_REPORT_PATH.write_text(content, encoding='utf-8')
    print(f"\n[OK] Environment report: {ENV_REPORT_PATH}")
    return True


def run_context_command(args: list) -> int:
    """Run context subcommand via ooenv_context.py."""
    context_script = SCRIPT_DIR / "ooenv_context.py"
    if not context_script.exists():
        print(f"[ERROR] Context script not found: {context_script}")
        return 1

    cmd = ["uv", "run", "python", str(context_script)] + args
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    return result.returncode


def get_cli_version(command: str) -> str:
    """Get CLI tool version string."""
    cmd_path = resolve_command_path(command)
    for flag in ["--version", "version", "-v"]:
        success, output = run_command([cmd_path, flag], f"{command} version", timeout=5)
        if success and output.strip():
            return output.strip().split('\n')[0]
    return "unknown"


def check_npm_global(package: str) -> bool:
    """npm global에 패키지 설치 여부 확인 (binary 없는 패키지 대응)."""
    try:
        result = subprocess.run(
            ["npm", "list", "-g", "--depth=0", package],
            capture_output=True, text=True, timeout=15
        )
        return result.returncode == 0 and package in result.stdout
    except Exception:
        return False


def check_cli_status() -> dict:
    """Check all CLI tools installation and version."""
    status = {}
    for cmd, info in CLI_REGISTRY.items():
        if info["method"] == "npm":
            installed = check_command(cmd) or check_npm_global(info["package"])
        else:
            installed = check_command(cmd)
        status[cmd] = {
            "installed": installed,
            "version": get_cli_version(cmd) if installed else "-",
            "method": info["method"],
            "package": info["package"],
            "description": info["description"],
        }
    return status


def _refresh_omc_update_cache() -> bool:
    """OMC(sisyphus) 설치/업데이트 후 HUD가 읽는 update-check 캐시를 동기화한다.

    HUD는 `~/.claude/.omc/update-check.json`을 참고하여 배너를 표시하지만,
    `omc update` / `npm install -g` 자체는 이 캐시를 갱신하지 않으므로
    이미 최신임에도 "update available" 알림이 계속 표시되는 문제가 있다.
    이 헬퍼는 현재 설치된 sisyphus 버전을 조회해 캐시를 덮어쓴다.
    """
    import json
    import time
    import subprocess

    cache_path = Path.home() / ".claude" / ".omc" / "update-check.json"
    try:
        # 현재 설치된 sisyphus 버전 조회
        result = subprocess.run(
            _npm_cmd(["list", "-g", "--depth=0", "--json"]),
            capture_output=True, text=True, timeout=20,
        )
        if result.returncode != 0:
            return False
        data = json.loads(result.stdout or "{}")
        deps = data.get("dependencies", {})
        sisyphus = deps.get("oh-my-claude-sisyphus", {})
        current = sisyphus.get("version")
        if not current:
            return False

        # registry latest도 조회 (실패 시 current와 동일 처리)
        latest = current
        latest_result = subprocess.run(
            _npm_cmd(["view", "oh-my-claude-sisyphus", "version"]),
            capture_output=True, text=True, timeout=15,
        )
        if latest_result.returncode == 0 and latest_result.stdout.strip():
            latest = latest_result.stdout.strip()

        cache_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "timestamp": int(time.time() * 1000),
            "latestVersion": latest,
            "currentVersion": current,
            "updateAvailable": latest != current,
        }
        cache_path.write_text(
            json.dumps(payload, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"[OK] OMC HUD 캐시 동기화 완료 (current={current}, latest={latest})")
        return True
    except Exception as exc:
        print(f"[WARN] OMC HUD 캐시 동기화 실패: {exc}")
        return False


def _cli_install(package: str, method: str, label: str) -> bool:
    """Install a CLI tool by method."""
    if method == "npm":
        print(f"설치 중: npm install -g {package}")
        success, output = run_command(_npm_cmd(["install", "-g", package]), f"install {label}", timeout=120)
        print(f"{'[OK]' if success else '[ERROR]'} {output.strip()[:200]}")
        if success and package == "oh-my-claude-sisyphus":
            _refresh_omc_update_cache()
        return success
    elif method == "winget":
        print(f"설치 중: winget install --id {package}")
        success, _ = run_command(
            ["winget", "install", "--id", package, "--source", "winget", "--silent"],
            f"install {label}", timeout=180
        )
        print(f"{'[OK]' if success else '[ERROR]'} winget 설치 {'완료' if success else '실패'}")
        return success
    else:
        print(f"[INFO] {label}: {method} 방식 - 수동 설치 필요")
        return False


def _npm_cmd(args: list) -> list:
    """Windows에서 npm.cmd를 cmd /c로 래핑."""
    import platform
    if platform.system() == "Windows":
        return ["cmd", "/c", "npm"] + args
    return ["npm"] + args


def _cli_update(package: str, method: str, label: str) -> bool:
    """Update a CLI tool by method."""
    if method == "npm":
        print(f"업데이트 중: npm install -g {package}")
        success, output = run_command(_npm_cmd(["install", "-g", package]), f"update {label}", timeout=120)
        print(f"{'[OK]' if success else '[ERROR]'} {output.strip()[:100]}")
        if success and package == "oh-my-claude-sisyphus":
            _refresh_omc_update_cache()
        return success
    elif method == "winget":
        print(f"업데이트 중: winget upgrade --id {package}")
        success, output = run_command(
            ["winget", "upgrade", "--id", package, "--source", "winget", "--silent"],
            f"update {label}", timeout=120
        )
        # winget은 "이미 최신" 상태에서도 비정상 종료코드 반환 → WARN 처리
        if success:
            print(f"[OK] winget upgrade 완료")
        else:
            print(f"[WARN] winget upgrade: 이미 최신이거나 winget 미지원")
        return True  # winget 실패는 치명적이지 않음
    else:
        print(f"[SKIP] {label}: {method} 수동 관리")
        return True


def _cli_remove(package: str, method: str, label: str) -> bool:
    """Remove a CLI tool by method."""
    if method == "npm":
        print(f"제거 중: npm uninstall -g {package}")
        success, output = run_command(_npm_cmd(["uninstall", "-g", package]), f"remove {label}", timeout=60)
        print(f"{'[OK]' if success else '[ERROR]'} {output.strip()[:100]}")
        return success
    elif method == "winget":
        print(f"제거 중: winget uninstall --id {package}")
        success, _ = run_command(
            ["winget", "uninstall", "--id", package, "--silent"],
            f"remove {label}", timeout=120
        )
        print(f"{'[OK]' if success else '[ERROR]'} winget 제거 {'완료' if success else '실패'}")
        return success
    else:
        print(f"[INFO] {label}: 수동 제거 필요")
        return False


def _resolve_cli_target(target: str) -> tuple:
    """Resolve target string to (cmd, info) from CLI_REGISTRY. Returns (None, None) if not found."""
    for cmd, info in CLI_REGISTRY.items():
        if cmd == target or info["package"] == target:
            return cmd, info
    return None, None


def run_cli_command(args: list) -> int:
    """Handle ooenv cli [subcommand] [args]."""
    subcmd = args[0] if args else ""

    if not subcmd or subcmd in ("list", "check") and not args[1:]:
        # Default: show status table
        print("## CLI 도구 현황\n")
        print("| 명령어 | 설명 | 방법 | 설치 | 버전 |")
        print("|--------|------|------|------|------|")
        for cmd, info in check_cli_status().items():
            installed_str = "O" if info["installed"] else "X"
            print(f"| {cmd} | {info['description']} | {info['method']} | {installed_str} | {info['version']} |")
        return 0

    if subcmd == "check":
        print("## CLI 버전 확인\n")
        for cmd, info in check_cli_status().items():
            if not info["installed"]:
                print(f"[X] {cmd}: 미설치 → ooenv cli add {cmd}")
                continue
            if info["method"] == "npm":
                success, latest = run_command(
                    _npm_cmd(["view", info["package"], "version"]), f"{cmd} latest", timeout=15
                )
                latest = latest.strip() if success else "확인 불가"
                print(f"[OK] {cmd}: {info['version']} (npm latest: {latest})")
            else:
                print(f"[OK] {cmd}: {info['version']} ({info['method']} 관리)")
        return 0

    if subcmd == "update":
        target = args[1] if len(args) > 1 else None
        if target:
            cmd, info = _resolve_cli_target(target)
            if not cmd:
                print(f"[ERROR] 알 수 없는 CLI: {target}")
                return 1
            targets = {cmd: info}
        else:
            targets = CLI_REGISTRY
        for cmd, info in targets.items():
            if not check_command(cmd):
                print(f"[SKIP] {cmd}: 미설치")
                continue
            _cli_update(info["package"], info["method"], cmd)
        return 0

    if subcmd == "add":
        if len(args) < 2:
            print("[ERROR] 패키지명 필요: ooenv cli add <pkg>")
            return 1
        pkg = args[1]
        cmd, info = _resolve_cli_target(pkg)
        package = info["package"] if info else pkg
        method = info["method"] if info else "npm"
        return 0 if _cli_install(package, method, pkg) else 1

    if subcmd == "remove":
        if len(args) < 2:
            print("[ERROR] 패키지명 필요: ooenv cli remove <pkg>")
            return 1
        pkg = args[1]
        cmd, info = _resolve_cli_target(pkg)
        package = info["package"] if info else pkg
        method = info["method"] if info else "npm"
        return 0 if _cli_remove(package, method, pkg) else 1

    print(f"[ERROR] 알 수 없는 cli 서브명령어: {subcmd}")
    print("사용 가능: ooenv cli [list|check|update [pkg]|add <pkg>|remove <pkg>]")
    return 1


def run_subcommand(subcmd: str, args: list) -> int:
    """Route subcommands to appropriate handlers."""
    if subcmd == "status":
        print("## ooenv status\n")
        print("| 서브명령어 | 설명 |")
        print("|-----------|------|")
        print("| run | 통합 점검 + 자동 수정 + d0009 생성 |")
        print("| check | 스킬 정합성 검증 |")
        print("| plugin | 플러그인 상태 확인 |")
        print("| uv check/update/cleanup | UV 의존성 관리 |")
        print("| cli [list|check|update|add|remove] | CLI 도구 관리 |")
        print("| context | 컨텍스트 관리 |")
        print("| gpu | GPU 환경 테스트 (NVIDIA/CUDA/PyTorch) |")
        return 0

    elif subcmd == "version":
        print("ooenv v08")
        return 0

    elif subcmd == "plugin":
        result = check_plugins(True)
        print(f"## Plugin Status\n\n{result['message']}")
        return 0

    elif subcmd == "check":
        validate_script = SCRIPT_DIR / "ooenv_validate_full.py"
        if not validate_script.exists():
            print("[ERROR] validate script not found")
            return 1
        cmd = ["uv", "run", "python", str(validate_script)] + args
        result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))

        # settings 정합성 검증 (dry-run)
        print("\n------------------------------------------------------------")
        print("\n[Settings Consistency Check]")
        settings_result = check_settings_consistency()
        if settings_result["passed"]:
            log_ok("Settings consistent (global/local match machines.json)")
        else:
            for issue in settings_result["issues"]:
                log_error(issue)
        for warn in settings_result.get("warnings", []):
            log_warn(warn)
        if not settings_result["passed"]:
            log_tip("Fix: run 'ooenv run' (auto-fix)")

        # qmd 필수 컬렉션 확인
        print("\n[QMD Collection Check]")
        qmd_cols = check_qmd_required_collections()
        if qmd_cols["available"]:
            if qmd_cols["missing"]:
                for name, desc in qmd_cols["missing"]:
                    log_warn(f"qmd 컬렉션 '{name}' 미등록 ({desc})")
                    print(f"  등록: qmd collection add <경로> --name {name}")
            else:
                log_ok(f"qmd 컬렉션 등록 확인: {', '.join(qmd_cols['collections'])}")
        else:
            log_warn("qmd 미설치 또는 collection list 실패")

        # TEMP/TMP MinGW git 호환성 확인
        print("\n[Git TEMP/TMP Check]")
        git_tmp = check_git_tmp()
        if git_tmp["ok"]:
            log_ok(git_tmp["message"])
        else:
            if git_tmp.get("fixed"):
                log_warn(git_tmp["message"])
            else:
                log_warn(git_tmp["message"])
            if git_tmp.get("details"):
                log_tip(git_tmp["details"])

        return result.returncode if settings_result["passed"] else 1

    elif subcmd == "uv":
        if not args:
            print("[ERROR] uv subcommand required: check, update, cleanup")
            return 1
        uv_sub = args[0]
        uv_args = args[1:]
        if uv_sub == "cleanup":
            cleanup_script = SCRIPT_DIR / "ooenv_uv_cleanup.py"
            if not cleanup_script.exists():
                print("[ERROR] uv cleanup script not found")
                return 1
            cmd = ["uv", "run", "python", str(cleanup_script)] + uv_args
            result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
            return result.returncode
        elif uv_sub == "check":
            status = check_uv_status()
            print(f"## UV Status\n\nUV installed: {status['uv_installed']}")
            return 0
        elif uv_sub == "update":
            success, output = run_command(["uv", "sync"], "uv sync")
            print(output)
            return 0 if success else 1
        else:
            print(f"[ERROR] Unknown uv subcommand: {uv_sub}")
            return 1

    elif subcmd == "cli":
        return run_cli_command(args)

    elif subcmd == "context":
        return run_context_command(args)

    elif subcmd == "standard":
        standard_script = SCRIPT_DIR / "ooenv_standard.py"
        if not standard_script.exists():
            print("[ERROR] standard script not found")
            return 1
        cmd = ["uv", "run", "python", str(standard_script)] + args
        result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
        return result.returncode

    elif subcmd == "kill":
        kill_script = SCRIPT_DIR / "ooenv_kill.py"
        if not kill_script.exists():
            print("[ERROR] kill script not found")
            return 1
        cmd = ["uv", "run", "python", str(kill_script)] + args
        result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
        return result.returncode

    elif subcmd == "gpu":
        return run_gpu_check()

    elif subcmd == "run":
        return run_full_check(args)

    elif subcmd == "check":
        # check: run의 alias로 동작
        return run_full_check(args)

    else:
        print(f"[ERROR] Unknown subcommand: {subcmd}")
        print("Use 'ooenv status' for available commands.")
        return 1


def run_gpu_check() -> int:
    """GPU 환경 테스트 - NVIDIA 드라이버, CUDA, PyTorch GPU 지원 점검."""
    print("# ooenv gpu - GPU 환경 테스트\n")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. NVIDIA 드라이버
    print("\n## 1. NVIDIA 드라이버")
    success, output = run_command(["nvidia-smi"], "nvidia-smi", timeout=10)
    if success and output:
        for line in output.strip().split("\n")[:3]:
            print(f"  {line}")
        # GPU 이름, 메모리 추출
        success2, output2 = run_command(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.free,driver_version,cuda_version",
             "--format=csv,noheader,nounits"],
            "nvidia-smi query", timeout=10
        )
        if success2 and output2:
            print("\n| 항목 | 값 |")
            print("|------|-----|")
            parts = output2.strip().split(", ")
            labels = ["GPU", "VRAM 전체(MB)", "VRAM 여유(MB)", "드라이버", "CUDA"]
            for label, val in zip(labels, parts):
                print(f"| {label} | {val.strip()} |")
        print("\n[OK] NVIDIA 드라이버 정상")
    else:
        print("[X] nvidia-smi 실행 실패 - NVIDIA GPU 미탑재 또는 드라이버 미설치")

    # 2. CUDA Toolkit
    print("\n## 2. CUDA Toolkit")
    success, output = run_command(["nvcc", "--version"], "nvcc", timeout=10)
    if success and output:
        for line in output.strip().split("\n"):
            if "release" in line.lower():
                print(f"  {line.strip()}")
        print("[OK] CUDA Toolkit 설치됨")
    else:
        print("[INFO] nvcc 미발견 - CUDA Toolkit 미설치 (PyTorch 번들 CUDA로 동작 가능)")

    # 3. PyTorch GPU
    print("\n## 3. PyTorch GPU 지원")
    pytorch_ver, _ = get_pytorch_info()
    if pytorch_ver == "미설치":
        print(f"[X] PyTorch 미설치")
        print("    설치: uv add torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
        return 0

    print(f"  PyTorch 버전: {pytorch_ver}")

    # torch import 테스트 (subprocess, timeout 짧게)
    test_script = (
        "import torch; "
        "print(f'CUDA available: {torch.cuda.is_available()}'); "
        "print(f'CUDA version: {torch.version.cuda}') if torch.cuda.is_available() else None; "
        "print(f'cuDNN version: {torch.backends.cudnn.version()}') if torch.cuda.is_available() and torch.backends.cudnn.is_available() else None; "
        "print(f'GPU count: {torch.cuda.device_count()}') if torch.cuda.is_available() else None; "
        "print(f'GPU name: {torch.cuda.get_device_name(0)}') if torch.cuda.is_available() and torch.cuda.device_count() > 0 else None; "
        "t = torch.tensor([1.0]); "
        "t_gpu = t.to('cuda') if torch.cuda.is_available() else None; "
        "print(f'Tensor GPU test: OK') if t_gpu is not None else print(f'Tensor GPU test: SKIP (no CUDA)')"
    )
    success, output = run_command(
        ["uv", "run", "python", "-c", test_script],
        "pytorch gpu test", timeout=30
    )
    if success and output:
        print("\n| 항목 | 결과 |")
        print("|------|------|")
        for line in output.strip().split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                print(f"| {k.strip()} | {v.strip()} |")
        print("\n[OK] PyTorch GPU 테스트 완료")
    else:
        print("[WARN] PyTorch GPU 테스트 실패 또는 타임아웃")
        print("  수동 확인: uv run python -c \"import torch; print(torch.cuda.is_available())\"")

    # 4. 요약
    print("\n## 4. 요약")
    print("=" * 60)
    nvidia_ok = "nvidia-smi" in str(shutil.which("nvidia-smi") or "")
    print(f"  NVIDIA 드라이버: {'OK' if nvidia_ok else 'X'}")
    print(f"  CUDA Toolkit (nvcc): {'OK' if shutil.which('nvcc') else 'X (PyTorch 번들 사용 가능)'}")
    print(f"  PyTorch: {pytorch_ver}")
    print("=" * 60)

    return 0


def run_full_check(args: list) -> int:
    """Run full environment check (original main logic)."""
    dry_run = "--dry-run" in args

    print("# ooenv run - Development Environment Check\n")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {'Check only (dry-run)' if dry_run else 'Auto-fix + Verbose'}")
    print("=" * 60)

    issues_found = 0
    issues_fixed = 0

    # 1. UV install check
    print("\n## 1. UV Status")
    if not check_command("uv"):
        print("[ERROR] UV is not installed.")
        print("Install: https://docs.astral.sh/uv/getting-started/installation/")
        return 1
    print("[OK] UV installed")

    # 2. Dev tools status
    print("\n## 2. Dev Tools Status")
    print("| Tool | Status |")
    print("|------|--------|")

    tool_status = check_dev_tools()
    missing_tools = []

    for tool, installed in tool_status.items():
        status = "[OK]" if installed else "[X]"
        print(f"| {tool} | {status} |")
        if not installed:
            missing_tools.append(tool)
            issues_found += 1

    # 3. Auto-install missing tools
    if missing_tools:
        print(f"\n[WARN] Missing tools: {', '.join(missing_tools)}")

        if install_dev_group(dry_run):
            if not dry_run:
                # Re-check
                new_status = check_dev_tools()
                fixed = sum(1 for t in missing_tools if new_status.get(t, False))
                issues_fixed += fixed
                print(f"[OK] {fixed} tools installed")
    else:
        print("\n[OK] All dev tools installed")

    # 4. MCP Server Check
    print("\n## 3. MCP Server Status")
    mcp_status = check_mcp_status()

    print(f"Installed: {len(mcp_status['installed'])} servers")
    for server in mcp_status['installed']:
        print(f"  - {server}")

    # Handle missing MCP servers
    if mcp_status['missing'] or mcp_status['unknown']:
        print(f"\nMissing (known): {len(mcp_status['missing'])}")
        for server in mcp_status['missing']:
            print(f"  - {server}")
            issues_found += 1

        print(f"Missing (unknown): {len(mcp_status['unknown'])}")
        for server in mcp_status['unknown']:
            print(f"  - {server} [manual setup required]")
            issues_found += 1

        # Auto-install known missing servers
        if mcp_status['missing']:
            print("\n## MCP Server Install")
            for server in mcp_status['missing']:
                if install_mcp_server(server, dry_run):
                    if not dry_run:
                        issues_fixed += 1

        # Create placeholder for unknown servers
        if mcp_status['unknown'] and not dry_run:
            print("\n## Unknown MCP Servers (disabled)")
            for server in mcp_status['unknown']:
                install_mcp_server(server, dry_run)
    else:
        print("[OK] All required MCP servers configured")

    # 3-1. QMD Collection Check
    qmd_col = check_qmd_mcp_collection()
    if qmd_col["qmd_registered"]:
        if qmd_col["collection_set"]:
            log_ok(f"qmd MCP --collection={qmd_col['collection_value']} (검색 범위 제한됨)")
        else:
            log_warn(f"qmd MCP --collection 미설정 → 전체 인덱스 검색 (프로젝트 범위 미제한)")
            print(f"  프로젝트 폴더명: {qmd_col['project_folder']}")
            print(f"  등록된 컬렉션 확인: qmd collection list")
            print(f"  설정 방법 (둘 중 선택):")
            print(f"    1) .mcp.json (git 추적): qmd args에 \"--collection\", \"<컬렉션명>\" 추가")
            print(f"    2) .mcp.local.json (로컬 전용): 동일 형식으로 qmd 항목 오버라이드")
            print(f"  예시 args: [\"mcp\", \"--collection\", \"{qmd_col['project_folder']}\"]")
            issues_found += 1

    # 3-2. QMD Required Collections Check
    qmd_cols = check_qmd_required_collections()
    if qmd_cols["available"]:
        if qmd_cols["missing"]:
            for name, desc in qmd_cols["missing"]:
                log_warn(f"qmd 컬렉션 '{name}' 미등록 ({desc})")
                print(f"  등록: qmd collection add <경로> --name {name}")
                issues_found += 1
        else:
            log_ok(f"qmd 컬렉션 등록 확인: {', '.join(qmd_cols['collections'])}")

    # 5. HUD Config Check
    print("\n## 4. HUD Config Check")
    hud_status = check_hud_config()
    if hud_status["script_installed"]:
        log_ok("HUD script installed")
    else:
        log_warn("HUD script not installed (run /oh-my-claudecode:hud setup)")
        issues_found += 1

    if hud_status["created"]:
        log_ok("HUD config created with default settings")
        issues_fixed += 1
        issues_found += 1
    elif hud_status["config_exists"]:
        cfg = hud_status["config"]
        preset = cfg.get("preset", "unknown")
        elements_on = [k for k, v in cfg.get("elements", {}).items() if v is True]
        log_ok(f"HUD config: preset={preset}, ON=[{', '.join(elements_on)}]")
    else:
        log_warn("HUD config missing")
        issues_found += 1

    # 6. TEMP/TMP path validation
    print("\n## 5. TEMP/TMP Path Check")
    temp_tmp_ok = True
    # Check settings.local.json TEMP/TMP
    if LOCAL_SETTINGS.exists():
        try:
            local_cfg = json.loads(LOCAL_SETTINGS.read_text(encoding='utf-8'))
            env_cfg = local_cfg.get("env", {})
            for var_name in ("TEMP", "TMP"):
                val = env_cfg.get(var_name)
                if val:
                    p = Path(val)
                    if p.exists() and p.is_dir():
                        log_ok(f"settings.local.json {var_name}={val} (존재)")
                    else:
                        log_warn(f"settings.local.json {var_name}={val} (경로 없음)")
                        issues_found += 1
                        temp_tmp_ok = False
                        if not dry_run:
                            try:
                                p.mkdir(parents=True, exist_ok=True)
                                log_ok(f"  → 디렉토리 생성 완료: {val}")
                                issues_fixed += 1
                            except Exception as e:
                                log_error(f"  → 디렉토리 생성 실패: {e}")
                else:
                    log_warn(f"settings.local.json {var_name} 미설정")
                    issues_found += 1
                    temp_tmp_ok = False
        except Exception as e:
            log_error(f"settings.local.json 읽기 실패: {e}")
            issues_found += 1
            temp_tmp_ok = False
    else:
        log_warn("settings.local.json 파일 없음")
        issues_found += 1
        temp_tmp_ok = False

    # Check machines.json TEMP/TMP matches settings.local.json
    if temp_tmp_ok and MACHINES_JSON.exists():
        import platform
        hostname = platform.node().lower()
        try:
            machines = json.loads(MACHINES_JSON.read_text(encoding='utf-8'))
            if hostname in machines:
                expected_env = machines[hostname].get("settings_local", {}).get("env", {})
                local_cfg = json.loads(LOCAL_SETTINGS.read_text(encoding='utf-8'))
                actual_env = local_cfg.get("env", {})
                for var_name in ("TEMP", "TMP"):
                    expected = expected_env.get(var_name)
                    actual = actual_env.get(var_name)
                    if expected and actual and expected != actual:
                        log_warn(f"{var_name} 불일치: machines.json={expected}, settings.local={actual}")
                        issues_found += 1
        except Exception:
            pass

    # MinGW git.exe Unix-path 호환성 확인 + 자동수정
    git_tmp = check_git_tmp()
    if git_tmp["ok"]:
        log_ok(git_tmp["message"])
    else:
        if git_tmp.get("fixed"):
            log_ok(f"[자동수정] {git_tmp['message']}")
            issues_fixed += 1
        else:
            log_warn(git_tmp["message"])
            issues_found += 1
        if git_tmp.get("details"):
            log_tip(git_tmp["details"])

    # 7. Settings consistency check + auto-fix (machines.json)
    print("\n## 6. Settings Consistency Check")
    settings_result = check_settings_consistency(fix=not dry_run)
    for fixed_msg in settings_result.get("fixed", []):
        log_ok(f"[자동수정] {fixed_msg}")
        issues_fixed += 1
    if settings_result["passed"] and not settings_result.get("issues"):
        log_ok("Settings consistent (global/local match machines.json)")
    else:
        for issue in settings_result["issues"]:
            log_error(issue)
            issues_found += 1
        if not dry_run and settings_result["issues"]:
            # machines.json 기반 추가 sync (로컬 설정 동기화)
            try:
                import platform as _plat
                _hostname = _plat.node().lower()
                with open(MACHINES_JSON, 'r', encoding='utf-8') as _f:
                    _machines = json.load(_f)
                _mcfg = _machines.get(_hostname)
                if _mcfg:
                    from ooenv_settings import sync_settings
                    _changes = sync_settings(_mcfg, dry_run=False)
                    if _changes:
                        log_ok(f"Settings sync: {_changes} changes")
                        issues_fixed += _changes
            except Exception as _e:
                log_warn(f"Settings sync failed: {_e}")
    for warn in settings_result.get("warnings", []):
        log_warn(warn)

    # 8. Claude Code path duplication check
    print("\n## 7. Claude Code Path Check")
    _home_env = os.environ.get("HOME", "")
    _userprofile = os.environ.get("USERPROFILE", "")
    if _home_env and _userprofile and os.path.normpath(_home_env) != os.path.normpath(_userprofile):
        _claude_home = Path(_home_env) / ".claude"
        _claude_userprofile = Path(_userprofile) / ".claude"
        if _claude_home.exists() and _claude_userprofile.exists():
            log_warn(f"HOME({_home_env}) ≠ USERPROFILE({_userprofile}) — .claude 디렉토리 중복")
            log_tip("HOME 쪽 삭제 후 reinstall 권장")
            issues_found += 1
        else:
            log_ok(f"HOME/USERPROFILE 분리되어 있으나 .claude 중복 없음")
    else:
        log_ok("HOME/USERPROFILE 경로 일치 또는 단일 경로")

    # 9. Zombie process check & auto-kill
    print("\n## 8. Zombie Process Check")
    zombie_targets = ["node"]
    for target in zombie_targets:
        kill_script = SCRIPT_DIR / "ooenv_kill.py"
        if kill_script.exists():
            # 먼저 감지 (dry-run)
            result = subprocess.run(
                ["uv", "run", "python", str(kill_script), target, "--dry-run"],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                cwd=str(PROJECT_ROOT)
            )
            output = (result.stdout or "").strip()
            if "프로세스가 없습니다" in output or "No tasks" in output:
                log_ok(f"{target}.exe: 좀비 프로세스 없음")
            else:
                match = _re.search(r'프로세스 (\d+)개', output)
                count = match.group(1) if match else "?"
                log_warn(f"{target}.exe: {count}개 프로세스 감지")
                if not dry_run:
                    # 자동 종료 실행
                    kill_result = subprocess.run(
                        ["uv", "run", "python", str(kill_script), target, "--force"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                        cwd=str(PROJECT_ROOT)
                    )
                    kill_output = (kill_result.stdout or "").strip()
                    if kill_result.returncode == 0:
                        log_ok(f"{target}.exe: {count}개 프로세스 자동 종료 완료")
                        issues_found += 1
                        issues_fixed += 1
                    else:
                        log_warn(f"{target}.exe: 자동 종료 실패 - 수동 실행 필요")
                        print(f"  수동 종료: uv run python {kill_script} {target} --force")
                        issues_found += 1
                else:
                    print(f"  [DRY-RUN] 종료 대상: {count}개 프로세스")
                    issues_found += 1
        else:
            log_warn("ooenv_kill.py 스크립트 없음")

    # 10. Validation check (final)
    print("\n## 9. Validation Check")
    validation = run_validation(True)
    if validation["passed"]:
        print("[OK] Validation passed")
    else:
        for issue in validation["issues"]:
            print(f"[WARN] {issue}")
            # Don't double-count issues already counted from MCP check

    # 11. Required plugin/skill missing check
    print("\n## 11. Required Plugin/Skill Check")
    installed_plugins = get_claude_plugins()
    missing_plugins = [p for p in PLUGIN_REQUIRED if p not in installed_plugins]
    if missing_plugins:
        print(f"[WARN] 필수 플러그인 미설치 ({len(missing_plugins)}건) — Claude Code 내 슬래시 명령으로 수동 설치 필요:")
        for p in missing_plugins:
            cmd = PLUGIN_INSTALL_CMDS.get(p, f"(설치 명령 미등록: {p})")
            print(f"  - {p}")
            print(f"      → {cmd}")
        issues_found += len(missing_plugins)
    else:
        print(f"[OK] 필수 플러그인 {len(PLUGIN_REQUIRED)}개 모두 설치됨")

    # 공식 스킬은 Claude Code에 기본 내장 (별도 플러그인 불필요)

    # OMC (oh-my-claudecode) 설정 체크
    omc = check_omc_setup()
    if not omc["plugin"]:
        print(f"[WARN] OMC 플러그인 디렉토리 없음 → `/plugin install oh-my-claudecode` 실행 필요")
        issues_found += 1
    elif omc["issues"]:
        for issue in omc["issues"]:
            print(f"[WARN] OMC: {issue}")
            issues_found += 1
    else:
        print(f"[OK] OMC 설정 정상 (HUD 스크립트 OK, statusLine OK)")

    # GSD (get-shit-done-cc) 직접설치형 필수 시스템 체크
    gsd = check_gsd_installed()
    if gsd["local"]:
        ver = f" v{gsd['version']}" if gsd["version"] else ""
        print(f"[OK] GSD{ver} 로컬 설치됨 (.claude/commands/gsd/)")
        if gsd["global"]:
            print(f"[WARN] GSD 글로벌 중복 설치 감지 → `npx get-shit-done-cc --global --uninstall` 로 제거 권장")
            issues_found += 1
    elif gsd["global"]:
        print(f"[WARN] GSD 글로벌에만 설치됨 → 로컬 설치 권장: `npx get-shit-done-cc@latest --claude --local`")
        issues_found += 1
    else:
        print(f"[WARN] GSD 미설치 (필수) → `npx get-shit-done-cc@latest --claude --local`")
        issues_found += 1

    # C13. OMC 플러그인 비활성화 항목 탐지 및 자동 삭제
    if LOCAL_SETTINGS.exists():
        try:
            local_cfg = json.loads(LOCAL_SETTINGS.read_text(encoding='utf-8'))
            enabled_plugins = local_cfg.get('enabledPlugins', {})
            if 'oh-my-claudecode@omc' in enabled_plugins:
                issues_found += 1
                if not dry_run:
                    del enabled_plugins['oh-my-claudecode@omc']
                    if not enabled_plugins:
                        local_cfg.pop('enabledPlugins', None)
                    else:
                        local_cfg['enabledPlugins'] = enabled_plugins
                    LOCAL_SETTINGS.write_text(
                        json.dumps(local_cfg, indent=2, ensure_ascii=False),
                        encoding='utf-8'
                    )
                    issues_fixed += 1
                    print("[FIX] C13: settings.local.json에서 oh-my-claudecode@omc 항목 삭제 완료")
                else:
                    val = enabled_plugins['oh-my-claudecode@omc']
                    print(f"[WARN] C13: settings.local.json enabledPlugins.oh-my-claudecode@omc={val} → 삭제 필요")
        except Exception as e:
            log_error(f"C13: settings.local.json 읽기 실패: {e}")

    # C21. 중복 GitHub 도구 정리 — gh CLI 인증 시 github@claude-plugins-official plugin 제거
    # (guide.md §3.10 — CLI 우선 시 MCP 서버 제거 정책)
    project_settings = Path('.claude/settings.json')
    gh_authenticated = False
    try:
        # stdout/stderr 캡처 없이 returncode만 사용 (cp949 환경 인코딩 오류 회피)
        gh_check = subprocess.run(
            ['gh', 'auth', 'status'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
        gh_authenticated = gh_check.returncode == 0
    except Exception:
        pass

    if gh_authenticated and project_settings.exists():
        try:
            proj_cfg = json.loads(project_settings.read_text(encoding='utf-8'))
            enabled = proj_cfg.get('enabledPlugins', {})
            if 'github@claude-plugins-official' in enabled:
                issues_found += 1
                if not dry_run:
                    del enabled['github@claude-plugins-official']
                    proj_cfg['enabledPlugins'] = enabled
                    project_settings.write_text(
                        json.dumps(proj_cfg, indent=2, ensure_ascii=False),
                        encoding='utf-8'
                    )
                    issues_fixed += 1
                    print("[FIX] C21: settings.json에서 github@claude-plugins-official 제거 완료 (gh CLI 우선 정책, guide.md §3.10)")
                else:
                    print("[WARN] C21: gh CLI 인증됨 + github@claude-plugins-official plugin 등록 → 제거 필요 (guide.md §3.10)")
        except Exception as e:
            log_error(f"C21: settings.json 읽기 실패: {e}")

    # 12. Generate environment report
    write_env_report(tool_status, mcp_status, validation, issues_found, issues_fixed, hud_status)

    # 13. Package & CLI Update
    print("\n## 10. Package & CLI Update")
    if dry_run:
        print("[DRY-RUN] uv sync + CLI 업데이트 생략")
    else:
        success, output = run_command(["uv", "sync"], "uv sync", timeout=120)
        if success:
            print("[OK] uv sync 완료")
        else:
            print(f"[ERROR] uv sync 실패\n{output.strip()[:200]}")
        cli_ok_u = 0
        cli_fail_u = 0
        cli_new_u = 0
        for cmd, info in CLI_REGISTRY.items():
            _is_installed = check_command(cmd) or (info["method"] == "npm" and check_npm_global(info["package"]))
            if not _is_installed:
                print(f"  [NEW] {cmd}: 미설치 → 설치 중...")
                ok = _cli_install(info["package"], info["method"], cmd)
                if ok:
                    cli_new_u += 1
                    print(f"  [OK] {cmd}: 설치 완료")
                else:
                    cli_fail_u += 1
                    print(f"  [ERROR] {cmd}: 설치 실패")
                continue
            ok = _cli_update(info["package"], info["method"], cmd)
            if ok:
                cli_ok_u += 1
            else:
                cli_fail_u += 1
        print(f"  업데이트: {cli_ok_u}개 | 신규 설치: {cli_new_u}개 | 실패: {cli_fail_u}개")

    # 14. Summary
    print("\n" + "=" * 60)
    print("# Summary")
    print("=" * 60)
    print(f"\nIssues found: {issues_found}")
    print(f"Issues fixed: {issues_fixed}")

    if issues_found > issues_fixed:
        remaining = issues_found - issues_fixed
        print(f"Remaining issues: {remaining}")
        print("\n[WARN] Some issues require manual action.")
        return 1
    else:
        print("\n[OK] Development environment ready")
        return 0


def cmd_show_checklist():
    """references/checklist.md 내용 출력"""
    checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[{SKILL_NAME}] checklist.md 없음: {checklist_path}")
        return
    print(checklist_path.read_text(encoding="utf-8"))


def main():
    if len(sys.argv) > 2 and sys.argv[1].lower() == "show" and sys.argv[2].lower() == "checklist":
        cmd_show_checklist()
        return
    """Entry point: parse args and route to subcommand."""
    if show_help_if_no_args("ooenv", sys.argv[1:]):
        return 0
    if not sys.argv[1:]:
        sys.argv.append("run")
    args = sys.argv[1:]
    subcmd = args[0]
    return run_subcommand(subcmd, args[1:])


if __name__ == "__main__":
    sys.exit(main())
