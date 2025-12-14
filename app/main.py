from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from . import models, schemas, crud
from .database import engine, Base, get_db
from .security import verify_password, create_access_token
from .security import get_current_user, require_roles  # get_current_user swagger oauth için gerekli
from .security import generate_hash
from .ethics import evaluate_ethics


app = FastAPI(
    title="Digital Ethics Monitor API",
    description="Secure backend for monitoring AI decisions",
    version="0.1.0",
)


# ✅ Tabloları her server açılışında garanti oluştur
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


# --------- HEALTH CHECK ---------

@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}


# --------- REQUEST BOYUTU KONTROL MIDDLEWARE ---------

MAX_CONTENT_LENGTH = 1024 * 1024  # 1 MB


@app.middleware("http")
async def validate_request_size(request: Request, call_next):
    if int(request.headers.get("content-length") or 0) > MAX_CONTENT_LENGTH:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={"detail": "Request too large."},
        )

    response = await call_next(request)
    return response


# --------- USERS ---------

@app.post("/users/", response_model=schemas.UserRead, tags=["users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Aynı kullanıcı adı veya email var mı?
    existing = (
        db.query(models.User)
        .filter(
            (models.User.username == user.username)
            | (models.User.email == user.email)
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists.",
        )

    return crud.create_user(db, user)


@app.get("/users/{user_id}", response_model=schemas.UserRead, tags=["users"])
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# --------- AUTH ---------

@app.post("/auth/login", response_model=schemas.TokenResponse, tags=["auth"])
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(models.User)
        .filter(models.User.username == data.username)
        .first()
    )

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=30),
    )

    return {"access_token": access_token, "token_type": "bearer"}


# --------- AI DECISIONS ---------

@app.post(
    "/decisions/",
    response_model=schemas.AIDecisionRead,
    tags=["decisions"],
)
def create_decision(
    decision: schemas.AIDecisionCreate,
    db: Session = Depends(get_db),
    user_payload=Depends(require_roles(["admin", "analyst"])),
):
    owner = crud.get_user(db, decision.owner_id)
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner (user) does not exist.",
        )

    return crud.create_ai_decision(db, decision)


@app.get(
    "/decisions/{decision_id}",
    response_model=schemas.AIDecisionRead,
    tags=["decisions"],
)
def read_decision(decision_id: int, db: Session = Depends(get_db)):
    db_decision = crud.get_ai_decision(db, decision_id)
    if not db_decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    return db_decision


# --------- DECISION LOGS ---------

@app.post(
    "/logs/",
    response_model=schemas.DecisionLogRead,
    tags=["logs"],
)
def create_log(
    log: schemas.DecisionLogCreate,
    db: Session = Depends(get_db),
    user_payload=Depends(require_roles(["admin"])),
):
    decision = crud.get_ai_decision(db, log.decision_id)
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision does not exist.",
        )
    return crud.create_decision_log(db, log)


# --------- ETHICS ENGINE ---------

@app.post(
    "/ethics/evaluate",
    tags=["ethics"],
)
def evaluate_decision_ethics(
    decision_id: int,
    db: Session = Depends(get_db),
    user_payload=Depends(require_roles(["admin", "analyst"])),
):
    decision = crud.get_ai_decision(db, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    status_label, explanation = evaluate_ethics(
        decision.decision_label,
        decision.score,
        decision.sensitive_attribute,
    )

    log_message = f"ETHICS RESULT: {status_label} | {explanation}"
    log_hash = generate_hash(log_message)

    log = models.DecisionLog(
        decision_id=decision.id,
        message=log_message,
        hash=log_hash,
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return {
        "decision_id": decision.id,
        "ethics_status": status_label,
        "explanation": explanation,
        "log_hash": log_hash,
    }
