#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SAMPLE-REF 블록을 모든 oo* SKILL.md에 일괄 추가
- GEMMA-REF:END 다음에 삽입 (있는 경우)
- GEMMA-REF 없으면 파일 끝에 추가
- 알리아스(ooc, ood, oof, ook, oos) 제외
- 이미 SAMPLE-REF:START 있으면 skip (멱등)
"""

from pathlib import Path

BASE = Path(__file__).parent

ALIASES = {"ooc", "ood", "oof", "ook", "oos"}

SAMPLE_BLOCK = """
<!-- SAMPLE-REF:START -->

## 샘플 참조 (산출물 품질 향상)

> 산출물 작성 직전, `samples/` 폴더가 존재하면 샘플을 few-shot 참고 자료로 활용한다.

| 항목 | 내용 |
|------|------|
| 샘플 위치 | `.claude/skills/{스킬명}/samples/` |
| 참조 시점 | 산출물 작성 직전 (on-demand, 자동 로드 X) |
| 샘플 있는 경우 | 샘플의 스타일·깊이·어조를 참고하여 산출물 작성 |
| 샘플 없는 경우 | 템플릿(`templates/`)만으로 진행 (현재 상태) |
| 샘플 추가 방법 | 품질 좋은 기존 산출물을 `samples/` 폴더에 저장 |

<!-- SAMPLE-REF:END -->"""


def patch(skill_dir: Path) -> str:
    skill_name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        return f"[SKIP] {skill_name}: SKILL.md 없음"

    raw = skill_md.read_bytes()
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        content = raw.decode("utf-8-sig")

    use_crlf = "\r\n" in content
    text = content.replace("\r\n", "\n")

    if "<!-- SAMPLE-REF:START -->" in text:
        return f"[SKIP] {skill_name}: 이미 존재"

    if "<!-- GEMMA-REF:END -->" in text:
        text = text.replace("<!-- GEMMA-REF:END -->", "<!-- GEMMA-REF:END -->" + SAMPLE_BLOCK)
    else:
        text = text.rstrip("\n") + "\n" + SAMPLE_BLOCK + "\n"

    if use_crlf:
        text = text.replace("\n", "\r\n")

    skill_md.write_text(text, encoding="utf-8")
    return f"[OK] {skill_name}"


def main():
    skill_dirs = sorted(
        d for d in BASE.iterdir()
        if d.is_dir() and d.name.startswith("oo") and d.name not in ALIASES
    )

    ok = skip = 0
    for d in skill_dirs:
        result = patch(d)
        print(result)
        if result.startswith("[OK]"):
            ok += 1
        else:
            skip += 1

    print(f"\n완료: {ok}개 추가, {skip}개 스킵")


if __name__ == "__main__":
    main()
