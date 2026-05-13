"""
Design Token Sync - 토큰 JSON → SCSS/CSS 자동 변환 도구

Usage:
    uv run token_sync.py                    # base 토큰만 변환
    uv run token_sync.py --theme chuckchuck # 테마 오버라이드 적용
    uv run token_sync.py --all-themes       # 전체 테마 일괄 생성
    uv run token_sync.py --dry-run          # 미리보기 (파일 생성 안 함)
"""

import json
import argparse
from pathlib import Path
from datetime import datetime


# 경로 설정 (1_oais/07_designsystem 기준)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent  # 1_oais/
DS_ROOT = PROJECT_ROOT / "07_designsystem"
TOKENS_SHARED = DS_ROOT / "02_tokens" / "00_shared"
TOKENS_WEB = DS_ROOT / "02_tokens" / "01_web"
TOKENS_DIR = DS_ROOT / "02_tokens"   # 테마 폴더들이 {NN}_{name} 형태로 직접 위치
OUTPUT_DIR = DS_ROOT / "03_vars"


def load_json(path: Path) -> dict:
    """JSON 파일 로드."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def deep_merge(base: dict, override: dict) -> dict:
    """딕셔너리 깊은 병합. override가 base를 덮어씀."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_tokens(theme: str | None = None) -> dict:
    """shared + web 토큰 로드 후 테마 오버라이드 병합."""
    tokens = {}

    # 1) 공유 토큰 (00_shared)
    for json_file in sorted(TOKENS_SHARED.glob("*.json")):
        data = load_json(json_file)
        tokens[json_file.stem] = data

    # 2) 웹 전용 토큰 (01_web)
    for json_file in sorted(TOKENS_WEB.glob("*.json")):
        data = load_json(json_file)
        tokens[json_file.stem] = data

    # 3) 테마 오버라이드 ({NN}_{theme} 폴더 탐색)
    if theme:
        theme_dir = next(
            (d for d in sorted(TOKENS_DIR.iterdir())
             if d.is_dir() and d.name.endswith(f"_{theme}") and d.name[0].isdigit()),
            None
        )
        if theme_dir is None:
            raise FileNotFoundError(f"테마 '{theme}' 없음 in {TOKENS_DIR}")
        for json_file in sorted(theme_dir.glob("*.json")):
            if json_file.stem in tokens:
                tokens[json_file.stem] = deep_merge(tokens[json_file.stem], load_json(json_file))
            else:
                tokens[json_file.stem] = load_json(json_file)

    return tokens


def extract_values(data: dict, prefix: str = "") -> list[tuple[str, str, str]]:
    """중첩 JSON에서 (변수명, 값, 주석) 튜플 리스트 추출."""
    results = []
    for key, value in data.items():
        if key.startswith("$") or key in ("description", "version", "base-unit", "usage-guide", "bootstrap-defaults", "cdn"):
            continue

        current = f"{prefix}-{key}" if prefix else key

        if isinstance(value, dict):
            if "value" in value:
                comment = value.get("comment", "")
                results.append((current, value["value"], comment))
            else:
                results.extend(extract_values(value, current))

    return results


def generate_scss(tokens: dict, theme: str | None) -> str:
    """SCSS 변수 파일 생성."""
    theme_label = theme or "base"
    lines = [
        f"// Design Token - Auto Generated",
        f"// Theme: {theme_label}",
        f"// Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"// Source: 07_designsystem/02_tokens/base/ {'+ 07_designsystem/02_tokens/themes/' + theme + '/' if theme else ''}",
        f"// WARNING: 이 파일을 직접 수정하지 마세요. token_sync.py로 생성됩니다.",
        "",
    ]

    for file_name, data in tokens.items():
        values = extract_values(data)
        if not values:
            continue

        desc = data.get("description", file_name)
        lines.append(f"// --- {desc} ---")

        for var_name, var_value, comment in values:
            scss_var = f"${var_name}"
            comment_str = f" // {comment}" if comment else ""
            lines.append(f"{scss_var}: {var_value} !default;{comment_str}")

        lines.append("")

    return "\n".join(lines)


def generate_css(tokens: dict, theme: str | None) -> str:
    """CSS Custom Properties 파일 생성."""
    theme_label = theme or "base"
    lines = [
        f"/* Design Token - Auto Generated */",
        f"/* Theme: {theme_label} */",
        f"/* Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} */",
        f"/* WARNING: 이 파일을 직접 수정하지 마세요. token_sync.py로 생성됩니다. */",
        "",
        ":root {",
    ]

    for file_name, data in tokens.items():
        values = extract_values(data)
        if not values:
            continue

        desc = data.get("description", file_name)
        lines.append(f"  /* {desc} */")

        for var_name, var_value, comment in values:
            css_var = f"--ds-{var_name}"
            comment_str = f" /* {comment} */" if comment else ""
            lines.append(f"  {css_var}: {var_value};{comment_str}")

        lines.append("")

    lines.append("}")
    return "\n".join(lines)


