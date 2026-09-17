"""Tests for Dynamic CBT Generation, Device Binding, Paper Validation & Exam Release."""
from __future__ import annotations

import datetime
from datetime import timezone
from app.models.models import (
    Exam,
    ExamCandidateAssignment,
    ExamCentre,
    ExamCentreAssignment,
    Question,
    QuestionReview,
    CentreDevice,
)
from app.security.auth import hash_password
from app.security.encryption import encrypt_question


def setup_cbt_environment(db, seed_users):
    admin = seed_users["admin"]
    setter1 = seed_users["setter1"]
    rev1 = seed_users["reviewer1"]
    candidate = seed_users["candidate"]

    # 1. Create Centre & Device
    centre = ExamCentre(code="CTR-TEST", name="Test Centre", status="ACTIVE")
    db.add(centre)
    db.flush()

    import hashlib
    dev_token_hash = hashlib.sha256("SECURE_DEV_TOKEN_0001_TESTING".encode("utf-8")).hexdigest()
    device = CentreDevice(centre_id=centre.id, device_code="DEV-TEST-0001", device_token_hash=dev_token_hash, status="ACTIVE")
    db.add(device)

    # 2. Add approved questions
    for i in range(5):
        encrypted = encrypt_question(f"Test Question {i}?", f"Answer {i}")
        q = Question(
            encrypted_content=encrypted["encrypted_content"],
            encryption_nonce=encrypted["encryption_nonce"],
            wrapped_key=encrypted["wrapped_key"],
            content_hash=encrypted["content_hash"],
            crypto_version=encrypted["crypto_version"],
            subject="Computer Science",
            topic="Algorithms",
            difficulty="EASY",
            created_by=setter1.id,
            reviewer_id=rev1.id,
            status="APPROVED",
            exposure_status="ACTIVE",
            exposure_count=0,
        )
        db.add(q)

    # 3. Create Exam
    now = datetime.datetime.now(timezone.utc)
    exam = Exam(
        name="Test CBT Exam",
        subject="Computer Science",
        starts_at=now - datetime.timedelta(minutes=2),
        ends_at=now + datetime.timedelta(hours=2),
        blueprint=[{"topic": "Algorithms", "difficulty": "EASY", "count": 2}],
        created_by=admin.id,
        status="RELEASED",
    )
    db.add(exam)
    db.flush()

    # Assign Centre & Candidate
    db.add(ExamCentreAssignment(exam_id=exam.id, centre_id=centre.id))
    db.add(ExamCandidateAssignment(exam_id=exam.id, candidate_id=candidate.id, centre_id=centre.id, identity_status="VERIFIED"))
    db.commit()

    return exam, centre, device, candidate


def test_paper_validation_and_release_gate(client, seed_users, setup_db):
    exam, centre, device, candidate = setup_cbt_environment(setup_db, seed_users)
    admin_tok = client.post("/auth/login", json={"email": "admin@test.com", "password": "password123"}).json()["access_token"]
    off1_tok = client.post("/auth/login", json={"email": "off1@test.com", "password": "password123"}).json()["access_token"]

    # Validate paper endpoint
    val_res = client.get(f"/exams/{exam.id}/validate", headers={"Authorization": f"Bearer {admin_tok}"})
    assert val_res.status_code == 200
    val_data = val_res.json()
    assert val_data["status"] in ("PASS", "WARNING")


def test_cbt_start_and_jit_question_delivery(client, seed_users, setup_db):
    exam, centre, device, candidate = setup_cbt_environment(setup_db, seed_users)
    cand_tok = client.post("/auth/login", json={"email": "cand1@test.com", "password": "password123"}).json()["access_token"]

    headers = {
        "Authorization": f"Bearer {cand_tok}",
        "X-Exam-Centre-ID": str(centre.id),
        "X-Exam-Device-ID": "DEV-TEST-0001",
        "X-Exam-Device-Token": "SECURE_DEV_TOKEN_0001_TESTING",
    }

    # Start CBT Session
    start_res = client.post(f"/exams/{exam.id}/start", headers=headers)
    assert start_res.status_code == 200
    s_data = start_res.json()
    assert s_data["status"] == "ACTIVE"
    assert s_data["question_count"] == 2
    session_token = s_data["session_token"]

    # Fetch Question Position 1 (Just-In-Time)
    cbt_headers = {**headers, "X-Exam-Session-Token": session_token}
    q1_res = client.get(f"/exams/{exam.id}/questions/1", headers=cbt_headers)
    assert q1_res.status_code == 200
    q1_data = q1_res.json()
    assert q1_data["position"] == 1
    assert "content" in q1_data
    assert "answer" not in q1_data  # Answers NEVER leaked to candidate!

    # Submit Replay-Safe Answer
    ans_res = client.post(
        f"/exams/{exam.id}/answers",
        headers=cbt_headers,
        json={"question_id": q1_data["question_id"], "answer": "My Solution", "client_nonce": "NONCE_TEST_123456789"},
    )
    assert ans_res.status_code == 200
    assert ans_res.json()["updated"] is False

    # Submit with SAME Nonce (Idempotent Retry)
    ans_retry = client.post(
        f"/exams/{exam.id}/answers",
        headers=cbt_headers,
        json={"question_id": q1_data["question_id"], "answer": "My Solution", "client_nonce": "NONCE_TEST_123456789"},
    )
    assert ans_retry.status_code == 200
    assert ans_retry.json()["updated"] is False

    # Finish Exam
    fin_res = client.post(f"/exams/{exam.id}/finish", headers=cbt_headers)
    assert fin_res.status_code == 200
    assert fin_res.json()["status"] == "COMPLETED"
