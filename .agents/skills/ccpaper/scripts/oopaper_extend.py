"""
[oopaper_extend.py]
서머리 파일의 외부 참고문헌을 스캔하여 미보유 논문을 자동으로 검색·다운로드합니다.

사용법:
    uv run python .agents/skills/ccpaper/scripts/oopaper_extend.py [--folder ID] [--dry-run] [--limit N] [--source all|arxiv|s2]
"""

import argparse
import fnmatch
import json
import re
import ssl
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

import certifi


def _glob_korean(folder: Path, pattern: str) -> list[Path]:
    """한글 포함 glob 패턴을 플랫폼(macOS NFD / Windows NFC) 무관하게 매칭."""
    if not folder.exists():
        return []
    nfc_pat = unicodedata.normalize('NFC', pattern)
    nfd_pat = unicodedata.normalize('NFD', pattern)
    matches = []
    for f in folder.iterdir():
        name = f.name
        nfc_name = unicodedata.normalize('NFC', name)
        nfd_name = unicodedata.normalize('NFD', name)
        if (fnmatch.fnmatch(nfc_name, nfc_pat) or
            fnmatch.fnmatch(nfd_name, nfd_pat) or
            fnmatch.fnmatch(nfc_name, nfd_pat) or
            fnmatch.fnmatch(nfd_name, nfc_pat)):
            matches.append(f)
    return matches

# scripts/ → ccpaper/ → skills/ → .codex/ → PROJECT_ROOT
# OAIS=03_paper/ 하위, 독립 프로젝트=루트 직하 양쪽 호환
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
PAPER_BASE = PROJECT_ROOT / "03_paper" if (PROJECT_ROOT / "03_paper").exists() else PROJECT_ROOT
PAPER_DIR = PAPER_BASE / "11_paper_en"
DOWN_DIR = PAPER_BASE / "00_down"
PAPER_LIST_FILE = PAPER_DIR / "paper_list.md"

# HTTP 요청 설정
REQUEST_TIMEOUT = 5       # API 요청 타임아웃 (초)
RATE_LIMIT_DELAY = 0.5    # 요청 간 딜레이 (초)
USER_AGENT = "Mozilla/5.0 (compatible; ccpaper-extend/1.0; academic research)"
_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


# ---------------------------------------------------------------------------
# 유틸리티 함수
# ---------------------------------------------------------------------------

def _http_get_json(url: str) -> dict | None:
    """JSON API를 GET 요청하고 파싱 결과를 반환합니다. 실패 시 None."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT, context=_SSL_CONTEXT) as resp:
            raw = resp.read()
            return json.loads(raw.decode("utf-8"))
    except Exception:
        return None


def _http_download_pdf(url: str, dest: Path) -> bool:
    """URL에서 PDF를 다운로드하여 dest에 저장합니다. 성공 여부 반환."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30, context=_SSL_CONTEXT) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "pdf" not in content_type.lower() and not url.lower().endswith(".pdf"):
                # Content-Type 검증: PDF가 아니면 거부
                return False
            data = resp.read()
            # 최소 크기 검증 (1KB 미만은 오류 페이지로 간주)
            if len(data) < 1024:
                return False
            # PDF 시그니처 검증
            if not data.startswith(b"%PDF"):
                return False
            dest.write_bytes(data)
            return True
    except Exception:
        return False


def _sanitize_filename(title: str) -> str:
    """파일명으로 사용 가능한 문자열로 변환합니다."""
    # 특수문자 제거, 공백→언더스코어
    name = re.sub(r'[\\/:*?"<>|]', '', title)
    name = re.sub(r'\s+', '_', name.strip())
    return name[:80]  # 최대 80자 제한


def _load_paper_list_titles() -> set:
    """paper_list.md에서 보유 논문 제목을 소문자 집합으로 반환합니다."""
    titles = set()
    if not PAPER_LIST_FILE.exists():
        return titles
    content = PAPER_LIST_FILE.read_text(encoding="utf-8")
    # 마크다운 테이블 행에서 첫 번째 셀(제목) 추출
    for line in content.split("\n"):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.split("|") if c.strip()]
        if not cells or cells[0] in ("#", "---", "버전", "제목", "Title"):
            continue
        if all(set(c) <= {"-", ":", " "} for c in cells):
            continue
        # 첫 번째 셀이 제목 (링크 형식 [제목](경로) 처리)
        title_cell = cells[0]
        link_match = re.search(r'\[([^\]]+)\]', title_cell)
        title = link_match.group(1) if link_match else title_cell
        titles.add(title.lower().strip())
    return titles


