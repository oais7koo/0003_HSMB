#!/usr/bin/env python3
"""
gemma_batch.py - Gemma4 SLM 배치 처리 (비용 절감용)

Usage:
  uv run python .claude/skills/gemma/scripts/gemma_batch.py <input> [options]

Examples:
  # 텍스트 파일 요약
  uv run python ... input.txt --task summarize

  # JSONL 파일 키워드 추출, 결과 저장
  uv run python ... papers.jsonl --task extract_keywords --output results.json

  # 커스텀 프롬프트 (분류)
  uv run python ... data.txt --prompt "다음을 긍정/부정/중립으로 분류하세요:\n\n{text}\n\n분류:"

  # 테스트 (5개만 처리)
  uv run python ... input.txt --task summarize --limit 5
"""
import sys
import json
import time
import argparse
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://localhost:8080/v1"
MODEL = "mlx-community/gemma-4-e4b-it-4bit"
API_KEY = "local"

# 태스크별 기본 프롬프트 템플릿 ({text} 자리표시자 사용)
TASK_PROMPTS: dict[str, str] = {
    "summarize": (
        "다음 텍스트를 2~3문장으로 간결하게 요약하세요. 핵심 내용만 포함하세요:\n\n{text}\n\n요약:"
    ),
    "classify": (
        "다음 텍스트의 카테고리를 아래 중 하나로 분류하세요.\n"
        "카테고리: 과학, 기술, 사회, 경제, 문화, 의학, 공학, 기타\n\n"
        "{text}\n\n"
        "카테고리 (한 단어만):"
    ),
    "extract_keywords": (
        "다음 텍스트에서 핵심 키워드 5개를 추출하세요.\n"
        "JSON 배열 형식으로만 답하세요. 예: [\"키워드1\", \"키워드2\", \"키워드3\", \"키워드4\", \"키워드5\"]\n\n"
        "{text}\n\n"
        "키워드:"
    ),
    "translate_ko": (
        "다음 텍스트를 자연스러운 한국어로 번역하세요:\n\n{text}\n\n번역:"
    ),
    "translate_en": (
        "Translate the following text to natural English:\n\n{text}\n\nTranslation:"
    ),
    "sentiment": (
        "다음 텍스트의 감성을 분석하세요.\n"
        "긍정/부정/중립 중 하나로만 답하세요.\n\n"
        "{text}\n\n"
        "감성:"
    ),
    "qa": "{text}",  # 커스텀 프롬프트 사용 시 이 태스크로 전달
}


def _get_client():
    """OpenAI 클라이언트 초기화"""
    try:
        from openai import OpenAI
    except ImportError:
        print("[ERROR] openai 패키지 없음. 설치: uv add openai")
        sys.exit(1)
    return OpenAI(base_url=BASE_URL, api_key=API_KEY)


def check_server(client) -> bool:
    """서버 연결 확인"""
    try:
        models = client.models.list()
        ids = [m.id for m in models.data]
        print(f"[OK] 서버 연결 정상 | 모델: {ids[0] if ids else '(없음)'}")
        return True
    except Exception as e:
        print(f"[ERROR] 서버 연결 실패: {e}")
        print("  → mlx-lm 서버를 먼저 실행하세요:")
        print("    uv run mlx_lm.server --model mlx-community/gemma-4-e4b-it-4bit --port 8080")
        return False


def call_gemma(client, prompt: str, max_tokens: int = 512) -> str:
    """Gemma 단일 추론 (non-stream)"""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        stream=False,
        temperature=0.3,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()


