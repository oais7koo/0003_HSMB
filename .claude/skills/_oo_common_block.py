# --- oo_common inline ---
import re as _re
_SKILLS_DIR = Path(__file__).parent.parent.parent

def _print_skill_help(skill_name):
    _sf = _SKILLS_DIR / skill_name / "SKILL.md"
    if not _sf.exists():
        print(f"[ERROR] .claude/skills/{skill_name}/SKILL.md not found")
        return
    _c = _sf.read_text(encoding="utf-8")
    _m = _re.search(r"## 서브명령어

((?:\|.+
)+)", _c)
    if _m:
        print(f" 서브명령어 목록:
")
        print(_m.group(1).strip())
    else:
        print(f"[WARN] 서브명령어 섹션 없음: {skill_name}/SKILL.md")

def show_help_if_no_args(skill_name, args):
    if not args:
        _print_skill_help(skill_name)
        return True
    return False
# --- end oo_common inline ---