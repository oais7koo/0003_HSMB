#!/usr/bin/env python3
"""
oodata_run.py - data/ 폴더 문서화/백업/복원 스킬
Usage: uv run python .claude/skills/oodata/scripts/oodata_run.py [run|comment|backup|restore|list|status|help]
"""
import sys
import shutil
from datetime import datetime
from pathlib import Path
import re as _re

# --- oo_common inline ---
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

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

SKILL_NAME = "oodata"
VERSION = "v04"

# 프로젝트 루트: scripts/ → oodata/ → skills/ → .claude/ → project_root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_BACKUP_PATH = Path(r"f:\udd\data_exa\exa63_dual_branch")
# data/ 는 프로젝트 공통 폴더 — SP 무관, 단일 문서로 관리
DATA_DOC_PATH = PROJECT_ROOT / "00_doc" / "sp00" / "d0007_data.md"


# ============================================================
# 유틸리티
# ============================================================

def ask_backup_path(default: Path) -> Path:
    print(f"백업 경로 입력 (Enter = {default}): ", end="", flush=True)
    user_input = input().strip()
    return Path(user_input) if user_input else default


def folder_size_mb(folder: Path) -> float:
    try:
        return sum(f.stat().st_size for f in folder.rglob("*") if f.is_file()) / (1024 * 1024)
    except Exception:
        return 0.0


def list_data_folders() -> list:
    """data/ 내 실제 ps 폴더 목록 (_backup 마커·숨김 제외)"""
    if not DATA_DIR.exists():
        return []
    return sorted(
        p for p in DATA_DIR.iterdir()
        if p.is_dir() and not p.name.endswith("_backup") and not p.name.startswith(".")
    )


def list_backup_markers() -> list:
    """data/ 내 _backup 마커 폴더 목록"""
    if not DATA_DIR.exists():
        return []
    return sorted(p for p in DATA_DIR.iterdir() if p.is_dir() and p.name.endswith("_backup"))


def select_from_list(items: list, label_fn, prompt: str) -> list:
    """목록에서 사용자 선택 (번호 / 쉼표 복수 / all / 0=취소)"""
    if not items:
        print("[INFO] 선택 가능한 항목이 없습니다.")
        return []

    print(f"\n{prompt}")
    for i, item in enumerate(items, 1):
        print(f"  [{i}] {label_fn(item)}")
    print(f"  [0] 취소\n")
    print("선택 (번호, 복수=쉼표 구분, all=전체): ", end="", flush=True)
    raw = input().strip()

    if not raw or raw == "0":
        return []
    if raw.lower() == "all":
        return list(items)

    selected = []
    for token in raw.split(","):
        token = token.strip()
        if token.isdigit():
            idx = int(token) - 1
            if 0 <= idx < len(items):
                selected.append(items[idx])
            else:
                print(f"  [WARN] 범위 초과: {token}")
    return selected


def confirm(message: str) -> bool:
    print(f"\n{message} (y/N): ", end="", flush=True)
    return input().strip().lower() == "y"


# ============================================================
# 서브명령어
# ============================================================

def cmd_list():
    print(f"\n[oodata list] data/ 폴더 현황")
    print(f"  DATA_DIR: {DATA_DIR}\n")

    folders = list_data_folders()
    markers = list_backup_markers()

    print(f"실제 폴더 ({len(folders)}개):")
    if folders:
        for f in folders:
            mb = folder_size_mb(f)
            print(f"  {f.name:<25}  {mb:>8.1f} MB")
    else:
        print("  (없음)")

    print(f"\n백업 마커 ({len(markers)}개) — 외부로 이동된 항목:")
    if markers:
        for m in markers:
            ps_name = m.name.removesuffix("_backup")
            print(f"  {m.name:<25}  (원본: {ps_name})")
    else:
        print("  (없음)")


