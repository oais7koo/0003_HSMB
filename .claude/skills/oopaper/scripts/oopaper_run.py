"""
[oopaper_run.py]
이 스크립트는 'oopaper' 스킬의 핵심 실행 파일로, 논문 데이터의 정합성을 검사하고 관리합니다.

사용법:
    uv run python .claude/skills/oopaper/scripts/oopaper_run.py run [--limit N] [--dry-run] [--skip-organize]
    uv run python .claude/skills/oopaper/scripts/oopaper_run.py status
    uv run python .claude/skills/oopaper/scripts/oopaper_run.py sync-list [--dry-run]
    uv run python .claude/skills/oopaper/scripts/oopaper_run.py fix [--folder ID]
    uv run python .claude/skills/oopaper/scripts/oopaper_run.py delete-broken [--dry-run]
    uv run python .claude/skills/oopaper/scripts/oopaper_run.py download [--dry-run] [--file FILE] [--force]
"""

import argparse
import os
import sys
import json
import re as _re
import time
from pathlib import Path
from datetime import datetime

# PDF 백업 폴백 지원 (OAIS: 03_paper/ 하위, 독립 프로젝트: 루트 직하)
_root = Path(__file__).resolve().parent.parent.parent.parent.parent
_paper_base_for_import = _root / "03_paper" if (_root / "03_paper").exists() else _root
sys.path.insert(0, str(_paper_base_for_import))
try:
    from pdf_resolver import resolve_pdf, find_pdfs_in_folder
except ModuleNotFoundError:
    # pdf_resolver는 paper 데이터 폴더에 위치. 데이터 없으면 disabled.
    def resolve_pdf(p): return p if p.exists() else None
    def find_pdfs_in_folder(folder): return list(folder.glob("*.pdf")) if folder.exists() else []

# --- oo_common inline ---
import re as _re
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

# 공용 template_loader import
_SCRIPT_DIR = Path(__file__).resolve().parent
_SKILL_DIR = _SCRIPT_DIR.parent
_SKILLS_ROOT = _SKILL_DIR.parent  # .claude/skills/
if str(_SKILLS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SKILLS_ROOT))
try:
    from _shared.template_loader import load_template_block as _load_template_block
except ImportError:
    _load_template_block = lambda p, name="template": ""  # noqa: E731


def _load_template(filename: str, block_name: str = "template") -> str:
    """스킬 내 templates/ 파일에서 블록 로드."""
    return _load_template_block(_SKILL_DIR / "templates" / filename, block_name)


# 상수 정의 - 경로 (v39: OAIS=03_paper/ 하위, 독립 프로젝트=루트 직하 양쪽 호환)
# scripts/ → oopaper/ → skills/ → .claude/ → PROJECT_ROOT
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
PAPER_BASE = PROJECT_ROOT / "03_paper" if (PROJECT_ROOT / "03_paper").exists() else PROJECT_ROOT
PAPER_DIR = PAPER_BASE / "11_paper_en"
DOWN_DIR = PAPER_BASE / "00_down"
SURVEY_DIR = PAPER_BASE / "15_paper_survey"
PAPER_LIST_FILE = PAPER_DIR / "paper_list.md"

# 품질 기준
QUALITY_THRESHOLDS = {
    "summary": 500,      # 서머리 최소 bytes
    "english": 1000,     # 영문 전문 최소 bytes
    "korean": 1000,      # 한글 전문 최소 bytes
}

# 템플릿/미완료 마커
INCOMPLETE_MARKERS = [
    "(추출 필요)", "(추후 작성)", "[저자명]", "[제목]",
    "# 번역 필요", "[Translation Required]", "내용 자동 생성됨",
    "TODO", "(미작성)", "[미완료]", "작성 예정"
]


