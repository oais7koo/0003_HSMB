# oowiki Tutorial

> LLM Wiki 지식 체계 구축 스킬 — 지식을 수집·통합하고 01_obsidian/0020_wiki/에 위키를 관리한다 | 최종 업데이트: 2026-04-29

## 개요

Karpathy LLM Wiki 철학("지식을 한 번 컴파일하고 매번 재생성하지 않는다") 기반의 지식 관리 스킬. 새 정보를 단순 파일로 저장하지 않고 기존 위키에 **유기적으로 통합**하여 교차참조를 유지한다. RAG 없이 위키 직접 활용으로 지식 조회.

저장 위치: `01_obsidian/0020_wiki/` | DDC(듀이 십진분류법) 기반 카테고리 체계

## 명령어

| 명령어 | 설명 |
|--------|------|
| `oowiki run [내용]` | 새 지식 수집·통합 (Ingest) — 가장 핵심 명령 |
| `oowiki run --url [URL]` | URL 내용 수집·통합 |
| `oowiki run --file [경로]` | 파일 내용 수집·통합 |
| `oowiki inbox` | 0019_정리 처리 대기 파일 목록 표시 |
| `oowiki inbox --clear` | 0019_정리 전체 파일 삭제 (통합 완료 후) |
| `oowiki inbox --clear [파일명]` | 특정 파일만 삭제 |
| `oowiki search [질문]` | 위키에서 정보 조회 (인용 포함) |
| `oowiki lint` | 모순·고아 페이지·교차참조 누락 점검 |
| `oowiki index` | index.md 전체 재생성 |
| `oowiki show [페이지]` | 특정 위키 페이지 내용 표시 |
| `oowiki list` | 전체 위키 페이지 목록 |
| `oowiki status` | 위키 현황 (페이지 수, 카테고리, 마지막 수집일) |

## 주요 사용 예시

```bash
# 새 지식 텍스트 직접 입력
oowiki run "Transformer의 Attention 메커니즘은 Q, K, V 행렬로..."

# URL에서 지식 수집
oowiki run --url https://arxiv.org/abs/2305.xxxxx

# 파일에서 지식 수집
oowiki run --file 01_obsidian/0019_정리/논문요약.md

# inbox(0019_정리) 일괄 처리
oowiki run          # 자동으로 0019_정리 파일 감지·목록 출력
# → Claude가 각 파일 통합 후
oowiki inbox --clear  # 처리 완료 파일 삭제

# 위키 조회
oowiki search "BERT와 GPT의 차이점"
```

## 워크플로우

```
1. index.md 로드 — 기존 위키 카탈로그 파악
   ↓
2. 관련 페이지 탐색 — 입력 내용과 연관된 기존 페이지 식별
   ↓
3. 통합 판단
   ├── 관련 페이지 있음 → 기존 페이지에 유기적 통합 (단순 추가 X)
   └── 관련 페이지 없음 → 새 카테고리/페이지 생성
   ↓
4. 교차참조 갱신 — 관련 페이지 간 [[링크]] 추가/수정
   ↓
5. index.md 갱신 — 새 페이지/수정 페이지 카탈로그 반영
   ↓
6. log.md 기록 — 작업 내용 이력 추가
```

**통합 전 AI 품질 필터**: 내용 없음·완전 중복·단순 목록·임시 메모·포맷 전용 파일은 스킵 + log 기록. 개인 프로젝트 코드에서 개념·패턴·알고리즘을 추출해 위키화하는 Code-to-Wiki 기능도 지원.

## 관련 스킬

| 스킬 | 관계 |
|------|------|
| `oomemo` | 임시 메모 (위키 통합 전 단계) |
| `oonote` | 연구노트 (SP별 문서) |
| `ooscrap` | 웹 스크래핑 (원본 소스 수집) |
| `ooresearch` | SOTA 연구 (위키 소스 생성) |
