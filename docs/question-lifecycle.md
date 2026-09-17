# Question Lifecycle & Chain of Custody

## Visual Lifecycle Timeline

Every question in the system follows a strict, state-machine governed chain of custody:

```text
CREATED
   ↓ (Setter creates question)
ENCRYPTED & SEALED
   ↓ (AES-256-GCM + RSA-OAEP envelope encryption)
SUBMITTED
   ↓ (Assigned to independent reviewer)
REVIEWED
   ↓ (Reviewer approves or rejects)
APPROVED
   ↓ (Added to active verified pool)
SELECTED
   ↓ (Cryptographically sampled by dynamic exam generator)
DELIVERED
   ↓ (Just-In-Time single-question CBT delivery)
EXPOSED
   ↓ (Exposure count incremented, logged to audit ledger)
USED
   ↓ (Answer logged with replay-safe client nonce)
RETIRED
   ↓ (Automatically retired when exposure threshold exceeded)
```

---

## Audit Traceability
Every event records:
- **Timestamp** (ISO UTC)
- **Actor Name & Role** (e.g. `Setter Alice`, `Reviewer Charlie`, `Candidate Session #12`)
- **Source Module**
- **Event Payload & Details**
- **Blockchain Block Reference Hash**

Access the visual chain of custody timeline via the API:
```http
GET /investigation/questions/{question_id}/lifecycle
```
or directly in the UI under **Question Bank & Custody**.
