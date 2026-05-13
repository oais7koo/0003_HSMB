---
type: translation_korean
folder_id: {folder_id}
source_pdf: {source_pdf}
source_english: {source_english}
translation:
  stage: {stage}                 # 1=Gemma 1차, 2=Claude 검수 완료
  v1_engine: {v1_engine}          # 예: gemma4:26b, claude-sonnet (Gemma 미가용 시)
  v1_at: {v1_at}                  # ISO 8601
  v1_chars: {v1_chars}
  v2_engine: {v2_engine}          # 빈 값이면 미수행
  v2_at: {v2_at}
  v2_changes: {v2_changes}        # Claude 수정 횟수
---

# {title} (한글 번역)

> **번역 단계**: {stage_label}
> **1차**: {v1_engine} · {v1_at}
> **2차**: {v2_engine} · {v2_at}
> **원본**: {source_pdf}

---

{full_text}
