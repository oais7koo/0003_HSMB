#!/usr/bin/env python3
"""
sync_flag.py - PostToolUse hook용 스킬/튜토리얼 변경 감지 스크립트

편집된 파일이 스킬 SKILL.md 또는 튜토리얼 MD이면
.omc/sync-flags/tutorial_sync.json에 동기화 필요 플래그 기록.

Hook input (stdin): JSON with tool_name, tool_input fields
"""

import sys
import json
import datetime
from pathlib import Path


def load_flags(flags_file: Path) -> dict:
    if flags_file.exists():
        try:
            return json.loads(flags_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"skill_to_tutorial": [], "tutorial_to_skill": []}


def save_flags(flags_file: Path, flags: dict):
    flags_file.parent.mkdir(parents=True, exist_ok=True)
    flags_file.write_text(json.dumps(flags, ensure_ascii=False, indent=2), encoding="utf-8")


def upsert(lst: list, key: str, value: str, entry: dict):
    """key=value인 항목을 제거 후 entry 추가 (중복 방지)."""
    lst[:] = [x for x in lst if x.get(key) != value]
    lst.append(entry)


def main():
    try:
        raw = sys.stdin.read()
        hook_data = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)

    tool_name = hook_data.get("tool_name", "")
    tool_input = hook_data.get("tool_input", {})

    # 편집된 파일 경로 추출
    file_path = None
    if tool_name in ("Edit", "MultiEdit", "Write"):
        file_path = tool_input.get("file_path", "")

    if not file_path:
        sys.exit(0)

    fp = Path(file_path)
    parts = fp.parts
    now = datetime.datetime.now().isoformat()

    flags_file = Path(".omc/sync-flags/tutorial_sync.json")
    flags = load_flags(flags_file)
    changed = False

    # 스킬 SKILL.md 변경 감지: .claude/skills/oo*/SKILL.md
    if ".claude" in parts and "skills" in parts:
        try:
            skills_idx = list(parts).index("skills")
            skill_name = parts[skills_idx + 1] if skills_idx + 1 < len(parts) else ""
            if skill_name.startswith("oo") and fp.name == "SKILL.md":
                upsert(
                    flags["skill_to_tutorial"],
                    "skill", skill_name,
                    {"skill": skill_name, "file": str(fp), "modified": now}
                )
                changed = True
        except (ValueError, IndexError):
            pass

    # 튜토리얼 파일 변경 감지: .claude/tutorial/*.md
    if "00_doc" in parts and "tutorial" in parts:
        tutorial_file = fp.name
        if tutorial_file.endswith(".md") and tutorial_file != "README.md":
            upsert(
                flags["tutorial_to_skill"],
                "tutorial", tutorial_file,
                {"tutorial": tutorial_file, "file": str(fp), "modified": now}
            )
            changed = True

    if changed:
        save_flags(flags_file, flags)


if __name__ == "__main__":
    main()