def cmd_backup():
    print(f"\n[oodata backup]\n")

    backup_root = ask_backup_path(DEFAULT_BACKUP_PATH)

    folders = list_data_folders()

    def label(f: Path) -> str:
        mb = folder_size_mb(f)
        return f"{f.name}  ({mb:.1f} MB)"

    selected = select_from_list(folders, label, "백업할 폴더를 선택하세요:")
    if not selected:
        print("[INFO] 취소되었습니다.")
        return

    print(f"\n  백업 경로 : {backup_root}")
    print(f"  대상      : {[f.name for f in selected]}")

    if not confirm("백업을 진행하시겠습니까?"):
        print("[INFO] 취소되었습니다.")
        return

    backup_root.mkdir(parents=True, exist_ok=True)

    success, errors = [], []
    for folder in selected:
        dest = backup_root / folder.name
        marker = DATA_DIR / f"{folder.name}_backup"
        try:
            if dest.exists():
                print(f"  [SKIP] {folder.name}: 대상 경로 이미 존재 ({dest})")
                errors.append((folder.name, "대상 경로 이미 존재"))
                continue
            print(f"  이동 중: {folder.name} → {dest} ...", end="", flush=True)
            shutil.move(str(folder), str(dest))
            marker.mkdir(exist_ok=True)
            print(" ✓")
            success.append(folder.name)
        except Exception as e:
            print(f" FAIL: {e}")
            errors.append((folder.name, str(e)))

    print(f"\n완료: 성공 {len(success)}개 / 실패 {len(errors)}개")
    if errors:
        for name, reason in errors:
            print(f"  [FAIL] {name}: {reason}")


def cmd_restore():
    print(f"\n[oodata restore]\n")

    backup_root = ask_backup_path(DEFAULT_BACKUP_PATH)

    markers = list_backup_markers()
    if not markers:
        print("[INFO] 복원할 _backup 마커가 없습니다.")
        return

    # (marker_path, ps_name, src_path) 튜플 목록
    restore_items = [
        (m, m.name.removesuffix("_backup"), backup_root / m.name.removesuffix("_backup"))
        for m in markers
    ]

    def label(item) -> str:
        m, ps_name, src = item
        exists = "존재" if src.exists() else "없음"
        return f"{ps_name:<25}  외부: [{exists}] {src}"

    selected = select_from_list(restore_items, label, "복원할 항목을 선택하세요:")
    if not selected:
        print("[INFO] 취소되었습니다.")
        return

    print(f"\n  복원 경로 : {backup_root}")
    print(f"  대상      : {[ps_name for _, ps_name, _ in selected]}")

    if not confirm("복원을 진행하시겠습니까?"):
        print("[INFO] 취소되었습니다.")
        return

    success, errors = [], []
    for marker, ps_name, src in selected:
        dest = DATA_DIR / ps_name
        try:
            if not src.exists():
                print(f"  [SKIP] {ps_name}: 외부 경로 없음 ({src})")
                errors.append((ps_name, "외부 경로 없음"))
                continue
            if dest.exists():
                print(f"  [SKIP] {ps_name}: data/ 에 이미 존재")
                errors.append((ps_name, "data/ 에 이미 존재"))
                continue
            print(f"  복원 중: {src} → {dest} ...", end="", flush=True)
            shutil.move(str(src), str(dest))
            marker.rmdir()
            print(" ✓")
            success.append(ps_name)
        except Exception as e:
            print(f" FAIL: {e}")
            errors.append((ps_name, str(e)))

    print(f"\n완료: 성공 {len(success)}개 / 실패 {len(errors)}개")
    if errors:
        for name, reason in errors:
            print(f"  [FAIL] {name}: {reason}")


def scan_all_data_entries() -> list:
    """data/ 의 실제 폴더 + 백업 마커를 통합한 항목 목록.
    Returns: [(name, status, size_mb), ...]  status ∈ {'존재', '백업됨'}
    """
    folders = list_data_folders()
    markers = list_backup_markers()
    folder_names = {f.name for f in folders}
    backup_only = {m.name.removesuffix("_backup") for m in markers} - folder_names

    entries = []
    for f in folders:
        entries.append((f.name, "존재", folder_size_mb(f)))
    for name in backup_only:
        entries.append((name, "백업됨", 0.0))
    return sorted(entries, key=lambda x: x[0])


def parse_existing_descriptions(doc_path: Path) -> dict:
    """기존 문서에서 '폴더명 → 설명' 매핑 추출 (보존용)."""
    if not doc_path.exists():
        return {}
    desc = {}
    for line in doc_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        # 헤더/구분선 스킵
        if cells[0] in ("폴더", "") or set(cells[0]) <= set("-: "):
            continue
        folder_clean = cells[0].rstrip("/").strip()
        desc[folder_clean] = cells[2]
    return desc


