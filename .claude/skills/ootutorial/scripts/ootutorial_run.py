"""ootutorial - 프로젝트 튜토리얼 생성 스크립트

OAIS 프로젝트의 oo 스킬, SC 명령어, 플러그인에 대한
튜토리얼 문서를 00_doc/tutorial/에 생성한다.

Usage:
    uv run python .claude/skills/ootutorial/scripts/ootutorial_run.py [run|status]
    uv run python .claude/skills/ootutorial/scripts/ootutorial_run.py run --skill <name>
    uv run python .claude/skills/ootutorial/scripts/ootutorial_run.py run --category <cat>
"""

import argparse
import io
import json
import re
import sys
import sys as _sys
if _sys.stdout.encoding and _sys.stdout.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stdout.reconfigure(encoding='utf-8')
if _sys.stderr.encoding and _sys.stderr.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stderr.reconfigure(encoding='utf-8')

# --- oo_common inline ---
from pathlib import Path
import re as _re
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
from datetime import datetime
from pathlib import Path

# Windows cp949 인코딩 문제 방지
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# 프로젝트 루트
ROOT = Path(__file__).resolve().parents[4]  # .claude/skills/ootutorial/scripts/ → ROOT
SKILLS_DIR = ROOT / ".claude" / "skills"
COMMANDS_DIR = ROOT / ".claude" / "commands" / "sc"
MCP_JSON = ROOT / ".mcp.json"
TUTORIAL_DIR = ROOT / "00_doc" / "tutorial"
SKILLS_OUT = TUTORIAL_DIR / "skills"
COMMANDS_OUT = TUTORIAL_DIR / "commands"
PLUGINS_OUT = TUTORIAL_DIR / "plugins"
TEMPLATES_DIR = TUTORIAL_DIR / "templates"
OOTUTORIAL_VERSION = "v02"
DOC_DIR = ROOT / "00_doc"


def ensure_dirs():
    """출력 디렉터리 생성."""
    for d in [TUTORIAL_DIR, SKILLS_OUT, COMMANDS_OUT, PLUGINS_OUT]:
        d.mkdir(parents=True, exist_ok=True)


def get_oo_skills() -> list[str]:
    """oo* 스킬 이름 목록 반환."""
    if not SKILLS_DIR.exists():
        return []
    return sorted(
        d.name for d in SKILLS_DIR.iterdir()
        if d.is_dir() and d.name.startswith("oo") and (d / "SKILL.md").exists()
    )


def parse_skill_md(skill_name: str) -> dict:
    """SKILL.md에서 메타데이터와 본문 파싱."""
    skill_path = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_path.exists():
        return {}

    text = skill_path.read_text(encoding="utf-8")
    result = {"name": skill_name, "content": text}

    # frontmatter 파싱
    fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        for line in fm.split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip().strip('"')
                if key == "description":
                    result["description"] = val
                elif key == "version":
                    result["version"] = val
                elif key == "category":
                    result["category"] = val
        # metadata 내부의 version/category
        meta_match = re.search(r"metadata:\s*\n\s+version:\s*\"?([^\"]+)\"?\s*\n\s+category:\s*\"?([^\"]+)\"?", fm)
        if meta_match:
            result["version"] = meta_match.group(1)
            result["category"] = meta_match.group(2)

    return result


def load_template(name: str) -> str | None:
    """templates/ 디렉토리에서 템플릿 로드. 없으면 None."""
    path = TEMPLATES_DIR / f"{name}_template.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def extract_sections(body: str) -> dict[str, str]:
    """SKILL.md 본문에서 ## 섹션별 내용 추출."""
    sections: dict[str, str] = {}
    current_key = ""
    current_lines: list[str] = []

    for line in body.split("\n"):
        if line.startswith("## "):
            if current_key:
                sections[current_key] = "\n".join(current_lines).strip()
            current_key = line[3:].strip().lower()
            current_lines = []
        else:
            current_lines.append(line)

    if current_key:
        sections[current_key] = "\n".join(current_lines).strip()

    return sections


