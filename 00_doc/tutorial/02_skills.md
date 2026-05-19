# oo 스킬 레퍼런스

> `ooenv tutorial --update`로 현행화 | 소스: `.claude/skills/oo*/SKILL.md`

---

## 세션/메타 스킬

### oostart - 세션 시작

| 명령 | 설명 |
|------|------|
| `oostart run` | 세션 시작 (문서 상태 점검 + oocheck 연동) |
| `oostart status` | 현재 상태 확인 |

### oostop - 세션 종료

| 명령 | 설명 |
|------|------|
| `oostop run` | 세션 종료 (변경사항 정리 + 커밋 권고) |

### oohelp - 도움말

| 명령 | 설명 |
|------|------|
| `oohelp` | 전체 스킬/명령어 목록 |
| `oohelp [스킬명]` | 특정 스킬 상세 도움말 |

### oocontext - 서브프로젝트 컨텍스트

| 명령 | 설명 |
|------|------|
| `oocontext` | 현재 컨텍스트 확인 |
| `oocontext [N]` | SP N으로 전환 (00~06) |
| `oocontext list` | SP 목록 표시 |
| `oocontext clear` | SP00으로 초기화 |

```bash
oocontext 3    # SP03(03_paper) 활성화 → 이후 d30001~ 문서 사용
oocontext      # 현재 SP 확인
```

---

## 핵심 개발 스킬

### ooprd - PRD 생성/검증

| 명령 | 설명 |
|------|------|
| `ooprd run` | PRD 생성(신규) 또는 정합성 검증(기존) |
| `ooprd clarify` | 모호성 해소 (최대 5개 질문) |
| `ooprd validate` | 구조 검증 |
| `ooprd optimize` | PRD 최적화 |
| `ooprd section [N]` | 특정 섹션 갱신 |

출력: `00_doc/d{SP}0001_prd.md`

### ooplan - 구현 계획

| 명령 | 설명 |
|------|------|
| `ooplan run` | 구현 계획 생성/업데이트 |
| `ooplan section [N]` | 특정 섹션 업데이트 |

출력: `00_doc/d{SP}0002_plan.md`

### oodev - TDD 기반 개발

| 명령 | 설명 |
|------|------|
| `oodev run` | RED→GREEN→REFACTOR 사이클 |
| `oodev run [기능명]` | 특정 기능 구현 |

### ootest - 통합 테스트

| 명령 | 설명 |
|------|------|
| `ootest run` | 테스트 실행 + 결과 기록 |
| `ootest generate` | 테스트 코드 자동 생성 |

출력: `00_doc/d{SP}0003_test.md`

### oocheck - 코드 품질 체크

| 명령 | 설명 |
|------|------|
| `oocheck run` | 정적 분석 + 이슈 → d0004 등록 |
| `oocheck run --full` | 전체 스캔 |

출력: `00_doc/d{SP}0004_todo.md`

### oofix - 코드 오류 수정

| 명령 | 설명 |
|------|------|
| `oofix run` | d0004 기반 이슈 자동 수정 |
| `oofix run [ID]` | 특정 이슈만 수정 |

### oocommit - Git 커밋

| 명령 | 설명 |
|------|------|
| `oocommit run` | 커밋 + 이력 정리 |
| `oocommit run --push` | 커밋 + push |
| `oocommit run --pr` | 커밋 + PR 생성 |

---

## 모듈/DB 스킬

### oolib - oo 모듈 최적화

| 명령 | 설명 |
|------|------|
| `oolib run` | oo 모듈 분석/최적화 |
| `oolib check` | 모듈 정합성 체크 |

### oodb - DB 관리

| 명령 | 설명 |
|------|------|
| `oodb run` | DB 현황 분석 → d0006_db.md |
| `oodb migrate` | 마이그레이션 실행 |
| `oodb design` | 스키마 설계 지원 |

### oodeep - 딥러닝 최적화

| 명령 | 설명 |
|------|------|
| `oodeep run` | GPU 학습 효율성 분석 |
| `oodeep profile` | 메모리/속도 프로파일링 |

---

## 문서/환경 스킬

### oodoc - 문서 자동화

| 명령 | 설명 |
|------|------|
| `oodoc run` | d0001~d0010 일괄 생성/업데이트 |
| `oodoc create [문서ID]` | 특정 문서 생성 |
| `oodoc optimize` | 문서 최적화 (크기/품질) |
| `oodoc check` | 품질+정합성 통합 검사 |
| `oodoc clear` | 이력 5개 초과 행 제거 |

### ooenv - 개발 환경 관리

| 명령 | 설명 |
|------|------|
| `ooenv run` | 환경 점검 + d0009_env.md 생성 |
| `ooenv tutorial` | 튜토리얼 생성/업데이트 |
| `ooenv uv check` | Python 의존성 확인 |
| `ooenv mcp` | MCP 서버 현황 |
| `ooenv cli` | CLI 도구 현황 |
| `ooenv settings` | Claude 설정 파일 관리 |
| `ooenv kill <target>` | 좀비 프로세스 종료 |

### oohistory - 이력 관리

