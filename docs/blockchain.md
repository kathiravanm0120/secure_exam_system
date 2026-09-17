# Blockchain Ledger Documentation

## Dual Ledger Architecture

The system supports two interchangeable blockchain backends via a unified interface:

1. **Local Development Ledger (`app/blockchain/ledger.py`)**:
   - Zero-dependency append-only JSON file store (`./data/blockchain.json`).
   - Maintains Genesis block, sequential index, ISO timestamp, event name, canonical payload, and previous SHA-256 block hash.
   - Built-in verification algorithm verifies link hashes and payload integrity.

2. **Hyperledger Fabric Gateway (`app/blockchain/fabric_gateway.py`)**:
   - Production permissioned blockchain adapter interfacing with Fabric peers via gRPC / SDK.
   - Smart contract written in Go (`fabric/chaincode-go/secureexam/contract.go`).
   - Supports methods: `RecordEvent`, `GetEvent`, `GetQuestionEvents`, `GetExamEvents`, `VerifyQuestion`, `RecordReleaseApproval`, `RecordExamRelease`, `RecordQuestionExposure`, `VerifyChain`.

---

## What is Stored On-Chain
- Question ID
- SHA-256 content hash
- Event type (e.g. `QUESTION_CREATED`, `QUESTION_APPROVED`, `EXAM_RELEASED`, `QUESTION_EXPOSED`)
- Actor ID & timestamp
- Verification status

> **Important**: Plaintext question text and answers are **NEVER** stored on-chain. Blockchain provides integrity and auditability, not data encryption.