def gather_folder_detail(folder: Path, max_files: int = 20000) -> dict:
    """폴더의 파일 통계·서브폴더 구조 수집.
    Returns: {file_count, ext_counts, subdirs, truncated}
    """
    ext_counts: dict = {}
    file_count = 0
    truncated = False
    subdirs: list = []

    if not folder.exists():
        return {"file_count": 0, "ext_counts": {}, "subdirs": [], "truncated": False}

    # 1단계 서브폴더 (각 서브폴더의 재귀 파일 수)
    try:
        for child in sorted(folder.iterdir()):
            if child.is_dir() and not child.name.startswith("."):
                try:
                    sub_count = sum(1 for p in child.rglob("*") if p.is_file())
                except Exception:
                    sub_count = -1
                subdirs.append((child.name, sub_count))
    except Exception:
        pass

    # 전체 파일 / 확장자 카운트 (max_files 제한)
    try:
        for f in folder.rglob("*"):
            if not f.is_file():
                continue
            file_count += 1
            if file_count > max_files:
                truncated = True
                break
            ext = f.suffix.lower() or "(확장자없음)"
            ext_counts[ext] = ext_counts.get(ext, 0) + 1
    except Exception:
        pass

    return {
        "file_count": file_count,
        "ext_counts": ext_counts,
        "subdirs": subdirs,
        "truncated": truncated,
    }


_EXT_LABEL = {
    ".png": "이미지", ".jpg": "이미지", ".jpeg": "이미지", ".bmp": "이미지",
    ".gif": "이미지", ".tif": "이미지", ".tiff": "이미지", ".webp": "이미지",
    ".csv": "CSV 데이터", ".tsv": "TSV 데이터", ".parquet": "Parquet 데이터",
    ".json": "JSON 데이터", ".yaml": "YAML 설정", ".yml": "YAML 설정", ".toml": "TOML 설정",
    ".pdf": "PDF 문서", ".md": "Markdown 문서", ".txt": "텍스트",
    ".docx": "Word 문서", ".xlsx": "Excel 시트", ".pptx": "PPT",
    ".ttf": "폰트", ".otf": "폰트", ".woff": "폰트", ".woff2": "폰트",
    ".py": "Python 스크립트", ".ipynb": "Jupyter 노트북",
    ".js": "JavaScript", ".ts": "TypeScript", ".html": "HTML", ".css": "CSS",
    ".zip": "압축", ".tar": "압축", ".gz": "압축", ".7z": "압축",
    ".npy": "NumPy 배열", ".npz": "NumPy 배열", ".pkl": "Pickle",
    ".pt": "PyTorch 모델", ".pth": "PyTorch 모델", ".onnx": "ONNX 모델", ".h5": "HDF5",
    ".mp4": "동영상", ".mov": "동영상", ".avi": "동영상",
    ".mp3": "오디오", ".wav": "오디오",
    ".db": "DB", ".sqlite": "DB",
}


def guess_folder_purpose(name: str, ext_counts: dict) -> str:
    """폴더명·확장자 분포로 성격 추정."""
    name_lower = name.lower()
    parts = []

    # 폴더명 키워드
    name_hints = {
        "env": "환경 설정",
        "capture": "화면 캡처/스크린샷",
        "font": "폰트 자산",
        "csv": "CSV 데이터",
        "backup": "백업",
        "design": "디자인 자산",
        "sample": "샘플 데이터",
        "memory": "메모리/지식 저장소",
        "gemini": "Gemini 관련",
        "claude": "Claude 관련",
        "old": "구버전/보관용",
        "tunnel": "터널 데이터",
        "crack": "균열 데이터",
        "pocketbase": "PocketBase DB",
    }
    for key, hint in name_hints.items():
        if key in name_lower:
            parts.append(hint)
            break

    # 확장자 기반
    if not ext_counts:
        parts.append("빈 폴더")
    else:
        total = sum(ext_counts.values())
        top_ext, top_n = max(ext_counts.items(), key=lambda x: x[1])
        ext_label = _EXT_LABEL.get(top_ext, top_ext)
        ratio = top_n / total
        if ratio >= 0.7:
            parts.append(f"{ext_label} 위주 ({top_n}/{total})")
        else:
            parts.append(f"혼합 (최다 {ext_label} {top_n}/{total})")

    # ps번호 정책
    if _re.match(r"^ps1\d{3}", name) or _re.match(r"^ps10\d{2}", name):
        parts.append("원본 데이터 추정 (백업 정책: 제외)")
    elif _re.match(r"^ps3\d{3}", name):
        parts.append("Inopam 실험 결과 추정 (백업 대상)")
    elif _re.match(r"^ps4\d{3}", name):
        parts.append("CrackSeg9k 실험 결과 추정 (백업 대상)")
    elif _re.match(r"^ps[6-9]\d{3}", name):
        parts.append("SP별 워킹 데이터 추정")

    return " · ".join(parts)


