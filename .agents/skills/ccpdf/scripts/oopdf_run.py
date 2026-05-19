"""ccpdf - PDF 변환/처리 스킬 (MD→PDF, PDF→Image)"""
import subprocess
import sys
import sys as _sys
if _sys.stdout.encoding and _sys.stdout.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stdout.reconfigure(encoding='utf-8')
if _sys.stderr.encoding and _sys.stderr.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
    _sys.stderr.reconfigure(encoding='utf-8')

# --- oo_common inline ---
from pathlib import Path
import re as _re
_SKILLS_DIR = Path(__file__).parent.parent.parent

def _print_skill_help(skill_name):
    if sys.stdout.encoding and sys.stdout.encoding.lower() in ('cp949', 'cp1252', 'ascii'):
        sys.stdout.reconfigure(encoding='utf-8')
    _sf = _SKILLS_DIR / skill_name / "SKILL.md"
    if not _sf.exists():
        print(f"[ERROR] .agents/skills/{skill_name}/SKILL.md not found")
        return
    _c = _sf.read_text(encoding="utf-8")
    _m = _re.search(r"##[^\n]*(?:서브명령어|명령어)\n\n((?:\|.+\n)+)", _c)
    if _m:
        print(f"`{skill_name} help` 서브명령어 목록:\n")
        print(_m.group(1).strip())
    else:
        print(f"[WARN] 서브명령어 섹션 없음: {skill_name}/SKILL.md")

def cmd_show_checklist():
    """references/checklist.md 내용 출력"""
    checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
    if not checklist_path.exists():
        print(f"[ccpdf] checklist.md 없음: {checklist_path}")
        return
    print(checklist_path.read_text(encoding="utf-8"))

def show_help_if_no_args(skill_name, args):
    if not args or args[0].lower() in ("help", "-h", "--help"):
        _print_skill_help(skill_name)
        return True
    return False
# --- end oo_common inline ---
import argparse
from pathlib import Path


def convert_md_to_pdf(input_path: str, output_path: str, css_path: str = None):
    """Convert markdown to PDF using markdown + weasyprint"""
    try:
        import markdown
        from weasyprint import HTML, CSS
    except ImportError:
        print('weasyprint가 설치되어 있지 않습니다.')
        print('설치: uv pip install markdown weasyprint')
        sys.exit(1)

    with open(input_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'codehilite']
    )

    if css_path:
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
    else:
        css_content = """
            body {
                font-family: 'Malgun Gothic', sans-serif;
                font-size: 11pt;
                line-height: 1.6;
                margin: 2cm;
            }
            h1 { font-size: 18pt; margin-top: 1em; }
            h2 { font-size: 14pt; margin-top: 0.8em; }
            h3 { font-size: 12pt; margin-top: 0.6em; }
            code {
                font-family: Consolas, monospace;
                font-size: 9pt;
                background-color: #f4f4f4;
                padding: 2px 4px;
            }
            pre {
                background-color: #f4f4f4;
                padding: 10px;
                overflow-x: auto;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 1em 0;
            }
            th, td {
                border: 1px solid #000;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f0f0f0;
                font-weight: bold;
            }
            blockquote {
                margin-left: 1em;
                padding-left: 1em;
                border-left: 3px solid #ccc;
                color: #666;
            }
        """

    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>{css_content}</style>
</head>
<body>
    {html_content}
