# 시나리오: Streamlit 앱 개발

> 페이지 설계부터 구현, 테스트, 배포까지

---

## 개요

Streamlit 기반 웹 앱을 개발하는 워크플로우입니다. 페이지 구조 설계부터 구현, 실행, 코드 리뷰까지 oostreamlit 스킬이 전담합니다. 데이터 대시보드, 관리 도구, 프로토타입 등을 빠르게 만들 수 있습니다.

**이럴 때 사용:** 데이터 시각화 대시보드, 내부 관리 도구, 빠른 프로토타입이 필요할 때
**결과물:** Streamlit 멀티페이지 앱 (pages/*.py)


## 전체 흐름

```
oostreamlit plan → oostreamlit create → oodev run → oostreamlit run → oostreamlit review
```

---

## 1. 페이지 계획

```bash
oostreamlit plan   # 페이지 구조 설계
```

**설계 항목:**
- 페이지 목록 및 네비게이션 구조
- 각 페이지의 컴포넌트 구성
- 데이터 흐름 (입력 → 처리 → 출력)

---

## 2. 페이지 생성

```bash
oostreamlit create <page_name>   # 새 페이지 생성
```

**생성되는 파일:**
- `pages/{page_name}.py` (페이지 코드)
- 기본 레이아웃, 세션 상태 초기화 포함

---

## 3. 구현

```bash
oodev run          # TDD 기반 구현
```

**Streamlit 개발 팁:**
- `st.session_state`로 상태 관리
- `st.cache_data`로 데이터 캐싱
- `st.sidebar`로 설정 패널

---

## 4. 실행 및 테스트

```bash
oostreamlit run    # Streamlit 앱 실행
oorun run          # 자율 빌드 (TDD Builder)
```

**테스트 확인:**
- UI 렌더링 정상 여부
- 데이터 바인딩
- 에러 핸들링

---

## 5. 코드 리뷰

```bash
oostreamlit review # Streamlit 전용 코드 리뷰
```

**리뷰 항목:**
- 성능 (불필요한 리렌더링)
- UX (사용자 흐름)
- 코드 구조 (재사용성)

---

## FAQ

**Q: 멀티 페이지 앱은?**
A: `pages/` 폴더에 페이지별 .py 파일 생성. Streamlit이 자동 인식.

**Q: DB 연동은?**
A: `oodb run`으로 DB 설계 후 Streamlit에서 연결.

---

> 관련: [기본 워크플로우](11_기본개발워크플로우.md) | [DB 개발](00_doc/tutorial/14_DB포함개발.md)
