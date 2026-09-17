# Secure Exam System — Backend & Security Service

For complete project documentation, architectural diagrams, threat model, and end-to-end demo instructions, please refer to the root documentation:

- **[Root Project README](../README.md)**
- **[Architecture Documentation](../docs/architecture.md)**
- **[Security Threat Model](../docs/security/threat-model.md)**
- **[End-to-End Demo Walkthrough Guide](../docs/demo.md)**

---

## Quickstart

```bash
# Seed database with sample users, centre, device, and 30 questions
python -m app.seed

# Run API server
python -m uvicorn app.main:app --reload

# Run test suite
python -m pytest tests/ -v
```

Open `http://127.0.0.1:8000/ui` in your browser.
