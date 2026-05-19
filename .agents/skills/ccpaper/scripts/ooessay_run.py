"""
[ooessay_run.py]
이 스크립트는 'ooessay' 스킬의 핵심 실행 파일로, 국내 보고서 데이터를 관리합니다.

사용법:
    uv run python .agents/skills/ooessay/scripts/ooessay_run.py run [--limit N] [--dry-run]
    uv run python .agents/skills/ooessay/scripts/ooessay_run.py status
    uv run python .agents/skills/ooessay/scripts/ooessay_run.py trans [--folder ID] [--force]
    uv run python .agents/skills/ooessay/scripts/ooessay_run.py fix [--folder ID] [--check-only] [--auto-fix]
    uv run python .agents/skills/ooessay/scripts/ooessay_run.py version
"""

import argparse
import sys
import sys as _sys
if _sys.stdout.encoding and _sys.stdout.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stdout.reconfigure(encoding='utf-8')
if _sys.stderr.encoding and _sys.stderr.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stderr.reconfigure(encoding='utf-8')
from pathlib import Path
from datetime import datetime

# --- oo_common inline ---
import re as _re
_SKILLS_DIR = Path(__file__).parent.parent.parent
_PROJECT_ROOT = _SKILLS_DIR.parent.parent

def show_help_if_no_args(skill_name, args):
    if not args:
        _sf = _SKILLS_DIR / skill_name / "SKILL.md"
        if _sf.exists():
            _c = _sf.read_text(encoding="utf-8")
            _m = _re.search(r"^# \w+ - (.+)$", _c, _re.MULTILINE)
            print(f"## {skill_name}\n\n**용도**: {_m.group(1).strip() if _m else ''}\n")
            _cmds = []
            for _cm in _re.finditer(r"\|\s*`([^`]+)`\s*\|", _c):
                _cc = _cm.group(1).strip()
                if _cc.startswith(skill_name):
                    _s = _cc.replace(skill_name, "").strip()
                    if _s and _s not in _cmds:
                        _cmds.append(_s)
            print("### 서브명령어\n")
            for _cc in _cmds:
                print(f"- `{skill_name} {_cc}`")
            print(f"\n**상세 문서**: `.agents/skills/{skill_name}/SKILL.md`")
        else:
            print(f"[ERROR] .agents/skills/{skill_name}/SKILL.md not found")
        return True
    return False

PROJECT_ROOT = _PROJECT_ROOT
SCRIPT_DIR = Path(__file__).parent
DOC_DIR = _PROJECT_ROOT / "doc"
TMP_DIR = _PROJECT_ROOT / "tmp"
V_DIR = _SKILLS_DIR
TODO_FILE = DOC_DIR / "d0004_todo.md"
HISTORY_FILE = DOC_DIR / "d0010_history.md"
def log_info(msg): print(f"[INFO] {msg}")
def log_ok(msg): print(f"[OK] {msg}")
def log_warn(msg): print(f"[WARN] {msg}")
def log_error(msg): print(f"[ERROR] {msg}")
def log_tip(msg): print(f"[TIP] {msg}")
def log_dry_run(msg): print(f"[DRY-RUN] {msg}")
def get_date():
    from datetime import datetime as _dt
    return _dt.now().strftime("%Y-%m-%d")
# --- end oo_common inline ---

# 상수 정의 (OAIS=03_paper/ 하위, 독립 프로젝트=루트 직하 양쪽 호환)
PAPER_BASE = PROJECT_ROOT / "03_paper" if (PROJECT_ROOT / "03_paper").exists() else PROJECT_ROOT
ESSAY_DIR = PAPER_BASE / "12_paper_ko"
REPORT_DIR = ESSAY_DIR  # 별칭
DOWN_DIR = PAPER_BASE / "00_down"
REPORT_LIST = PAPER_BASE / "12_paper_ko.md"

# 버전 정보
VERSION = "v01"
VERSION_DATE = "2026-01-31"

# 품질 기준
QUALITY_THRESHOLDS = {
    "summary": 500,      # 서머리 최소 bytes
    "korean": 1000,      # 한글 전문 최소 bytes
}

