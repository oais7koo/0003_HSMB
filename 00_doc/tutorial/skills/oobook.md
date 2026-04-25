# oobook Tutorial

> 도서 서머리 자동 생성 AI | 버전: v03 | 카테고리: content

## §1 이유 (Reason)

도서 한 권의 내용을 체계적으로 정리하고 다양한 형식(마크다운, Word, 슬라이드, 플래시카드)으로 변환해야 할 때 사용합니다. 강의자료 준비, 학습 자료 생성, 출판 자료화 등에 활용됩니다.

## §2 빠른 시작 (Quick Start)

```bash
oobook run --input data/ps1001_박기성/BOOKQAI.xlsx --title "책 제목"
```

결과: `data/ps9003/` 하위에 마크다운, Word, 슬라이드 자동 생성

## §3 자주 쓰는 명령 (Frequent Commands)

| 명령어 | 설명 |
|--------|------|
| `oobook run` | 전체 도서 요약 생성 |
| `oobook to-word` | 마크다운 → Word 변환 |
| `oobook to-slide` | 마크다운 → 슬라이드 설계 |
| `oobook flashcard` | 플래시카드/퀴즈 생성 |
| `oobook batch` | 배치 처리 (여러 도서) |

## §4 권장 흐름 (Recommended Flow)

1. BOOKQAI.xlsx 준비 (각 장별 요약 등록)
2. `oobook run` 실행 → 마크다운 자동 생성
3. `oobook to-word` → 강의 자료용 Word 생성
4. `oobook to-slide` → 프레젠테이션 설계
5. `oobook flashcard` → 학습용 문제 생성

## §5 전체 명령어 (All Commands)

```
oobook help               # 도움말
oobook version            # 버전 정보
oobook run [OPTIONS]      # 도서 요약 생성
oobook to-word [FILE]     # Word 변환
oobook to-slide [FILE]    # 슬라이드 설계
oobook flashcard [FILE]   # 플래시카드 생성
oobook batch [DIR]        # 배치 처리
```

## §6 상세 사용법 (Detailed Usage)

**기본 실행:**
- 입력: `data/ps1001_박기성/BOOKQAI.xlsx`
- 출력: `data/ps9003/01_도서/*.md`, `data/ps9003/02_워드/*.docx`

**생성 형식:**
1. 각 장별 요약
2. 핵심 구절 30개
3. 핵심 키워드
4. 강의안
5. 강의 전문
6. 슬라이드 설계
7. 플래시카드/퀴즈

## §7 실전 예시 (Real Examples)

```bash
oobook run --input data/ps1001_박기성/BOOKQAI.xlsx --title "경제학 원론"
```

## §8 입출력 (Input/Output)

**입력:** Excel 파일 (BOOKQAI.xlsx)
**출력:** 마크다운, Word, JSON, Excel

## §9 FAQ

**Q: 도서 요약의 정확도는?**
A: AI 기반이므로 재검토 권장.

**Q: 여러 도서를 한 번에 처리할 수 있나?**
A: 네, `oobook batch` 로 배치 처리 가능.

## §10 서브에이전트 (Sub-agents)

- writer, slide-designer, flashcard-gen

## §11 관련 스킬 (Related Skills)

- `ooword`, `ooppt`, `ooreport`, `oodev`

---

**버전**: v03 | **카테고리**: content | **업데이트**: 2026-04-14