def extract_commands_table(body: str) -> str:
    """본문에서 명령어 테이블 추출."""
    lines = body.split("\n")
    table_lines = []
    in_table = False
    for line in lines:
        if "|" in line and ("명령어" in line or "설명" in line or in_table):
            in_table = True
            table_lines.append(line)
        elif in_table and "|" in line:
            table_lines.append(line)
        elif in_table and "|" not in line:
            break
    return "\n".join(table_lines) if table_lines else "(명령어 테이블 없음)"


def extract_related_skills(body: str) -> str:
    """본문에서 관련 스킬/문서 추출."""
    sections = extract_sections(body)
    for key in ["관련", "관련 문서", "관련 스킬", "관련 명령어"]:
        if key in sections:
            return sections[key]
    return "(관련 스킬 정보 없음)"


def find_section(sections: dict[str, str], *candidates: str) -> str:
    """여러 후보 키 중 첫 번째 매칭되는 섹션 내용 반환."""
    for key in candidates:
        # 정확히 일치
        if key in sections:
            return sections[key]
        # 번호 접두사 포함 (예: "1. 개요" → "개요" 매칭)
        for sk, sv in sections.items():
            cleaned = re.sub(r"^\d+\.\s*", "", sk)
            if cleaned == key:
                return sv
    return ""


def build_examples(skill_name: str, sections: dict[str, str], body: str) -> str:
    """스킬의 사용 예시를 SKILL.md에서 최대한 추출하여 구성."""
    # 1. 기존 사용 예시 섹션이 있으면 그대로 사용
    examples = find_section(sections, "사용 예시", "examples", "예시")
    if examples:
        return examples

    # 2. SKILL.md에서 서브명령어 정보를 기반으로 구체적 예시 생성
    result_parts = []

    # 서브명령어 테이블에서 주요 명령어 추출
    cmd_table = extract_commands_table(body)
    custom_cmds = []
    for line in cmd_table.split("\n"):
        match = re.search(r"`" + skill_name + r"\s+(\w[\w\s]*?)`", line)
        if match:
            cmd = match.group(1).strip()
            if cmd not in ("help", "version", "status", "check", "show checklist", "add checklist"):
                custom_cmds.append(cmd)

    # 기본 명령어 예시
    result_parts.append(f"### 기본 사용")
    result_parts.append(f"```bash")
    result_parts.append(f"# 전체 실행")
    result_parts.append(f"{skill_name} run")
    result_parts.append(f"```")

    # 커스텀 명령어 예시
    if custom_cmds:
        result_parts.append(f"\n### 서브명령어 활용")
        result_parts.append(f"```bash")
        for cmd in custom_cmds[:5]:
            # 설명 추출
            desc_match = re.search(r"`" + skill_name + r"\s+" + re.escape(cmd) + r"`\s*\|\s*(.+?)(\s*\||$)", cmd_table)
            desc = desc_match.group(1).strip() if desc_match else ""
            comment = f"  # {desc}" if desc else ""
            result_parts.append(f"{skill_name} {cmd}{comment}")
        result_parts.append(f"```")

    # 옵션이 있으면 추가
    options = find_section(sections, "옵션", "일반 옵션", "options")
    if options:
        result_parts.append(f"\n### 옵션")
        result_parts.append(options)

    # 스크립트 직접 실행 예시 (scripts/ 참조가 있으면)
    script_match = re.search(r"uv run python\s+([^\s]+\.py)(?:\s+(\w+))?", body)
    if script_match:
        script_path = script_match.group(1)
        result_parts.append(f"\n### 스크립트 직접 실행")
        result_parts.append(f"```bash")
        result_parts.append(f"uv run python {script_path}")
        result_parts.append(f"```")

    return "\n".join(result_parts)


