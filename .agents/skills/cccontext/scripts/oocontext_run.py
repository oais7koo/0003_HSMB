#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
oocontext_run.py

서브프로젝트 컨텍스트 관리 (.agents/skills/cccontext/SKILL.md 구현)

서브명령어:
    [N]            - SP N으로 설정 (sp_config.json 자동 갱신 포함)
    clear          - 공통(00)으로 초기화
    list           - SP 목록 표시
    status         - 현재 상태 및 서브명령어 리스트
    version        - 스킬 버전 정보

사용법:
    python .agents/skills/cccontext/scripts/oocontext_run.py
    python .agents/skills/cccontext/scripts/oocontext_run.py 04
    python .agents/skills/cccontext/scripts/oocontext_run.py clear
    python .agents/skills/cccontext/scripts/oocontext_run.py list
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

# Windows cp949 인코딩 문제 방지
if sys.stdout.encoding and sys.stdout.encoding.lower() in ("cp949", "cp1252", "ascii"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() in ("cp949", "cp1252", "ascii"):
    sys.stderr.reconfigure(encoding="utf-8")

# --- oo_common inline ---
import re as _re
_SKILLS_DIR = Path(__file__).parent.parent.parent

def _print_skill_help(skill_name):
    if sys.stdout.encoding and sys.stdout.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
        sys.stdout.reconfigure(encoding='utf-8')
    _sf = _SKILLS_DIR / skill_name / "SKILL.md"
    if not _sf.exists():
        print(f"[ERROR] .agents/skills/{skill_name}/SKILL.md not found")
        return
    _c = _sf.read_text(encoding="utf-8")
    _m = _re.search(r"##[^\n]*(?:서브명령어|명령어)\n\n((?:\|.+\n)+)", _c)
    if _m:
        print(f"`{skill_name} help` 서브명령어 목록:\n")
        print(_m.group(1).strip())
    else:
        print(f"[WARN] 서브명령어 섹션 없음: {skill_name}/SKILL.md")
# --- end oo_common inline ---

# 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
STATE_FILE = PROJECT_ROOT / ".omc" / "state" / "context.json"
DOC_DIR = PROJECT_ROOT / "00_doc"
SP_CONFIG_FILE = Path(__file__).parent.parent / "references" / "sp_config.json"


# ============================================================
# sp_config.json 로드 / 스캔
# ============================================================

def load_sp_definitions() -> dict:
    """
    sp_config.json → SP 정의 dict 반환.
    파일 없으면 프로젝트 폴더 스캔으로 자동 생성.
    반환 형식: {"00": {"folder": None, "doc_range": "d0001~d9999", "description": "..."}, ...}
    """
    if SP_CONFIG_FILE.exists():
        try:
            data = json.loads(SP_CONFIG_FILE.read_text(encoding="utf-8"))
            result = {}
            # SP00 공통은 항상 포함
            result["00"] = {"folder": None, "doc_range": "d0001~d9999", "description": "공통"}
            for item in data.get("sp_list", []):
                sp = item["sp"]
                if sp == "00":
                    result["00"]["description"] = item.get("description", "공통")
                    continue
                result[sp] = {
                    "folder": item.get("folder"),
                    "doc_range": item.get("doc_range", _calc_doc_range(sp)),
                    "description": item.get("description", item.get("folder", "")),
                }
            return result
        except Exception:
            pass
    # fallback: 폴더 스캔
    return scan_sp_folders()


def _calc_doc_range(sp: str) -> str:
    """SP 번호로 doc_range 계산: SP=04 → 'd40001~d49999'"""
    n = int(sp)
    if n == 0:
        return "d0001~d9999"
    return f"d{n*10000+1}~d{n*10000+9999}"


def scan_sp_folders() -> dict:
    """
    프로젝트 루트에서 0N_* 패턴 폴더 스캔 → SP 정의 dict 반환.
    """
    result = {"00": {"folder": None, "doc_range": "d0001~d9999", "description": "공통"}}
    pattern = re.compile(r'^(0[1-9])_(.+)$')
    for item in sorted(PROJECT_ROOT.iterdir()):
        if not item.is_dir():
            continue
        m = pattern.match(item.name)
        if not m:
            continue
        sp = m.group(1)          # "04"
        desc = m.group(2)        # "scraping"
        result[sp] = {
            "folder": item.name,
            "doc_range": _calc_doc_range(sp),
            "description": desc,
        }
    return result


# ============================================================
# 컨텍스트 저장/로드
# ============================================================

def load_context() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, KeyError):
            pass
    return {"sp": "00", "updated_at": None}


