from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import SecurityAlert, SecurityEvent, User
from app.routes.questions import require_role
from app.schemas.schemas import SecurityAlertOut, SecurityEventOut

router = APIRouter(prefix="/security", tags=["security"])


def _alert_out(a: SecurityAlert) -> dict:
    return {
        "id": a.id, "exam_id": a.exam_id, "session_id": a.session_id,
        "candidate_id": a.candidate_id, "risk_score": a.risk_score,
        "severity": a.severity, "reasons": a.reasons or [], "status": a.status,
        "created_at": a.created_at,
    }


@router.get("/alerts", response_model=list[SecurityAlertOut])
def list_alerts(
    admin: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    alerts = db.query(SecurityAlert).order_by(SecurityAlert.created_at.desc()).limit(200).all()
    return [_alert_out(a) for a in alerts]


@router.get("/alerts/{alert_id}", response_model=SecurityAlertOut)
def get_alert(
    alert_id: int,
    admin: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    alert = db.get(SecurityAlert, alert_id)
    if not alert:
        raise HTTPException(404, "Security alert not found")
    return _alert_out(alert)


@router.post("/alerts/{alert_id}/resolve", response_model=SecurityAlertOut)
def resolve_alert(
    alert_id: int,
    admin: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    alert = db.get(SecurityAlert, alert_id)
    if not alert:
        raise HTTPException(404, "Security alert not found")
    alert.status = "RESOLVED"
    alert.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)
    return _alert_out(alert)


@router.get("/events/{candidate_id}", response_model=list[SecurityEventOut])
def candidate_events(
    candidate_id: int,
    admin: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    events = (
        db.query(SecurityEvent)
        .filter(SecurityEvent.candidate_id == candidate_id)
        .order_by(SecurityEvent.created_at.desc())
        .limit(500)
        .all()
    )
    return [
        {"id": e.id, "event_type": e.event_type, "risk_score": e.risk_score, "created_at": e.created_at}
        for e in events
    ]
