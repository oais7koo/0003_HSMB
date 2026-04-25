# oohwp Tutorial

> HWPX 문서 생성 및 템플릿 기반 자동화 | 버전: v03 | 카테고리: content

## §1. 자주 쓰는 명령어 (Quick Commands)

```bash
# 기본 HWPX 생성
oohwp create --template gonmun --title "공문 제목"

# 보고서 템플릿으로 생성
oohwp create --template report --title "월간 보고서"

# 의사록 생성
oohwp create --template minutes --title "회의록"

# 제안서 생성
oohwp create --template proposal --title "프로젝트 제안서"
```

## §2. 권장 사용 흐름 (Recommended Workflow)

1. **템플릿 선택**: `oohwp list-templates` → 적절한 템플릿 확인
2. **문서 생성**: `oohwp create --template [TYPE] --title [TITLE]`
3. **콘텐츠 작성**: 마크다운 또는 직접 XML 편집
4. **페이지 조정**: `oohwp adjust-pages --file output.hwpx`
5. **최종 저장**: 자동 HWPX 패키징

## §3. 실전 시나리오 (Practical Scenarios)

**시나리오 1: 공식 문서(공문) 생성**
- 기본 공문 템플릿으로 생성 → 수신처, 발신처 자동 채움
- 마크다운 콘텐츠 변환 → HWPX 문서로 저장
- 페이지 레이아웃 자동 조정

**시나리오 2: 월간 보고서 작성**
- 보고서 템플릿 선택 → 챕터별 구조 제공
- 마크다운 섹션 삽입 → XML 자동 생성
- 목차 및 페이지 번호 자동 계산

**시나리오 3: 회의록 기록**
- 의사록 템플릿 → 참석자, 일시, 안건 자동 입력
- 토론 내용 마크다운 → HWPX 변환
- 결정사항 체크리스트 자동 생성

## §4. 핵심 개념 (Core Concepts)

**HWPX 구조**:
- HWPX = ZIP 컨테이너 + XML 메타데이터
- content.xml: 문서 본문
- styles.xml: 스타일 정의
- meta.xml: 메타정보 (제목, 저자, 작성일)

**템플릿 종류**:
- `gonmun`: 공식 문서/공문
- `report`: 보고서/분석 보고
- `minutes`: 회의록/의사록
- `proposal`: 제안서/기획안

**XML-First 접근**:
- 모든 변환은 XML 단계에서 처리
- 최종 ZIP 패킹 전에 검증
- 페이지 계산 최적화

## §5. 명령어 레퍼런스 (Command Reference)

```yaml
oohwp:
  create:
    desc: 템플릿 기반 HWPX 생성
    usage: oohwp create --template [TYPE] --title [TITLE] [--content FILE]
    templates: gonmun, report, minutes, proposal
    
  list-templates:
    desc: 사용 가능한 템플릿 목록 조회
    usage: oohwp list-templates [--category TYPE]
    
  adjust-pages:
    desc: 페이지 레이아웃 자동 조정
    usage: oohwp adjust-pages --file [FILE] [--page-size A4|Letter]
    
  validate:
    desc: HWPX 파일 구조 검증
    usage: oohwp validate --file [FILE]
    
  export:
    desc: 다른 형식으로 내보내기
    usage: oohwp export --file [FILE] --format [pdf|docx|txt]
```

## §6. 내부 구조 (Internal Structure)

**페이지 계산 알고리즘**:
```python
# 콘텐츠 크기 → 페이지 수 자동 계산
pages = (content_length / avg_chars_per_page) + 1
```

**XML 생성 프로세스**:
1. 마크다운 파싱
2. XML 요소 생성
3. 스타일 적용
4. 메타데이터 삽입
5. HWPX ZIP 패킹

## §7. 통합 패턴 (Integration Patterns)

**다른 스킬과의 연계**:
- `ooreport`: 마크다운 보고서 → `oohwp create` HWPX로 변환
- `ooppt`: 슬라이드 내용 → 공문/보고서로 재구성
- `oodoc`: 문서 자동화 시 템플릿 활용

**파일 흐름**:
- MD 파일 → XML 변환 → HWPX 생성 → PDF 내보내기

## §8. 예제 및 응용 (Examples & Applications)

**예제 1: 공식 보고서 자동화**
```bash
oohwp create --template report --title "Q1 성과 보고서" --content report.md
# 결과: report_20260414.hwpx (자동 저장)
```

**예제 2: 배치 문서 생성**
```bash
for file in *.md; do
  oohwp create --template gonmun --title "$(basename $file)" --content "$file"
done
```

**예제 3: 페이지 최적화**
```bash
oohwp adjust-pages --file doc.hwpx --page-size A4 --margin 2cm
```

## §9. 문제 해결 (Troubleshooting)

**Q: 페이지 레이아웃이 깨졌다**
- `oohwp adjust-pages` 실행 → 자동 정렬
- 마크다운 포맷 검증 → 긴 문단 분할

**Q: 메타데이터가 제대로 저장되지 않는다**
- `oohwp validate` 실행 → 에러 확인
- meta.xml 직접 편집 → 재저장

**Q: 이미지 포함이 안 된다**
- 이미지 경로 절대경로로 변경
- 이미지 형식 검증 (JPG, PNG 권장)

## §10. 고급 팁 (Advanced Tips)

1. **커스텀 템플릿**: 기본 템플릿 복제 → 스타일 커스터마이징
2. **배치 처리**: 여러 마크다운 파일 동시 변환
3. **메타데이터 자동화**: 파일명 → 제목/저자 자동 추출
4. **스타일 상속**: 템플릿 기본 스타일 → 커스텀 CSS 적용

## §11. 다음 단계 (Next Steps)

- **PDF 내보내기**: `oohwp export --format pdf` → 최종 배포 버전
- **버전 관리**: 템플릿 버전 추적 및 업데이트
- **협업 지원**: 댓글 및 변경사항 추적 기능

---

> 생성일: 2026-04-14 | ootutorial v03
