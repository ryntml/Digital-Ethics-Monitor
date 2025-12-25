# Digital Ethics Monitor - Final Presentation

## Project Overview

**Digital Ethics Monitor (DEM)** is a secure and transparent AI monitoring framework that ensures AI decisions remain ethical, explainable, and aligned with human values.

---

## Key Features

### 🔒 Security
- **JWT Authentication** - Secure token-based access
- **AES-256 Encryption** - Sensitive data protected at rest
- **SHA-256 Logging** - Tamper-proof audit trails
- **RBAC** - Role-based access control

### 🤖 AI Ethics Engine
- **Bias Detection** - Fairlearn metrics (demographic parity, equalized odds)
- **Explainability** - LIME-based decision explanations
- **Risk Assessment** - Automated LOW/MEDIUM/HIGH classification

### 📊 Transparency Dashboard
- Real-time monitoring of AI decisions
- Bias distribution visualizations
- Fairness metrics radar charts
- Decision timeline analysis

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│                    Frontend (Dashboard)                 │
│           HTML5 + Tailwind CSS + Chart.js              │
└────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│                  FastAPI Backend                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐ │
│  │   Auth   │  │  Ethics  │  │   AI Services        │ │
│  │  (JWT)   │  │  Engine  │  │  - FairnessEvaluator │ │
│  └──────────┘  └──────────┘  │  - DecisionExplainer │ │
│                              │  - ModelTrainer      │ │
│                              └──────────────────────┘ │
└────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│              PostgreSQL + AES-256 Encryption            │
└────────────────────────────────────────────────────────┘
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/login` | POST | User authentication |
| `/ethics/evaluate` | POST | Evaluate AI decision ethics |
| `/ai/analyze-fairness` | POST | Run bias analysis |
| `/ai/explain-decision` | POST | Get LIME explanation |
| `/ai/metrics` | GET | Dashboard metrics |
| `/admin/logs` | GET | Audit log access |

---

## Demo Flow

1. **Login** → JWT token issued
2. **Submit AI Decision** → Ethics evaluation
3. **View Dashboard** → Real-time metrics
4. **Analyze Bias** → Fairlearn analysis
5. **Review Logs** → Secure audit trail

---

## Security Compliance

| Requirement | Implementation |
|-------------|----------------|
| Input Validation | Pydantic schemas + validators |
| Authentication | JWT with HS256 |
| Authorization | RBAC (admin, analyst, viewer) |
| Encryption | AES-256 (Fernet) |
| Logging | SHA-256 hashed |
| Static Analysis | Bandit |

---

## Team

- Fundanur Öztürk – 21118080056
- Reyyan Temel – 21118080015
- Hatice Sevde Kaplan – 21118080090
- Osman Sefa Coşar – 21118080013
- Baran Türkmen – 21118080012

---

## Running the Project

```bash
# Backend
cd d:\Secure\Digital-Ethics-Monitor
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
python -m http.server 3000
```

**Dashboard:** http://localhost:3000/dashboard.html
**API Docs:** http://localhost:8000/docs
