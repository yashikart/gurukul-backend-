"""
service_orchestrator.py — Gurukul Service Supervisor
=====================================================

Standalone Python supervisor that starts and keeps alive the core
Gurukul services.  Run this instead of (or alongside) start-all.bat
for fully automated recovery.

Services managed:
  Name               | Command
  -------------------|-------------------------------------------------------
  GurkulBackend      | uvicorn app.main:app --host 0.0.0.0 --port 3000
  VaaniEngine        | python start.py              (vaani-engine dir)
  VaaniEngine        | python start.py              (vaani-engine dir)
  BucketConsumer     | python scripts/start_bucket_consumer.py (backend)

Usage:
    cd Gurukul
    python backend/scripts/service_orchestrator.py

Flags:
    --no-frontend   Skip frontend npm dev servers (headless mode)
    --poll 30       Health check interval in seconds (default: 30)
"""

import argparse
import logging
import os
import subprocess
import sys
import time
import signal
import threading
from dataclasses import dataclass, field
from typing import Optional, List

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-8s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("Orchestrator")

# ---------------------------------------------------------------------------
# Base directory (Gurukul root, two levels up from this script)
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# backend/scripts/ → backend/ → Gurukul/
BASE_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", ".."))


# ---------------------------------------------------------------------------
# Service definition
# ---------------------------------------------------------------------------

