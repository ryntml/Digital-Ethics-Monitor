from datetime import timedelta
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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
    version="1.0.0",
)

app.add_middleware(  # frontend ile iletişim için gerekli
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    existing = crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists.",
        )

    return crud.create_user(db, user)

@app.get("/users/me", response_model=schemas.UserRead, tags=["users"])
def read_users_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_user(db, current_user["id"])


@app.patch("/users/{user_id}/role", tags=["admin"])
def update_user_role(user_id: int,
                     role_data: schemas.UserRoleUpdate,
                     db: Session = Depends(get_db),
                     current_user=Depends(require_roles(["admin"]))
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = role_data.role
    db.commit()
    return {"status": "success", "new_role": user.role}


# --------- AUTH ---------

@app.post("/auth/login", response_model=schemas.TokenResponse, tags=["auth"])
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(models.User)
        .filter(models.User.email == data.username)
        .first()
    )

    if not user:
        user = db.query(models.User).filter(models.User.username == data.username).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "id": user.id},
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

    return crud.create_ai_decision(db, decision, owner_id=user_payload["id"])


@app.get(
    "/decisions/{decision_id}",
    response_model=schemas.AIDecisionRead,
    tags=["decisions"],
)
def read_decision(decision_id: int, db: Session = Depends(get_db), user_payload=Depends(require_roles(["admin", "analyst", "viewer"]))):
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
    if log.decision_id:
        decision = crud.get_ai_decision(db, log.decision_id)
        if not decision:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Decision does not exist.",
            )

    log_hash = generate_hash(log.message + str(user_payload["id"]))

    db_log = models.DecisionLog(
        decision_id=log.decision_id,
        actor_user_id=user_payload["id"], # Logu yazan adminin ID'si
        event_type=log.event_type,        # "SYSTEM", "WARNING" vb.
        message=log.message,
        hash=log_hash,
    )

    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    
    return db_log


# --------- ETHICS ENGINE ---------

@app.post(
    "/ethics/evaluate",
    tags=["ethics"],
)
def evaluate_decision_ethics(
    decision_in: schemas.AIDecisionCreate,
    db: Session = Depends(get_db),
    user_payload=Depends(require_roles(["admin", "analyst"])),
):

    status_label, explanation = evaluate_ethics(
        decision_in.decision_label,
        decision_in.score,
        decision_in.sensitive_attribute,
    )

    db_decision = models.AIDecision(
        owner_id=user_payload["id"],
        decision_label=status_label,
        score=decision_in.score,
        sensitive_attribute=decision_in.sensitive_attribute
    )
    db.add(db_decision)
    db.commit()
    db.refresh(db_decision)

    log_message = f"ETHICS EVALUATION: User {user_payload['sub']} processed decision. Result: {status_label}. Reason: {explanation}"
  
    log_hash = generate_hash(log_message + str(db_decision.id) + str(user_payload["id"]))

    db_log = models.DecisionLog(
        decision_id=db_decision.id,
        actor_user_id=user_payload["id"],
        event_type="ETHICS_EVALUATION",
        message=log_message,
        hash=log_hash,
    )

    db.add(db_log)
    db.commit()

    return {
        "decision_id": db_decision.id,
        "ethics_status": status_label,
        "explanation": explanation,
        "log_hash": log_hash,
    }

# --------- ADMIN AUDIT LOGS ---------

@app.get("/admin/logs", response_model=List[schemas.DecisionLogRead], tags=["admin"])
def read_audit_logs(
    limit: int = 100,
    event_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"])) # Sadece ADMIN
):
    query = db.query(models.DecisionLog)
    if event_type:
        query = query.filter(models.DecisionLog.event_type == event_type)
    
    return query.order_by(models.DecisionLog.created_at.desc()).limit(limit).all()


# --------- DASHBOARD STATS (Frontend Integration) ---------

@app.get("/stats/dashboard", response_model=schemas.DashboardStats, tags=["dashboard"])
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user) # Login olan herkes görebilir
):
    total = db.query(models.AIDecision).count()
    biased = db.query(models.AIDecision).filter(models.AIDecision.decision_label == "BIASED").count()
    
    # Adalet skoru hesabı (1.0 = Mükemmel, 0.0 = Çok Kötü)
    fairness = 1.0
    if total > 0:
        fairness = 1.0 - (biased / total)
    
    return {
        "total_decisions": total,
        "bias_count": biased,
        "fairness_score": round(fairness, 2),
        "system_health": 100
    }
