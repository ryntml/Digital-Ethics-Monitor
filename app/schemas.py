from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, ConfigDict, constr, confloat


# ---------- USER ----------

class UserBase(BaseModel):
    username: constr(strip_whitespace=True, min_length=3, max_length=50)
    email: EmailStr
    role: constr(strip_whitespace=True, min_length=3, max_length=50) = "analyst"


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int

    # Pydantic v2: ORM objelerinden model oluşturabilmek için
    model_config = ConfigDict(from_attributes=True)


# ---------- AI DECISION ----------

class AIDecisionBase(BaseModel):
    decision_label: constr(strip_whitespace=True, min_length=2, max_length=50)
    score: confloat(ge=0.0, le=1.0)  # 0.0–1.0 arası
    sensitive_attribute: Optional[constr(strip_whitespace=True, max_length=50)] = None


class AIDecisionCreate(AIDecisionBase):
    owner_id: int


class AIDecisionRead(AIDecisionBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- DECISION LOG ----------

class DecisionLogBase(BaseModel):
    message: constr(strip_whitespace=True, min_length=5, max_length=5000)


class DecisionLogCreate(DecisionLogBase):
    decision_id: int


class DecisionLogRead(DecisionLogBase):
    id: int
    decision_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Karar + logları bir arada döndürmek istersek kullanırız (ileride)
class AIDecisionWithLogs(AIDecisionRead):
    logs: List[DecisionLogRead] = []