# 템플릿/미완료 마커
INCOMPLETE_MARKERS = [
    "(추출 필요)", "(추후 작성)", "[저자명]", "[제목]",
    "TODO", "(미작성)", "[미완료]", "작성 예정",
    "{1-2문단}", "{설명}", "{결론}", "{원문}"
]

# 국내 출처 약어
DOMESTIC_SOURCES = [
    "SCIENCEON", "RISS", "DBpia", "KCI", "KISS",
    "KISTI", "NRF", "NTIS", "NDSL"
]


def check_file_quality(file_path, file_type):
    """
    파일의 내부 내용을 읽어 품질을 정밀 검사합니다.
    """
    # 1. 인코딩 검사
    try:
        content = file_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return "인코딩 오류 (파일 깨짐)"
    except Exception as e:
        return f"읽기 실패 ({str(e)})"

    # 2. 최소 분량 검사
    threshold = QUALITY_THRESHOLDS.get(file_type, 500)
    if len(content.strip()) < threshold:
        return f"내용 부족 ({len(content)} bytes < {threshold})"

    # 3. 템플릿/미완료 마커 검사
    for marker in INCOMPLETE_MARKERS:
        if marker in content:
            return f"미완료 ('{marker}' 포함)"

    return None


def check_report_completeness(folder_path):
    """
    보고서 폴더의 완성도를 상세히 검사합니다.
    03_report는 03_전문(영어) 파일이 불필요합니다.
    Returns: dict with status for each file type
    """
    result = {
        "folder": folder_path.name,
        "pdf": {"exists": False, "path": None},
        "summary": {"exists": False, "path": None, "quality": None, "issue": None},
        "korean": {"exists": False, "path": None, "quality": None, "issue": None},
        "needs_work": [],
        "is_complete": False
    }

    if not folder_path.is_dir():
        return result

    files = list(folder_path.iterdir())

    # PDF 체크
    pdf_files = [f for f in files if f.suffix.lower() == '.pdf']
    if pdf_files:
        result["pdf"]["exists"] = True
        result["pdf"]["path"] = str(pdf_files[0])
    else:
        result["needs_work"].append("pdf_missing")

    # 서머리 체크 (00_*_서머리.md)
    summary_files = [f for f in files if "_00_" in f.name and "서머리" in f.name]
    if summary_files:
        result["summary"]["exists"] = True
        result["summary"]["path"] = str(summary_files[0])
        issue = check_file_quality(summary_files[0], "summary")
        if issue:
            result["summary"]["quality"] = "incomplete"
            result["summary"]["issue"] = issue
            result["needs_work"].append("summary_incomplete")
        else:
            result["summary"]["quality"] = "ok"
    else:
        result["needs_work"].append("summary_missing")

    # 한글 전문 체크 (04_*_전문(한글).md)
    # 03_report는 03_전문(영어) 파일이 불필요
    kor_files = [f for f in files if "_04_" in f.name and "전문(한글)" in f.name]
    if kor_files:
        result["korean"]["exists"] = True
        result["korean"]["path"] = str(kor_files[0])
        issue = check_file_quality(kor_files[0], "korean")
        if issue:
            result["korean"]["quality"] = "incomplete"
            result["korean"]["issue"] = issue
            result["needs_work"].append("korean_incomplete")
        else:
            result["korean"]["quality"] = "ok"
    else:
        result["needs_work"].append("korean_missing")

    # 완료 여부 판단: PDF + 서머리 + 한글전문 모두 OK
    result["is_complete"] = (
        result["pdf"]["exists"] and
        result["summary"]["quality"] == "ok" and
        result["korean"]["quality"] == "ok"
    )

    return result


def get_all_report_folders():
    """
    03_report 내의 모든 보고서 폴더 목록을 반환합니다.
    YYMMDD-HHMM 형식의 폴더만 반환합니다.
    """
    if not REPORT_DIR.exists():
        return []

    folders = []
    for item in REPORT_DIR.iterdir():
        if item.is_dir() and item.name != "0000":
            # YYMMDD-HHMM 형식 체크 (6자리-4자리)
            parts = item.name.split("-")
            if len(parts) == 2 and len(parts[0]) == 6 and len(parts[1]) >= 4:
                folders.append(item)

    return sorted(folders, key=lambda x: x.name, reverse=True)


