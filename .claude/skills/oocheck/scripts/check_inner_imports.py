#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_inner_imports.py

함수/메서드 내부의 import 구문으로 인한 UnboundLocalError 위험 감지 (AST 정적 분석).

Python은 함수 스코프 전체를 컴파일 타임에 스캔하여 `import X`가 있으면
`X`를 로컬 변수로 취급한다. import 이전 라인에서 X를 사용하면
런타임에 UnboundLocalError가 발생한다.

감지 기준:
  [ERROR]   함수 내부에 import X가 있고, 그 이전 라인에서 X를 이미 사용한 경우
  [WARNING] 함수 내부에 import X만 있는 경우 (import 이전 사용은 없지만 위험 패턴)

사용법:
    python check_inner_imports.py [파일_또는_폴더] [옵션]
    python check_inner_imports.py 02_poc_server/pages/
    python check_inner_imports.py oais/
    python check_inner_imports.py --error-only     # [ERROR]만 출력
    python check_inner_imports.py --json           # JSON 출력

예시:
    uv run python .claude/skills/oocheck/scripts/check_inner_imports.py 02_poc_server/pages/
"""

import ast
import sys
import json
import argparse
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding and sys.stderr.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    sys.stderr.reconfigure(encoding='utf-8')


def get_import_names(node: ast.stmt) -> list[str]:
    """import 구문에서 최상위 모듈 이름 추출."""
    names = []
    if isinstance(node, ast.Import):
        for alias in node.names:
            # import oais.session → 'oais'
            names.append(alias.asname if alias.asname else alias.name.split('.')[0])
    elif isinstance(node, ast.ImportFrom):
        # from oais import session → 'session'
        for alias in node.names:
            names.append(alias.asname if alias.asname else alias.name)
    return names


def get_used_names_before_line(func_node: ast.FunctionDef, target_line: int) -> set[str]:
    """함수 바디에서 target_line 이전에 사용된 이름 집합 반환 (annotations 제외).

    func_node 전체가 아닌 func_node.body만 walk하여
    함수 시그니처의 타입 어노테이션을 "사용"으로 오탐하지 않는다.
    (from __future__ import annotations 환경에서 어노테이션은 런타임 미평가)
    """
    used = set()
    for stmt in func_node.body:
        for node in ast.walk(stmt):
            if getattr(node, 'lineno', None) is None:
                continue
            if node.lineno >= target_line:
                continue
            # Name 노드: 변수·함수·모듈 이름 직접 참조
            if isinstance(node, ast.Name):
                used.add(node.id)
            # Attribute 노드의 value가 Name인 경우: oais.ui → 'oais'
            elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                used.add(node.value.id)
    return used


def is_in_type_checking_block(import_node: ast.stmt, module_body: list) -> bool:
    """TYPE_CHECKING 블록 내부 import 여부 확인 (정상 패턴 제외)."""
    for node in ast.walk(ast.Module(body=module_body, type_ignores=[])):
        if not isinstance(node, ast.If):
            continue
        # if TYPE_CHECKING: 패턴
        test = node.test
        is_type_checking = (
            (isinstance(test, ast.Name) and test.id == 'TYPE_CHECKING') or
            (isinstance(test, ast.Attribute) and test.attr == 'TYPE_CHECKING')
        )
        if is_type_checking:
            for child in ast.walk(node):
                if child is import_node:
                    return True
    return False


def collect_functions(tree: ast.Module) -> list[ast.FunctionDef]:
    """모듈 전체에서 모든 함수/메서드 수집 (중첩 함수 포함)."""
    funcs = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs.append(node)
    return funcs


def analyze_file(filepath: Path) -> list[dict]:
    """파일 하나를 분석하여 이슈 목록 반환."""
    issues = []
    try:
        source = filepath.read_text(encoding='utf-8')
    except (UnicodeDecodeError, OSError):
        return issues

    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:
        return issues

    module_body = tree.body

    for func in collect_functions(tree):
        func_start = func.lineno
        func_name = func.name

        # 함수 직접 자식 노드 중 import 구문만 추출 (중첩 함수 내부 제외)
        direct_imports = [
            node for node in func.body
            if isinstance(node, (ast.Import, ast.ImportFrom))
        ]

        for imp in direct_imports:
            # TYPE_CHECKING 블록 내부는 정상 패턴 → 제외
            if is_in_type_checking_block(imp, module_body):
                continue

            import_line = imp.lineno
            imported_names = get_import_names(imp)

            for name in imported_names:
                used_before = get_used_names_before_line(func, import_line)

                if name in used_before:
                    # import 이전에 같은 이름 사용 → UnboundLocalError 확정
                    level = 'ERROR'
                    message = (
                        f"함수 '{func_name}' 내부에서 '{name}'을 "
                        f"line {import_line}에서 import하기 전에 이미 사용함 "
                        f"→ UnboundLocalError 발생"
                    )
                else:
                    # import만 함수 내부에 있음 → 잠재적 위험
                    level = 'WARNING'
                    message = (
                        f"함수 '{func_name}' 내부 line {import_line}에서 "
                        f"'import {name}' — 파일 상단으로 이동 권장"
                    )

                # import 구문 텍스트
                import_text = ast.unparse(imp) if hasattr(ast, 'unparse') else str(imp)

                issues.append({
                    'level': level,
                    'file': str(filepath),
                    'line': import_line,
                    'func': func_name,
                    'func_start': func_start,
                    'name': name,
                    'import': import_text,
                    'message': message,
                })

    return issues


def scan_target(target: Path, error_only: bool = False) -> list[dict]:
    """파일 또는 폴더를 재귀 스캔."""
    all_issues = []

    if target.is_file():
        files = [target] if target.suffix == '.py' else []
    else:
        files = sorted(target.rglob('*.py'))

    # 제외 패턴
    exclude_patterns = {'__pycache__', '.venv', 'venv', 'node_modules', '.git', 'build', 'dist'}

    filtered = [
        f for f in files
        if not any(part in exclude_patterns for part in f.parts)
    ]

    for filepath in filtered:
        issues = analyze_file(filepath)
        if error_only:
            issues = [i for i in issues if i['level'] == 'ERROR']
        all_issues.extend(issues)

    return all_issues


def print_issues(issues: list[dict], target: str) -> None:
    """이슈를 사람이 읽기 쉬운 형태로 출력."""
    errors = [i for i in issues if i['level'] == 'ERROR']
    warnings = [i for i in issues if i['level'] == 'WARNING']

    print(f"\n=== check_inner_imports 스캔 결과: {target} ===\n")

    if not issues:
        print("✅ 함수 내부 import 이슈 없음\n")
        return

    if errors:
        print(f"[ERROR] {len(errors)}건 — UnboundLocalError 위험 (즉시 수정 필요)\n")
        for i in errors:
            print(f"  ❌ {i['file']}:{i['line']}")
            print(f"     함수: {i['func']}()")
            print(f"     import: {i['import']}")
            print(f"     → {i['message']}\n")

    if warnings:
        print(f"[WARNING] {len(warnings)}건 — 함수 내부 import (상단 이동 권장)\n")
        for i in warnings:
            print(f"  ⚠️  {i['file']}:{i['line']}")
            print(f"     함수: {i['func']}()")
            print(f"     import: {i['import']}\n")

    print(f"합계: ERROR {len(errors)}건, WARNING {len(warnings)}건")
    print(f"수정: import 구문을 파일 최상단으로 이동\n")


def main():
    parser = argparse.ArgumentParser(
        description='함수 내부 import로 인한 UnboundLocalError 위험 감지'
    )
    parser.add_argument('target', nargs='?', default='.', help='검사할 파일 또는 폴더 (기본: 현재 디렉토리)')
    parser.add_argument('--error-only', action='store_true', help='[ERROR]만 출력')
    parser.add_argument('--json', action='store_true', help='JSON 형식으로 출력')
    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(f"오류: 경로가 존재하지 않습니다 — {target}", file=sys.stderr)
        sys.exit(1)

    issues = scan_target(target, error_only=args.error_only)

    if args.json:
        print(json.dumps(issues, ensure_ascii=False, indent=2))
    else:
        print_issues(issues, str(target))

    # ERROR가 있으면 exit code 1
    errors = [i for i in issues if i['level'] == 'ERROR']
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
