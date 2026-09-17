# Security Architecture & Controls

## Core Security Pillars

### 1. Cryptographic Envelope Encryption
Questions are encrypted using AES-256-GCM prior to database insertion. A fresh 256-bit Data Encryption Key (DEK) is generated per question. The DEK is encrypted (wrapped) with a 3072-bit RSA-OAEP authority public key. Only the authority private key can unwrap the DEK to decrypt question contents.

### 2. Immutable Blockchain Audit Ledger
All state transitions (Question Creation, Assignment, Review, Approval, Exam Release, Candidate Session Start, Question Exposure, Answer Submission) are logged as canonical JSON blocks in an append-only hash chain. Each block references the SHA-256 hash of the preceding block.

### 3. Explainable Risk Engine
Candidate behavioral events are evaluated continuously. Rapid question fetching (>8 requests in 10s), IP drift, device token changes, excessive answer submissions, or unregistered hardware elevate candidate risk scores (0-100) and generate admin-visible security alerts.

### 4. Deterministic Fingerprinting & Leak Investigation
For every question, a deterministic SHA-256 fingerprint is generated from canonicalized text. When a document leak is suspected, the Leak Investigation Module computes exact hash matches and token-overlap similarity Jaccard scores to identify the source question, author, reviewer, exam sessions, and complete chain of custody.

### 5. Pre-Exam AI Paper Validation
Exams cannot be released if pre-exam validation detects unapproved items, retired/compromised questions, insufficient topic/difficulty coverage, or duplicate question content.