def build_detail_section(entries: list, descriptions: dict) -> str:
    """폴더별 상세 섹션 생성."""
    lines = ["## 폴더 상세", ""]
    for name, status, mb in entries:
        folder = DATA_DIR / name
        comment = descriptions.get(name, "")

        lines.append(f"### {name}/")
        lines.append("")
        status_line = f"- 상태: {status}"
        if status == "존재" and mb > 0:
            status_line += f" ({mb:.1f} MB)"
        lines.append(status_line)
        if comment:
            lines.append(f"- 코멘트: {comment}")

        if status == "백업됨":
            lines.append("- 비고: 외부 경로로 이동됨 (data/ 본체 없음)")
            lines.append("")
            continue

        detail = gather_folder_detail(folder)
        file_count_str = f"{detail['file_count']}개"
        if detail["truncated"]:
            file_count_str += " (≥, 스캔 제한)"
        lines.append(f"- 총 파일 수: {file_count_str}")

        # 확장자 분포 (상위 5)
        if detail["ext_counts"]:
            top5 = sorted(detail["ext_counts"].items(), key=lambda x: -x[1])[:5]
            ext_str = ", ".join(f"`{ext}` {cnt}" for ext, cnt in top5)
            lines.append(f"- 주요 확장자: {ext_str}")

        # 서브폴더 (최대 20개)
        if detail["subdirs"]:
            lines.append("- 서브폴더:")
            for sub_name, sub_count in detail["subdirs"][:20]:
                cnt_str = f"{sub_count} files" if sub_count >= 0 else "?"
                lines.append(f"  - `{sub_name}/` ({cnt_str})")
            if len(detail["subdirs"]) > 20:
                lines.append(f"  - … 외 {len(detail['subdirs']) - 20}개")
        else:
            lines.append("- 서브폴더: 없음 (루트에 파일만)")

        # 추정
        lines.append(f"- 추정 성격: {guess_folder_purpose(name, detail['ext_counts'])}")
        lines.append("")

    return "\n".join(lines)


