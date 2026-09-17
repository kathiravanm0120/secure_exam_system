# Security Threat Model

## Overview
This document details the security threat model for the **Secure Dynamic Examination Paper & CBT Integrity System**. It identifies key threat vectors across the examination lifecycle, attack surfaces, existing protection mechanisms, remaining risks, and recommended mitigations.

---

## Threat Matrix

### 1. Malicious Question Setter
- **Attack Surface**: Question Creation API (`POST /questions`).
- **Threat Vector**: Setter attempts to harvest the complete examination paper or leak authored questions.
- **Existing Protection**:
  - Role-based least-privilege scoping: Setters work exclusively at the single-question level.
  - Setters cannot view or query questions created by other setters (`GET /questions/my` scopes strictly to `created_by == current_user.id`).
  - Setters cannot assign, review, or approve their own questions.
- **Remaining Risk**: A setter can leak their own authored question before encryption.
- **Mitigation**: Fingerprinting and Leak Investigation Module trace leaked text back to the author's identity and audit trail.

---

### 2. Malicious Reviewer
- **Attack Surface**: Reviewer Workspace (`POST /questions/{id}/review`).
- **Threat Vector**: Reviewer attempts to review own questions or leak assigned questions.
- **Existing Protection**:
  - System enforces `question.created_by != reviewer.id` during assignment and review.
  - Reviewers see only specifically assigned questions.
- **Remaining Risk**: Collusion between setter and reviewer.
- **Mitigation**: Dual-officer approval gates, anonymized review assignment, and audit event logging.

---

### 3. Compromised CBT Device / Stolen Session Token
- **Attack Surface**: Candidate CBT API endpoints (`/exams/{id}/start`, `/questions/{pos}`, `/answers`).
- **Threat Vector**: An attacker steals candidate credentials or session tokens to attempt exam from an unauthorized laptop/device.
- **Existing Protection**:
  - Cryptographic Device Binding: Exam session is bound to `X-Exam-Device-ID` and `X-Exam-Device-Token`.
  - Token Hash Validation: Session tokens are stored as SHA-256 hashes in database and validated via constant-time `hmac.compare_digest`.
  - Reconnection Token Rotation: Reconnecting candidate invalidates previous session token instantly.
- **Remaining Risk**: Physical compromise of registered CBT device.
- **Mitigation**: Screen monitoring, session heartbeat frequency checks, and hardware TPM/attestation in production.

---

### 4. Replay Attacks on Answer Submissions
- **Attack Surface**: Answer Submission Endpoint (`POST /exams/{id}/answers`).
- **Threat Vector**: Network packet interception and replay of candidate answers.
- **Existing Protection**:
  - Mandatory unique `client_nonce` per submission.
  - Database enforces unique constraint `uq_session_answer` and client nonce indexing.
  - Re-sending an identical nonce returns idempotent response without creating duplicate answer records or triggering artificial exposure alerts.
- **Remaining Risk**: Network-level MITM if TLS is terminated improperly.
- **Mitigation**: Enforce TLS 1.3 with Certificate Pinning on CBT clients.

---

### 5. Question Bank Theft / Database Compromise
- **Attack Surface**: Storage Layer (`secure_exam.db` / RDBMS).
- **Threat Vector**: An attacker dumps the SQL database or storage volumes.
- **Existing Protection**:
  - Envelope Encryption: Question text and correct answers are encrypted using AES-256-GCM data encryption keys (DEK).
  - Public-Key Wrapping: DEKs are wrapped with RSA-OAEP 3072-bit public keys.
  - Plaintext question content and answers are NEVER persisted unencrypted.
- **Remaining Risk**: Compromise of private key stored on local filesystem in development.
- **Mitigation**: Production HSM/KMS integration where private keys never touch disk or memory unencrypted.

---

### 6. Blockchain Tampering / Audit Log Manipulation
- **Attack Surface**: Audit logs and block history.
- **Threat Vector**: Malicious database administrator attempts to modify past question approval or exam release events to cover unauthorized changes.
- **Existing Protection**:
  - SHA-256 hash chaining: Each block contains `previous_hash` forming an append-only chain.
  - Chain validation endpoint `GET /blockchain/verify` detects any modified, inserted, or deleted blocks.
  - Hyperledger Fabric backend integration distributes ledger state across permissioned consensus nodes.
- **Remaining Risk**: Single node compromise in local development mode.
- **Mitigation**: Multi-organization permissioned Fabric network with Raft/BFT consensus.
