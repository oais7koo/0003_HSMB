#!/usr/bin/env python
"""
test_gemma_translate.py - Gemma 한글 번역 품질 테스트
"""
import sys
import time
from pathlib import Path
from openai import OpenAI

sys.stdout.reconfigure(encoding="utf-8")

if len(sys.argv) < 2:
    print("Usage: test_gemma_translate.py <english_file> [chunk_size=3000]")
    sys.exit(1)

en_path = Path(sys.argv[1])
chunk_size = int(sys.argv[2]) if len(sys.argv) > 2 else 3000

text = en_path.read_text(encoding="utf-8")[:chunk_size]

client = OpenAI(base_url="http://localhost:8080/v1", api_key="local")

prompt = f"""아래 영문 학술 논문 발췌를 한국어로 정확히 번역하시오. 학술적 문체를 유지하고, 전문용어는 한글(영어 병기) 형식으로 처리하시오. 번역 결과만 출력하고 다른 설명은 하지 마시오.

[영문 원문]
{text}

[한글 번역]"""

print(f"[입력] {len(text)} chars from {en_path.name}", flush=True)
print(f"[모델] gemma4:26b", flush=True)
print(f"[설정] enable_thinking=False, reasoning_effort=none, max_tokens=4000\n", flush=True)

t0 = time.time()
resp = client.chat.completions.create(
    model="gemma4:26b",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=4000,
    temperature=0.3,
    extra_body={"enable_thinking": False, "reasoning_effort": "none"},
)
elapsed = time.time() - t0

translation = resp.choices[0].message.content
print(f"[출력] {len(translation)} chars · {elapsed:.1f}s · {len(translation)/elapsed:.0f} char/s\n")
print("=" * 60)
print(translation)
print("=" * 60)