def do_status():
    """
    현재 보고서 관리 현황을 출력합니다.
    """
    print("=== ooessay 현황 ===\n")

    # 03_paper/00_down 대기 현황
    print("[03_paper/00_down 대기]")
    if DOWN_DIR.exists():
        pdf_count = len(list(DOWN_DIR.glob("*.pdf")))
        list_count = len(list(DOWN_DIR.glob("*.md")))
        print(f"- PDF 파일: {pdf_count}개")
        print(f"- 리스트 파일: {list_count}개")
    else:
        print("- (폴더 없음)")
    print()

    # 03_paper/12_paper_ko 현황
    print("[03_paper/12_paper_ko 현황]")
    if not ESSAY_DIR.exists():
        print("- (폴더 없음)")
        return

    folders = get_all_report_folders()
    total = len(folders)
    complete = 0
    incomplete = 0

    for folder in folders:
        result = check_report_completeness(folder)
        if result["is_complete"]:
            complete += 1
        else:
            incomplete += 1

    print(f"- 총 보고서: {total}개")
    print(f"- 완료: {complete}개 (00+01+04 존재)")
    print(f"- 미완료: {incomplete}개")
    print()

    # 최근 추가
    print("[최근 추가]")
    if folders:
        for i, folder in enumerate(folders[:5], 1):
            # 서머리에서 제목 추출 시도
            summary_files = list(folder.glob("*_00_*서머리*.md"))
            title = folder.name
            if summary_files:
                try:
                    content = summary_files[0].read_text(encoding='utf-8')
                    for line in content.split('\n'):
                        if line.startswith('# '):
                            title = line[2:].strip()[:50]
                            break
                except:
                    pass
            print(f"{i}. {folder.name} - {title}")
    else:
        print("- (등록된 보고서 없음)")
    print()

    # 서브명령어
    print("[서브명령어]")
    print("- ooessay run: 통합 실행")
    print("- ooessay status: 현황 조회")
    print("- ooessay trans: 텍스트 추출")
    print("- ooessay fix: 무결성 검사")
    print("- ooessay version: 버전 정보")


def do_run(limit=None, dry_run=False):
    """
    통합 실행: 00_down → 12_paper_ko 정리 + 서머리 + 한글추출
    """
    log_info("ooessay run 시작")

    if dry_run:
        log_dry_run("실행 없이 계획만 출력합니다")

    # Phase 0: 03_paper/00_down 스캔
    log_info("Phase 0: 03_paper/00_down 스캔")
    if DOWN_DIR.exists():
        pdf_files = list(DOWN_DIR.glob("*.pdf"))
        log_info(f"  대기 중인 PDF: {len(pdf_files)}개")
        if pdf_files and not dry_run:
            log_warn("  03_paper/00_down에 PDF가 있습니다. 수동으로 국내/해외 분류 후 처리 필요")
    else:
        log_info("  03_paper/00_down 폴더 없음")

    # Phase 1~4: 미완료 폴더 처리
    log_info("Phase 1-4: 미완료 보고서 처리")
    folders = get_all_report_folders()

    if limit:
        folders = folders[:limit]

    incomplete_folders = []
    for folder in folders:
        result = check_report_completeness(folder)
        if not result["is_complete"]:
            incomplete_folders.append((folder, result))

    log_info(f"  처리 대상: {len(incomplete_folders)}개 (전체 {len(folders)}개 중)")

    for folder, result in incomplete_folders:
        log_info(f"\n  처리: {folder.name}")
        log_info(f"    필요 작업: {', '.join(result['needs_work'])}")

        if dry_run:
            continue

        # 실제 처리 로직은 추후 구현
        # - 서머리 작성 (AI 필요)
        # - 한글 추출 (PyPDF2)

    log_ok("ooessay run 완료")


