"""
Sync student to Gurukul when created in EMS.
Calls Gurukul's /api/v1/auth/register with the same email/password so the student can log in to both.
"""
import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# Timeout so we don't block EMS if Gurukul is slow or down
GURUKUL_REGISTER_TIMEOUT = 10


def sync_student_to_gurukul(
    base_url: str,
    email: str,
    password: str,
    full_name: str,
) -> bool:
    """
    Register the student in Gurukul (POST /api/v1/auth/register).
    Returns True if created or already exists (400 email already registered), False on other errors.
    Sync/blocking; run from asyncio.to_thread() if needed.
    """
    url = base_url.rstrip("/") + "/api/v1/auth/register"
    payload = {
        "email": email,
        "password": password,
        "full_name": full_name or email.split("@")[0],
        "role": "STUDENT",
    }
    try:
        r = requests.post(url, json=payload, timeout=GURUKUL_REGISTER_TIMEOUT)
        if r.status_code in (200, 201):
            logger.info("Gurukul: created student %s", email)
            return True
        if r.status_code == 400:
            detail = (r.json() or {}).get("detail", "")
            if "already registered" in str(detail).lower():
                logger.info("Gurukul: student %s already exists", email)
                return True
            logger.warning("Gurukul register failed for %s: %s", email, detail)
            return False
        logger.warning("Gurukul register failed for %s: %s %s", email, r.status_code, r.text[:200])
        return False
    except Exception as e:
        logger.warning("Gurukul sync failed for %s: %s", email, e)
        return False
