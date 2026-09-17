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

### 3. Run Backend API Server
```bash
# From backend directory
python -m uvicorn app.main:app --reload
```
- **API Server**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`

### 4. Run Frontend React UI
```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies (if not already installed)
npm install

# Start development server
npm run dev
```
- **React Frontend App**: `http://localhost:5173`

### 5. Run Test Suite
```bash
# From backend directory
python -m pytest tests/ -v
```

---

## 🔑 Demo Account Credentials

| Role | Email | Password | Capabilities |
|------|-------|----------|--------------|
| **ADMIN** | `admin@secureexam.gov` | `Admin@123` | Full System Management, Centres, Devices, Audit |
| **SETTER** | `setter@secureexam.gov` | `Setter@123` | Author & AES-256 Envelope Encrypt Questions |
| **REVIEWER** | `reviewer@secureexam.gov` | `Reviewer@123` | Cryptographic Approval & Review Queue |
| **EXAM_OFFICER** | `officer@secureexam.gov` | `Officer@123` | Pre-Exam AI Validation, Dual Release Approvals |
| **CANDIDATE** | `candidate@secureexam.gov` | `Candidate@123` | Device-bound Secure CBT Examination |
| **SECURITY_AUDITOR** | `auditor@secureexam.gov` | `Auditor@123` | Real-time Risk Scoring, Anomaly Monitoring, Simhash Leak Tracing |

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
