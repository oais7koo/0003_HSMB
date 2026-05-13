"""ccwork - 범용 워크플로우 상태 관리 스크립트"""

import json
import re
import subprocess
import sys
import sys as _sys
if _sys.stdout.encoding and _sys.stdout.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stdout.reconfigure(encoding='utf-8')
if _sys.stderr.encoding and _sys.stderr.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stderr.reconfigure(encoding='utf-8')

# --- oo_common inline ---
from pathlib import Path
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
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
PROCESSES_DIR = SKILL_DIR / "references" / "processes"
HWP_TO_MD_SCRIPT = SKILL_DIR / "scripts" / "hwp_to_md.py"

# 비텍스트 문서 확장자 분류
HWP_EXTS = {".hwp", ".hwpx"}
PDF_EXTS = {".pdf"}
DOCX_EXTS = {".doc", ".docx"}
PPT_EXTS = {".ppt", ".pptx"}


def list_processes():
    """등록된 프로세스 목록 출력"""
    print("# ccwork 등록 프로세스 목록\n")
    processes = sorted(PROCESSES_DIR.glob("*.md"))
    if not processes:
        print("등록된 프로세스 없음")
        return
    print(f"| # | 프로세스 | 경로 |")
    print(f"|---|---------|------|")
    for i, p in enumerate(processes, 1):
        name = p.stem
        print(f"| {i} | {name} | {p.relative_to(SKILL_DIR)} |")
    print(f"\n총 {len(processes)}개 프로세스")


def status(process_name: str, workdir: str = "."):
    """프로세스 진행 상태 확인"""
    state_dir = Path(workdir) / ".ccwork"
    state_file = state_dir / f"{process_name}_state.json"

    print(f"# ccwork status: {process_name}\n")

    if not state_file.exists():
        print(f"상태 파일 없음: {state_file}")
        print("아직 실행되지 않은 프로세스입니다.")
        return

    with open(state_file, encoding="utf-8") as f:
        state = json.load(f)

    print(f"| 항목 | 값 |")
    print(f"|------|------|")
    print(f"| 프로세스 | {state.get('process', '-')} |")
    print(f"| 주제 | {state.get('topic', '-')} |")
    print(f"| 시작 | {state.get('started', '-')} |")
    print(f"| 현재 단계 | {state.get('current_step', '-')} |")
    print()

    steps = state.get("steps", {})
    if steps:
        print(f"| 단계 | 상태 | 출력물 |")
        print(f"|------|------|--------|")
        for step_id, step_info in sorted(steps.items()):
            st = step_info.get("status", "pending")
            outputs = step_info.get("output", [])
            out_str = ", ".join(outputs[:2]) if outputs else "-"
            icon = {"done": "완료", "running": "진행중", "pending": "대기", "failed": "실패"}.get(st, st)
            print(f"| {step_id} | {icon} | {out_str} |")


def init_state(process_name: str, topic: str, workdir: str = "."):
    """상태 파일 초기화"""
    state_dir = Path(workdir) / ".ccwork"
    state_dir.mkdir(parents=True, exist_ok=True)
    state_file = state_dir / f"{process_name}_state.json"

    state = {
        "process": process_name,
        "topic": topic,
        "started": datetime.now().isoformat(),
        "current_step": 0,
        "steps": {
            "0": {"status": "pending", "output": []},
            "1": {"status": "pending", "output": []},
            "2": {"status": "pending", "output": []},
            "3": {"status": "pending", "output": []},
            "4": {"status": "pending", "output": []},
        },
    }

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    print(f"상태 초기화 완료: {state_file}")
    return state


def update_step(process_name: str, step: int, step_status: str, output: list = None, workdir: str = "."):
    """단계 상태 업데이트"""
    state_dir = Path(workdir) / ".ccwork"
    state_file = state_dir / f"{process_name}_state.json"

    if not state_file.exists():
        print(f"상태 파일 없음: {state_file}")
        return

    with open(state_file, encoding="utf-8") as f:
        state = json.load(f)

    step_key = str(step)
    if step_key in state["steps"]:
        state["steps"][step_key]["status"] = step_status
        if output:
            state["steps"][step_key]["output"] = output
        if step_status == "running":
            state["current_step"] = step

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    print(f"step {step} → {step_status}")


def _resolve_output_path(input_path: Path, output_arg: str | None) -> Path:
    """출력 경로 결정: 명시된 경우 그대로, 없으면 ccwork 넘버링 규칙 적용.

    규칙:
      - 원본 파일명에 앞자리 숫자 접두사(NN_)가 있으면 +1 적용
      - 접두사 없으면 폴더 내 최대 번호 +1 할당
      - 확장자는 .md 고정, 나머지 파일명은 원본 유지
    """
    if output_arg:
        return Path(output_arg)

    parent = input_path.parent
    stem = input_path.stem  # 확장자 제외 파일명

    # 기존 번호 접두사 파싱 (예: 10_기술사업계획서 → 10, 기술사업계획서)
    m = re.match(r"^(\d+)_(.+)$", stem)
    if m:
        new_num = int(m.group(1)) + 1
        base_name = m.group(2)
    else:
        # 폴더 내 기존 파일 중 최대 번호 탐색
        existing_nums = []
        for f in parent.iterdir():
            nm = re.match(r"^(\d+)_", f.stem)
            if nm:
                existing_nums.append(int(nm.group(1)))
        new_num = (max(existing_nums) + 1) if existing_nums else 1
        base_name = stem

    return parent / f"{new_num:02d}_{base_name}.md"


