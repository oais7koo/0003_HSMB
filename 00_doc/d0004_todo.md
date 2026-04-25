# TODO / 디버깅 이슈 — 0003_HSMB

## 진행 중

없음

---

## 완료 (→ d0010_history.md)

- [DONE] ps2000_통합IQA.py v04 — DL-IQA (DBCNN + ARNIQA) 통합 (2026-04-23)
- [DONE] pyproject.toml — cu128 explicit index + [tool.uv.sources] 설정 (2026-04-23)
- [DONE] CUDA torch 2.11.0+cu128 동작 확인 — RTX 3070, CUDA available=True (2026-04-23)
- [DONE] ps2000_통합IQA.py GPU 전체 실행 — 940장, DL-IQA 포함, 결과 3파일 생성 (2026-04-23)

---

## 환경 메모

| 항목 | 내용 |
|------|------|
| GPU | RTX 3070 8GB |
| Driver | 581.57 |
| CUDA | 13.0 (12.x 하위호환) |
| 목표 torch | 2.11.0+cu128 |
| pip 명령 | `.venv/Scripts/pip install --force-reinstall --no-deps torch==2.11.0+cu128 torchvision==0.26.0+cu128 --index-url https://download.pytorch.org/whl/cu128` |
