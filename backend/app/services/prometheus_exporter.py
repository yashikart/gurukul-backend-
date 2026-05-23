import time
from fastapi import APIRouter, Response
from app.services.system_metrics import (
    _total_requests,
    _error_count,
    _status_counts,
    _voice_latencies,
    _ai_latencies,
    _avg,
    _p95,
    _start_time,
    _lock
)

prometheus_router = APIRouter(tags=["Observability"])

@prometheus_router.get("/metrics")
async def prometheus_metrics():
    """
    Exposes Gurukul system metrics in the official Prometheus text format.
    """
    lines = []
    
    with _lock:
        total = _total_requests
        errors = _error_count
        status_snapshot = dict(_status_counts)
        voice_avg_ms = _avg(_voice_latencies)
        voice_p95_ms = _p95(_voice_latencies)
        ai_avg_ms = _avg(_ai_latencies)
        ai_p95_ms = _p95(_ai_latencies)

    uptime_s = time.time() - _start_time
    
    # Try importing psutil for CPU/Memory
    cpu_percent = 0.0
    mem_percent = 0.0
    try:
        import psutil
        cpu_percent = psutil.cpu_percent()
        mem_percent = psutil.virtual_memory().percent
    except Exception:
        pass

    # 1. Total Requests Metric
    lines.append("# HELP gurukul_requests_total Total number of HTTP requests processed.")
    lines.append("# TYPE gurukul_requests_total counter")
    lines.append(f"gurukul_requests_total {total}")

    # 2. Requests per Status Code
    lines.append("# HELP gurukul_requests_by_status_code_total Total requests partitioned by HTTP status code.")
    lines.append("# TYPE gurukul_requests_by_status_code_total counter")
    for status, count in status_snapshot.items():
        lines.append(f'gurukul_requests_by_status_code_total{{status="{status}"}} {count}')

    # 3. Total Errors
    lines.append("# HELP gurukul_errors_total Total number of HTTP 5xx errors.")
    lines.append("# TYPE gurukul_errors_total counter")
    lines.append(f"gurukul_errors_total {errors}")

    # 4. Latencies
    lines.append("# HELP gurukul_voice_latency_seconds_avg Average voice inference latency in seconds.")
    lines.append("# TYPE gurukul_voice_latency_seconds_avg gauge")
    lines.append(f"gurukul_voice_latency_seconds_avg {voice_avg_ms / 1000.0}")

    lines.append("# HELP gurukul_voice_latency_seconds_p95 p95 voice inference latency in seconds.")
    lines.append("# TYPE gurukul_voice_latency_seconds_p95 gauge")
    lines.append(f"gurukul_voice_latency_seconds_p95 {voice_p95_ms / 1000.0}")

    lines.append("# HELP gurukul_ai_latency_seconds_avg Average AI/LLM inference latency in seconds.")
    lines.append("# TYPE gurukul_ai_latency_seconds_avg gauge")
    lines.append(f"gurukul_ai_latency_seconds_avg {ai_avg_ms / 1000.0}")

    # 5. Uptime
    lines.append("# HELP gurukul_uptime_seconds Process uptime in seconds.")
    lines.append("# TYPE gurukul_uptime_seconds gauge")
    lines.append(f"gurukul_uptime_seconds {round(uptime_s, 2)}")

    # 6. System Resource Usage
    lines.append("# HELP gurukul_cpu_usage_ratio CPU usage ratio.")
    lines.append("# TYPE gurukul_cpu_usage_ratio gauge")
    lines.append(f"gurukul_cpu_usage_ratio {cpu_percent / 100.0}")

    lines.append("# HELP gurukul_memory_usage_ratio Memory usage ratio.")
    lines.append("# TYPE gurukul_memory_usage_ratio gauge")
    lines.append(f"gurukul_memory_usage_ratio {mem_percent / 100.0}")

    # Join with newlines and return as plain text
    content = "\n".join(lines) + "\n"
    return Response(content=content, media_type="text/plain; version=0.0.4")
