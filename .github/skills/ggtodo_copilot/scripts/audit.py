"""
ggtodo_copilot: 완료 ToDo 블록 검증 (audit)
사용법: python audit.py <문서번호>
"""

import sys
import os
import re
from datetime import datetime


def get_todo_path(doc_num):
    doc_num = int(doc_num)
    sp_num = doc_num // 10000
    sp_str = f"sp{sp_num:02d}"
    fname = f"d{doc_num:05d}_todo.md"
    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "..", "00_doc", sp_str, fname
        )
    )


def parse_completed_blocks(lines):
    in_done = False
    block = []
    blocks = []
    for line in lines:
        if re.match(r"^## 완료 ToDo", line):
            in_done = True
            continue
        if in_done:
            if re.match(r"^### [A-Z]\d+", line):
                if block:
                    blocks.append(block)
                block = [line]
            elif block:
                block.append(line)
    if block:
        blocks.append(block)
    return blocks


def audit_block(block):
    title = None
    reg_date = None
    todo_content = None
    done_date = None
    done_content = None
    for line in block:
        if re.match(r"^### [A-Z]\d+", line):
            title = line.strip()
        elif line.strip().startswith("#### 등록일:"):
            reg_date = line.strip()
        elif line.strip().startswith("#### ToDo 내용"):
            todo_content = True
        elif line.strip().startswith("#### 완료일:"):
            done_date = line.strip()
        elif line.strip().startswith("#### 완료 내용"):
            done_content = True
    result = []
    if not title:
        result.append("❌ 제목(헤딩) 없음")
    if not reg_date:
        result.append("❌ 등록일 없음")
    if not todo_content:
        result.append("❌ ToDo 내용 없음")
    if not done_date:
        result.append("❌ 완료일 없음")
    if not done_content:
        result.append("❌ 완료 내용 없음")
    if not result:
        result.append("✅ 형식 이상 없음")
    return title or "(제목 없음)", result


def main():
    if len(sys.argv) != 2:
        print("사용법: python audit.py <문서번호>")
        return
    todo_path = get_todo_path(sys.argv[1])
    if not os.path.exists(todo_path):
        print(f"파일 없음: {todo_path}")
        return
    with open(todo_path, encoding="utf-8") as f:
        lines = f.readlines()
    blocks = parse_completed_blocks(lines)
    print(f"[완료 ToDo 블록 {len(blocks)}개 검증 결과]")
    for i, block in enumerate(blocks, 1):
        title, result = audit_block(block)
        print(f"\n{i}. {title}")
        for r in result:
            print(f"   {r}")


if __name__ == "__main__":
    main()