</body>
</html>"""

    HTML(string=full_html).write_pdf(output_path)
    print(f'PDF 생성 완료: {output_path}')


def convert_with_pandoc(input_path: str, output_path: str):
    """Convert markdown to PDF using pandoc (supports LaTeX math + mermaid)"""
    import os

    engines = ['xelatex', 'pdflatex', 'lualatex', 'wkhtmltopdf']

    for engine in engines:
        cmd = ['pandoc', input_path, '-o', output_path, f'--pdf-engine={engine}']
        if engine == 'xelatex':
            cmd.extend(['-V', 'mainfont=Malgun Gothic'])
        cmd.extend(['-V', 'geometry:margin=2cm'])

        result = subprocess.run(cmd, capture_output=True)
        if result.returncode == 0 and os.path.exists(output_path):
            print(f'PDF 생성 완료 (pandoc/{engine}): {output_path}')
            return

    print('PDF 엔진을 찾을 수 없습니다.')
    print('다음 중 하나를 설치해주세요: xelatex, pdflatex, wkhtmltopdf')
    sys.exit(1)


def convert_pdf_to_images(input_path: str, output_dir: str = None, dpi: int = 200, fmt: str = 'png'):
    """Convert PDF pages to images using PyMuPDF"""
    try:
        import fitz
    except ImportError:
        print('PyMuPDF가 설치되어 있지 않습니다.')
        print('설치: uv pip install pymupdf')
        sys.exit(1)

    input_p = Path(input_path)
    if not input_p.exists():
        print(f'파일을 찾을 수 없습니다: {input_path}')
        sys.exit(1)

    out_dir = Path(output_dir) if output_dir else input_p.parent / input_p.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(input_path)
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    pad = 3 if len(doc) >= 100 else 2

    total = len(doc)
    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=matrix)
        out_file = out_dir / f'{input_p.stem}_{i + 1:0{pad}d}.{fmt}'
        pix.save(str(out_file))
        print(f'  [{i + 1}/{total}] {out_file.name}')

    doc.close()
    print(f'이미지 변환 완료: {total} 페이지 → {out_dir}')


def check_dependencies():
    """의존성 설치 상태 확인"""
    print('[ccpdf check] 의존성 상태')
    items = [
        ('markdown', 'uv pip install markdown'),
        ('weasyprint', 'uv pip install weasyprint'),
        ('fitz', 'uv pip install pymupdf'),
    ]
    for pkg, install_cmd in items:
        try:
            __import__(pkg)
            print(f'  [OK] {pkg}')
        except ImportError:
            print(f'  [MISS] {pkg}  →  {install_cmd}')

    # pandoc
    result = subprocess.run(['pandoc', '--version'], capture_output=True)
    if result.returncode == 0:
        version = result.stdout.decode().split('\n')[0]
        print(f'  [OK] pandoc ({version})')
    else:
        print('  [MISS] pandoc  →  https://pandoc.org/installing.html')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ccpdf - Markdown to PDF converter')
    subparsers = parser.add_subparsers(dest='command')

    # run
    run_parser = subparsers.add_parser('run', help='MD → PDF 변환')
    run_parser.add_argument('input_file', help='입력 Markdown 파일')
    run_parser.add_argument('--pandoc', action='store_true', help='pandoc 엔진 사용')
    run_parser.add_argument('--output', help='출력 파일 경로')
    run_parser.add_argument('--style', help='커스텀 CSS 파일 경로')

    # convert
    convert_parser = subparsers.add_parser('convert', help='PDF 변환 (이미지 등)')
    convert_parser.add_argument('input_file', help='입력 PDF 파일')
    convert_parser.add_argument('--image', action='store_true', default=True, help='PDF → 이미지 변환 (기본)')
    convert_parser.add_argument('--output', help='출력 디렉토리 경로')
    convert_parser.add_argument('--dpi', type=int, default=200, help='해상도 (기본: 200)')
    convert_parser.add_argument('--format', dest='fmt', default='png', choices=['png', 'jpg'], help='이미지 포맷 (기본: png)')

    # check
    subparsers.add_parser('check', help='의존성 상태 확인')

    if len(sys.argv) > 2 and sys.argv[1].lower() == "show" and sys.argv[2].lower() == "checklist":
        cmd_show_checklist()
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] in ("help", "-h", "--help"):
        _print_skill_help("ccpdf")
        sys.exit(0)

    args = parser.parse_args()

    if args.command == 'check':
        check_dependencies()
    elif args.command == 'run':
        output = args.output or str(Path(args.input_file).with_suffix('.pdf'))
        if args.pandoc:
            convert_with_pandoc(args.input_file, output)
        else:
            convert_md_to_pdf(args.input_file, output, args.style)
    elif args.command == 'convert':
        convert_pdf_to_images(args.input_file, args.output, args.dpi, args.fmt)
    else:
        parser.print_help()
