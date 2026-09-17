from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Question, QuestionReview, User
from app.schemas.schemas import QuestionCreate, QuestionOut, ReviewCreate
from app.security.auth import decode_access_token
from app.security.encryption import decrypt_question, encrypt_question
from app.blockchain.service import add_event

router = APIRouter(prefix="/questions", tags=["questions"])
bearer = HTTPBearer()


def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_access_token(credentials.credentials)
        user = db.get(User, int(payload["sub"]))
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_role(*roles: str):
    def dependency(user: User = Depends(current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return dependency


def serialize_question(question: Question) -> dict:
    try:
        content, _answer = decrypt_question(
            question.encrypted_content,
            question.encryption_nonce,
            question.wrapped_key,
            question.content_hash,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Question integrity/decryption failure") from exc

    return {
        "id": question.id,
        "content": content,
        "subject": question.subject,
        "topic": question.topic,
        "difficulty": question.difficulty,
        "created_by": question.created_by,
        "reviewer_id": question.reviewer_id,
        "status": question.status,
        "content_hash": question.content_hash,
        "crypto_version": question.crypto_version,
    }


@router.post("", response_model=QuestionOut, status_code=201)
def create_question(
    data: QuestionCreate,
    user: User = Depends(require_role("SETTER", "ADMIN")),
    db: Session = Depends(get_db),
):
    encrypted = encrypt_question(data.content, data.answer)
    question = Question(
        encrypted_content=encrypted["encrypted_content"],
        encryption_nonce=encrypted["encryption_nonce"],
        wrapped_key=encrypted["wrapped_key"],
        content_hash=encrypted["content_hash"],
        crypto_version=encrypted["crypto_version"],
        subject=data.subject,
        topic=data.topic,
        difficulty=data.difficulty,
        created_by=user.id,
        status="SUBMITTED",
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    add_event(
        "QUESTION_CREATED",
        {
            "question_id": question.id,
            "content_hash": question.content_hash,
            "creator_id": user.id,
            "subject": question.subject,
            "topic": question.topic,
            "difficulty": question.difficulty,
        },
    )
    return serialize_question(question)


@router.get("/my", response_model=list[QuestionOut])
def my_questions(user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role == "SETTER":
        questions = db.query(Question).filter(Question.created_by == user.id).all()
    elif user.role == "REVIEWER":
        questions = db.query(Question).filter(Question.reviewer_id == user.id).all()
    else:
        questions = db.query(Question).all()
    return [serialize_question(q) for q in questions]


@router.post("/{question_id}/assign/{reviewer_id}", response_model=QuestionOut)
def assign_reviewer(
    question_id: int,
    reviewer_id: int,
    admin: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    question = db.get(Question, question_id)
    reviewer = db.get(User, reviewer_id)
    if not question:
        raise HTTPException(404, "Question not found")
    if not reviewer or reviewer.role != "REVIEWER":
        raise HTTPException(400, "Reviewer not found")
    if question.created_by == reviewer_id:
        raise HTTPException(400, "A setter cannot review their own question")
    question.reviewer_id = reviewer_id
    question.status = "IN_REVIEW"
    db.commit()
    db.refresh(question)
    add_event(
        "QUESTION_REVIEW_ASSIGNED",
        {"question_id": question.id, "content_hash": question.content_hash, "reviewer_id": reviewer_id, "assigned_by": admin.id},
    )
    return serialize_question(question)


@router.post("/{question_id}/review", response_model=QuestionOut)
def review_question(
    question_id: int,
    data: ReviewCreate,
    reviewer: User = Depends(require_role("REVIEWER")),
    db: Session = Depends(get_db),
):
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(404, "Question not found")
    if question.reviewer_id != reviewer.id:
        raise HTTPException(403, "Question is not assigned to this reviewer")
    if question.created_by == reviewer.id:
        raise HTTPException(403, "Cannot review your own question")

    review = QuestionReview(
        question_id=question_id,
        reviewer_id=reviewer.id,
        decision=data.decision,
        comments=data.comments,
    )
    question.status = "APPROVED" if data.decision == "APPROVE" else "REJECTED"
    db.add(review)
    db.commit()
    db.refresh(question)
    add_event(
        "QUESTION_APPROVED" if data.decision == "APPROVE" else "QUESTION_REJECTED",
        {
            "question_id": question.id,
            "content_hash": question.content_hash,
            "reviewer_id": reviewer.id,
            "decision": data.decision,
        },
    )
    return serialize_question(question)