def _load_existing_summary_titles() -> set:
    """11_paper_en의 모든 서머리에서 논문 제목을 추출하여 소문자 집합으로 반환합니다."""
    titles = set()
    if not PAPER_DIR.exists():
        return titles
    for folder in PAPER_DIR.iterdir():
        if not folder.is_dir() or not re.match(r'\d{6}-\d{4}', folder.name):
            continue
        for f in _glob_korean(folder, "*_00_*서머리.md"):
            # 파일명에서 제목 추출: {CODE}_00_{Title}_서머리.md
            stem = f.stem  # 예: 260301_00_AttentionIsAllYouNeed_서머리
            parts = stem.split("_00_", 1)
            if len(parts) == 2:
                raw_title = parts[1].replace("_서머리", "").replace("_", " ")
                titles.add(raw_title.lower().strip())
    return titles


# ---------------------------------------------------------------------------
# 참고문헌 파싱
# ---------------------------------------------------------------------------

def _parse_fulltext_refs(fulltext_path: Path) -> list[dict]:
    """
    Phase 3 전문(영어) 파일의 ## References 섹션에서 참고문헌을 추출합니다.
    IEEE/학술 인용 형식: [N] Author, "Title," in *Venue*, Year.
    """
    refs = []
    try:
        content = fulltext_path.read_text(encoding="utf-8")
    except Exception:
        return refs

    # ## References 섹션 찾기 (다양한 헤딩 패턴)
    ref_match = re.search(
        r'^#{1,4}\s*(?:\d+\.)?\s*References?\s*$',
        content, re.MULTILINE | re.IGNORECASE
    )
    if ref_match:
        ref_block = content[ref_match.end():]
        next_sec = re.search(r'^#{1,4}\s+', ref_block, re.MULTILINE)
        if next_sec:
            ref_block = ref_block[:next_sec.start()]
    else:
        # 헤딩 없이 [1] 패턴으로 시작하는 참고문헌 블록 탐색
        bracket_matches = list(re.finditer(r'^\[1\]\s+\w', content, re.MULTILINE))
        if not bracket_matches:
            return refs
        # 마지막 [1] 출현 위치부터 (본문 끝의 References)
        ref_block = content[bracket_matches[-1].start():]

    source_folder = fulltext_path.parent.name

    # [N] 패턴으로 각 참고문헌 분리
    entries = re.split(r'\n\s*\[(\d+)\]\s*', ref_block)
    # entries[0]은 빈 문자열 또는 앞부분, 이후 (번호, 텍스트) 쌍
    for i in range(1, len(entries) - 1, 2):
        text = entries[i + 1].strip().replace("\n", " ")
        if not text:
            continue

        # 제목 추출: "Title" 또는 ``Title''
        title = ""
        title_match = re.search(r'["\u201c](.+?)["\u201d]', text)
        if title_match:
            title = _clean_text(title_match.group(1).strip().rstrip(",").strip())

        # 저자 추출: [N] 뒤 첫 번째 " 또는 제목 전까지
        author = ""
        if title_match:
            author = text[:title_match.start()].strip().rstrip(",").strip()

        # 연도 추출
        year = ""
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        if year_match:
            year = year_match.group(0)

        # arXiv ID 추출
        arxiv_id = ""
        arxiv_match = re.search(r'arXiv[:\s]*(\d{4}\.\d{4,5})', text, re.IGNORECASE)
        if arxiv_match:
            arxiv_id = arxiv_match.group(1)

        # DOI 추출
        doi = ""
        doi_match = re.search(r'(10\.\d{4,}/\S+)', text)
        if doi_match:
            doi = doi_match.group(1).rstrip(".,;)")

        if title:
            refs.append({
                "title": title, "author": author, "year": year,
                "doi": doi, "arxiv_id": arxiv_id, "source_folder": source_folder
            })

    return refs


