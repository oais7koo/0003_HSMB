#!/usr/bin/env python3
"""oosidi - 옵시디언 볼트 문서 관리 스킬 메인 스크립트"""

import sys
import sys as _sys
if _sys.stdout.encoding and _sys.stdout.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stdout.reconfigure(encoding='utf-8')
if _sys.stderr.encoding and _sys.stderr.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stderr.reconfigure(encoding='utf-8')
import os
from pathlib import Path
from datetime import datetime


def get_vault_path():
    """볼트 경로 반환"""
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent.parent.parent
    return project_root / "01_obsidian"


def cmd_status(vault: Path):
    """볼트 상태 리포트"""
    print("# oosidi Vault Status Report\n")
    print(f"Vault Path: {vault}")
    print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    print("## Folder Summary\n")
    print(f"| {'Folder':<30} | {'MD Files':>8} | {'Subfolders':>10} |")
    print(f"|{'-'*32}|{'-'*10}|{'-'*12}|")

    total_md = 0
    folders = sorted([d for d in vault.iterdir() if d.is_dir() and not d.name.startswith(".")])

    for folder in folders:
        md_count = len(list(folder.rglob("*.md")))
        sub_count = len([d for d in folder.iterdir() if d.is_dir()])
        total_md += md_count
        print(f"| {folder.name:<30} | {md_count:>8} | {sub_count:>10} |")

    print(f"|{'-'*32}|{'-'*10}|{'-'*12}|")
    print(f"| {'TOTAL':<30} | {total_md:>8} | {len(folders):>10} |")
    print(f"\nTotal Folders: {len(folders)}")
    print(f"Total MD Files: {total_md}")


def cmd_list(vault: Path, folder_name: str):
    """특정 폴더의 문서 목록"""
    target = resolve_folder(vault, folder_name)
    if not target:
        print(f"[ERROR] Folder not found: {folder_name}")
        print(f"Available folders:")
        for d in sorted(vault.iterdir()):
            if d.is_dir() and not d.name.startswith("."):
                print(f"  - {d.name}")
        return

    print(f"# Documents in {target.name}\n")
    md_files = sorted(target.rglob("*.md"))
    for f in md_files:
        rel = f.relative_to(target)
        size = f.stat().st_size
        print(f"  - {rel} ({size:,} bytes)")
    print(f"\nTotal: {len(md_files)} files")


def cmd_search(vault: Path, keyword: str):
    """볼트 전체 키워드 검색"""
    print(f"# Search Results for '{keyword}'\n")
    results = []
    for md_file in vault.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            if keyword.lower() in content.lower():
                rel = md_file.relative_to(vault)
                results.append(str(rel))
        except (UnicodeDecodeError, PermissionError):
            continue

    if results:
        for r in sorted(results):
            print(f"  - {r}")
        print(f"\nFound in {len(results)} files")
    else:
        print("  No results found.")


def resolve_folder(vault: Path, folder_name: str):
    """폴더 경로 해석 (부분 매칭 지원, 중첩 경로 지원)"""
    # 직접 경로 시도
    target = vault / folder_name
    if target.exists() and target.is_dir():
        return target
    # 1단계 부분 매칭
    matches = [d for d in vault.iterdir() if d.is_dir() and folder_name.lower() in d.name.lower()]
    if matches:
        return matches[0]
    return None


def cmd_create(vault: Path, folder_name: str, title: str):
    """새 문서 생성"""
    target = resolve_folder(vault, folder_name)
    if not target:
        print(f"[ERROR] Folder not found: {folder_name}")
        return

    filename = f"{title}.md"
    filepath = target / filename

    if filepath.exists():
        print(f"[ERROR] File already exists: {filepath.relative_to(vault)}")
        return

    filepath.write_text(f"## 개요\n", encoding="utf-8")
    print(f"[OK] Created: {filepath.relative_to(vault)}")


# 개요 5종 세트 카테고리
OVERVIEW_SERIES = ["개요", "환경", "사용", "APIs", "채널"]


