#!/usr/bin/env python
"""
oopaper_doctor.py - 종합 정합성 진단 (읽기 전용, v01)

진단 항목:
    folder-id : FOLDER_ID 표준 위반 (^\\d{6}-\\d{4}$)
    file-name : 파일명 prefix 위반 (00/01/03/04/05 미준수)
    multi-pdf : 1폴더 1논문 위반 (PDF 2개 이상)
    sync      : paper_list ↔ 실제 폴더 차이
    orphan    : paper_list에만 등재, 폴더 없음
    quality   : 산출물 품질 미달 (용량/미완료 마커)

사용법:
    uv run python .claude/skills/ccpaper/scripts/oopaper_doctor.py [--check NAME] [--lang en|ko]

옵션:
    --check NAME   특정 체크만 (생략 시 전체)
    --lang en|ko   대상 언어 (기본 en)
    --quiet        ERROR/WARN만 출력
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Set, Tuple

_HERE = Path(__file__).resolve()
PROJECT_ROOT = _HERE.parents[4]
PAPER_BASE = PROJECT_ROOT / "03_paper" if (PROJECT_ROOT / "03_paper").exists() else PROJECT_ROOT
PAPER_DIR_EN = PAPER_BASE / "11_paper_en"
PAPER_DIR_KO = PAPER_BASE / "12_paper_ko"
PAPER_LIST_EN = PAPER_DIR_EN / "paper_list.md"
PAPER_LIST_KO = PAPER_BASE / "12_paper_ko.md"

FOLDER_ID = re.compile(r"^\d{6}-\d{4}$")
SUFFIX_PATTERN = re.compile(r"^\d{6}-\d{4}-\d{1,3}$")

THRESHOLDS = {"summary": 500, "english": 1000, "korean": 1000}
INCOMPLETE = [
    "(추출 필요)", "(추후 작성)", "[저자명]", "[제목]",
    "# 번역 필요", "[Translation Required]", "TODO",
    "(미작성)", "[미완료]", "작성 예정",
]

CHECKS = ("folder-id", "file-name", "multi-pdf", "sync", "orphan", "quality")


def list_folders(d: Path) -> List[Path]:
    if not d.exists():
        return []
    return sorted(p for p in d.iterdir() if p.is_dir() and not p.name.startswith("_"))


# ─────────────────────────────────────────
# 체크 함수
# ─────────────────────────────────────────
def check_folder_id(folders: List[Path]) -> List[Tuple[str, str]]:
    out = []
    for f in folders:
        n = f.name
        if FOLDER_ID.match(n):
            continue
        if SUFFIX_PATTERN.match(n):
            reason = "suffix `-NN` 부착 — split-multi로 신규 ID 발급 필요"
        elif re.match(r"^\d{6}-\d{1,3}$", n):
            reason = "HHMM 자릿수 부족"
        elif re.match(r"^\d{6}-\d{5,}$", n):
            reason = "HHMM 자릿수 초과"
        elif re.match(r"^[A-Za-z]+_?\d{6}-\d{4}$", n):
            reason = "prefix 부착 (DS01_, IR07_ 등)"
        elif "_" in n or " " in n:
            reason = "구분자/공백 위반 (하이픈만 허용)"
        else:
            reason = "정규식 ^\\d{6}-\\d{4}$ 위반"
        out.append((n, reason))
    return out


def check_file_name(folders: List[Path]) -> List[Tuple[str, str, str]]:
    out = []
    for f in folders:
        if not FOLDER_ID.match(f.name):
            continue
        fid = f.name
        for sub in f.iterdir():
            if not sub.is_file():
                continue
            name = sub.name
            # 이중 prefix (예: {ID}_01_00_*_서머리.md)
            if re.match(rf"^{re.escape(fid)}_\d{{2}}_\d{{2}}_", name):
                out.append((fid, name, "이중 prefix (01_00_… 등)"))
                continue
            # PDF prefix 미적용
            if name.lower().endswith(".pdf") and not name.startswith(f"{fid}_01_"):
                out.append((fid, name, "PDF prefix 미적용 (`{ID}_01_` 필요)"))
                continue
            # md prefix 미적용 (메타 파일 제외)
            if name.endswith(".md") and not re.match(rf"^{re.escape(fid)}_\d{{2}}_", name):
                if name not in ("paper_list.md", "README.md", ".keep"):
                    out.append((fid, name, "md prefix 미적용 (`{ID}_NN_` 필요)"))
    return out


def check_multi_pdf(folders: List[Path]) -> List[Tuple[str, int, List[str]]]:
    out = []
    for f in folders:
        if not FOLDER_ID.match(f.name):
            continue
        pdfs = sorted(f.glob("*.pdf"))
        if len(pdfs) >= 2:
            out.append((f.name, len(pdfs), [p.name for p in pdfs[:3]]))
    return out


def parse_paper_list_ids(list_file: Path) -> Set[str]:
    if not list_file.exists():
        return set()
    text = list_file.read_text(encoding="utf-8", errors="ignore")
    return set(re.findall(r"\b(\d{6}-\d{4})\b", text))


def check_sync(folders: List[Path], list_file: Path) -> Tuple[List[str], List[str]]:
    folder_ids = {f.name for f in folders if FOLDER_ID.match(f.name)}
    list_ids = parse_paper_list_ids(list_file)
    missing_in_list = sorted(folder_ids - list_ids)
    missing_in_fs = sorted(list_ids - folder_ids)
    return missing_in_list, missing_in_fs


def check_orphan(folders: List[Path], list_file: Path) -> List[str]:
    folder_ids = {f.name for f in folders if FOLDER_ID.match(f.name)}
    list_ids = parse_paper_list_ids(list_file)
    return sorted(list_ids - folder_ids)


def check_quality(folders: List[Path]) -> List[Tuple[str, str, str]]:
    out = []
    targets = [
        ("summary", "*_00_*_서머리.md", THRESHOLDS["summary"]),
        ("english", "*_03_*_전문(영어).md", THRESHOLDS["english"]),
        ("korean",  "*_04_*_전문(한글).md", THRESHOLDS["korean"]),
    ]
    for f in folders:
        if not FOLDER_ID.match(f.name):
            continue
        for kind, glob, threshold in targets:
            for file in f.glob(glob):
                try:
                    size = file.stat().st_size
                    if size < threshold:
                        out.append((f.name, file.name, f"용량 {size}B < {threshold}B"))
                        break
                    content = file.read_text(encoding="utf-8")
                    for marker in INCOMPLETE:
                        if marker in content:
                            out.append((f.name, file.name, f"미완료 마커 '{marker}'"))
                            break
                except Exception as e:
                    out.append((f.name, file.name, f"읽기 실패 {e}"))
                break
    return out


# ─────────────────────────────────────────
# 출력
# ─────────────────────────────────────────
def fmt_section(title: str, count: int, lines: List[str], severity: str, max_show: int = 10):
    tag = {"OK": "[OK]", "INFO": "[INFO]", "WARN": "[WARN]", "ERROR": "[ERROR]"}.get(severity, "[?]")
    print(f"\n## {title} {tag} {count}건")
    for line in lines[:max_show]:
        print(f"  - {line}")
    if count > max_show:
        print(f"  ... ({count - max_show}건 더)")


def cmd_doctor(args):
    if sys.stdout.encoding and sys.stdout.encoding.lower() in ("cp949", "cp1252", "ascii"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print(f"# ccpaper doctor — 종합 진단 (v01)")
    print(f"paper_root: {PAPER_BASE}")
    print(f"lang: {args.lang}")

    if args.lang == "ko":
        paper_dir, list_file = PAPER_DIR_KO, PAPER_LIST_KO
    else:
        paper_dir, list_file = PAPER_DIR_EN, PAPER_LIST_EN

    folders = list_folders(paper_dir)
    if not folders:
        print(f"\n[INFO] {paper_dir} 폴더 없음 또는 비어있음")
        return 0

    print(f"대상 폴더: {len(folders)}개 ({paper_dir.name})")
    list_status = "있음" if list_file.exists() else "없음"
    print(f"paper_list: {list_file.name} ({list_status})")

    target = args.check or "all"
    summary = {"OK": 0, "INFO": 0, "WARN": 0, "ERROR": 0}

    def tally(sev: str):
        summary[sev] = summary.get(sev, 0) + 1

    if target in ("all", "folder-id"):
        v = check_folder_id(folders)
        sev = "ERROR" if v else "OK"
        tally(sev)
        fmt_section("폴더 ID 표준 (folder-id)", len(v), [f"{n} : {r}" for n, r in v], sev)

    if target in ("all", "file-name"):
        v = check_file_name(folders)
        sev = "WARN" if v else "OK"
        tally(sev)
        fmt_section("파일명 prefix (file-name)", len(v),
                    [f"{f}/{n} : {r}" for f, n, r in v], sev)

    if target in ("all", "multi-pdf"):
        v = check_multi_pdf(folders)
        sev = "ERROR" if v else "OK"
        tally(sev)
        fmt_section("1폴더 1논문 (multi-pdf)", len(v),
                    [f"{n} : PDF {c}개 — {p}" for n, c, p in v], sev)

    if target in ("all", "sync"):
        m_list, m_fs = check_sync(folders, list_file)
        v_total = len(m_list) + len(m_fs)
        sev = "WARN" if v_total else "OK"
        tally(sev)
        lines = [f"리스트 미등록: {len(m_list)}건 / 폴더 부재(고아): {len(m_fs)}건"]
        if m_list:
            lines += [f"[리스트 미등록] {x}" for x in m_list[:5]]
        if m_fs:
            lines += [f"[폴더 부재] {x}" for x in m_fs[:5]]
        fmt_section("paper_list 동기화 (sync)", v_total, lines, sev)

    if target in ("all", "orphan"):
        v = check_orphan(folders, list_file)
        sev = "WARN" if v else "OK"
        tally(sev)
        fmt_section("고아 항목 (orphan)", len(v),
                    [f"{x} : 폴더 없음 (paper_list만 등재)" for x in v], sev)

    if target in ("all", "quality"):
        v = check_quality(folders)
        sev = "INFO" if v else "OK"
        tally(sev)
        fmt_section("산출물 품질 (quality)", len(v),
                    [f"{f}/{n} : {r}" for f, n, r in v], sev)

    print(f"\n## 소계")
    print(f"OK: {summary['OK']} | INFO: {summary['INFO']} | "
          f"WARN: {summary['WARN']} | ERROR: {summary['ERROR']}")

    return 1 if summary["ERROR"] else 0


def main():
    parser = argparse.ArgumentParser(description="ccpaper 종합 정합성 진단 (읽기 전용)")
    parser.add_argument("--check", choices=list(CHECKS), help="특정 체크만 실행")
    parser.add_argument("--lang", choices=["en", "ko"], default="en")
    parser.add_argument("--quiet", action="store_true", help="ERROR/WARN만 출력")
    args = parser.parse_args()
    sys.exit(cmd_doctor(args))


if __name__ == "__main__":
    main()
