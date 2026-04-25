"""
ggskill: oo스킬을 copilot 호환 스킬로 변환하는 스크립트 (샘플)
- SKILL.md에서 copilot 미지원 요소(모델, 플러그인 등) 제거
- scripts/ 내 주요 명령어만 복사
"""

import sys
import os
import shutil

COPILOT_UNSUPPORTED = [
    "클로드코드",
    "전용 모델",
    "플러그인",
    "uv run",
    "claude",
    "playwright",
    "mcp",
    "ooenv",
    "ooflow",
    "oodev",
    "oocheck",
    "oofix",
    "ootest",
    "oocommit",
    "ooreview",
    "oosync",
    "oostart",
    "oostop",
    "ooskill",
    "oodeep",
    "oohwp",
    "ooppt",
    "oobook",
    "oosota",
    "oosurvey",
    "ooscrap",
    "oosidi",
    "ooreport",
    "ooresearch",
    "ooref",
    "oouser",
    "ooword",
    "oopaper",
    "oopdf",
    "oocontext",
    "oofeature",
    "oof",
    "ood",
    "ook",
    "ooc",
    "oos",
    "oorun",
    "oouv",
    "oonote",
    "oonext",
    "oonow",
    "oomemo",
    "ootodo",
    "oohistory",
    "oodata",
    "ooopti",
    "oolib",
    "oodb",
    "oodesign",
    "ootutorial",
    "theme-factory",
    "canvas-design",
    "web-artifacts-builder",
    "artifacts-builder",
    "frontend-design",
    "brand-guidelines",
    "slack-gif-creator",
    "algorithmic-art",
    "gemma",
    "ccenv",
    "ccusage",
    "qmd",
    "mcp-builder",
    "skillsmp-search",
    "python-expert",
    "summarize-github-issue-pr-notification",
    "suggest-fix-issue",
    "form-github-search-query",
    "show-github-search-result",
    "address-pr-comments",
    "create-pull-request",
    "pdf",
    "pptx",
    "xlsx",
]


def filter_skill_md(src, dst):
    with open(src, encoding="utf-8") as f:
        lines = f.readlines()
    filtered = []
    for line in lines:
        if not any(x in line for x in COPILOT_UNSUPPORTED):
            filtered.append(line)
    with open(dst, "w", encoding="utf-8") as f:
        f.writelines(filtered)


def copy_scripts(src_dir, dst_dir):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    for fname in os.listdir(src_dir):
        if fname.endswith(".py"):
            shutil.copy(os.path.join(src_dir, fname), os.path.join(dst_dir, fname))


def main():
    if len(sys.argv) != 3:
        print("사용법: convert.py <oo스킬폴더> <gg스킬폴더>")
        return
    oo_dir, gg_dir = sys.argv[1], sys.argv[2]
    filter_skill_md(os.path.join(oo_dir, "SKILL.md"), os.path.join(gg_dir, "SKILL.md"))
    copy_scripts(os.path.join(oo_dir, "scripts"), os.path.join(gg_dir, "scripts"))
    print(f"변환 완료: {gg_dir}")


if __name__ == "__main__":
    main()
