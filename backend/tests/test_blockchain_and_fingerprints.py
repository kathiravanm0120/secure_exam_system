"""Tests for Blockchain Audit Ledger, Fingerprinting & Leak Investigation."""
from __future__ import annotations

from app.blockchain.service import add_event, get_chain, verify_chain
from app.security.fingerprint import (
    compute_exam_fingerprint,
    compute_question_fingerprint,
    compute_text_similarity,
)


def test_blockchain_event_and_verification():
    ev = add_event("TEST_EVENT", {"detail": "unit test"})
    assert "hash" in ev
    assert "index" in ev

    chain = get_chain()
    assert len(chain) >= 2  # Genesis + at least 1 event

    res = verify_chain()
    assert res["valid"] is True


def test_fingerprinting_deterministic():
    fp1 = compute_question_fingerprint(
        content="What is a binary tree?",
        subject="Computer Science",
        topic="Trees",
        difficulty="EASY",
        answer="A tree structure",
    )
    fp2 = compute_question_fingerprint(
        content="what is a binary tree? ",
        subject="computer science",
        topic="trees",
        difficulty="easy",
        answer="a tree structure",
    )
    assert fp1 == fp2


def test_exam_paper_fingerprinting():
    q_fps = ["hash1", "hash2", "hash3"]
    exam_fp1 = compute_exam_fingerprint(q_fps)
    exam_fp2 = compute_exam_fingerprint(["hash1", "hash2", "hash3"])
    exam_fp3 = compute_exam_fingerprint(["hash2", "hash1", "hash3"])

    assert exam_fp1 == exam_fp2
    assert exam_fp1 != exam_fp3


def test_leak_investigation_endpoint(client, seed_users):
    admin_tok = client.post("/auth/login", json={"email": "admin@test.com", "password": "password123"}).json()["access_token"]
    s1_tok = client.post("/auth/login", json={"email": "setter1@test.com", "password": "password123"}).json()["access_token"]

    # Create question
    content = "Unique Leaked Question Topic on QuickSort Algorithm"
    q_res = client.post(
        "/questions",
        headers={"Authorization": f"Bearer {s1_tok}"},
        json={"content": content, "answer": "O(n log n)", "subject": "CS", "topic": "Algo", "difficulty": "MEDIUM"},
    )
    qid = q_res.json()["id"]

    # Run leak investigation
    inv_res = client.post(
        "/investigation/analyze",
        headers={"Authorization": f"Bearer {admin_tok}"},
        json={"suspected_text": "leaked question topic on quicksort algorithm"},
    )
    assert inv_res.status_code == 200
    data = inv_res.json()
    assert data["matches_found"] >= 1
    assert data["top_match"]["question_id"] == qid

    # Test lifecycle timeline
    lc_res = client.get(
        f"/investigation/questions/{qid}/lifecycle",
        headers={"Authorization": f"Bearer {admin_tok}"},
    )
    assert lc_res.status_code == 200
    lc_data = lc_res.json()
    assert lc_data["question_id"] == qid
    assert len(lc_data["timeline"]) >= 2
