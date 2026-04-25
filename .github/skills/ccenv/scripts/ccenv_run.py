#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
DOC_SOURCE = PROJECT_ROOT / "00_doc" / "d0009_env.md"
DOC_OUTPUT = PROJECT_ROOT / "00_doc" / "d0009_ccenv.md"
SKILL_VERSION = "v01"


def configure_utf8() -> None:
    import sys

    if sys.stdout.encoding and sys.stdout.encoding.lower() in {"cp949", "cp1252", "ascii"}:
        sys.stdout.reconfigure(encoding="utf-8")
    if sys.stderr.encoding and sys.stderr.encoding.lower() in {"cp949", "cp1252", "ascii"}:
        sys.stderr.reconfigure(encoding="utf-8")


@dataclass(frozen=True)
class CapabilityRow:
    name: str
    copilot_status: str
    basis: str
    note: str


def parse_markdown_table(section_text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    lines = [line.rstrip() for line in section_text.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return rows

    headers = [cell.strip() for cell in lines[0].strip("|").split("|")]
    for line in lines[2:]:
        values = [cell.strip() for cell in line.strip("|").split("|")]
        if len(values) != len(headers):
            continue
        rows.append(dict(zip(headers, values)))
    return rows


def extract_section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""
    remainder = text[start + len(heading):]
    next_heading_offset = remainder.find("\n## ")
    if next_heading_offset == -1:
        return remainder
    return remainder[:next_heading_offset]


def load_doc_state() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    if not DOC_SOURCE.exists():
        return [], []

    text = DOC_SOURCE.read_text(encoding="utf-8")
    mcp_section = extract_section(text, "## 2. MCP 서버 현황")
    plugin_section = extract_section(text, "## 3. Claude 플러그인")
    return parse_markdown_table(mcp_section), parse_markdown_table(plugin_section)


def index_rows(rows: list[dict[str, str]], key_name: str) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for row in rows:
        key = row.get(key_name, "").strip()
        if key:
            indexed[key] = row
    return indexed


def build_core_capabilities() -> list[CapabilityRow]:
    return [
        CapabilityRow("파일 읽기/수정/생성", "사용 가능", "read_file, apply_patch, create_file", "기본 편집 작업 가능"),
        CapabilityRow("코드/파일 검색", "사용 가능", "grep_search, file_search, semantic_search", "텍스트 검색과 코드 검색 가능"),
        CapabilityRow("터미널 실행", "사용 가능", "run_in_terminal, await_terminal", "Windows PowerShell 기준 실행 가능"),
        CapabilityRow("Python 환경 관리", "사용 가능", "configure_python_environment, install_python_packages", "Python 실행/설치/환경 조회 가능"),
        CapabilityRow("브라우저 자동화", "사용 가능", "mcp_playwright_browser_*", "GitHub UI 확인, 웹 테스트 가능"),
        CapabilityRow("문서/라이브러리 조회", "사용 가능", "mcp_context7_*, fetch_webpage", "최신 라이브러리 문서 조회 가능"),
        CapabilityRow("GitHub 연동", "사용 가능", "github-pull-request_*, mcp_gitkraken_*", "이슈/PR/저장소 관련 조회 가능"),
        CapabilityRow("Notebook 작업", "사용 가능", "configure_notebook, run_notebook_cell", "Jupyter 작업 가능"),
        CapabilityRow("Mermaid/디자인 도구", "사용 가능", "renderMermaidDiagram, mcp_pencil_*", "Mermaid와 Pencil 도구 사용 가능"),
        CapabilityRow("메모리/할 일 관리", "사용 가능", "memory, manage_todo_list", "세션/저장 메모리와 작업 계획 관리 가능"),
    ]


def build_plugin_crosscheck(plugin_rows: dict[str, dict[str, str]]) -> list[tuple[str, str, CapabilityRow]]:
    mapping = [
        ("context7", CapabilityRow("context7", "사용 가능", "mcp_context7_*", "최신 라이브러리 문서 조회 가능")),
        ("playwright", CapabilityRow("playwright", "사용 가능", "mcp_playwright_browser_*", "브라우저 자동화 가능")),
        ("pyright-lsp", CapabilityRow("pyright-lsp", "사용 가능", "mcp_pylance_*", "Python 분석/실행 도구로 대체 확인")),
        ("github", CapabilityRow("github", "사용 가능", "github-pull-request_*, mcp_gitkraken_*", "GitHub 관련 도구 확인")),
        ("document-skills", CapabilityRow("document-skills", "사용 가능", "docx/pdf/pptx/xlsx skills", "문서 계열 스킬 사용 가능")),
        ("frontend-design", CapabilityRow("frontend-design", "사용 가능", "frontend-design skill", "프론트엔드 디자인 스킬 사용 가능")),
        ("pencil", CapabilityRow("pencil", "사용 가능", "mcp_pencil_*", "문서상 설치 X지만 현재 세션 도구는 존재")),
        ("claude-mem", CapabilityRow("claude-mem", "부분 사용 가능", "memory tool", "동일 플러그인은 아니지만 메모리 기능은 존재")),
        ("code-review", CapabilityRow("code-review", "부분 사용 가능", "리뷰 요청 + subagent", "전용 플러그인 명령 대신 일반 리뷰 워크플로우 사용")),
        ("commit-commands", CapabilityRow("commit-commands", "부분 사용 가능", "git add/commit tools", "전용 명령 대신 일반 git 도구 사용")),
        ("feature-dev", CapabilityRow("feature-dev", "부분 사용 가능", "todo + edit + test workflow", "전용 플러그인 여부와 무관하게 구현 작업은 가능")),
        ("oh-my-claudecode", CapabilityRow("oh-my-claudecode", "부분 사용 가능", "지침/스킬/에이전트 파일", "OMC 명령 UI 자체보다 문서/규칙 기반 활용")),
        ("typescript-lsp", CapabilityRow("typescript-lsp", "확인 불가", "현재 노출 도구 직접 확인 없음", "세션 도구 목록 기준")),
        ("security-guidance", CapabilityRow("security-guidance", "확인 불가", "현재 노출 도구 직접 확인 없음", "보안 검토는 일반 워크플로우로는 가능")),
        ("paper-search-tools", CapabilityRow("paper-search-tools", "확인 불가", "현재 노출 도구 직접 확인 없음", "별도 논문 검색 스킬과는 구분")),
        ("codex", CapabilityRow("codex", "사용 불가", "현재 노출 도구 없음", "이 세션에 Codex 전용 도구는 없음")),
        ("superpowers", CapabilityRow("superpowers", "확인 불가", "구체 도구 식별 불가", "현재 세션 도구명과 직접 매칭되지 않음")),
    ]

    result: list[tuple[str, str, CapabilityRow]] = []
    for name, capability in mapping:
        doc_status = plugin_rows.get(name, {}).get("설치", "-")
        result.append((name, doc_status, capability))
    return result


def build_mcp_crosscheck(mcp_rows: dict[str, dict[str, str]]) -> list[tuple[str, str, CapabilityRow]]:
    mapping = [
        ("sequential-thinking", CapabilityRow("sequential-thinking", "확인 불가", "현재 노출 도구 직접 확인 없음", "지침상 설치 O지만 세션 도구명으로는 확인되지 않음")),
        ("desktop-commander", CapabilityRow("desktop-commander", "부분 사용 가능", "파일/터미널 기본 도구", "동일 MCP 이름 대신 기본 도구로 대체 가능")),
        ("puppeteer", CapabilityRow("puppeteer", "부분 사용 가능", "mcp_playwright_browser_*", "동일 서버는 아니지만 브라우저 자동화 기능은 존재")),
        ("postgres", CapabilityRow("postgres", "사용 불가", "현재 노출 도구 없음", "DB MCP 직접 사용 불가")),
        ("sqlite", CapabilityRow("sqlite", "사용 불가", "현재 노출 도구 없음", "DB MCP 직접 사용 불가")),
        ("taskmaster-ai", CapabilityRow("taskmaster-ai", "확인 불가", "현재 노출 도구 직접 확인 없음", "task 관련 일반 도구와는 구분")),
        ("google", CapabilityRow("google", "사용 불가", "현재 노출 도구 없음", "Google API MCP 직접 사용 불가")),
    ]

    result: list[tuple[str, str, CapabilityRow]] = []
    for name, capability in mapping:
        doc_status = mcp_rows.get(name, {}).get("설치", "-")
        result.append((name, doc_status, capability))
    return result


def render_table(headers: list[str], rows: list[list[str]]) -> str:
    header_line = "| " + " | ".join(headers) + " |"
    separator_line = "|" + "|".join(["---" for _ in headers]) + "|"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header_line, separator_line, *body])


