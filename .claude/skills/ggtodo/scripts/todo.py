"""
ggtodo: Copilot용 간단 todo 관리 스크립트
- add <내용>: todo 추가
- list: todo 목록 출력
- done <번호>: todo 완료 처리
"""

import sys
import os

TODO_FILE = os.path.join(os.path.dirname(__file__), "..", "todo.md")


def add_todo(content):
    with open(TODO_FILE, "a", encoding="utf-8") as f:
        f.write(f"- [ ] {content}\n")
    print("추가 완료")


def list_todo():
    if not os.path.exists(TODO_FILE):
        print("todo 없음")
        return
    with open(TODO_FILE, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            print(f"{i}. {line.strip()}")


def done_todo(idx):
    if not os.path.exists(TODO_FILE):
        print("todo 없음")
        return
    with open(TODO_FILE, encoding="utf-8") as f:
        lines = f.readlines()
    if idx < 1 or idx > len(lines):
        print("잘못된 번호")
        return
    if "[x]" in lines[idx - 1]:
        print("이미 완료됨")
        return
    lines[idx - 1] = lines[idx - 1].replace("[ ]", "[x]", 1)
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("완료 처리")


def main():
    if len(sys.argv) < 2:
        print("add/list/done 명령어 필요")
        return
    cmd = sys.argv[1]
    if cmd == "add" and len(sys.argv) >= 3:
        add_todo(" ".join(sys.argv[2:]))
    elif cmd == "list":
        list_todo()
    elif cmd == "done" and len(sys.argv) == 3:
        try:
            idx = int(sys.argv[2])
            done_todo(idx)
        except ValueError:
            print("숫자 입력 필요")
    else:
        print("사용법: add <내용> | list | done <번호>")


if __name__ == "__main__":
    main()
