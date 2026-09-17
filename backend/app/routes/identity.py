from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.blockchain.service import add_event
from app.database import get_db
from app.models.models import CentreDevice, Exam, ExamCandidateAssignment, ExamCentre, ExamCentreAssignment, User
from app.routes.questions import require_role
from app.schemas.schemas import CandidateAssignmentCreate, CandidateAssignmentOut, CentreCreate, CentreDeviceCreate

router = APIRouter(prefix="/identity", tags=["identity-centres"])


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _assignment_out(a: ExamCandidateAssignment) -> dict:
    return {
        "id": a.id,
        "exam_id": a.exam_id,
        "candidate_id": a.candidate_id,
        "centre_id": a.centre_id,
        "seat_number": a.seat_number,
        "identity_status": a.identity_status,
        "verified_at": a.verified_at,
    }


@router.post("/centres", status_code=201)
def create_centre(data: CentreCreate, admin: User = Depends(require_role("ADMIN")), db: Session = Depends(get_db)):
    if db.query(ExamCentre).filter(ExamCentre.code == data.code).first():
        raise HTTPException(409, "Centre code already exists")
    centre = ExamCentre(code=data.code, name=data.name, status="ACTIVE")
    db.add(centre)
    db.commit()
    db.refresh(centre)
    add_event("CENTRE_CREATED", {"centre_id": centre.id, "code": centre.code, "created_by": admin.id})
    return {"id": centre.id, "code": centre.code, "name": centre.name, "status": centre.status}


@router.post("/centres/{centre_id}/devices", status_code=201)
def register_device(
    centre_id: int,
    data: CentreDeviceCreate,
    admin: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    centre = db.get(ExamCentre, centre_id)
    if not centre or centre.status != "ACTIVE":
        raise HTTPException(404, "Active centre not found")
    if db.query(CentreDevice).filter(CentreDevice.centre_id == centre_id, CentreDevice.device_code == data.device_code).first():
        raise HTTPException(409, "Device already registered")
    raw_token = secrets.token_urlsafe(36)
    device = CentreDevice(
        centre_id=centre_id,
        device_code=data.device_code,
        device_token_hash=_sha(raw_token),
        status="ACTIVE",
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    add_event("CENTRE_DEVICE_REGISTERED", {"centre_id": centre_id, "device_id": device.id, "registered_by": admin.id})
    return {"device_id": device.id, "device_code": device.device_code, "device_token": raw_token, "warning": "Store this token securely; it is shown only once."}


@router.post("/exams/{exam_id}/centres", status_code=201)
def assign_centre(
    exam_id: int,
    centre_id: int,
    admin: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    exam = db.get(Exam, exam_id)
    centre = db.get(ExamCentre, centre_id)
    if not exam:
        raise HTTPException(404, "Exam not found")
    if not centre or centre.status != "ACTIVE":
        raise HTTPException(404, "Active centre not found")
    existing = db.query(ExamCentreAssignment).filter(ExamCentreAssignment.exam_id == exam_id, ExamCentreAssignment.centre_id == centre_id).first()
    if existing:
        return {"id": existing.id, "exam_id": exam_id, "centre_id": centre_id, "status": "ASSIGNED"}
    row = ExamCentreAssignment(exam_id=exam_id, centre_id=centre_id)
    db.add(row)
    db.commit()
    db.refresh(row)
    add_event("EXAM_CENTRE_ASSIGNED", {"exam_id": exam_id, "centre_id": centre_id, "assigned_by": admin.id})
    return {"id": row.id, "exam_id": exam_id, "centre_id": centre_id, "status": "ASSIGNED"}


@router.post("/exams/{exam_id}/candidates", response_model=CandidateAssignmentOut, status_code=201)
def assign_candidate(
    exam_id: int,
    data: CandidateAssignmentCreate,
    admin: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    exam = db.get(Exam, exam_id)
    candidate = db.get(User, data.candidate_id)
    centre = db.get(ExamCentre, data.centre_id)
    if not exam or not candidate:
        raise HTTPException(404, "Exam or candidate not found")
    if candidate.role != "CANDIDATE":
        raise HTTPException(400, "User is not a candidate")
    if not centre or centre.status != "ACTIVE":
        raise HTTPException(404, "Active centre not found")
    assigned_centre = db.query(ExamCentreAssignment).filter(ExamCentreAssignment.exam_id == exam_id, ExamCentreAssignment.centre_id == data.centre_id).first()
    if not assigned_centre:
        raise HTTPException(400, "Centre is not assigned to this exam")
    existing = db.query(ExamCandidateAssignment).filter(ExamCandidateAssignment.exam_id == exam_id, ExamCandidateAssignment.candidate_id == data.candidate_id).first()
    if existing:
        raise HTTPException(409, "Candidate is already assigned to this exam")
    row = ExamCandidateAssignment(
        exam_id=exam_id,
        candidate_id=data.candidate_id,
        centre_id=data.centre_id,
        seat_number=data.seat_number,
        identity_status="PENDING",
        identity_reference_hash=_sha(data.identity_reference) if data.identity_reference else None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    add_event("CANDIDATE_ASSIGNED_TO_CENTRE", {"exam_id": exam_id, "candidate_id": data.candidate_id, "centre_id": data.centre_id, "seat_number": data.seat_number, "assigned_by": admin.id})
    return _assignment_out(row)


@router.post("/exams/{exam_id}/candidates/{candidate_id}/verify", response_model=CandidateAssignmentOut)
def verify_candidate(
    exam_id: int,
    candidate_id: int,
    admin: User = Depends(require_role("ADMIN", "EXAM_OFFICER")),
    db: Session = Depends(get_db),
):
    row = db.query(ExamCandidateAssignment).filter(ExamCandidateAssignment.exam_id == exam_id, ExamCandidateAssignment.candidate_id == candidate_id).first()
    if not row:
        raise HTTPException(404, "Candidate is not assigned to this exam")
    row.identity_status = "VERIFIED"
    row.verified_at = datetime.now(timezone.utc)
    row.verified_by = admin.id
    db.commit()
    db.refresh(row)
    add_event("CANDIDATE_IDENTITY_VERIFIED", {"exam_id": exam_id, "candidate_id": candidate_id, "centre_id": row.centre_id, "verified_by": admin.id})
    return _assignment_out(row)


@router.get("/exams/{exam_id}/candidates/{candidate_id}", response_model=CandidateAssignmentOut)
def get_candidate_assignment(
    exam_id: int,
    candidate_id: int,
    admin: User = Depends(require_role("ADMIN", "EXAM_OFFICER")),
    db: Session = Depends(get_db),
):
    row = db.query(ExamCandidateAssignment).filter(ExamCandidateAssignment.exam_id == exam_id, ExamCandidateAssignment.candidate_id == candidate_id).first()
    if not row:
        raise HTTPException(404, "Candidate is not assigned to this exam")
    return _assignment_out(row)
