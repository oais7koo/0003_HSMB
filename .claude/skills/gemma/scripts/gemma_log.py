#!/usr/bin/env python3
"""gemma_log.py - Gemma 호출 로그 저장/조회 유틸

저장 경로: .claude/.omc/gemma-usage/{HOSTNAME}-{YYYYMM}.jsonl
- 호스트별·월별 샤딩으로 Resilio 동기화 시 충돌 회피
- 각 기기는 자기 파일에만 append → 동시 쓰기 불가
"""
from __future__ import annotations

import json
import os
import socket
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Iterable

# 경로: .../<repo>/.claude/skills/gemma/scripts/gemma_log.py
#   parents[0]=scripts  [1]=gemma  [2]=skills  [3]=.claude  [4]=<repo>
_REPO_ROOT = Path(__file__).resolve().parents[4]
LOG_DIR = _REPO_ROOT / ".claude" / ".omc" / "gemma-usage"


def _ensure_utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if stream and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


_ensure_utf8_stdio()


def _hostname() -> str:
    return (
        os.environ.get("COMPUTERNAME")
        or os.environ.get("HOSTNAME")
        or socket.gethostname()
        or "unknown"
    )


def _log_file() -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return LOG_DIR / f"{_hostname()}-{datetime.now().strftime('%Y%m')}.jsonl"


def _head(text: str | None, n: int = 120) -> str:
    if not text:
        return ""
    s = text.replace("\n", " ").replace("\r", " ").strip()
    return s[:n]


def append_log(
    *,
    caller: str | None,
    model: str,
    prompt: str,
    response: str,
    elapsed_ms: int | None = None,
    extra: dict | None = None,
) -> None:
    """Gemma 호출 1건을 호스트별 월간 로그 파일에 append."""
    entry = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "host": _hostname(),
        "caller": caller or "direct",
        "model": model,
        "prompt_head": _head(prompt),
        "response_head": _head(response),
        "elapsed_ms": elapsed_ms,
    }
    if extra:
        entry["extra"] = extra
    try:
        with _log_file().open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        # 로그 실패가 본 작업을 막지 않도록 경고만
        print(f"[gemma_log WARN] append 실패: {e}", file=sys.stderr)


def iter_logs(caller: str | None = None) -> Iterable[dict]:
    if not LOG_DIR.exists():
        return
    for p in sorted(LOG_DIR.glob("*.jsonl")):
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if caller and (rec.get("caller") or "").lower() != caller.lower():
                continue
            yield rec


def cmd_log(args: list[str]) -> None:
    """gemma log [skill] — 인자 없으면 집계, 있으면 해당 스킬 최근 20건 표시."""
    target = args[0] if args else None
    rows = list(iter_logs(caller=target))
    rows.sort(key=lambda r: r.get("ts", ""))

    if not rows:
        suffix = f" (caller={target})" if target else ""
        print(f"[gemma log] 기록 없음{suffix}")
        print(f"  경로: {LOG_DIR}")
        return

    if target:
        rows = rows[-20:]
        print(f"[gemma log] caller={target} 최근 {len(rows)}건")
        print(f"{'TS':<19}  {'HOST':<12}  {'MODEL':<28}  PROMPT")
        print("-" * 100)
        for r in rows:
            ts = r.get("ts", "")[:19]
            host = (r.get("host") or "")[:12]
            model = (r.get("model") or "")[:28]
            prompt = r.get("prompt_head", "")
            print(f"{ts:<19}  {host:<12}  {model:<28}  {prompt}")
        return

    # 전체 집계
    by_caller = Counter(r.get("caller") or "direct" for r in rows)
    by_model = Counter(r.get("model") or "?" for r in rows)
    by_host = Counter(r.get("host") or "?" for r in rows)

    print(f"[gemma log] 총 {len(rows)}건")
    print(f"  로그 디렉토리: {LOG_DIR}")
    print(f"\n호출 스킬(caller)별:")
    for caller, n in by_caller.most_common():
        print(f"  {caller:<22} {n:>5}")
    print(f"\n모델별:")
    for model, n in by_model.most_common():
        print(f"  {model:<32} {n:>5}")
    print(f"\n호스트별:")
    for host, n in by_host.most_common():
        print(f"  {host:<20} {n:>5}")


if __name__ == "__main__":
    cmd_log(sys.argv[1:])
