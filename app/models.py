from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="analyst")

    decisions = relationship("AIDecision", back_populates="owner")
    audit_logs = relationship("DecisionLog", back_populates="actor")

class AIDecision(Base):
    """
    AI modelinin verdiği kararları tutan tablo.
    Örn: approve / reject, skor, hassas özellik vb.
    """
    __tablename__ = "ai_decisions"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    decision_label = Column(String(50), nullable=False)
    score = Column(Float, nullable=False)
    sensitive_attribute = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="decisions")
    logs = relationship("DecisionLog", back_populates="decision")


class DecisionLog(Base):
    __tablename__ = "decision_logs"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("ai_decisions.id"), nullable=True)
    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String(50), nullable=False, default="SYSTEM")
    message = Column(Text, nullable=False)
    hash = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    decision = relationship("AIDecision", back_populates="logs")
    actor = relationship("User", back_populates="audit_logs")
