"""Tests for Question Security, Encryption & Integrity."""
from __future__ import annotations

import pytest
from app.security.encryption import decrypt_question, encrypt_question


def test_encryption_roundtrip():
    content = "What is the complexity of binary search?"
    answer = "O(log n)"
    encrypted = encrypt_question(content, answer)

    assert "encrypted_content" in encrypted
    assert "wrapped_key" in encrypted
    assert "content_hash" in encrypted
    assert encrypted["crypto_version"].startswith("v1-")

    dec_content, dec_answer = decrypt_question(
        encrypted["encrypted_content"],
        encrypted["encryption_nonce"],
        encrypted["wrapped_key"],
        encrypted["content_hash"],
    )
    assert dec_content == content
    assert dec_answer == answer


def test_encryption_tamper_detection():
    content = "Authentic question content"
    answer = "Secret"
    encrypted = encrypt_question(content, answer)

    with pytest.raises(ValueError, match="Question integrity check failed"):
        decrypt_question(
            encrypted["encrypted_content"],
            encrypted["encryption_nonce"],
            encrypted["wrapped_key"],
            "0000000000000000000000000000000000000000000000000000000000000000",
        )


def test_setter_workflow_and_isolation(client, seed_users):
    # Login Setter 1
    s1_login = client.post("/auth/login", json={"email": "setter1@test.com", "password": "password123"}).json()
    s1_token = s1_login["access_token"]

    # Setter 1 creates a question
    res = client.post(
        "/questions",
        headers={"Authorization": f"Bearer {s1_token}"},
        json={"content": "Setter 1 Question?", "answer": "Answer 1", "subject": "CS", "topic": "DS", "difficulty": "EASY"},
    )
    assert res.status_code == 201
    q_data = res.json()
    q_id = q_data["id"]

    # Setter 1 sees it in /my
    my_res = client.get("/questions/my", headers={"Authorization": f"Bearer {s1_token}"})
    assert my_res.status_code == 200
    my_ids = [q["id"] for q in my_res.json()]
    assert q_id in my_ids

    # Setter 2 login
    s2_login = client.post("/auth/login", json={"email": "setter2@test.com", "password": "password123"}).json()
    s2_token = s2_login["access_token"]

    # Setter 2 does NOT see Setter 1's question in /my
    s2_my_res = client.get("/questions/my", headers={"Authorization": f"Bearer {s2_token}"})
    s2_ids = [q["id"] for q in s2_my_res.json()]
    assert q_id not in s2_ids


def test_reviewer_assignment_and_approval(client, seed_users):
    admin_tok = client.post("/auth/login", json={"email": "admin@test.com", "password": "password123"}).json()["access_token"]
    s1_tok = client.post("/auth/login", json={"email": "setter1@test.com", "password": "password123"}).json()["access_token"]
    rev1_tok = client.post("/auth/login", json={"email": "rev1@test.com", "password": "password123"}).json()["access_token"]

    # Create question
    q_res = client.post(
        "/questions",
        headers={"Authorization": f"Bearer {s1_tok}"},
        json={"content": "To be reviewed question?", "answer": "Ans", "subject": "CS", "topic": "Algo", "difficulty": "MEDIUM"},
    )
    qid = q_res.json()["id"]

    # Assign Reviewer 1
    rev1_id = seed_users["reviewer1"].id
    assign_res = client.post(f"/questions/{qid}/assign/{rev1_id}", headers={"Authorization": f"Bearer {admin_tok}"})
    assert assign_res.status_code == 200

    # Reviewer 1 approves question
    rev_res = client.post(
        f"/questions/{qid}/review",
        headers={"Authorization": f"Bearer {rev1_tok}"},
        json={"decision": "APPROVE", "comments": "Looks good"},
    )
    assert rev_res.status_code == 200
    assert rev_res.json()["status"] == "APPROVED"
