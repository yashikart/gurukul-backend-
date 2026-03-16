"""
system_monitor.py — Runtime Monitoring for Gurukul Infrastructure

Exposes /system/health endpoint with deep metrics:
  - TTS service health (ping Vaani engine)
  - Vaani model load status
  - GPU availability
  - Disk usage in audio directory
  - Service uptime
  - CPU and memory usage
  - Request statistics from VoiceProvider
"""

import time
import os
import subprocess
import logging
import psutil
import shutil
import requests
from fastapi import APIRouter
from app.services.voice_provider import provider
from app.core.config import settings

logger = logging.getLogger("SystemMonitor")

router = APIRouter(prefix="/system", tags=["Infrastructure"])

START_TIME = time.time()


def _check_vaani_health() -> dict:
    """Ping the Vaani engine health endpoint."""
    vaani_url = getattr(settings, "VAANI_API_URL", "http://localhost:8008")
    try:
        resp = requests.get(f"{vaani_url}/health", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "reachable": True,
                "status": data.get("status", "unknown"),
                "device": data.get("device", "unknown"),
                "model_loaded": data.get("status") == "healthy",
            }
        return {"reachable": True, "status": f"error_{resp.status_code}", "model_loaded": False}
    except requests.exceptions.ConnectionError:
        return {"reachable": False, "status": "unreachable", "model_loaded": False}
    except Exception as e:
        return {"reachable": False, "status": f"error: {str(e)[:80]}", "model_loaded": False}


def _check_gpu() -> dict:
    """Check GPU availability via nvidia-smi or torch."""
    gpu_info = {"available": False, "device_name": "N/A", "memory_used_mb": 0, "memory_total_mb": 0}

    # Method 1: Try torch (if available in this process)
    try:
        import torch
        if torch.cuda.is_available():
            gpu_info["available"] = True
            gpu_info["device_name"] = torch.cuda.get_device_name(0)
            gpu_info["memory_used_mb"] = round(torch.cuda.memory_allocated(0) / (1024 ** 2), 1)
            gpu_info["memory_total_mb"] = round(torch.cuda.get_device_properties(0).total_mem / (1024 ** 2), 1)
            return gpu_info
    except ImportError:
        pass
    except Exception:
        pass

    # Method 2: Try nvidia-smi
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.used,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split(",")
            if len(parts) >= 3:
                gpu_info["available"] = True
                gpu_info["device_name"] = parts[0].strip()
                gpu_info["memory_used_mb"] = float(parts[1].strip())
                gpu_info["memory_total_mb"] = float(parts[2].strip())
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    except Exception:
        pass

    return gpu_info


def _check_disk_usage() -> dict:
    """Check disk usage for audio output directories."""
    audio_dirs = [
        os.path.join(os.getcwd(), "audio"),
        os.path.join(os.getcwd(), "audio_samples"),
        os.path.join(os.getcwd(), "..", "vaani-engine", "audio_samples"),
    ]

    disk_info = {"total_gb": 0, "used_gb": 0, "free_gb": 0, "audio_files_count": 0}

    for audio_dir in audio_dirs:
        if os.path.exists(audio_dir):
            total, used, free = shutil.disk_usage(audio_dir)
            disk_info["total_gb"] = round(total / (2 ** 30), 2)
            disk_info["used_gb"] = round(used / (2 ** 30), 2)
            disk_info["free_gb"] = round(free / (2 ** 30), 2)
            try:
                audio_files = [f for f in os.listdir(audio_dir) if f.endswith(('.wav', '.mp3'))]
                disk_info["audio_files_count"] += len(audio_files)
            except OSError:
                pass
            break  # Use first found directory for disk stats

    return disk_info


@router.get("/health")
async def get_system_health():
    """
    Deep metrics for 24x7 stability monitoring.

    Returns comprehensive system health including:
    - Overall status
    - TTS service connectivity
    - Vaani model load state
    - GPU availability
    - Service uptime
    - Voice engine request statistics
    - Infrastructure metrics (CPU, memory, disk)
    """
    # 1. Voice Engine Stats
    voice_stats = provider.get_status()

    # 2. Vaani Engine Health (direct ping)
    vaani_health = _check_vaani_health()

    # 3. GPU Status
    gpu_info = _check_gpu()

    # 4. Infrastructure
    uptime_min = (time.time() - START_TIME) / 60
    disk_info = _check_disk_usage()

    # 5. Determine overall status
    overall_status = "healthy"
    if voice_stats["failure_count"] >= 10:
        overall_status = "degraded"
    if not vaani_health["reachable"]:
        overall_status = "degraded"

    return {
        "status": overall_status,
        "tts_service": "running" if vaani_health["reachable"] else "stopped",
        "vaani_model": "loaded" if vaani_health.get("model_loaded") else "not_loaded",
        "gpu": "available" if (gpu_info["available"] or voice_stats["gpu_mode"]) else "unavailable (CPU fallback)",
        "uptime_minutes": int(uptime_min),
        "voice_engine": {
            "status": "running" if vaani_health["reachable"] else "stopped",
            "vaani_url": getattr(settings, "VAANI_API_URL", "http://localhost:8008"),
            "vaani_device": vaani_health.get("device", "unknown"),
            "model_loaded": vaani_health.get("model_loaded", False),
            "gpu_mode": voice_stats["gpu_mode"],
            "requests_processed": voice_stats["total_requests"],
            "successful_requests": voice_stats.get("successful_requests", 0),
            "failures": voice_stats["failure_count"],
            "timeouts": voice_stats.get("timeout_count", 0),
            "cache_size": voice_stats["cache_size"],
            "cache_hits": voice_stats.get("cache_hits", 0),
            "queue_depth": voice_stats.get("queue_depth", 0),
            "max_concurrency": voice_stats.get("max_concurrency", 3),
            "max_input_chars": voice_stats.get("max_input_chars", 5000),
            "inference_timeout_s": voice_stats.get("inference_timeout_s", 20),
        },
        "gpu_details": gpu_info,
        "infrastructure": {
            "cpu_usage_percent": psutil.cpu_percent(),
            "memory_usage_percent": psutil.virtual_memory().percent,
            "memory_available_mb": round(psutil.virtual_memory().available / (1024 ** 2), 1),
            "disk_storage": disk_info,
        },
        "orchestration_mode": "supervised",
    }
