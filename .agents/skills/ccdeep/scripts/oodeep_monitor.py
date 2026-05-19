"""ccdeep GPU 모니터링 스크립트 v01

nvidia-smi 기반 GPU 사용률/메모리 실시간 모니터링.
JSON 형식으로 결과를 출력하여 에이전트가 파싱할 수 있도록 한다.

Usage:
    uv run python .agents/skills/ccdeep/scripts/oodeep_monitor.py [subcommand] [options]

Subcommands:
    status      GPU 현재 상태 1회 조회
    monitor     연속 모니터링 (--interval, --count)
    check       Python 스크립트 GPU 효율성 사전 분석
    find-pid    특정 PID의 GPU 사용량 조회
"""

import subprocess
import json
import sys
import time
import re
import ast
from pathlib import Path


def get_gpu_status():
    """nvidia-smi로 GPU 상태 조회. JSON dict 반환."""
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw,power.limit",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return {"error": "nvidia-smi 실행 실패", "stderr": result.stderr.strip()}

        gpus = []
        for i, line in enumerate(result.stdout.strip().split("\n")):
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 7:
                mem_used = float(parts[2])
                mem_total = float(parts[3])
                mem_pct = (mem_used / mem_total * 100) if mem_total > 0 else 0
                gpus.append({
                    "index": i,
                    "name": parts[0],
                    "utilization_pct": float(parts[1]),
                    "memory_used_mb": mem_used,
                    "memory_total_mb": mem_total,
                    "memory_pct": round(mem_pct, 1),
                    "temperature_c": float(parts[4]),
                    "power_draw_w": float(parts[5]) if parts[5] != "[N/A]" else None,
                    "power_limit_w": float(parts[6]) if parts[6] != "[N/A]" else None,
                })
        return {"gpus": gpus, "count": len(gpus)}
    except FileNotFoundError:
        return {"error": "nvidia-smi를 찾을 수 없습니다. NVIDIA 드라이버가 설치되어 있는지 확인하세요."}
    except subprocess.TimeoutExpired:
        return {"error": "nvidia-smi 응답 시간 초과"}


def get_gpu_processes():
    """GPU에서 실행 중인 프로세스 목록 조회."""
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-compute-apps=pid,used_gpu_memory,name",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return []

        processes = []
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 3:
                processes.append({
                    "pid": int(parts[0]),
                    "memory_mb": float(parts[1]),
                    "name": parts[2],
                })
        return processes
    except Exception:
        return []


def monitor_continuous(interval=30, count=3):
    """연속 모니터링. interval초 간격으로 count회 측정 후 평균 반환."""
    samples = []
    for i in range(count):
        status = get_gpu_status()
        if "error" in status:
            print(json.dumps(status, ensure_ascii=False))
            return status

        samples.append(status)
        print(json.dumps({
            "sample": i + 1,
            "total": count,
            "gpus": status["gpus"],
        }, ensure_ascii=False))

        if i < count - 1:
            time.sleep(interval)

    # 평균 계산
    if samples and samples[0].get("gpus"):
        gpu_count = len(samples[0]["gpus"])
        averages = []
        for g in range(gpu_count):
            avg_util = sum(s["gpus"][g]["utilization_pct"] for s in samples) / len(samples)
            avg_mem_pct = sum(s["gpus"][g]["memory_pct"] for s in samples) / len(samples)
            averages.append({
                "index": g,
                "name": samples[0]["gpus"][g]["name"],
                "avg_utilization_pct": round(avg_util, 1),
                "avg_memory_pct": round(avg_mem_pct, 1),
            })

        result = {"averages": averages, "sample_count": len(samples)}
        print(json.dumps(result, ensure_ascii=False))
        return result

    return {"error": "샘플 수집 실패"}