def _parse_external_refs(summary_path: Path) -> list[dict]:
    """
    서머리 파일에서 ## 참고 논문 → ### 외부 섹션을 파싱합니다. (폴백용)

    반환: [{"title": str, "author": str, "year": str, "doi": str, "arxiv_id": str, "source_folder": str}, ...]
    """
    refs = []
    try:
        content = summary_path.read_text(encoding="utf-8")
    except Exception:
        return refs

    # ## 참고 논문 (References) 섹션 찾기
    ref_section_match = re.search(
        r'^##\s*(참고\s*논문|참고문헌)[^\n]*\n',
        content, re.MULTILINE | re.IGNORECASE
    )
    if not ref_section_match:
        return refs

    ref_start = ref_section_match.end()
    # 다음 ## 섹션 전까지만
    next_section = re.search(r'^##\s+', content[ref_start:], re.MULTILINE)
    ref_block = content[ref_start:ref_start + next_section.start()] if next_section else content[ref_start:]

    # ### 외부 섹션 찾기 (뒤에 "(미보유)" 등 부가 텍스트 허용)
    ext_match = re.search(r'^###\s*외부(?:\s*\([^)]*\))?\s*\n', ref_block, re.MULTILINE)
    if not ext_match:
        return refs

    ext_start = ext_match.end()
    # 다음 ### 섹션 전까지
    next_sub = re.search(r'^###\s+', ref_block[ext_start:], re.MULTILINE)
    ext_block = ref_block[ext_start:ext_start + next_sub.start()] if next_sub else ref_block[ext_start:]

    source_folder = summary_path.parent.name

    # 테이블 형식 감지: | # | 참고문헌 | DOI/arXiv | 링크 |
    table_match = re.search(r'\|.*참고문헌.*\|', ext_block)
    if table_match:
        refs.extend(_parse_table_refs(ext_block, source_folder))
    else:
        refs.extend(_parse_list_refs(ext_block, source_folder))

    return refs


def _extract_doi_arxiv(text: str) -> tuple[str, str]:
    """텍스트에서 DOI와 arXiv ID를 추출."""
    doi = ""
    arxiv_id = ""
    doi_match = re.search(r'DOI:\s*(10\.\S+)', text, re.IGNORECASE)
    if doi_match:
        doi = doi_match.group(1).rstrip("|").strip()
    arxiv_match = re.search(r'arXiv:\s*(\d{4}\.\d{4,5})', text, re.IGNORECASE)
    if arxiv_match:
        arxiv_id = arxiv_match.group(1)
    return doi, arxiv_id


def _parse_table_refs(ext_block: str, source_folder: str) -> list[dict]:
    """테이블 형식 참고문헌 파싱 (새 형식: DOI/arXiv 컬럼 포함)."""
    refs = []
    for line in ext_block.split("\n"):
        line = line.strip()
        if not line.startswith("|") or line.startswith("|---") or "참고문헌" in line or line.startswith("| #"):
            continue
        cells = [c.strip() for c in line.split("|")]
        cells = [c for c in cells if c]  # 빈 셀 제거
        if len(cells) < 2:
            continue
        # cells[0] = #, cells[1] = 참고문헌, cells[2] = DOI/arXiv (있으면), cells[3] = 링크 (있으면)
        ref_text = cells[1] if len(cells) > 1 else ""
        doi_arxiv_text = cells[2] if len(cells) > 2 else ""

        # 참고문헌 텍스트에서 저자/연도 추출
        title, author, year = _parse_ref_text(ref_text)
        doi, arxiv_id = _extract_doi_arxiv(doi_arxiv_text)

        if title:
            refs.append({"title": title, "author": author, "year": year,
                         "doi": doi, "arxiv_id": arxiv_id, "source_folder": source_folder})
    return refs


def _parse_list_refs(ext_block: str, source_folder: str) -> list[dict]:
    """리스트 형식 참고문헌 파싱 (기존 형식: - Title (Author Year))."""
    refs = []
    for line in ext_block.split("\n"):
        line = line.strip()
        if not line or not line.startswith("-"):
            continue

        raw = line.lstrip("- ").strip()
        # DOI/arXiv가 인라인에 있는 경우 추출
        doi, arxiv_id = _extract_doi_arxiv(raw)

        title, author, year = _parse_ref_text(raw)
        if title:
            refs.append({"title": title, "author": author, "year": year,
                         "doi": doi, "arxiv_id": arxiv_id, "source_folder": source_folder})
    return refs


