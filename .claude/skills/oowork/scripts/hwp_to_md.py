"""hwp_to_md.py - HWP/HWPX → 구조화된 마크다운 변환 스크립트

사용법:
    uv run python .claude/skills/oowork/scripts/hwp_to_md.py <입력파일> [출력파일]

입력: .hwp 또는 .hwpx 파일
출력: 구조화된 마크다운 (.md) 파일
    - 출력 파일 미지정 시 넘버링 +1 규칙 적용 (예: 10_양식.hwp → 11_양식.md)

변환 파이프라인 (기본):
    HWP → pyhwpx로 HWPX 변환 → pyhwpx로 PDF 변환 → pdfplumber → .md
    HWPX → pyhwpx로 PDF 변환 → pdfplumber → .md
폴백 (PDF 변환 실패 시):
    HWPX → zipfile 해제 → xml.etree 파싱 → .md
"""

import glob
import os
import re
import sys
import zipfile
from xml.etree import ElementTree as ET


# --- 유틸리티 함수 ---


def tag_name(elem):
    """XML 요소에서 네임스페이스 제거한 태그명 반환"""
    return elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag


def get_text(elem):
    """요소 내 모든 <t> 태그 텍스트 결합"""
    texts = []
    for e in elem.iter():
        if tag_name(e) == "t" and e.text:
            texts.append(e.text)
    return "".join(texts).strip()


def normalize_spaces(text):
    """한글 사이 다중 공백 제거: '기  업  체' → '기 업 체'"""
    for _ in range(3):
        text = re.sub(
            r"([\uAC00-\uD7A3])\s{2,}([\uAC00-\uD7A3])", r"\1 \2", text
        )
    return text.strip()


def convert_section_markers(text):
    """HWP 섹션 마커를 원숫자로 변환"""
    markers = {
        "\U000f02b1": "①",
        "\U000f02b2": "②",
        "\U000f02b3": "③",
        "\U000f02b4": "④",
        "\U000f02b5": "⑤",
        "\U000f02b6": "⑥",
        "\U000f02b7": "⑦",
        "\U000f02b8": "⑧",
        "\U000f02b9": "⑨",
    }
    for k, v in markers.items():
        text = text.replace(k, v)
    return text


def clean_text(text):
    """텍스트 정규화 + 마커 변환"""
    return convert_section_markers(normalize_spaces(text))


def is_empty_row(cells):
    """모든 셀이 비어있는 행인지"""
    return all(not c.strip() for c in cells)


# --- HWP → HWPX 변환 ---


def convert_hwp_to_hwpx(hwp_path):
    """pyhwpx COM 자동화로 HWP → HWPX 변환"""
    hwpx_path = hwp_path.replace(".hwp", ".hwpx")
    if os.path.exists(hwpx_path):
        return hwpx_path

    try:
        import pyhwpx

        hwp = pyhwpx.Hwp(visible=False)
        hwp.open(os.path.abspath(hwp_path))
        hwp.save_as(os.path.abspath(hwpx_path), "HWPX")
        hwp.quit()
    except Exception as e:
        print(f"HWP→HWPX 변환 실패: {e}", file=sys.stderr)
        sys.exit(1)

    return hwpx_path


def convert_hwpx_to_pdf(hwpx_path):
    """pyhwpx COM 자동화로 HWPX → PDF 변환"""
    pdf_path = os.path.splitext(hwpx_path)[0] + ".pdf"
    if os.path.exists(pdf_path):
        return pdf_path

    try:
        import pyhwpx

        hwp = pyhwpx.Hwp(visible=False)
        hwp.open(os.path.abspath(hwpx_path))
        hwp.save_as(os.path.abspath(pdf_path), "PDF")
        hwp.quit()
    except Exception as e:
        print(f"HWPX→PDF 변환 실패: {e}", file=sys.stderr)
        return None

    return pdf_path


def pdf_to_md(pdf_path):
    """pdfplumber로 PDF → 구조화 마크다운 변환"""
    import pdfplumber

    md_lines = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            # 표 추출
            tables = page.extract_tables()
            table_bboxes = []
            if tables:
                for table_obj in page.find_tables():
                    table_bboxes.append(table_obj.bbox)

            # 표 → 마크다운 테이블
            for table in tables:
                if not table or not table[0]:
                    continue
                # 빈 행 제거
                rows = [r for r in table if any(c and c.strip() for c in r)]
                if not rows:
                    continue

                max_cols = max(len(r) for r in rows)
                cleaned = []
                for row in rows:
                    cells = []
                    for c in row:
                        cell = (c or "").replace("\n", " ").replace("|", "/").strip()
                        cell = clean_text(cell)
                        cells.append(cell)
                    while len(cells) < max_cols:
                        cells.append("")
                    cleaned.append(cells)

                md_lines.append("")
                md_lines.append("| " + " | ".join(cleaned[0]) + " |")
                md_lines.append("|" + "|".join(["---"] * max_cols) + "|")
                for row in cleaned[1:]:
                    md_lines.append("| " + " | ".join(row) + " |")
                md_lines.append("")

            # 본문 텍스트 (표 영역 제외)
            text = page.extract_text()
            if text:
                for line in text.split("\n"):
                    line = clean_text(line)
                    if not line:
                        continue
                    # 표에 이미 포함된 텍스트 중복 방지 (짧은 행은 스킵)
                    if tables and len(line) < 40:
                        skip = False
                        for table in tables:
                            for row in table:
                                if row and any(
                                    line in (c or "") for c in row
                                ):
                                    skip = True
                                    break
                            if skip:
                                break
                        if skip:
                            continue
                    md_lines.append(line)

            # 페이지 구분 (마지막 페이지 제외)
            if i < len(pdf.pages) - 1:
                md_lines.append("")

    result = "\n".join(md_lines)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result