def extract(input_path_str: str, output_path_str: str | None = None) -> None:
    """비텍스트 문서를 마크다운으로 변환한다.

    지원 형식:
      - HWP/HWPX: hwp_to_md.py 호출
      - PDF: 안내 메시지 출력 (pdfplumber 직접 작성 필요)
      - DOC/DOCX: 안내 메시지 출력 (python-docx 직접 작성 필요)
      - PPT/PPTX: 안내 메시지 출력
    """
    input_path = Path(input_path_str)

    if not input_path.exists():
        print(f"오류: 파일을 찾을 수 없습니다 → {input_path}")
        sys.exit(1)

    ext = input_path.suffix.lower()
    output_path = _resolve_output_path(input_path, output_path_str)

    print(f"# ccwork extract\n")
    print(f"| 항목 | 값 |")
    print(f"|------|------|")
    print(f"| 입력 | {input_path} |")
    print(f"| 출력 | {output_path} |")
    print(f"| 형식 | {ext} |")
    print()

    if ext in HWP_EXTS:
        # hwp_to_md.py 위임
        if not HWP_TO_MD_SCRIPT.exists():
            print(f"오류: hwp_to_md.py 를 찾을 수 없습니다 → {HWP_TO_MD_SCRIPT}")
            sys.exit(1)
        cmd = ["uv", "run", "python", str(HWP_TO_MD_SCRIPT), str(input_path), str(output_path)]
        print(f"실행: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=False)
        if result.returncode != 0:
            print(f"오류: hwp_to_md.py 실행 실패 (exit {result.returncode})")
            sys.exit(result.returncode)
        print(f"\n완료: {output_path}")

    elif ext in PDF_EXTS:
        print("PDF 추출 안내:")
        print("  pdfplumber 또는 Claude Read 도구를 사용하여 직접 추출하세요.")
        print()
        print("  예시 (pdfplumber):")
        print("    import pdfplumber")
        print(f"    with pdfplumber.open('{input_path}') as pdf:")
        print("        text = '\\n'.join(p.extract_text() or '' for p in pdf.pages)")
        print(f"    Path('{output_path}').write_text(text, encoding='utf-8')")
        print()
        print("  또는 Claude Read 도구로 PDF를 직접 읽은 뒤 마크다운으로 저장하세요.")

    elif ext in DOCX_EXTS:
        print("DOCX 추출 안내:")
        print("  python-docx 를 사용하여 직접 추출하세요.")
        print()
        print("  예시 (python-docx):")
        print("    from docx import Document")
        print(f"    doc = Document('{input_path}')")
        print("    text = '\\n'.join(p.text for p in doc.paragraphs)")
        print(f"    Path('{output_path}').write_text(text, encoding='utf-8')")

    elif ext in PPT_EXTS:
        print("PPT/PPTX 추출 안내:")
        print("  PDF로 변환 후 PDF 추출 파이프라인을 적용하세요.")
        print("  LibreOffice 변환 예시:")
        print(f"    libreoffice --headless --convert-to pdf '{input_path}'")
        print("  이후 ccwork extract <변환된.pdf> 를 실행하세요.")

    else:
        print(f"오류: 지원하지 않는 파일 형식입니다 → {ext}")
        print("지원 형식: .hwp .hwpx .pdf .doc .docx .ppt .pptx")
        sys.exit(1)


def cmd_show_checklist():
    """references/checklist.md 내용 출력"""
    checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[{SKILL_NAME}] checklist.md 없음: {checklist_path}")
        return
    print(checklist_path.read_text(encoding="utf-8"))


def main():
    args = sys.argv[1:]

    if show_help_if_no_args("ccwork", args):
        return

    cmd = args[0]

    if cmd == "list":
        list_processes()
    elif cmd == "status" and len(args) >= 2:
        status(args[1])
    elif cmd == "init" and len(args) >= 3:
        init_state(args[1], args[2])
    elif cmd == "update" and len(args) >= 4:
        step_num = int(args[2])
        step_status = args[3]
        output = args[4:] if len(args) > 4 else None
        update_step(args[1], step_num, step_status, output)
    elif cmd == "extract" and len(args) >= 2:
        output_arg = args[2] if len(args) >= 3 else None
        extract(args[1], output_arg)
    else:
        if cmd in ("show",) and len(args) > 1 and args[1].lower() == "checklist":
            cmd_show_checklist()
            return
        print(f"알 수 없는 명령: {cmd}")
        print("oowork_run.py help 로 사용법 확인")


if __name__ == "__main__":
    main()
