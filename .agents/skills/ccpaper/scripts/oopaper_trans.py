#!/usr/bin/env python3
"""
oopaper_trans.py

PDF 텍스트 추출 및 번역 스크립트
- PDF에서 영문 전문 추출
- 영문 전문에서 한글 번역 생성
"""

import argparse
import re
import sys
import time
from pathlib import Path
from datetime import datetime
import PyPDF2

# 경로 설정 (OAIS=03_paper/ 하위, 독립 프로젝트=루트 직하 양쪽 호환)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
PAPER_BASE = PROJECT_ROOT / "03_paper" if (PROJECT_ROOT / "03_paper").exists() else PROJECT_ROOT
PAPER_DIR = PAPER_BASE / "11_paper_en"
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

# Gemma 서버 (mlx-lm)
GEMMA_BASE_URL = "http://localhost:8080/v1"
GEMMA_MODEL = "gemma4:26b"


def _load_template(name: str) -> str | None:
    """templates/*.md 파일 로드."""
    p = TEMPLATES_DIR / name
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8")


def _safe_format(template: str, vars: dict) -> str:
    """템플릿 변수 치환 (없는 변수는 빈 문자열)."""
    class _SafeDict(dict):
        def __missing__(self, k):
            return ""
    return template.format_map(_SafeDict(**vars))


def _check_gemma_available() -> bool:
    """Gemma 서버 가용성 체크."""
    try:
        from openai import OpenAI
        client = OpenAI(base_url=GEMMA_BASE_URL, api_key="local", timeout=3.0)
        client.models.list()
        return True
    except Exception:
        return False


def _gemma_translate(text: str, max_chunk: int = 3000) -> str | None:
    """Gemma로 영문 → 한글 번역. 긴 텍스트는 chunking."""
    try:
        from openai import OpenAI
        client = OpenAI(base_url=GEMMA_BASE_URL, api_key="local")
    except Exception as e:
        print(f"[Gemma] 클라이언트 생성 실패: {e}", file=sys.stderr)
        return None

    # chunking: paragraph 우선, 너무 길면 강제 char-split
    def _split_by_chars(s: str, n: int) -> list:
        return [s[i:i+n] for i in range(0, len(s), n)]

    chunks = []
    cur = ""
    for para in text.split("\n\n"):
        # 단일 paragraph가 max를 초과하면 강제 분할
        if len(para) > max_chunk:
            if cur:
                chunks.append(cur)
                cur = ""
            chunks.extend(_split_by_chars(para, max_chunk))
            continue
        if len(cur) + len(para) > max_chunk and cur:
            chunks.append(cur)
            cur = para
        else:
            cur += ("\n\n" if cur else "") + para
    if cur:
        chunks.append(cur)

    print(f"[Gemma] {len(chunks)}개 chunk로 번역 (총 {len(text)} chars)", flush=True)
    parts = []
    for i, ch in enumerate(chunks, 1):
        prompt = (
            "아래 영문 학술 논문 텍스트를 한국어로 정확히 번역하시오. "
            "학술적 문체 유지, 전문용어는 한글(영어 병기) 형식. "
            "마크다운 포맷·수식·인용 부호는 그대로 보존. "
            "번역 결과만 출력하고 다른 설명·서두는 금지.\n\n"
            f"[영문]\n{ch}\n\n[한글]"
        )
        try:
            t0 = time.time()
            resp = client.chat.completions.create(
                model=GEMMA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=8000,
                temperature=0.3,
                extra_body={"enable_thinking": False, "reasoning_effort": "none"},
            )
            out = resp.choices[0].message.content
            # 응답이 비정상적으로 짧으면 (입력의 30% 미만) 경고
            ratio = len(out) / max(len(ch), 1)
            warn = " ⚠️ TOO_SHORT" if ratio < 0.3 else ""
            parts.append(out)
            print(f"[Gemma] {i}/{len(chunks)} · in={len(ch)} → out={len(out)} chars "
                  f"({ratio*100:.0f}%) · {time.time()-t0:.1f}s{warn}", flush=True)
        except Exception as e:
            print(f"[Gemma] chunk {i} 실패: {e}", file=sys.stderr)
            return None
    return "\n\n".join(parts)


