# Digital Ethics Monitor - Backend Integration Guide

## Overview
This document describes how to integrate external AI models with the Digital Ethics Monitor (DEM) backend.

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   AI Model      │────▶│   DEM Backend   │────▶│   PostgreSQL    │
│   (External)    │     │   (FastAPI)     │     │   Database      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   Frontend      │
                        │   Dashboard     │
                        └─────────────────┘
```

---

## Integration Steps

### 1. Authentication
First, obtain a JWT token:

```python
import requests

response = requests.post(
    "http://localhost:8000/auth/login",
    json={"username": "ai_service@system.com", "password": "secure_password"}
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
```

### 2. Submit AI Decision for Ethics Evaluation

```python
decision = {
    "decision_label": "APPROVED",  # or "REJECTED", "PENDING"
    "score": 0.85,                 # Model confidence (0.0 - 1.0)
    "sensitive_attribute": "male"  # Will be encrypted
}

response = requests.post(
    "http://localhost:8000/ethics/evaluate",
    json=decision,
    headers=headers
)

result = response.json()
# {
#   "decision_id": 123,
#   "ethics_status": "FAIR",  # or "BIASED", "RISKY"
#   "explanation": "Decision passed basic ethical checks",
#   "log_hash": "sha256..."
# }
```

### 3. Request Fairness Analysis

```python
response = requests.post(
    "http://localhost:8000/ai/analyze-fairness",
    json={"dataset_name": "biased"},  # or "balanced"
    headers=headers
)

analysis = response.json()
# {
#   "dataset_name": "biased",
#   "metrics": {
#     "demographic_parity_difference": 0.25,
#     "equalized_odds_difference": 0.18
#   },
#   "risk_analysis": {
#     "demographic_parity_risk": "MEDIUM",
#     "overall_risk": "MEDIUM"
#   },
#   "explanation": "WARNING: Moderate bias detected..."
# }
```

---

## Ethics Status Codes

| Status | Condition | Action |
|--------|-----------|--------|
| FAIR | score ≥ 0.6, no sensitive attribute issues | Proceed normally |
| RISKY | score < 0.6 | Manual review recommended |
| BIASED | sensitive attribute + low score | Investigate model bias |

---

## Webhook Integration (Future)

For real-time notifications, configure webhook URL:

```python
# Coming soon
POST /settings/webhook
{
    "url": "https://your-service.com/dem-callback",
    "events": ["BIASED", "RISKY"]
}
```

---

## Error Handling

| HTTP Code | Meaning |
|-----------|---------|
| 200 | Success |
| 401 | Invalid/expired token |
| 403 | Insufficient permissions |
| 422 | Validation error |
| 500 | Server error |

---

## Rate Limits

- **Default:** 100 requests/hour per user
- **Exceeded:** HTTP 429 Too Many Requests

---

## Best Practices

1. **Batch Processing:** Group decisions when possible
2. **Async Integration:** Use background workers for high-volume
3. **Retry Logic:** Implement exponential backoff for failures
4. **Logging:** Track all DEM responses for audit purposes
