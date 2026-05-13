#!/usr/bin/env python3
"""
oofeature_rmdup.py - 같은 상세번호(dXXXX)에 복수 단계/파일이 존재할 때 정리
Usage:
  uv run python oofeature_rmdup.py [--sp N] [--all] [--dry-run] [--verbose]
  uv run python oofeature_rmdup.py --sp 04         # SP04만 검사
  uv run python oofeature_rmdup.py --all           # 전체 SP 검사
  uv run python oofeature_rmdup.py --all --dry-run # 삭제 미리보기
  uv run python oofeature_rmdup.py --verbose       # 파일 상세 정보 표시

판단 기준:
  1. 단계가 다른 중복: 더 높은 단계(기획<설계<구현<검증<완료) 파일 유지
  2. 단계가 같은 중복: 수정일 최신 파일 유지, 동점이면 줄 수 많은 파일 유지
"""
import sys
import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
DOC_ROOT = PROJECT_ROOT / "00_doc"

STAGE_ORDER = ["상세기획", "상세설계", "상세구현", "상세검증", "상세완료"]
STAGE_RANK = {s: i for i, s in enumerate(STAGE_ORDER)}

FILE_PATTERN = re.compile(r'^(d\w+)_(상세기획|상세설계|상세구현|상세검증|상세완료)_(.+)\.md$')


def get_current_sp() -> str:
    context_file = PROJECT_ROOT / ".claude" / "skills" / "oocontext" / "references" / "current_context.json"
    if context_file.exists():
        try:
            data = json.loads(context_file.read_text(encoding="utf-8"))
            return str(data.get("sp", "00"))
        except Exception:
            pass
    return "00"


def file_info(path: Path) -> dict:
    stat = path.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime)
    try:
        lines = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
    except Exception:
        lines = 0
    return {"mtime": mtime, "lines": lines, "path": path}


def select_best(files_info: list) -> Path:
    """수정일 최신 → 동점이면 줄 수 많은 파일 선택"""
    best = max(files_info, key=lambda x: (x["mtime"], x["lines"]))
    return best["path"]


def scan_sp_dir(sp_dir: Path) -> dict:
    """doc_num → [(stage, path), ...] 그룹핑"""
    groups = defaultdict(list)
    if not sp_dir.exists():
        return groups
    for f in sp_dir.glob("d*_상세*.md"):
        m = FILE_PATTERN.match(f.name)
        if m:
            doc_num, stage, _ = m.groups()
            groups[doc_num].append((stage, f))
    return groups