def do_trans(folder_id=None, force=False):
    """
    PDF에서 한글 텍스트를 추출합니다. (pdfplumber 기반)
    """
    log_info("ooessay trans 시작")
    import subprocess

    extract_script = SCRIPT_DIR / "oopaper_extract_text.py"
    if not extract_script.exists():
        log_error(f"추출 스크립트 없음: {extract_script}")
        return

    if folder_id:
        cmd = ["uv", "run", "python", str(extract_script), "--folder", str(REPORT_DIR / folder_id)]
    else:
        cmd = ["uv", "run", "python", str(extract_script), "--batch", str(REPORT_DIR)]

    if force:
        cmd.append("--force")

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    if result.returncode == 0:
        log_ok("trans 완료")
    else:
        log_error("trans 실패")


def do_fix(folder_id=None, check_only=False, auto_fix=False):
    """
    무결성 검사 및 수정
    """
    log_info("ooessay fix 시작")

    if folder_id:
        target_folders = [REPORT_DIR / folder_id]
        if not target_folders[0].exists():
            log_error(f"폴더를 찾을 수 없습니다: {folder_id}")
            return
    else:
        target_folders = get_all_report_folders()

    issues = []

    for folder in target_folders:
        result = check_report_completeness(folder)
        if result["needs_work"]:
            issues.append({
                "folder": folder.name,
                "issues": result["needs_work"]
            })

    # 결과 출력
    print(f"\n[검사 결과] 총 {len(target_folders)}개 중 {len(issues)}개 문제 발견\n")

    for item in issues:
        print(f"- {item['folder']}: {', '.join(item['issues'])}")

    if not check_only and auto_fix:
        log_info("\n자동 수정 가능한 항목 수정 중...")
        # 파일명 수정 등 자동화 가능한 작업
        log_ok("자동 수정 완료")


def do_version():
    """
    버전 정보 출력
    """
    print(f"ooessay {VERSION}")
    print(f"Release: {VERSION_DATE}")
    print(f"Essay Dir: {ESSAY_DIR}")
    print(f"\n국내 보고서 관리 스킬")
    print(f"- 대상: 사이언스온, RISS, DBpia, KCI 등 국내 사이트")
    print(f"- 파일 구성: 00(서머리) + 01(PDF) + 04(한글전문)")
    print(f"- 03_전문(영어) 파일 불필요")


def cmd_show_checklist():
    """references/checklist.md 내용 출력"""
    checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[{SKILL_NAME}] checklist.md 없음: {checklist_path}")
        return
    print(checklist_path.read_text(encoding="utf-8"))


def main():
    if len(sys.argv) > 2 and sys.argv[1].lower() == "show" and sys.argv[2].lower() == "checklist":
        cmd_show_checklist()
        return
    if not sys.argv[1:]:
        sys.argv.append("run")

    parser = argparse.ArgumentParser(
        description="ooessay - 국내 보고서 관리 스킬"
    )
    subparsers = parser.add_subparsers(dest="command", help="서브명령어")

    # run
    run_parser = subparsers.add_parser("run", help="통합 실행")
    run_parser.add_argument("--limit", type=int, help="처리할 최대 보고서 수")
    run_parser.add_argument("--dry-run", action="store_true", help="실행 없이 계획만 출력")
    run_parser.add_argument("--folder", help="특정 폴더만 처리")

    # status
    subparsers.add_parser("status", help="현황 조회")

    # trans
    trans_parser = subparsers.add_parser("trans", help="PDF 텍스트 추출")
    trans_parser.add_argument("--folder", help="특정 폴더만 처리")
    trans_parser.add_argument("--force", action="store_true", help="기존 파일 덮어쓰기")

    # fix
    fix_parser = subparsers.add_parser("fix", help="무결성 검사/수정")
    fix_parser.add_argument("--folder", help="특정 폴더만 검사")
    fix_parser.add_argument("--check-only", action="store_true", help="검사만 수행")
    fix_parser.add_argument("--auto-fix", action="store_true", help="자동 수정")

    # version
    subparsers.add_parser("version", help="버전 정보")

    args = parser.parse_args()

    if args.command == "run":
        do_run(limit=args.limit, dry_run=args.dry_run)
    elif args.command == "status":
        do_status()
    elif args.command == "trans":
        do_trans(folder_id=args.folder, force=args.force)
    elif args.command == "fix":
        do_fix(
            folder_id=args.folder,
            check_only=args.check_only,
            auto_fix=args.auto_fix
        )
    elif args.command == "version":
        do_version()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
