from fastapi import APIRouter, Depends, HTTPException
from app.routes.questions import current_user, require_role
from app.models.models import Question, User
from app.database import get_db
from sqlalchemy.orm import Session
from app.blockchain.service import find_question_events, get_chain, verify_chain
from app.security.encryption import decrypt_question
import hashlib
import json

router = APIRouter(prefix="/blockchain", tags=["blockchain"])


@router.get("/verify")
def verify_ledger(user: User = Depends(require_role("ADMIN"))):
    return verify_chain()


@router.get("/chain")
def read_chain(user: User = Depends(require_role("ADMIN"))):
    return {"chain": get_chain()}


@router.get("/questions/{question_id}/verify")
def verify_question(
    question_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(404, "Question not found")

    # Recompute the hash from the decrypted source of truth and compare it with DB.
    try:
        content, answer = decrypt_question(
            question.encrypted_content,
            question.encryption_nonce,
            question.wrapped_key,
            question.content_hash,
        )
        payload = json.dumps(
            {"content": content, "answer": answer},
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        current_hash = hashlib.sha256(payload).hexdigest()
    except Exception as exc:
        raise HTTPException(500, "Question decryption/integrity check failed") from exc

    events = find_question_events(question_id)
    matching = [e for e in events if e.get("data", {}).get("content_hash") == current_hash]

    return {
        "question_id": question_id,
        "database_hash": question.content_hash,
        "current_content_hash": current_hash,
        "content_integrity": current_hash == question.content_hash,
        "blockchain_record_found": bool(matching),
        "event_count": len(events),
        "events": events,
        "blockchain": verify_chain(),
    }
