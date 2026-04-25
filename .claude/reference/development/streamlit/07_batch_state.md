# 배치/상태 머신 패턴

## session_state 기반 상태 머신

> 장시간 작업(크롤링, 배치 수집)을 Streamlit rerun 사이클에서 진행률과 함께 처리하는 패턴.

```python
# 상태 초기화 (페이지 최초 로드 시)
if "crawl_phase" not in st.session_state:
    st.session_state.crawl_phase = "idle"    # idle | crawling | syncing | done
if "crawl_pending" not in st.session_state:
    st.session_state.crawl_pending = []
if "crawl_results" not in st.session_state:
    st.session_state.crawl_results = []

# --- idle 상태 ---
if st.session_state.crawl_phase == "idle":
    sites = get_active_sites()  # DB에서 수집 대상 사이트 로드
    if st.button("수집 시작", type="primary"):
        st.session_state.crawl_pending = list(sites.items())  # [(name, url), ...]
        st.session_state.crawl_results = []
        st.session_state.crawl_phase = "crawling"
        st.rerun()

# --- crawling 상태 ---
if st.session_state.crawl_phase == "crawling":
    total = len(st.session_state.crawl_pending) + len(st.session_state.crawl_results)
    done = len(st.session_state.crawl_results)

    if st.session_state.crawl_pending:
        name, url = st.session_state.crawl_pending.pop(0)
        st.progress(done / total, text=f"수집 중: {name}")

        result = run_news_pipeline(sites={name: url})
        st.session_state.crawl_results.append(result)
        st.rerun()  # 다음 사이트로
    else:
        st.session_state.crawl_phase = "done"
        st.rerun()

# --- done 상태 ---
if st.session_state.crawl_phase == "done":
    st.success(f"수집 완료: {len(st.session_state.crawl_results)}개 사이트")

    # 결과 표시
    for r in st.session_state.crawl_results:
        st.write(f"- {r['site']}: {r['count']}건")

    if st.button("초기화"):
        st.session_state.crawl_phase = "idle"
        st.rerun()
```

## 상태 전이도

```
[idle]
  ↓ 시작 버튼
[crawling] ← st.rerun() 루프 (사이트 1개씩 처리)
  ↓ pending 소진
[done]
  ↓ 초기화
[idle]
```

## 단순 진행률 패턴 (한 번에 처리)

```python
# 전체 목록을 미리 받아 한 번에 처리 (단순하지만 UI 블로킹)
items = get_items()
progress_bar = st.progress(0)
status_text = st.empty()

for i, item in enumerate(items):
    status_text.text(f"처리 중: {item['name']} ({i+1}/{len(items)})")
    process(item)
    progress_bar.progress((i + 1) / len(items))

status_text.text("완료!")
```

> **주의**: 이 방식은 rerun 없이 블로킹 처리 — 수십 건 이하 소량 작업에만 적합.
> 수백 건 이상은 session_state 상태 머신 사용.

## 배치 스케줄러 자동 실행

```python
# login.py 또는 공통 초기화 위치
from oais.batch import init_scheduler, start_scheduler, add_job

if "scheduler_started" not in st.session_state:
    init_scheduler()

    # 매일 오전 6시 뉴스 수집
    add_job(func=run_news_pipeline, trigger="cron",
            hour=6, minute=0, id="news_daily", replace_existing=True)

    # 매주 월요일 오전 2시 일자리 수집
    add_job(func=run_job_pipeline, trigger="cron",
            day_of_week="mon", hour=2, id="job_weekly", replace_existing=True)

    start_scheduler()
    st.session_state["scheduler_started"] = True
```

## 주의사항

- `st.rerun()` 남용 시 성능 저하 — 상태 전이가 필요할 때만 호출
- 배치 도중 페이지 이탈 시 `crawl_pending`이 남은 채로 다음 방문에 이어서 실행됨 — 필요 시 초기화 버튼 제공
- 멀티 사용자 환경에서 `session_state`는 사용자별 독립 — 공유 진행 상태가 필요하면 DB 테이블에 저장
