from datetime import timedelta
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas, crud
from .database import engine, Base, get_db, SessionLocal
from .security import verify_password, create_access_token
from .security import get_current_user, require_roles  # get_current_user swagger oauth için gerekli
from .security import generate_hash, encrypt_data
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
    
    # Generate demo data if database is empty
    generate_demo_data()


def generate_demo_data():
    """Generate sample data for dashboard demonstration"""
    from .security import hash_password, encrypt_data, generate_hash
    import random
    
    db = SessionLocal()
    try:
        # Check if demo user exists
        demo_user = db.query(models.User).filter(models.User.email == "demo@test.com").first()
        
        if not demo_user:
            # Create demo user
            demo_user = models.User(
                username="demo",
                email="demo@test.com",
                password_hash=hash_password("demo123"),
                role="analyst"
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
            print("✅ Demo user created: demo@test.com / demo123")
        
        # Check if we have enough decisions
        decision_count = db.query(models.AIDecision).count()
        
        if decision_count < 5:
            # Generate sample AI decisions
            labels = ["APPROVED", "REJECTED", "APPROVED", "BIASED", "APPROVED", "REJECTED", "RISKY"]
            attributes = ["male", "female", "male", "female", "male", "female", "male"]
            
            for i in range(7 - decision_count):
                score = round(random.uniform(0.3, 0.95), 2)
                label = labels[i % len(labels)]
                attr = attributes[i % len(attributes)]
                
                decision = models.AIDecision(
                    owner_id=demo_user.id,
                    decision_label=label,
                    score=score,
                    sensitive_attribute=encrypt_data(attr)
                )
                db.add(decision)
                db.commit()
                db.refresh(decision)
                
                # Create log entry
                log_message = f"DEMO: Auto-generated decision {label} with score {score}"
                log_hash = generate_hash(log_message + str(decision.id))
                
                log = models.DecisionLog(
                    decision_id=decision.id,
                    actor_user_id=demo_user.id,
                    event_type="DEMO_DATA",
                    message=log_message,
                    hash=log_hash
                )
                db.add(log)
                db.commit()
            
            print(f"✅ Generated {7 - decision_count} demo AI decisions")
    
    except Exception as e:
        print(f"⚠️ Demo data generation skipped: {e}")
        db.rollback()
    finally:
        db.close()


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
    
    try:
        user.role = role_data.role
        db.commit()
        return {"status": "success", "new_role": user.role}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error during role update")


# --------- AUTH ---------

from fastapi.security import OAuth2PasswordRequestForm

@app.post("/auth/login", response_model=schemas.TokenResponse, tags=["auth"])
def login(data: schemas.LoginRequest = None, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Support both JSON body and form data (for Swagger OAuth2)
    username = form_data.username if form_data else data.username
    password = form_data.password if form_data else data.password
    
    user = (
        db.query(models.User)
        .filter(models.User.email == username)
        .first()
    )

    if not user:
        user = db.query(models.User).filter(models.User.username == username).first()

    if not user or not verify_password(password, user.password_hash):
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
    
    try:
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating log")


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

    try:
        # 1. Kararı Kaydet (Hassas Veriyi Şifrele)
        encrypted_attr = encrypt_data(decision_in.sensitive_attribute)
        
        db_decision = models.AIDecision(
            owner_id=user_payload["id"],
            decision_label=status_label,
            score=decision_in.score,
            sensitive_attribute=encrypted_attr  # Şifreli kaydet
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

    except Exception as e:
        db.rollback()  # Bir hata olursa yapılanları geri al
        print(f"Error during ethics evaluation: {e}")
        raise HTTPException(status_code=500, detail="System error during evaluation")

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


# --------- AI ANALYSIS ENDPOINTS ---------

import pandas as pd
from pathlib import Path
import sys

# Add project root to path for services import
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from services.fairness_evaluator import FairnessEvaluator
from services.explainer import FairnessExplainer
from services.model_trainer import ModelTrainer
from services.decision_explainer import DecisionExplainer

# Initialize AI services (lazy load)
_fairness_evaluator = None
_fairness_explainer = None
_model_trainer = None
_decision_explainer = None
_trained_model = None
_feature_names = None
_training_data = None


def get_ai_services():
    """Lazy initialization of AI services"""
    global _fairness_evaluator, _fairness_explainer, _model_trainer, _decision_explainer
    global _trained_model, _feature_names, _training_data
    
    if _fairness_evaluator is None:
        _fairness_evaluator = FairnessEvaluator()
        _fairness_explainer = FairnessExplainer()
        _model_trainer = ModelTrainer()
        _decision_explainer = DecisionExplainer()
        
        # Train model on startup for decision explanations
        try:
            dataset_path = project_root / "datasets" / "dummy.csv"
            if dataset_path.exists():
                df = pd.read_csv(dataset_path)
                _trained_model, _feature_names, _training_data = _model_trainer.train(
                    df, target_col="approved", drop_cols=["gender", "approved"]
                )
        except Exception as e:
            print(f"Warning: Could not train model: {e}")
    
    return {
        "evaluator": _fairness_evaluator,
        "explainer": _fairness_explainer,
        "trainer": _model_trainer,
        "decision_explainer": _decision_explainer,
        "model": _trained_model,
        "feature_names": _feature_names,
        "training_data": _training_data
    }


@app.post(
    "/ai/analyze-fairness",
    response_model=schemas.FairnessAnalysisResponse,
    tags=["ai"],
)
def analyze_fairness(
    request: schemas.FairnessAnalysisRequest,
    current_user=Depends(get_current_user),
):
    """
    Analyze fairness metrics on a dataset.
    Uses FairnessEvaluator to calculate demographic parity and equalized odds.
    """
    services = get_ai_services()
    
    # Determine dataset path
    dataset_name = request.dataset_name
    if dataset_name == "biased":
        dataset_path = project_root / "datasets" / "biased.csv"
    else:
        dataset_path = project_root / "datasets" / "dummy.csv"
        dataset_name = "balanced"
    
    if not dataset_path.exists():
        raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_name}")
    
    try:
        df = pd.read_csv(dataset_path)
        
        # Run fairness evaluation
        evaluation = services["evaluator"].evaluate(df)
        
        # Generate explanation
        explanation = services["explainer"].generate_explanation(evaluation, dataset_name)
        
        return {
            "dataset_name": dataset_name,
            "metrics": evaluation["metrics"],
            "risk_analysis": evaluation["risk_analysis"],
            "explanation": explanation
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post(
    "/ai/explain-decision",
    response_model=schemas.DecisionExplanationResponse,
    tags=["ai"],
)
def explain_decision(
    request: schemas.DecisionExplanationRequest,
    current_user=Depends(get_current_user),
):
    """
    Explain a single AI decision using LIME.
    Provides interpretable reasons for the model's prediction.
    """
    services = get_ai_services()
    
    if services["model"] is None:
        raise HTTPException(
            status_code=503, 
            detail="Model not available. Please ensure training data exists."
        )
    
    try:
        # Create instance from request
        instance = pd.Series({
            "income": request.income,
            "age": request.age,
            "credit_score": request.credit_score
        })
        
        # Get LIME explanation
        explanation = services["decision_explainer"].explain_decision(
            model=services["model"],
            feature_names=services["feature_names"],
            instance_row=instance,
            training_data=services["training_data"]
        )
        
        return explanation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")


@app.get(
    "/ai/metrics",
    response_model=schemas.AIMetricsResponse,
    tags=["ai"],
)
def get_ai_metrics(current_user=Depends(get_current_user)):
    """
    Get AI fairness metrics for dashboard display.
    Analyzes both balanced and biased datasets and returns summary.
    """
    services = get_ai_services()
    
    try:
        results = []
        
        for dataset_name in ["dummy.csv", "biased.csv"]:
            dataset_path = project_root / "datasets" / dataset_name
            if dataset_path.exists():
                df = pd.read_csv(dataset_path)
                evaluation = services["evaluator"].evaluate(df)
                results.append(evaluation)
        
        if not results:
            return {
                "demographic_parity": 0.0,
                "equalized_odds": 0.0,
                "overall_risk": "UNKNOWN",
                "datasets_analyzed": 0
            }
        
        # Average metrics across datasets
        avg_dp = sum(r["metrics"]["demographic_parity_difference"] for r in results) / len(results)
        avg_eo = sum(r["metrics"]["equalized_odds_difference"] for r in results) / len(results)
        
        # Determine overall risk (worst case)
        risks = [r["risk_analysis"]["overall_risk"] for r in results]
        if "HIGH" in risks:
            overall = "HIGH"
        elif "MEDIUM" in risks:
            overall = "MEDIUM"
        else:
            overall = "LOW"
        
        return {
            "demographic_parity": round(avg_dp, 4),
            "equalized_odds": round(avg_eo, 4),
            "overall_risk": overall,
            "datasets_analyzed": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics calculation failed: {str(e)}")

