# oopaper status 출력 템플릿

> oopaper status 명령의 고정 출력 섹션 템플릿.
> 스크립트는 `_shared.template_loader.load_template_block()` 으로 이 파일의 `template` 블록을 로드한다.

## 사용 변수

| 변수명 | 설명 | 예시 |
|--------|------|------|
| `{down_count}` | 00_down 대기 PDF 수 | 7 |
| `{total}` | 전체 논문 폴더 수 | 362 |
| `{x_count}` / `{x_pct}` | 상태 X 건수 / 비율 | 10 / 2 |
| `{e_count}` / `{e_pct}` | 상태 E 건수 / 비율 (영문 추출 완료) | 426 / 30 |
| `{s_count}` / `{s_pct}` | 상태 S 건수 / 비율 | 150 / 41 |
| `{t_count}` / `{t_pct}` | 상태 T 건수 / 비율 | 100 / 27 |
| `{o_count}` / `{o_pct}` | 상태 O 건수 / 비율 | 102 / 28 |

## 템플릿: status_table

```template
## 논문 현황: {total}개

| 상태 | 설명 | 건수 | 비율 |
|:----:|------|:----:|:----:|
| X | 미처리 | {x_count} | {x_pct}% |
| E | 영문 추출 완료 | {e_count} | {e_pct}% |
| S | 서머리 완료 | {s_count} | {s_pct}% |
| T | 번역 완료 | {t_count} | {t_pct}% |
| O | 완료 | {o_count} | {o_pct}% |
| **합계** | | **{total}** | 100% |
```

## 템플릿: commands_footer (정적)

```commands_footer
## 명령어

  run              : 완전 자동 파이프라인 (7 Phase)
  status           : 현황 표시 (이 화면)
  sync-list        : paper_list.md 동기화
  fix              : 무결성 체크
  delete-broken    : 깨진 파일 삭제
  download         : 리스트 기반 PDF 자동 다운로드
  clean-duplicates : 중복 파일 정리
  ref-update       : 서머리에 참고문헌 추가
```
