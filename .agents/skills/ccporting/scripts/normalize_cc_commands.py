import json
import re
from pathlib import Path

ROOT = Path('.').resolve()
MANIFEST = ROOT / '.agents' / 'skills' / 'ccporting_manifest_all.json'
TARGET_ROOT = ROOT / '.agents' / 'skills'


def load_ports():
    data = json.loads(MANIFEST.read_text(encoding='utf-8'))
    return [(p['source'].split('/')[-1], p['target']) for p in data.get('ports', [])]


def replace_text(text: str, src: str, tgt: str) -> str:
    out = text
    out = re.sub(rf'\b{re.escape(src)}\b', tgt, out)
    # command variants like `oohelp` etc in generic lines
    if src.startswith('oo') and tgt.startswith('cc'):
        out = re.sub(rf'\b{re.escape(src)}\b', tgt, out)
    return out


def normalize_target(src: str, tgt: str) -> tuple[int, int]:
    base = TARGET_ROOT / tgt
    changed = 0
    files = 0
    for p in [base / 'SKILL.md', *list((base / 'scripts').rglob('*.py'))]:
        if not p.exists() or 'upstream' in p.parts:
            continue
        old = p.read_text(encoding='utf-8', errors='ignore')
        new = replace_text(old, src, tgt)
        if new != old:
            p.write_text(new, encoding='utf-8')
            changed += 1
        files += 1
    return files, changed


def main():
    total_files = 0
    total_changed = 0
    for src, tgt in load_ports():
        files, changed = normalize_target(src, tgt)
        total_files += files
        total_changed += changed
        print(f'normalized: {src} -> {tgt} (scanned {files}, changed {changed})')
    print(f'done: scanned={total_files}, changed={total_changed}')


if __name__ == '__main__':
    main()