def load_inputs(path: str) -> list[dict]:
    """
    입력 파일 로드
    - .txt  : 줄별로 처리 (빈 줄 제외)
    - .jsonl: JSON Lines (각 줄: {"id": ..., "text": ...})
    - .json : JSON 배열 ([str] 또는 [{"id": ..., "text": ...}])
    """
    p = Path(path)
    if not p.exists():
        print(f"[ERROR] 파일 없음: {path}")
        sys.exit(1)

    items = []
    if p.suffix == ".jsonl":
        with open(p, encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                items.append({
                    "id": data.get("id", i),
                    "text": data.get("text", data.get("abstract", data.get("content", ""))),
                })
    elif p.suffix == ".json":
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, str):
                    items.append({"id": i, "text": item})
                elif isinstance(item, dict):
                    items.append({
                        "id": item.get("id", i),
                        "text": item.get("text", item.get("abstract", item.get("content", ""))),
                    })
    else:  # .txt 또는 기타: 줄별 처리
        with open(p, encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if line:
                    items.append({"id": i, "text": line})

    return items


def process_batch(
    client,
    items: list[dict],
    task: str,
    custom_prompt: str | None,
    max_tokens: int,
    delay: float,
) -> list[dict]:
    """배치 처리 실행"""
    results = []
    total = len(items)
    template = custom_prompt if custom_prompt else TASK_PROMPTS.get(task, "{text}")

    for i, item in enumerate(items, 1):
        text = item.get("text", "").strip()
        if not text:
            continue

        prompt = template.replace("{text}", text)
        input_preview = text[:80] + "..." if len(text) > 80 else text
        print(f"[{i:>4}/{total}] id={item['id']} ... ", end="", flush=True)

        start = time.time()
        try:
            output = call_gemma(client, prompt, max_tokens=max_tokens)
            elapsed = round(time.time() - start, 2)
            print(f"완료 ({elapsed}s)")
            results.append({
                "id": item["id"],
                "input_preview": input_preview,
                "output": output,
                "task": task,
                "elapsed_s": elapsed,
            })
        except Exception as e:
            elapsed = round(time.time() - start, 2)
            print(f"실패 ({e})")
            results.append({
                "id": item["id"],
                "input_preview": input_preview,
                "output": None,
                "task": task,
                "elapsed_s": elapsed,
                "error": str(e),
            })

        if delay > 0 and i < total:
            time.sleep(delay)

    return results


def save_results(results: list[dict], task: str, output_path: str, elapsed_total: float):
    """결과 JSON 저장"""
    success = sum(1 for r in results if r.get("output") is not None)
    failed = len(results) - success

    data = {
        "meta": {
            "task": task,
            "model": MODEL,
            "total": len(results),
            "success": success,
            "failed": failed,
            "elapsed_total_s": round(elapsed_total, 2),
            "avg_elapsed_s": round(elapsed_total / len(results), 2) if results else 0,
        },
        "results": results,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data["meta"]


def main():
    parser = argparse.ArgumentParser(
        description="gemma_batch - Gemma4 SLM 배치 처리 (비용 절감용)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("input", help="입력 파일 경로 (.txt/.json/.jsonl)")
    parser.add_argument(
        "--task", default="summarize",
        choices=list(TASK_PROMPTS.keys()),
        help=f"처리 태스크 (default: summarize) | 선택: {', '.join(TASK_PROMPTS.keys())}",
    )
    parser.add_argument("--prompt", help="커스텀 프롬프트 ({text} 자리표시자 사용)")
    parser.add_argument("--output", help="결과 저장 경로 (default: <입력파일>_<task>.json)")
    parser.add_argument("--max-tokens", type=int, default=512, help="최대 토큰 수 (default: 512)")
    parser.add_argument("--delay", type=float, default=0.0, help="요청 간 딜레이(초) (default: 0.0)")
    parser.add_argument("--limit", type=int, help="처리할 최대 항목 수 (테스트용)")

    args = parser.parse_args()

    print("## gemma_batch - Gemma4 SLM 배치 처리")
    print(f"  입력: {args.input}")
    print(f"  태스크: {args.task}")

    # 서버 연결
    client = _get_client()
    if not check_server(client):
        sys.exit(1)

    # 입력 로드
    items = load_inputs(args.input)
    if args.limit:
        items = items[: args.limit]
        print(f"[OK] 입력 로드: {len(items)}개 (limit={args.limit})")
    else:
        print(f"[OK] 입력 로드: {len(items)}개 항목")
    print()

    # 배치 처리
    start_total = time.time()
    results = process_batch(
        client, items,
        task=args.task,
        custom_prompt=args.prompt,
        max_tokens=args.max_tokens,
        delay=args.delay,
    )
    elapsed_total = time.time() - start_total

    # 결과 저장
    input_stem = Path(args.input).stem
    output_path = args.output or f"{input_stem}_{args.task}.json"
    meta = save_results(results, args.task, output_path, elapsed_total)

    # 요약 출력
    print(f"\n## 처리 완료")
    print(f"  성공: {meta['success']}/{meta['total']}개")
    print(f"  실패: {meta['failed']}개")
    print(f"  총 소요: {meta['elapsed_total_s']}초 (평균 {meta['avg_elapsed_s']}초/건)")
    print(f"  결과 저장: {output_path}")


if __name__ == "__main__":
    main()
