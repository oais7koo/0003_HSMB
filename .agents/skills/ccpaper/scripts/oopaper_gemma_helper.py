"""oopaper_gemma_helper - Gemma 위임 공통 헬퍼.

실험(2026-04-17)에서 검증된 안전 설정을 강제 적용한다:
  - reasoning_effort="none" + enable_thinking=False (reasoning 누수 차단)
  - max_tokens ≥ 4000 (reasoning 잔여로 잘림 방지)
  - temperature 0.2~0.3 (반복 루프 방지)

사용 예:
    from oopaper_gemma_helper import gemma_is_enabled, gemma_call

    if gemma_is_enabled():
        summary = gemma_call("task_summary", paper_text)
    else:
        # 기존 경로(academic-researcher 등)
        ...

업무 경계 (`.claude/guides/gemma_delegation.md` 준수):
  ⭕ 허용: 자유형식 서머리(초안), 단일 페이지 번역(초안), Rephrase
  ❌ 금지: 엄격한 포맷 강제, 장문 배치 번역(최종), 학술 번역 최종본
"""
from __future__ import annotations
import os
import sys
import time
from pathlib import Path

BASE_URL = "http://localhost:8080/v1"
API_KEY = "local"
DEFAULT_MODEL = "gemma4:26b"
LOG_DIR = Path(__file__).resolve().parent.parent.parent.parent / ".omc" / "gemma-usage"


def gemma_is_enabled() -> bool:
    """env OOPAPER_USE_GEMMA=1 이면 True."""
    return os.environ.get("OOPAPER_USE_GEMMA", "").strip() in ("1", "true", "True")


def _get_client():
    from openai import OpenAI
    return OpenAI(base_url=BASE_URL, api_key=API_KEY)


def _safe_extra_body() -> dict:
    """Gemma reasoning 비활성 옵션."""
    return {
        "reasoning_effort": "none",
        "chat_template_kwargs": {"enable_thinking": False},
    }


def _append_log(caller: str, task: str, prompt_head: str, resp_head: str, elapsed: float, finish: str):
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        import json, datetime, socket
        host = os.environ.get("COMPUTERNAME") or socket.gethostname()
        month = datetime.datetime.now().strftime("%Y%m")
        f = LOG_DIR / f"{host}-{month}.jsonl"
        with f.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps({
                "ts": datetime.datetime.now().isoformat(timespec="seconds"),
                "host": host,
                "caller": caller,
                "task": task,
                "model": DEFAULT_MODEL,
                "prompt_head": prompt_head[:200],
                "resp_head": resp_head[:200],
                "elapsed_ms": int(elapsed * 1000),
                "finish_reason": finish,
            }, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[WARN] gemma log 기록 실패: {e}", file=sys.stderr)


def gemma_call(
    task: str,
    prompt: str,
    *,
    system: str | None = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 6000,
    temperature: float = 0.25,
    caller: str = "ccpaper",
) -> tuple[str, str]:
    """Gemma 호출. (content, finish_reason) 튜플 반환.

    Args:
        task: 작업 종류 태그 (로그용) — summary/translate/classify 등
        prompt: user 메시지
        system: system 메시지 (선택)
        max_tokens: 기본 6000 (reasoning 여유 포함)
        temperature: 기본 0.25 (낮지만 반복 루프 안 빠지는 선)
        caller: 호출 스킬명 (로그용)

    Raises:
        RuntimeError: 서버 미가동 / content 빈값 등.
    """
    assert max_tokens >= 4000, "reasoning 누수 대비 max_tokens ≥ 4000 필요"
    assert 0.1 <= temperature <= 0.6, "반복 루프 방지를 위해 0.1~0.6 권장"

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    client = _get_client()
    t0 = time.time()
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        extra_body=_safe_extra_body(),
    )
    elapsed = time.time() - t0

    msg = resp.choices[0].message
    content = (msg.content or "").strip()
    finish = resp.choices[0].finish_reason

    _append_log(caller, task, prompt[:200], content[:200], elapsed, finish)

    if not content:
        raise RuntimeError(
            f"[gemma] 빈 응답 (finish={finish}, elapsed={elapsed:.1f}s) — "
            f"fallback 권장"
        )
    return content, finish


# ------------------ 작업별 프리셋 ------------------

def task_summary_draft(paper_text: str, caller: str = "ccpaper") -> str:
    """Phase 2 서머리 초안 (자유 포맷). 최종 포맷 보정은 Claude에서 수행."""
    head = paper_text[:12000]
    prompt = (
        "다음 영문 학술 논문 본문을 바탕으로 한국어로 간결한 서머리를 작성해라.\n"
        "포함 내용: (1) 연구 배경·문제, (2) 제안 방법, (3) 수식(LaTeX), (4) 실험 결과, (5) 기여.\n"
        "규칙: 추측·외부 지식 주입 금지, 원문 근거만 사용, 전문용어 영어 병기.\n\n"
        f"---\n{head}\n---"
    )
    content, _ = gemma_call("summary", prompt, caller=caller, max_tokens=5000, temperature=0.3)
    return content


def task_translate_page(english_page: str, caller: str = "ccpaper") -> str:
    """Phase 4 단일 페이지 번역 초안. 전체 논문 배치 번역은 금지 — 페이지별 호출만."""
    if len(english_page) > 5000:
        raise ValueError("페이지당 5KB 초과 — 반복 루프 위험. 분할 후 호출하라.")
    prompt = (
        "Translate this English to Korean. Output only the translation, "
        "no thinking, no explanation. 전문용어는 영어 병기(예: 학습률(learning rate)). "
        "수식은 LaTeX 원문 그대로 보존.\n\n"
        f"{english_page}"
    )
    content, _ = gemma_call("translate", prompt, caller=caller, max_tokens=6000, temperature=0.2)
    return content


def task_rephrase(text: str, instruction: str, caller: str = "ccpaper") -> str:
    """단순 rephrase — 지시에 따라 문장 재작성. 포맷 강제는 금지."""
    prompt = f"{instruction}\n\n---\n{text}\n---"
    content, _ = gemma_call("rephrase", prompt, caller=caller, max_tokens=4000, temperature=0.3)
    return content
