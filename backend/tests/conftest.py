"""Pytest configuration and test database fixtures."""
from __future__ import annotations

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.security.auth import hash_password
from app.models.models import User, ExamCentre, CentreDevice, Exam, Question, ExamCentreAssignment, ExamCandidateAssignment
from app.security.encryption import _ensure_authority_keypair, encrypt_question

from sqlalchemy.pool import StaticPool

TEST_DB_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    _ensure_authority_keypair()
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def seed_users(setup_db):
    db = setup_db
    users = {
        "admin": User(name="Admin", email="admin@test.com", password_hash=hash_password("password123"), role="ADMIN"),
        "setter1": User(name="Setter 1", email="setter1@test.com", password_hash=hash_password("password123"), role="SETTER"),
        "setter2": User(name="Setter 2", email="setter2@test.com", password_hash=hash_password("password123"), role="SETTER"),
        "reviewer1": User(name="Reviewer 1", email="rev1@test.com", password_hash=hash_password("password123"), role="REVIEWER"),
        "reviewer2": User(name="Reviewer 2", email="rev2@test.com", password_hash=hash_password("password123"), role="REVIEWER"),
        "officer1": User(name="Officer 1", email="off1@test.com", password_hash=hash_password("password123"), role="EXAM_OFFICER"),
        "officer2": User(name="Officer 2", email="off2@test.com", password_hash=hash_password("password123"), role="EXAM_OFFICER"),
        "candidate": User(name="Candidate 1", email="cand1@test.com", password_hash=hash_password("password123"), role="CANDIDATE"),
    }
    for u in users.values():
        db.add(u)
    db.commit()
    for u in users.values():
        db.refresh(u)
    return users