def check_script(script_path):
    """Python 스크립트의 GPU 효율성을 정적 분석."""
    path = Path(script_path)
    if not path.exists():
        print(json.dumps({"error": f"파일 없음: {script_path}"}, ensure_ascii=False))
        return

    content = path.read_text(encoding="utf-8")
    issues = []
    suggestions = []

    # batch_size 분석
    bs_match = re.search(r"batch[_\s]*size\s*[=:]\s*(\d+)", content, re.IGNORECASE)
    if bs_match:
        bs = int(bs_match.group(1))
        if bs < 16:
            issues.append(f"batch_size={bs}로 매우 작음")
            suggestions.append(f"batch_size를 {bs * 4} 이상으로 증가 권장")
        elif bs < 32:
            issues.append(f"batch_size={bs}로 작을 수 있음")
            suggestions.append(f"batch_size를 {bs * 2}로 증가 시도 권장")

    # num_workers 분석
    nw_match = re.search(r"num_workers\s*[=:]\s*(\d+)", content)
    if nw_match:
        nw = int(nw_match.group(1))
        if nw == 0:
            issues.append("num_workers=0 (데이터 로딩 병목)")
            suggestions.append("num_workers=4 이상 설정 권장")
    elif "DataLoader" in content:
        issues.append("num_workers 미지정 (기본값 0)")
        suggestions.append("DataLoader에 num_workers=4 추가 권장")

    # pin_memory 분석
    if "DataLoader" in content and "pin_memory" not in content:
        issues.append("pin_memory 미설정")
        suggestions.append("DataLoader에 pin_memory=True 추가 권장")

    # mixed precision 분석
    if "torch" in content and "amp" not in content and "autocast" not in content:
        issues.append("mixed precision 미사용")
        suggestions.append("torch.cuda.amp.autocast() 사용 권장")

    # non_blocking 분석
    to_device_count = len(re.findall(r"\.to\(device\)", content))
    non_blocking_count = len(re.findall(r"non_blocking\s*=\s*True", content))
    if to_device_count > 0 and non_blocking_count == 0:
        issues.append(f".to(device) {to_device_count}회 사용, non_blocking 미사용")
        suggestions.append(".to(device, non_blocking=True) 사용 권장")

    # cudnn.benchmark 분석
    if "torch" in content and "cudnn.benchmark" not in content:
        suggestions.append("torch.backends.cudnn.benchmark = True 추가 권장")

    # torch.compile 분석
    if "torch" in content and "torch.compile" not in content:
        suggestions.append("PyTorch 2.0+: torch.compile(model) 사용 검토")

    result = {
        "script": str(script_path),
        "issues": issues,
        "suggestions": suggestions,
        "issue_count": len(issues),
        "severity": "high" if len(issues) >= 3 else "medium" if len(issues) >= 1 else "low",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def print_status_table(status):
    """GPU 상태를 테이블 형식으로 출력."""
    if "error" in status:
        print(f"Error: {status['error']}")
        return

    print("# ccdeep - GPU 상태\n")
    for gpu in status.get("gpus", []):
        util = gpu["utilization_pct"]
        mem_pct = gpu["memory_pct"]
        util_status = "양호" if util >= 50 else "비효율"
        mem_status = "양호" if mem_pct >= 30 else "비효율"

        print(f"## GPU {gpu['index']}: {gpu['name']}\n")
        print(f"| 항목 | 값 | 상태 |")
        print(f"|------|-----|------|")
        print(f"| 사용률 | {util}% | {util_status} |")
        print(f"| 메모리 | {gpu['memory_used_mb']:.0f}MB / {gpu['memory_total_mb']:.0f}MB ({mem_pct}%) | {mem_status} |")
        print(f"| 온도 | {gpu['temperature_c']}°C | - |")
        if gpu.get("power_draw_w"):
            print(f"| 전력 | {gpu['power_draw_w']}W / {gpu['power_limit_w']}W | - |")
        print()

    processes = get_gpu_processes()
    if processes:
        print("## GPU 프로세스\n")
        print("| PID | 메모리 | 프로세스 |")
        print("|-----|--------|---------|")
        for p in processes:
            print(f"| {p['pid']} | {p['memory_mb']:.0f}MB | {p['name']} |")
        print()


def main():
    if len(sys.argv) < 2:
        print("Usage: oodeep_monitor.py <subcommand> [options]")
        print("  status              GPU 현재 상태")
        print("  monitor [--interval N] [--count N]  연속 모니터링")
        print("  check <script.py>   스크립트 사전 분석")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "status":
        status = get_gpu_status()
        print_status_table(status)

    elif cmd == "monitor":
        interval = 30
        count = 3
        for i, arg in enumerate(sys.argv[2:], 2):
            if arg == "--interval" and i + 1 < len(sys.argv):
                interval = int(sys.argv[i + 1])
            elif arg == "--count" and i + 1 < len(sys.argv):
                count = int(sys.argv[i + 1])
        monitor_continuous(interval=interval, count=count)

    elif cmd == "check":
        if len(sys.argv) < 3:
            print("Error: 스크립트 경로를 지정하세요")
            sys.exit(1)
        check_script(sys.argv[2])

    elif cmd == "json":
        # JSON 출력 모드 (에이전트 파싱용)
        status = get_gpu_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

    else:
        print(f"Unknown subcommand: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
