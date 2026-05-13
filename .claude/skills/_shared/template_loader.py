"""
공용 템플릿 로더 유틸 - oo 스킬 전반 출력 포맷 분리 표준.

사용 패턴:
    from _shared.template_loader import load_template_block, render

    tpl = load_template_block(Path(__file__).parent.parent / "templates" / "foo_list.md")
    print(tpl.format(name="bar", count=3))

특징:
- templates/*.md 안의 ```template ... ``` 블록을 추출
- 블록이 없거나 파일이 없으면 빈 문자열 반환 (호출측이 fallback 처리)
- render() 는 변수 치환 + 누락 변수 경고 출력 (선택)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


_TEMPLATE_BLOCK_RE = re.compile(r"```template\n(.*?)\n```", re.DOTALL)


def load_template_block(template_path: Path, block_name: str = "template") -> str:
    """templates/*.md 파일에서 명명된 ``` ... ``` 블록 추출.

    Args:
        template_path: 템플릿 파일 절대 경로
        block_name: 블록 마커 (기본 'template'). 파일 안에 ```template 또는
                    ```{block_name} 으로 시작하는 블록을 찾는다.

    Returns:
        추출된 블록 문자열. 파일/블록 없으면 빈 문자열.
    """
    if not template_path.exists():
        return ""
    content = template_path.read_text(encoding="utf-8")
    pattern = re.compile(rf"```{re.escape(block_name)}\n(.*?)\n```", re.DOTALL)
    match = pattern.search(content)
    return match.group(1) if match else ""


def render(template: str, **vars: object) -> str:
    """템플릿 변수 치환. 누락 변수는 stderr로 경고 후 원본 `{name}` 보존."""
    try:
        return template.format(**vars)
    except KeyError as e:
        missing = str(e).strip("'\"")
        print(f"[template_loader] 누락 변수: {missing}", file=sys.stderr)
        safe_vars = {**{k: "{" + k + "}" for k in _extract_vars(template)}, **vars}
        return template.format(**safe_vars)


def _extract_vars(template: str) -> set[str]:
    return set(re.findall(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", template))


def verify_template_exists(skill_dir: Path, filename: str) -> bool:
    """스킬 디렉토리의 templates/ 아래 파일 존재 여부."""
    return (skill_dir / "templates" / filename).exists()