def cmd_init_topic(vault: Path, folder_name: str, topic: str):
    """주제 폴더 + 개요 5종 세트 + 인덱스 생성

    표준 구조:
      {parent}/{topic}/
      ├── {topic}.md              (서브 인덱스)
      ├── 01_{topic} 개요.md
      ├── 02_{topic} 환경.md
      ├── 03_{topic} 사용.md
      ├── 04_{topic} APIs.md
      └── 05_{topic} 채널.md
    """
    target = resolve_folder(vault, folder_name)
    if not target:
        print(f"[ERROR] Folder not found: {folder_name}")
        return

    topic_dir = target / topic
    topic_dir.mkdir(exist_ok=True)

    created = []

    # 개요 5종 세트 생성
    for i, category in enumerate(OVERVIEW_SERIES, 1):
        fname = f"{i:02d}_{topic} {category}.md"
        fpath = topic_dir / fname
        if not fpath.exists():
            fpath.write_text(f"## {category}\n", encoding="utf-8")
            created.append(fname)

    # 서브 인덱스 파일 생성/갱신
    index_file = topic_dir / f"{topic}.md"
    links = ["## 개요"]
    for i, category in enumerate(OVERVIEW_SERIES, 1):
        stem = f"{i:02d}_{topic} {category}"
        links.append(f"- [[{stem}]]")
    index_file.write_text("\n".join(links) + "\n", encoding="utf-8")

    # 상위 인덱스에 [[위키링크]] 추가
    parent_index = target / f"{target.name}.md"
    if parent_index.exists():
        content = parent_index.read_text(encoding="utf-8")
        link_line = f"- [[{topic}]]"
        if link_line not in content:
            content = content.rstrip() + f"\n{link_line}\n"
            parent_index.write_text(content, encoding="utf-8")
            print(f"[OK] Parent index updated: {parent_index.relative_to(vault)}")

    print(f"[OK] Topic initialized: {topic_dir.relative_to(vault)}/")
    print(f"     Index: {topic}.md")
    print(f"     Created: {len(created)} files")
    for f in created:
        print(f"       - {f}")


def cmd_init_folder(vault: Path, folder_num: str, folder_name: str):
    """최상위 주제 폴더 + 인덱스 + 01_개요/ 5종 세트 생성

    표준 구조:
      01_obsidian/{NNNN}_{name}/
      ├── {NNNN}_{name}.md          (루트 인덱스)
      └── 01_개요/
          ├── 01_{name} 개요.md
          ├── 02_{name} 환경.md
          ├── 03_{name} 사용.md
          ├── 04_{name} APIs.md
          └── 05_{name} 채널.md
    """
    dir_name = f"{folder_num}_{folder_name}"
    folder_path = vault / dir_name

    if folder_path.exists():
        print(f"[WARN] Folder already exists: {dir_name}")
    else:
        folder_path.mkdir()
        print(f"[OK] Folder created: {dir_name}/")

    # 루트 인덱스
    index_file = folder_path / f"{dir_name}.md"
    if not index_file.exists():
        links = ["## 개요"]
        for i, category in enumerate(OVERVIEW_SERIES, 1):
            stem = f"{i:02d}_{folder_name} {category}"
            links.append(f"- [[{stem}]]")
        index_file.write_text("\n".join(links) + "\n", encoding="utf-8")
        print(f"[OK] Index created: {index_file.relative_to(vault)}")

    # 01_개요/ 서브폴더 + 5종 세트
    overview_dir = folder_path / "01_개요"
    overview_dir.mkdir(exist_ok=True)
    created = []
    for i, category in enumerate(OVERVIEW_SERIES, 1):
        fname = f"{i:02d}_{folder_name} {category}.md"
        fpath = overview_dir / fname
        if not fpath.exists():
            fpath.write_text(f"## {category}\n", encoding="utf-8")
            created.append(fname)

    print(f"[OK] Overview series: {len(created)} files in 01_개요/")
    for f in created:
        print(f"       - {f}")


def cmd_index(vault: Path, folder_name: str):
    """폴더 인덱스 파일 갱신"""
    target = resolve_folder(vault, folder_name)
    if not target:
        print(f"[ERROR] Folder not found: {folder_name}")
        return

    # 인덱스 파일 찾기
    index_candidates = [f for f in target.iterdir() if f.is_file() and f.suffix == ".md" and f.stem == target.name]
    if not index_candidates:
        index_file = target / f"{target.name}.md"
    else:
        index_file = index_candidates[0]

    # 하위 md 파일 목록 (인덱스 자신 제외)
    md_files = sorted([
        f for f in target.iterdir()
        if f.is_file() and f.suffix == ".md" and f != index_file
    ])

    links = ["## 개요"]
    for f in md_files:
        stem = f.stem
        links.append(f"- [[{stem}]]")

    index_file.write_text("\n".join(links) + "\n", encoding="utf-8")
    print(f"[OK] Index updated: {index_file.relative_to(vault)}")
    print(f"     Entries: {len(md_files)}")


