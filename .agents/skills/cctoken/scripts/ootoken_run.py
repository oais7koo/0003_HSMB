#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ootoken_run.py - 토큰 사용량 모니터링
현재 소비율 기준으로 리셋 전 여유(+) 또는 초과(-) 시간을 표로 표시.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

if sys.stdout.encoding and sys.stdout.encoding.lower() in ("cp949", "cp1252", "ascii"):
    sys.stdout.reconfigure(encoding="utf-8")

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

def show_help_if_no_args(skill_name, args):
    if not args or args[0].lower() in ("help", "-h", "--help"):
        _print_skill_help(skill_name)
        return True
    return False
# --- end oo_common inline ---

CACHE_FILE = Path.home() / ".codex" / "plugins" / "oh-my-claudecode" / ".usage-cache.json"
WINDOW_5H  = timedelta(hours=5)
WINDOW_7D  = timedelta(days=7)
KST        = timezone(timedelta(hours=9))


def parse_iso(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def fmt_delta(td: timedelta) -> str:
    """timedelta → 'DDdHHh' 형식 (예: 02d03h)"""
    total = int(abs(td.total_seconds()))
    days  = total // 86400
    hours = (total % 86400) // 3600
    return f"{days:02d}d{hours:02d}h"


def calc_margin(pct: float, resets_at: datetime, window: timedelta, now: datetime):
    """
    Returns (pct, margin_str, is_safe)
    margin = time_to_100% - time_to_reset
      + : 여유 있음 (리셋 후에야 100% 도달)
      - : 초과 예상 (리셋 전에 100% 도달)
    """
    if resets_at is None or pct <= 0:
        return pct, "N/A", True

    window_start = resets_at - window
    elapsed_sec  = (now - window_start).total_seconds()
    if elapsed_sec <= 0:
        return pct, "N/A", True

    rate_per_h      = pct / (elapsed_sec / 3600)          # %/h
    hours_to_limit  = (100.0 - pct) / rate_per_h
    hours_to_reset  = (resets_at - now).total_seconds() / 3600

    margin_h = hours_to_limit - hours_to_reset             # + 여유, - 초과
    is_safe  = margin_h >= 0
    sign     = "+" if is_safe else "-"
    margin_str = sign + fmt_delta(timedelta(hours=abs(margin_h)))
    return pct, margin_str, is_safe


def run():
    if not CACHE_FILE.exists():
        print("[ERROR] 캐시 파일 없음 — OMC HUD 실행 여부 확인:", CACHE_FILE)
        return

    try:
        cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[ERROR] 캐시 읽기 실패: {e}")
        return

    data = cache.get("data") or {}
    if not data:
        print(f"[ERROR] 사용량 데이터 없음 (reason: {cache.get('errorReason', 'unknown')})")
        return

    now = datetime.now(timezone.utc)

    rows = [
        ("5시간",        data.get("fiveHourPercent", 0),  parse_iso(data.get("fiveHourResetsAt")),    WINDOW_5H),
        ("주간",         data.get("weeklyPercent", 0),     parse_iso(data.get("weeklyResetsAt")),      WINDOW_7D),
    ]
    if data.get("sonnetWeeklyPercent") is not None:
        rows.append(("Sonnet 주간", data["sonnetWeeklyPercent"], parse_iso(data.get("sonnetWeeklyResetsAt")), WINDOW_7D))
    if data.get("opusWeeklyPercent") is not None:
        rows.append(("Opus 주간",   data["opusWeeklyPercent"],   parse_iso(data.get("opusWeeklyResetsAt")),   WINDOW_7D))

    # 모델 정보 읽기
    model_cache = Path.home() / ".codex" / ".omc" / "model-cache.json"
    model_name = "unknown"
    if model_cache.exists():
        try:
            mc = json.loads(model_cache.read_text(encoding="utf-8"))
            model_name = mc.get("model", "unknown")
        except Exception:
            pass

    print(f"## cctoken — {model_name}\n")
    print(f"| 구분 | 사용률 | 여유(+) / 초과(-) |")
    print(f"|------|--------|-----------------|")
    for label, pct, resets_at, window in rows:
        pct, margin_str, is_safe = calc_margin(pct, resets_at, window, now)
        print(f"| {label} | {pct:.0f}% | {margin_str} |")


def cmd_show_checklist():
    """references/checklist.md 내용 출력"""
    checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[{SKILL_NAME}] checklist.md 없음: {checklist_path}")
        return
    print(checklist_path.read_text(encoding="utf-8"))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    cmd  = (args[0].lower() if args else "")
    if cmd in ("", "status"):
        run()
    elif cmd == "version":
        print("cctoken 버전: v01")
    elif cmd in ("help", "-h", "--help"):
        _print_skill_help("cctoken")
    else:
        if cmd in ("show",) and len(args) > 1 and args[1].lower() == "checklist":
            cmd_show_checklist()
            return
        print(f"[ERROR] 알 수 없는 명령어: {cmd}")


if __name__ == "__main__":
    main()