def build_details(sections: dict[str, str]) -> str:
    """SKILL.md의 핵심 상세 섹션들을 수집하여 반환."""
    detail_parts = []

    # 주요 상세 섹션 후보들 (번호 접두사 있는 것도 포함)
    detail_candidates = [
        ("tdd 사이클", "TDD 사이클"),
        ("반복/에스컬레이션", "반복/에스컬레이션"),
        ("체크 대상", "체크 대상"),
        ("커밋 형식", "커밋 형식"),
        ("자막 우선 순위", "자막 우선 순위"),
        ("stt 서브명령어", "STT 서브명령어"),
        ("4단계 상태 체계", "4단계 상태 체계"),
        ("결과 기록", "결과 기록"),
        ("주의사항", "주의사항"),
        ("ai 실행 규칙", "AI 실행 규칙"),
        ("에러 처리", "에러 처리"),
        ("의존성", "의존성"),
        ("실행 방법", "실행 방법"),
        ("검증 기준", "검증 기준"),
        ("표준용어 검증", "표준용어 검증"),
        ("optimize", "optimize"),
    ]

    for search_key, display_title in detail_candidates:
        content = find_section(sections, search_key)
        if content:
            detail_parts.append(f"### {display_title}\n\n{content}")

    # 번호 붙은 섹션 중 아직 수집하지 않은 것들
    skip_keys = {
        "개요", "overview", "서브명령어", "명령어", "워크플로우", "workflow",
        "관련", "관련 문서", "관련 스킬", "관련 명령어", "서브에이전트",
        "사용 예시", "examples", "입출력", "출력", "출력 구조", "변경 이력",
        "문서 이력 관리", "help 서브명령어 표준", "version 서브명령어 표준",
    }
    # 이미 수집한 키 추가
    skip_keys.update(k for k, _ in detail_candidates)

    for key, val in sections.items():
        cleaned = re.sub(r"^\d+\.\s*", "", key)
        if cleaned.lower() not in skip_keys and cleaned not in skip_keys:
            # 매우 짧은 섹션은 스킵
            if len(val) > 30:
                detail_parts.append(f"### {cleaned}\n\n{val}")

    if not detail_parts:
        return "(상세 정보는 SKILL.md 참조)"

    return "\n\n".join(detail_parts[:6])  # 최대 6개 섹션


def build_why_section(skill_name: str, desc: str, sections: dict[str, str]) -> str:
    """'왜 필요한가' 섹션 생성 - SKILL.md 개요 + PRD 시나리오에서 추출."""
    parts = []

    # SKILL.md 개요에서 목적 추출
    overview = find_section(sections, "개요", "overview")
    if overview:
        # **목적**: 이후 텍스트 추출
        purpose_match = re.search(r"\*\*목적\*\*:\s*(.+?)(?:\n|$)", overview)
        if purpose_match:
            parts.append(purpose_match.group(1).strip())
        # **핵심 기능**: 리스트 추출
        features = re.findall(r"^- (.+)$", overview, re.MULTILINE)
        if features:
            parts.append("\n**이런 상황에서 사용합니다:**")
            for f in features[:5]:
                parts.append(f"- {f}")

    if not parts:
        parts.append(desc if desc else f"`{skill_name}` 스킬의 기능을 활용할 수 있습니다.")

    # PRD에서 관련 시나리오 찾기 (SP별 PRD 검색)
    for prd_file in sorted(DOC_DIR.glob("d*0001_prd.md")):
        try:
            prd_text = prd_file.read_text(encoding="utf-8")
            if skill_name in prd_text.lower():
                # 시나리오 섹션에서 관련 내용 추출
                scenario_match = re.search(
                    r"### 시나리오[^#]*?" + re.escape(skill_name) + r"[^#]*?```(.*?)```",
                    prd_text, re.DOTALL | re.IGNORECASE
                )
                if scenario_match:
                    parts.append(f"\n**PRD 시나리오 ({prd_file.name}):**")
                    parts.append(f"```\n{scenario_match.group(1).strip()[:300]}\n```")
                    break
        except (OSError, UnicodeDecodeError):
            continue

    return "\n".join(parts)


