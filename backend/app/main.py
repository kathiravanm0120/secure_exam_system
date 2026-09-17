from fastapi import FastAPI
from fastapi.responses import FileResponse
from app.database import Base, engine
from app.routes.auth import router as auth_router
from app.routes.questions import router as questions_router
from app.routes.blockchain import router as blockchain_router
from app.routes.exams import router as exams_router
from app.routes.security import router as security_router
from app.routes.dashboard import router as dashboard_router
from app.routes.identity import router as identity_router
from app.routes.fingerprints import router as fingerprints_router
from app.routes.investigation import router as investigation_router
from app.security.encryption import _ensure_authority_keypair

# Prototype initialization. Production should use migrations and an HSM/KMS.
_ensure_authority_keypair()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure Exam System", version="1.0.0")
app.include_router(auth_router)
app.include_router(questions_router)
app.include_router(blockchain_router)
app.include_router(exams_router)
app.include_router(security_router)
app.include_router(dashboard_router)
app.include_router(identity_router)
app.include_router(fingerprints_router)
app.include_router(investigation_router)



@app.get("/")
def root():
    return {"name": "Secure Exam System", "status": "running", "phase": 10, "security": "envelope-encryption+blockchain-audit+dynamic-cbt-generation+item-exposure-control+device-bound-session+anti-replay-cbt+behavior-risk-scoring+time-locked-release+dual-officer-authorization+candidate-identity+centre-device-authorization"}


@app.get("/ui", include_in_schema=False)
def ui():
    return FileResponse("app/static/index.html")