def resolve_group(doc_num: str, files: list, verbose: bool) -> tuple:
    """
    같은 doc_num의 파일들에서 유지할 파일 1개와 삭제할 파일들을 반환.
    Returns: (keep_path, [(stage, path), ...] to_delete, reason_str)
    """
    # stage별로 묶기
    stage_groups = defaultdict(list)
    for stage, path in files:
        stage_groups[stage].append(path)

    # 각 stage의 대표 파일 선택 (같은 단계 중복 처리)
    stage_reps = {}  # stage -> (keep_path, [delete_paths])
    same_stage_dups = []

    for stage, paths in stage_groups.items():
        if len(paths) == 1:
            stage_reps[stage] = (paths[0], [])
        else:
            infos = [file_info(p) for p in paths]
            keep = select_best(infos)
            deletes = [p for p in paths if p != keep]
            stage_reps[stage] = (keep, deletes)
            same_stage_dups.append((stage, keep, deletes, infos))

    # 여러 단계 중 최신 단계 선택
    best_stage = max(stage_reps.keys(), key=lambda s: STAGE_RANK.get(s, -1))
    keep_path = stage_reps[best_stage][0]

    # 삭제 목록: 다른 단계 모든 파일 + 같은 단계 중복 파일
    to_delete = []
    for stage, (rep_path, dup_deletes) in stage_reps.items():
        to_delete.extend(dup_deletes)  # 같은 단계 중복 제거
        if stage != best_stage:
            to_delete.append(rep_path)  # 낮은 단계 대표 파일

    # 판단 이유 구성
    reasons = []
    if len(stage_reps) > 1:
        other_stages = [s for s in stage_reps if s != best_stage]
        reasons.append(f"최신 단계 '{best_stage}' 유지 (제거: {', '.join(other_stages)})")
    for stage, keep, deletes, infos in same_stage_dups:
        keep_info = next(i for i in infos if i["path"] == keep)
        del_info = [i for i in infos if i["path"] != keep]
        reasons.append(
            f"'{stage}' 중복 {len(deletes)+1}개 → 최신본 유지 "
            f"({keep_info['mtime'].strftime('%m/%d %H:%M')}, {keep_info['lines']}줄)"
        )

    return keep_path, to_delete, " | ".join(reasons)


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("help", "-h", "--help"):
        print("Usage:")
        print("  oof rmdup [--sp N] [--all] [--dry-run] [--verbose]")
        print("  --sp N      특정 SP만 검사 (기본: 현재 SP)")
        print("  --all       전체 SP 검사")
        print("  --dry-run   삭제 미리보기 (실제 삭제 안 함)")
        print("  --verbose   파일별 수정일·줄 수 표시")
        return

    sp = None
    scan_all = False
    dry_run = False
    verbose = False

    i = 0
    while i < len(args):
        if args[i] == "--sp" and i + 1 < len(args):
            sp = args[i + 1]; i += 2
        elif args[i] == "--all":
            scan_all = True; i += 1
        elif args[i] == "--dry-run":
            dry_run = True; i += 1
        elif args[i] == "--verbose":
            verbose = True; i += 1
        else:
            i += 1

    if scan_all:
        sp_dirs = sorted(DOC_ROOT.glob("sp*"))
    else:
        sp_str = sp if sp else get_current_sp()
        sp_dirs = [DOC_ROOT / f"sp{sp_str.zfill(2)}"]

    total_dup = 0
    total_deleted = 0

    print("# oofeature rmdup - 중복 상세 문서 정리\n")
    if dry_run:
        print("> [dry-run] 실제 삭제 없음\n")

    found_any = False
    for sp_dir in sp_dirs:
        groups = scan_sp_dir(sp_dir)
        dups = {k: v for k, v in groups.items() if len(v) > 1}

        if not dups:
            print(f"[{sp_dir.name}] 중복 없음")
            continue

        found_any = True
        print(f"\n## {sp_dir.name} — 중복 {len(dups)}건\n")

        for doc_num, files in sorted(dups.items()):
            total_dup += 1
            keep_path, to_delete, reason = resolve_group(doc_num, files, verbose)

            print(f"### {doc_num}  ({reason})")

            # 전체 파일 목록 표시
            all_paths = [p for _, p in files]
            for _, path in sorted(files, key=lambda x: STAGE_RANK.get(x[0], -1)):
                marker = "✅ 유지" if path == keep_path else "🗑️  삭제"
                if verbose:
                    info = file_info(path)
                    print(f"  {marker}  {path.name}  ({info['mtime'].strftime('%m/%d %H:%M')}, {info['lines']}줄)")
                else:
                    print(f"  {marker}  {path.name}")

            if dry_run:
                print(f"  → [dry-run] {len(to_delete)}개 삭제 예정\n")
            else:
                for p in to_delete:
                    p.unlink()
                    total_deleted += 1
                print(f"  → 삭제 완료: {len(to_delete)}개\n")

    print("\n## 완료")
    if not found_any:
        print("- 중복 파일 없음")
    else:
        print(f"- 중복 그룹: {total_dup}건")
        if dry_run:
            print("- [dry-run] 실제 삭제 없음 (--dry-run 제거 후 재실행)")
        else:
            print(f"- 삭제: {total_deleted}개 파일")


if __name__ == "__main__":
    main()