def _parse_ref_text(text: str) -> tuple[str, str, str]:
    """참고문헌 텍스트에서 제목, 저자, 연도를 추출."""
    # 형식: Title (Author et al. Year) 또는 Author (Year). Title.
    title_match = re.match(r'^(.+?)\s*\(', text)
    if not title_match:
        # 괄호 없는 경우
        clean = re.sub(r'\[.*?\]', '', text).strip()
        return (clean, "", "") if clean and clean != "-" else ("", "", "")

    title = title_match.group(1).strip()
    author = ""
    year = ""

    paren_match = re.search(r'\(([^)]+)\)', text)
    if paren_match:
        paren_content = paren_match.group(1)
        year_match = re.search(r'\b(19|20)\d{2}\b', paren_content)
        if year_match:
            year = year_match.group(0)
            author = paren_content[:year_match.start()].strip().rstrip(",").strip()

    return (title, author, year)


# ---------------------------------------------------------------------------
# API 검색
# ---------------------------------------------------------------------------

_STOP_WORDS = {"a", "an", "the", "of", "for", "in", "on", "to", "and", "with", "by", "from", "at", "is", "are", "was", "were"}

def _clean_text(text: str) -> str:
    """PDF 추출 아티팩트 정리 (줄바꿈 하이픈, ligature 등)."""
    text = re.sub(r'(\w)- (\w)', r'\1\2', text)  # "regu- larization" → "regularization"
    text = text.replace('ﬁ', 'fi').replace('ﬂ', 'fl').replace('ﬀ', 'ff')
    text = text.replace('ﬃ', 'ffi').replace('ﬄ', 'ffl')
    return text


def _normalize_title(title: str) -> set[str]:
    """제목을 정규화하여 의미 단어 집합으로 변환."""
    clean = _clean_text(title.lower())
    clean = re.sub(r'[^\w\s]', ' ', clean)
    return {w for w in clean.split() if w and w not in _STOP_WORDS and len(w) > 1}


def _search_arxiv(title: str) -> dict | None:
    """
    arXiv API로 제목 검색합니다.
    반환: {"title": str, "pdf_url": str, "source": "arXiv"} 또는 None
    """
    # 핵심 단어만 추출하여 검색 (정확 매칭 대신 일반 검색)
    words = list(_normalize_title(title))[:8]
    query = "+AND+".join(f"ti:{urllib.parse.quote(w)}" for w in words)
    url = f"http://export.arxiv.org/api/query?search_query={query}&max_results=3"

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT, context=_SSL_CONTEXT) as resp:
            raw = resp.read().decode("utf-8")
    except Exception:
        return None

    # entry 블록 추출
    entries = re.findall(r'<entry>(.*?)</entry>', raw, re.DOTALL)
    if not entries:
        return None

    title_words = _normalize_title(title)

    for entry in entries:
        # 제목 추출
        title_match = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
        if not title_match:
            continue
        found_title = re.sub(r'\s+', ' ', title_match.group(1)).strip()

        # PDF 링크 추출: <link title="pdf" href="..."/>
        pdf_match = re.search(r'<link[^>]+title="pdf"[^>]+href="([^"]+)"', entry)
        if not pdf_match:
            id_match = re.search(r'<id>(http[^<]+)</id>', entry)
            if id_match:
                abs_url = id_match.group(1).strip()
                pdf_url = abs_url.replace("/abs/", "/pdf/") + ".pdf"
            else:
                continue
        else:
            pdf_url = pdf_match.group(1).strip()
            if not pdf_url.endswith(".pdf"):
                pdf_url += ".pdf"

        # 정규화된 제목 유사도 검증
        found_words = _normalize_title(found_title)
        overlap = len(title_words & found_words) / max(len(title_words), 1)
        if overlap >= 0.4:
            return {"title": found_title, "pdf_url": pdf_url, "source": "arXiv"}

    return None


def _search_semantic_scholar_by_doi(doi: str) -> dict | None:
    """DOI로 Semantic Scholar에서 직접 조회하여 오픈액세스 PDF를 찾습니다."""
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,openAccessPdf,externalIds"
    data = _http_get_json(url)
    if not data:
        return None
    oa = data.get("openAccessPdf")
    if oa and oa.get("url"):
        ext_ids = data.get("externalIds", {})
        arxiv_id = ext_ids.get("ArXiv", "")
        source = f"S2(DOI)" if not arxiv_id else f"S2(arXiv)"
        return {"title": data.get("title", ""), "pdf_url": oa["url"], "source": source}
    return None