def save_context(sp: str) -> dict:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "sp": sp,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    STATE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def get_sp_folder(sp: str) -> str:
    return f"sp{int(sp):02d}"


def get_todo_doc_path(sp: str) -> Path:
    sp_num = int(sp)
    doc_num = sp_num * 10000 + 4
    return DOC_DIR / get_sp_folder(sp) / f"d{str(doc_num).zfill(4)}_todo.md"


def get_sp_info(sp: str, defs: dict) -> str:
    info = defs.get(sp, {"description": "unknown", "folder": None, "doc_range": "?"})
    folder = info["folder"] or "(공통)"
    return f"SP{sp} ({info['description']}) | {folder} | {info['doc_range']}"


# ============================================================
# 명령어
# ============================================================

def cmd_show():
    defs = load_sp_definitions()
    ctx = load_context()
    current_sp = ctx.get("sp", "00")
    updated_at = ctx.get("updated_at", "미설정")
    todo_path = get_todo_doc_path(current_sp)
    todo_exists = "✓ 존재" if todo_path.exists() else "✗ 없음"

    print("## cccontext - 현재 컨텍스트\n")
    print(f"| 항목 | 값 |")
    print(f"|------|-----|")
    print(f"| 현재 SP | **SP{current_sp}** |")
    print(f"| 서브프로젝트 | {get_sp_info(current_sp, defs)} |")
    print(f"| TODO 문서 | `{todo_path.relative_to(PROJECT_ROOT)}` {todo_exists} |")
    print(f"| 설정 시각 | {updated_at} |")
    print(f"| 상태 파일 | `.omc/state/context.json` |")


def cmd_set(sp: str, dry_run: bool = False):
    # SP 전환 전 sp_config.json 자동 갱신 (dry_run이 아닐 때만)
    if not dry_run:
        cmd_update(dry_run=False)

    defs = load_sp_definitions()
    sp = sp.zfill(2)
    if sp not in defs:
        print(f"[ERROR] 유효하지 않은 SP: {sp}")
        print(f"  등록된 SP: {', '.join(sorted(defs.keys()))}")
        print(f"  새 SP 추가는 프로젝트 루트에 0N_* 폴더를 생성하면 자동 감지됩니다.")
        sys.exit(1)

    if dry_run:
        print(f"## cccontext - SP{sp} 설정 예정 (dry-run)\n")
        print(f"- **서브프로젝트**: {get_sp_info(sp, defs)}")
        todo_path = get_todo_doc_path(sp)
        todo_exists = "✓ 존재" if todo_path.exists() else "✗ 없음 (자동 생성 필요)"
        print(f"- **TODO 문서**: `{todo_path.relative_to(PROJECT_ROOT)}` {todo_exists}")
        print(f"\n(dry-run) 실제 수정 없음.")
        return

    data = save_context(sp)
    todo_path = get_todo_doc_path(sp)
    todo_exists = "✓ 존재" if todo_path.exists() else "✗ 없음 (자동 생성 필요)"

    print(f"## cccontext - SP{sp} 설정 완료\n")
    print(f"- **서브프로젝트**: {get_sp_info(sp, defs)}")
    print(f"- **TODO 문서**: `{todo_path.relative_to(PROJECT_ROOT)}` {todo_exists}")
    print(f"- **설정 시각**: {data['updated_at']}")
    print(f"\n> 이후 cccheck/ccfix/ccdev 등은 SP{sp} 문서를 참조합니다.")


def cmd_clear():
    save_context("00")
    print("## cccontext - 공통(SP00)으로 초기화\n")
    print("- 이후 모든 스킬은 `00_doc/sp00/d0004_todo.md`를 참조합니다.")


def cmd_list():
    defs = load_sp_definitions()
    ctx = load_context()
    current_sp = ctx.get("sp", "00")
    config_src = "sp_config.json" if SP_CONFIG_FILE.exists() else "폴더 스캔"

    print(f"## cccontext - SP 목록 ({config_src})\n")
    print("| SP | 설명 | 폴더 | 문서 범위 | 상태 |")
    print("|----|------|------|----------|------|")

    for sp, info in sorted(defs.items()):
        folder = info["folder"] or "(공통)"
        marker = " ◀ 현재" if sp == current_sp else ""
        if info["folder"]:
            folder_path = PROJECT_ROOT / info["folder"]
            status = "Active" if folder_path.exists() else "미생성"
        else:
            status = "공통"
        print(f"| SP{sp} | {info['description']} | {folder} | {info['doc_range']} | {status}{marker} |")