def build_faq_section(skill_name: str, sections: dict[str, str], body: str) -> str:
    """FAQ 섹션 생성 - 에러 처리, 주의사항, 의존성에서 추출."""
    faqs = []

    # 에러 처리 섹션에서 FAQ 추출
    error_section = find_section(sections, "에러 처리", "error handling", "ai 실행 규칙")
    if error_section:
        error_items = re.findall(r"^- (.+)$", error_section, re.MULTILINE)
        for item in error_items[:3]:
            parts = item.split(":", 1) if ":" in item else item.split("→", 1)
            if len(parts) == 2:
                faqs.append(f"**Q: {parts[0].strip()}?**\n\nA: {parts[1].strip()}\n")

    # 주의사항에서 FAQ 추출
    caution = find_section(sections, "주의사항", "참고", "비고")
    if caution:
        caution_items = re.findall(r"^- (.+)$", caution, re.MULTILINE)
        for item in caution_items[:2]:
            faqs.append(f"**Q: {item}**\n\nA: SKILL.md 참조\n")

    # 의존성 정보
    deps = find_section(sections, "의존성", "dependencies", "핵심 의존성")
    if deps:
        faqs.append(f"**Q: 필요한 의존성은?**\n\n{deps}\n")

    if not faqs:
        faqs.append("> 실전 사용 중 FAQ가 축적되면 이 섹션에 추가됩니다.\n>\n> `ootutorial add-faq {skill_name} \"질문\" \"답변\"` 으로 추가 가능")

    return "\n".join(faqs)


def generate_skill_tutorial(skill_name: str) -> str:
    """스킬 SKILL.md를 템플릿 기반 튜토리얼로 변환 (v02: Why+FAQ 추가)."""
    info = parse_skill_md(skill_name)
    if not info:
        return ""

    version = info.get("version", "?")
    category = info.get("category", "?")
    desc = info.get("description", "")
    short_desc = desc.split("'")[0].strip() if "'" in desc else desc

    content = info.get("content", "")
    body = re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL).strip()
    sections = extract_sections(body)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    template = load_template("skill")
    if template:
        # 개요
        overview = find_section(sections, "개요", "overview") or short_desc

        # 워크플로우
        workflow = find_section(sections, "워크플로우", "workflow", "실행 프로세스")
        if not workflow:
            workflow = "(워크플로우 정보는 SKILL.md 참조)"

        # 사용 예시 (구체적 추출)
        examples = build_examples(skill_name, sections, body)

        # 주요 기능 상세
        details = build_details(sections)

        # 입출력
        io_section = find_section(
            sections, "입출력", "출력", "입출력 경로", "출력 구조",
            "파일 구조", "결과 파일 형식"
        )
        if not io_section:
            io_section = "(입출력 정보는 SKILL.md 참조)"

        # 서브에이전트
        subagents = find_section(sections, "서브에이전트", "서브에이전트 매핑", "서브에이전트 활용")
        if not subagents:
            subagents = "(서브에이전트 정보 없음)"

        # Why 섹션 (v02)
        why_section = build_why_section(skill_name, short_desc, sections)

        # FAQ 섹션 (v02)
        faq_section = build_faq_section(skill_name, sections, body)

        tutorial = template.replace("{skill_name}", skill_name)
        tutorial = tutorial.replace("{description}", short_desc)
        tutorial = tutorial.replace("{version}", version)
        tutorial = tutorial.replace("{category}", category)
        tutorial = tutorial.replace("{why_section}", why_section)
        tutorial = tutorial.replace("{overview}", overview)
        # 명령어 섹션 기반 추출 (이력 테이블 오반응 방지)
        commands_content = find_section(
            sections,
            "명령어", "서브명령어", "commands", "명령어 목록", "서브명령어 목록",
            "명령어 정의", "명령어 체계"
        )
        if not commands_content:
            commands_content = extract_commands_table(body)
        if not commands_content:
            commands_content = "(명령어 정보는 SKILL.md 참조)"
        tutorial = tutorial.replace("{commands_table}", commands_content)
        tutorial = tutorial.replace("{examples}", examples)
        tutorial = tutorial.replace("{workflow}", workflow)
        tutorial = tutorial.replace("{details}", details)
        tutorial = tutorial.replace("{io_section}", io_section)
        tutorial = tutorial.replace("{faq_section}", faq_section)
        tutorial = tutorial.replace("{subagents}", subagents)
        tutorial = tutorial.replace("{related_skills}", extract_related_skills(body))
        tutorial = tutorial.replace("{generated_at}", now)
        tutorial = tutorial.replace("{ootutorial_version}", OOTUTORIAL_VERSION)
    else:
        # 폴백: 기존 방식
        tutorial = f"# {skill_name} Tutorial\n\n"
        tutorial += f"> {short_desc} | 버전: {version} | 카테고리: {category}\n\n"
        tutorial += body
        tutorial += f"\n\n---\n\n> 생성일: {now} | ootutorial {OOTUTORIAL_VERSION}\n"

    return tutorial


