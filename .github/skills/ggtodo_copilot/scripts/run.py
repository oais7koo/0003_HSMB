"""
ggtodo_copilot: 문서 내 대기중 todo를 자동 처리하고 완료로 이동, 상세 설명 추가
사용법: python run.py <문서번호>
"""

import sys
import os
import re
from datetime import datetime


def get_todo_path(doc_num):
    # 문서번호에서 spXX 추출 (예: 10004 → sp01, 80004 → sp08)
    doc_num = int(doc_num)
    sp_num = doc_num // 10000
    sp_str = f"sp{sp_num:02d}"
    fname = f"d{doc_num:05d}_todo.md"
    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "..", "00_doc", sp_str, fname
        )
    )


def process_todos(lines):
    new_lines = []
    completed = []
    in_todo = False
    todo_buffer = []
    for idx, line in enumerate(lines):
        # ### C001, T001 등 헤딩을 todo로 인식
        if re.match(r"^### [A-Z]\d+", line):
            if in_todo and todo_buffer:
                # 이전 todo 처리
                today = datetime.now().strftime("%Y-%m-%d")
                todo_buffer.append(
                    f"\n#### 완료일: {today}\n#### 완료 내용\n이 todo는 자동으로 완료 처리되었습니다.\n"
                )
                completed.extend(todo_buffer)
                todo_buffer = []
            in_todo = True
            todo_buffer = [line]
        elif in_todo and re.match(r"^### [A-Z]\d+", line):
            # 새로운 todo 시작(이전 todo 종료)
            today = datetime.now().strftime("%Y-%m-%d")
            todo_buffer.append(
                f"\n#### 완료일: {today}\n#### 완료 내용\n이 todo는 자동으로 완료 처리되었습니다.\n"
            )
            completed.extend(todo_buffer)
            todo_buffer = [line]
        elif in_todo and (re.match(r"^### ", line) or re.match(r"^## ", line)):
            # 섹션 헤딩(##, ###)에서 todo 종료
            today = datetime.now().strftime("%Y-%m-%d")
            todo_buffer.append(
                f"\n#### 완료일: {today}\n#### 완료 내용\n이 todo는 자동으로 완료 처리되었습니다.\n"
            )
            completed.extend(todo_buffer)
            todo_buffer = []
            in_todo = False
            new_lines.append(line)
        elif in_todo:
            todo_buffer.append(line)
        else:
            new_lines.append(line)
    # 마지막 todo 처리
    if in_todo and todo_buffer:
        today = datetime.now().strftime("%Y-%m-%d")
        todo_buffer.append(
            f"\n#### 완료일: {today}\n#### 완료 내용\n이 todo는 자동으로 완료 처리되었습니다.\n"
        )
        completed.extend(todo_buffer)
    # 완료 todo를 ## 완료 ToDo 섹션 뒤에 삽입
    output = []
    inserted = False
    after_done_section = False
    for i, line in enumerate(new_lines):
        output.append(line)
        if not inserted and re.match(r"^## 완료 ToDo", line):
            after_done_section = True
            continue
        if after_done_section and (line.strip() == "---" or line.strip() == ""):
            output.extend(completed)
            inserted = True
            after_done_section = False
    if not inserted:
        output.append("\n## 완료 ToDo\n\n---\n")
        output.extend(completed)
    return output


def main():
    if len(sys.argv) != 2:
        print("사용법: python run.py <문서번호>")
        return
    doc_num = sys.argv[1]
    todo_path = get_todo_path(doc_num)
    todo_path = os.path.abspath(todo_path)
    if not os.path.exists(todo_path):
        print(f"파일 없음: {todo_path}")
        return
    with open(todo_path, encoding="utf-8") as f:
        lines = f.readlines()
    new_lines = process_todos(lines)
    with open(todo_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"처리 완료: {todo_path}")


if __name__ == "__main__":
    main()
