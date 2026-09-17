# Secure Dynamic Examination Paper & CBT Integrity System

An end-to-end, production-ready secure CBT examination platform featuring envelope question encryption, cryptographic paper fingerprinting, automated leak origin tracing, visual chain of custody, dynamic blueprint sampling, device-bound CBT delivery, pre-exam AI paper validation, explainable security risk scoring, and Hyperledger Fabric audit ledger integration.

---

## 🚀 Quickstart Guide

### 1. Installation & Environment Setup
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt
```

### 2. Seed Demo Environment
```bash
# Seed users, exam centre CTR-001, CBT device DEV-0001, 30 CS questions, and scheduled exam
python -m app.seed
```

### 3. Run Application Server
```bash
python -m uvicorn app.main:app --reload
```

- **Web Dashboard & UI**: `http://127.0.0.1:8000/ui`
- **Interactive Swagger API Docs**: `http://127.0.0.1:8000/docs`

### 4. Run Test Suite
```bash
python -m pytest tests/ -v
```

---

## 🔑 Demo Account Credentials

| Role | Email | Password | Capabilities |
|------|-------|----------|--------------|
| **ADMIN** | `admin@example.com` | `password123` | Security Dashboard, Release Exam, Leak Investigation, Audit |
| **SETTER** | `setter_a@example.com` | `password123` | Author & encrypt individual questions |
| **REVIEWER** | `reviewer_a@example.com` | `password123` | Review & approve assigned questions |
| **EXAM_OFFICER** | `officer_a@example.com` | `password123` | Pre-Exam AI Validation, Dual-Officer Release Approval |
| **CANDIDATE** | `candidate_a@example.com` | `password123` | Device-bound Candidate CBT Exam Session |

---

## 📚 Comprehensive Documentation

- **[Architecture Guide](docs/architecture.md)**: Component diagrams and service boundaries.
- **[Security Architecture](docs/security.md)**: Encryption pillars, envelope keys, and security controls.
- **[Security Threat Model](docs/security/threat-model.md)**: Detailed threat matrix, attack surfaces, and mitigations.
- **[Blockchain Ledger](docs/blockchain.md)**: Local append-only chain and Hyperledger Fabric gateway adapter.
- **[Key Management](docs/key-management.md)**: RSA-OAEP / AES-GCM envelope encryption and KMS migration path.
- **[CBT Security](docs/cbt-security.md)**: Device binding, session tokens, JIT question delivery, anti-replay nonces.
- **[Question Lifecycle](docs/question-lifecycle.md)**: Visual chain of custody timeline (`CREATED` → `EXPOSED` → `RETIRED`).
- **[Demo Walkthrough Guide](docs/demo.md)**: Step-by-step instructions to demonstrate all 29 system phases.
