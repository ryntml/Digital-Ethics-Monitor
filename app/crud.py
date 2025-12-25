from .security import hash_password, encrypt_data, decrypt_data

from sqlalchemy.orm import Session

from . import models, schemas


# ---------- USER ----------

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_pw = hash_password(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_pw,
        role=user.role,
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()  # Hata durumunda işlemi geri al
        raise e



def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


# ---------- AI DECISION ----------

def create_ai_decision(db: Session, decision: schemas.AIDecisionCreate, owner_id: int) -> models.AIDecision:
   # Hassas veriyi şifrele (Encryption Support)
    encrypted_sensitive_attr = encrypt_data(decision.sensitive_attribute)
    
    db_decision = models.AIDecision(
        owner_id=owner_id,
        decision_label=decision.decision_label,
        score=decision.score,
        sensitive_attribute=encrypted_sensitive_attr, # Şifreli hâlini kaydet
    )
    try:
        db.add(db_decision)
        db.commit()
        db.refresh(db_decision)

        # Dönüş yaparken şifreyi çözmemize gerek yok, kullanıcı ne gönderdiyse onu response_model'e verebiliriz
        # Ama tutarlılık için obje üzerindeki veriyi decrypt edilmiş hâliyle güncelleyebiliriz (DB'yi etkilemez)
        db_decision.sensitive_attribute = decision.sensitive_attribute
        return db_decision
    except Exception as e:
        db.rollback()
        raise e


def get_ai_decision(db: Session, decision_id: int):
    decision = db.query(models.AIDecision).filter(models.AIDecision.id == decision_id).first()

    # Okurken şifreyi çöz (Decryption)
    if decision and decision.sensitive_attribute:
        # DB objesini geçici olarak değiştiriyoruz (Commit etmediğimiz sürece DB'de değişmez)
        decision.sensitive_attribute = decrypt_data(decision.sensitive_attribute)
        
    return decision

# ---------- DECISION LOG ----------

def create_decision_log(db: Session, log: schemas.DecisionLogCreate, actor_id: int, log_hash: str) -> models.DecisionLog:
    db_log = models.DecisionLog(
        decision_id=log.decision_id,
        actor_user_id=actor_id,
        event_type=log.event_type,
        message=log.message,
        hash=log_hash
    )
    try:
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log
    except Exception as e:
        db.rollback()
        raise e
