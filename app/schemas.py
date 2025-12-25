from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, ConfigDict, constr, confloat


# ---------- USER ----------

class UserBase(BaseModel):
    username: constr(strip_whitespace=True, min_length=3, max_length=50)
    email: EmailStr
    role: constr(strip_whitespace=True, min_length=3, max_length=50) = "analyst"


class UserCreate(UserBase):
    password: constr(min_length=6, max_length=128)


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)

class UserRoleUpdate(BaseModel):
    role: str

# ---------- AI DECISION ----------

class AIDecisionBase(BaseModel):
    decision_label: constr(strip_whitespace=True, min_length=2, max_length=50)
    score: confloat(ge=0.0, le=1.0)  # 0.0–1.0 arası
    sensitive_attribute: Optional[constr(strip_whitespace=True, max_length=50)] = None


class AIDecisionCreate(AIDecisionBase):
    pass


class AIDecisionRead(AIDecisionBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- DECISION LOG ----------

class DecisionLogBase(BaseModel):
    message: constr(strip_whitespace=True, min_length=5, max_length=5000)
    event_type: str = "SYSTEM"


class DecisionLogCreate(DecisionLogBase):
    decision_id: Optional[int] = None


class DecisionLogRead(DecisionLogBase):
    id: int
    decision_id: Optional[int]
    actor_user_id: Optional[int]
    hash: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Karar + logları bir arada döndürmek istersek kullanırız (ileride)
class AIDecisionWithLogs(AIDecisionRead):
    logs: List[DecisionLogRead] = []

class DashboardStats(BaseModel):
    total_decisions: int
    bias_count: int
    fairness_score: float
    system_health: int

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- AI ANALYSIS ----------

class FairnessAnalysisRequest(BaseModel):
    """Request for fairness analysis on a dataset"""
    dataset_name: str = "default"  # "balanced" or "biased"


class FairnessAnalysisResponse(BaseModel):
    """Response from fairness analysis"""
    dataset_name: str
    metrics: dict
    risk_analysis: dict
    explanation: str


class DecisionExplanationRequest(BaseModel):
    """Request for explaining a single AI decision"""
    income: float
    age: int
    credit_score: float


class DecisionExplanationResponse(BaseModel):
    """Response with LIME explanation for a decision"""
    prediction: str
    confidence: float
    top_features: list
    explanation_text: str


class AIMetricsResponse(BaseModel):
    """Response for dashboard AI metrics"""
    demographic_parity: float
    equalized_odds: float
    overall_risk: str
    datasets_analyzed: int