def _search_semantic_scholar(title: str) -> dict | None:
    """
    Semantic Scholar API로 제목 검색합니다.
    반환: {"title": str, "pdf_url": str, "source": "S2"} 또는 None
    """
    encoded = urllib.parse.quote(title)
    url = (
        f"https://api.semanticscholar.org/graph/v1/paper/search"
        f"?query={encoded}&limit=3&fields=title,externalIds,openAccessPdf"
    )
    data = _http_get_json(url)
    if not data:
        return None

    papers = data.get("data", [])
    if not papers:
        return None

    title_words = _normalize_title(title)

    for paper in papers:
        found_title = paper.get("title", "")
        found_words = _normalize_title(found_title)
        overlap = len(title_words & found_words) / max(len(title_words), 1)
        if overlap < 0.4:
            continue

        # openAccessPdf 확인
        oa_pdf = paper.get("openAccessPdf")
        if oa_pdf and oa_pdf.get("url"):
            return {"title": found_title, "pdf_url": oa_pdf["url"], "source": "S2"}

        # arXiv ID가 있으면 PDF URL 생성
        ext_ids = paper.get("externalIds", {})
        arxiv_id = ext_ids.get("ArXiv")
        if arxiv_id:
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            return {"title": found_title, "pdf_url": pdf_url, "source": "S2(arXiv)"}

    return None


# ---------------------------------------------------------------------------
# 메인 로직
# ---------------------------------------------------------------------------