def generate_pen_variables(tokens: dict) -> dict:
    """Pencil .pen 변수 포맷 생성 (JSON 출력)."""
    pen_vars = {}
    for file_name, data in tokens.items():
        values = extract_values(data)
        for var_name, var_value, comment in values:
            val_str = str(var_value)
            if val_str.startswith("#") or val_str.startswith("rgb"):
                pen_vars[var_name] = {"type": "color", "value": val_str}
            elif isinstance(var_value, (int, float)) or val_str.replace(".", "").replace("-", "").isdigit():
                pen_vars[var_name] = {"type": "number", "value": val_str}
            else:
                pen_vars[var_name] = {"type": "string", "value": val_str}
    return pen_vars


def sync(theme: str | None = None, dry_run: bool = False) -> dict:
    """토큰 동기화 실행. 생성된 파일 경로 반환."""
    tokens = load_tokens(theme)
    theme_label = theme or "base"

    scss_content = generate_scss(tokens, theme)
    css_content = generate_css(tokens, theme)
    pen_vars = generate_pen_variables(tokens)

    results = {"theme": theme_label, "files": []}

    if dry_run:
        print(f"\n=== [{theme_label}] SCSS Preview ===")
        print(scss_content[:500] + "\n...")
        print(f"\n=== [{theme_label}] CSS Preview ===")
        print(css_content[:500] + "\n...")
        print(f"\n=== [{theme_label}] Pencil Variables: {len(pen_vars)} tokens ===")
        return results

    # 출력 디렉토리: base→01_web, 테마→{NN}_{name} (입력 폴더와 같은 번호 사용)
    if theme:
        ref_dir = next(
            (d for d in sorted(TOKENS_DIR.iterdir())
             if d.is_dir() and d.name.endswith(f"_{theme}") and d.name[0].isdigit()),
            None
        )
        prefix = ref_dir.name.split("_")[0] if ref_dir else "10"
        sample_dir = OUTPUT_DIR / f"{prefix}_{theme_label}"
    else:
        sample_dir = OUTPUT_DIR / "01_web"
    scss_dir = sample_dir / "scss"
    css_dir = sample_dir / "css"
    pen_dir = sample_dir / "pen"

    scss_dir.mkdir(parents=True, exist_ok=True)
    css_dir.mkdir(parents=True, exist_ok=True)
    pen_dir.mkdir(parents=True, exist_ok=True)

    scss_path = scss_dir / "_variables.scss"
    css_path = css_dir / "variables.css"
    pen_path = pen_dir / f"{theme_label}_variables.json"

    scss_path.write_text(scss_content, encoding="utf-8")
    css_path.write_text(css_content, encoding="utf-8")
    pen_path.write_text(json.dumps(pen_vars, indent=2, ensure_ascii=False), encoding="utf-8")

    results["files"] = [str(scss_path), str(css_path), str(pen_path)]
    print(f"[{theme_label}] Generated:")
    for f in results["files"]:
        print(f"  + {f}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Design Token Sync")
    parser.add_argument("--theme", type=str, help="테마 이름 (예: chuckchuck)")
    parser.add_argument("--all-themes", action="store_true", help="전체 테마 일괄 생성")
    parser.add_argument("--dry-run", action="store_true", help="미리보기 (파일 생성 안 함)")
    args = parser.parse_args()

    print(f"Design Token Sync v2.0")
    print(f"Shared: {TOKENS_SHARED}")
    print(f"Web:    {TOKENS_WEB}")
    print(f"Themes: {TOKENS_DIR} (11_~15_* 폴더)")

    # base 토큰 항상 생성
    sync(theme=None, dry_run=args.dry_run)

    if args.all_themes:
        for theme_dir in sorted(TOKENS_DIR.iterdir()):
            if not theme_dir.is_dir():
                continue
            parts = theme_dir.name.split("_", 1)
            # 숫자 prefix가 11 이상인 폴더만 테마로 처리
            if len(parts) < 2 or not parts[0].isdigit() or int(parts[0]) < 11:
                continue
            theme_name = parts[1]
            if any(theme_dir.glob("*.json")):
                sync(theme=theme_name, dry_run=args.dry_run)
            else:
                print(f"[{theme_dir.name}] 토큰 파일 없음, 건너뜀")
    elif args.theme:
        sync(theme=args.theme, dry_run=args.dry_run)

    print("\nDone.")


if __name__ == "__main__":
    main()