def build_data_doc(entries: list, descriptions: dict) -> str:
    """d0007_data.md 본문 생성 (SP 무관, 프로젝트 공통)."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "# data/ 폴더 구조 (프로젝트 공통)",
        "",
        "> data/ 는 SP에 무관한 프로젝트 루트 공통 폴더이며, 본 문서는 oodata 스킬이 관리한다.",
        "",
        "## 문서 이력 관리",
        f"- {now} — oodata run 자동 생성/업데이트",
        "",
        "## 서브폴더 목록",
        "",
        "| 폴더 | 상태 | 설명 |",
        "|------|------|------|",
    ]
    for name, status, mb in entries:
        if status == "존재" and mb > 0:
            status_cell = f"존재 ({mb:.1f} MB)"
        else:
            status_cell = status
        desc = descriptions.get(name, "")
        lines.append(f"| {name}/ | {status_cell} | {desc} |")
    lines += [
        "",
        f"> data/ 경로: `{DATA_DIR}`",
        f"> 외부 백업 기본 경로: `{DEFAULT_BACKUP_PATH}`",
        "",
    ]
    # 상세 섹션 추가
    lines.append(build_detail_section(entries, descriptions))
    return "\n".join(lines)


def cmd_run():
    DATA_DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

    entries = scan_all_data_entries()
    existing_desc = parse_existing_descriptions(DATA_DOC_PATH)
    content = build_data_doc(entries, existing_desc)

    is_new = not DATA_DOC_PATH.exists()
    DATA_DOC_PATH.write_text(content, encoding="utf-8")

    print(f"# oodata run\n")
    print(f"- data/  : {DATA_DIR}")
    print(f"- 문서   : {DATA_DOC_PATH}")
    print(f"- 상태   : {'생성됨' if is_new else '업데이트'} ({len(entries)}개 폴더)")
    print()
    print("## 등록된 서브폴더")
    print()
    print("| 폴더 | 상태 | 크기 |")
    print("|------|------|------|")
    for name, status, mb in entries:
        size_str = f"{mb:.1f} MB" if status == "존재" and mb > 0 else "-"
        print(f"| {name}/ | {status} | {size_str} |")


def _update_detail_comment(lines: list, target: str, merged_comment: str) -> bool:
    """상세 섹션 '### target/' 블록에 '- 코멘트:' 라인 갱신/삽입."""
    heading = f"### {target}/"
    for i, line in enumerate(lines):
        if line.strip() != heading:
            continue
        # 블록 범위 (다음 ### 또는 ## 헤딩까지)
        block_end = len(lines)
        for j in range(i + 1, len(lines)):
            if lines[j].startswith("### ") or lines[j].startswith("## "):
                block_end = j
                break
        # 기존 코멘트 라인 갱신
        for k in range(i + 1, block_end):
            if lines[k].lstrip().startswith("- 코멘트:"):
                lines[k] = f"- 코멘트: {merged_comment}"
                return True
        # 없으면 '- 상태:' 다음에 삽입
        for k in range(i + 1, block_end):
            if lines[k].lstrip().startswith("- 상태:"):
                lines.insert(k + 1, f"- 코멘트: {merged_comment}")
                return True
        # 상태 라인도 없으면 heading 바로 아래 빈 줄 다음에 삽입
        lines.insert(i + 2, f"- 코멘트: {merged_comment}")
        return True
    return False


def cmd_comment(folder_name: str, memo: str):
    if not DATA_DOC_PATH.exists():
        print(f"[ERROR] 문서 없음: {DATA_DOC_PATH}")
        print("먼저 `oodata run` 을 실행하세요.")
        return

    target = folder_name.rstrip("/").strip()
    lines = DATA_DOC_PATH.read_text(encoding="utf-8").splitlines()
    updated = False
    merged_comment = memo

    # 1) 서브폴더 목록 테이블 셀 갱신
    for i, line in enumerate(lines):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        if cells[0] in ("폴더", "") or set(cells[0]) <= set("-: "):
            continue
        cell_name = cells[0].rstrip("/").strip()
        if cell_name == target:
            merged_comment = f"{cells[2]} | {memo}" if cells[2] else memo
            cells[2] = merged_comment
            lines[i] = "| " + " | ".join(cells) + " |"
            updated = True
            break

    # 2) 상세 섹션 코멘트 라인 갱신/삽입
    detail_updated = _update_detail_comment(lines, target, merged_comment) if updated else False

    if updated:
        DATA_DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"[OK] '{target}' 설명 업데이트")
        print(f"  메모   : {memo}")
        print(f"  반영   : 테이블 셀{' + 상세 섹션' if detail_updated else ''}")
        print(f"  문서   : {DATA_DOC_PATH}")
    else:
        print(f"[WARN] '{target}' 폴더를 문서에서 찾을 수 없음")
        print(f"  문서: {DATA_DOC_PATH}")


def cmd_status():
    print(f"[{SKILL_NAME} status]  버전: {VERSION}")
    print(f"  DATA_DIR     : {DATA_DIR}  ({'존재' if DATA_DIR.exists() else '없음'})")
    print(f"  기본 백업 경로: {DEFAULT_BACKUP_PATH}")
    folders = list_data_folders()
    markers = list_backup_markers()
    print(f"  실제 폴더    : {len(folders)}개")
    print(f"  백업 마커    : {len(markers)}개")


def cmd_version():
    print(f"[{SKILL_NAME}] 버전: {VERSION}")


# ============================================================
# 진입점
# ============================================================

def cmd_show_checklist():
    """references/checklist.md 내용 출력"""
    checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[{SKILL_NAME}] checklist.md 없음: {checklist_path}")
        return
    print(checklist_path.read_text(encoding="utf-8"))


def main():
    args = sys.argv[1:]
    if show_help_if_no_args(SKILL_NAME, args):
        return
    cmd = args[0].lower()
    if cmd == "comment":
        if len(args) < 3:
            print('[ERROR] 사용법: oodata comment <폴더명> "<메모>"')
            return
        cmd_comment(args[1], args[2])
        return
    dispatch = {
        "version": cmd_version,
        "status":  cmd_status,
        "list":    cmd_list,
        "run":     cmd_run,
        "backup":  cmd_backup,
        "restore": cmd_restore,
    }
    fn = dispatch.get(cmd)
    if fn:
        fn()
    else:
        if cmd in ("show",) and len(args) > 1 and args[1].lower() == "checklist":
            cmd_show_checklist()
            return
        print(f"[WARN] 알 수 없는 명령어: {cmd}")
        _print_skill_help(SKILL_NAME)


if __name__ == "__main__":
    main()
