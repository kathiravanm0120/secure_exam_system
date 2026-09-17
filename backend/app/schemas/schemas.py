from typing import Literal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

Role = Literal["SETTER", "REVIEWER", "ADMIN", "CANDIDATE", "EXAM_OFFICER"]
Difficulty = Literal["EASY", "MEDIUM", "HARD"]
Decision = Literal["APPROVE", "REJECT"]


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: Role


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    role: Role


class QuestionCreate(BaseModel):
    content: str = Field(min_length=5)
    answer: str = Field(min_length=1)
    subject: str = Field(min_length=1, max_length=100)
    topic: str = Field(min_length=1, max_length=100)
    difficulty: Difficulty


class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    content: str
    subject: str
    topic: str
    difficulty: Difficulty
    created_by: int
    reviewer_id: int | None
    status: str
    content_hash: str
    crypto_version: str


class ReviewCreate(BaseModel):
    decision: Decision
    comments: str | None = None


class BlueprintRule(BaseModel):
    topic: str = Field(min_length=1, max_length=100)
    difficulty: Difficulty
    count: int = Field(gt=0, le=200)


class CentreCreate(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=200)


class CentreDeviceCreate(BaseModel):
    device_code: str = Field(min_length=4, max_length=100)


class CandidateAssignmentCreate(BaseModel):
    candidate_id: int
    centre_id: int
    seat_number: str | None = Field(default=None, max_length=50)
    identity_reference: str | None = Field(default=None, max_length=200)


class CandidateAssignmentOut(BaseModel):
    id: int
    exam_id: int
    candidate_id: int
    centre_id: int
    seat_number: str | None
    identity_status: str
    verified_at: datetime | None


class ExamCreate(BaseModel):
    name: str = Field(min_length=3, max_length=200)
    subject: str = Field(min_length=1, max_length=100)
    starts_at: datetime
    ends_at: datetime
    rules: list[BlueprintRule] = Field(min_length=1, max_length=50)


class ExamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    subject: str
    starts_at: datetime
    ends_at: datetime
    blueprint: list[BlueprintRule]
    status: str


class ReleaseApprovalOut(BaseModel):
    id: int
    exam_id: int
    officer_id: int
    approved_at: datetime


class ReleaseStatusOut(BaseModel):
    exam_id: int
    status: str
    release_window_open: bool
    required_approvals: int
    approval_count: int
    approver_ids: list[int]
    released: bool


class CandidateQuestionOut(BaseModel):
    position: int
    question_id: int
    content: str
    subject: str
    topic: str
    difficulty: Difficulty


class ExamSessionOut(BaseModel):
    session_id: int
    exam_id: int
    status: str
    question_count: int
    started_at: datetime
    session_token: str | None = None
    device_bound: bool = True


class CandidatePaperOut(BaseModel):
    session_id: int
    exam_id: int
    questions: list[CandidateQuestionOut]


class ExposureOut(BaseModel):
    question_id: int
    exposure_count: int
    first_exposed_at: datetime | None
    last_exposed_at: datetime | None
    exposure_status: str


class AnswerSubmit(BaseModel):
    question_id: int
    answer: str = Field(max_length=10000)
    client_nonce: str = Field(min_length=16, max_length=64)


class AnswerOut(BaseModel):
    question_id: int
    submitted_at: datetime
    updated: bool


class SecurityEventOut(BaseModel):
    id: int
    event_type: str
    risk_score: int
    created_at: datetime


class SecurityAlertOut(BaseModel):
    id: int
    exam_id: int | None
    session_id: int | None
    candidate_id: int | None
    risk_score: int
    severity: str
    reasons: list[str]
    status: str
    created_at: datetime


class FingerprintMatchRequest(BaseModel):
    suspected_text: str = Field(min_length=3)
    exam_id: int | None = None


class FingerprintMatchOut(BaseModel):
    match: bool
    question_id: int | None = None
    exam_id: str | None = None
    confidence: float
    canonical_hash: str | None = None
    matched_subject: str | None = None
    matched_topic: str | None = None


class InvestigationRequest(BaseModel):
    suspected_text: str = Field(min_length=3)
    exam_id: int | None = None
    document_hash: str | None = None
    metadata: dict | None = None


class PaperValidationReportOut(BaseModel):
    exam_id: int
    status: Literal["PASS", "WARNING", "BLOCKED"]
    syllabus_coverage: str
    difficulty_balance: str
    duplicate_detection: str
    exposed_questions: str
    compromised_questions: str
    approval_status: str
    details: list[str]

