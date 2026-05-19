#!/usr/bin/env python3
"""
oolib_update.py

oais 모듈 분석 및 문서화 스크립트

명령어:
    cclib run              전체 모듈 분석
    cclib run [모듈명]     특정 모듈 분석 (예: cclib run image)
    cclib update           d0005_lib.md 문서 업데이트 (oais 모듈 + 함수 상세)

출처 태그 규약:
    oais 함수의 docstring에 아래 한 줄을 넣으면 d0005 '출처' 컬럼에 자동 반영된다.
        출처: 02_pycode/d2XXXX_원본파일.py
    태그가 없으면 d0005의 수동 기재 출처를 재생성 시 보존한다(하이브리드).
"""

import ast
import re
import sys
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[3]   # scripts -> cclib -> skills -> .codex -> 프로젝트 루트
OAIS_DIR = PROJECT_ROOT / "oais"
LIB_DOC_FILE = PROJECT_ROOT / "00_doc" / "sp00" / "d0005_lib.md"
SUBPACKAGES = ["iqa", "rag", "modules", "training"]

# docstring 출처 태그: "출처: ..." / "Source: ..."
SOURCE_TAG_RE = re.compile(r"^[ \t]*(?:출처|source)[ \t]*[:：][ \t]*(.+?)[ \t]*$", re.M | re.I)


def print_usage():
    """사용법 출력"""
    print(f"Log started at {datetime.now()}")
    print("cclib - oais 모듈 분석 및 문서화")
    print()
    print("사용법:")
    print("    cclib run              전체 모듈 분석")
    print("    cclib run [모듈명]     특정 모듈 분석 (예: image, metrics)")
    print("    cclib update           d0005_lib.md 문서 업데이트 (oais 모듈 + 함수 상세)")
    print()
    print("옵션:")
    print("    --depth [n]              분석 깊이 설정 (기본: 2)")
    print("    --include-private        private 함수 포함")
    print("    --doc-only               문서만 생성, 분석 생략")
    print()
    print("예시:")
    print("    python .agents/skills/cclib/scripts/oolib_update.py run")
    print("    python .agents/skills/cclib/scripts/oolib_update.py run image")
    print("    python .agents/skills/cclib/scripts/oolib_update.py update")

