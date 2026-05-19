import json
import re
from pathlib import Path

ROOT = Path('.').resolve()
MANIFEST = ROOT / '.agents' / 'skills' / 'ccporting_manifest_all.json'
TARGET_ROOT = ROOT / '.agents' / 'skills'


def load_ports():
    data = json.loads(MANIFEST.read_text(encoding='utf-8'))
    return [(p['source'].split('/')[-1], p['target']) for p in data.get('ports', [])]


def replace_text(text: str, mapping: list[tuple[str, str]]) -> str:
    out = text
    out = out.replace('.claude/skills/', '.agents/skills/')
    out = out.replace('.codex/skills/', '.agents/skills/')
    out = out.replace('.codex/commands/', '.claude/commands/')
    out = out.replace('.codex/templates/', '.claude/templates/')
    for src, tgt in mapping:
        out = re.sub(rf'\b{re.escape(src)}\b', tgt, out)
    return out


def normalize_target(tgt: str, mapping: list[tuple[str, str]]) -> tuple[int, int]:
    base = TARGET_ROOT / tgt
    changed = 0
    files = 0
    for p in [base / 'SKILL.md', *list((base / 'scripts').rglob('*.py'))]:
        if not p.exists() or 'upstream' in p.parts:
            continue
        old = p.read_text(encoding='utf-8', errors='ignore')
        new = replace_text(old, mapping)
        if new != old:
            p.write_text(new, encoding='utf-8')
            changed += 1
        files += 1
    return files, changed


def main():
    mapping = sorted(load_ports(), key=lambda item: len(item[0]), reverse=True)
    total_files = 0
    total_changed = 0
    for src, tgt in mapping:
        files, changed = normalize_target(tgt, mapping)
        total_files += files
        total_changed += changed
        print(f'normalized: {src} -> {tgt} (scanned {files}, changed {changed})')
    print(f'done: scanned={total_files}, changed={total_changed}')


if __name__ == '__main__':
    main()