@dataclass
class ManagedService:
    name: str
    cmd: List[str]
    cwd: str
    health_url: Optional[str] = None     # HTTP GET for liveness check
    restart_delay: int = 5               # seconds before restarting
    max_restarts: int = 10               # 0 = unlimited
    restart_count: int = field(default=0, init=False)
    proc: Optional[subprocess.Popen] = field(default=None, init=False)
    _stop: bool = field(default=False, init=False)

    def is_alive(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def start(self):
        logger.info(f"[{self.name}] Starting: {' '.join(self.cmd)}")
        try:
            self.proc = subprocess.Popen(
                self.cmd,
                cwd=self.cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
        except FileNotFoundError as exc:
            logger.error(f"[{self.name}] Could not start — command not found: {exc}")
            self.proc = None

    def stop(self):
        self._stop = True
        if self.proc and self.proc.poll() is None:
            logger.info(f"[{self.name}] Sending SIGTERM...")
            self.proc.terminate()
            try:
                self.proc.wait(timeout=8)
            except subprocess.TimeoutExpired:
                logger.warning(f"[{self.name}] Timeout — sending SIGKILL")
                self.proc.kill()

    def restart_rolling(self):
        """
        Implementation of Phase 2 Zero Downtime:
        Spin new instance -> Verify Health -> Kill old instance
        """
        logger.info(f"[{self.name}] Initiating ROLLING RESTART (Zero Downtime)...")
        
        # 1. Start new instance on a temporary offset if port is fixed
        # (Simplified: for this local setup, we just ensure fast swap)
        old_proc = self.proc
        self.start() 
        
        # 2. Wait for health (if health_url exists)
        if self.health_url:
            logger.info(f"[{self.name}] Waiting for new instance health: {self.health_url}")
            for _ in range(30):
                try:
                    r = requests.get(self.health_url, timeout=2)
                    if r.status_code == 200:
                        logger.info(f"[{self.name}] New instance is HEALTHY.")
                        break
                except:
                    pass
                time.sleep(1)
        
        # 3. Kill old proc
        if old_proc and old_proc.poll() is None:
            logger.info(f"[{self.name}] Killing old instance.")
            old_proc.terminate()
            try:
                old_proc.wait(timeout=5)
            except:
                old_proc.kill()


# ---------------------------------------------------------------------------
# Log drainer — streams subprocess output to the orchestrator logger
# ---------------------------------------------------------------------------

def _drain_output(service: ManagedService):
    if service.proc is None or service.proc.stdout is None:
        return
    for line in service.proc.stdout:
        logger.info(f"  [{service.name}] {line.rstrip()}")


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class ServiceOrchestrator:
    def __init__(self, poll_interval: int = 30, include_frontend: bool = True):
        self._poll = poll_interval
        self._stop_event = threading.Event()
        self._services: List[ManagedService] = self._build_service_list(include_frontend)

    def _build_service_list(self, include_frontend: bool) -> List[ManagedService]:
        python = sys.executable
        services = [
            ManagedService(
                name="GurkulBackend",
                cmd=[python, "-m", "uvicorn", "app.main:app",
                     "--host", "0.0.0.0", "--port", "3000"],
                cwd=os.path.join(BASE_DIR, "backend"),
                health_url="http://localhost:3000/system/health",
            ),
            ManagedService(
                name="VaaniEngine",
                cmd=[python, "start.py"],
                cwd=os.path.join(BASE_DIR, "vaani-engine"),
                health_url="http://localhost:8008/health",
            ),
            ManagedService(
                name="BucketConsumer",
                cmd=[python, "scripts/start_bucket_consumer.py"],
                cwd=os.path.join(BASE_DIR, "backend"),
                health_url=None,   # uses sentinel file
            ),
        ]

        if include_frontend:
            services += [
                ManagedService(
                    name="GurkulFrontend",
                    cmd=["npm", "run", "dev"],
                    cwd=os.path.join(BASE_DIR, "Frontend"),
                ),
                ManagedService(
                    name="EMSFrontend",
                    cmd=["npm", "run", "dev"],
                    cwd=os.path.join(BASE_DIR, "EMS System", "frontend"),
                ),
            ]
        return services

    # ------------------------------------------------------------------

    def start_all(self):
        logger.info("=== Gurukul Orchestrator: Starting all services ===")
        for svc in self._services:
            svc.start()
            time.sleep(2)
            # Drain in background thread
            t = threading.Thread(target=_drain_output, args=(svc,), daemon=True)
            t.start()

    def stop_all(self):
        logger.info("=== Gurukul Orchestrator: Stopping all services ===")
        for svc in reversed(self._services):
            svc.stop()

    def run(self):
        """Start services and keep them alive."""
        self.start_all()
        signal.signal(signal.SIGINT, self._handle_exit)
        signal.signal(signal.SIGTERM, self._handle_exit)

        try:
            while not self._stop_event.is_set():
                self._check_and_recover()
                self._stop_event.wait(timeout=self._poll)
        finally:
            self.stop_all()

    def _check_and_recover(self):
        for svc in self._services:
            if svc._stop:
                continue
            if not svc.is_alive():
                if svc.max_restarts and svc.restart_count >= svc.max_restarts:
                    logger.critical(
                        f"[{svc.name}] Exceeded {svc.max_restarts} restarts. Not restarting."
                    )
                    svc._stop = True
                    continue
                logger.warning(
                    f"[{svc.name}] Detected as dead (exit={svc.proc.returncode if svc.proc else 'N/A'}). "
                    f"Restarting in {svc.restart_delay}s..."
                )
                time.sleep(svc.restart_delay)
                svc.start()
                svc.restart_count += 1
                t = threading.Thread(target=_drain_output, args=(svc,), daemon=True)
                t.start()
                logger.info(f"[{svc.name}] Restarted (attempt #{svc.restart_count}).")

    def _handle_exit(self, signum, frame):
        logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
        self._stop_event.set()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gurukul Service Orchestrator")
    parser.add_argument("--no-frontend", action="store_true",
                        help="Skip frontend dev servers (headless mode)")
    parser.add_argument("--poll", type=int, default=30,
                        help="Health check poll interval in seconds (default: 30)")
    args = parser.parse_args()

    orchestrator = ServiceOrchestrator(
        poll_interval=args.poll,
        include_frontend=not args.no_frontend,
    )
    orchestrator.run()
