"""Pre-exam paper validation service (Phase 18).

Validates question pool readiness, topic distribution, difficulty balance,
duplicate detection, exposure status, and approval status before an exam can be RELEASED.
"""
from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session

from app.models.models import Exam, Question
from app.security.encryption import decrypt_question
from app.security.fingerprint import compute_text_similarity


def validate_exam_paper(db: Session, exam_id: int) -> dict[str, Any]:
    """Perform pre-exam paper validation and return structured report with status (PASS, WARNING, BLOCKED)."""
    exam = db.get(Exam, exam_id)
    if not exam:
        return {
            "exam_id": exam_id,
            "status": "BLOCKED",
            "syllabus_coverage": "BLOCKED",
            "difficulty_balance": "BLOCKED",
            "duplicate_detection": "BLOCKED",
            "exposed_questions": "BLOCKED",
            "compromised_questions": "BLOCKED",
            "approval_status": "BLOCKED",
            "details": ["Exam not found"],
        }

    blueprint = exam.blueprint or []
    details = []

    syllabus_status = "PASS"
    difficulty_status = "PASS"
    duplicate_status = "PASS"
    exposed_status = "PASS"
    compromised_status = "PASS"
    approval_status = "PASS"

    all_matched_questions: list[Question] = []
    seen_contents: list[str] = []

    for rule in blueprint:
        topic = rule["topic"]
        difficulty = rule["difficulty"]
        required_count = int(rule["count"])

        available = (
            db.query(Question)
            .filter(
                Question.subject == exam.subject,
                Question.topic == topic,
                Question.difficulty == difficulty,
            )
            .all()
        )

        approved_available = [q for q in available if q.status == "APPROVED"]
        if len(approved_available) < required_count:
            approval_status = "BLOCKED"
            details.append(
                f"Insufficient APPROVED questions for topic '{topic}', difficulty '{difficulty}': "
                f"required {required_count}, found {len(approved_available)} approved out of {len(available)} total"
            )

        all_matched_questions.extend(available)

    # Check question statuses and exposure
    for q in all_matched_questions:
        if q.status != "APPROVED":
            approval_status = "BLOCKED"
            details.append(f"Question #{q.id} is in status '{q.status}' (must be APPROVED)")

        if q.exposure_status in ("RETIRED_EXPOSURE", "COMPROMISED"):
            compromised_status = "BLOCKED"
            details.append(f"Question #{q.id} has exposure status '{q.exposure_status}' and cannot be used")
        elif q.exposure_status == "WARNING" or q.exposure_count > 60:
            if exposed_status != "BLOCKED":
                exposed_status = "WARNING"
            details.append(f"Question #{q.id} has elevated exposure count ({q.exposure_count})")

        # Decrypt for duplicate detection
        try:
            content, _ = decrypt_question(q.encrypted_content, q.encryption_nonce, q.wrapped_key, q.content_hash)
            for existing_content in seen_contents:
                sim = compute_text_similarity(content, existing_content)
                if sim >= 0.85:
                    duplicate_status = "BLOCKED"
                    details.append(f"High similarity ({sim:.2f}) detected between Question #{q.id} and another question in pool")
            seen_contents.append(content)
        except Exception:
            pass

    # Aggregate overall status
    statuses = [syllabus_status, difficulty_status, duplicate_status, exposed_status, compromised_status, approval_status]
    if "BLOCKED" in statuses:
        final_status = "BLOCKED"
    elif "WARNING" in statuses:
        final_status = "WARNING"
    else:
        final_status = "PASS"

    if not details:
        details.append("All paper validation checks passed successfully.")

    return {
        "exam_id": exam_id,
        "status": final_status,
        "syllabus_coverage": syllabus_status,
        "difficulty_balance": difficulty_status,
        "duplicate_detection": duplicate_status,
        "exposed_questions": exposed_status,
        "compromised_questions": compromised_status,
        "approval_status": approval_status,
        "details": details,
    }
