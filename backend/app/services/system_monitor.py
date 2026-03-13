import psutil
import shutil
import time
import os
from fastapi import APIRouter
from app.services.voice_provider import provider

router = APIRouter(prefix="/system", tags=["Infrastructure"])

START_TIME = time.time()

@router.get("/health")
async def get_system_health():
    """
    Deep metrics for 24x7 stability monitoring.
    """
    # 1. Voice Engine Stats
    voice_stats = provider.get_status()
    
    # 2. Infrastructure Stats
    uptime_min = (time.time() - START_TIME) / 60
    
    # Disk Usage for audio directory
    audio_dir = "./audio" # Assuming audio files are stored here
    disk_info = {"total": 0, "used": 0, "free": 0}
    if os.path.exists(audio_dir):
        total, used, free = shutil.disk_usage(audio_dir)
        disk_info = {
            "total_gb": total // (2**30),
            "used_gb": used // (2**30),
            "free_gb": free // (2**30)
        }
    
    # 3. GPU Status (Simulated or via nvidia-smi if available)
    # For now we use the provider's gpu_mode as a proxy
    gpu_status = "Available" if voice_stats["gpu_mode"] else "Degraded (CPU Fallback)"
    
    return {
        "status": "healthy" if voice_stats["failure_count"] < 10 else "unstable",
        "service_uptime_min": int(uptime_min),
        "voice_engine": {
            "status": "running",
            "gpu": gpu_status,
            "requests_processed": voice_stats["total_requests"],
            "failures": voice_stats["failure_count"],
            "cache_hits": voice_stats["cache_size"]
        },
        "infrastructure": {
            "cpu_usage_percent": psutil.cpu_percent(),
            "memory_usage_percent": psutil.virtual_memory().percent,
            "disk_storage": disk_info
        },
        "orchestration_mode": "supervised"
    }
