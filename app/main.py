from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from . import models, schemas, crud
from .database import engine, Base, get_db

# Tabloları oluştur (eğer yoksa)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Digital Ethics Monitor API",
    description="Secure backend for monitoring AI decisions",
    version="0.1.0",
)


# --------- HEALTH CHECK ---------

@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}


# --------- BASİT REQUEST BOYUTU KONTROL MIDDLEWARE'İ ---------

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


# --------- AI DECISIONS ---------

@app.post(
    "/decisions/",
    response_model=schemas.AIDecisionRead,
    tags=["decisions"],
)
def create_decision(
    decision: schemas.AIDecisionCreate,
    db: Session = Depends(get_db),
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
):
    decision = crud.get_ai_decision(db, log.decision_id)
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision does not exist.",
        )
    return crud.create_decision_log(db, log)
