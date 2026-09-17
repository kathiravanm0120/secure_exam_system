# End-to-End Demo Walkthrough Guide

## Overview
This guide provides a step-by-step walkthrough for running the complete end-to-end demonstration of the **Secure Dynamic Examination Paper & CBT Integrity System**.

---

## 1. Quickstart Commands

```bash
# 1. Navigate to backend directory
cd backend

# 2. Seed database with initial users, centre, device, and 30 questions
python -m app.seed

# 3. Start application server
python -m uvicorn app.main:app --reload
```

Open browser at: `http://127.0.0.1:8000/ui`

---

## 2. Seed Accounts & Credentials

| Role | Email | Password | Scope / Capabilities |
|------|-------|----------|----------------------|
| **Admin** | `admin@example.com` | `password123` | Security Dashboard, Exam Release, Investigation, Audit |
| **Setter A** | `setter_a@example.com` | `password123` | Single-question authoring (`CS` questions) |
| **Reviewer A** | `reviewer_a@example.com` | `password123` | Review assigned questions |
| **Exam Officer A** | `officer_a@example.com` | `password123` | Pre-Exam AI Validation, Dual-Officer Release Approval |
| **Candidate A** | `candidate_a@example.com` | `password123` | Device-bound Candidate CBT Exam Session |

---

## 3. Step-by-Step Flow

### Step A: Log in as Admin
1. Sign in with `admin@example.com` / `password123`.
2. Inspect the **Security Dashboard**: metrics show 30 questions, approved pool, active sessions, and valid blockchain ledger status.

### Step B: Question Lifecycle & Chain of Custody
1. Navigate to **Question Bank & Custody**.
2. Click **Visual Timeline** for `Q1`.
3. View the complete chain of custody timeline (`CREATED` → `ENCRYPTED_AND_SEALED` → `REVIEWED_APPROVE` → `SELECTED_FOR_EXAM`).

### Step C: Pre-Exam AI Validation & Dual-Officer Release
1. Navigate to **Exam Management & CBT**.
2. Click **Run Pre-Exam AI Validation** for Exam #2.
3. Observe paper validation report checking syllabus coverage, difficulty balance, duplicate detection, and compromised questions.
4. Click **Approve Release (Officer)**.
5. Click **Release Exam (Admin)** to shift exam status to `RELEASED`.

### Step D: Candidate CBT Exam Execution
1. In CBT Section, enter:
   - Exam ID: `2`
   - Centre ID: `1`
   - Device Code: `DEV-0001`
   - Device Token: `SECURE_DEV_TOKEN_0001`
2. Click **Start Candidate CBT Exam**.
3. Questions are dynamically selected from the approved pool.
4. Navigate between questions, type answers, and click **Save & Next**. Observe answer save confirmation and JIT question delivery.
5. Click **Submit & Finish Exam**.

### Step E: Leak Investigation Module
1. Log in as Admin or Officer.
2. Navigate to **Leak Investigation Module**.
3. Paste suspected leaked text: `"What is the time complexity of array lookup by index?"`.
4. Click **Analyze & Trace Leak Origin**.
5. Observe instant match results showing 100% confidence, matching `Q1`, author (`Setter Alice`), assigned reviewer, delivered sessions, and one-click link to the visual chain of custody timeline!

### Step F: Blockchain Verification
1. Navigate to **Security Operations**.
2. Click **View Immutable Chain**.
3. Observe tamper verification badge (`VALID`) and view append-only JSON block history.