def build_document() -> str:
    mcp_rows, plugin_rows = load_doc_state()
    indexed_mcp = index_rows(mcp_rows, "MCP 서버")
    indexed_plugins = index_rows(plugin_rows, "플러그인")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    core_rows = [
        [row.name, row.copilot_status, row.basis, row.note]
        for row in build_core_capabilities()
    ]
    plugin_crosscheck = [
        [name, doc_status, capability.copilot_status, capability.basis, capability.note]
        for name, doc_status, capability in build_plugin_crosscheck(indexed_plugins)
    ]
    mcp_crosscheck = [
        [name, doc_status, capability.copilot_status, capability.basis, capability.note]
        for name, doc_status, capability in build_mcp_crosscheck(indexed_mcp)
    ]

    direct_count = sum(1 for _, _, capability in build_plugin_crosscheck(indexed_plugins) if capability.copilot_status == "사용 가능")
    partial_count = sum(1 for _, _, capability in build_plugin_crosscheck(indexed_plugins) if capability.copilot_status == "부분 사용 가능")

    return f"""# d0009_ccenv.md - Copilot 환경 현황

## 문서 이력 관리

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| {SKILL_VERSION} | {datetime.now().strftime('%Y-%m-%d')} | ccenv run 자동 생성 |

---

## 목차

1. [문서 개요](#1-문서-개요)
2. [Copilot 직접 사용 가능 기능](#2-copilot-직접-사용-가능-기능)
3. [플러그인 교차 판정](#3-플러그인-교차-판정)
4. [MCP 교차 판정](#4-mcp-교차-판정)
5. [해석 가이드](#5-해석-가이드)

---

> 스킬: `.github/skills/ccenv/SKILL.md` | 생성 시각: {now}

## 1. 문서 개요

- 기준 문서: `00_doc/d0009_env.md`
- 관점: "설치 여부"가 아니라 "현재 GitHub Copilot 세션에서 실제로 호출 가능한가"
- 요약:
  - 플러그인 계열 직접 사용 가능 판정: {direct_count}개
  - 플러그인 계열 부분 사용 가능 판정: {partial_count}개
  - `d0009_env.md`와 현재 Copilot 세션 사이에 차이가 있음

## 2. Copilot 직접 사용 가능 기능

{render_table(["기능", "Copilot 판정", "근거", "비고"], core_rows)}

## 3. 플러그인 교차 판정

{render_table(["플러그인", "d0009_env", "Copilot 판정", "근거", "비고"], plugin_crosscheck)}

## 4. MCP 교차 판정

{render_table(["MCP", "d0009_env", "Copilot 판정", "근거", "비고"], mcp_crosscheck)}

## 5. 해석 가이드

- `사용 가능`: 현재 세션 도구나 스킬로 직접 대응 기능이 확인된 항목
- `부분 사용 가능`: 동일한 이름의 플러그인/MCP는 아니어도 Copilot 기본 도구나 다른 통합으로 대체 가능한 항목
- `확인 불가`: 문서에는 있으나 현재 세션 도구 목록으로 직접 확인되지 않은 항목
- `사용 불가`: 현재 세션 도구로는 직접 호출할 수 없는 항목
- `repository size`와 `billing storage`는 별개이며, 이 문서는 Copilot capability 관점 문서다
"""


def run() -> int:
    DOC_OUTPUT.write_text(build_document(), encoding="utf-8")
    print(f"[ccenv run] wrote {DOC_OUTPUT}")
    return 0


def status() -> int:
    print("[ccenv status]")
    print(f"- source: {DOC_SOURCE}")
    print(f"- output: {DOC_OUTPUT}")
    print("- purpose: summarize what is actually usable in the current Copilot environment")
    return 0


def version() -> int:
    print(f"ccenv {SKILL_VERSION}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Copilot environment summary generator")
    parser.add_argument(
        "command",
        nargs="?",
        default="run",
        choices=("run", "status", "version"),
    )
    return parser.parse_args()


def main() -> int:
    configure_utf8()
    args = parse_args()
    if args.command == "run":
        return run()
    if args.command == "status":
        return status()
    return version()


if __name__ == "__main__":
    raise SystemExit(main())