def generate_command_tutorial(cmd_path: Path) -> str:
    """SC 명령어 파일을 템플릿 기반 튜토리얼로 변환."""
    text = cmd_path.read_text(encoding="utf-8")
    name = cmd_path.stem
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    template = load_template("command")
    if template:
        # 본문에서 개요 추출 (첫 번째 단락)
        lines = text.strip().split("\n")
        overview_lines = []
        for line in lines:
            if line.startswith("#"):
                continue
            if line.strip() == "" and overview_lines:
                break
            if line.strip():
                overview_lines.append(line)
        overview = "\n".join(overview_lines) if overview_lines else text[:200]

        tutorial = template.replace("{command_name}", name)
        tutorial = tutorial.replace("{overview}", overview)
        tutorial = tutorial.replace("{options_table}", "(원본 참조: `.claude/commands/sc/{}.md`)".format(name))
        tutorial = tutorial.replace("{examples}", f"```bash\n/{name} [target] [flags]\n```")
        tutorial = tutorial.replace("{related_skills}", "(관련 스킬은 CLAUDE.md 참조)")
        tutorial = tutorial.replace("{generated_at}", now)
        tutorial = tutorial.replace("{ootutorial_version}", OOTUTORIAL_VERSION)
    else:
        tutorial = f"# SC 명령어: {name}\n\n"
        tutorial += text
        tutorial += f"\n\n---\n\n> 생성일: {now} | ootutorial {OOTUTORIAL_VERSION}\n"

    return tutorial


