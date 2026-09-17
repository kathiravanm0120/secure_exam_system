"""Central Audit Logging Service (Phase 26).

Structured, sanitized audit event recorder ensuring no sensitive question plaintext,
passwords, or bearer tokens are persisted in system logs.
"""
from __future__ import annotations

import logging
import json
import uuid
from datetime import datetime, timezone
from typing import Any

# Configure standard logger
logger = logging.getLogger("secure_exam_audit")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[AUDIT] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def log_audit_event(
    *,
    event_type: str,
    actor_id: int | None = None,
    role: str | None = None,
    ip_address: str | None = None,
    device_id: str | None = None,
    exam_id: int | None = None,
    question_id: int | None = None,
    session_id: int | None = None,
    result: str = "SUCCESS",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Record a structured, sanitized audit log entry."""
    event_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    # Sanitize metadata to prevent sensitive content leakage
    sanitized_meta = {}
    if metadata:
        for k, v in metadata.items():
            if any(secret_key in k.lower() for secret_key in ("password", "token", "secret", "answer", "content")):
                sanitized_meta[k] = "[REDACTED]"
            else:
                sanitized_meta[k] = v

    record = {
        "event_id": event_id,
        "timestamp": now,
        "event_type": event_type,
        "actor_id": actor_id,
        "role": role,
        "ip_address": ip_address,
        "device_id": device_id,
        "exam_id": exam_id,
        "question_id": question_id,
        "session_id": session_id,
        "result": result,
        "metadata": sanitized_meta,
    }

    logger.info(json.dumps(record))
    return record
