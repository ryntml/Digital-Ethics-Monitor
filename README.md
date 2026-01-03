# Digital Ethics Monitor

AI sistemlerinde etik değerlendirme ve bias (önyargı) tespiti için geliştirilen web tabanlı izleme platformu.

## Proje Hakkında

Digital Ethics Monitor, yapay zeka sistemlerinin kararlarını analiz ederek potansiyel önyargıları tespit eden ve adalet metriklerini hesaplayan bir araçtır. Kredi onayı, işe alım gibi kritik AI kararlarında demografik gruplar arası eşitliği ölçer.

**Temel Özellikler:**
- Demographic Parity ve Equalized Odds metrikleri ile adalet analizi
- LIME tabanlı karar açıklamaları (Explainable AI)
- JWT authentication ve RBAC güvenlik altyapısı
- Real-time dashboard ile metrik görselleştirme
- RESTful API ile entegrasyon desteği

## Kurulum

### Gereksinimler
- Python 3.10+
- PostgreSQL
- Node.js (opsiyonel, frontend geliştirme için)

### Adımlar

1. Repoyu klonlayın:
```bash
git clone https://github.com/username/Digital-Ethics-Monitor.git
cd Digital-Ethics-Monitor
```

2. Virtual environment oluşturun:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

4. Environment değişkenlerini ayarlayın:
```bash
cp .env.example .env
# .env dosyasını düzenleyin
```

5. Veritabanını oluşturun:
```bash
# PostgreSQL'de digital_ethics_db veritabanını oluşturun
```

6. Uygulamayı başlatın:
```bash
uvicorn app.main:app --reload --port 8000
```

7. Frontend'i çalıştırın:
```bash
cd frontend
python -m http.server 8080
```

Tarayıcıda açın: `http://localhost:8080`

## Proje Yapısı

```
Digital-Ethics-Monitor/
├── app/                    # FastAPI backend
│   ├── main.py            # API endpoints
│   ├── models.py          # Database modelleri
│   ├── schemas.py         # Pydantic şemaları
│   ├── security.py        # JWT ve auth
│   └── database.py        # DB bağlantısı
├── services/              # AI servisleri
│   ├── fairness_evaluator.py
│   ├── decision_explainer.py
│   ├── model_trainer.py
│   └── security_manager.py
├── frontend/              # Web arayüzü
│   ├── index.html         # Login sayfası
│   ├── dashboard.html     # Ana panel
│   └── admin.html         # Yönetici paneli
├── metrics/               # Adalet metrikleri
├── datasets/              # Örnek veri setleri
├── docs/                  # Dokümantasyon
└── tests/                 # Test dosyaları
```

## API Kullanımı

### Authentication
```bash
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password"
}
```

### Bias Analizi
```bash
GET /api/analysis/bias?dataset=balanced
Authorization: Bearer <token>
```

### Fairness Metrikleri
```bash
GET /api/analysis/fairness
Authorization: Bearer <token>
```

Detaylı API dokümantasyonu: [docs/api_documentation.md](docs/api_documentation.md)

## Teknolojiler

**Backend:** FastAPI, SQLAlchemy, PostgreSQL, JWT  
**Frontend:** HTML5, Tailwind CSS, Chart.js  
**AI/ML:** scikit-learn, LIME, pandas, numpy

## Güvenlik

- JWT tabanlı authentication
- Role-based access control (RBAC)
- Rate limiting
- Input validation ve sanitization
- CORS koruması

## Test

```bash
pytest tests/ -v
```

## Lisans

Bu proje eğitim amaçlı geliştirilmiştir.
