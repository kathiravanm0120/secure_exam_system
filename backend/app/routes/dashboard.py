from __future__ import annotations

from collections import Counter
from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.blockchain.service import get_chain, verify_chain
from app.database import get_db
from app.models.models import Exam, ExamSession, Question, SecurityAlert, User
from app.routes.questions import require_role

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

DASHBOARD_HTML = Path(__file__).resolve().parents[1] / "static" / "admin.html"


@router.get("", include_in_schema=False)
def dashboard_page():
    return FileResponse(DASHBOARD_HTML)


@router.get("/summary")
def dashboard_summary(
    admin: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    question_status = {
        status: count
        for status, count in db.query(Question.status, func.count(Question.id)).group_by(Question.status).all()
    }
    exposure_status = {
        status: count
        for status, count in db.query(Question.exposure_status, func.count(Question.id)).group_by(Question.exposure_status).all()
    }
    role_counts = {
        role: count
        for role, count in db.query(User.role, func.count(User.id)).group_by(User.role).all()
    }
    exam_status = {
        status: count
        for status, count in db.query(Exam.status, func.count(Exam.id)).group_by(Exam.status).all()
    }
    session_status = {
        status: count
        for status, count in db.query(ExamSession.status, func.count(ExamSession.id)).group_by(ExamSession.status).all()
    }
    alert_status = {
        status: count
        for status, count in db.query(SecurityAlert.status, func.count(SecurityAlert.id)).group_by(SecurityAlert.status).all()
    }

    critical_questions = (
        db.query(Question)
        .order_by(Question.exposure_count.desc())
        .limit(10)
        .all()
    )
    recent_alerts = (
        db.query(SecurityAlert)
        .order_by(SecurityAlert.created_at.desc())
        .limit(10)
        .all()
    )
    chain = get_chain()
    recent_chain = list(reversed(chain[-10:]))

    return {
        "totals": {
            "users": db.query(func.count(User.id)).scalar() or 0,
            "questions": db.query(func.count(Question.id)).scalar() or 0,
            "approved_questions": db.query(func.count(Question.id)).filter(Question.status == "APPROVED").scalar() or 0,
            "exposed_questions": db.query(func.count(Question.id)).filter(Question.exposure_count > 0).scalar() or 0,
            "exams": db.query(func.count(Exam.id)).scalar() or 0,
            "active_sessions": db.query(func.count(ExamSession.id)).filter(ExamSession.status == "ACTIVE").scalar() or 0,
            "open_alerts": db.query(func.count(SecurityAlert.id)).filter(SecurityAlert.status == "OPEN").scalar() or 0,
        },
        "question_status": question_status,
        "exposure_status": exposure_status,
        "role_counts": role_counts,
        "exam_status": exam_status,
        "session_status": session_status,
        "alert_status": alert_status,
        "chain": {
            "verification": verify_chain(),
            "recent": recent_chain,
        },
        "exposure_ranking": [
            {
                "id": q.id,
                "subject": q.subject,
                "topic": q.topic,
                "difficulty": q.difficulty,
                "exposure_count": q.exposure_count,
                "exposure_status": q.exposure_status,
            }
            for q in critical_questions
        ],
        "recent_alerts": [
            {
                "id": a.id,
                "risk_score": a.risk_score,
                "severity": a.severity,
                "status": a.status,
                "candidate_id": a.candidate_id,
                "exam_id": a.exam_id,
                "reasons": a.reasons or [],
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in recent_alerts
        ],
    }
