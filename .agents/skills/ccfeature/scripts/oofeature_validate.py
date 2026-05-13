#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
oofeature_validate.py
상세 문서(상세기획/설계/구현/검증) 정합성 검증 스크립트

검증 항목:
    V01 파일명 형식    d{N}_상세{단계}_{기능명}.md 형식 준수
    V02 단계 유효성    기획/설계/구현/검증 중 하나인지
    V03 SP 귀속        문서번호 prefix가 폴더 SP와 일치
    V04 헤더 메타      내부 문서번호·단계가 파일명과 일치
    V05 필수 섹션      단계별 필수 섹션 존재 여부
    V06 플레이스홀더   {기능명} 등 미치환 값 감지
    V07 plan.md 연결   Feature ID가 plan.md에 등록되어 있는지
    V08 빈 섹션        내용이 없는 섹션 감지

사용법:
    uv run python .claude/skills/ccfeature/scripts/oofeature_validate.py
    uv run python .claude/skills/ccfeature/scripts/oofeature_validate.py --sp 04
    uv run python .claude/skills/ccfeature/scripts/oofeature_validate.py --sp 04 --verbose
    uv run python .claude/skills/ccfeature/scripts/oofeature_validate.py --dry-run
"""

import sys
import re
import json
from pathlib import Path

# Windows 인코딩 문제 방지
if sys.stdout.encoding and sys.stdout.encoding.lower() in ("cp949", "cp1252", "ascii"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() in ("cp949", "cp1252", "ascii"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
DOC_DIR = PROJECT_ROOT / "00_doc"
STATE_FILE = PROJECT_ROOT / ".omc" / "state" / "context.json"

# 단계 정의
STAGES = ["기획", "설계", "구현", "검증"]

# 단계별 필수 섹션 prefix
STAGE_SECTIONS = {
    "기획": ["## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6."],
    "설계": ["## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6.", "## 7."],
    "구현": ["## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6.", "## 7.", "## 8."],
    "검증": ["## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6.", "## 7.", "## 8.", "## 9."],
}

# 미치환 플레이스홀더 패턴
PLACEHOLDER_PATTERNS = [
    (r'\{기능명\}', '{기능명}'),
    (r'\{dXXXX\}', '{dXXXX}'),
    (r'\{YYYY-MM-DD\}', '{YYYY-MM-DD}'),
    (r'\{F_ID\}', '{F_ID}'),
    (r'\{SPNN\}', '{SPNN}'),
    (r'\{SP번호\}', '{SP번호}'),
    (r'\{기능번호\}', '{기능번호}'),
    (r'\{Feature명\}', '{Feature명}'),
]

# 파일명 패턴: d{문서번호}_상세{단계}_{기능명}.md
FILE_PATTERN = re.compile(r'^(d\d{5,})_상세(기획|설계|구현|검증)_(.+)\.md$')


def get_current_sp() -> str:
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            return data.get("sp", "00")
        except Exception:
            pass
    return "00"


def get_sp_folder(sp: str) -> str:
    return f"sp{int(sp):02d}"


def scan_detail_docs(sp: str) -> list:
    """SP 폴더의 상세 문서 목록 반환"""
    sp_dir = DOC_DIR / get_sp_folder(sp)
    if not sp_dir.exists():
        return []
    docs = []
    for f in sorted(sp_dir.iterdir()):
        if not f.is_file() or not f.name.endswith(".md"):
            continue
        if any(kw in f.name for kw in ("_상세기획_", "_상세설계_", "_상세구현_", "_상세검증_")):
            docs.append(f)
    return docs


def load_plan_doc_nums(sp: str) -> set:
    """plan.md에서 d{N}XXXX 형태의 문서번호 추출"""
    sp_num = int(sp)
    doc_num = sp_num * 10000 + 2
    plan_path = DOC_DIR / get_sp_folder(sp) / f"d{str(doc_num).zfill(4)}_plan.md"
    if not plan_path.exists():
        return set()
    content = plan_path.read_text(encoding="utf-8")
    return set(re.findall(r'd\d{5,}', content))


def validate_doc(doc_path: Path, sp: str, plan_doc_nums: set) -> dict:
    """단일 상세 문서 검증. 결과 dict 반환."""
    result = {
        "file": doc_path.name,
        "V01": "OK", "V02": "OK", "V03": "OK", "V04": "OK",
        "V05": "OK", "V06": "OK", "V07": "OK", "V08": "OK",
        "messages": [],
    }

    filename = doc_path.name
    try:
        content = doc_path.read_text(encoding="utf-8")
    except Exception as e:
        result["V01"] = "ERROR"
        result["messages"].append(f"V01: 파일 읽기 실패 — {e}")
        return result

    # V01: 파일명 형식
    m = FILE_PATTERN.match(filename)
    if not m:
        result["V01"] = "ERROR"
        result["messages"].append(f"V01: 파일명 형식 불일치 (기대: d{{N}}_상세{{단계}}_{{기능명}}.md)")
        # 파일명 파싱 불가 → 이후 검증 생략
        return result

    doc_num = m.group(1)   # e.g. d41001
    stage = m.group(2)     # e.g. 기획
    # func_name = m.group(3)  # e.g. 데이터수집소스

    # V02: 단계 유효성 (FILE_PATTERN이 이미 걸러주지만 명시적 확인)
    if stage not in STAGES:
        result["V02"] = "ERROR"
        result["messages"].append(f"V02: 유효하지 않은 단계: '{stage}' (허용: {'/'.join(STAGES)})")

    # V03: SP 귀속 — d4XXXX → SP04
    num_str = doc_num[1:]  # 예: "41001"
    try:
        expected_sp = str(int(num_str) // 10000).zfill(2)  # "04"
    except ValueError:
        expected_sp = "??"
    if expected_sp != sp.zfill(2):
        result["V03"] = "ERROR"
        result["messages"].append(
            f"V03: SP 귀속 불일치 — {doc_num} → SP{expected_sp}, 현재 폴더: SP{sp.zfill(2)}"
        )

    # V04: 헤더 메타 정합성
    # 기대 형식: > 문서번호: dXXXX | 단계: 기획 | SP: SPNN | ...
    meta_line = None
    for line in content.splitlines()[:8]:
        if "문서번호:" in line and "단계:" in line:
            meta_line = line.strip()
            break

    if meta_line:
        meta_issues = []
        if doc_num not in meta_line:
            meta_issues.append(f"문서번호({doc_num}) 불일치")
        if f"단계: {stage}" not in meta_line and f"단계:{stage}" not in meta_line:
            meta_issues.append(f"단계({stage}) 불일치")
        if meta_issues:
            result["V04"] = "WARN"
            result["messages"].append(f"V04: 헤더 메타 불일치 — {', '.join(meta_issues)}")
    else:
        result["V04"] = "WARN"
        result["messages"].append("V04: 헤더 메타라인 없음 (> 문서번호: ... | 단계: ... 형식 필요)")

    # V05: 단계별 필수 섹션 존재 여부
    required_sections = STAGE_SECTIONS.get(stage, [])
    missing = [s for s in required_sections if s not in content]
    if missing:
        result["V05"] = "WARN"
        result["messages"].append(f"V05: 필수 섹션 누락 — {', '.join(missing)}")

    # V06: 플레이스홀더 미치환
    found_ph = []
    for pattern, display in PLACEHOLDER_PATTERNS:
        if re.search(pattern, content):
            found_ph.append(display)
    if found_ph:
        result["V06"] = "WARN"
        result["messages"].append(f"V06: 미치환 플레이스홀더 — {', '.join(found_ph)}")

    # V07: plan.md Feature 연결 유효성
    if plan_doc_nums:
        if doc_num not in plan_doc_nums:
            result["V07"] = "INFO"
            result["messages"].append(f"V07: plan.md에 {doc_num} 미등록")
    else:
        result["V07"] = "INFO"
        result["messages"].append("V07: plan.md 없음 (교차 검증 불가)")

    # V08: 빈 섹션 감지
    lines = content.splitlines()
    empty_sections = []
    for i, line in enumerate(lines):
        if not re.match(r'^## \d+\.', line):
            continue
        # 다음 섹션 시작까지 실질 내용 확인
        j = i + 1
        has_content = False
        while j < len(lines) and not lines[j].startswith("## "):
            if lines[j].strip() and not lines[j].strip().startswith(">"):
                has_content = True
                break
            j += 1
        if not has_content:
            empty_sections.append(line.strip()[:30])
    if empty_sections:
        result["V08"] = "INFO"
        result["messages"].append(f"V08: 빈 섹션 {len(empty_sections)}개 — {', '.join(empty_sections[:3])}")

    return result


def overall_grade(result: dict) -> str:
    vals = [result[f"V{i:02d}"] for i in range(1, 9)]
    if "ERROR" in vals:
        return "ERROR"
    if "WARN" in vals:
        return "WARN"
    if "INFO" in vals:
        return "INFO"
    return "PASS"


def run_validate(sp: str, verbose: bool = False):
    docs = scan_detail_docs(sp)
    plan_doc_nums = load_plan_doc_nums(sp)

    print(f"[ccfeature validate] SP{sp.zfill(2)}\n")

    if not docs:
        print(f"  상세 문서 없음: 00_doc/sp{int(sp):02d}/")
        return

    # 헤더
    print("| 파일 | V01 | V02 | V03 | V04 | V05 | V06 | V07 | V08 | 결과 |")
    print("|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:----:|")

    counts = {"PASS": 0, "WARN": 0, "ERROR": 0, "INFO": 0}
    all_results = []

    for doc in docs:
        r = validate_doc(doc, sp, plan_doc_nums)
        grade = overall_grade(r)
        counts[grade] = counts.get(grade, 0) + 1
        all_results.append((r, grade))
        row = (
            f"| {r['file']} "
            f"| {r['V01']} | {r['V02']} | {r['V03']} | {r['V04']} "
            f"| {r['V05']} | {r['V06']} | {r['V07']} | {r['V08']} "
            f"| **{grade}** |"
        )
        print(row)

    print(
        f"\n소계: PASS:{counts['PASS']} | WARN:{counts['WARN']} "
        f"| ERROR:{counts['ERROR']} | INFO:{counts['INFO']}"
    )

    if verbose:
        has_detail = any(r["messages"] for r, _ in all_results)
        if has_detail:
            print("\n### 상세 메시지\n")
            for r, grade in all_results:
                if r["messages"]:
                    print(f"**{r['file']}** ({grade})")
                    for msg in r["messages"]:
                        print(f"  - {msg}")


def run_dry_run(sp: str):
    docs = scan_detail_docs(sp)
    print(f"[ccfeature validate --dry-run] SP{sp.zfill(2)}")
    print(f"검증 대상: {len(docs)}개 상세 문서\n")
    for d in docs:
        print(f"  - {d.name}")
    if docs:
        print(f"\n검증 항목: V01(파일명형식) V02(단계유효성) V03(SP귀속) V04(헤더메타)")
        print(f"           V05(필수섹션) V06(플레이스홀더) V07(plan연결) V08(빈섹션)")


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("help", "-h", "--help"):
        print("사용법: oofeature_validate.py [--sp N] [--verbose] [--dry-run]")
        print("  --sp N       특정 SP 지정 (기본값: 현재 oocontext SP)")
        print("  --verbose    상세 메시지 출력")
        print("  --dry-run    검증 대상 목록만 출력")
        return

    sp = None
    verbose = "--verbose" in args or "-v" in args
    dry_run = "--dry-run" in args

    for i, a in enumerate(args):
        if a == "--sp" and i + 1 < len(args):
            sp = args[i + 1].zfill(2)

    if sp is None:
        sp = get_current_sp()

    if dry_run:
        run_dry_run(sp)
    else:
        run_validate(sp, verbose=verbose)


if __name__ == "__main__":
    main()