def _now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M")


def _check_pdf_integrity(pdf_path) -> tuple[bool, str | None]:
    """PDF 무결성 사전 검사 — EOF marker 존재 + 헤더 확인.

    Returns:
        (ok, reason): ok=True면 정상, False면 reason에 사유.
    """
    try:
        with open(pdf_path, "rb") as f:
            head = f.read(8)
            if not head.startswith(b"%PDF-"):
                return False, "PDF header 누락 (%PDF- not found)"
            f.seek(-1024, 2)  # 끝 1KB 검사
            tail = f.read()
            if b"%%EOF" not in tail:
                return False, "EOF marker 누락 (PDF 손상 가능성)"
        return True, None
    except OSError as e:
        return False, f"파일 접근 실패: {e}"


def extract_text_from_pdf(pdf_path):
    """
    PDF 파일에서 텍스트 추출

    Args:
        pdf_path (Path): PDF 파일 경로

    Returns:
        str: 추출된 텍스트
    """
    # 사전 무결성 검사 — 손상 PDF는 빠르게 실패
    ok, reason = _check_pdf_integrity(pdf_path)
    if not ok:
        print(f"[Error] PDF 무결성 검사 실패: {reason}", file=sys.stderr)
        return None
    try:
        with open(pdf_path, "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""

            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

            return text
    except Exception as e:
        print(f"[Error] PDF 추출 실패: {e}", file=sys.stderr)
        return None


def create_english_full_text(folder_path, pdf_path, title):
    """
    03_전문(영어).md 파일 생성

    Args:
        folder_path (Path): 논문 폴더 경로
        pdf_path (Path): PDF 파일 경로
        title (str): 논문 제목

    Returns:
        tuple: (성공 여부, 파일 경로, 오류 메시지)
    """
    text = extract_text_from_pdf(pdf_path)

    if text is None:
        return False, None, "PDF 추출 실패"

    if len(text.strip()) < 1000:
        return False, None, f"추출된 텍스트 부족 ({len(text)} bytes < 1000)"

    # 폴더 ID 추출
    folder_id = folder_path.name

    # 파일명 생성 (기존 형식 준수) - Windows 불가 문자 제거: \ / : * ? " < > |
    title_safe = re.sub(r'[\\/:*?"<>|]', '', title.replace(" ", "_"))[:30]
    english_file = folder_path / f"{folder_id}_03_{title_safe}_전문(영어).md"

    # surrogate 문자 제거
    text = text.encode("utf-8", errors="replace").decode("utf-8")

    # 파일 쓰기
    content = f"""# {title}

*Extracted from PDF - English Text*

---

{text}
"""

    try:
        english_file.write_text(content, encoding="utf-8")
        return True, english_file, None
    except Exception as e:
        return False, None, f"파일 쓰기 실패: {e}"


def create_korean_translation(folder_path, english_file, title, use_gemma=True):
    """
    04_전문(한글).md 파일 생성 (v06+: 템플릿 + Gemma 1차 + frontmatter 단계 추적).

    Returns:
        tuple: (성공, 파일경로, 오류, stage)
            - stage=1: Gemma 1차 완료 (Codex 검수 대기)
            - stage=0: 템플릿만 생성됨 (Gemma 미사용/실패, Codex/사용자 직접 번역 필요)
    """
    if not english_file.exists():
        return False, None, "영문 전문 파일 없음", 0

    try:
        english_text = english_file.read_text(encoding="utf-8")
    except Exception as e:
        return False, None, f"영문 전문 읽기 실패: {e}", 0

    folder_id = folder_path.name
    title_safe = re.sub(r'[\\/:*?"<>|]', '', title.replace(" ", "_"))[:30]
    korean_file = folder_path / f"{folder_id}_04_{title_safe}_전문(한글).md"

    # Gemma 1차 번역 시도
    v1_engine = "(미수행)"
    v1_at = ""
    v1_chars = 0
    full_text = "[TODO: 번역 필요]"
    stage = 0
    stage_label = "★ 0차 (템플릿만 — Codex/사용자 번역 대기)"

    RATIO_MIN = 0.3  # 한글/영어 문자량 최소 비율
    eng_len = len(english_text.strip())

    def _check_ratio(text: str) -> float:
        return len(text.strip()) / eng_len if eng_len > 0 else 0.0

    if use_gemma and _check_gemma_available():
        for attempt in range(1, 3):  # 최대 2회 시도
            print(f"  [Gemma] {folder_id} 번역 시작 (시도 {attempt}/2)...", flush=True)
            translated = _gemma_translate(english_text)
            if not translated:
                print(f"  [Gemma] 번역 실패 → 재시도 불가" if attempt == 2 else f"  [Gemma] 번역 실패 → 재시도", flush=True)
                continue
            ratio = _check_ratio(translated)
            print(f"  [Gemma] 완료 · 비율 {ratio:.2f} (한글/영어)", flush=True)
            if ratio >= RATIO_MIN:
                full_text = translated
                v1_engine = GEMMA_MODEL
                v1_at = _now_iso()
                v1_chars = len(translated)
                stage = 1
                stage_label = "★ 1차 (Gemma 자동 번역 — Codex 검수 대기)"
                break
            else:
                print(f"  [WARN] 비율 {ratio:.2f} < {RATIO_MIN} → {'재시도' if attempt == 1 else '번역 실패 처리'}", flush=True)
        else:
            # 2회 모두 비율 미달 → 실패 처리
            ratio = _check_ratio(translated) if translated else 0.0
            full_text = (
                f"[TRANSLATION_FAILED]\n\n"
                f"Gemma 1차 번역 2회 시도 후 품질 미달 (비율 {ratio:.2f} < {RATIO_MIN}).\n"
                f"수동 번역 또는 재처리 필요.\n\n"
                f"영문 원본 길이: {eng_len}자\n"
                f"번역 결과 길이: {len(translated.strip()) if translated else 0}자\n"
            )
            v1_engine = GEMMA_MODEL
            v1_at = _now_iso()
            v1_chars = 0
            stage = -1
            stage_label = "✗ 번역 실패 (Gemma 품질 미달 — 재처리 필요)"
            print(f"  [FAIL] {folder_id}: 번역 품질 미달 → stage=-1 기록", flush=True)
    elif use_gemma:
        print(f"  [WARN] Gemma 서버 미가동 → 템플릿만 생성", flush=True)

    # 템플릿 적용
    template = _load_template("translation_korean.md")
    if template:
        content = _safe_format(template, {
            "folder_id": folder_id,
            "source_pdf": "",
            "source_english": english_file.name,
            "stage": stage,
            "stage_label": stage_label,
            "v1_engine": v1_engine,
            "v1_at": v1_at,
            "v1_chars": v1_chars,
            "v2_engine": "",
            "v2_at": "",
            "v2_changes": 0,
            "title": title,
            "full_text": full_text,
        })
    else:
        # 템플릿 미발견 시 fallback
        content = (f"# {title} (한글 번역)\n\n"
                   f"> 단계: {stage_label}\n"
                   f"> 1차: {v1_engine} · {v1_at}\n\n---\n\n{full_text}\n")

    try:
        korean_file.write_text(content, encoding="utf-8")
        return True, korean_file, None, stage
    except Exception as e:
        return False, None, f"파일 쓰기 실패: {e}", 0


def find_pdf_and_title(folder_path):
    """
    폴더에서 PDF 파일과 제목 추출

    Args:
        folder_path (Path): 논문 폴더 경로

    Returns:
        tuple: (PDF 경로, 제목)
    """
    # PDF 파일 찾기
    pdf_files = list(folder_path.glob("*.pdf"))
    if not pdf_files:
        return None, None

    pdf_path = pdf_files[0]

    # 서머리 파일에서 제목 추출 시도
    summary_files = list(folder_path.glob("*_00_*서머리.md"))
    if summary_files:
        try:
            summary_content = summary_files[0].read_text(encoding="utf-8")
            # 제목 추출 (H1 헤더)
            for line in summary_content.split("\n"):
                if line.startswith("# "):
                    title = line[2:].strip()
                    return pdf_path, title
        except:
            pass

    # PDF 파일명에서 제목 추출
    pdf_name = pdf_path.stem
    title = pdf_name.replace(f"{folder_path.name}_01_", "").replace("_", " ").strip()

    return pdf_path, title


def process_folder(folder_path, extract_english=True, translate_korean=False, use_gemma=True):
    """
    단일 폴더 처리

    Args:
        folder_path (Path): 논문 폴더 경로
        extract_english (bool): 영문 추출 여부
        translate_korean (bool): 한글 번역 여부

    Returns:
        dict: 처리 결과
    """
    result = {
        "folder": folder_path.name,
        "english": {"success": False, "path": None, "error": None},
        "korean": {"success": False, "path": None, "error": None},
    }

    # PDF와 제목 찾기
    pdf_path, title = find_pdf_and_title(folder_path)

    if pdf_path is None:
        result["english"]["error"] = "PDF 파일 없음"
        return result

    if title is None:
        title = "Unknown Title"

    # 영문 추출
    if extract_english:
        success, english_file, error = create_english_full_text(
            folder_path, pdf_path, title
        )
        result["english"]["success"] = success
        result["english"]["path"] = str(english_file) if english_file else None
        result["english"]["error"] = error

    # 한글 번역
    if translate_korean:
        # 영문 파일 찾기
        english_files = list(folder_path.glob("*_03_*전문(영어).md"))
        if english_files:
            english_file = english_files[0]
            success, korean_file, error, _stage = create_korean_translation(
                folder_path, english_file, title, use_gemma=use_gemma
            )
            result["korean"]["success"] = success
            result["korean"]["path"] = str(korean_file) if korean_file else None
            result["korean"]["error"] = error
        else:
            result["korean"]["error"] = "영문 전문 파일 없음"

    return result


def do_english(args):
    """
    영문 전문 추출 명령어 실행
    """
    sys.stdout.reconfigure(encoding="utf-8")
    print("# ccpaper trans english - 영문 전문 추출\n", flush=True)
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", flush=True)

    if not PAPER_DIR.exists():
        print(f"Error: Paper directory not found at {PAPER_DIR}", flush=True)
        return

    # 대상 폴더 결정
    if args.folder:
        target_folders = [PAPER_DIR / args.folder]
        if not target_folders[0].exists():
            print(f"Error: Folder {args.folder} not found", flush=True)
            return
    else:
        target_folders = sorted([d for d in PAPER_DIR.iterdir() if d.is_dir()])

    print(f"총 {len(target_folders)}개 폴더 처리 중...\n", flush=True)

    # 처리
    success_count = 0
    failed_count = 0
    skipped_count = 0

    results = []

    for folder in target_folders:
        # 사전 SKIP 검사 (process_folder 호출 전 — 불필요한 작업/덮어쓰기 방지)
        existing_english = list(folder.glob("*_03_*전문(영어).md"))
        if existing_english and not args.force:
            try:
                ec = existing_english[0].read_text(encoding="utf-8", errors="ignore")
                low_quality = (
                    "TODO" in ec or "[영문 전문 추출 필요]" in ec or len(ec) < 1000
                )
            except Exception:
                low_quality = False
            if low_quality:
                print(f"- [AUTO-RETRY] {folder.name}: 품질 미달 → 재추출", flush=True)
                try:
                    existing_english[0].unlink()
                except Exception:
                    pass
            else:
                skipped_count += 1
                print(f"- [SKIP] {folder.name}: 이미 존재 (품질 OK)", flush=True)
                continue

        result = process_folder(folder, extract_english=True, translate_korean=False)
        results.append(result)

        if result["english"]["success"]:
            success_count += 1
            print(
                f"- [OK] {folder.name}: {Path(result['english']['path']).name}",
                flush=True,
            )
        else:
            failed_count += 1
            error = result["english"]["error"] or "알 수 없는 오류"
            print(f"- [FAIL] {folder.name}: {error}", flush=True)

    # 결과 요약
    print(f"\n## 요약", flush=True)
    print(f"- 성공: {success_count}개", flush=True)
    print(f"- 실패: {failed_count}개", flush=True)
    print(f"- 건너뜀: {skipped_count}개", flush=True)
    print(f"- 총 처리: {len(target_folders)}개", flush=True)

    # 실패 목록 저장
    failed = [r for r in results if not r["english"]["success"]]
    if failed:
        log_file = PROJECT_ROOT / "tmp" / "trans_english_failed.txt"
        log_file.parent.mkdir(exist_ok=True)
        log_content = f"영문 추출 실패 로그 - {datetime.now()}\n\n"
        for r in failed:
            log_content += f"{r['folder']}: {r['english']['error']}\n"
        log_file.write_text(log_content, encoding="utf-8")
        print(f"\n실패 로그: tmp/trans_english_failed.txt", flush=True)

    # 처리 시도가 있었고 모두 실패했다면 exit 1
    return 0 if (success_count > 0 or failed_count == 0) else 1


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """YAML frontmatter 파싱. (meta_dict, body_text) 반환."""
    if not content.startswith("---"):
        return {}, content
    end = content.find("\n---", 3)
    if end == -1:
        return {}, content
    yaml_block = content[3:end].strip()
    body = content[end + 4:].lstrip("\n")
    meta = {}
    current_parent = None
    for line in yaml_block.splitlines():
        if line.startswith("  ") and current_parent:
            sub_key, _, sub_val = line.strip().partition(":")
            val = sub_val.split("#")[0].strip()
            meta[current_parent][sub_key.strip()] = val
        else:
            key, _, val = line.partition(":")
            val = val.split("#")[0].strip()
            if not val:
                meta[key.strip()] = {}
                current_parent = key.strip()
            else:
                meta[key.strip()] = val
                current_parent = None
    return meta, body


def _update_frontmatter(content: str, updates: dict) -> str:
    """frontmatter의 translation 하위 필드를 updates로 갱신."""
    if not content.startswith("---"):
        return content
    end = content.find("\n---", 3)
    if end == -1:
        return content
    yaml_block = content[3:end]
    rest = content[end + 4:]

    for key, val in updates.items():
        # translation.key 형식 처리
        pattern = rf"(  {re.escape(key)}:)[^\n]*"
        replacement = rf"\g<1> {val}"
        yaml_block = re.sub(pattern, replacement, yaml_block)

    return f"---{yaml_block}\n---{rest}"


def _claude_review(folder_id: str, korean_file: Path, english_file: Path, limit_chunks: int | None = None) -> tuple[bool, int, str | None]:
    """
    Codex CLI로 한글 번역 2차 검수.
    Returns: (성공, 수정건수, 오류메시지)
    """
    import subprocess
    import tempfile

    try:
        korean_text = korean_file.read_text(encoding="utf-8")
        english_text = english_file.read_text(encoding="utf-8") if english_file.exists() else ""
    except Exception as e:
        return False, 0, f"파일 읽기 실패: {e}"

    meta, body = _parse_frontmatter(korean_text)
    trans_meta = meta.get("translation", {})
    current_stage = str(trans_meta.get("stage", "0")).strip()

    if current_stage == "2":
        return False, 0, "이미 2차 검수 완료 (stage=2)"

    # 번역 본문 추출 (--- 구분선 이후 실제 텍스트)
    body_lines = body.splitlines()
    text_start = 0
    for i, line in enumerate(body_lines):
        if line.startswith("---") and i > 0:
            text_start = i + 1
            break
    translation_body = "\n".join(body_lines[text_start:]).strip()
    header_lines = body_lines[:text_start]

    english_snippet = english_text[:2000] if english_text else "(영문 원본 없음)"

    prompt = (
        "아래는 Gemma AI가 자동 번역한 한국어 학술 논문 번역문입니다.\n"
        "다음 기준으로 검수하고 수정된 전문을 출력하시오:\n\n"
        "1. 오탈자·문법 오류 수정\n"
        "2. 학술 용어 일관성 확보 (처음 등장 시 '한글(영어)' 병기)\n"
        "3. 어색한 직역 표현을 자연스러운 한국어 학술 문체로 교정\n"
        "4. 마크다운 포맷·수식·인용 부호 보존\n"
        "5. 번역 누락 구간(영어가 그대로 남은 부분) 번역\n\n"
        "출력 형식: 수정된 번역 전문만 출력. 설명·서두·마무리 인사 금지.\n\n"
        f"[영문 원본 일부]\n{english_snippet}\n\n"
        f"[Gemma 1차 번역]\n{translation_body}"
    )

    # codex CLI 경로 탐색
    import shutil, os
    claude_cmd = shutil.which("codex")
    if not claude_cmd:
        # Git Bash / Windows 공통 fallback 경로
        for candidate in [
            os.path.expanduser("~/.local/bin/codex"),
            r"C:\Users\oaiskoo\.local\bin\codex",
        ]:
            if Path(candidate).exists():
                claude_cmd = candidate
                break
    if not claude_cmd:
        return False, 0, "codex CLI 미설치 또는 PATH 미설정"

    env = os.environ.copy()
    env["PATH"] = str(Path(claude_cmd).parent) + os.pathsep + env.get("PATH", "")

    # 청크 분할 (paragraph 우선, 초과 시 강제 분할)
    max_chunk = 4000
    def _split_chunks(text: str, n: int) -> list[str]:
        chunks, cur = [], ""
        for para in text.split("\n\n"):
            if len(para) > n:
                if cur:
                    chunks.append(cur)
                    cur = ""
                chunks.extend([para[i:i+n] for i in range(0, len(para), n)])
            elif len(cur) + len(para) > n and cur:
                chunks.append(cur)
                cur = para
            else:
                cur += ("\n\n" if cur else "") + para
        if cur:
            chunks.append(cur)
        return chunks

    chunks = _split_chunks(translation_body, max_chunk)
    limit = limit_chunks
    if limit:
        chunks = chunks[:limit]
    print(f"  [Codex] {folder_id} 2차 검수 시작 ({len(translation_body):,}자, {len(chunks)}개 chunk)...", flush=True)

    reviewed_parts = []
    t0 = time.time()
    for i, chunk in enumerate(chunks, 1):
        chunk_prompt = (
            "아래 한국어 학술 논문 번역문을 검수하시오.\n"
            "기준: 오탈자·문법 수정, 학술 용어 일관성, 어색한 직역 교정, 마크다운·수식 보존, 미번역 구간 번역.\n"
            "출력: 수정된 번역문만. 설명·서두 금지.\n\n"
            f"{chunk}"
        )
        try:
            ct0 = time.time()
            result = subprocess.run(
                [claude_cmd, "-p", "--output-format", "text"],
                input=chunk_prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=120,
                env=env,
            )
            if result.returncode != 0:
                err = result.stderr.strip() or f"chunk {i} CLI 오류"
                return False, 0, err
            out = result.stdout.strip()
            if not out:
                return False, 0, f"chunk {i} 응답 비어 있음"
            reviewed_parts.append(out)
            print(f"  [Codex] {i}/{len(chunks)} · {len(chunk)}→{len(out)}자 · {time.time()-ct0:.1f}s", flush=True)
        except subprocess.TimeoutExpired:
            return False, 0, f"chunk {i} 타임아웃 (120s)"

    reviewed_text = "\n\n".join(reviewed_parts)
    elapsed = time.time() - t0
    changes = sum(1 for a, b in zip(translation_body.split("\n"), reviewed_text.split("\n")) if a != b)
    print(f"  [Codex] 완료 · 총 {elapsed:.1f}s · 수정 ~{changes}줄", flush=True)

    # frontmatter 갱신
    v2_engine = "codex-code"
    v2_at = _now_iso()
    updated_content = _update_frontmatter(korean_text, {
        "stage": "2",
        "v2_engine": v2_engine,
        "v2_at": v2_at,
        "v2_changes": str(changes),
    })

    # body 교체: frontmatter 끝 이후를 헤더 + 검수 결과로 대체
    fm_end = updated_content.find("\n---", 3) + 4
    stage_label = "★★ 2차 (Codex 검수 완료)"
    new_body_section = "\n" + "\n".join(header_lines) + "\n" + reviewed_text + "\n"
    updated_content = updated_content[:fm_end] + new_body_section

    # 메타 라인 교체
    updated_content = re.sub(r"> \*\*번역 단계\*\*:.*", f"> **번역 단계**: {stage_label}", updated_content)
    updated_content = re.sub(r"> \*\*2차\*\*:.*", f"> **2차**: {v2_engine} · {v2_at}", updated_content)

    korean_file.write_text(updated_content, encoding="utf-8")
    return True, changes, None


def do_korean_review(args):
    """한글 번역 2차 Codex 검수."""
    sys.stdout.reconfigure(encoding="utf-8")
    print("# ccpaper trans korean --review - Codex 2차 검수\n", flush=True)
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", flush=True)

    if not PAPER_DIR.exists():
        print(f"Error: Paper directory not found at {PAPER_DIR}", flush=True)
        return

    if args.folder:
        target_folders = [PAPER_DIR / args.folder]
        if not target_folders[0].exists():
            print(f"Error: Folder {args.folder} not found", flush=True)
            return
    else:
        target_folders = sorted([d for d in PAPER_DIR.iterdir() if d.is_dir()])

    print(f"총 {len(target_folders)}개 폴더 검사 중...\n", flush=True)

    success_count = 0
    skipped_count = 0
    failed_count = 0

    for folder in target_folders:
        korean_files = list(folder.glob("*_04_*전문(한글).md"))
        english_files = list(folder.glob("*_03_*전문(영어).md"))

        if not korean_files:
            continue

        korean_file = korean_files[0]
        english_file = english_files[0] if english_files else Path("/dev/null")

        # stage 확인
        try:
            content = korean_file.read_text(encoding="utf-8")
            meta, _ = _parse_frontmatter(content)
            stage = str(meta.get("translation", {}).get("stage", "0")).strip()
        except Exception:
            stage = "0"

        if stage == "2" and not args.force:
            skipped_count += 1
            print(f"- [SKIP] {folder.name}: 이미 2차 완료", flush=True)
            continue

        if stage == "0":
            skipped_count += 1
            print(f"- [SKIP] {folder.name}: 1차 번역 없음 (stage=0)", flush=True)
            continue

        ok, changes, err = _claude_review(folder.name, korean_file, english_file, limit_chunks=getattr(args, "limit_chunks", None))
        if ok:
            success_count += 1
            print(f"- [OK] {folder.name}: 수정 ~{changes}줄", flush=True)
        else:
            if err and "이미 2차" in err:
                skipped_count += 1
                print(f"- [SKIP] {folder.name}: {err}", flush=True)
            else:
                failed_count += 1
                print(f"- [FAIL] {folder.name}: {err}", flush=True)

    print(f"\n## 요약", flush=True)
    print(f"- 성공: {success_count}개", flush=True)
    print(f"- 실패: {failed_count}개", flush=True)
    print(f"- 건너뜀: {skipped_count}개", flush=True)


def do_korean(args):
    """
    한글 번역 명령어 실행
    """
    if getattr(args, "review", False):
        do_korean_review(args)
        return

    sys.stdout.reconfigure(encoding="utf-8")
    print("# ccpaper trans korean - 한글 번역 생성\n", flush=True)
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", flush=True)

    if not PAPER_DIR.exists():
        print(f"Error: Paper directory not found at {PAPER_DIR}", flush=True)
        return

    # 대상 폴더 결정
    if args.folder:
        target_folders = [PAPER_DIR / args.folder]
        if not target_folders[0].exists():
            print(f"Error: Folder {args.folder} not found", flush=True)
            return
    else:
        target_folders = sorted([d for d in PAPER_DIR.iterdir() if d.is_dir()])

    print(f"총 {len(target_folders)}개 폴더 처리 중...\n", flush=True)

    # 처리
    success_count = 0
    failed_count = 0
    skipped_count = 0

    results = []

    INCOMPLETE_MARKERS = [
        "(추출 필요)", "[Translation Required]", "TODO",
        "[TRANSLATION_FAILED]", "[TODO: 번역 필요]",
    ]

    def _is_low_quality(p: Path) -> bool:
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return True
        if len(txt.strip()) < 1000:
            return True
        return any(m in txt for m in INCOMPLETE_MARKERS)

    for folder in target_folders:
        use_gemma = not getattr(args, "no_gemma", False)

        # 사전 SKIP 체크 (process_folder 호출 전 — 파일 덮어쓰기 방지)
        existing_korean = list(folder.glob("*_04_*전문(한글).md"))
        if existing_korean and not args.force:
            if _is_low_quality(existing_korean[0]):
                # 품질 미달 → 자동 재처리 (force와 동일 효과)
                print(f"- [AUTO-RETRY] {folder.name}: 품질 미달 → 재번역", flush=True)
            else:
                skipped_count += 1
                print(f"- [SKIP] {folder.name}: 이미 존재 (품질 OK)", flush=True)
                continue

        result = process_folder(folder, extract_english=False, translate_korean=True, use_gemma=use_gemma)
        results.append(result)

        if result["korean"]["success"]:
            success_count += 1
            print(
                f"- [OK] {folder.name}: {Path(result['korean']['path']).name}",
                flush=True,
            )
        else:
            failed_count += 1
            error = result["korean"]["error"] or "알 수 없는 오류"
            print(f"- [FAIL] {folder.name}: {error}", flush=True)

    # 결과 요약
    print(f"\n## 요약", flush=True)
    print(f"- 성공: {success_count}개", flush=True)
    print(f"- 실패: {failed_count}개", flush=True)
    print(f"- 건너뜀: {skipped_count}개", flush=True)
    print(f"- 총 처리: {len(target_folders)}개", flush=True)

    # 실패 목록 저장
    failed = [r for r in results if not r["korean"]["success"]]
    if failed:
        log_file = PROJECT_ROOT / "tmp" / "trans_korean_failed.txt"
        log_file.parent.mkdir(exist_ok=True)
        log_content = f"한글 번역 실패 로그 - {datetime.now()}\n\n"
        for r in failed:
            log_content += f"{r['folder']}: {r['korean']['error']}\n"
        log_file.write_text(log_content, encoding="utf-8")
        print(f"\n실패 로그: tmp/trans_korean_failed.txt", flush=True)

    return 0 if (success_count > 0 or failed_count == 0) else 1


def main():
    parser = argparse.ArgumentParser(description="PDF 텍스트 추출 및 번역")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # english 명령어
    eng_p = subparsers.add_parser("english", help="영문 전문 추출")
    eng_p.add_argument("--folder", type=str, help="특정 폴더만 처리")
    eng_p.add_argument("--force", action="store_true", help="기존 파일 덮어쓰기")

    # korean 명령어
    kor_p = subparsers.add_parser("korean", help="한글 번역 생성")
    kor_p.add_argument("--folder", type=str, help="특정 폴더만 처리")
    kor_p.add_argument("--force", action="store_true", help="기존 파일 덮어쓰기")
    kor_p.add_argument("--review", action="store_true", help="Codex 2차 검수 (stage 1→2)")
    kor_p.add_argument("--no-gemma", action="store_true", dest="no_gemma", help="Gemma 건너뛰기 (Codex 직접 번역)")
    kor_p.add_argument("--limit-chunks", type=int, dest="limit_chunks", help="검수할 최대 chunk 수 (테스트용)")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    if args.command == "english":
        sys.exit(do_english(args) or 0)
    elif args.command == "korean":
        sys.exit(do_korean(args) or 0)
    else:
        print("Not implemented")
        sys.exit(1)


if __name__ == "__main__":
    main()
