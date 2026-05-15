"""00_doc/ 플랫 구조 → SP별 서브폴더 마이그레이션 스크립트

실행: uv run python 00_doc/migrate_to_sp_folders.py [--dry-run]

1단계: SP별 서브폴더 생성 + 파일 이동
2단계: 전체 프로젝트의 경로 참조 업데이트
"""

import argparse
import re
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOC_DIR = PROJECT_ROOT / "00_doc"

# tutorial/ 폴더는 이동하지 않음
EXCLUDE_DIRS = {"tutorial"}


def get_sp_from_docnum(filename: str) -> str | None:
    """파일명에서 SP 번호 추출. 예: d30004_todo.md → sp03"""
    m = re.match(r'd(\d+)', filename)
    if not m:
        return None
    num = int(m.group(1))
    if num < 10000:
        return "sp00"
    sp = num // 10000
    return f"sp{sp:02d}"


def collect_files_to_move() -> list[tuple[Path, Path]]:
    """이동 대상 파일 목록: (원본, 대상) 쌍"""
    moves = []
    for f in sorted(DOC_DIR.glob("*.md")):
        sp = get_sp_from_docnum(f.name)
        if sp is None:
            continue
        dest = DOC_DIR / sp / f.name
        moves.append((f, dest))
    return moves


def update_references(dry_run: bool = False) -> int:
    """프로젝트 전체에서 00_doc/dNNNN 참조를 00_doc/spNN/dNNNN으로 변경"""
    # 검색 대상 디렉토리
    search_dirs = [
        PROJECT_ROOT / ".claude",
        PROJECT_ROOT / "CLAUDE.md",
        DOC_DIR,
    ]

    # 대상 파일 수집
    target_files = []
    for sd in search_dirs:
        if sd.is_file():
            target_files.append(sd)
        elif sd.is_dir():
            target_files.extend(sd.rglob("*.md"))
            target_files.extend(sd.rglob("*.py"))
            target_files.extend(sd.rglob("*.json"))

    # 패턴: 00_doc/dNNNN 또는 00_doc\dNNNN 또는 "00_doc" 디렉토리 내 dNNNN
    # 핵심: 00_doc/d{숫자} → 00_doc/sp{NN}/d{숫자}
    pattern = re.compile(r'(00_doc[/\\])d(\d+)')

    updated_count = 0

    for fpath in target_files:
        if not fpath.exists() or fpath.name == "migrate_to_sp_folders.py":
            continue
        try:
            content = fpath.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue

        original = content

        def replacer(m):
            prefix = m.group(1)  # "00_doc/" or "00_doc\"
            num_str = m.group(2)
            num = int(num_str)
            if num < 10000:
                sp = "sp00"
            else:
                sp = f"sp{num // 10000:02d}"
            return f"{prefix}{sp}/{prefix[-1] if prefix[-1] in '/\\\\' else '/'}d{num_str}"

        # 더 정확한 치환: 00_doc/dNNNN → 00_doc/spNN/dNNNN
        def smart_replace(m):
            prefix = m.group(1)  # "00_doc/" or "00_doc\"
            num_str = m.group(2)
            num = int(num_str)
            if num < 10000:
                sp = "sp00"
            else:
                sp = f"sp{num // 10000:02d}"
            sep = "/" if "/" in prefix else "\\"
            return f"00_doc{sep}{sp}{sep}d{num_str}"

        new_content = pattern.sub(smart_replace, content)

        if new_content != original:
            changes = len(pattern.findall(original))
            if dry_run:
                print(f"  [UPDATE] {fpath.relative_to(PROJECT_ROOT)} ({changes}건)")
            else:
                fpath.write_text(new_content, encoding="utf-8")
                print(f"  [UPDATE] {fpath.relative_to(PROJECT_ROOT)} ({changes}건)")
            updated_count += changes

    return updated_count