def cmd_check(vault: Path, folder_prefix: str = None):
    """checklist.md 기반 스킬 건강 상태 검증 (C01~C06)

    Args:
        folder_prefix: 폴더 번호 접두사 (예: "0004") → 해당 폴더만 C05/C06 검사
    """
    if folder_prefix:
        print(f"[oosidi check {folder_prefix}]\n")
    else:
        print("[oosidi check]\n")
    skill_dir = Path(__file__).resolve().parent.parent
    ok_count = 0
    warn_count = 0
    error_count = 0
    info_count = 0

    # C01: 필수 파일 존재
    required = [skill_dir / "SKILL.md", skill_dir / "scripts" / "oosidi_run.py"]
    missing = [f for f in required if not f.exists()]
    if not missing:
        print("C01 필수 파일 존재       [OK]")
        ok_count += 1
    else:
        names = ", ".join(f.name for f in missing)
        print(f"C01 필수 파일 존재       [ERROR] 누락: {names}")
        error_count += 1

    # C02: 버전 일치 (SKILL.md version 텍스트 vs 스크립트 version 출력)
    skill_md = skill_dir / "SKILL.md"
    script_version = "v02"  # cmd_version 출력값과 동일하게 유지
    skill_version_ok = False
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        # SKILL.md의 version 행에서 버전 추출 (예: "v02")
        if script_version in content:
            skill_version_ok = True
    if skill_version_ok:
        print(f"C02 버전 일치            [OK] {script_version}")
        ok_count += 1
    else:
        print(f"C02 버전 일치            [ERROR] 스크립트={script_version}, SKILL.md 불일치")
        error_count += 1

    # C03: 볼트 경로 존재
    if vault.exists() and vault.is_dir():
        print(f"C03 볼트 경로 존재       [OK] {vault}")
        ok_count += 1
    else:
        print(f"C03 볼트 경로 존재       [ERROR] {vault}")
        error_count += 1

    # C04: 스크립트 구문 검증
    import subprocess
    script_path = skill_dir / "scripts" / "oosidi_run.py"
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(script_path)],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode == 0:
        print("C04 스크립트 구문 검증   [OK]")
        ok_count += 1
    else:
        print(f"C04 스크립트 구문 검증   [ERROR] {result.stderr.strip()}")
        error_count += 1

    # C05: 인덱스 파일 정합성
    broken_links = []
    all_folders = sorted([d for d in vault.iterdir() if d.is_dir() and not d.name.startswith(".")])
    folders = [d for d in all_folders if d.name.startswith(folder_prefix)] if folder_prefix else all_folders
    if folder_prefix and not folders:
        print(f"  ('{folder_prefix}'로 시작하는 폴더 없음)")
    elif folder_prefix:
        print(f"  대상 폴더: {', '.join(d.name for d in folders)}\n")
    for folder in folders:
        index_file = folder / f"{folder.name}.md"
        if not index_file.exists():
            continue
        try:
            content = index_file.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        import re
        links = re.findall(r"\[\[([^\]]+)\]\]", content)
        for link in links:
            # 위키링크 대상 파일 검색 (폴더 내 재귀)
            candidates = list(folder.rglob(f"{link}.md"))
            if not candidates:
                broken_links.append(f"{folder.name}/{index_file.name} → [[{link}]]")
    if not broken_links:
        print("C05 인덱스 파일 정합성   [OK]")
        ok_count += 1
    else:
        print(f"C05 인덱스 파일 정합성   [WARN] 깨진 링크 {len(broken_links)}건")
        for bl in broken_links[:10]:
            print(f"      - {bl}")
        if len(broken_links) > 10:
            print(f"      ... 외 {len(broken_links) - 10}건")
        warn_count += 1

    # C06: 빈 문서 탐지 (헤더만 있는 문서: 30바이트 이하)
    empty_docs = []
    scan_dirs = folders if folder_prefix else [vault]
    for scan_dir in scan_dirs:
        for md_file in scan_dir.rglob("*.md"):
            try:
                size = md_file.stat().st_size
                if size <= 30:
                    content = md_file.read_text(encoding="utf-8").strip()
                    # 헤더 한 줄만 있는 경우
                    lines = [l for l in content.split("\n") if l.strip()]
                    if len(lines) <= 1:
                        empty_docs.append(str(md_file.relative_to(vault)))
            except (UnicodeDecodeError, PermissionError):
                continue
    if not empty_docs:
        print("C06 빈 문서 탐지         [OK]")
        ok_count += 1
    else:
        print(f"C06 빈 문서 탐지         [INFO] {len(empty_docs)}건")
        for ed in empty_docs[:10]:
            print(f"      - {ed}")
        if len(empty_docs) > 10:
            print(f"      ... 외 {len(empty_docs) - 10}건")
        info_count += 1

    # 소계
    print(f"\n소계: OK:{ok_count} | WARN:{warn_count} | ERROR:{error_count} | INFO:{info_count}")


