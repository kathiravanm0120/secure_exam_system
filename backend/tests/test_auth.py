"""Tests for Authentication & Role Access Control."""
from __future__ import annotations


def test_auth_valid_login(client, seed_users):
    res = client.post("/auth/login", json={"email": "admin@test.com", "password": "password123"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_auth_invalid_password(client, seed_users):
    res = client.post("/auth/login", json={"email": "admin@test.com", "password": "wrongpassword"})
    assert res.status_code == 401
    assert "detail" in res.json()


def test_auth_register_existing_email(client, seed_users):
    res = client.post(
        "/auth/register",
        json={"name": "New Admin", "email": "admin@test.com", "password": "password123", "role": "ADMIN"},
    )
    assert res.status_code == 409


def test_role_restrictions(client, seed_users):
    # Candidate login
    cand_login = client.post("/auth/login", json={"email": "cand1@test.com", "password": "password123"}).json()
    cand_token = cand_login["access_token"]

    # Candidate trying to create question should be forbidden (403)
    res = client.post(
        "/questions",
        headers={"Authorization": f"Bearer {cand_token}"},
        json={"content": "Sample?", "answer": "Ans", "subject": "CS", "topic": "Algo", "difficulty": "EASY"},
    )
    assert res.status_code == 403
