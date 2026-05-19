#!/usr/bin/env python3
"""
v/oais*.md 파일들의 문서 이력 관리 섹션 초기화
과거 버전 이력을 삭제하고 v1.0으로 초기화
"""
import re
from pathlib import Path
from datetime import datetime

# 대상 파일 목록
TARGET_FILES = [
    ".claude/skills/oaischeck/SKILL.md",
    ".claude/skills/oaiscommand/SKILL.md",
    ".claude/skills/oaiscommit/SKILL.md",
    ".claude/skills/oaisdb/SKILL.md",
    ".claude/skills/oaisdoc/SKILL.md",
    ".claude/skills/oaisenv/SKILL.md",
    ".claude/skills/oaisfix/SKILL.md",
    ".claude/skills/oaishistory/SKILL.md",
    ".claude/skills/oaislib/SKILL.md",
    ".claude/skills/oaisplan/SKILL.md",
    ".claude/skills/oaisppt/SKILL.md",
    ".claude/skills/oaisprd/SKILL.md",
    ".claude/skills/oaisreport/SKILL.md",
    ".claude/skills/oaisbatch/SKILL.md",
    ".claude/skills/oaisstart/SKILL.md",
    ".claude/skills/oaisstop/SKILL.md",
    ".claude/skills/oaistest/SKILL.md",
]

def clean_version_history(file_path: str) -> bool:
    """
    문서 이력 관리 섹션의 과거 버전 이력 삭제
    
    Args:
        file_path: 처리할 파일 경로
        
    Returns:
        bool: 성공 여부
    """
    path = Path(file_path)
    if not path.exists():
        print(f"[ERROR] File not found: {file_path}")
        return False
    
    try:
        content = path.read_text(encoding='utf-8')
        
        # 문서 이력 관리 섹션 찾기 (다양한 변형 대응)
        pattern = r'(## 문서\s*이력\s*관리\s*\n\n\|[^\n]+\|\n\|[^\n]+\|)\n(\|[^\n]+\|\n)+\n(---)'
        
        # 새로운 이력으로 교체
        today = datetime.now().strftime('%Y-%m-%d')
        replacement = r'\1\n| v1.0 | ' + today + r' | 이력 초기화 |\n\n\3'
        
        new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
        
        if count == 0:
            print(f"[WARN] Pattern not found: {file_path}")
            return False
        
        if count > 1:
            print(f"[WARN] Multiple matches ({count}): {file_path}")
        
        # 파일 저장
        path.write_text(new_content, encoding='utf-8')
        print(f"[OK] Processed: {file_path} (matches: {count})")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed: {file_path} - {e}")
        return False

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("v/oais*.md 문서 이력 관리 섹션 초기화")
    print("=" * 60)
    print()
    
    success_count = 0
    fail_count = 0
    
    for file_path in TARGET_FILES:
        if clean_version_history(file_path):
            success_count += 1
        else:
            fail_count += 1
    
    print()
    print("=" * 60)
    print(f"처리 완료: {success_count}개 성공, {fail_count}개 실패")
    print("=" * 60)

if __name__ == "__main__":
    main()
