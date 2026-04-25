# oohwp check 체크리스트

> oohwp 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md, scripts/oohwp_run.py 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | lxml 설치 | `uv run --with lxml python -c "import lxml"` 성공 여부 | ERROR |
| C04 | 스크립트 파일 | build_hwpx.py, text_extract.py 존재 여부 | CRITICAL |
| C05 | 템플릿 디렉터리 | templates/ 하위 gonmun/report/minutes/proposal 존재 여부 | WARNING |

---

> `oohwp check` 역할 수행 기준 (환경 확인용)
> 결과: ✅ Pass / ❌ Fail / ⚠️ Warning

## 사전 조건

- [ ] lxml 설치 여부: `uv run --with lxml python -c "import lxml"` 실행으로 lxml 의존성 확인
- [ ] 스크립트 파일 존재: `build_hwpx.py`, `text_extract.py`, `validate.py`, `analyze_template.py` 가 scripts/ 에 존재하는지 확인
- [ ] 템플릿 디렉터리 존재: `templates/gonmun/`, `templates/report/`, `templates/minutes/`, `templates/proposal/` 가 모두 존재하는지 확인
- [ ] hwpx-format.md 존재: `references/hwpx-format.md` 파일이 존재하는지 확인

## 실행 환경

- [ ] office/pack.py, unpack.py 존재: `scripts/office/pack.py`, `scripts/office/unpack.py` 가 존재하는지 확인
- [ ] 템플릿 XML 유효성: 각 템플릿의 `header.xml`, `section0.xml` 파일이 존재하고 비어있지 않은지 확인
- [ ] Python 버전 호환성: `uv run python --version`으로 Python 3.13+ 여부 확인

## 산출물/출력

- [ ] validate.py 실행 가능: `uv run --with lxml python .claude/skills/oohwp/scripts/validate.py --help` 실행 성공 여부 확인
- [ ] build_hwpx.py 실행 가능: `uv run --with lxml python .claude/skills/oohwp/scripts/build_hwpx.py --help` 실행 성공 여부 확인
- [ ] examples/ 디렉터리 존재: 예제 파일 디렉터리가 존재하는지 확인 (없으면 경고)

## 품질 기준

- [ ] mimetype 파일 확인: 템플릿의 `mimetype` 파일이 존재하고 올바른 값(`application/hwp+zip`)을 가지는지 확인
- [ ] 네임스페이스 일관성: 템플릿 XML 파일들이 필수 네임스페이스(`hp:`, `hs:`, `hh:`, `hc:`)를 포함하는지 확인
- [ ] secPr 포함 여부: `templates/*/section0.xml` 파일에 `secPr` 요소가 포함되어 있는지 확인