def parse_module(file_path):
    """
    Parses a python file to extract classes and functions with docstrings.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(file_path))

    module_doc = ast.get_docstring(tree)
    functions = []
    classes = []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            func_doc = ast.get_docstring(node)
            args = [a.arg for a in node.args.args]
            functions.append({
                "name": node.name,
                "args": args,
                "doc": func_doc
            })
        elif isinstance(node, ast.ClassDef):
            class_doc = ast.get_docstring(node)
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_doc = ast.get_docstring(item)
                    m_args = [a.arg for a in item.args.args]
                    methods.append({
                        "name": item.name,
                        "args": m_args,
                        "doc": method_doc
                    })
            classes.append({
                "name": node.name,
                "doc": class_doc,
                "methods": methods
            })

    return module_doc, classes, functions


def _safe_parse(py_file):
    """parse_module 래퍼 — 구문 오류 시 빈 결과 반환"""
    try:
        return parse_module(py_file)
    except (SyntaxError, ValueError):
        return None, [], []


def _extract_source(docstring):
    """docstring의 '출처:' / 'Source:' 태그 추출. 없으면 ''"""
    if not docstring:
        return ""
    m = SOURCE_TAG_RE.search(docstring)
    return m.group(1).strip() if m else ""


def _first_desc_line(docstring):
    """docstring 첫 설명 줄 (출처 태그 줄은 건너뜀). 없으면 '-'"""
    if not docstring:
        return "-"
    for ln in docstring.strip().splitlines():
        s = ln.strip()
        if not s:
            continue
        low = s.lower()
        if low.startswith("출처") or low.startswith("source"):
            continue
        return s
    return "-"


def _public_func_details(functions):
    """공개 함수 -> [{name, sig, desc, source}]"""
    out = []
    for f in functions:
        if f["name"].startswith("_"):
            continue
        sig = "(" + ", ".join(f["args"]) + ")"
        out.append({
            "name": f["name"],
            "sig": sig,
            "desc": _first_desc_line(f["doc"]),
            "source": _extract_source(f["doc"]),
        })
    return out


def scan_oais_modules():
    """oais/ 최상위 모듈 + 서브패키지 스캔.

    -> [{name, funcs:[{name,sig,desc,source}], func_count, class_count, doc}]
    """
    mods = []
    for py in sorted(OAIS_DIR.glob("*.py")):
        if py.name == "__init__.py":
            continue
        mod_doc, classes, functions = _safe_parse(py)
        funcs = _public_func_details(functions)
        pub_c = sum(1 for c in classes if not c["name"].startswith("_"))
        mods.append({
            "name": py.stem, "funcs": funcs, "func_count": len(funcs),
            "class_count": pub_c, "doc": _first_desc_line(mod_doc),
        })
    for pkg in SUBPACKAGES:
        pkg_dir = OAIS_DIR / pkg
        if not pkg_dir.is_dir():
            continue
        funcs = []
        tc = 0
        pkg_doc = None
        for py in sorted(pkg_dir.glob("*.py")):
            mod_doc, classes, functions = _safe_parse(py)
            funcs.extend(_public_func_details(functions))
            tc += sum(1 for c in classes if not c["name"].startswith("_"))
            if py.name == "__init__.py" and mod_doc:
                pkg_doc = _first_desc_line(mod_doc)
        mods.append({
            "name": f"{pkg}/", "funcs": funcs, "func_count": len(funcs),
            "class_count": tc, "doc": pkg_doc or "-",
        })
    return mods


def parse_existing_doc():
    """기존 d0005_lib.md에서 큐레이션 보존 대상 추출.

    -> {history: [...], rows: {모듈명: 주요기능}, func_sources: {모듈명: {함수명: 출처}}}
    func_sources: §2 함수 표에 수동 기재된 출처 (재생성 시 보존)
    """
    result = {"history": [], "rows": {}, "func_sources": {}}
    if not LIB_DOC_FILE.exists():
        return result
    content = LIB_DOC_FILE.read_text(encoding="utf-8")

    m = re.search(r"##\s*문서이력관리\s*\n((?:-\s.+\n?)+)", content)
    if m:
        result["history"] = [
            ln.rstrip() for ln in m.group(1).splitlines() if ln.strip().startswith("- ")
        ]

    cur_module = None  # None=§1 영역, 값 설정 시 §2 함수 표 영역
    for line in content.splitlines():
        hm = re.match(r"^###\s+[\d.]+\s+(.+?)\s*$", line)
        if hm:
            cur_module = hm.group(1).strip().lower()
            continue
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        first = cells[0]
        if not first or first.startswith("-") or first.startswith("**") or first in ("모듈", "함수"):
            continue
        if cur_module is None and len(cells) >= 3:
            # §1 모듈 표: 모듈명 -> 마지막 셀(주요 기능)
            result["rows"][first.lower()] = cells[-1]
        elif cur_module and len(cells) >= 4:
            # §2 함수 표: 함수명 -> 출처(4번째 셀)
            src = cells[3]
            if src and src not in ("-", "미기재"):
                result["func_sources"].setdefault(cur_module, {})[first.lower()] = src

    return result


def _read_oais_version():
    """oais/__init__.py의 __version__ 추출"""
    init = OAIS_DIR / "__init__.py"
    if init.exists():
        m = re.search(
            r'__version__\s*=\s*["\']([^"\']+)["\']', init.read_text(encoding="utf-8")
        )
        if m:
            return m.group(1)
    return "?"


def _next_version(history):
    """이력 첫 줄의 vN.N -> 다음 마이너 버전"""
    for ln in history:
        m = re.search(r"v(\d+)\.(\d+)", ln)
        if m:
            return f"v{m.group(1)}.{int(m.group(2)) + 1}"
    return "v1.0"


def _esc(text):
    """표 셀용 파이프 이스케이프"""
    return str(text).replace("|", "\\|")


def build_lib_doc():
    """d0005_lib.md 생성 — oais 모듈 구조(§1) + 함수 상세(§2).

    Python 의존성(pyproject.toml)은 d0009_env.md(ooenv) 관할 — 여기서 다루지 않는다.
    함수 출처는 docstring '출처:' 태그 자동 추출 + 기존 문서 수동 기재 보존(하이브리드).
    """
    existing = parse_existing_doc()
    mods = scan_oais_modules()
    oais_ver = _read_oais_version()
    today = datetime.now().strftime("%Y-%m-%d")
    rows = existing["rows"]
    func_sources = existing["func_sources"]

    new_ver = _next_version(existing["history"])
    history = [f"- {new_ver} {today} — cclib doc 자동 현행화 (oais v{oais_ver})"]
    history.extend(existing["history"])
    history = history[:5]

    lines = ["# d0005_lib.md - oais 모듈 문서", ""]
    lines += [
        "> 프로젝트 루트 `oais/` 패키지의 모듈·함수 구조 문서.",
        "> 함수는 SP02(`02_pycode/`)에서 개발·검증 후 함수화되며, **출처**는 해당 SP02 원본 파일을 가리킨다.",
        "> Python 의존성(pyproject.toml)은 `d0009_env.md`(ooenv) 참조.",
        "",
    ]
    lines += ["## 문서이력관리"]
    lines.extend(history)

    # §1 모듈 구조
    lines += ["", "---", "", f"## 1. oais 모듈 구조 (v{oais_ver})", ""]
    lines += ["| 모듈 | 함수 수 | 주요 기능 |", "|------|--------|---------|"]
    total_f = total_c = 0
    for m in mods:
        total_f += m["func_count"]
        total_c += m["class_count"]
        feature = _esc(rows.get(m["name"].lower()) or m["doc"] or "-")
        lines.append(f"| {m['name']} | {m['func_count']} | {feature} |")
    lines.append(
        f"| **합계** | **{total_f}** | **{total_c}개 클래스 / {len(mods)}개 모듈** |"
    )

    # §2 함수 상세
    lines += ["", "---", "", "## 2. 함수 상세", ""]
    lines += [
        "> `출처`: 함수가 함수화되기 전 개발·검증된 SP02(`02_pycode/`) 원본 파일.",
        "> docstring `출처:` 태그에서 자동 추출하며, 태그가 없으면 수동 기재값을 재생성 시 보존한다.",
        "> `미기재` = 아직 출처가 확인되지 않은 함수.",
        "",
    ]
    tagged = 0
    for idx, m in enumerate(mods, 1):
        lines += [f"### 2.{idx} {m['name']}", ""]
        if not m["funcs"]:
            lines += ["(공개 함수 없음)", ""]
            continue
        lines += ["| 함수 | 시그니처 | 설명 | 출처 |", "|------|---------|------|------|"]
        mod_src = func_sources.get(m["name"].lower(), {})
        for fn in m["funcs"]:
            src = fn["source"] or mod_src.get(fn["name"].lower(), "") or "미기재"
            if fn["source"]:
                tagged += 1
            lines.append(
                f"| {fn['name']} | {_esc(fn['sig'])} | {_esc(fn['desc'])} | {_esc(src)} |"
            )
        lines += [""]

    lines += [
        "---", "",
        f"> 공개 함수 {total_f}개 중 출처 태그 기재 {tagged}개 / 미기재 {total_f - tagged}개.",
        "> 미기재 항목은 해당 함수 docstring에 `출처:` 태그를 추가하거나 위 표의 출처 칸을 직접 기입한다.",
        "",
    ]

    return "\n".join(lines)

def cmd_run(args, options):
    """모듈 분석 (run 서브명령어)"""
    print("# cclib run\n")

    if not OAIS_DIR.exists():
        print(f"[ERROR] {OAIS_DIR} directory not found.")
        return 1

    include_private = options.get("include_private", False)
    target_module = args[0] if args else None

    print(f"분석 대상: {OAIS_DIR}")
    if target_module:
        print(f"모듈 필터: {target_module}")
    print()

    modules_data = {}

    for py_file in sorted(OAIS_DIR.glob("*.py")):
        if py_file.name == "__init__.py":
            continue

        # 모듈 필터 적용
        if target_module and target_module.lower() not in py_file.stem.lower():
            continue

        try:
            mod_doc, classes, functions = parse_module(py_file)

            # private 필터
            if not include_private:
                functions = [f for f in functions if not f["name"].startswith("_")]
                for cls in classes:
                    cls["methods"] = [m for m in cls["methods"] if not m["name"].startswith("_")]

            modules_data[py_file.stem] = {
                "doc": mod_doc,
                "classes": classes,
                "functions": functions
            }

            # 분석 결과 출력
            print(f"## {py_file.stem}")
            if mod_doc:
                first_line = mod_doc.strip().split("\n")[0]
                print(f"  {first_line[:60]}")
            print(f"  클래스: {len(classes)}개 | 함수: {len(functions)}개")
            print()

        except Exception as e:
            print(f"[ERROR] Failed to parse {py_file.name}: {e}")

    print(f"---\n총 {len(modules_data)}개 모듈 분석 완료")
    return 0


def cmd_update(options):
    """d0005_lib.md 문서 현행화 (update / doc 서브명령어)"""
    print("# cclib update\n")

    if not OAIS_DIR.exists():
        print(f"[ERROR] {OAIS_DIR} 디렉토리를 찾을 수 없습니다.")
        return 1

    print(f"분석 대상 : {OAIS_DIR}")
    print(f"출력 문서 : {LIB_DOC_FILE}\n")

    md = build_lib_doc()
    LIB_DOC_FILE.parent.mkdir(parents=True, exist_ok=True)
    LIB_DOC_FILE.write_text(md, encoding="utf-8")

    mods = scan_oais_modules()
    total_f = sum(m["func_count"] for m in mods)
    tagged = sum(1 for m in mods for fn in m["funcs"] if fn["source"])
    print(f"  [OK] oais 모듈 {len(mods)}개 / 공개 함수 {total_f}개 문서화")
    print(f"  [출처] docstring 태그 자동 추출 {tagged}개 / 미기재 {total_f - tagged}개")
    print(f"\n[OK] d0005_lib.md 현행화 완료")
    return 0


def main():
    print(f"Log started at {datetime.now()}")

    args = sys.argv[1:]

    if not args:
        print_usage()
        return 0

    cmd = args[0].lower()
    cmd_args = args[1:]

    # 옵션 파싱
    options = {
        "include_private": "--include-private" in cmd_args,
        "doc_only": "--doc-only" in cmd_args
    }

    # depth 옵션
    if "--depth" in cmd_args:
        idx = cmd_args.index("--depth")
        if idx + 1 < len(cmd_args):
            try:
                options["depth"] = int(cmd_args[idx + 1])
            except ValueError:
                pass

    # 옵션 제거
    cmd_args = [a for a in cmd_args if not a.startswith("--") and not a.isdigit()]

    if cmd == "run":
        return cmd_run(cmd_args, options)
    elif cmd == "update":
        return cmd_update(options)
    else:
        print(f"[ERROR] Unknown command: {cmd}")
        print_usage()
        return 1


if __name__ == "__main__":
    sys.exit(main())