def update_python_scripts(dry_run: bool = False) -> int:
    """Python 스크립트의 동적 경로 패턴 업데이트

    패턴: PROJECT_ROOT / "00_doc" / f"d{sp}0004_todo.md"
    변경: PROJECT_ROOT / "00_doc" / f"sp{sp:02d}" / f"d{sp}0004_todo.md"

    이 패턴은 자동 치환이 어려우므로 수동 목록으로 처리
    """
    # 동적 경로를 사용하는 스크립트 목록 (grep 결과 기반)
    scripts_with_dynamic_paths = [
        ".claude/skills/oocheck/scripts/oocheck_run.py",
        ".claude/skills/oocontext/scripts/oocontext_run.py",
        ".claude/skills/oodoc/scripts/oodoc_check.py",
        ".claude/skills/oodoc/scripts/oodoc_clear.py",
        ".claude/skills/oodoc/scripts/oodoc_run.py",
        ".claude/skills/ooenv/scripts/ooenv_run.py",
        ".claude/skills/oonext/scripts/oonext_run.py",
        ".claude/skills/oonote/scripts/oonote_run.py",
        ".claude/skills/ooopti/scripts/ooopti_run.py",
        ".claude/skills/oostart/scripts/oostart_run.py",
        ".claude/skills/ootodo/scripts/ootodo_run.py",
        ".claude/skills/ootutorial/scripts/ootutorial_run.py",
        ".claude/skills/oobatch/scripts/oobatch_run.py",
        ".claude/skills/oosync/scripts/oosync_run.py",
    ]

    count = 0
    for script_rel in scripts_with_dynamic_paths:
        script_path = PROJECT_ROOT / script_rel
        if not script_path.exists():
            continue
        try:
            content = script_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue

        original = content

        # 패턴 1: "00_doc" / f"d{...}" → "00_doc" / f"sp{sp_folder}" / f"d{...}"
        # 패턴 2: "00_doc" / "d0004_todo.md" → "00_doc" / "sp00" / "d0004_todo.md"
        # 패턴 3: Path("00_doc") 관련

        # 정적 참조: "00_doc/d0004" → "00_doc/sp00/d0004"  (이미 update_references에서 처리)
        # 동적 참조: DOC_DIR / f"d{sp_num}..." 패턴은 스크립트마다 다르므로 여기서는 리포트만

        # DOC_DIR 또는 "00_doc" 직접 사용 패턴 찾기
        dynamic_patterns = re.findall(r'(?:DOC_DIR|"00_doc"|\'00_doc\')\s*/\s*f?["\']d\{', content)
        if dynamic_patterns:
            count += len(dynamic_patterns)
            if dry_run:
                print(f"  [MANUAL] {script_rel} - 동적 경로 {len(dynamic_patterns)}건 (수동 수정 필요)")

    return count


def main():
    parser = argparse.ArgumentParser(description="00_doc SP별 서브폴더 마이그레이션")
    parser.add_argument("--dry-run", action="store_true", help="실제 이동/수정 없이 미리보기")
    args = parser.parse_args()

    print("# 00_doc/ SP별 서브폴더 마이그레이션\n")
    if args.dry_run:
        print("(dry-run 모드: 실제 변경 없음)\n")

    # 1단계: 파일 이동
    moves = collect_files_to_move()
    sp_counts: dict[str, int] = {}
    for src, dst in moves:
        sp = dst.parent.name
        sp_counts[sp] = sp_counts.get(sp, 0) + 1

    print("## 1단계: 파일 이동\n")
    print("| SP | 파일 수 |")
    print("|:--:|:------:|")
    for sp in sorted(sp_counts):
        print(f"| {sp} | {sp_counts[sp]} |")
    print(f"\n총 {len(moves)}개 파일 이동 예정\n")

    if not args.dry_run:
        for src, dst in moves:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
        print(f"[OK] {len(moves)}개 파일 이동 완료\n")

    # 2단계: 정적 참조 업데이트
    print("## 2단계: 참조 업데이트\n")
    ref_count = update_references(dry_run=args.dry_run)
    print(f"\n정적 참조 업데이트: {ref_count}건\n")

    # 3단계: 동적 경로 리포트
    print("## 3단계: 동적 경로 (수동 수정 필요)\n")
    dynamic_count = update_python_scripts(dry_run=True)  # 항상 리포트만
    print(f"\n동적 경로: {dynamic_count}건 (수동 수정 필요)\n")

    print("## 완료")
    if args.dry_run:
        print("실제 실행: `uv run python 00_doc/migrate_to_sp_folders.py`")


if __name__ == "__main__":
    main()
