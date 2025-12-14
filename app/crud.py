from .security import hash_password

from sqlalchemy.orm import Session

from . import models, schemas


# ---------- USER ----------

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


# ---------- AI DECISION ----------

def create_ai_decision(db: Session, decision: schemas.AIDecisionCreate) -> models.AIDecision:
    db_decision = models.AIDecision(
        owner_id=decision.owner_id,
        decision_label=decision.decision_label,
        score=decision.score,
        sensitive_attribute=decision.sensitive_attribute,
    )
    db.add(db_decision)
    db.commit()
    db.refresh(db_decision)
    return db_decision


def get_ai_decision(db: Session, decision_id: int):
    return db.query(models.AIDecision).filter(models.AIDecision.id == decision_id).first()


# ---------- DECISION LOG ----------

def create_decision_log(db: Session, log: schemas.DecisionLogCreate) -> models.DecisionLog:
    db_log = models.DecisionLog(
        decision_id=log.decision_id,
        message=log.message,
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log
