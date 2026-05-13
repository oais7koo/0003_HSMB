# FastAPI 배치 엔진 패턴

## 아키텍처: 이벤트 + 폴링 폴백

```
작업 접수 (POST)
    ↓
task_event.set()  ← 즉시 깨우기
    ↓
[배치 루프]
    ├─ event.wait(timeout=POLL_INTERVAL)  ← 이벤트 없으면 폴링
    ├─ recover_stale_tasks()              ← 타임아웃 복구 (60초마다)
    ├─ cleanup_old_files()                ← 파일 정리 (1시간마다)
    ├─ claim_next_task("high")            ← 우선순위 선점
    ├─ claim_next_task("normal")
    └─ process_task(task)                 ← 비동기 처리
```

## engine.py 핵심 구조

```python
async def start_batch_loop(task_event: asyncio.Event):
    last_recovery = last_cleanup = time.time()

    while True:
        try:
            # 이벤트 대기 (폴링 폴백)
            try:
                await asyncio.wait_for(
                    task_event.wait(),
                    timeout=config.BATCH_POLL_INTERVAL
                )
                task_event.clear()
            except asyncio.TimeoutError:
                pass

            now = time.time()

            # 타임아웃 복구 (60초마다)
            if now - last_recovery > 60:
                recover_stale_tasks()
                last_recovery = now

            # 파일 정리 (1시간마다)
            if now - last_cleanup > 3600:
                cleanup_old_files()
                last_cleanup = now

            # 우선순위 큐 선점 (high → normal)
            task = claim_next_task("high") or claim_next_task("normal")
            if task:
                await process_task(task)

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"배치 루프 에러: {e}")
            await asyncio.sleep(5)
```

## 원자적 선점 (claim)

```python
def claim_next_task(priority="normal"):
    """동시성 안전한 작업 선점"""
    conn = get_db_connection()
    try:
        row = conn.execute("""
            SELECT task_id FROM api_task_queue
            WHERE status = 'pending' AND priority = ?
            ORDER BY created_at ASC LIMIT 1
        """, (priority,)).fetchone()

        if row:
            conn.execute("""
                UPDATE api_task_queue
                SET status = 'processing', started_at = ?
                WHERE task_id = ? AND status = 'pending'
            """, (datetime.now().isoformat(), row["task_id"]))
            conn.commit()
            return get_task_by_id(row["task_id"])
    finally:
        conn.close()
    return None
```

## 작업 처리 흐름 (process_task)

```python
async def process_task(task):
    task_id = task["task_id"]
    identifier = task["identifier"]

    try:
        # 1. 외부 DB 상태 업데이트 (선택)
        update_status_process(identifier)

        # 2. SCP 다운로드 (필요 시)
        if task.get("remote_file_path"):
            local_path = scp_download(task["remote_file_path"])
            update_input_path(task_id, local_path)

        # 3. 핸들러 디스패치
        result = dispatch_task(task)

        # 4. 결과 처리
        if not result["success"]:
            mark_failed(task_id, result["message"])
            update_status_fail(identifier, result["message"])
            return

        # 5. SCP 업로드 (파일 있으면)
        if result.get("output_file_path"):
            scp_success = scp_transfer(result["output_file_path"])
            if not scp_success:
                handle_infra_failure(task_id, "SCP 전송 실패")
                return

        # 6. 완료
        mark_done(task_id, result)
        update_status_success(identifier, result)

    except Exception as e:
        handle_infra_failure(task_id, str(e))
```

## 인프라 실패 재시도

```python
def handle_infra_failure(task_id, error_msg):
    conn = get_db_connection()
    task = get_task_by_id(task_id)
    retry_count = task["retry_count"] + 1

    if retry_count < config.BATCH_MAX_RETRY:
        # pending으로 복구 → 자동 재시도
        conn.execute("""
            UPDATE api_task_queue
            SET status = 'pending', retry_count = ?, error_message = ?
            WHERE task_id = ?
        """, (retry_count, error_msg, task_id))
    else:
        # 최종 실패
        conn.execute("""
            UPDATE api_task_queue
            SET status = 'failed', retry_count = ?, error_message = ?,
                completed_at = ?
            WHERE task_id = ?
        """, (retry_count, error_msg, datetime.now().isoformat(), task_id))
    conn.commit()
```

## 핸들러 디스패치 패턴 (handlers.py)

```python
HANDLER_MAP = {
    "task_type_a": handle_type_a,
    "task_type_b": handle_type_b,
}

def dispatch_task(task):
    handler = HANDLER_MAP.get(task["task_type"])
    if not handler:
        return {"success": False, "message": f"미지원 업무: {task['task_type']}"}
    params = json.loads(task["params"] or "{}")
    return handler(task, params)
```

## 핸들러 공통 구조

```python
def handle_type_a(task, params):
    try:
        # 1. 입력 파일 검증
        input_path = task.get("input_file_path")
        if not input_path or not os.path.exists(input_path):
            return {"success": False, "message": "입력 파일 없음"}

        # 2. 비즈니스 로직 (oais 함수 호출)
        result_data = process_something(input_path, **params)

        # 3. 결과 파일 생성
        output_path = os.path.join(config.OUTPUT_DIR, f"result_{task['task_id']}.xlsx")
        save_excel(result_data, output_path)

        return {
            "success": True,
            "output_file_path": output_path,
            "filename": os.path.basename(output_path),
            "data": result_data,
        }
    except Exception as e:
        return {"success": False, "message": str(e)}
```

## 에러 분류

| 유형 | 재시도 | 처리 |
|------|--------|------|
| 비즈니스 에러 | X | 즉시 failed |
| 인프라 에러 (SCP, 네트워크) | O (최대 3회) | pending 복구 |
| 타임아웃 (5분 초과) | O | stale 복구 |
