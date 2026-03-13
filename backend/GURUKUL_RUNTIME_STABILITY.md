# GURUKUL_RUNTIME_STABILITY.md

This document explains the infrastructure hardening implemented to ensure Gurukul operates 24x7 without human intervention.

## 1. Unified Startup Orchestration
All services are started in a deterministic order using `start_gurukul_services.sh`:
1. **Database Recovery**: Ensures SQL and MongoDB are reachable.
2. **Voice Engine (Vaani)**: Loads the XTTS model into the GPU.
3. **Gurukul Backend**: Starts the main API layer.
4. **Monitoring Watchdog**: Starts the background supervisor.

## 2. Self-Healing Watchdog (`watchdog_runner.py`)
The system employs a "supervisor" pattern:
- **Health Checks**: Every 30 seconds, it pings the `/system/health` metrics endpoint.
- **Auto-Recovery**: If the backend becomes unresponsive or reports consecutive failures, the watchdog automatically terminates stale processes and restarts the service cluster.
- **Fail-Safe**: If memory usage exceeds safe limits, the watchdog triggers a graceful reload.

## 3. Voice Engine Guardrails (`VoiceProvider`)
The `VoiceProvider` module enforces structural discipline on AI inference:
- **Inference Queue**: Max 3 concurrent requests (using `asyncio.Semaphore`).
- **Timing Constraint**: 20-second timeout to prevent "hanging" endpoints.
- **Hardware Elasticity**: Automatically falls back from GPU to CPU mode if VRAM is exhausted.
- **Input Sanitization**: 5000 character hard limit per request.

## 4. Operational Monitoring
Admins can monitor real-time system state at `/system/health`.
Sample Metrics:
- **Uptime**: Total service runtime.
- **GPU Availability**: Current inference hardware mode.
- **Request Cache**: Efficiency of the in-memory audio cache.
- **Disk Saturation**: Available storage in the audio generation directory.

---
**Gurukul Runtime Stability: HARDENED**
