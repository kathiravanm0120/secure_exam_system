"""Fingerprinting API routes for question and exam paper integrity verification."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Exam, Question, ExamSessionQuestion, User
from app.routes.questions import current_user, require_role
from app.schemas.schemas import FingerprintMatchOut, FingerprintMatchRequest
from app.security.encryption import decrypt_question
from app.security.fingerprint import (
    compute_exam_fingerprint,
    compute_question_fingerprint,
    compute_text_similarity,
    verify_question_integrity,
)

router = APIRouter(prefix="/fingerprints", tags=["fingerprints"])


def _get_decrypted_question(question: Question) -> tuple[str, str]:
    try:
        return decrypt_question(
            question.encrypted_content,
            question.encryption_nonce,
            question.wrapped_key,
            question.content_hash,
        )
    except Exception as exc:
        raise HTTPException(500, f"Decryption failure for question #{question.id}") from exc


@router.get("/question/{question_id}")
def get_question_fingerprint(
    question_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(404, "Question not found")

    content, answer = _get_decrypted_question(question)
    fp = compute_question_fingerprint(
        content=content,
        subject=question.subject,
        topic=question.topic,
        difficulty=question.difficulty,
        answer=answer,
    )
    return {
        "question_id": question.id,
        "subject": question.subject,
        "topic": question.topic,
        "difficulty": question.difficulty,
        "fingerprint": fp,
        "content_hash": question.content_hash,
    }


@router.get("/exam/{exam_id}")
def get_exam_fingerprint(
    exam_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    exam = db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(404, "Exam not found")

    # Get sample session questions or blueprint questions
    session_questions = (
        db.query(ExamSessionQuestion)
        .join(ExamSessionQuestion.session)
        .filter(ExamSessionQuestion.session.has(exam_id=exam_id))
        .order_by(ExamSessionQuestion.position.asc())
        .all()
    )

    fingerprints = []
    seen = set()
    for sq in session_questions:
        if sq.question_id in seen:
            continue
        seen.add(sq.question_id)
        content, answer = _get_decrypted_question(sq.question)
        fp = compute_question_fingerprint(
            content=content,
            subject=sq.question.subject,
            topic=sq.question.topic,
            difficulty=sq.question.difficulty,
            answer=answer,
        )
        fingerprints.append(fp)

    exam_fp = compute_exam_fingerprint(fingerprints)
    return {
        "exam_id": exam.id,
        "exam_name": exam.name,
        "question_count": len(fingerprints),
        "exam_fingerprint": exam_fp,
        "question_fingerprints": fingerprints,
    }


@router.post("/match", response_model=FingerprintMatchOut)
def match_fingerprint(
    data: FingerprintMatchRequest,
    user: User = Depends(require_role("ADMIN", "EXAM_OFFICER", "REVIEWER")),
    db: Session = Depends(get_db),
):
    """Perform deterministic and normalized text matching against known approved/active questions."""
    questions = db.query(Question).all()
    best_match: Question | None = None
    best_score: float = 0.0

    for q in questions:
        try:
            content, answer = _get_decrypted_question(q)
        except Exception:
            continue

        score = compute_text_similarity(data.suspected_text, content)
        if score > best_score:
            best_score = score
            best_match = q

    if best_match and best_score >= 0.5:
        content, answer = _get_decrypted_question(best_match)
        fp = compute_question_fingerprint(
            content=content,
            subject=best_match.subject,
            topic=best_match.topic,
            difficulty=best_match.difficulty,
            answer=answer,
        )
        return FingerprintMatchOut(
            match=True,
            question_id=best_match.id,
            exam_id=f"EXAM-{data.exam_id}" if data.exam_id else None,
            confidence=round(best_score, 4),
            canonical_hash=fp,
            matched_subject=best_match.subject,
            matched_topic=best_match.topic,
        )

    return FingerprintMatchOut(
        match=False,
        question_id=None,
        exam_id=None,
        confidence=0.0,
        canonical_hash=None,
        matched_subject=None,
        matched_topic=None,
    )
