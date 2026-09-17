# Secure CBT Delivery & Candidate Authorization

## Session Security Model

Every candidate CBT session enforces multi-factor authorization headers on sensitive requests:

```http
POST /exams/1/questions/1 HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Bearer <JWT_CANDIDATE_TOKEN>
X-Exam-Session-Token: <OPAQUE_SESSION_TOKEN>
X-Exam-Centre-ID: 1
X-Exam-Device-ID: DEV-0001
X-Exam-Device-Token: SECURE_DEV_TOKEN_0001
```

---

## Authorization Checks
1. **JWT Validity**: Verifies candidate identity and `role == CANDIDATE`.
2. **Identity Verification**: Verifies candidate has `ExamCandidateAssignment.identity_status == VERIFIED` for the exam.
3. **Centre Assignment**: Verifies candidate's assigned centre matches `X-Exam-Centre-ID` and centre is assigned to exam.
4. **Device Token Binding**: Verifies `X-Exam-Device-ID` is registered to the centre and `X-Exam-Device-Token` matches registered hash.
5. **Session Ownership & Device Match**: Verifies candidate is not running on a different device or session token.
6. **Replay-Safe Answer Submission**: Answers submitted with `client_nonce` ensure duplicate packet submissions return idempotent responses without altering state.
7. **Just-In-Time Question Delivery**: Candidate endpoints deliver single questions (`/questions/{pos}`) and **NEVER** expose correct answers.
