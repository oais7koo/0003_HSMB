#!/usr/bin/env python3
"""
oos_new_session.py

UserPromptSubmit 훅: 사용자가 'oos'를 입력하면
새 터미널 창에서 claude를 열고 현재 프롬프트를 차단한다.
"""

import json
import sys
import subprocess
import os

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


def open_new_terminal(cwd: str):
    """새 터미널 창에서 claude를 실행. Windows Terminal → cmd 순서로 시도."""
    # 1순위: Windows Terminal
    try:
        subprocess.Popen(
            ["wt", "new-tab", "--startingDirectory", cwd, "--", "claude"],
            creationflags=subprocess.DETACHED_PROCESS,
        )
        return "wt"
    except FileNotFoundError:
        pass

    # 2순위: cmd.exe
    try:
        subprocess.Popen(
            ["cmd.exe", "/c", "start", "cmd", "/k",
             f'cd /d "{cwd}" && claude'],
        )
        return "cmd"
    except Exception:
        pass

    return None


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    prompt = data.get("prompt", "").strip()

    if prompt in ("oos", "oos run", "/oos"):
        cwd = os.getcwd()
        terminal = open_new_terminal(cwd)

        if terminal:
            msg = f"새 Claude 세션을 열었습니다 ({terminal}). 새 창에서 oos를 실행하세요."
        else:
            msg = "새 터미널을 열지 못했습니다. 수동으로 새 창을 열어 claude를 실행하세요."

        print(json.dumps({
            "decision": "block",
            "reason": msg,
        }, ensure_ascii=False))
    # else: 아무것도 출력하지 않으면 프롬프트가 정상 처리됨


if __name__ == "__main__":
    main()