def check_file_quality(file_path, file_type):
    """파일의 내부 내용을 읽어 품질을 정밀 검사합니다."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return "인코딩 오류 (파일 깨짐)"
    except Exception as e:
        return f"읽기 실패 ({str(e)})"

    threshold = QUALITY_THRESHOLDS.get(file_type, 500)
    if len(content.strip()) < threshold:
        return f"내용 부족 ({len(content)} bytes < {threshold})"

    for marker in INCOMPLETE_MARKERS:
        if marker in content:
            return f"미완료 ('{marker}' 포함)"

    return None


def find_best_file(file_list, file_type):
    """여러 파일 중 가장 품질이 좋은 파일을 선택합니다."""
    if not file_list:
        return None, [], None

    if len(file_list) == 1:
        issue = check_file_quality(file_list[0], file_type)
        return file_list[0], [], issue

    quality_results = []
    for f in file_list:
        issue = check_file_quality(f, file_type)
        size = f.stat().st_size
        quality_results.append({
            "file": f, "issue": issue, "size": size, "is_ok": issue is None
        })

    quality_results.sort(key=lambda x: (not x["is_ok"], -x["size"]))
    best = quality_results[0]
    duplicates = [r["file"] for r in quality_results[1:]]
    return best["file"], duplicates, best["issue"]


def determine_status(result):
    """4단계 상태 판정 (C4): X/S/T/O"""
    has_summary = result["summary"]["exists"] and result["summary"]["quality"] == "ok"
    has_english = result["english"]["exists"] and result["english"]["quality"] == "ok"
    has_korean = result["korean"]["exists"] and result["korean"]["quality"] == "ok"

    # 참고문헌 연결 여부 확인
    has_refs_linked = False
    if has_summary and result["summary"]["path"]:
        try:
            content = Path(result["summary"]["path"]).read_text(encoding='utf-8')
            # 내부 보유 링크가 있는지 확인 (C1 형식: [YYMMDD-HHMM])
            if _re.search(r'###\s*내부 보유', content) or _re.search(r'\[\d{6}-\d{4}\]', content):
                has_refs_linked = True
            # 또는 참고문헌 섹션이 충분히 있으면 (모든 섹션 중 가장 큰 것 확인, 번호 포함 헤더 지원)
            for ref_match in _re.finditer(r'^##\s*(?:\d+\.\s*)?(참고\s*논문|참고문헌|References)', content, _re.MULTILINE | _re.IGNORECASE):
                ref_content = content[ref_match.end():]
                next_section = _re.search(r'^##\s+', ref_content, _re.MULTILINE)
                ref_text = ref_content[:next_section.start()] if next_section else ref_content
                if len(ref_text.strip()) > 100:
                    has_refs_linked = True
                    break
        except Exception:
            pass

    if has_summary and has_english and has_korean and has_refs_linked:
        return "O"
    elif has_summary and has_english and has_korean:
        return "T"
    elif has_summary:
        return "S"
    else:
        return "X"


def check_paper_completeness(folder_path):
    """논문 폴더의 완성도를 상세히 검사합니다."""
    result = {
        "folder": folder_path.name,
        "pdf": {"exists": False, "path": None},
        "summary": {"exists": False, "path": None, "quality": None, "issue": None},
        "english": {"exists": False, "path": None, "quality": None, "issue": None},
        "korean": {"exists": False, "path": None, "quality": None, "issue": None},
        "duplicates": [],
        "needs_work": [],
        "status": "X"  # 4단계 상태
    }

    if not folder_path.is_dir():
        return result

    files = list(folder_path.iterdir())

    # PDF 체크 (원본 → 백업 폴백)
    pdf_files = [f for f in files if f.suffix.lower() == '.pdf']
    if not pdf_files:
        pdf_files = find_pdfs_in_folder(folder_path)
    if pdf_files:
        result["pdf"]["exists"] = True
        result["pdf"]["path"] = str(pdf_files[0])
    else:
        result["needs_work"].append("pdf_missing")

    # 서머리 체크
    summary_files = [f for f in files if "_00_" in f.name and "서머리" in f.name]
    if summary_files:
        best_file, duplicates, issue = find_best_file(summary_files, "summary")
        result["summary"]["exists"] = True
        result["summary"]["path"] = str(best_file)
        result["duplicates"].extend([str(d) for d in duplicates])
        if duplicates:
            result["needs_work"].append("summary_duplicates")
        if issue:
            result["summary"]["quality"] = "incomplete"
            result["summary"]["issue"] = issue
            result["needs_work"].append("summary_incomplete")
        else:
            result["summary"]["quality"] = "ok"
    else:
        result["needs_work"].append("summary_missing")

    # 영문 전문 체크
    eng_files = [f for f in files if "_03_" in f.name and "전문(영어)" in f.name]
    if eng_files:
        best_file, duplicates, issue = find_best_file(eng_files, "english")
        result["english"]["exists"] = True
        result["english"]["path"] = str(best_file)
        result["duplicates"].extend([str(d) for d in duplicates])
        if duplicates:
            result["needs_work"].append("english_duplicates")
        if issue:
            result["english"]["quality"] = "incomplete"
            result["english"]["issue"] = issue
            result["needs_work"].append("english_incomplete")
        else:
            result["english"]["quality"] = "ok"
    else:
        result["needs_work"].append("english_missing")

    # 한글 전문 체크
    kor_files = [f for f in files if "_04_" in f.name and "전문(한글)" in f.name]
    if kor_files:
        best_file, duplicates, issue = find_best_file(kor_files, "korean")
        result["korean"]["exists"] = True
        result["korean"]["path"] = str(best_file)
        result["duplicates"].extend([str(d) for d in duplicates])
        if duplicates:
            result["needs_work"].append("korean_duplicates")
        if issue:
            result["korean"]["quality"] = "incomplete"
            result["korean"]["issue"] = issue
            result["needs_work"].append("korean_incomplete")
        else:
            result["korean"]["quality"] = "ok"
    else:
        result["needs_work"].append("korean_missing")

    # 4단계 상태 판정
    result["status"] = determine_status(result)

    return result


def do_run(args):
    """전체 논문 자동 정리 - Phase 0~1 실행 + Phase 2~6 작업 목록 출력."""
    sys.stdout.reconfigure(encoding='utf-8')
    print("# oopaper run - 완전 자동 파이프라인\n", flush=True)
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print(f"PRD: doc/d30001_prd.md | TODO: doc/d30004_todo.md\n", flush=True)

    # Phase 0: 00_down 처리
    if not getattr(args, 'skip_organize', False):
        if DOWN_DIR.exists():
            pdf_files = list(DOWN_DIR.glob("*.pdf"))
            if pdf_files:
                print(f"## Phase 0: 00_down 정리\n", flush=True)
                print(f"03_paper/00_down에서 {len(pdf_files)}개 PDF 발견\n", flush=True)
                for pdf in pdf_files:
                    print(f"- `{pdf.name}`", flush=True)
                print("\n**→ Claude가 각 PDF를 YYMMDD-HHMM 폴더로 이동 필요**\n", flush=True)
                print("---\n", flush=True)

    if not PAPER_DIR.exists():
        print(f"Error: Paper directory not found at {PAPER_DIR}", flush=True)
        return

    # Phase 1: 스캔
    target_folders = sorted([d for d in PAPER_DIR.iterdir()
                             if d.is_dir() and d.name != "paper_list.md"])
    total = len(target_folders)

    print(f"## Phase 1: 스캔\n", flush=True)
    print(f"총 {total}개 논문 폴더 검사 중...\n", flush=True)

    all_results = []
    status_counts = {"X": 0, "S": 0, "T": 0, "O": 0}
    needs_summary = []
    needs_english = []
    needs_korean = []
    needs_refs = []
    all_duplicates = []

    for folder in target_folders:
        result = check_paper_completeness(folder)
        all_results.append(result)

        status_counts[result["status"]] += 1

        if result["duplicates"]:
            all_duplicates.extend(result["duplicates"])

        work_items = result["needs_work"]
        if "summary_missing" in work_items or "summary_incomplete" in work_items:
            needs_summary.append(result["folder"])
        if "english_missing" in work_items or "english_incomplete" in work_items:
            needs_english.append(result["folder"])
        if "korean_missing" in work_items or "korean_incomplete" in work_items:
            needs_korean.append(result["folder"])
        if result["status"] == "T":  # 번역 완료지만 참고문헌 미연결
            needs_refs.append(result["folder"])

    # 4단계 상태 통계
    print("### 4단계 상태 (C4)\n", flush=True)
    print(f"| 상태 | 설명 | 건수 | 비율 |", flush=True)
    print(f"|:----:|------|:----:|:----:|", flush=True)
    print(f"| X | 미처리 | {status_counts['X']} | {status_counts['X']*100//max(total,1)}% |", flush=True)
    print(f"| S | 서머리 완료 | {status_counts['S']} | {status_counts['S']*100//max(total,1)}% |", flush=True)
    print(f"| T | 번역 완료 | {status_counts['T']} | {status_counts['T']*100//max(total,1)}% |", flush=True)
    print(f"| O | 완료 | {status_counts['O']} | {status_counts['O']*100//max(total,1)}% |", flush=True)
    print(f"| **합계** | | **{total}** | 100% |", flush=True)
    print("", flush=True)

    # 작업 필요 통계
    print("### 작업 필요 항목\n", flush=True)
    print(f"| 작업 | 건수 | PRD 참조 |", flush=True)
    print(f"|------|:----:|---------|", flush=True)
    print(f"| 서머리 생성 | {len(needs_summary)} | F3010, F3012 |", flush=True)
    print(f"| 영문 추출 | {len(needs_english)} | F3010 |", flush=True)
    print(f"| 한글 번역 | {len(needs_korean)} | F3011 |", flush=True)
    print(f"| 참고문헌 매칭 | {len(needs_refs)} | F3013, F3020, C1 |", flush=True)
    if all_duplicates:
        print(f"| 중복 파일 정리 | {len(all_duplicates)} | - |", flush=True)
    print("", flush=True)

    # 중복 파일 자동 삭제
    if all_duplicates and not args.dry_run:
        print("### 중복 파일 자동 삭제\n", flush=True)
        deleted = 0
        for dup_path in all_duplicates:
            try:
                Path(dup_path).unlink()
                deleted += 1
            except Exception:
                pass
        print(f"{deleted}개 중복 파일 삭제 완료\n", flush=True)

    # limit 적용
    limit = args.limit if args.limit else 999999

    # Phase 2~5 작업 목록
    tasks = []
    task_count = 0

    if needs_summary:
        print("## Phase 2: 서머리 생성 필요 (F3010 + F3012)\n", flush=True)
        for folder_id in needs_summary[:limit]:
            if task_count >= limit:
                break
            result = next(r for r in all_results if r["folder"] == folder_id)
            issue = result["summary"].get("issue", "파일 없음")
            print(f"- [ ] `{folder_id}`: {issue}", flush=True)
            tasks.append({"folder": folder_id, "type": "summary", "phase": 2})
            task_count += 1
        print("", flush=True)

    if needs_english and task_count < limit:
        print("## Phase 3: 영문 추출 필요 (F3010)\n", flush=True)
        for folder_id in needs_english[:limit - task_count]:
            if task_count >= limit:
                break
            result = next(r for r in all_results if r["folder"] == folder_id)
            issue = result["english"].get("issue", "파일 없음")
            print(f"- [ ] `{folder_id}`: {issue}", flush=True)
            tasks.append({"folder": folder_id, "type": "english", "phase": 3})
            task_count += 1
        print("", flush=True)

    if needs_korean and task_count < limit:
        print("## Phase 4: 한글 번역 필요 (F3011)\n", flush=True)
        for folder_id in needs_korean[:limit - task_count]:
            if task_count >= limit:
                break
            print(f"- [ ] `{folder_id}`", flush=True)
            tasks.append({"folder": folder_id, "type": "korean", "phase": 4})
            task_count += 1
        print("", flush=True)

    if needs_refs:
        print("## Phase 5: 참고문헌 매칭 필요 (F3013, F3020, C1)\n", flush=True)
        for folder_id in needs_refs:
            print(f"- [ ] `{folder_id}`: 내부 보유 논문 매칭 필요", flush=True)
            tasks.append({"folder": folder_id, "type": "refs", "phase": 5})
        print("", flush=True)

    # JSON 작업 목록 저장
    output_file = PROJECT_ROOT / "tmp" / "oopaper_tasks.json"
    output_file.parent.mkdir(exist_ok=True)
    output_file.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding='utf-8')

    # 요약
    print(f"## 요약\n", flush=True)
    print(f"- 전체 논문: {total}개", flush=True)
    print(f"- 완료(O): {status_counts['O']}개 ({status_counts['O']*100//max(total,1)}%)", flush=True)
    print(f"- 처리 대상: {len(tasks)}건", flush=True)
    print(f"- 작업 목록: `tmp/oopaper_tasks.json`\n", flush=True)

    if not args.dry_run and tasks:
        print("## 실행 지침\n", flush=True)
        print("Claude가 위 목록의 각 논문을 순차 처리합니다:", flush=True)
        print("1. PDF 읽기 → 서머리 + 키워드 추출 (Phase 2)", flush=True)
        print("2. PDF 읽기 → 영문 전문 추출 (Phase 3)", flush=True)
        print("3. 영문 → 한글 번역 [translator 에이전트] (Phase 4)", flush=True)
        print("4. 참고문헌 추출 → paper_list.md 대조 → 내부/외부 링크 (Phase 5)", flush=True)
        print("5. `oopaper_run.py sync-list` 실행 (Phase 6)", flush=True)
        print("", flush=True)


def do_sync_list(args):
    """paper_list.md를 실제 폴더 상태와 동기화합니다 (Phase 6)."""
    import re
    sys.stdout.reconfigure(encoding='utf-8')
    print("# oopaper sync-list - paper_list.md 동기화\n", flush=True)
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", flush=True)

    if not PAPER_DIR.exists():
        print(f"Error: Paper directory not found at {PAPER_DIR}", flush=True)
        return

    # 1. 현재 paper_list.md 파싱
    existing_entries = {}
    if PAPER_LIST_FILE.exists():
        content = PAPER_LIST_FILE.read_text(encoding='utf-8')
        # 각 ### YYMMDD-HHMM 항목 파싱
        for match in re.finditer(r'###\s+(\d{6}-\d{4})\s*-\s*(.+?)(?=\n###|\Z)', content, re.DOTALL):
            folder_id = match.group(1)
            existing_entries[folder_id] = match.group(0)

    # 2. 실제 폴더 스캔
    actual_folders = sorted([d.name for d in PAPER_DIR.iterdir()
                             if d.is_dir() and re.match(r'\d{6}-\d{4}', d.name)])

    # 3. 비교
    in_list_only = set(existing_entries.keys()) - set(actual_folders)
    in_folder_only = set(actual_folders) - set(existing_entries.keys())
    in_both = set(actual_folders) & set(existing_entries.keys())

    print(f"## 동기화 현황\n", flush=True)
    print(f"| 항목 | 건수 |", flush=True)
    print(f"|------|:----:|", flush=True)
    print(f"| paper_list.md 항목 | {len(existing_entries)} |", flush=True)
    print(f"| 실제 폴더 | {len(actual_folders)} |", flush=True)
    print(f"| 양쪽 존재 | {len(in_both)} |", flush=True)
    print(f"| 폴더만 존재 (추가 필요) | {len(in_folder_only)} |", flush=True)
    print(f"| 리스트만 존재 (폴더 없음) | {len(in_list_only)} |", flush=True)
    print("", flush=True)

    # 4. 상태 갱신
    status_updates = []
    for folder_id in in_both:
        folder_path = PAPER_DIR / folder_id
        result = check_paper_completeness(folder_path)
        new_status = result["status"]

        # 기존 항목에서 상태 추출
        entry_text = existing_entries[folder_id]
        old_status_match = re.search(r'\*\*완료\*\*:\s*([XSTO])', entry_text)
        old_status = old_status_match.group(1) if old_status_match else "X"

        if old_status != new_status:
            status_updates.append((folder_id, old_status, new_status))

    if status_updates:
        print("## 상태 변경\n", flush=True)
        print("| 폴더 | 이전 | 이후 |", flush=True)
        print("|------|:----:|:----:|", flush=True)
        for folder_id, old, new in status_updates:
            print(f"| `{folder_id}` | {old} | {new} |", flush=True)
        print("", flush=True)

    if in_folder_only:
        print("## 추가 필요 (폴더는 있지만 paper_list.md에 없음)\n", flush=True)
        for folder_id in sorted(in_folder_only):
            print(f"- `{folder_id}`", flush=True)
        print("", flush=True)

    if in_list_only:
        print("## 경고: 폴더 없음 (paper_list.md에만 존재)\n", flush=True)
        for folder_id in sorted(in_list_only):
            print(f"- `{folder_id}`", flush=True)
        print("", flush=True)

    # 5. 실제 업데이트 (dry-run 아닐 때)
    if not args.dry_run and (status_updates or in_folder_only):
        print("## 업데이트 실행\n", flush=True)

        if PAPER_LIST_FILE.exists():
            content = PAPER_LIST_FILE.read_text(encoding='utf-8')
        else:
            content = "# 논문 목록 (paper_list.md)\n\n"

        # 상태 업데이트
        for folder_id, old_status, new_status in status_updates:
            # 완료: O/X/S/T 패턴 치환
            content = re.sub(
                rf'(###\s+{re.escape(folder_id)}.+?\*\*완료\*\*:\s*){old_status}',
                rf'\g<1>{new_status}',
                content,
                flags=re.DOTALL
            )
            print(f"- 상태 갱신: `{folder_id}` {old_status} → {new_status}", flush=True)

        # 새 항목 추가
        for folder_id in sorted(in_folder_only):
            folder_path = PAPER_DIR / folder_id
            result = check_paper_completeness(folder_path)
            status = result["status"]

            # 서머리에서 제목 추출 시도
            title = "제목 미확인"
            if result["summary"]["path"]:
                try:
                    summary_content = Path(result["summary"]["path"]).read_text(encoding='utf-8')
                    title_match = re.search(r'^#\s+(.+)$', summary_content, re.MULTILINE)
                    if title_match:
                        title = title_match.group(1).strip()
                except Exception:
                    pass

            new_entry = f"\n### {folder_id} - {title}\n"
            new_entry += f"- **키워드**: (미추출)\n"
            new_entry += f"- **저자**: 미확인 | **연도**: 미확인 | **출처**: 미확인\n"
            new_entry += f"- **등록일**: {datetime.now().strftime('%Y-%m-%d')} | **완료**: {status}\n"

            content += new_entry
            print(f"- 신규 추가: `{folder_id}` (상태: {status})", flush=True)

        PAPER_LIST_FILE.write_text(content, encoding='utf-8')
        print(f"\npaper_list.md 업데이트 완료", flush=True)
    elif args.dry_run:
        print("**[Dry Run]** 실제 업데이트하지 않음\n", flush=True)
    else:
        print("업데이트할 항목 없음\n", flush=True)


def do_status(args):
    """전체 논문 폴더의 상태 통계를 출력합니다."""
    sys.stdout.reconfigure(encoding='utf-8')
    print("# oopaper status\n", flush=True)

    # 00_down 상태
    down_pdfs = list(DOWN_DIR.glob("*.pdf")) if DOWN_DIR.exists() else []
    if down_pdfs:
        print(f"## 03_paper/00_down 대기: {len(down_pdfs)}개 PDF\n", flush=True)
        for pdf in down_pdfs[:5]:
            print(f"  - {pdf.name}", flush=True)
        if len(down_pdfs) > 5:
            print(f"  - ... 외 {len(down_pdfs) - 5}개", flush=True)
        print("", flush=True)

    if not PAPER_DIR.exists():
        print(f"Error: Paper directory not found at {PAPER_DIR}", flush=True)
        return

    target_folders = [d for d in PAPER_DIR.iterdir()
                      if d.is_dir() and _re.match(r'\d{6}-\d{4}', d.name)]
    total = len(target_folders)

    status_counts = {"X": 0, "S": 0, "T": 0, "O": 0}

    for folder in target_folders:
        result = check_paper_completeness(folder)
        status_counts[result["status"]] += 1

    # 템플릿 기반 출력
    _tpl_status = _load_template("oopaper_status.md", "template")
    if _tpl_status:
        print(_tpl_status.format(
            total=total,
            x_count=status_counts['X'], x_pct=status_counts['X']*100//max(total,1),
            s_count=status_counts['S'], s_pct=status_counts['S']*100//max(total,1),
            t_count=status_counts['T'], t_pct=status_counts['T']*100//max(total,1),
            o_count=status_counts['O'], o_pct=status_counts['O']*100//max(total,1),
        ), flush=True)
        print("", flush=True)
    else:
        # fallback (템플릿 파일 없을 때)
        print(f"## 논문 현황: {total}개\n", flush=True)
        print("| 상태 | 설명 | 건수 | 비율 |", flush=True)
        print("|:----:|------|:----:|:----:|", flush=True)
        for key, label in [("X", "미처리"), ("S", "서머리 완료"), ("T", "번역 완료"), ("O", "완료")]:
            print(f"| {key} | {label} | {status_counts[key]} | {status_counts[key]*100//max(total,1)}% |", flush=True)
        print(f"| **합계** | | **{total}** | 100% |\n", flush=True)

    # 서베이 현황
    if SURVEY_DIR.exists():
        surveys = list(SURVEY_DIR.glob("*.md"))
        print(f"## 서베이: {len(surveys)}개 (03_paper/15_paper_survey/)\n", flush=True)
        for s in surveys:
            print(f"  - {s.name}", flush=True)
        print("", flush=True)

    # 명령어 안내 (템플릿)
    _tpl_cmds = _load_template("oopaper_status.md", "commands_footer")
    if _tpl_cmds:
        print(_tpl_cmds, flush=True)
        print("", flush=True)
    else:
        print("## 명령어\n", flush=True)
        for line in [
            "  run              : 완전 자동 파이프라인 (7 Phase)",
            "  status           : 현황 표시 (이 화면)",
            "  sync-list        : paper_list.md 동기화",
            "  fix              : 무결성 체크",
            "  delete-broken    : 깨진 파일 삭제",
            "  download         : 리스트 기반 PDF 자동 다운로드",
            "  clean-duplicates : 중복 파일 정리",
            "  ref-update       : 서머리에 참고문헌 추가",
        ]:
            print(line, flush=True)
        print("", flush=True)


def check_folder(folder_path):
    """개별 논문 폴더를 검사하고 발견된 오류 리스트를 반환합니다."""
    errors = []
    if not folder_path.is_dir():
        return []
    files = list(folder_path.iterdir())

    summary_files = [f for f in files if "_00_" in f.name and "서머리" in f.name]
    if not summary_files: errors.append("00_서머리 파일 누락")

    pdf_files = [f for f in files if f.suffix.lower() == '.pdf']
    if not pdf_files:
        pdf_files = find_pdfs_in_folder(folder_path)
    if not pdf_files: errors.append("01_PDF 파일 누락")

    eng_files = [f for f in files if "_03_" in f.name and "전문(영어)" in f.name]
    if not eng_files: errors.append("03_전문(영어) 파일 누락")
    else:
        quality_msg = check_file_quality(eng_files[0], 'english')
        if quality_msg: errors.append(f"03_전문(영어) 품질 미달: {quality_msg}")

    kor_files = [f for f in files if "_04_" in f.name and "전문(한글)" in f.name]
    if not kor_files: errors.append("04_전문(한글) 파일 누락")
    else:
        quality_msg = check_file_quality(kor_files[0], 'korean')
        if quality_msg: errors.append(f"04_전문(한글) 품질 미달: {quality_msg}")

    return errors


def do_fix(args):
    sys.stdout.reconfigure(encoding='utf-8')
    print(f"Running oopaper fix...", flush=True)

    if args.folder:
        target_folders = [PAPER_DIR / args.folder]
    else:
        target_folders = [d for d in PAPER_DIR.iterdir() if d.is_dir()]

    error_data = {}
    total_folders = len(target_folders)

    for folder in sorted(target_folders):
        errors = check_folder(folder)
        if errors:
            error_data[folder.name] = errors

    report_lines = []
    report_lines.append(f"Check Result: {len(error_data)} errors found in {total_folders} folders.")
    for name, errs in error_data.items():
        for err in errs:
            report_lines.append(f"{name}: {err}")

    report_text = "\n".join(report_lines)
    print(report_text, flush=True)
    fix_report_path = PROJECT_ROOT / "tmp" / "fix_report.txt"
    fix_report_path.parent.mkdir(exist_ok=True)
    fix_report_path.write_text(report_text, encoding='utf-8')


def do_delete_broken(args):
    sys.stdout.reconfigure(encoding='utf-8')
    print("Running delete-broken...", flush=True)
    target_folders = [d for d in PAPER_DIR.iterdir() if d.is_dir()]

    deleted_files = []
    for folder in target_folders:
        kor_files = [f for f in folder.iterdir() if "_04_" in f.name and "전문(한글)" in f.name]
        for kf in kor_files:
            is_broken = False
            try:
                content = kf.read_text(encoding='utf-8')
                if "\ufffd" in content and content.count("\ufffd") > 10:
                    is_broken = True
            except UnicodeDecodeError:
                is_broken = True

            if is_broken:
                if not args.dry_run:
                    kf.unlink()
                    deleted_files.append(kf.name)
                else:
                    deleted_files.append(f"{kf.name} (DryRun)")

    log_text = f"Deleted {len(deleted_files)} files.\n" + "\n".join(deleted_files)
    print(log_text, flush=True)
    broken_log_path = PROJECT_ROOT / "tmp" / "broken_files_log.txt"
    broken_log_path.parent.mkdir(exist_ok=True)
    broken_log_path.write_text(log_text, encoding='utf-8')


def do_clean_duplicates(args):
    """중복 파일만 검사하고 정리합니다."""
    sys.stdout.reconfigure(encoding='utf-8')
    print("# oopaper clean-duplicates\n", flush=True)

    if not PAPER_DIR.exists():
        print(f"Error: Paper directory not found at {PAPER_DIR}", flush=True)
        return

    target_folders = sorted([d for d in PAPER_DIR.iterdir() if d.is_dir()])
    all_duplicates = []

    for folder in target_folders:
        result = check_paper_completeness(folder)
        if result["duplicates"]:
            for dup in result["duplicates"]:
                all_duplicates.append({"folder": result["folder"], "file": dup, "name": Path(dup).name})

    print(f"중복 파일: {len(all_duplicates)}개\n", flush=True)

    if not all_duplicates:
        return

    for dup in all_duplicates:
        print(f"- `{dup['folder']}` / `{dup['name']}`", flush=True)
    print("", flush=True)

    if not args.dry_run:
        deleted = 0
        for dup in all_duplicates:
            try:
                Path(dup["file"]).unlink()
                deleted += 1
            except Exception:
                pass
        print(f"{deleted}개 삭제 완료", flush=True)
    else:
        print("**[Dry Run]** 실제 삭제 안 함", flush=True)


def do_ref_update(args):
    """서머리 파일에 참고문헌을 추가합니다."""
    import re
    sys.stdout.reconfigure(encoding='utf-8')
    print("Running oopaper ref-update...", flush=True)

    if args.folder:
        target_folders = [d for d in PAPER_DIR.iterdir() if d.is_dir() and d.name == args.folder]
    else:
        target_folders = [d for d in PAPER_DIR.iterdir() if d.is_dir()]

    print(f"Processing {len(target_folders)} folders...", flush=True)

    updated = 0
    skipped = 0
    failed = 0

    for folder in target_folders:
        summary_files = list(folder.glob("*_00_*서머리.md"))
        eng_files = list(folder.glob("*_03_*전문(영어).md"))

        if not summary_files:
            failed += 1
            continue
        if not eng_files:
            failed += 1
            continue

        summary_file = summary_files[0]
        eng_file = eng_files[0]

        try:
            summary_content = summary_file.read_text(encoding='utf-8')
        except Exception:
            failed += 1
            continue

        if re.search(r'^##\s*(References?|참고\s*문헌|참고문헌|참고\s*논문)', summary_content, re.MULTILINE | re.IGNORECASE):
            match = re.search(r'^##\s*(References?|참고\s*문헌|참고문헌|참고\s*논문)', summary_content, re.MULTILINE | re.IGNORECASE)
            start = match.end()
            end_match = re.search(r'^##\s+', summary_content[start:], re.MULTILINE)
            content = summary_content[start:start+end_match.start()] if end_match else summary_content[start:]
            if len(content.strip()) > 50:
                skipped += 1
                continue

        try:
            eng_content = eng_file.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            failed += 1
            continue

        match = re.search(r'^##\s*(References?|Bibliography|참고\s*문헌|참고문헌)', eng_content, re.MULTILINE | re.IGNORECASE)
        refs = None
        if match:
            refs = eng_content[match.end():].strip()
        else:
            # Title case / uppercase without markdown header
            match_tc = re.search(r'\n(REFERENCES|References|BIBLIOGRAPHY)\s*\n', eng_content)
            if match_tc:
                refs = eng_content[match_tc.end():].strip()

        if not refs or len(refs) < 50:
            failed += 1
            print(f"- [FAILED] {folder.name}: Extraction failed", flush=True)
            continue

        keyword_match = re.search(r'^##\s*키워드', summary_content, re.MULTILINE)
        new_section = f"\n\n## 참고문헌\n{refs}\n"

        if keyword_match:
            insert_pos = keyword_match.start()
            new_content = summary_content[:insert_pos] + new_section + "\n" + summary_content[insert_pos:]
        else:
            new_content = summary_content + new_section

        if not args.dry_run:
            summary_file.write_text(new_content, encoding='utf-8')
            updated += 1
            print(f"- [UPDATED] {folder.name}", flush=True)
        else:
            updated += 1
            print(f"- [UPDATED] {folder.name} (Dry Run)", flush=True)

    print("-" * 30, flush=True)
    print(f"Total: {len(target_folders)}, Updated: {updated}, Skipped: {skipped}, Failed: {failed}", flush=True)


def _sanitize_filename(title, max_len=80):
    """제목에서 파일명으로 사용할 수 없는 문자를 제거합니다."""
    sanitized = _re.sub(r'[^a-zA-Z0-9가-힣\s_\-]', '', title)
    sanitized = _re.sub(r'\s+', '_', sanitized.strip())
    if len(sanitized) > max_len:
        sanitized = sanitized[:max_len]
    return sanitized


def _parse_download_list(file_path):
    """다운로드 리스트 마크다운 파일에서 항목을 파싱합니다."""
    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    items = []

    for line_no, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith('|'):
            continue
        cells = [c.strip() for c in stripped.split('|')]
        # 앞뒤 빈 셀 제거 (| 로 시작/끝)
        cells = [c for c in cells if c != '']
        if len(cells) < 3:
            continue
        # 헤더/구분선 스킵
        if all(set(c) <= {'-', ':', ' '} for c in cells):
            continue
        if cells[0] == '#':
            continue

        # URL 컬럼 찾기
        url = None
        url_idx = -1
        for i, cell in enumerate(cells):
            if 'https://' in cell or 'http://' in cell:
                url = cell.strip()
                url_idx = i
                break
        if not url:
            continue

        # 상태 컬럼: 마지막 셀에서 [ ] 또는 [x] 확인
        last_cell = cells[-1]
        if '[ ]' in last_cell:
            done = False
        elif '[x]' in last_cell.lower():
            done = True
        else:
            continue

        # 제목 컬럼: URL 직전 컬럼 또는 인덱스 1 (# 다음)
        title_idx = 1 if len(cells) > 2 else 0
        title = cells[title_idx].strip()

        items.append({
            'title': title,
            'url': url,
            'done': done,
            'line_no': line_no,
        })

    return items


def extract_keywords_from_summary(summary_path):
    """서머리 파일에서 키워드를 추출합니다. (2가지 형식 지원)"""
    try:
        content = Path(summary_path).read_text(encoding='utf-8')
    except Exception:
        return []

    keywords = []

    # 형식 1: ## 키워드 섹션 (- keyword 항목)
    kw_match = _re.search(r'^##\s*키워드', content, _re.MULTILINE)
    if kw_match:
        kw_start = kw_match.end()
        next_section = _re.search(r'^##\s+', content[kw_start:], _re.MULTILINE)
        kw_text = content[kw_start:kw_start + next_section.start()] if next_section else content[kw_start:]
        for line in kw_text.strip().split('\n'):
            line = line.strip()
            if line.startswith('-'):
                kw = line.lstrip('- ').strip()
                # "(한글)" 부분 제거하여 간결한 키워드만 추출
                kw_clean = _re.sub(r'\s*\([^)]*\)\s*$', '', kw).strip()
                if kw_clean:
                    keywords.append(kw_clean)

    # 형식 2: 파일 상단 #keyword 태그 (형식 1이 없을 때만)
    if not keywords:
        for line in content.split('\n')[:5]:
            tags = _re.findall(r'#([^\s#]+)', line)
            for tag in tags:
                if tag not in ('paper',) and not _re.match(r'^\d+_paper$', tag):
                    keywords.append(tag)

    return keywords


def do_keyword_sync(args):
    """서머리에서 키워드를 추출하여 paper_list.md에 반영합니다 (F3012, C3)."""
    import re
    sys.stdout.reconfigure(encoding='utf-8')
    print("# oopaper keyword-sync - 키워드 자동 추출 및 동기화\n", flush=True)
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", flush=True)

    if not PAPER_DIR.exists():
        print(f"Error: Paper directory not found at {PAPER_DIR}", flush=True)
        return

    if not PAPER_LIST_FILE.exists():
        print(f"Error: paper_list.md not found at {PAPER_LIST_FILE}", flush=True)
        return

    content = PAPER_LIST_FILE.read_text(encoding='utf-8')

    # 폴더 스캔
    target_folders = sorted([d for d in PAPER_DIR.iterdir()
                             if d.is_dir() and re.match(r'\d{6}-\d{4}', d.name)])

    updated = 0
    skipped = 0
    no_keywords = 0

    print("| 폴더 | 상태 | 키워드 |", flush=True)
    print("|------|------|--------|", flush=True)

    for folder in target_folders:
        folder_id = folder.name
        # paper_list.md에서 해당 항목의 키워드 확인
        pattern = rf'(###\s+{re.escape(folder_id)}\s+-\s+.+?\n-\s+\*\*키워드\*\*:\s*)(.+?)(\n)'
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            continue

        current_kw = match.group(2).strip()

        # 이미 키워드가 있으면 스킵 (단, "-" 또는 "(미추출)"이면 업데이트)
        if current_kw and current_kw not in ('-', '(미추출)'):
            skipped += 1
            continue

        # 서머리에서 키워드 추출
        summary_files = list(folder.glob("*_00_*서머리.md"))
        if not summary_files:
            no_keywords += 1
            continue

        keywords = extract_keywords_from_summary(summary_files[0])
        if not keywords:
            no_keywords += 1
            print(f"| `{folder_id}` | 키워드 없음 | - |", flush=True)
            continue

        kw_str = ', '.join(keywords[:8])  # 최대 8개
        new_text = match.group(1) + kw_str + match.group(3)
        content = content[:match.start()] + new_text + content[match.end():]
        updated += 1
        print(f"| `{folder_id}` | 업데이트 | {kw_str[:60]} |", flush=True)

    print("", flush=True)
    print(f"## 결과\n", flush=True)
    print(f"| 항목 | 건수 |", flush=True)
    print(f"|------|:----:|", flush=True)
    print(f"| 업데이트 | {updated} |", flush=True)
    print(f"| 스킵 (이미 있음) | {skipped} |", flush=True)
    print(f"| 키워드 없음 | {no_keywords} |", flush=True)
    print("", flush=True)

    if updated > 0 and not args.dry_run:
        PAPER_LIST_FILE.write_text(content, encoding='utf-8')
        print(f"paper_list.md 업데이트 완료 ({updated}건)", flush=True)
    elif args.dry_run:
        print("**[Dry Run]** 실제 업데이트하지 않음", flush=True)
    else:
        print("업데이트할 항목 없음", flush=True)


def _build_paper_index(paper_dir):
    """paper_list.md와 서머리에서 논문 제목/저자 인덱스를 구축합니다."""
    import re
    index = {}  # folder_id -> {"title": ..., "authors": ...}

    # 1. paper_list.md에서 파싱
    paper_list_file = paper_dir / "paper_list.md"
    if paper_list_file.exists():
        content = paper_list_file.read_text(encoding='utf-8')
        for match in re.finditer(r'###\s+(\d{6}-\d{4})\s+-\s+(.+?)(?=\n)', content):
            folder_id = match.group(1)
            title = match.group(2).strip()
            index[folder_id] = {"title": title, "authors": ""}

    # 2. 서머리에서 보완 (제목이 미확인인 경우)
    for folder in paper_dir.iterdir():
        if not folder.is_dir() or not re.match(r'\d{6}-\d{4}', folder.name):
            continue
        folder_id = folder.name
        if folder_id in index and index[folder_id]["title"] != "제목 미확인":
            continue
        summary_files = list(folder.glob("*_00_*서머리.md"))
        if summary_files:
            try:
                sc = summary_files[0].read_text(encoding='utf-8')
                title_match = re.search(r'^#\s+(.+)$', sc, re.MULTILINE)
                if title_match:
                    index.setdefault(folder_id, {})["title"] = title_match.group(1).strip()
            except Exception:
                pass

    return index


def _match_reference(ref_text, paper_index):
    """참고문헌 한 줄을 내부 보유 논문과 매칭합니다."""
    ref_lower = ref_text.lower()
    best_match = None
    best_score = 0

    for folder_id, info in paper_index.items():
        title = info.get("title", "")
        if not title or title == "제목 미확인":
            continue
        # 제목 단어 매칭 (3단어 이상 일치하면 매칭)
        title_words = set(w.lower() for w in _re.findall(r'[a-zA-Z]{3,}', title))
        if len(title_words) < 2:
            continue
        matched = sum(1 for w in title_words if w in ref_lower)
        score = matched / len(title_words) if title_words else 0
        if score > best_score and score >= 0.6:
            best_score = score
            best_match = folder_id

    return best_match, best_score


def do_ref_match(args):
    """서머리 참고문헌에서 내부 보유 논문을 매칭하여 링크를 생성합니다 (F3020, C1)."""
    import re
    sys.stdout.reconfigure(encoding='utf-8')
    print("# oopaper ref-match - 참고문헌 내부 논문 매칭\n", flush=True)
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", flush=True)

    if not PAPER_DIR.exists():
        print(f"Error: Paper directory not found at {PAPER_DIR}", flush=True)
        return

    # 1. 논문 인덱스 구축
    paper_index = _build_paper_index(PAPER_DIR)
    print(f"논문 인덱스: {len(paper_index)}편\n", flush=True)

    # 2. 대상 폴더 결정
    if args.folder:
        target_folders = [PAPER_DIR / args.folder]
    else:
        target_folders = sorted([d for d in PAPER_DIR.iterdir()
                                 if d.is_dir() and re.match(r'\d{6}-\d{4}', d.name)])

    updated = 0
    skipped = 0
    total_matches = 0

    for folder in target_folders:
        folder_id = folder.name
        summary_files = list(folder.glob("*_00_*서머리.md"))
        if not summary_files:
            continue

        summary_file = summary_files[0]
        try:
            content = summary_file.read_text(encoding='utf-8')
        except Exception:
            continue

        # 참고문헌 섹션 찾기
        ref_match = re.search(
            r'^##\s*(참고문헌|참고\s*논문\s*\(References\)|References)',
            content, re.MULTILINE | re.IGNORECASE)
        if not ref_match:
            continue

        ref_start = ref_match.end()
        next_section = re.search(r'^##\s+', content[ref_start:], re.MULTILINE)
        ref_text = content[ref_start:ref_start + next_section.start()] if next_section else content[ref_start:]

        # 이미 내부 매칭이 완료된 경우 스킵
        if '### 내부 보유' in ref_text:
            skipped += 1
            continue

        # 참고문헌 각 줄에서 매칭
        lines = ref_text.strip().split('\n')
        internal_refs = []
        external_refs = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            match_result, score = _match_reference(line, paper_index)
            if match_result and match_result != folder_id:
                title = paper_index[match_result]["title"]
                internal_refs.append(f"- [{match_result}] {title}")
                total_matches += 1
            elif line.startswith('-') or line.startswith('[') or re.match(r'^\d+\.?\s', line):
                external_refs.append(line if line.startswith('-') else f"- {line}")

        if not internal_refs:
            continue

        # 새 참고문헌 섹션 생성 (C1 형식)
        new_ref_section = f"\n## 참고 논문 (References)\n\n### 내부 보유\n"
        new_ref_section += '\n'.join(internal_refs) + '\n'
        if external_refs:
            new_ref_section += f"\n### 외부\n"
            new_ref_section += '\n'.join(external_refs[:20]) + '\n'  # 외부는 최대 20개
        new_ref_section += '\n'

        # 기존 참고문헌 섹션 교체
        if next_section:
            new_content = content[:ref_match.start()] + new_ref_section + content[ref_start + next_section.start():]
        else:
            new_content = content[:ref_match.start()] + new_ref_section

        if not args.dry_run:
            summary_file.write_text(new_content, encoding='utf-8')
        updated += 1
        print(f"- [{folder_id}] 내부 매칭 {len(internal_refs)}건", flush=True)

    print(f"\n## 결과\n", flush=True)
    print(f"| 항목 | 건수 |", flush=True)
    print(f"|------|:----:|", flush=True)
    print(f"| 업데이트 | {updated} |", flush=True)
    print(f"| 스킵 (이미 매칭) | {skipped} |", flush=True)
    print(f"| 내부 매칭 발견 | {total_matches} |", flush=True)

    if args.dry_run:
        print(f"\n**[Dry Run]** 실제 업데이트하지 않음", flush=True)


def do_quality(args):
    """논문 품질 자동 스코어링. PDF/서머리/전문/참고문헌 상태를 일괄 점검."""
    sys.stdout.reconfigure(encoding='utf-8')
    print("# oopaper quality - 논문 분석 품질 리포트\n", flush=True)
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", flush=True)

    if not PAPER_DIR.exists():
        print(f"Error: 논문 디렉토리 없음: {PAPER_DIR}", flush=True)
        return

    folders = sorted([d for d in PAPER_DIR.iterdir() if d.is_dir()])
    if not folders:
        print("논문 폴더 없음", flush=True)
        return

    print(f"스캔 대상: {len(folders)}개 폴더\n", flush=True)

    # 품질 항목별 집계
    issues = {
        "pdf_missing": [],       # PDF 없음
        "pdf_small": [],         # PDF < 100KB (abstract 페이지 의심)
        "pdf_not_pdf": [],       # PDF 시그니처 없음
        "summary_missing": [],   # 서머리 없음
        "summary_short": [],     # 서머리 너무 짧음
        "summary_incomplete": [],# 서머리 미완료 마커
        "ref_placeholder": [],   # 참고문헌 "[나중에 추가]"
        "english_missing": [],   # 영문 전문 없음
        "korean_missing": [],    # 한글 번역 없음
    }

    grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    status_counts = {"X": 0, "S": 0, "T": 0, "O": 0}
    detail_rows = []

    for folder in folders:
        folder_id = folder.name
        score = 100
        folder_issues = []

        # 1. PDF 검사
        pdfs = list(folder.glob("*_01_*.pdf")) + list(folder.glob("*.pdf"))
        if not pdfs:
            issues["pdf_missing"].append(folder_id)
            score -= 30
            folder_issues.append("PDF없음")
        else:
            pdf = pdfs[0]
            pdf_size = pdf.stat().st_size
            if pdf_size < 100 * 1024:
                issues["pdf_small"].append(f"{folder_id} ({pdf_size//1024}KB)")
                score -= 20
                folder_issues.append(f"PDF소형({pdf_size//1024}KB)")
            # PDF 시그니처 확인
            try:
                with open(pdf, 'rb') as f:
                    if f.read(5) != b'%PDF-':
                        issues["pdf_not_pdf"].append(folder_id)
                        score -= 25
                        folder_issues.append("PDF아님(HTML?)")
            except Exception:
                pass

        # 2. 서머리 검사
        summaries = list(folder.glob("*_00_*서머리*.md"))
        if not summaries:
            issues["summary_missing"].append(folder_id)
            score -= 25
            folder_issues.append("서머리없음")
        else:
            sm = summaries[0]
            try:
                content = sm.read_text(encoding='utf-8')
                if len(content) < 500:
                    issues["summary_short"].append(f"{folder_id} ({len(content)}B)")
                    score -= 15
                    folder_issues.append("서머리짧음")
                # 미완료 마커
                for marker in INCOMPLETE_MARKERS:
                    if marker in content:
                        issues["summary_incomplete"].append(f"{folder_id} ({marker})")
                        score -= 10
                        folder_issues.append("미완료마커")
                        break
                # 참고문헌 플레이스홀더
                if "[나중에 추가]" in content or "나중에 추가" in content:
                    issues["ref_placeholder"].append(folder_id)
                    score -= 5
                    folder_issues.append("참고문헌미등록")
            except Exception:
                pass

        # 3. 영문 전문
        eng = list(folder.glob("*_03_*전문*영어*.md"))
        if not eng:
            issues["english_missing"].append(folder_id)
            score -= 10

        # 4. 한글 번역
        kor = list(folder.glob("*_04_*전문*한글*.md"))
        if not kor:
            issues["korean_missing"].append(folder_id)
            score -= 5

        # 등급 산정
        score = max(0, score)
        if score >= 80:
            grade = "A"
        elif score >= 60:
            grade = "B"
        elif score >= 40:
            grade = "C"
        else:
            grade = "D"
        grade_counts[grade] += 1

        # 상태 판정
        has_s = bool(summaries) and len(content if summaries else "") >= 500
        has_e = bool(eng)
        has_k = bool(kor)
        if has_s and has_e and has_k:
            st = "T"
        elif has_s:
            st = "S"
        else:
            st = "X"
        status_counts[st] += 1

        if folder_issues and (args.verbose or grade in ("C", "D")):
            detail_rows.append((folder_id, grade, score, ", ".join(folder_issues)))

    total = len(folders)

    # 결과 출력
    print("## 등급 분포\n", flush=True)
    print("| 등급 | 기준 | 건수 | 비율 |", flush=True)
    print("|:----:|------|:----:|:----:|", flush=True)
    for g, label in [("A", "80~100"), ("B", "60~79"), ("C", "40~59"), ("D", "0~39")]:
        pct = grade_counts[g] / total * 100 if total else 0
        print(f"| {g} | {label} | {grade_counts[g]} | {pct:.1f}% |", flush=True)
    print(f"| **합계** | | **{total}** | |", flush=True)

    print("\n## 상태 분포\n", flush=True)
    print("| 상태 | 건수 | 비율 |", flush=True)
    print("|:----:|:----:|:----:|", flush=True)
    for st in ("X", "S", "T", "O"):
        pct = status_counts[st] / total * 100 if total else 0
        print(f"| {st} | {status_counts[st]} | {pct:.1f}% |", flush=True)

    print("\n## 이슈 요약\n", flush=True)
    print("| 이슈 | 건수 | 심각도 |", flush=True)
    print("|------|:----:|:------:|", flush=True)
    issue_labels = [
        ("pdf_not_pdf", "PDF 파일이 아님 (HTML 등)", "CRITICAL"),
        ("pdf_missing", "PDF 없음", "CRITICAL"),
        ("pdf_small", "PDF < 100KB (abstract 의심)", "ERROR"),
        ("summary_missing", "서머리 없음", "ERROR"),
        ("summary_short", "서머리 < 500B", "WARNING"),
        ("summary_incomplete", "미완료 마커 잔존", "WARNING"),
        ("ref_placeholder", "참고문헌 '[나중에 추가]'", "INFO"),
        ("english_missing", "영문 전문 없음", "INFO"),
        ("korean_missing", "한글 번역 없음", "INFO"),
    ]
    for key, label, severity in issue_labels:
        cnt = len(issues[key])
        if cnt > 0:
            print(f"| {label} | {cnt} | {severity} |", flush=True)

    # 상세 (C/D 등급 또는 --verbose)
    if detail_rows:
        print(f"\n## 상세 (등급 C/D)\n", flush=True)
        print("| 폴더 | 등급 | 점수 | 이슈 |", flush=True)
        print("|------|:----:|:----:|------|", flush=True)
        for fid, g, s, iss in detail_rows[:30]:
            print(f"| {fid} | {g} | {s} | {iss} |", flush=True)
        if len(detail_rows) > 30:
            print(f"| ... | | | +{len(detail_rows)-30}건 |", flush=True)

    # CRITICAL 상세
    for key in ("pdf_not_pdf", "pdf_missing"):
        items = issues[key]
        if items and len(items) <= 10:
            label = "PDF 파일이 아님" if "not" in key else "PDF 없음"
            print(f"\n### {label} ({len(items)}건)\n", flush=True)
            for item in items:
                print(f"- {item}", flush=True)

    print("", flush=True)


def _is_abstract_page(pdf_path, file_size, content_type=''):
    """다운로드된 파일이 abstract 페이지(HTML)인지 판별.
    - HTML Content-Type이면서 PDF 시그니처 없음 → abstract 페이지
    - 파일 크기 < 100KB이면서 PDF 시그니처 없음 → abstract 페이지 의심
    """
    try:
        with open(pdf_path, 'rb') as f:
            header = f.read(16)
        is_pdf_sig = header[:5] == b'%PDF-'
    except Exception:
        return False

    # HTML Content-Type + PDF 시그니처 없음 → 확실히 abstract
    if 'html' in content_type.lower() and not is_pdf_sig:
        return True
    # PDF 시그니처 없음 + 작은 파일 → 의심
    if not is_pdf_sig and file_size < 100 * 1024:
        return True
    # PDF 시그니처 있지만 매우 작음 (< 50KB) → abstract PDF 가능성
    if is_pdf_sig and file_size < 50 * 1024:
        return True
    return False


def _try_fix_pdf_url(url):
    """arXiv/OpenReview abstract URL을 PDF URL로 변환 시도."""
    import re
    # arXiv: abs → pdf
    m = re.match(r'(https?://arxiv\.org/)abs/(.+?)(?:\?.*)?$', url)
    if m:
        return f"{m.group(1)}pdf/{m.group(2)}.pdf"
    # OpenReview: forum → pdf
    m = re.match(r'(https?://openreview\.net/)forum\?id=(.+?)$', url)
    if m:
        return f"{m.group(1)}pdf?id={m.group(2)}"
    return None


def do_download(args):
    """다운로드 리스트 기반 PDF 자동 다운로드."""
    sys.stdout.reconfigure(encoding='utf-8')
    print("# oopaper download - PDF 자동 다운로드\n", flush=True)
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", flush=True)

    if not DOWN_DIR.exists():
        print(f"Error: 다운로드 디렉토리 없음: {DOWN_DIR}", flush=True)
        return

    # 리스트 파일 탐색
    if args.file:
        target_file = DOWN_DIR / args.file
        if not target_file.exists():
            print(f"Error: 파일 없음: {target_file}", flush=True)
            return
        list_files = [target_file]
    else:
        list_files = sorted(DOWN_DIR.glob("*_download_list.md"))

    if not list_files:
        print("다운로드 리스트 파일 없음 (03_paper/00_down/*_download_list.md)", flush=True)
        return

    print(f"리스트 파일: {len(list_files)}개\n", flush=True)

    total_success = 0
    total_fail = 0
    total_skip = 0

    for list_file in list_files:
        print(f"## {list_file.name}\n", flush=True)
        items = _parse_download_list(list_file)

        if not items:
            print("  파싱된 항목 없음\n", flush=True)
            continue

        # 처리 대상 필터링
        to_download = []
        for item in items:
            if item['done'] and not args.force:
                total_skip += 1
                continue
            # 이미 PDF 존재 확인
            safe_name = _sanitize_filename(item['title'])
            pdf_path = DOWN_DIR / f"{safe_name}.pdf"
            if pdf_path.exists() and not args.force:
                total_skip += 1
                continue
            to_download.append(item)

        if not to_download:
            print(f"  다운로드 대상 없음 (전체 {len(items)}건 중 {total_skip}건 스킵)\n", flush=True)
            continue

        print(f"  대상: {len(to_download)}건 (스킵: {len(items) - len(to_download)}건)\n", flush=True)

        if args.dry_run:
            for item in to_download:
                print(f"  - [DRY] {item['title']}", flush=True)
                print(f"    URL: {item['url']}", flush=True)
            print("", flush=True)
            continue

        # 실제 다운로드
        try:
            import requests
        except ImportError:
            print("Error: requests 패키지 필요 (uv pip install requests)", flush=True)
            return

        lines = list_file.read_text(encoding='utf-8').split('\n')
        updated = False

        for item in to_download:
            title = item['title']
            url = item['url']
            safe_name = _sanitize_filename(title)
            pdf_path = DOWN_DIR / f"{safe_name}.pdf"

            print(f"  다운로드: {title}", flush=True)
            print(f"    URL: {url}", flush=True)

            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (compatible; oopaper/1.0; academic research)'
                }
                resp = requests.get(url, headers=headers, timeout=60, stream=True)
                resp.raise_for_status()

                # Content-Type 확인
                content_type = resp.headers.get('Content-Type', '')
                if 'pdf' not in content_type and 'octet-stream' not in content_type:
                    # arXiv 등은 redirect 후 PDF 제공, 일단 저장 시도
                    pass

                with open(pdf_path, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)

                # PDF 검증: 크기 + abstract 페이지 감지
                file_size = pdf_path.stat().st_size
                if file_size < 1024:
                    pdf_path.unlink()
                    print(f"    [FAIL] 파일 크기 부족 (<1KB)", flush=True)
                    total_fail += 1
                elif _is_abstract_page(pdf_path, file_size, content_type):
                    pdf_path.unlink()
                    fixed_url = _try_fix_pdf_url(url)
                    if fixed_url and fixed_url != url:
                        print(f"    [WARN] abstract 페이지 감지 → PDF URL로 재시도: {fixed_url}", flush=True)
                        try:
                            resp2 = requests.get(fixed_url, headers=headers, timeout=60, stream=True)
                            resp2.raise_for_status()
                            with open(pdf_path, 'wb') as f2:
                                for chunk2 in resp2.iter_content(chunk_size=8192):
                                    f2.write(chunk2)
                            retry_size = pdf_path.stat().st_size
                            if retry_size > 50 * 1024:  # 50KB 이상이면 본문 PDF
                                size_kb = retry_size / 1024
                                print(f"    [OK] 재다운로드 성공 {size_kb:.0f} KB → {pdf_path.name}", flush=True)
                                total_success += 1
                                line = lines[item['line_no']]
                                lines[item['line_no']] = line.replace('[ ]', '[x]', 1)
                                updated = True
                                time.sleep(3)
                                continue
                            else:
                                pdf_path.unlink()
                        except Exception:
                            if pdf_path.exists():
                                pdf_path.unlink()
                    print(f"    [FAIL] abstract 페이지만 저장됨 (본문 PDF 아님, {file_size/1024:.0f}KB)", flush=True)
                    total_fail += 1
                else:
                    size_kb = file_size / 1024
                    print(f"    [OK] {size_kb:.0f} KB → {pdf_path.name}", flush=True)
                    total_success += 1
                    # 리스트 파일에서 [ ] → [x] 업데이트
                    line = lines[item['line_no']]
                    lines[item['line_no']] = line.replace('[ ]', '[x]', 1)
                    updated = True

            except Exception as e:
                print(f"    [FAIL] {e}", flush=True)
                total_fail += 1
                if pdf_path.exists():
                    pdf_path.unlink()

            # Rate limiting: 3초 딜레이
            time.sleep(3)

        if updated:
            list_file.write_text('\n'.join(lines), encoding='utf-8')
            print(f"\n  리스트 파일 업데이트 완료", flush=True)
        print("", flush=True)

    # 결과 요약
    print(f"## 요약\n", flush=True)
    print(f"| 항목 | 건수 |", flush=True)
    print(f"|------|:----:|", flush=True)
    print(f"| 성공 | {total_success} |", flush=True)
    print(f"| 실패 | {total_fail} |", flush=True)
    print(f"| 스킵 | {total_skip} |", flush=True)
    print(f"| **합계** | **{total_success + total_fail + total_skip}** |", flush=True)
    print("", flush=True)

    if total_success > 0:
        print("**→ `oopaper run` Phase 0으로 다운로드된 PDF를 논문 폴더로 정리하세요**\n", flush=True)


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

    if len(sys.argv) > 1 and sys.argv[1] in ("help", "-h"):
        _print_skill_help("oopaper")
        return

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    # run
    run_p = subparsers.add_parser('run', help="완전 자동 파이프라인 (7 Phase)")
    run_p.add_argument('--limit', type=int, help="처리할 최대 논문 수")
    run_p.add_argument('--dry-run', action='store_true', help="실행 없이 계획만 출력")
    run_p.add_argument('--folder', type=str, help="특정 폴더만 처리")
    run_p.add_argument('--skip-organize', action='store_true', help="Phase 0 건너뛰기")
    run_p.add_argument('--gemma', action='store_true',
        help="Phase 2(서머리)·Phase 4(번역) 초안을 로컬 Gemma에 위임. "
             "최종 포맷·검수는 여전히 Claude 필요. "
             "상세: .claude/guides/gemma_delegation.md")

    # status
    subparsers.add_parser('status', help="현황 표시")

    # sync-list
    sync_p = subparsers.add_parser('sync-list', help="paper_list.md 동기화")
    sync_p.add_argument('--dry-run', action='store_true', help="실행 없이 계획만 출력")

    # fix
    fix_p = subparsers.add_parser('fix', help="무결성 체크")
    fix_p.add_argument('--check-only', action='store_true')
    fix_p.add_argument('--folder', type=str)
    fix_p.add_argument('--auto-fix', action='store_true')

    # delete-broken
    del_p = subparsers.add_parser('delete-broken', help="깨진 파일 삭제")
    del_p.add_argument('--dry-run', action='store_true')

    # clean-duplicates
    dup_p = subparsers.add_parser('clean-duplicates', help="중복 파일 정리")
    dup_p.add_argument('--dry-run', action='store_true')

    # ref-update
    ref_p = subparsers.add_parser('ref-update', help="서머리에 참고문헌 추가")
    ref_p.add_argument('--folder', type=str)
    ref_p.add_argument('--dry-run', action='store_true')

    # quality
    qual_p = subparsers.add_parser('quality', help="논문 품질 자동 스코어링")
    qual_p.add_argument('--verbose', action='store_true', help="모든 이슈 상세 표시")

    # download
    dl_p = subparsers.add_parser('download', help="다운로드 리스트 기반 PDF 다운로드")
    dl_p.add_argument('--dry-run', action='store_true', help="실행 없이 목록만 출력")
    dl_p.add_argument('--file', type=str, help="특정 리스트 파일만 처리")
    dl_p.add_argument('--force', action='store_true', help="이미 다운로드된 항목도 재다운로드")

    # keyword-sync
    kw_p = subparsers.add_parser('keyword-sync', help="서머리에서 키워드 추출 → paper_list.md 반영")
    kw_p.add_argument('--dry-run', action='store_true', help="실행 없이 계획만 출력")

    # ref-match
    rm_p = subparsers.add_parser('ref-match', help="참고문헌 내부 논문 매칭 (C1)")
    rm_p.add_argument('--folder', type=str, help="특정 폴더만 처리")
    rm_p.add_argument('--dry-run', action='store_true', help="실행 없이 계획만 출력")

    # check (status의 alias)
    subparsers.add_parser('check', help="체크리스트/현황 표시 (status의 alias)")

    args = parser.parse_args()

    if args.command == 'help' or (len(sys.argv) > 1 and sys.argv[1] in ("help", "-h")):
        _print_skill_help("oopaper")
        return

    if args.command == 'run' or args.command is None:
        if args.command is None:
            args.limit = None
            args.dry_run = False
            args.folder = None
            args.skip_organize = False
            args.gemma = False
        # --gemma 플래그 → env var로 하위 phase에 전파
        if getattr(args, 'gemma', False):
            os.environ['OOPAPER_USE_GEMMA'] = '1'
            print("[INFO] Gemma 위임 활성화 (Phase 2 서머리 · Phase 4 번역 초안)")
            print("       경계: .claude/guides/gemma_delegation.md")
        do_run(args)
    elif args.command == 'status':
        do_status(args)
    elif args.command == 'check':
        do_status(args)
    elif args.command == 'sync-list':
        do_sync_list(args)
    elif args.command == 'fix':
        do_fix(args)
    elif args.command == 'delete-broken':
        do_delete_broken(args)
    elif args.command == 'clean-duplicates':
        do_clean_duplicates(args)
    elif args.command == 'ref-update':
        do_ref_update(args)
    elif args.command == 'quality':
        do_quality(args)
    elif args.command == 'download':
        do_download(args)
    elif args.command == 'keyword-sync':
        do_keyword_sync(args)
    elif args.command == 'ref-match':
        do_ref_match(args)
    else:
        print("Not implemented")

if __name__ == "__main__":
    main()
