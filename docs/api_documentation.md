# Digital Ethics Monitor - API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
All protected endpoints require JWT Bearer token in the Authorization header.

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

## User Endpoints

### Create User
```http
POST /users/
```
| Field | Type | Required |
|-------|------|----------|
| username | string | Yes |
| email | string | Yes |
| password | string | Yes |
| role | string | No (default: analyst) |

### Get Current User
```http
GET /users/me
Authorization: Bearer <token>
```

---

## AI Decision Endpoints

### Create Decision
```http
POST /decisions/
Authorization: Bearer <token>
```
**Roles:** admin, analyst

### Get Decision
```http
GET /decisions/{decision_id}
Authorization: Bearer <token>
```

---

## Ethics Engine

### Evaluate Decision
```http
POST /ethics/evaluate
Authorization: Bearer <token>
```
| Field | Type | Description |
|-------|------|-------------|
| decision_label | string | APPROVED, REJECTED, etc. |
| score | float | 0.0 - 1.0 confidence score |
| sensitive_attribute | string | Gender, age, etc. (encrypted) |

**Response:**
```json
{
  "decision_id": 1,
  "ethics_status": "FAIR",
  "explanation": "Decision passed basic ethical checks",
  "log_hash": "sha256..."
}
```

---

## AI Analysis Endpoints

### Analyze Fairness
```http
POST /ai/analyze-fairness
Authorization: Bearer <token>
```
Analyzes dataset for bias using Fairlearn metrics.

### Explain Decision
```http
POST /ai/explain-decision
Authorization: Bearer <token>
```
Returns LIME explanation for a single decision.

### Get AI Metrics
```http
GET /ai/metrics
Authorization: Bearer <token>
```
Returns dashboard metrics (demographic parity, equalized odds).

---

## Admin Endpoints

### Get Audit Logs
```http
GET /admin/logs?limit=100&event_type=ETHICS_EVALUATION
Authorization: Bearer <token>
```
**Roles:** admin only

### Update User Role
```http
PATCH /users/{user_id}/role
Authorization: Bearer <token>
```
**Roles:** admin only

---

## Security Features
- **JWT Authentication** with 30-minute expiration
- **AES-256 Encryption** for sensitive attributes
- **SHA-256 Hashing** for audit log integrity
- **Role-Based Access Control (RBAC)**
- **Input Validation** on all endpoints
- **Rate Limiting** (100 requests/hour per user)