# --- 표 파싱 ---


def extract_table_full_text(tbl):
    """표의 모든 텍스트를 순서대로 추출"""
    texts = []
    for tr in tbl:
        if tag_name(tr) != "tr":
            continue
        for tc in tr:
            if tag_name(tc) != "tc":
                continue
            t = get_text(tc)
            if t:
                texts.append(t)
    return " ".join(texts)


def is_single_mega_cell(tbl):
    """1행1셀이고 내용이 긴 표 (표지 등)"""
    trs = [e for e in tbl if tag_name(e) == "tr"]
    if len(trs) == 1:
        tcs = [e for e in trs[0] if tag_name(e) == "tc"]
        if len(tcs) == 1:
            return len(get_text(tcs[0])) > 100
    return False


def format_announcement_text(text):
    """안내말씀 등 긴 텍스트를 구조화된 마크다운으로 변환"""
    text = clean_text(text)
    result = []

    if "< 안내 말씀 >" in text:
        parts = text.split("< 안내 말씀 >")
        if parts[0].strip():
            result.append(parts[0].strip())
        text = "< 안내 말씀 >" + (parts[1] if len(parts) > 1 else "")

    # ◈ 단위로 분리
    segments = re.split(r"(◈[^◈]+?)(?=◈|$)", text)

    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        if seg.startswith("< 안내"):
            result.append(f"\n### {seg}\n")
        elif seg.startswith("◈"):
            result.append(f"\n**{seg.strip()}**\n")
        elif seg.startswith("‣") or seg.startswith("•"):
            result.append(f"- {seg[1:].strip()}")
        else:
            sub_parts = re.split(r"(?=‣)", seg)
            for sp in sub_parts:
                sp = sp.strip()
                if sp.startswith("‣"):
                    result.append(f"- {sp[1:].strip()}")
                elif sp:
                    result.append(sp)

    return "\n".join(result) if result else text


def classify_header(text):
    """텍스트를 헤더 레벨로 분류"""
    if text.startswith("[별지"):
        return 1
    keywords_h2 = [
        "기업체 개요",
        "대표자 등 및 경영진",
        "매출현황 및 영업현황",
        "기술 사업 계획",
        "기술사업계획",
        "매출현황 및 영업현황(건설업)",
    ]
    if any(k in text for k in keywords_h2):
        return 2
    return 3