| 명령 | 설명 |
|------|------|
| `oohistory run` | d0004 해결 항목 → d0010 아카이브 |

### oonote - 연구노트

| 명령 | 설명 |
|------|------|
| `oonote add "내용"` | 노트 추가 → d0011_note.md |
| `oonote list` | 노트 목록 |

### ootodo - TODO 관리

| 명령 | 설명 |
|------|------|
| `ootodo add "내용"` | TODO 추가 → d0004 |
| `ootodo done [ID]` | 항목 완료 처리 |
| `ootodo list` | 목록 확인 |

---

## 실행/유틸 스킬

### oorun - 자율 실행

| 명령 | 설명 |
|------|------|
| `oorun run` | TDD 기반 자율 빌드 실행 |

### oostreamlit - Streamlit 앱

| 명령 | 설명 |
|------|------|
| `oostreamlit run` | Streamlit 앱 실행/개발 |
| `oostreamlit build` | 앱 빌드 |

### oouv - 의존성 관리

| 명령 | 설명 |
|------|------|
| `oouv check` | 의존성 상태 확인 |
| `oouv add <pkg>` | 패키지 추가 |
| `oouv remove <pkg>` | 패키지 제거 |
| `oouv update` | 전체 업데이트 |

```bash
uv add numpy          # 패키지 추가
uv remove numpy       # 패키지 제거
uv sync               # 의존성 동기화
```

### oosync - 동기화

| 명령 | 설명 |
|------|------|
| `oosync run` | Vibe 환경 동기화 |
| `oosync status` | 동기화 상태 확인 |

---

## 콘텐츠 생성 스킬

### oopaper - 문헌 관리

| 명령 | 설명 |
|------|------|
| `oopaper run --lang en` | 영문 논문 처리 (PDF → 서머리) |
| `oopaper run --lang ko` | 국문 보고서 처리 |
| `oopaper status` | 처리 현황 (369편 등) |
| `oopaper add [경로]` | 논문 추가 |

경로: `D:/resilio/1_oais/03_paper/` | 이력: `D:/resilio/1_oais/03_paper/stt.xlsx`

### ooscrap - 유튜브/스크래핑

| 명령 | 설명 |
|------|------|
| `ooscrap summary` | 음성→텍스트 (자막우선, Whisper폴백) |
| `ooscrap download` | 동영상 다운로드 |
| `ooscrap music` | MP3 추출 |
| `ooscrap summary --url <URL>` | 특정 URL만 처리 |
| `ooscrap summary --force` | 중복 URL 재처리 |

입력: `04_scraping/00_down/01_유튜브다운로드.md` (## 서머리/동영상/음악 섹션)

### ooppt - PPT 생성

| 명령 | 설명 |
|------|------|
| `ooppt run [주제]` | PPT 생성 |
| `ooppt run --template [타입]` | 템플릿 지정 |

### ooword - Word 문서

| 명령 | 설명 |
|------|------|
| `ooword convert [파일.md]` | MD → DOCX 변환 |
| `ooword convert [파일.md] --pandoc` | LaTeX/Mermaid 포함 |
| `ooword quotation [파일.md]` | 견적서 변환 |

### oopdf - PDF 변환

| 명령 | 설명 |
|------|------|
| `oopdf convert [파일.md]` | MD → PDF 변환 |
| `oopdf compress [파일.pdf]` | PDF 압축 |

### ooreport - 리포트 생성

| 명령 | 설명 |
|------|------|
| `ooreport run [주제]` | 리포트 생성 (MD→PDF/PPTX/DOCX) |

### ooresearch - 연구 수행

| 명령 | 설명 |
|------|------|
| `ooresearch run --ai` | AI 도메인 SOTA 연구 |
| `ooresearch run [주제]` | 특정 주제 연구 |

### oosota - 학술 논문 작성

| 명령 | 설명 |
|------|------|
| `oosota run` | 실험결과 → 저널 논문 초안 |
| `oosota section [N]` | 특정 섹션 작성 |

### oosurvey - 설문 분석

| 명령 | 설명 |
|------|------|
| `oosurvey run [파일]` | 설문 데이터 분석 |

### oobook - 도서 요약

| 명령 | 설명 |
|------|------|
| `oobook run [제목]` | 도서 서머리 생성 |

### oohwp - 한글 문서

| 명령 | 설명 |
|------|------|
| `oohwp run [파일.md]` | MD → HWPX 변환 |
| `oohwp edit [파일.hwpx]` | HWPX 편집 |

---

## 스킬 관리 스킬

### ooskill - 스킬 최적화

| 명령 | 설명 |
|------|------|
| `ooskill validate` | 전체 스킬 검증 |
| `ooskill run` | 자동 최적화 |
| `ooskill run [스킬명]` | 특정 스킬 최적화 |
| `ooskill backup` | 스킬 환경 백업 |

### oohelp - 스킬 카탈로그 조회

| 명령 | 설명 |
|------|------|
| `oohelp` | .claude/CLAUDE.md 스킬 카탈로그 전체 표시 |
| `oohelp [스킬명]` | 특정 스킬 상세 (SKILL.md 표시) |
