"""Leak Investigation & Question Lifecycle (Chain of Custody) endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.blockchain.service import find_question_events, get_chain
from app.database import get_db
from app.models.models import (
    Exam,
    ExamAnswer,
    ExamSessionQuestion,
    Question,
    QuestionReview,
    SecurityEvent,
    User,
)
from app.routes.questions import current_user, require_role
from app.schemas.schemas import InvestigationRequest
from app.security.encryption import decrypt_question
from app.security.fingerprint import (
    compute_question_fingerprint,
    compute_text_similarity,
)

router = APIRouter(prefix="/investigation", tags=["investigation"])


def _get_decrypted(q: Question) -> tuple[str, str]:
    try:
        return decrypt_question(q.encrypted_content, q.encryption_nonce, q.wrapped_key, q.content_hash)
    except Exception:
        return ("", "")


@router.get("/questions/{question_id}/lifecycle")
def get_question_lifecycle(
    question_id: int,
    admin: User = Depends(require_role("ADMIN", "EXAM_OFFICER", "REVIEWER")),
    db: Session = Depends(get_db),
):
    """Retrieve complete visual timeline & chain of custody for a specific question."""
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(404, "Question not found")

    creator = db.get(User, question.created_by)
    reviews = db.query(QuestionReview).filter(QuestionReview.question_id == question_id).all()
    session_questions = db.query(ExamSessionQuestion).filter(ExamSessionQuestion.question_id == question_id).all()
    answers = db.query(ExamAnswer).filter(ExamAnswer.question_id == question_id).all()
    blockchain_events = find_question_events(question_id)

    timeline = []

    # 1. CREATED & SUBMITTED
    timeline.append({
        "stage": "CREATED",
        "timestamp": question.created_at.isoformat() if question.created_at else None,
        "actor": creator.name if creator else f"User#{question.created_by}",
        "actor_role": creator.role if creator else "SETTER",
        "source": "Question Bank Service",
        "details": f"Question created in topic {question.topic}",
        "blockchain_ref": next((b["hash"] for b in blockchain_events if b.get("event") == "QUESTION_CREATED"), "Local Ledger"),
    })

    # 2. ENCRYPTED & SEALED
    timeline.append({
        "stage": "ENCRYPTED_AND_SEALED",
        "timestamp": question.created_at.isoformat() if question.created_at else None,
        "actor": "System Cryptographic Engine",
        "actor_role": "SYSTEM",
        "source": "AES-256-GCM + RSA-OAEP",
        "details": f"Content encrypted with key wrap. Hash: {question.content_hash[:16]}...",
        "blockchain_ref": "Internal Crypto Vault",
    })

    # 3. REVIEWED & APPROVED / REJECTED
    for r in reviews:
        reviewer = db.get(User, r.reviewer_id)
        timeline.append({
            "stage": f"REVIEWED_{r.decision}",
            "timestamp": r.reviewed_at.isoformat() if r.reviewed_at else None,
            "actor": reviewer.name if reviewer else f"User#{r.reviewer_id}",
            "actor_role": reviewer.role if reviewer else "REVIEWER",
            "source": "Review Workspace",
            "details": f"Decision: {r.decision}. Comments: {r.comments or 'None'}",
            "blockchain_ref": next((b["hash"] for b in blockchain_events if b.get("event") in ("QUESTION_APPROVED", "QUESTION_REJECTED")), "Local Ledger"),
        })

    # 4. SELECTED FOR DYNAMIC CBT
    for sq in session_questions:
        sess = sq.session
        exam = sess.exam if sess else None
        timeline.append({
            "stage": "SELECTED_FOR_EXAM",
            "timestamp": sq.selected_at.isoformat() if sq.selected_at else None,
            "actor": f"Candidate #{sess.candidate_id if sess else 'N/A'}",
            "actor_role": "CANDIDATE_SESSION",
            "source": f"Dynamic Exam Generator (Exam #{sess.exam_id if sess else 'N/A'})",
            "details": f"Position {sq.position} in Session #{sq.session_id}",
            "blockchain_ref": next((b["hash"] for b in blockchain_events if b.get("event") == "QUESTIONS_SELECTED"), "Local Ledger"),
        })

        if sq.first_exposed_at:
            timeline.append({
                "stage": "EXPOSED_AND_DELIVERED",
                "timestamp": sq.first_exposed_at.isoformat(),
                "actor": f"Candidate #{sess.candidate_id if sess else 'N/A'}",
                "actor_role": "CANDIDATE",
                "source": "Just-In-Time CBT Delivery Endpoint",
                "details": f"Delivered to bound device in Session #{sq.session_id}",
                "blockchain_ref": next((b["hash"] for b in blockchain_events if b.get("event") == "QUESTION_EXPOSED"), "Local Ledger"),
            })

    # 5. ANSWER SUBMITTED
    for ans in answers:
        timeline.append({
            "stage": "ANSWER_SUBMITTED",
            "timestamp": ans.submitted_at.isoformat() if ans.submitted_at else None,
            "actor": f"Session #{ans.session_id}",
            "actor_role": "CANDIDATE",
            "source": "CBT Engine",
            "details": f"Replay-safe answer logged with nonce {ans.client_nonce[:8]}...",
            "blockchain_ref": "Local Audit Stream",
        })

    timeline.sort(key=lambda x: x["timestamp"] or "")

    return {
        "question_id": question_id,
        "current_status": question.status,
        "exposure_count": question.exposure_count,
        "exposure_status": question.exposure_status,
        "timeline_events_count": len(timeline),
        "timeline": timeline,
        "blockchain_events": blockchain_events,
    }


@router.post("/analyze")
def analyze_leak(
    data: InvestigationRequest,
    admin: User = Depends(require_role("ADMIN", "EXAM_OFFICER")),
    db: Session = Depends(get_db),
):
    """Investigate a suspected leaked question text or document."""
    questions = db.query(Question).all()
    results = []

    for q in questions:
        content, answer = _get_decrypted(q)
        if not content:
            continue

        score = compute_text_similarity(data.suspected_text, content)
        if score >= 0.25 or (data.document_hash and data.document_hash.lower() == q.content_hash.lower()):
            fp = compute_question_fingerprint(
                content=content,
                subject=q.subject,
                topic=q.topic,
                difficulty=q.difficulty,
                answer=answer,
            )
            creator = db.get(User, q.created_by)
            reviewer = db.get(User, q.reviewer_id) if q.reviewer_id else None

            # Get sessions that used this question
            session_questions = (
                db.query(ExamSessionQuestion)
                .filter(ExamSessionQuestion.question_id == q.id)
                .all()
            )
            exam_ids = list({sq.session.exam_id for sq in session_questions if sq.session})

            # Security events linked to sessions containing this question
            session_ids = [sq.session_id for sq in session_questions]
            sec_events = (
                db.query(SecurityEvent)
                .filter(SecurityEvent.session_id.in_(session_ids))
                .limit(50)
                .all()
            ) if session_ids else []

            bc_events = find_question_events(q.id)

            results.append({
                "question_id": q.id,
                "confidence": round(score, 4),
                "exact_hash_match": data.document_hash and data.document_hash.lower() == q.content_hash.lower(),
                "fingerprint": fp,
                "subject": q.subject,
                "topic": q.topic,
                "difficulty": q.difficulty,
                "created_by": {"id": creator.id, "name": creator.name, "email": creator.email} if creator else None,
                "reviewed_by": {"id": reviewer.id, "name": reviewer.name, "email": reviewer.email} if reviewer else None,
                "status": q.status,
                "exposure_count": q.exposure_count,
                "associated_exam_ids": exam_ids,
                "sessions_received_count": len(session_questions),
                "security_events_count": len(sec_events),
                "blockchain_audit_events_count": len(bc_events),
            })

    results.sort(key=lambda x: x["confidence"], reverse=True)

    top_match = results[0] if results else None
    return {
        "suspected_text_snippet": data.suspected_text[:100] + "..." if len(data.suspected_text) > 100 else data.suspected_text,
        "matches_found": len(results),
        "top_match": top_match,
        "all_candidate_matches": results,
    }
