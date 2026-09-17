"""Security Anomaly and Risk Engine Module.

Features explainable rule-based scoring and an abstract BaseRiskEngine interface
allowing seamless plug-and-play for future machine learning anomaly detectors.
"""
from __future__ import annotations

import abc
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.models import SecurityAlert, SecurityEvent


def _hash(value: str | None) -> str | None:
    if not value:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class BaseRiskEngine(abc.ABC):
    """Abstract Risk Engine interface for security event anomaly evaluation."""

    @abc.abstractmethod
    def evaluate(
        self,
        db: Session,
        *,
        event_type: str,
        exam_id: int | None,
        session_id: int | None,
        candidate_id: int | None,
        ip_address: str | None = None,
        device_id: str | None = None,
        user_agent: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[int, list[str]]:
        """Return (risk_score, list_of_explainable_reasons)."""
        pass


class RuleBasedRiskEngine(BaseRiskEngine):
    """Explainable rule-based security risk engine."""

    def evaluate(
        self,
        db: Session,
        *,
        event_type: str,
        exam_id: int | None,
        session_id: int | None,
        candidate_id: int | None,
        ip_address: str | None = None,
        device_id: str | None = None,
        user_agent: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[int, list[str]]:
        now = _now()
        cutoff_1m = now - timedelta(minutes=1)
        cutoff_10s = now - timedelta(seconds=10)

        recent = []
        if candidate_id is not None:
            recent = (
                db.query(SecurityEvent)
                .filter(
                    SecurityEvent.candidate_id == candidate_id,
                    SecurityEvent.created_at >= cutoff_1m,
                )
                .order_by(SecurityEvent.created_at.desc())
                .limit(200)
                .all()
            )

        score = 0
        reasons: list[str] = []
        device_hash = _hash(device_id)
        ua_hash = _hash(user_agent)
        meta = metadata or {}

        # 1. RAPID_QUESTION_REQUESTS
        q10 = [e for e in recent if e.event_type == "QUESTION_REQUEST" and _as_utc(e.created_at) >= cutoff_10s]
        if len(q10) >= 8 or event_type == "RAPID_QUESTION_REQUESTS":
            score += 25
            reasons.append(f"RAPID_QUESTION_REQUESTS: {len(q10)} question requests in 10 seconds")
        elif len(q10) >= 5:
            score += 12
            reasons.append("RAPID_QUESTION_REQUESTS: 5+ question requests in 10 seconds")

        # 2. EXCESSIVE ANSWER SUBMISSIONS / TOKEN REPLAY
        a1 = [e for e in recent if e.event_type == "ANSWER_SUBMITTED"]
        if len(a1) >= 20 or event_type == "TOKEN_REPLAY":
            score += 25
            reasons.append("TOKEN_REPLAY / Excessive answer submissions in 1 minute")

        # 3. DEVICE_CHANGED / IP_CHANGED / USER_AGENT DRIFT
        prior_devices = {e.device_id_hash for e in recent if e.device_id_hash}
        prior_ips = {e.ip_address for e in recent if e.ip_address}
        prior_uas = {e.user_agent_hash for e in recent if e.user_agent_hash}

        if (device_hash and prior_devices and device_hash not in prior_devices) or event_type == "DEVICE_CHANGED":
            score += 35
            reasons.append("DEVICE_CHANGED: Device identity changed during active exam session")

        if (ip_address and prior_ips and ip_address not in prior_ips) or event_type == "IP_CHANGED":
            score += 25
            reasons.append("IP_CHANGED: Source IP changed during active exam session")

        if ua_hash and prior_uas and ua_hash not in prior_uas:
            score += 15
            reasons.append("Browser/client fingerprint changed during session")

        # 4. EXAM_SESSION_REUSED / MULTIPLE_FAILED_LOGINS
        starts = [e for e in recent if e.event_type == "SESSION_START"]
        if len(starts) >= 2 or event_type == "EXAM_SESSION_REUSED":
            score += 20
            reasons.append("EXAM_SESSION_REUSED: Multiple exam-session start attempts in 1 minute")

        if event_type == "MULTIPLE_FAILED_LOGINS":
            score += 30
            reasons.append("MULTIPLE_FAILED_LOGINS: Excessive login failures detected")

        # 5. CENTRE_MISMATCH / UNREGISTERED_DEVICE
        if event_type == "CENTRE_MISMATCH" or meta.get("centre_mismatch"):
            score += 40
            reasons.append("CENTRE_MISMATCH: Candidate attempted exam at unauthorized centre")

        if event_type == "UNREGISTERED_DEVICE" or meta.get("unregistered_device"):
            score += 45
            reasons.append("UNREGISTERED_DEVICE: Access attempted from unregistered hardware")

        # 6. HIGH_ITEM_EXPOSURE
        if event_type == "HIGH_ITEM_EXPOSURE" or meta.get("high_exposure"):
            score += 15
            reasons.append("HIGH_ITEM_EXPOSURE: Session contains items exceeding exposure threshold")

        # 7. UNUSUAL_LOGIN_TIME
        if event_type == "UNUSUAL_LOGIN_TIME":
            score += 15
            reasons.append("UNUSUAL_LOGIN_TIME: Login outside scheduled operational hours")

        return min(score, 100), reasons


class MLRiskEngineAdapter(BaseRiskEngine):
    """Adapter class for future Machine Learning model integration.

    Falls back to RuleBasedRiskEngine if model is not trained/available.
    """

    def __init__(self, model_path: str | None = None):
        self.model_path = model_path
        self.rule_engine = RuleBasedRiskEngine()

    def evaluate(
        self,
        db: Session,
        *,
        event_type: str,
        exam_id: int | None,
        session_id: int | None,
        candidate_id: int | None,
        ip_address: str | None = None,
        device_id: str | None = None,
        user_agent: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[int, list[str]]:
        # Simulation / placeholder for trained ML inference.
        # Uses explainable rule engine as underlying baseline engine.
        return self.rule_engine.evaluate(
            db,
            event_type=event_type,
            exam_id=exam_id,
            session_id=session_id,
            candidate_id=candidate_id,
            ip_address=ip_address,
            device_id=device_id,
            user_agent=user_agent,
            metadata=metadata,
        )


# Global active risk engine instance
_DEFAULT_ENGINE: BaseRiskEngine = RuleBasedRiskEngine()


def assess_event(
    db: Session,
    *,
    event_type: str,
    exam_id: int | None,
    session_id: int | None,
    candidate_id: int | None,
    ip_address: str | None = None,
    device_id: str | None = None,
    user_agent: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> tuple[int, list[str]]:
    return _DEFAULT_ENGINE.evaluate(
        db,
        event_type=event_type,
        exam_id=exam_id,
        session_id=session_id,
        candidate_id=candidate_id,
        ip_address=ip_address,
        device_id=device_id,
        user_agent=user_agent,
        metadata=metadata,
    )


def record_event(
    db: Session,
    *,
    event_type: str,
    exam_id: int | None,
    session_id: int | None,
    candidate_id: int | None,
    ip_address: str | None = None,
    device_id: str | None = None,
    user_agent: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> tuple[SecurityEvent, SecurityAlert | None]:
    score, reasons = assess_event(
        db,
        event_type=event_type,
        exam_id=exam_id,
        session_id=session_id,
        candidate_id=candidate_id,
        ip_address=ip_address,
        device_id=device_id,
        user_agent=user_agent,
        metadata=metadata,
    )
    event = SecurityEvent(
        exam_id=exam_id,
        session_id=session_id,
        candidate_id=candidate_id,
        event_type=event_type,
        ip_address=ip_address,
        device_id_hash=_hash(device_id),
        user_agent_hash=_hash(user_agent),
        event_metadata=metadata or {},
        risk_score=score,
    )
    db.add(event)
    alert = None
    if score >= 70:
        alert = SecurityAlert(
            exam_id=exam_id,
            session_id=session_id,
            candidate_id=candidate_id,
            risk_score=score,
            severity="CRITICAL" if score >= 90 else "HIGH",
            reasons=reasons or ["Composite anomaly score exceeded threshold"],
            status="OPEN",
        )
        db.add(alert)
    elif score >= 40:
        alert = SecurityAlert(
            exam_id=exam_id,
            session_id=session_id,
            candidate_id=candidate_id,
            risk_score=score,
            severity="MEDIUM",
            reasons=reasons or ["Composite anomaly score exceeded threshold"],
            status="OPEN",
        )
        db.add(alert)
    db.flush()
    return event, alert