def cmd_update(dry_run: bool = False):
    """프로젝트 폴더 스캔 → sp_config.json 자동 갱신 (내부 헬퍼, cmd_set에서 자동 호출)"""
    print(f"[cccontext sp_config 갱신{'  --dry-run' if dry_run else ''}]\n")

    # 현재 상태 로드
    old_defs = load_sp_definitions()
    # 폴더 스캔으로 신규 상태 생성
    new_defs = scan_sp_folders()

    # 변경사항 계산
    added = sorted(set(new_defs) - set(old_defs))
    removed = sorted(set(old_defs) - set(new_defs))
    changed = []
    for sp in sorted(set(new_defs) & set(old_defs)):
        if new_defs[sp].get("folder") != old_defs[sp].get("folder"):
            changed.append(sp)

    if not added and not removed and not changed:
        print("변경사항 없음 — sp_config.json이 최신 상태입니다.")
        return

    # 변경사항 출력
    if added:
        print("**추가:**")
        for sp in added:
            info = new_defs[sp]
            print(f"  + SP{sp} | {info['folder']} | {info['doc_range']}")
    if removed:
        print("**제거:**")
        for sp in removed:
            info = old_defs[sp]
            print(f"  - SP{sp} | {info.get('folder', '(공통)')} | {info['doc_range']}")
    if changed:
        print("**변경:**")
        for sp in changed:
            print(f"  ~ SP{sp}: {old_defs[sp].get('folder')} → {new_defs[sp].get('folder')}")

    if dry_run:
        print("\n(dry-run) 실제 수정 없음.")
        return

    # sp_config.json 생성/갱신 — 기존 description 보존
    sp_list = []
    for sp, info in sorted(new_defs.items()):
        # 기존 description 보존 (폴더명에서 추출한 값 대신)
        old_info = old_defs.get(sp, {})
        desc = old_info.get("description") or info["description"]
        sp_list.append({
            "sp": sp,
            "folder": info["folder"],
            "doc_range": info["doc_range"],
            "description": desc,
        })

    config = {
        "project": PROJECT_ROOT.name,
        "description": f"SP 목록. SSOT: 00_doc/sp00/d0001_prd.md §2.1",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sp_list": sp_list,
    }
    SP_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    SP_CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nsp_config.json 갱신 완료: {len(sp_list)}개 SP 등록")


def cmd_status():
    print("## cccontext v09 - 서브프로젝트 컨텍스트 관리\n")
    print("### 서브명령어\n")
    print("| 명령어 | 설명 |")
    print("|--------|------|")
    print("| `cccontext` | 현재 컨텍스트 확인 |")
    print("| `cccontext [N]` | SP N으로 설정 (sp_config.json 자동 갱신 포함) |")
    print("| `cccontext clear` | 공통(00) 초기화 |")
    print("| `cccontext list` | SP 목록 표시 |")
    print("| `cccontext status` | 현재 상태 (이 화면) |")
    print("| `cccontext version` | 버전 정보 |")
    print()
    cmd_show()


def cmd_version():
    print("cccontext v09")
    print("서브프로젝트 컨텍스트 관리 스킬")
    print(f"상태 파일: {STATE_FILE}")
    config_src = f"{SP_CONFIG_FILE} (존재)" if SP_CONFIG_FILE.exists() else "폴더 스캔 (sp_config.json 없음)"
    print(f"SP 정의: {config_src}")


def get_current_sp() -> str:
    """외부 스크립트에서 현재 SP 읽기용 함수"""
    return load_context().get("sp", "00")


# ============================================================
# main
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

    if not args:
        cmd_show()
        return

    cmd = args[0].lower()

    if cmd in ("help", "-h", "--help"):
        _print_skill_help("cccontext")
    elif cmd == "version":
        cmd_version()
    elif cmd == "status":
        cmd_status()
    elif cmd == "clear":
        cmd_clear()
    elif cmd == "list":
        cmd_list()
    elif cmd == "show":
        cmd_show()
    elif cmd == "check":
        print(f"[check] cccontext 체크리스트 안내")
        _print_skill_help("cccontext")
    elif cmd == "update":
        dry_run = "--dry-run" in args
        cmd_update(dry_run=dry_run)
    elif cmd.isdigit() or (len(cmd) == 2 and cmd[0].isdigit() and cmd[1].isdigit()):
        dry_run = "--dry-run" in args
        cmd_set(cmd, dry_run=dry_run)
    else:
        if cmd in ("show",) and len(args) > 1 and args[1].lower() == "checklist":
            cmd_show_checklist()
            return
        print(f"[ERROR] 알 수 없는 명령어: {cmd}")
        print("사용법: cccontext [N | clear | list | status | version]")
        sys.exit(1)


if __name__ == "__main__":
    main()
