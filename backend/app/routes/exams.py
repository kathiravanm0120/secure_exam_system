from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.blockchain.service import add_event
from app.database import get_db
from app.models.models import Exam, ExamAnswer, ExamSession, ExamSessionQuestion, ExamReleaseApproval, Question, User, CentreDevice, ExamCandidateAssignment, ExamCentreAssignment
from app.routes.questions import current_user, require_role
from app.schemas.schemas import (
    AnswerOut,
    AnswerSubmit,
    CandidatePaperOut,
    CandidateQuestionOut,
    ExamCreate,
    ExamOut,
    ExamSessionOut,
    ExposureOut,
    ReleaseApprovalOut,
    ReleaseStatusOut,
    PaperValidationReportOut,
)
from app.security.encryption import decrypt_question
from app.security.anomaly import record_event

router = APIRouter(prefix="/exams", tags=["exams"])
EXPOSURE_LIMIT = int(os.getenv("QUESTION_EXPOSURE_LIMIT", "100"))
RELEASE_WINDOW_MINUTES = int(os.getenv("EXAM_RELEASE_WINDOW_MINUTES", "15"))
REQUIRED_RELEASE_APPROVALS = int(os.getenv("EXAM_REQUIRED_RELEASE_APPROVALS", "2"))
DEVICE_HEADER = "X-Exam-Device-ID"
DEVICE_TOKEN_HEADER = "X-Exam-Device-Token"
CENTRE_HEADER = "X-Exam-Centre-ID"
SESSION_HEADER = "X-Exam-Session-Token"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_dt(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _exam_out(exam: Exam) -> dict:
    return {
        "id": exam.id,
        "name": exam.name,
        "subject": exam.subject,
        "starts_at": exam.starts_at,
        "ends_at": exam.ends_at,
        "blueprint": exam.blueprint,
        "status": exam.status,
    }


def _release_window_open(exam: Exam, now: datetime | None = None) -> bool:
    now = now or _utc_now()
    starts_at = _normalize_dt(exam.starts_at)
    ends_at = _normalize_dt(exam.ends_at)
    window_start = starts_at.timestamp() - (RELEASE_WINDOW_MINUTES * 60)
    return window_start <= now.timestamp() <= ends_at.timestamp()


def _release_status(exam: Exam, db: Session, now: datetime | None = None) -> dict:
    approvals = (
        db.query(ExamReleaseApproval)
        .filter(ExamReleaseApproval.exam_id == exam.id)
        .order_by(ExamReleaseApproval.approved_at.asc())
        .all()
    )
    approver_ids = [a.officer_id for a in approvals]
    return {
        "exam_id": exam.id,
        "status": exam.status,
        "release_window_open": _release_window_open(exam, now),
        "required_approvals": REQUIRED_RELEASE_APPROVALS,
        "approval_count": len(approver_ids),
        "approver_ids": approver_ids,
        "released": exam.status == "RELEASED",
    }


def _get_session(
    exam_id: int,
    candidate: User,
    db: Session,
    session_token: str,
    device_id: str,
) -> ExamSession:
    if not session_token or len(session_token) < 32:
        raise HTTPException(401, "Missing or invalid exam session token")
    if not device_id or len(device_id) < 8:
        raise HTTPException(400, "A valid X-Exam-Device-ID is required")

    session = (
        db.query(ExamSession)
        .filter(ExamSession.exam_id == exam_id, ExamSession.candidate_id == candidate.id)
        .first()
    )
    if not session:
        raise HTTPException(404, "Exam has not been started for this candidate")

    if session.status != "ACTIVE":
        raise HTTPException(403, "Exam session is not active")

    if not hmac.compare_digest(session.session_token_hash, _sha256_text(session_token)):
        raise HTTPException(401, "Invalid or expired exam session token")
    if not hmac.compare_digest(session.device_id_hash, _sha256_text(device_id)):
        raise HTTPException(403, "Exam session is bound to a different device")

    exam = session.exam
    now = _utc_now()
    if now < _normalize_dt(exam.starts_at) or now > _normalize_dt(exam.ends_at):
        raise HTTPException(403, "Exam is not currently open")

    session.last_heartbeat_at = now
    return session


def _authorize_candidate_endpoint(
    exam_id: int,
    candidate: User,
    db: Session,
    session_token: str,
    device_id: str,
    device_token: str,
    centre_id: int,
) -> ExamSession:
    session = _get_session(exam_id, candidate, db, session_token, device_id)
    assignment = (db.query(ExamCandidateAssignment)
        .filter(ExamCandidateAssignment.exam_id == exam_id, ExamCandidateAssignment.candidate_id == candidate.id)
        .first())
    if not assignment or assignment.identity_status != "VERIFIED" or assignment.centre_id != centre_id:
        raise HTTPException(403, "Candidate identity/centre authorization failed")
    device = (db.query(CentreDevice)
        .filter(CentreDevice.centre_id == centre_id, CentreDevice.device_code == device_id, CentreDevice.status == "ACTIVE")
        .first())
    if not device or not hmac.compare_digest(device.device_token_hash, _sha256_text(device_token)):
        raise HTTPException(403, "Unauthorized examination device")
    device.last_seen_at = _utc_now()
    return session


@router.post("", response_model=ExamOut, status_code=201)
def create_exam(
    data: ExamCreate,
    admin: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    starts_at = _normalize_dt(data.starts_at)
    ends_at = _normalize_dt(data.ends_at)
    if ends_at <= starts_at:
        raise HTTPException(400, "ends_at must be after starts_at")

    blueprint = [rule.model_dump() for rule in data.rules]
    exam = Exam(
        name=data.name,
        subject=data.subject,
        starts_at=starts_at,
        ends_at=ends_at,
        blueprint=blueprint,
        created_by=admin.id,
        status="SCHEDULED",
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    add_event(
        "EXAM_CREATED",
        {"exam_id": exam.id, "name": exam.name, "subject": exam.subject, "created_by": admin.id, "blueprint": blueprint},
    )
    return _exam_out(exam)


@router.get("/{exam_id}/release-status", response_model=ReleaseStatusOut)
def get_release_status(
    exam_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    exam = db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(404, "Exam not found")
    return _release_status(exam, db)


@router.post("/{exam_id}/release/approve", response_model=ReleaseApprovalOut, status_code=201)
def approve_release(
    exam_id: int,
    request: Request,
    officer: User = Depends(require_role("EXAM_OFFICER")),
    db: Session = Depends(get_db),
    device_id: str = Header("", alias=DEVICE_HEADER),
):
    exam = db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(404, "Exam not found")
    now = _utc_now()
    if exam.status == "RELEASED":
        raise HTTPException(409, "Exam is already released")
    if not _release_window_open(exam, now):
        raise HTTPException(403, f"Release approval is allowed only {RELEASE_WINDOW_MINUTES} minutes before the exam")

    existing = (
        db.query(ExamReleaseApproval)
        .filter(ExamReleaseApproval.exam_id == exam_id, ExamReleaseApproval.officer_id == officer.id)
        .first()
    )
    if existing:
        raise HTTPException(409, "This officer has already approved this exam")

    approval = ExamReleaseApproval(
        exam_id=exam_id,
        officer_id=officer.id,
        approved_at=now,
        device_id_hash=_sha256_text(device_id) if device_id else None,
        ip_address=request.client.host if request.client else None,
    )
    db.add(approval)
    record_event(
        db, event_type="EXAM_RELEASE_APPROVAL", exam_id=exam_id, session_id=None,
        candidate_id=None, ip_address=request.client.host if request.client else None,
        device_id=device_id or None, user_agent=request.headers.get("user-agent"),
        metadata={"officer_id": officer.id, "approval_count_before": db.query(ExamReleaseApproval).filter(ExamReleaseApproval.exam_id == exam_id).count()},
    )
    db.commit()
    db.refresh(approval)
    add_event(
        "EXAM_RELEASE_APPROVED",
        {"exam_id": exam_id, "officer_id": officer.id, "approved_at": now.isoformat()},
    )
    return approval


@router.get("/{exam_id}/validate", response_model=PaperValidationReportOut)
def validate_exam(
    exam_id: int,
    user: User = Depends(require_role("ADMIN", "EXAM_OFFICER")),
    db: Session = Depends(get_db),
):
    from app.services.paper_validation import validate_exam_paper
    return validate_exam_paper(db, exam_id)


@router.post("/{exam_id}/release", response_model=ReleaseStatusOut)
def release_exam(
    exam_id: int,
    admin: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    exam = db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(404, "Exam not found")
    now = _utc_now()
    status = _release_status(exam, db, now)
    if exam.status == "RELEASED":
        return status
    if not status["release_window_open"]:
        raise HTTPException(403, f"Exam release window is {RELEASE_WINDOW_MINUTES} minutes before the exam")
    if status["approval_count"] < REQUIRED_RELEASE_APPROVALS:
        raise HTTPException(403, f"{REQUIRED_RELEASE_APPROVALS} distinct officer approvals are required")

    from app.services.paper_validation import validate_exam_paper
    validation = validate_exam_paper(db, exam_id)
    if validation["status"] == "BLOCKED":
        raise HTTPException(403, f"Exam release BLOCKED by Pre-Exam Paper Validation: {'; '.join(validation['details'])}")

    exam.status = "RELEASED"
    db.commit()
    add_event(
        "EXAM_RELEASED",
        {
            "exam_id": exam_id,
            "released_by": admin.id,
            "approver_ids": status["approver_ids"],
            "release_time": now.isoformat(),
            "validation_status": validation["status"],
        },
    )
    return _release_status(exam, db, now)


@router.get("/{exam_id}", response_model=ExamOut)
def get_exam(exam_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    exam = db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(404, "Exam not found")
    return _exam_out(exam)



@router.post("/{exam_id}/start", response_model=ExamSessionOut)
def start_exam(
    exam_id: int,
    request: Request,
    candidate: User = Depends(require_role("CANDIDATE")),
    db: Session = Depends(get_db),
    device_id: str = Header(..., alias=DEVICE_HEADER),
    device_token: str = Header(..., alias=DEVICE_TOKEN_HEADER),
    centre_id: int = Header(..., alias=CENTRE_HEADER),
):
    exam = db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(404, "Exam not found")
    if len(device_id) < 8:
        raise HTTPException(400, f"{DEVICE_HEADER} must contain a stable device identifier")
    if len(device_token) < 24:
        raise HTTPException(400, f"{DEVICE_TOKEN_HEADER} is required")

    # Candidate must be pre-assigned and identity-verified for this exam and centre.
    assignment = (db.query(ExamCandidateAssignment)
        .filter(ExamCandidateAssignment.exam_id == exam_id, ExamCandidateAssignment.candidate_id == candidate.id)
        .first())
    if not assignment or assignment.identity_status != "VERIFIED":
        raise HTTPException(403, "Candidate identity has not been verified for this exam")
    if assignment.centre_id != centre_id:
        raise HTTPException(403, "Candidate is assigned to a different examination centre")
    centre_assignment = (db.query(ExamCentreAssignment)
        .filter(ExamCentreAssignment.exam_id == exam_id, ExamCentreAssignment.centre_id == centre_id)
        .first())
    if not centre_assignment:
        raise HTTPException(403, "Centre is not authorized for this examination")
    device = (db.query(CentreDevice)
        .filter(CentreDevice.centre_id == centre_id, CentreDevice.device_code == device_id, CentreDevice.status == "ACTIVE")
        .first())
    if not device or not hmac.compare_digest(device.device_token_hash, _sha256_text(device_token)):
        raise HTTPException(403, "Unauthorized examination device")

    device.last_seen_at = _utc_now()
    now = _utc_now()
    starts_at = _normalize_dt(exam.starts_at)
    ends_at = _normalize_dt(exam.ends_at)
    if not (starts_at <= now <= ends_at):
        raise HTTPException(403, "Exam is not currently open")
    if exam.status != "RELEASED":
        raise HTTPException(403, "Exam has not been authorized for release")

    existing = (
        db.query(ExamSession)
        .filter(ExamSession.exam_id == exam_id, ExamSession.candidate_id == candidate.id)
        .first()
    )
    if existing:
        if not hmac.compare_digest(existing.device_id_hash, _sha256_text(device_id)):
            raise HTTPException(403, "This candidate is already bound to another exam device")
        if existing.status != "ACTIVE":
            raise HTTPException(403, "Exam session is no longer active")
        # Rotate the opaque token when the candidate reconnects; the previous token is immediately revoked.
        session_token = secrets.token_urlsafe(48)
        existing.session_token_hash = _sha256_text(session_token)
        existing.last_heartbeat_at = now
        record_event(
            db, event_type="SESSION_START", exam_id=exam_id, session_id=existing.id,
            candidate_id=candidate.id, ip_address=request.client.host if request.client else None,
            device_id=device_id, user_agent=request.headers.get("user-agent"),
            metadata={"reconnect": True, "centre_id": centre_id, "device_id": device_id},
        )
        db.commit()
        return {
            "session_id": existing.id,
            "exam_id": existing.exam_id,
            "status": existing.status,
            "question_count": len(existing.questions),
            "started_at": existing.started_at,
            "session_token": session_token,
            "device_bound": True,
        }

    seed = secrets.token_bytes(32)
    seed_hash = hashlib.sha256(seed).hexdigest()
    rng = secrets.SystemRandom()
    used_ids: set[int] = set()
    selections: list[tuple[int, int]] = []

    for rule in exam.blueprint:
        topic = rule["topic"]
        difficulty = rule["difficulty"]
        count = int(rule["count"])
        candidates = (
            db.query(Question)
            .filter(
                Question.status == "APPROVED",
                Question.exposure_status == "ACTIVE",
                Question.exposure_count < EXPOSURE_LIMIT,
                Question.subject == exam.subject,
                Question.topic == topic,
                Question.difficulty == difficulty,
            )
            .all()
        )
        candidates = [q for q in candidates if q.id not in used_ids]
        if len(candidates) < count:
            raise HTTPException(
                409,
                f"Insufficient approved questions for topic={topic}, difficulty={difficulty}: required {count}, available {len(candidates)}",
            )
        chosen = rng.sample(candidates, count)
        for q in chosen:
            used_ids.add(q.id)
            selections.append((q.id, len(selections) + 1))

    session_token = secrets.token_urlsafe(48)
    session = ExamSession(
        exam_id=exam_id,
        candidate_id=candidate.id,
        seed_hash=seed_hash,
        started_at=now,
        status="ACTIVE",
        device_id_hash=_sha256_text(device_id),
        session_token_hash=_sha256_text(session_token),
        last_heartbeat_at=now,
    )
    db.add(session)
    db.flush()

    for question_id, position in selections:
        db.add(ExamSessionQuestion(session_id=session.id, question_id=question_id, position=position))

    db.commit()
    db.refresh(session)

    record_event(
        db, event_type="SESSION_START", exam_id=exam_id, session_id=session.id,
        candidate_id=candidate.id, ip_address=request.client.host if request.client else None,
        device_id=device_id, user_agent=request.headers.get("user-agent"),
    )
    db.commit()

    add_event(
        "EXAM_SESSION_CREATED",
        {
            "exam_id": exam_id,
            "session_id": session.id,
            "candidate_id": candidate.id,
            "seed_hash": seed_hash,
            "question_count": len(selections),
            "device_id_hash": session.device_id_hash,
            "centre_id": centre_id,
            "identity_status": assignment.identity_status,
        },
    )
    add_event(
        "QUESTIONS_SELECTED",
        {
            "exam_id": exam_id,
            "session_id": session.id,
            "candidate_id": candidate.id,
            "question_ids": [qid for qid, _ in selections],
            "centre_id": centre_id,
        },
    )

    return {
        "session_id": session.id,
        "exam_id": exam_id,
        "status": session.status,
        "question_count": len(selections),
        "started_at": session.started_at,
        "session_token": session_token,
        "device_bound": True,
    }


def _mark_exposed(db: Session, item: ExamSessionQuestion, candidate_id: int) -> None:
    now = _utc_now()
    question = item.question
    if item.first_exposed_at is not None:
        item.last_exposed_at = now
        db.flush()
        return
    item.first_exposed_at = now
    item.last_exposed_at = now
    question.exposure_count += 1
    if question.first_exposed_at is None:
        question.first_exposed_at = now
    question.last_exposed_at = now
    if question.exposure_count >= EXPOSURE_LIMIT:
        question.exposure_status = "RETIRED_EXPOSURE"
    db.flush()
    add_event(
        "QUESTION_EXPOSED",
        {
            "question_id": question.id,
            "session_id": item.session_id,
            "candidate_id": candidate_id,
            "exposure_count": question.exposure_count,
            "exposure_limit": EXPOSURE_LIMIT,
        },
    )


def _question_out(item: ExamSessionQuestion) -> CandidateQuestionOut:
    try:
        content, _answer = decrypt_question(
            item.question.encrypted_content,
            item.question.encryption_nonce,
            item.question.wrapped_key,
            item.question.content_hash,
        )
    except Exception as exc:
        raise HTTPException(500, "Question integrity/decryption failure") from exc
    return CandidateQuestionOut(
        position=item.position,
        question_id=item.question_id,
        content=content,
        subject=item.question.subject,
        topic=item.question.topic,
        difficulty=item.question.difficulty,
    )


@router.get("/{exam_id}/questions/{position}", response_model=CandidateQuestionOut)
def get_question(
    exam_id: int,
    position: int,
    request: Request,
    candidate: User = Depends(require_role("CANDIDATE")),
    db: Session = Depends(get_db),
    session_token: str = Header(..., alias=SESSION_HEADER),
    device_id: str = Header(..., alias=DEVICE_HEADER),
    device_token: str = Header(..., alias=DEVICE_TOKEN_HEADER),
    centre_id: int = Header(..., alias=CENTRE_HEADER),
):
    if position < 1:
        raise HTTPException(400, "Position must be >= 1")
    session = _authorize_candidate_endpoint(exam_id, candidate, db, session_token, device_id, device_token, centre_id)
    item = (
        db.query(ExamSessionQuestion)
        .filter(ExamSessionQuestion.session_id == session.id, ExamSessionQuestion.position == position)
        .first()
    )
    if not item:
        raise HTTPException(404, "Question position not found")

    _mark_exposed(db, item, candidate.id)
    record_event(
        db, event_type="QUESTION_REQUEST", exam_id=exam_id, session_id=session.id,
        candidate_id=candidate.id, ip_address=request.client.host if request.client else None,
        device_id=device_id, user_agent=request.headers.get("user-agent"),
        metadata={"position": position, "question_id": item.question_id},
    )
    db.commit()
    return _question_out(item)


@router.get("/{exam_id}/paper", response_model=CandidatePaperOut)
def get_paper(
    exam_id: int,
    candidate: User = Depends(require_role("CANDIDATE")),
    db: Session = Depends(get_db),
    session_token: str = Header(..., alias=SESSION_HEADER),
    device_id: str = Header(..., alias=DEVICE_HEADER),
    device_token: str = Header(..., alias=DEVICE_TOKEN_HEADER),
    centre_id: int = Header(..., alias=CENTRE_HEADER),
):
    """Demo endpoint: prefer /questions/{position} for just-in-time CBT delivery."""
    session = _authorize_candidate_endpoint(exam_id, candidate, db, session_token, device_id, device_token, centre_id)
    output = []
    for item in session.questions:
        _mark_exposed(db, item, candidate.id)
        output.append(_question_out(item))
    db.commit()
    return {"session_id": session.id, "exam_id": exam_id, "questions": output}


@router.post("/{exam_id}/answers", response_model=AnswerOut)
def submit_answer(
    exam_id: int,
    request: Request,
    data: AnswerSubmit,
    candidate: User = Depends(require_role("CANDIDATE")),
    db: Session = Depends(get_db),
    session_token: str = Header(..., alias=SESSION_HEADER),
    device_id: str = Header(..., alias=DEVICE_HEADER),
    device_token: str = Header(..., alias=DEVICE_TOKEN_HEADER),
    centre_id: int = Header(..., alias=CENTRE_HEADER),
):
    session = _authorize_candidate_endpoint(exam_id, candidate, db, session_token, device_id, device_token, centre_id)
    item = (
        db.query(ExamSessionQuestion)
        .filter(ExamSessionQuestion.session_id == session.id, ExamSessionQuestion.question_id == data.question_id)
        .first()
    )
    if not item:
        raise HTTPException(400, "Question is not part of this exam session")
    if item.first_exposed_at is None:
        raise HTTPException(403, "Question must be delivered before submitting an answer")

    # Replay-safe/idempotent retry: re-sending the same nonce returns success without creating another record.
    existing_nonce = (
        db.query(ExamAnswer)
        .filter(ExamAnswer.session_id == session.id, ExamAnswer.client_nonce == data.client_nonce)
        .first()
    )
    if existing_nonce:
        return {"question_id": existing_nonce.question_id, "submitted_at": existing_nonce.submitted_at, "updated": False}

    answer_row = (
        db.query(ExamAnswer)
        .filter(ExamAnswer.session_id == session.id, ExamAnswer.question_id == data.question_id)
        .first()
    )
    now = _utc_now()
    if answer_row:
        answer_row.answer = data.answer
        answer_row.client_nonce = data.client_nonce
        answer_row.updated_at = now
        updated = True
    else:
        answer_row = ExamAnswer(
            session_id=session.id,
            question_id=data.question_id,
            answer=data.answer,
            client_nonce=data.client_nonce,
            submitted_at=now,
            updated_at=now,
        )
        db.add(answer_row)
        updated = False

    session.last_heartbeat_at = now
    record_event(
        db, event_type="ANSWER_SUBMITTED", exam_id=exam_id, session_id=session.id,
        candidate_id=candidate.id, ip_address=request.client.host if request.client else None,
        device_id=device_id, user_agent=request.headers.get("user-agent"),
        metadata={"question_id": data.question_id, "updated": updated},
    )
    db.commit()
    add_event(
        "ANSWER_SUBMITTED",
        {
            "exam_id": exam_id,
            "session_id": session.id,
            "candidate_id": candidate.id,
            "question_id": data.question_id,
            "client_nonce": _sha256_text(data.client_nonce),
            "updated": updated,
        },
    )
    return {"question_id": data.question_id, "submitted_at": now, "updated": updated}


@router.post("/{exam_id}/heartbeat", response_model=ExamSessionOut)
def heartbeat(
    exam_id: int,
    request: Request,
    candidate: User = Depends(require_role("CANDIDATE")),
    db: Session = Depends(get_db),
    session_token: str = Header(..., alias=SESSION_HEADER),
    device_id: str = Header(..., alias=DEVICE_HEADER),
    device_token: str = Header(..., alias=DEVICE_TOKEN_HEADER),
    centre_id: int = Header(..., alias=CENTRE_HEADER),
):
    session = _authorize_candidate_endpoint(exam_id, candidate, db, session_token, device_id, device_token, centre_id)
    record_event(
        db, event_type="HEARTBEAT", exam_id=exam_id, session_id=session.id,
        candidate_id=candidate.id, ip_address=request.client.host if request.client else None,
        device_id=device_id, user_agent=request.headers.get("user-agent"),
    )
    db.commit()
    return {
        "session_id": session.id,
        "exam_id": exam_id,
        "status": session.status,
        "question_count": len(session.questions),
        "started_at": session.started_at,
        "session_token": None,
        "device_bound": True,
    }


@router.post("/{exam_id}/finish", response_model=ExamSessionOut)
def finish_exam(
    exam_id: int,
    request: Request,
    candidate: User = Depends(require_role("CANDIDATE")),
    db: Session = Depends(get_db),
    session_token: str = Header(..., alias=SESSION_HEADER),
    device_id: str = Header(..., alias=DEVICE_HEADER),
    device_token: str = Header(..., alias=DEVICE_TOKEN_HEADER),
    centre_id: int = Header(..., alias=CENTRE_HEADER),
):
    session = _authorize_candidate_endpoint(exam_id, candidate, db, session_token, device_id, device_token, centre_id)
    session.status = "COMPLETED"
    session.completed_at = _utc_now()
    record_event(
        db, event_type="EXAM_FINISHED", exam_id=exam_id, session_id=session.id,
        candidate_id=candidate.id, ip_address=request.client.host if request.client else None,
        device_id=device_id, user_agent=request.headers.get("user-agent"),
    )
    db.commit()
    add_event(
        "EXAM_SESSION_COMPLETED",
        {"exam_id": exam_id, "session_id": session.id, "candidate_id": candidate.id},
    )
    return {
        "session_id": session.id,
        "exam_id": exam_id,
        "status": session.status,
        "question_count": len(session.questions),
        "started_at": session.started_at,
        "session_token": None,
        "device_bound": True,
    }


@router.get("/exposure/questions", response_model=list[ExposureOut])
def question_exposure(
    admin: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    questions = db.query(Question).order_by(Question.exposure_count.desc(), Question.id.asc()).all()
    return [
        {
            "question_id": q.id,
            "exposure_count": q.exposure_count,
            "first_exposed_at": q.first_exposed_at,
            "last_exposed_at": q.last_exposed_at,
            "exposure_status": q.exposure_status,
        }
        for q in questions
    ]
