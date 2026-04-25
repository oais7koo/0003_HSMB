"""check_circular_imports.py - Python 모듈 순환 import 탐지

사용법:
    uv run python .claude/scripts/check_circular_imports.py [대상디렉토리]
    uv run python .claude/scripts/check_circular_imports.py oo/
    uv run python .claude/scripts/check_circular_imports.py 02_pycode/oo/
    uv run python .claude/scripts/check_circular_imports.py  # 기본: 프로젝트 루트의 oo/

AST 파싱으로 import 의존성 그래프를 구축하고 DFS로 사이클을 탐지합니다.
"""

import ast
import argparse
import os
import sys
from collections import defaultdict


def get_imports(file_path):
    """Python 파일을 파싱하여 import 모듈명 추출."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=file_path)
    except Exception:
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def find_cycles(graph):
    """의존성 그래프에서 사이클 탐지 (DFS)."""
    visited = set()
    stack = set()
    cycles = []

    def dfs(node, path):
        visited.add(node)
        stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor, path)
            elif neighbor in stack:
                cycle = path[path.index(neighbor):] + [neighbor]
                cycles.append(cycle)

        path.pop()
        stack.remove(node)

    for node in list(graph.keys()):
        if node not in visited:
            dfs(node, [])

    return cycles


def main():
    parser = argparse.ArgumentParser(description="Python 모듈 순환 import 탐지")
    parser.add_argument("target", nargs="?", default=None,
                        help="검사 대상 디렉토리 (기본: 프로젝트 루트의 oo/)")
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if args.target:
        target_dir = os.path.abspath(args.target)
    else:
        target_dir = os.path.join(project_root, 'oo')

    if not os.path.exists(target_dir):
        print(f"[ERROR] 대상 디렉토리 없음: {target_dir}")
        sys.exit(1)

    # 패키지명 추출 (디렉토리명)
    pkg_name = os.path.basename(target_dir)
    print(f"# 순환 import 검사: {pkg_name}/ ({target_dir})\n")

    dependency_graph = defaultdict(set)
    py_files = {}

    # 1. 모듈 매핑
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                full_path = os.path.join(root, file)
                rel = os.path.relpath(full_path, os.path.dirname(target_dir))
                module_name = rel.replace(os.sep, '.').replace('.py', '')
                py_files[module_name] = full_path

    print(f"스캔: {len(py_files)}개 모듈\n")

    # 2. 의존성 그래프 구축
    for module_name, file_path in py_files.items():
        imported_modules = get_imports(file_path)
        for imp in imported_modules:
            if imp.startswith(f'{pkg_name}.') or imp.startswith('.'):
                target = imp
                if imp.startswith('.'):
                    target = f'{pkg_name}.' + imp.lstrip('.')

                if target in py_files and target != module_name:
                    dependency_graph[module_name].add(target)

    # 3. 사이클 탐지
    cycles = find_cycles(dependency_graph)

    if cycles:
        # 중복 사이클 제거 (같은 노드 집합)
        unique = []
        seen = set()
        for c in cycles:
            key = tuple(sorted(set(c)))
            if key not in seen:
                seen.add(key)
                unique.append(c)

        print(f"[WARNING] 순환 의존성 {len(unique)}건 발견:\n")
        for i, cycle in enumerate(unique, 1):
            print(f"  {i}. {' -> '.join(cycle)}")
        sys.exit(1)
    else:
        print("[OK] 순환 의존성 없음")

    # 4. __init__.py import 확인
    init_path = os.path.join(target_dir, '__init__.py')
    if os.path.exists(init_path):
        imports = get_imports(init_path)
        if imports:
            print(f"\n{pkg_name}/__init__.py imports: {imports}")


if __name__ == "__main__":
    main()