def cmd_add_checklist(item: str):
    """체크리스트에 새 항목 추가"""
    checklist_path = Path(__file__).resolve().parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[ERROR] checklist.md not found: {checklist_path}")
        return

    content = checklist_path.read_text(encoding="utf-8")

    # 기존 ID에서 최대 번호 추출
    import re
    ids = re.findall(r"\| C(\d+) \|", content)
    next_num = max(int(n) for n in ids) + 1 if ids else 1
    new_id = f"C{next_num:02d}"

    # 체크리스트 테이블(| ID | 항목 | 이후)의 마지막 데이터 행 찾기
    lines = content.split("\n")
    insert_idx = None
    in_checklist_table = False
    for i, line in enumerate(lines):
        if "| ID |" in line and "항목" in line:
            in_checklist_table = True
            continue
        if in_checklist_table and line.startswith("| C") and "|" in line:
            insert_idx = i
        elif in_checklist_table and not line.startswith("|"):
            break

    if insert_idx is None:
        print("[ERROR] 체크리스트 테이블을 찾을 수 없습니다.")
        return

    new_row = f"| {new_id} | {item} | (검증 내용 작성 필요) | INFO |"
    lines.insert(insert_idx + 1, new_row)
    checklist_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"[OK] 체크리스트 항목 추가: {new_id} - {item}")
    print(f"     파일: {checklist_path.relative_to(checklist_path.parent.parent.parent.parent.parent)}")


def cmd_help():
    """도움말"""
    print("# oosidi - 옵시디언 볼트 문서 관리\n")
    print("Usage: oosidi <command> [args]\n")
    print("Commands:")
    print("  help                              서브명령어 목록")
    print("  version                           버전 정보")
    print("  status                            볼트 전체 현황")
    print("  run                               상태 점검 (= status)")
    print('  list <folder>                     폴더 문서 목록')
    print('  create <folder> "<title>"         새 문서 생성')
    print("  index <folder>                    인덱스 파일 갱신")
    print('  search "<keyword>"                키워드 검색')
    print('  init-topic <folder> "<topic>"     주제 폴더 + 개요 5종 세트 생성')
    print('  init-folder <NNNN> "<name>"       최상위 폴더 + 인덱스 + 개요 5종 세트')
    print("  check                             체크리스트 기반 건강 상태 검증")
    print('  add checklist "<항목>"            체크리스트 항목 추가')


def cmd_show_checklist():
    """references/checklist.md 내용 출력"""
    checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[{SKILL_NAME}] checklist.md 없음: {checklist_path}")
        return
    print(checklist_path.read_text(encoding="utf-8"))


def main():
    vault = get_vault_path()

    if not vault.exists():
        print(f"[ERROR] Vault not found: {vault}")
        sys.exit(1)

    args = sys.argv[1:]
    cmd = args[0] if args else "run"
    if cmd in ("show",) and len(args) > 1 and args[1].lower() == "checklist":
        cmd_show_checklist()
        return

    if cmd == "help":
        cmd_help()
    elif cmd == "version":
        print("oosidi v02")
    elif cmd == "add" and len(args) >= 3 and args[1] == "checklist":
        cmd_add_checklist(args[2])
    elif cmd == "check":
        folder_prefix = args[1] if len(args) >= 2 else None
        cmd_check(vault, folder_prefix)
    elif cmd in ("status", "run"):
        cmd_status(vault)
    elif cmd == "list" and len(args) >= 2:
        cmd_list(vault, args[1])
    elif cmd == "search" and len(args) >= 2:
        cmd_search(vault, args[1])
    elif cmd == "create" and len(args) >= 3:
        cmd_create(vault, args[1], args[2])
    elif cmd == "index" and len(args) >= 2:
        cmd_index(vault, args[1])
    elif cmd == "init-topic" and len(args) >= 3:
        cmd_init_topic(vault, args[1], args[2])
    elif cmd == "init-folder" and len(args) >= 3:
        cmd_init_folder(vault, args[1], args[2])
    else:
        print(f"[ERROR] Unknown command or missing args: {' '.join(args)}")
        cmd_help()


if __name__ == "__main__":
    main()