def parse_table(tbl):
    """표를 마크다운으로 변환. 반환: (type, content) 또는 None"""
    trs = [e for e in tbl if tag_name(e) == "tr"]
    if not trs:
        return None

    # 1행1셀 mega cell → 스킵
    if is_single_mega_cell(tbl):
        return ("skip", "")

    rows = []
    for tr in trs:
        tcs = [e for e in tr if tag_name(e) == "tc"]
        cells = []
        for tc in tcs:
            cell_text = get_text(tc).replace("\n", " ").replace("|", "/").strip()
            cell_text = clean_text(cell_text)
            if len(cell_text) > 80:
                cell_text = cell_text[:77] + "..."
            cells.append(cell_text)
        if cells:
            rows.append(cells)

    if not rows:
        return None

    # 1행 1셀, 짧은 텍스트 → 헤더
    if len(rows) == 1 and len(rows[0]) == 1:
        text = rows[0][0]
        if len(text) < 60:
            return ("header", text)

    # 안내말씀 포함 → 텍스트로 변환
    full = extract_table_full_text(tbl)
    if ("안내 말씀" in full or "윤리경영" in full) and len(full) > 200:
        return ("announcement", format_announcement_text(full))

    # 빈 행 제거 (헤더행은 유지)
    filtered = [rows[0]]
    for row in rows[1:]:
        if not is_empty_row(row):
            filtered.append(row)
    rows = filtered

    if not rows:
        return None

    # 열 수 통일
    max_cols = max(len(r) for r in rows)
    if max_cols == 0:
        return None
    for r in rows:
        while len(r) < max_cols:
            r.append("")

    # 마크다운 테이블
    lines = []
    lines.append("| " + " | ".join(rows[0]) + " |")
    lines.append("|" + "|".join(["---"] * max_cols) + "|")
    for row in rows[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return ("table", "\n".join(lines))


# --- HWPX → 마크다운 ---


def hwpx_to_md(hwpx_path):
    """HWPX 파일을 구조화된 마크다운으로 변환"""
    with zipfile.ZipFile(hwpx_path) as z:
        sections = sorted(
            [n for n in z.namelist() if "section" in n.lower() and n.endswith(".xml")]
        )
        if not sections:
            print("섹션 XML을 찾을 수 없습니다.", file=sys.stderr)
            sys.exit(1)

        md_lines = []

        for sec_file in sections:
            data = z.read(sec_file).decode("utf-8")
            root = ET.fromstring(data)

            for child in root:
                if tag_name(child) != "p":
                    continue

                # p 안에서 tbl 찾기
                has_table = False
                for sub in child.iter():
                    if tag_name(sub) == "tbl":
                        has_table = True
                        result = parse_table(sub)
                        if not result:
                            continue
                        item_type, content = result
                        if item_type == "skip":
                            continue
                        elif item_type == "header":
                            level = classify_header(content)
                            md_lines.append(f'\n{"#" * level} {content}\n')
                        elif item_type == "announcement":
                            md_lines.append(content)
                        elif item_type == "table":
                            md_lines.append("\n" + content + "\n")

                if not has_table:
                    text = clean_text(get_text(child))
                    if text:
                        if text.startswith("[별지"):
                            md_lines.append(f"\n# {text}\n")
                        elif text.startswith("※"):
                            md_lines.append(f"> {text}")
                        elif text.startswith("◈"):
                            md_lines.append(f"\n**{text}**\n")
                        else:
                            md_lines.append(text)

    result = "\n".join(md_lines)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result


# --- 출력 파일명 결정 ---


def resolve_output_path(input_path, output_path=None):
    """넘버링 +1 규칙으로 출력 파일명 결정"""
    if output_path:
        return output_path

    dirname = os.path.dirname(input_path)
    basename = os.path.basename(input_path)

    # 확장자 제거
    name_no_ext = os.path.splitext(basename)[0]

    # 넘버링 추출: "10_기술사업계획서" → (10, "기술사업계획서")
    match = re.match(r"^(\d+)_(.+)$", name_no_ext)
    if match:
        num = int(match.group(1)) + 1
        name = match.group(2)
        out_name = f"{num}_{name}.md"
    else:
        # 넘버링 없는 경우: 폴더 내 기존 파일 최대 번호 + 1
        existing = glob.glob(os.path.join(dirname, "[0-9]*_*.md"))
        max_num = 10
        for f in existing:
            m = re.match(r"^(\d+)_", os.path.basename(f))
            if m:
                max_num = max(max_num, int(m.group(1)))
        out_name = f"{max_num + 1}_{name_no_ext}.md"

    return os.path.join(dirname, out_name)


# --- 메인 ---


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("help", "--help", "-h"):
        print("hwp_to_md.py - HWP/HWPX → 구조화된 마크다운 변환")
        print()
        print("사용법:")
        print("  hwp_to_md.py <입력.hwp|hwpx> [출력.md]")
        print()
        print("예시:")
        print("  hwp_to_md.py 10_양식.hwp              → 11_양식.md")
        print("  hwp_to_md.py 10_양식.hwp output.md     → output.md")
        print("  hwp_to_md.py 10_양식.hwpx              → 11_양식.md")
        return

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(input_path):
        print(f"파일 없음: {input_path}", file=sys.stderr)
        sys.exit(1)

    ext = os.path.splitext(input_path)[1].lower()

    # HWP → HWPX 변환
    if ext == ".hwp":
        print(f"HWP→HWPX 변환 중...")
        hwpx_path = convert_hwp_to_hwpx(input_path)
        print(f"  HWPX: {hwpx_path}")
    elif ext == ".hwpx":
        hwpx_path = input_path
    else:
        print(f"지원하지 않는 형식: {ext} (.hwp, .hwpx만 지원)", file=sys.stderr)
        sys.exit(1)

    # 기본: HWPX → PDF → MD (pdfplumber)
    md_content = None
    print(f"HWPX→PDF 변환 중...")
    pdf_path = convert_hwpx_to_pdf(hwpx_path)
    if pdf_path:
        print(f"  PDF: {pdf_path}")
        try:
            print(f"PDF→MD 변환 중 (pdfplumber)...")
            md_content = pdf_to_md(pdf_path)
        except Exception as e:
            print(f"  PDF→MD 실패: {e}, XML 폴백 시도", file=sys.stderr)

    # 폴백: HWPX → MD (XML 파싱)
    if not md_content:
        print(f"HWPX→MD 변환 중 (XML 폴백)...")
        md_content = hwpx_to_md(hwpx_path)

    # 출력
    out_path = resolve_output_path(input_path, output_path)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"  완료: {len(md_content)} chars → {out_path}")


if __name__ == "__main__":
    main()
