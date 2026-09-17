from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    encrypted_content = Column(Text, nullable=False)
    encryption_nonce = Column(String(64), nullable=False)
    wrapped_key = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    crypto_version = Column(String(80), nullable=False)

    subject = Column(String(100), nullable=False)
    topic = Column(String(100), nullable=False)
    difficulty = Column(String(20), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(30), nullable=False, default="SUBMITTED")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
    exposure_count = Column(Integer, nullable=False, default=0)
    first_exposed_at = Column(DateTime(timezone=True), nullable=True)
    last_exposed_at = Column(DateTime(timezone=True), nullable=True)
    exposure_status = Column(String(20), nullable=False, default="ACTIVE")

    creator = relationship("User", foreign_keys=[created_by])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    reviews = relationship("QuestionReview", back_populates="question", cascade="all, delete-orphan")


class QuestionReview(Base):
    __tablename__ = "question_reviews"

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    decision = Column(String(20), nullable=False)
    comments = Column(Text, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    question = relationship("Question", back_populates="reviews")
    reviewer = relationship("User")


class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    subject = Column(String(100), nullable=False)
    starts_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(DateTime(timezone=True), nullable=False)
    blueprint = Column(JSON, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), nullable=False, default="SCHEDULED")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    creator = relationship("User", foreign_keys=[created_by])
    sessions = relationship("ExamSession", back_populates="exam", cascade="all, delete-orphan")
    release_approvals = relationship("ExamReleaseApproval", back_populates="exam", cascade="all, delete-orphan")


class ExamReleaseApproval(Base):
    __tablename__ = "exam_release_approvals"
    __table_args__ = (UniqueConstraint("exam_id", "officer_id", name="uq_exam_release_officer"),)

    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    officer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    device_id_hash = Column(String(64), nullable=True)
    ip_address = Column(String(64), nullable=True)

    exam = relationship("Exam", back_populates="release_approvals")
    officer = relationship("User")


class ExamSession(Base):
    __tablename__ = "exam_sessions"
    __table_args__ = (UniqueConstraint("exam_id", "candidate_id", name="uq_exam_candidate"),)

    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    seed_hash = Column(String(64), nullable=False)
    started_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False, default="ACTIVE")
    device_id_hash = Column(String(64), nullable=False)
    session_token_hash = Column(String(64), nullable=False, unique=True)
    last_heartbeat_at = Column(DateTime(timezone=True), nullable=True)

    exam = relationship("Exam", back_populates="sessions")
    candidate = relationship("User")
    questions = relationship("ExamSessionQuestion", back_populates="session", cascade="all, delete-orphan", order_by="ExamSessionQuestion.position")


class ExamSessionQuestion(Base):
    __tablename__ = "exam_session_questions"
    __table_args__ = (UniqueConstraint("session_id", "question_id", name="uq_session_question"),)

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("exam_sessions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    position = Column(Integer, nullable=False)
    selected_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    first_exposed_at = Column(DateTime(timezone=True), nullable=True)
    last_exposed_at = Column(DateTime(timezone=True), nullable=True)

    session = relationship("ExamSession", back_populates="questions")
    question = relationship("Question")


class ExamAnswer(Base):
    __tablename__ = "exam_answers"
    __table_args__ = (UniqueConstraint("session_id", "question_id", name="uq_session_answer"),)

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("exam_sessions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer = Column(Text, nullable=False)
    client_nonce = Column(String(64), nullable=False, unique=True)
    submitted_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    session = relationship("ExamSession")
    question = relationship("Question")


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=True)
    session_id = Column(Integer, ForeignKey("exam_sessions.id"), nullable=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String(50), nullable=False, index=True)
    ip_address = Column(String(64), nullable=True)
    device_id_hash = Column(String(64), nullable=True)
    user_agent_hash = Column(String(64), nullable=True)
    event_metadata = Column(JSON, nullable=True)
    risk_score = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)


class SecurityAlert(Base):
    __tablename__ = "security_alerts"

    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=True)
    session_id = Column(Integer, ForeignKey("exam_sessions.id"), nullable=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    risk_score = Column(Integer, nullable=False)
    severity = Column(String(20), nullable=False)
    reasons = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False, default="OPEN")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class ExamCentre(Base):
    __tablename__ = "exam_centres"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    status = Column(String(20), nullable=False, default="ACTIVE")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class CentreDevice(Base):
    __tablename__ = "centre_devices"
    __table_args__ = (UniqueConstraint("centre_id", "device_code", name="uq_centre_device"),)

    id = Column(Integer, primary_key=True)
    centre_id = Column(Integer, ForeignKey("exam_centres.id"), nullable=False)
    device_code = Column(String(100), nullable=False)
    device_token_hash = Column(String(64), nullable=False, unique=True)
    status = Column(String(20), nullable=False, default="ACTIVE")
    registered_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)

    centre = relationship("ExamCentre")


class ExamCentreAssignment(Base):
    __tablename__ = "exam_centre_assignments"
    __table_args__ = (UniqueConstraint("exam_id", "centre_id", name="uq_exam_centre"),)

    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    centre_id = Column(Integer, ForeignKey("exam_centres.id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    exam = relationship("Exam")
    centre = relationship("ExamCentre")


class ExamCandidateAssignment(Base):
    __tablename__ = "exam_candidate_assignments"
    __table_args__ = (UniqueConstraint("exam_id", "candidate_id", name="uq_exam_candidate_assignment"),)

    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    centre_id = Column(Integer, ForeignKey("exam_centres.id"), nullable=False)
    seat_number = Column(String(50), nullable=True)
    identity_status = Column(String(20), nullable=False, default="PENDING")
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    identity_reference_hash = Column(String(64), nullable=True)

    exam = relationship("Exam")
    candidate = relationship("User", foreign_keys=[candidate_id])
    centre = relationship("ExamCentre")
    verifier = relationship("User", foreign_keys=[verified_by])


class ExposureConfig(Base):
    __tablename__ = "exposure_configs"

    id = Column(Integer, primary_key=True)
    warning_threshold = Column(Integer, nullable=False, default=60)
    high_threshold = Column(Integer, nullable=False, default=80)
    retire_threshold = Column(Integer, nullable=False, default=100)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class QuestionExposureLog(Base):
    __tablename__ = "question_exposure_logs"

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False, index=True)
    centre_id = Column(Integer, ForeignKey("exam_centres.id"), nullable=True, index=True)
    exposed_at = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)

    question = relationship("Question")
    candidate = relationship("User")
    exam = relationship("Exam")
    centre = relationship("ExamCentre")