def do_extend(args):
    """외부 참고문헌 스캔 → 검색 → 다운로드 실행."""
    sys.stdout.reconfigure(encoding="utf-8")
    print("# ccpaper extend - 참고문헌 확장 수집\n", flush=True)
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", flush=True)

    if not PAPER_DIR.exists():
        print(f"오류: 논문 디렉터리 없음 ({PAPER_DIR})", flush=True)
        sys.exit(1)

    # --- 1. 스캔 대상 결정 ---
    if args.folder:
        target_folders = [PAPER_DIR / args.folder]
        scan_label = f"폴더 {args.folder}"
    else:
        target_folders = sorted([
            d for d in PAPER_DIR.iterdir()
            if d.is_dir() and re.match(r'\d{6}-\d{4}', d.name)
        ])
        scan_label = "전체"

    print(f"스캔 대상: {len(target_folders)}개 서머리 ({scan_label})\n", flush=True)

    # --- 2. 참고문헌 추출 (Phase 3 전문 우선, 서머리 폴백) ---
    all_refs: list[dict] = []
    fulltext_count = 0
    summary_count = 0
    for folder in target_folders:
        # Phase 3 전문(영어) 파일 우선
        fulltext_files = _glob_korean(folder, "*_03_*전문*영어*.md")
        if fulltext_files:
            refs = _parse_fulltext_refs(fulltext_files[0])
            if refs:
                all_refs.extend(refs)
                fulltext_count += 1
                continue
        # 폴백: 서머리의 외부 참고문헌
        summary_files = _glob_korean(folder, "*_00_*서머리.md")
        if summary_files:
            refs = _parse_external_refs(summary_files[0])
            if refs:
                all_refs.extend(refs)
                summary_count += 1

    print(f"참고문헌 소스: Phase 3 전문 {fulltext_count}건, 서머리 폴백 {summary_count}건\n", flush=True)

    print(f"## 추출된 외부 참고문헌: {len(all_refs)}건\n", flush=True)
    if all_refs:
        print("| # | 제목 | 저자 | 연도 | 출처 서머리 |")
        print("|---|------|------|------|------------|")
        for i, r in enumerate(all_refs, 1):
            title_short = r["title"][:50] + ("..." if len(r["title"]) > 50 else "")
            print(f"| {i} | {title_short} | {r['author'][:20]} | {r['year']} | {r['source_folder']} |")
        print("", flush=True)

    if not all_refs:
        print("추출된 외부 참고문헌이 없습니다.", flush=True)
        return

    # --- 3. 중복 제거 ---
    # 3a. paper_list.md 보유 논문 제목
    owned_titles = _load_paper_list_titles()
    # 3b. 서머리 파일명 기반 제목
    summary_titles = _load_existing_summary_titles()
    all_known = owned_titles | summary_titles

    # 3c. 이번 배치 내 중복 제거 (같은 제목 여러 서머리에 등장)
    seen_titles: set = set()
    already_owned = 0
    deduplicated: list[dict] = []

    for ref in all_refs:
        key = ref["title"].lower().strip()
        if key in all_known:
            already_owned += 1
            continue
        if key in seen_titles:
            continue
        seen_titles.add(key)
        deduplicated.append(ref)

    print(f"## 이미 보유: {already_owned}건", flush=True)
    print(f"## 중복 제거 후 검색 대상: {len(deduplicated)}건\n", flush=True)

    if not deduplicated:
        print("검색 대상이 없습니다.", flush=True)
        return

    # --- 4. 검색 및 다운로드 ---
    search_targets = deduplicated[:args.limit] if args.limit else deduplicated
    if len(search_targets) < len(deduplicated):
        print(f"(--limit {args.limit} 적용: {len(deduplicated)}건 중 {len(search_targets)}건만 처리)\n", flush=True)

    DOWN_DIR.mkdir(parents=True, exist_ok=True)

    print("## 검색 결과\n", flush=True)
    print("| # | 제목 | 소스 | 다운로드 | 상태 |")
    print("|---|------|------|---------|------|")

    total_ok = 0
    total_fail = 0

    total_n = len(search_targets)
    for i, ref in enumerate(search_targets, 1):
        title = ref["title"]
        title_short = title[:45] + ("..." if len(title) > 45 else "")
        print(f"[{i}/{total_n}] {title_short}", file=sys.stderr, flush=True)
        doi = ref.get("doi", "")
        arxiv_id = ref.get("arxiv_id", "")

        # DOI/arXiv ID가 있으면 직접 다운로드 시도 (검색 스킵)
        found = None

        if arxiv_id:
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            found = {"title": title, "pdf_url": pdf_url, "source": f"arXiv({arxiv_id})"}

        if found is None and doi:
            # Semantic Scholar DOI 직접 조회
            time.sleep(RATE_LIMIT_DELAY)
            found = _search_semantic_scholar_by_doi(doi)

        # ID가 없으면 제목 기반 검색 (기존 로직)
        if found is None and args.source in ("all", "arxiv"):
            time.sleep(RATE_LIMIT_DELAY)
            found = _search_arxiv(title)

        if found is None and args.source in ("all", "s2"):
            time.sleep(RATE_LIMIT_DELAY)
            found = _search_semantic_scholar(title)

        if found is None:
            print(f"| {i} | {title_short} | - | 미발견 | - |")
            total_fail += 1
            continue

        source = found["source"]
        pdf_url = found["pdf_url"]

        if args.dry_run:
            print(f"| {i} | {title_short} | {source} | [DRY] | {pdf_url[:60]} |")
            total_ok += 1
            continue

        # 다운로드
        safe_name = _sanitize_filename(title)
        dest = DOWN_DIR / f"{safe_name}.pdf"

        # 파일명 충돌 방지
        if dest.exists():
            dest = DOWN_DIR / f"{safe_name}_{int(time.time())}.pdf"

        time.sleep(RATE_LIMIT_DELAY)
        success = _http_download_pdf(pdf_url, dest)

        if success:
            rel_path = f"03_paper/00_down/{dest.name}"
            print(f"| {i} | {title_short} | {source} | OK | {rel_path} |")
            total_ok += 1
        else:
            print(f"| {i} | {title_short} | {source} | 실패 | {pdf_url[:50]} |")
            total_fail += 1

    # --- 5. 요약 ---
    print("\n## 요약", flush=True)
    dry_note = " (dry-run)" if args.dry_run else ""
    print(
        f"- 추출: {len(all_refs)}건 → 신규: {len(deduplicated)}건 "
        f"→ 다운로드 성공: {total_ok}건{dry_note}",
        flush=True
    )
    if total_fail > 0:
        print(f"- 미발견/실패: {total_fail}건", flush=True)


def main():
    """CLI 진입점."""
    parser = argparse.ArgumentParser(
        description="ccpaper extend - 서머리 외부 참고문헌 검색·다운로드"
    )
    parser.add_argument("--folder", type=str, help="특정 폴더만 처리 (YYMMDD-HHMM)")
    parser.add_argument("--dry-run", action="store_true", help="검색만 수행, 다운로드 생략")
    parser.add_argument("--limit", type=int, default=10, help="최대 다운로드 수 (기본: 10)")
    parser.add_argument(
        "--source",
        choices=["all", "arxiv", "s2"],
        default="all",
        help="검색 소스 (기본: all)",
    )
    args = parser.parse_args()
    do_extend(args)


if __name__ == "__main__":
    main()