def generate_plugin_tutorials() -> list[tuple[str, str]]:
    """MCP 플러그인 튜토리얼을 템플릿 기반으로 생성."""
    results = []
    if not MCP_JSON.exists():
        return results

    try:
        data = json.loads(MCP_JSON.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return results

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    template = load_template("plugin")
    servers = data.get("mcpServers", {})

    for name, config in servers.items():
        cmd = config.get("command", "?")
        args_list = config.get("args", [])
        args = " ".join(args_list)

        if template:
            tutorial = template.replace("{plugin_name}", name)
            tutorial = tutorial.replace("{overview}", f"`{name}` MCP 서버. 프로젝트 `.mcp.json`에 등록되어 자동 연결됩니다.")
            tutorial = tutorial.replace("{command}", cmd)
            tutorial = tutorial.replace("{args}", args)
            tutorial = tutorial.replace("{tools_table}", "(MCP 도구는 세션 연결 시 자동 로드)")
            tutorial = tutorial.replace("{examples}", f"`.mcp.json`에 등록 후 자동 사용 가능")
            tutorial = tutorial.replace("{scenarios}", f"- `--seq` 플래그로 활성화\n- 복잡한 분석/디버깅 시 자동 활성화")
            tutorial = tutorial.replace("{generated_at}", now)
            tutorial = tutorial.replace("{ootutorial_version}", OOTUTORIAL_VERSION)
        else:
            tutorial = f"# MCP 플러그인: {name}\n\n"
            tutorial += f"## 설정\n\n| 항목 | 값 |\n|------|----|\n"
            tutorial += f"| command | `{cmd}` |\n| args | `{args}` |\n\n"
            tutorial += f"## 사용법\n\n프로젝트 `.mcp.json`에 등록되어 자동 연결됩니다.\n"
            tutorial += f"\n---\n\n> 생성일: {now} | ootutorial {OOTUTORIAL_VERSION}\n"

        results.append((name, tutorial))

    return results


def generate_overview() -> str:
    """프로젝트 전체 개요 튜토리얼 생성."""
    skills = get_oo_skills()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    overview = f"""# OAIS 프로젝트 튜토리얼

> OAIS (One AI System) 프로젝트의 Claude Code 환경 사용 가이드

## 프로젝트 구조

| 폴더 | 설명 |
|------|------|
| `00_doc/` | 프로젝트 문서 (PRD, TODO, 이력 등) |
| `01_obsidian/` | 옵시디언 노트 (SP01) |
| `02_pycode/` | Python/알고리즘 코드 (SP02) |
| `03_paper/` | 논문 관리 (SP03) |
| `04_scraping/` | 스크래핑/유튜브 (SP04) |
| `.claude/` | Claude Code 설정, 스킬, 에이전트 |

## 시작하기

1. **세션 시작**: `oostart run` (매 세션 첫 실행)
2. **도움말**: `oohelp` (전체 스킬 목록)
3. **환경 점검**: `ooenv run` (환경 검증)

## oo 스킬 ({len(skills)}개)

| 스킬 | 설명 |
|------|------|"""

    for s in skills:
        info = parse_skill_md(s)
        desc = info.get("description", "")
        short = desc.split("'")[0].strip() if "'" in desc else desc[:40]
        overview += f"\n| `{s}` | {short} |"

    overview += f"""

## SC 명령어

| 명령어 | 경로 |
|--------|------|"""

    if COMMANDS_DIR.exists():
        for f in sorted(COMMANDS_DIR.glob("*.md")):
            overview += f"\n| `{f.stem}` | `.claude/commands/sc/{f.name}` |"

    overview += f"""

## 공통 서브명령어

모든 oo 스킬은 다음 서브명령어를 지원합니다:

| 서브명령어 | 설명 |
|-----------|------|
| `help` | 서브명령어 목록 |
| `version` | 버전 정보 |
| `status` | 상태 확인 |
| `check` | 체크리스트 검증 |
| `show checklist` | 체크리스트 표시 |
| `add checklist "항목"` | 체크리스트 추가 |
| `run` | 기본 실행 |
| `tutorial` | 사용법 안내 |

---

> 생성일: {now} | ootutorial {OOTUTORIAL_VERSION}
"""
    return overview


def generate_readme(skills: list[str], commands: list[str], plugins: list[str]) -> str:
    """README.md 인덱스 생성."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    readme = f"""# OAIS 튜토리얼 인덱스

> 전체 튜토리얼 목차 | 최종 갱신: {now}

## 개요

- [프로젝트 전체 가이드](00_overview.md)

## oo 스킬 ({len(skills)}개)

| 스킬 | 튜토리얼 |
|------|---------|"""

    for s in skills:
        readme += f"\n| `{s}` | [skills/{s}.md](skills/{s}.md) |"

    readme += f"""

## SC 명령어 ({len(commands)}개)

| 명령어 | 튜토리얼 |
|--------|---------|"""

    for c in commands:
        readme += f"\n| `{c}` | [commands/{c}.md](commands/{c}.md) |"

    readme += f"""

## 플러그인 ({len(plugins)}개)

| 플러그인 | 튜토리얼 |
|----------|---------|"""

    for p in plugins:
        readme += f"\n| `{p}` | [plugins/{p}.md](plugins/{p}.md) |"

    readme += f"""

---

> ootutorial v01 | 자동 생성됨
"""
    return readme


def cmd_run(args):
    """run 서브명령어 실행."""
    ensure_dirs()

    stats = {"created": 0, "skipped": 0, "errors": 0}

    # 카테고리 필터
    categories = ["overview", "skills", "commands", "plugins"]
    if args.category:
        categories = [args.category]

    # 특정 스킬만
    if args.skill:
        categories = ["skills"]

    skill_names = []
    cmd_names = []
    plugin_names = []

    # 1. 개요
    if "overview" in categories:
        print("[1/4] 개요 튜토리얼 생성...")
        overview = generate_overview()
        (TUTORIAL_DIR / "00_overview.md").write_text(overview, encoding="utf-8")
        stats["created"] += 1

    # 2. oo 스킬
    if "skills" in categories:
        skills = get_oo_skills()
        if args.skill:
            skills = [args.skill] if args.skill in skills else []
            if not skills:
                print(f"  ❌ 스킬 '{args.skill}' 없음")
                stats["errors"] += 1

        print(f"[2/4] oo 스킬 튜토리얼 생성 ({len(skills)}개)...")
        for s in skills:
            try:
                tutorial = generate_skill_tutorial(s)
                if tutorial:
                    (SKILLS_OUT / f"{s}.md").write_text(tutorial, encoding="utf-8")
                    skill_names.append(s)
                    stats["created"] += 1
                    print(f"  ✅ {s}")
                else:
                    stats["skipped"] += 1
                    print(f"  ⚠️ {s} (SKILL.md 없음)")
            except Exception as e:
                stats["errors"] += 1
                print(f"  ❌ {s}: {e}")
    else:
        # 기존 파일에서 스킬 목록 수집
        skill_names = [f.stem for f in SKILLS_OUT.glob("*.md")]

    # 3. SC 명령어
    if "commands" in categories:
        cmds = sorted(COMMANDS_DIR.glob("*.md")) if COMMANDS_DIR.exists() else []
        print(f"[3/4] SC 명령어 튜토리얼 생성 ({len(cmds)}개)...")
        for cmd_path in cmds:
            if cmd_path.is_file():
                try:
                    tutorial = generate_command_tutorial(cmd_path)
                    (COMMANDS_OUT / cmd_path.name).write_text(tutorial, encoding="utf-8")
                    cmd_names.append(cmd_path.stem)
                    stats["created"] += 1
                    print(f"  ✅ {cmd_path.stem}")
                except Exception as e:
                    stats["errors"] += 1
                    print(f"  ❌ {cmd_path.stem}: {e}")
    else:
        cmd_names = [f.stem for f in COMMANDS_OUT.glob("*.md")]

    # 4. 플러그인
    if "plugins" in categories:
        print("[4/4] 플러그인 튜토리얼 생성...")
        plugin_tutorials = generate_plugin_tutorials()
        for name, tutorial in plugin_tutorials:
            try:
                (PLUGINS_OUT / f"{name}.md").write_text(tutorial, encoding="utf-8")
                plugin_names.append(name)
                stats["created"] += 1
                print(f"  ✅ {name}")
            except Exception as e:
                stats["errors"] += 1
                print(f"  ❌ {name}: {e}")
    else:
        plugin_names = [f.stem for f in PLUGINS_OUT.glob("*.md")]

    # 5. Orphan 정리 (스킬/명령어가 삭제된 경우 튜토리얼도 삭제)
    if "skills" in categories and not args.skill:
        current_skills = set(get_oo_skills())
        for f in SKILLS_OUT.glob("*.md"):
            if f.stem not in current_skills:
                f.unlink()
                stats["deleted"] = stats.get("deleted", 0) + 1
                print(f"  🗑 삭제(orphan): skills/{f.name}")

    if "commands" in categories:
        current_cmds = set()
        if COMMANDS_DIR.exists():
            current_cmds = {p.stem for p in COMMANDS_DIR.glob("*.md")}
        for f in COMMANDS_OUT.glob("*.md"):
            if f.stem not in current_cmds:
                f.unlink()
                stats["deleted"] = stats.get("deleted", 0) + 1
                print(f"  🗑 삭제(orphan): commands/{f.name}")

    # 6. README 인덱스
    if not skill_names:
        skill_names = [f.stem for f in SKILLS_OUT.glob("*.md")]
    if not cmd_names:
        cmd_names = [f.stem for f in COMMANDS_OUT.glob("*.md")]
    if not plugin_names:
        plugin_names = [f.stem for f in PLUGINS_OUT.glob("*.md")]

    readme = generate_readme(skill_names, cmd_names, plugin_names)
    (TUTORIAL_DIR / "README.md").write_text(readme, encoding="utf-8")

    # 결과 요약
    print(f"\n{'='*50}")
    print(f"ootutorial 완료")
    print(f"  생성: {stats['created']}건")
    print(f"  스킵: {stats['skipped']}건")
    print(f"  오류: {stats['errors']}건")
    if stats.get("deleted"):
        print(f"  삭제(orphan): {stats['deleted']}건")
    print(f"  출력: 00_doc/tutorial/")


def cmd_status():
    """status 서브명령어."""
    skills = get_oo_skills()
    existing = [f.stem for f in SKILLS_OUT.glob("*.md")] if SKILLS_OUT.exists() else []
    cmds = [f.stem for f in COMMANDS_OUT.glob("*.md")] if COMMANDS_OUT.exists() else []
    plugins = [f.stem for f in PLUGINS_OUT.glob("*.md")] if PLUGINS_OUT.exists() else []

    print("ootutorial 현황")
    print(f"  oo 스킬: {len(existing)}/{len(skills)}개 생성됨")
    print(f"  SC 명령어: {len(cmds)}개 생성됨")
    print(f"  플러그인: {len(plugins)}개 생성됨")

    missing = set(skills) - set(existing)
    if missing:
        print(f"  미생성 스킬: {', '.join(sorted(missing))}")


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
    # help 분기 (argparse 전에 처리)
    if len(sys.argv) > 1 and sys.argv[1] in ("help", "-h", "--help"):
        _print_skill_help("ootutorial")
        return

    parser = argparse.ArgumentParser(description="ootutorial - 프로젝트 튜토리얼 생성")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="튜토리얼 생성 실행")
    run_parser.add_argument("--skill", help="특정 oo 스킬만 생성")
    run_parser.add_argument("--category", choices=["overview", "skills", "commands", "plugins"],
                           help="특정 카테고리만 생성")

    subparsers.add_parser("status", help="현황 표시")

    subparsers.add_parser("check", help="체크리스트/현황 표시 (status의 alias)")

    args = parser.parse_args()

    if args.command == "help" or (len(sys.argv) > 1 and sys.argv[1] in ("help", "-h")):
        print("ootutorial [run|status|check|help]\n프로젝트 튜토리얼 생성")
        return

    if args.command == "run" or args.command is None:
        # 서브명령어 없이 실행하면 run으로 기본 동작
        if args.command is None:
            args.skill = None
            args.category = None
        cmd_run(args)
    elif args.command == "status":
        cmd_status()
    elif args.command == "check":
        cmd_status()


if __name__ == "__main__":
    main()
